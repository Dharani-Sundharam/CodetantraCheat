@echo off
echo Starting CodeTantra Automation Backend Server...
echo.
echo Make sure you have Python installed and all dependencies are installed.
echo Run: pip install -r requirements.txt
echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python start_server.py

pause
