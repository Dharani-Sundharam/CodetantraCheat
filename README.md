# CodeTantra Automation Desktop App

## Overview

This is the desktop application branch containing the Tkinter-based desktop client for the CodeTantra Automation Service. This branch focuses on the local automation tool that connects to the web API for credits management.

## Components

### Desktop Application (`desktop-app/`)
- **Tkinter GUI** with professional dark theme
- **API Client** for backend communication
- **Config Manager** for local settings storage
- **Automation Runner** that integrates with the core automation
- **Windows Installer** script for easy distribution

### Core Automation (`codetantra_playwright.py`)
- **Playwright-based** automation engine
- **Smart problem detection** and solving
- **Multi-language support** (Java, C++, Python, etc.)
- **Code completion** and multiple choice handling
- **Error handling** and retry mechanisms

### Configuration Files
- **config.py** - Main configuration settings
- **credentials.py** - Account credentials (auto-generated)
- **requirements.txt** - Python dependencies

## Features

- Professional dark themed interface
- Secure API-based authentication
- Real-time automation logging
- Automatic credit deduction
- Local configuration storage
- Problem success tracking
- Report generation
- Windows installer support

## Quick Start

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd CodetantraCheat

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install firefox

# Run the application
python desktop-app/main.py
```

### Building Executable
```bash
cd desktop-app
pip install -r requirements.txt
playwright install firefox
build_exe.bat  # Windows
# Or manually:
pyinstaller --onefile --windowed --name CodeTantraAutomation --icon=icon.ico main.py
```

## Configuration

### API Settings
Update the API URL in `desktop-app/api_client.py`:
```python
def __init__(self, base_url: str = "https://your-api-domain.com"):
```

### Automation Settings
The app stores settings in:
- Windows: `%APPDATA%\CodeTantraAutomation\`
- Mac/Linux: `~/.codetantra_automation/`

### Credentials
Credentials are managed through the GUI and stored securely in AppData.

## Usage

### First Time Setup
1. Launch the application
2. Login with your web account credentials
3. Enter CodeTantra URL and account details
4. Set number of problems to solve
5. Click "Start Automation"

### Configuration Fields
- **CodeTantra URL**: Your institution's CodeTantra URL
- **Answers Account**: Account with correct solutions
- **Target Account**: Account to submit solutions to
- **Number of Problems**: How many problems to solve (0 for all)

### Credits System
- Code completion success: 5 credits
- Other problems success: 3 credits
- Failed problem: 1 credit
- Credits are deducted automatically via API

## File Structure

```
desktop-app/
├── main.py              - Main GUI application
├── api_client.py        - API communication
├── config_manager.py    - Settings management
├── automation_runner.py - Automation integration
├── installer.iss        - Windows installer script
├── build_exe.bat        - Build automation
├── requirements.txt     - Dependencies
└── README.md           - This file

Core Files:
├── codetantra_playwright.py - Main automation engine
├── config.py               - Configuration
├── credentials.py          - Account credentials
└── requirements.txt        - Dependencies
```

## Building for Distribution

### Step 1: Create Executable
```bash
cd desktop-app
build_exe.bat
```

### Step 2: Create Installer
1. Install Inno Setup from https://jrsoftware.org/isinfo.php
2. Open `installer.iss` in Inno Setup Compiler
3. Click "Build" > "Compile"
4. Installer created in `installer_output/`

### Step 3: Upload to GitHub Releases
1. Create new release on GitHub
2. Upload installer .exe file
3. Add release notes

## API Integration

The desktop app connects to the web API for:
- User authentication
- Credits management
- Usage tracking
- Problem reporting

Default API URL: `http://localhost:8000`

For production, update the API URL in `api_client.py`.

## Troubleshooting

### Common Issues

**Cannot connect to API**
- Check if backend server is running
- Verify API URL in settings
- Check internet connection

**Login fails**
- Verify email and password
- Check if account is verified
- Ensure backend is accessible

**Automation errors**
- Check CodeTantra credentials
- Verify Playwright browsers are installed
- Check logs in AppData folder

**Insufficient credits**
- Purchase more credits on website
- Check current balance in header

### Logs

Logs are saved to:
```
%APPDATA%\CodeTantraAutomation\logs\
```

Each automation run creates a new log file with timestamp.

## Development

### Adding Features
1. Create new module in desktop-app/
2. Import in main.py
3. Add UI elements in show_main_screen()
4. Test thoroughly

### Project Structure
- `main.py` - Main GUI application
- `api_client.py` - API communication
- `config_manager.py` - Settings management
- `automation_runner.py` - Automation integration

## Security

- Credentials stored locally only
- Passwords not sent to any server except authentication
- Token stored securely in AppData
- All API communication uses HTTPS in production

## Updates

The app checks for updates from GitHub Releases.

To update manually:
1. Download latest installer
2. Run installer (upgrades existing installation)

## Support

For issues:
1. Check logs in AppData folder
2. Verify API connection
3. Contact support with log files

## License

Educational purposes only. Use responsibly.

---

**Note:** This is the desktop app branch. For the complete system with web platform, see the main branch.