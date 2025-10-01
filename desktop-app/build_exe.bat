@echo off
echo Building CodeTantra Automation Desktop App
echo ==========================================
echo.

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
pyinstaller --onefile --windowed --name CodeTantraAutomation --icon=icon.ico main.py
if errorlevel 1 (
    echo Error: Failed to create executable
    pause
    exit /b 1
)
echo.

echo Step 4: Cleaning up build files...
rmdir /s /q build
del /q CodeTantraAutomation.spec
echo.

echo ==========================================
echo Build complete!
echo Executable location: dist\CodeTantraAutomation.exe
echo ==========================================
echo.

echo Next steps:
echo 1. Test the executable in dist\ folder
echo 2. Use Inno Setup to create installer
echo 3. Upload to GitHub Releases
echo.

pause

