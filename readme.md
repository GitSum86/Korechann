# Korechann - K-Pop Music Video Monitoring Bot

Korechann is an automated Python-based service that monitors trusted K-Pop YouTube channels for new music video releases (it can be configured for other trusted channels).

It sends push notifications directly to your mobile device via Telegram account when new popular videos are detected, based on configurable view thresholds and timing windows.

You can optionally auto-download the videos to a local NAS or storage location, with generated metadata files for media libraries like Kodi.

---

## Features

- Monitors several official K-Pop YouTube channels
- Telegram push notifications for fast-surge and slow-surge videos
- Automated high-quality video downloads
- Auto-generation of `.nfo` metadata files for Kodi integration
- Configurable thresholds, keywords, and channel list
- Log can capture what YouTube API found as relevant videos even if the threshold for views were not met (no API quota waste)
- Fully self-hosted and private

---

## Requirements

- Windows 10/11
- Python 3.10 or higher
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (YouTube video downloader)
- Telegram mobile app (for receiving notifications)
- Google Developer Account (for YouTube API key generation)

---

## Setup Instructions

### 1. Clone This Repository or Download a Release

- bash
- git clone https://github.com/yourusername/Korechann.git
- cd Korechann_Public
## OR
- Download the latest [release](https://github.com/GitSum86/Korechann/releases)

### 2. Set Up YouTube Data API Access

- Visit Google Cloud Console.
- Create a new project.
- Enable the YouTube Data API v3 for the project.
- Create API credentials → choose API Key.
- Copy the generated key for later use.

### 3. Create your own Telegram bot

- Open Telegram.
- Start a chat with BotFather.
- Use /newbot and follow the prompts to create a bot.
- Copy your new bot token (looks like 123456789:ABCDefGHIJKlmNOPQRstuvWXYZ).
- Start a conversation with your bot (send any message).
- Retrieve your chat ID (you can use a bot like userinfobot or Telegram's web API).

### 4. Configure Korechann

- Copy "config_template.yaml" to be "config.yaml".
- Edit config.yaml and fill in:
	- youtube_api_key: "YOUR_YOUTUBE_API_KEY"
	- telegram_bot_token: "YOUR_TELEGRAM_BOT_TOKEN"
	- telegram_chat_id: "YOUR_TELEGRAM_CHAT_ID"
- Adjust thresholds, keywords, and channels as desired.

### 5. Install Dependencies

pip install -r requirements.txt

### 6. Install Korechann as a Windows Service

- Run install_korechann.bat as Administrator.
- Korechann will install itself as a Windows background service.
- It will monitor K-Pop channels and send Telegram notifications automatically.

### 7. Uninstalling Korechann

- Run uninst_korechann.bat as Administrator.
- Choose whether to delete your config files and program binaries.

### How Telegram Integration Works

Once configured, Korechann:

- Monitors trusted K-Pop YouTube channels.
- Detects new music video uploads based on your view thresholds and publish time windows.
- Sends push notifications via your custom Telegram bot directly to your mobile device.
- Optionally downloads videos automatically and generates .nfo metadata files for use in Kodi or other media centers.

### License

This project is licensed under the MIT License.

See LICENSE for details.

### Disclaimer

This project is intended for personal, educational use.
Please ensure you comply with YouTube's Terms of Service, Telegram's usage guidelines, and copyright laws in your jurisdiction.
