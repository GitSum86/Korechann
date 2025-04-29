import time
import yaml
import json
import re
import requests
import subprocess
import sys
import os
import html
from datetime import datetime, timedelta
from googleapiclient.discovery import build

if getattr(sys, 'frozen', False):
    # If the app is running as a bundled exe (frozen)
    os.chdir(os.path.dirname(sys.executable))
else:
    # If running normally (script)
    os.chdir(os.path.dirname(__file__))

# === Load Configuration (UTF-8 safe) ===
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

API_KEY = config["youtube_api_key"]
BOT_TOKEN = config["telegram_bot_token"]
CHAT_ID = config["telegram_bot_chat_id"] if "telegram_bot_chat_id" in config else config["telegram_chat_id"]
FAST_THRESHOLD = config["fast_threshold"]
SLOW_THRESHOLD = config["slow_threshold"]
FAST_HOURS = config("fast_hours")
SLOW_HOURS = config("slow_hours")
CHECK_INTERVAL = config.get("check_interval_minutes", 1440)  # in minutes (default 1440 = 24 hours)
DOWNLOAD_ROOT_FOLDER = config["download_root_folder"]
PREFERRED_FORMAT = config.get("preferred_format", "bestvideo+bestaudio/best")
TITLE_KEYWORDS = config.get("title_keywords", [])
EXCLUDE_TITLE_KEYWORDS = [kw.lower() for kw in config.get("exclude_title_keywords", [])]
TRUSTED_CHANNELS = config.get("official_channels", [])
ARTIST_NAME_MAP = config.get("artist_name_map", {})

# === Load Notified History ===
try:
    with open('notified.json', 'r', encoding='utf-8') as f:
        notified = json.load(f)
except FileNotFoundError:
    notified = {"fast": [], "slow": []}

# === Setup YouTube API Client ===
youtube = build('youtube', 'v3', developerKey=API_KEY)

# === Logging Helper Function ===
def log_event(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open('korechann.log', 'a', encoding='utf-8-sig') as f:
        f.write(f"{timestamp} {message}\n")

# === Helper Functions ===

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)
    log_event(f"Telegram notification sent: {message}")

def map_artist_name(original_name):
    return ARTIST_NAME_MAP.get(original_name, original_name)

def sanitize_filename(name):
    invalid_chars = r'<>:"/\|?*'
    for ch in invalid_chars:
        name = name.replace(ch, '')
    return name.strip()

def download_video(video_url, artist_name, video_title):
    mapped_artist = map_artist_name(artist_name)
    safe_artist_folder = sanitize_filename(mapped_artist)
    full_folder_path = os.path.join(DOWNLOAD_ROOT_FOLDER, safe_artist_folder)

    if not os.path.exists(full_folder_path):
        os.makedirs(full_folder_path)
        log_event(f"Created folder: {full_folder_path}")

    # Output template
    output_template = os.path.join(full_folder_path, "%(title)s.%(ext)s")

    command = [
        "python", "-m", "yt_dlp",
        video_url,
        "--format", PREFERRED_FORMAT,
        "--write-subs",
        "--sub-lang", "en",
        "--convert-subs", "srt",
        "-o", output_template
    ]

    print(f"Running command: {' '.join(command)}")
    log_event(f"Download command: {' '.join(command)}")

    result = subprocess.run(command)

    if result.returncode != 0:
        log_event(f"yt-dlp error downloading {video_url}")
        print(f"Download failed")
        return

    # IMPORTANT: Decode HTML entities!
    decoded_title = html.unescape(video_title)
    sanitized_title = sanitize_filename(decoded_title)
    base_path = os.path.join(full_folder_path, sanitized_title)

    found = False
    for ext in ["mp4", "webm", "mkv"]:
        candidate = f"{base_path}.{ext}"
        if os.path.exists(candidate):
            create_nfo_file(candidate, decoded_title, mapped_artist)
            log_event(f"NFO created for {candidate}")
            print(f"NFO created for {candidate}")
            found = True
            break

    if not found:
        log_event(f"Warning: Could not find downloaded video for {decoded_title} after download.")

def create_nfo_file(video_path, title, artist_name):
    """Create an NFO file next to the downloaded video."""
    nfo_path = os.path.splitext(video_path)[0] + ".nfo"
    nfo_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<musicvideo>
    <title>{title}</title>
    <userrating></userrating>
    <track></track>
    <album></album>
    <plot></plot>
    <genre></genre>
    <director></director>
    <premiered></premiered>
    <studio></studio>
    <artist>{artist_name}</artist>
</musicvideo>'''
    with open(nfo_path, 'w', encoding='utf-8') as f:
        f.write(nfo_content)
    log_event(f"NFO created at: {nfo_path}")
    print(f"NFO created at: {nfo_path}")
    
def title_matches(title, keywords):
    title_lower = title.lower()
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b' if len(keyword) > 1 else keyword.lower()
        if re.search(pattern, title_lower):
            return True
    return False

def title_excluded(title, exclude_keywords):
    title_lower = title.lower()
    return any(exclude_kw in title_lower for exclude_kw in exclude_keywords)

def check_videos():
    now = datetime.utcnow()
    published_after = (now - timedelta(hours=SLOW_HOURS)).isoformat("T") + "Z"
    print(f"\nChecking for official K-pop videos published after {published_after}...")
    log_event(f"Started check for videos after {published_after}")
    for channel_id in TRUSTED_CHANNELS:
        print(f"Scanning channel: {channel_id}")
        log_event(f"Scanning channel: {channel_id}")
        search_response = youtube.search().list(
            channelId=channel_id,
            part="id,snippet",
            order="date",
            publishedAfter=published_after,
            maxResults=50
        ).execute()
        candidates = []
        for item in search_response.get('items', []):
            if item['id']['kind'] != 'youtube#video':
                continue
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            publish_time = item['snippet']['publishedAt']
            channel_title = item['snippet']['channelTitle']
            publish_dt = datetime.strptime(publish_time, "%Y-%m-%dT%H:%M:%SZ")
            age_hours = (now - publish_dt).total_seconds() / 3600
            if not title_matches(title, TITLE_KEYWORDS):
                continue
            is_excluded = title_excluded(title, EXCLUDE_TITLE_KEYWORDS)
            candidates.append({
                "video_id": video_id,
                "title": title,
                "channel_title": channel_title,
                "publish_dt": publish_dt,
                "age_hours": age_hours,
                "is_excluded": is_excluded
            })
        if not candidates:
            print(f"No matching videos found for channel {channel_id}.")
            log_event(f"No matching videos found for channel {channel_id}")
            continue
        # Batch fetch view counts
        video_ids = [video['video_id'] for video in candidates]
        video_id_batches = [video_ids[i:i + 50] for i in range(0, len(video_ids), 50)]
        stats_lookup = {}
        for batch in video_id_batches:
            videos_response = youtube.videos().list(
                id=','.join(batch),
                part="statistics"
            ).execute()
            for item in videos_response.get('items', []):
                stats_lookup[item['id']] = int(item['statistics'].get('viewCount', 0))
        # Process each candidate after getting view counts
        for video in candidates:
            view_count = stats_lookup.get(video['video_id'], 0)
            video_url = f"https://www.youtube.com/watch?v={video['video_id']}"
            
            # CLEAN TITLE BEFORE USING
            decoded_title = html.unescape(video['title'])
            decoded_channel_title = html.unescape(video['channel_title'])
            
            if video['age_hours'] <= FAST_HOURS:
                if view_count >= FAST_THRESHOLD and video['video_id'] not in notified["fast"]:
                    base_msg = f"{video['title']}\nViews: {view_count}\n{video_url}"
                    if video['is_excluded']:
                        reason = f"Excluded from download due to keyword match: {', '.join([kw for kw in EXCLUDE_TITLE_KEYWORDS if kw in video['title'].lower()])}"
                        message = f"🔥 Fast Surge! 🔥 (Excluded)\n{base_msg}\n\n{reason}"
                        log_event(f"Excluded: {video['title']} | Reason: {reason}")
                    else:
                        message = f"🔥 Fast Surge! 🔥\n{base_msg}"
                        download_video(video_url, video['channel_title'], video['title'])
                        log_event(f"Fast Surge processed for video: {video['video_id']}")
                    print(f"Sending Telegram message:\n{message}\n")
                    send_telegram(message)
                    notified["fast"].append(video['video_id'])
                else: log_event(f"Video within fast window but below threshold: {decoded_title} | {view_count} views | {video_url}")
                    
            elif video['age_hours'] <= SLOW_HOURS:
                if view_count >= SLOW_THRESHOLD and video['video_id'] not in notified["slow"]:
                    base_msg = f"{video['title']}\nViews: {view_count}\n{video_url}"
                    if video['is_excluded']:
                        reason = f"Excluded from download due to keyword match: {', '.join([kw for kw in EXCLUDE_TITLE_KEYWORDS if kw in video['title'].tolower()])}"
                        message = f"⚡ Slow Surge! ⚡ (Excluded)\n{base_msg}\n\n{reason}"
                        log_event(f"Excluded: {decoded_title} | Reason: {reason}")
                    else:
                        message = f"⚡ Slow Surge! ⚡\n{base_msg}"
                        download_video(video_url, video['channel_title'], video['title'])
                        log_event(f"Slow Surge processed for video: {video['video_id']}")
                    print(f"Sending Telegram message:\n{message}\n")
                    send_telegram(message)
                    notified["slow"].append(video['video_id'])
                else: log_event(f"Video within slow window but below threshold: {decoded_title} | {view_count} views | {video_url}")
    with open('notified.json', 'w', encoding='utf-8') as f:
        json.dump(notified, f, indent=2)
    log_event("Completed check for all channels")

# === Main Loop ===

def main():
    # Print configuration summary at startup
    startup_msg = (
        f"Korechann Service Starting:\n"
        f"Fast Surge: {FAST_HOURS} hours window, {FAST_THRESHOLD} views threshold\n"
        f"Slow Surge: {SLOW_HOURS} hours window, {SLOW_THRESHOLD} views threshold\n"
        f"Check Interval: {CHECK_INTERVAL} minutes\n"
        f"Download Root Folder: {DOWNLOAD_ROOT_FOLDER}"
    )
    print(startup_msg)
    log_event(startup_msg)
    
    while True:
        try:
            check_videos()
            current_time = datetime.now().isoformat()
            msg = f"Checked at {current_time}. Sleeping {CHECK_INTERVAL} minutes..."
            print(msg)
            log_event(msg)
        except Exception as e:
            error_msg = f"Error during check: {e}"
            print(error_msg)
            log_event(error_msg)
        time.sleep(CHECK_INTERVAL * 60)

if __name__ == "__main__":
    main()
