@echo off
echo === Korechann Service Uninstaller ===

:: Check for admin rights
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] This uninstaller must be run as Administrator.
    echo.
    pause
    exit /b 1
)

:: Move to the batch file's own directory
cd /d %~dp0

set SERVICE_NAME=KorechannService

nssm.exe stop %SERVICE_NAME%
nssm.exe remove %SERVICE_NAME% confirm

echo [Uninstaller] Korechann Service uninstalled.
pause

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
    if exist notified.json del notified.json
) else (
    echo Keeping program files.
)

echo.
echo === Uninstallation Complete ===
pause
