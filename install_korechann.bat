@echo off
echo === Korechann 3.2 Service Installer ===

:: Move to the batch file's own directory
cd /d %~dp0

:: Check if the launcher EXE exists
if not exist korechann_launcher_service.exe (
    echo Launcher EXE not found. Attempting to build using PyInstaller...

    :: Check if pyinstaller is installed
    where pyinstaller >nul 2>&1
    if %errorlevel% neq 0 (
        echo Error: PyInstaller is not installed. Please install it first:
        echo pip install pyinstaller
        pause
        exit /b
    )

    :: Build the launcher EXE
    pyinstaller --onefile korechann_launcher_service.py --name korechann_launcher_service --noconsole

    :: Move the output EXE into the working folder
    move /Y dist\korechann_launcher_service.exe . >nul
    rmdir /s /q build
    del korechann_launcher_service.spec
    rmdir /s /q dist

    echo Launcher EXE built successfully.
)

:: Try to stop any existing service
echo Attempting to stop any existing Korechann service...
korechann_launcher_service.exe stop || echo No existing service to stop.

:: Try to remove any existing service
echo Attempting to remove any existing Korechann service...
korechann_launcher_service.exe remove || echo No existing service to remove.

:: Install fresh service
echo Installing Korechann Service...
korechann_launcher_service.exe install

:: Start fresh service
echo Starting Korechann Service...
korechann_launcher_service.exe start

echo === Installation Complete ===
pause
