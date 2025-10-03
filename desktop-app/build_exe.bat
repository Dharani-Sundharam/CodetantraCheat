@echo off
echo Building CodeTantra Automation Desktop App
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Step 2: Installing Playwright browsers...
playwright install firefox
if errorlevel 1 (
    echo Error: Failed to install Playwright browsers
    pause
    exit /b 1
)
echo.

echo Step 3: Creating executable with PyInstaller...
pyinstaller CodeTantraAutomation.spec
if errorlevel 1 (
    echo Error: Failed to create executable
    echo Trying fallback method...
    pyinstaller --onefile --windowed --name CodeTantraAutomation --add-data "*.py;." --hidden-import playwright --hidden-import tkinter --hidden-import pyperclip --hidden-import keyboard main.py
    if errorlevel 1 (
        echo Error: Both methods failed
        pause
        exit /b 1
    )
)
echo.

echo Step 4: Testing executable...
if exist "dist\CodeTantraAutomation.exe" (
    echo ✓ Executable created successfully
    echo File size: 
    dir "dist\CodeTantraAutomation.exe" | find "CodeTantraAutomation.exe"
) else (
    echo Error: Executable not found in dist folder
    pause
    exit /b 1
)
echo.

echo Step 5: Cleaning up build files...
if exist "build" rmdir /s /q build
if exist "CodeTantraAutomation.spec.bak" del /q CodeTantraAutomation.spec.bak
echo.

echo ==========================================
echo Build complete!
echo Executable location: dist\CodeTantraAutomation.exe
echo ==========================================
echo.

echo Next steps:
echo 1. Test the executable: dist\CodeTantraAutomation.exe
echo 2. Create installer: Run create_installer.bat
echo 3. Or manually use Inno Setup with installer.iss
echo.

pause

