@echo off
echo 🧹 Comment Remover - Choose Mode
echo ================================
echo.
echo 1. Simple Mode (Press Enter twice when done)
echo 2. Interactive Mode (Type END when done)
echo 3. Command Line Mode
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    python simple_comment_remover.py
) else if "%choice%"=="2" (
    python interactive_comment_remover.py
) else if "%choice%"=="3" (
    echo.
    echo Usage: python comment_remover.py [file] [-l language] [-o output]
    echo Example: python comment_remover.py code.java -l java -o clean_code.java
    echo.
    pause
) else (
    echo Invalid choice!
    pause
)
