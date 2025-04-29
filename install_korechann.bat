@echo off
:: Korechann Service Installer

:: Check if running as administrator
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] This installer must be run as Administrator.
    echo.
    pause
    exit /b 1
)

echo === Korechann Service Installer ===
cd /d "%~dp0"

:: Service and worker settings
set SERVICE_NAME=KorechannService
set DISPLAY_NAME=Korechann Service
set WORKER_EXE=%cd%\korechann_service.exe

:: Confirm worker exists
if not exist "%WORKER_EXE%" (
    echo [ERROR] korechann_service.exe not found in folder: %cd%
    pause
    exit /b 1
)

echo [INFO] Installing service: %SERVICE_NAME%
echo [INFO] Worker executable: %WORKER_EXE%

:: Install and configure service
nssm.exe install %SERVICE_NAME% "%WORKER_EXE%"
nssm.exe set %SERVICE_NAME% AppDirectory "%cd%"
nssm.exe set %SERVICE_NAME% DisplayName "%DISPLAY_NAME%"
nssm.exe set %SERVICE_NAME% Start SERVICE_AUTO_START
nssm.exe set %SERVICE_NAME% AppRestartDelay 5000
nssm.exe set %SERVICE_NAME% AppStdout "%cd%\korechann_service.log"
nssm.exe set %SERVICE_NAME% AppStderr "%cd%\korechann_service_error.log"

:: Start the service
nssm.exe start %SERVICE_NAME%

echo.
echo [SUCCESS] Korechann Service installed and started successfully.
pause