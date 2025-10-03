@echo off
echo ================================================
echo CodeTantra Automation - Complete Build Process
echo ================================================
echo.

echo This script will:
echo 1. Build the executable
echo 2. Create the installer
echo 3. Show you the final results
echo.

set /p continue="Continue? (Y/N): "
if /i not "%continue%"=="Y" (
    echo Build cancelled.
    pause
    exit /b 0
)

echo.
echo ================================================
echo STEP 1: Building Executable
echo ================================================
call build_exe.bat
if errorlevel 1 (
    echo.
    echo ❌ Executable build failed!
    echo Please check the errors above and try again.
    pause
    exit /b 1
)

echo.
echo ================================================
echo STEP 2: Creating Installer
echo ================================================
call create_installer.bat
if errorlevel 1 (
    echo.
    echo ❌ Installer creation failed!
    echo Please check the errors above and try again.
    pause
    exit /b 1
)

echo.
echo ================================================
echo 🎉 BUILD COMPLETE!
echo ================================================
echo.

echo ✅ Executable: dist\CodeTantraAutomation.exe
if exist "dist\CodeTantraAutomation.exe" (
    for %%A in ("dist\CodeTantraAutomation.exe") do echo    Size: %%~zA bytes
)

echo.
echo ✅ Installer: installer_output\CodeTantraAutomation_Setup_v1.0.0.exe
if exist "installer_output\CodeTantraAutomation_Setup_v1.0.0.exe" (
    for %%A in ("installer_output\CodeTantraAutomation_Setup_v1.0.0.exe") do echo    Size: %%~zA bytes
)

echo.
echo 📋 Next Steps:
echo 1. Test the executable: dist\CodeTantraAutomation.exe
echo 2. Test the installer: installer_output\CodeTantraAutomation_Setup_v1.0.0.exe
echo 3. Distribute the installer to users
echo.

echo 🚀 Ready for distribution!
echo.

pause
