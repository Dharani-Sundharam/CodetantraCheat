@echo off
title CodeTantra Automation - Installer
echo ================================================
echo CodeTantra Automation - Complete Setup
echo ================================================
echo.

echo This installer will:
echo 1. Install all required dependencies
echo 2. Set up Playwright browsers
echo 3. Configure the application for use
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if we're in the right directory
if not exist "desktop-app" (
    echo.
    echo ERROR: CodeTantra Automation files not found!
    echo.
    echo Please make sure you extracted all files from the zip archive
    echo and run this installer from the main CodeTantra Automation folder.
    echo.
    echo Expected structure:
    echo CodeTantraAutomation\
    echo   ├── desktop-app\
    echo   ├── install.bat
    echo   ├── run.bat
    echo   └── requirements.txt
    echo.
    pause
    exit /b 1
)

echo CodeTantra Automation files found!
echo.

echo Installing required packages...
echo.

REM Install packages from requirements.txt
echo Installing all dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install some packages
    echo Trying individual installation...
    
    echo Installing Playwright...
    pip install playwright==1.40.0
    if errorlevel 1 (
        echo ERROR: Failed to install Playwright
        pause
        exit /b 1
    )
    
    echo Installing PyPerclip...
    pip install pyperclip==1.8.2
    if errorlevel 1 (
        echo ERROR: Failed to install PyPerclip
        pause
        exit /b 1
    )
    
    echo Installing Keyboard...
    pip install keyboard==0.13.5
    if errorlevel 1 (
        echo ERROR: Failed to install Keyboard
        pause
        exit /b 1
    )
    
    echo Installing Requests...
    pip install requests==2.31.0
    if errorlevel 1 (
        echo ERROR: Failed to install Requests
        pause
        exit /b 1
    )
)

echo.
echo Installing Playwright browsers...
echo.

REM Install Playwright browsers
python -m playwright install firefox chromium webkit --with-deps
if errorlevel 1 (
    echo ERROR: Failed to install Playwright browsers.
    echo Please check your internet connection.
    echo You may need to install browsers manually by running:
    echo python -m playwright install firefox chromium webkit --with-deps
    echo.
    echo You may need to run this script as administrator.
    echo You may need to install browsers manually
) else (
    echo Browser installation successful!
)

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.

echo CodeTantra Automation has been installed successfully!
echo.
echo Application location: %CD%
echo.
echo To run the application:
echo 1. Double-click run.bat
echo 2. Or run: python desktop-app\main.py
echo.

echo IMPORTANT: Before first use:
echo 1. Copy desktop-app\credentials_template.py to desktop-app\credentials.py
echo 2. Edit desktop-app\credentials.py with your CodeTantra account details
echo 3. Edit desktop-app\config.py with your API settings
echo 4. Make sure you have internet connection
echo.

echo If you encounter any issues:
echo 1. Check your internet connection
echo 2. Try running as administrator
echo 3. Verify Python is properly installed
echo 4. Check Windows version compatibility
echo.

echo Setup complete! You can now use CodeTantra Automation.
echo.

pause