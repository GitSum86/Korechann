@echo off
echo === Korechann Service Uninstaller ===

:: Move to the batch file's own directory
cd /d %~dp0

:: Stop the service if running
echo Stopping Korechann Service...
python korechann_launcher_service.py stop || echo Service may not be running.

:: Remove the service
echo Removing Korechann Service...
python korechann_launcher_service.py remove || echo Service may not be installed.

:: Optional: clean up launcher logs
if exist korechann_launcher.log (
    echo Deleting launcher log...
    del korechann_launcher.log
)

:: Ask about config.yaml
echo.
set /p KEEP_CONFIG=Do you want to keep your config.yaml? (Y/N): 

if /I "%KEEP_CONFIG%"=="N" (
    echo Deleting config.yaml...
    if exist config.yaml del config.yaml
) else (
    echo Keeping config.yaml.
)

:: Ask about program files
echo.
set /p REMOVE_PROGRAM=Do you want to keep the Korechann program files (EXEs, JSONs)? (Y/N): 

if /I "%REMOVE_PROGRAM%"=="N" (
    echo Deleting program files...
    if exist korechann_service.exe del korechann_service.exe
    if exist korechann_launcher_service.exe del korechann_launcher_service.exe
    if exist notified.json del notified.json
) else (
    echo Keeping program files.
)

echo.
echo === Uninstallation Complete ===
pause
