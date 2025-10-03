@echo off
title CodeTantra Automation
echo ================================================
echo CodeTantra Automation - Starting Application
echo ================================================
echo.

REM Check if application directory exists
if not exist "CodeTantraAutomation" (
    echo ERROR: CodeTantra Automation not found!
    echo Please run install.bat first to set up the application.
    pause
    exit /b 1
)

REM Navigate to application directory
cd CodeTantraAutomation

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ and run install.bat.
    pause
    exit /b 1
)

REM Check if packages are installed
python -c "import playwright, pyperclip, keyboard, requests" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Required packages not installed!
    echo Please run install.bat first to install dependencies.
    pause
    exit /b 1
)

echo Starting CodeTantra Automation...
echo.

REM Run the main application
python desktop-app\main.py

echo.
echo Application closed.
pause
