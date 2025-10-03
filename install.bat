@echo off
title CodeTantra Automation - Installer
echo ================================================
echo CodeTantra Automation - Complete Setup
echo ================================================
echo.

echo This installer will:
echo 1. Clone the CodeTantra Automation repository
echo 2. Install all required dependencies
echo 3. Set up the application for use
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

REM Check if Git is installed
echo Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git from: https://git-scm.com/downloads
    echo.
    start https://git-scm.com/downloads
    pause
    exit /b 1
)

echo Git found:
git --version
echo.

REM Clone the repository
echo Cloning CodeTantra Automation repository...
echo.

REM Check if repository already exists
if exist "CodeTantraAutomation" (
    echo Repository already exists. Updating...
    cd CodeTantraAutomation
    git pull origin desktop-app
    if errorlevel 1 (
        echo Warning: Failed to update repository. Using existing version.
    )
    cd ..
) else (
    echo Cloning fresh repository...
    git clone -b desktop-app https://github.com/your-username/CodeTantraAutomation.git
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to clone repository!
        echo Please check your internet connection and try again.
        echo.
        echo If the repository URL is incorrect, please update the install.bat file
        echo with the correct GitHub repository URL.
        pause
        exit /b 1
    )
)

echo.
echo Repository cloned successfully!
echo.

REM Navigate to the application directory
cd CodeTantraAutomation

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

echo Installing Firefox...
python -m playwright install firefox
if errorlevel 1 (
    echo WARNING: Firefox installation failed
    echo You may need to install browsers manually later
)

echo Installing Chromium...
python -m playwright install chromium
if errorlevel 1 (
    echo WARNING: Chromium installation failed
)

echo Installing WebKit...
python -m playwright install webkit
if errorlevel 1 (
    echo WARNING: WebKit installation failed
)

echo.
echo Testing installation...
python -c "import playwright, pyperclip, keyboard, requests; print('All packages imported successfully')"
if errorlevel 1 (
    echo WARNING: Package test failed
    echo Some packages may not be installed correctly
) else (
    echo Package test successful
)

echo.
echo Testing browser...
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.firefox.launch(headless=True); browser.close(); p.stop(); print('Browser test successful')"
if errorlevel 1 (
    echo WARNING: Browser test failed
    echo You may need to install browsers manually
) else (
    echo Browser test successful
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
echo 1. Go back to the parent directory
echo 2. Double-click run.bat
echo 3. Or navigate to CodeTantraAutomation folder and run: python desktop-app\main.py
echo.

echo IMPORTANT: Before first use:
echo 1. Edit credentials.py with your CodeTantra account details
echo 2. Edit config.py with your API settings
echo 3. Make sure you have internet connection
echo.

echo If you encounter any issues:
echo 1. Check your internet connection
echo 2. Try running as administrator
echo 3. Verify Python and Git are properly installed
echo 4. Check Windows version compatibility
echo.

echo Setup complete! You can now use CodeTantra Automation.
echo.

pause
