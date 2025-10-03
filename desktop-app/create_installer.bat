@echo off
echo Creating CodeTantra Automation Installer
echo =========================================
echo.

REM Check if Inno Setup is installed
set "INNO_SETUP_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "INNO_SETUP_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set "INNO_SETUP_PATH=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 5\ISCC.exe" (
    set "INNO_SETUP_PATH=C:\Program Files\Inno Setup 5\ISCC.exe"
)

if "%INNO_SETUP_PATH%"=="" (
    echo Error: Inno Setup not found!
    echo.
    echo Please install Inno Setup from: https://jrsoftware.org/isinfo.php
    echo Or download from: https://jrsoftware.org/download.php/is.exe
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo Found Inno Setup at: %INNO_SETUP_PATH%
echo.

REM Check if executable exists
if not exist "dist\CodeTantraAutomation.exe" (
    echo Error: Executable not found!
    echo Please run build_exe.bat first to create the executable.
    pause
    exit /b 1
)

echo Step 1: Creating installer directory...
if not exist "installer_output" mkdir installer_output
echo.

echo Step 2: Compiling installer with Inno Setup...
"%INNO_SETUP_PATH%" installer.iss
if errorlevel 1 (
    echo Error: Failed to create installer
    echo.
    echo Common issues:
    echo - Missing wizard image files (fixed in updated script)
    echo - File paths not found
    echo - Inno Setup version compatibility
    echo.
    echo Try running the installer script manually in Inno Setup Compiler
    pause
    exit /b 1
)
echo.

echo Step 3: Checking installer...
if exist "installer_output\CodeTantraAutomation_Setup_v1.0.0.exe" (
    echo ✓ Installer created successfully!
    echo.
    echo Installer location: installer_output\CodeTantraAutomation_Setup_v1.0.0.exe
    echo File size:
    dir "installer_output\CodeTantraAutomation_Setup_v1.0.0.exe" | find "CodeTantraAutomation_Setup_v1.0.0.exe"
    echo.
    echo You can now distribute this installer to users.
) else (
    echo Error: Installer not found in expected location
    echo Check installer_output folder for any generated files
)
echo.

pause
