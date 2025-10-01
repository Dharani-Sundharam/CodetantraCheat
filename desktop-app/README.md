# CodeTantra Automation Desktop App

Professional desktop application for automating CodeTantra problems with dark themed UI.

## Features

- Dark themed professional interface
- API integration for credits management
- Real-time automation logging
- Secure credential storage in AppData
- Automatic credit deduction
- Problem success tracking
- Detailed reporting

## Installation

### From Installer (Recommended)
1. Download the latest installer from GitHub Releases
2. Run `CodeTantraAutomation_Setup_v1.0.0.exe`
3. Follow the installation wizard
4. Launch from Start Menu or Desktop shortcut

### From Source
```bash
cd desktop-app
pip install -r requirements.txt
python main.py
```

## Building from Source

### Prerequisites
- Python 3.8 or higher
- Playwright browsers installed

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install firefox
```

### Running
```bash
python main.py
```

## Creating Installer

### Using PyInstaller
```bash
# Create executable
pyinstaller --onefile --windowed --name CodeTantraAutomation --icon=icon.ico main.py

# Executable will be in dist/ folder
```

### Using Inno Setup
1. Install Inno Setup from https://jrsoftware.org/isinfo.php
2. Open `installer.iss` in Inno Setup Compiler
3. Click Build > Compile
4. Installer will be created in `installer_output/` folder

## Configuration

The app stores data in:
- Windows: `%APPDATA%\CodeTantraAutomation\`
- Mac/Linux: `~/.codetantra_automation/`

Folders created:
- `config/` - User settings and credentials
- `logs/` - Automation logs

## Usage

### First Time Setup
1. Launch the application
2. Login with your account credentials
3. Enter CodeTantra URL and credentials
4. Set number of problems to solve
5. Click "Start Automation"

### Configuration Fields
- **CodeTantra URL**: Your institution's CodeTantra URL
- **Answers Account**: Account with correct solutions
- **Target Account**: Account to submit solutions to
- **Number of Problems**: How many problems to solve

### Credits System
- Code completion success: 5 credits
- Other problems success: 3 credits
- Failed problem: 1 credit

## API Configuration

Default API URL: `http://localhost:8000`

To change:
1. Edit `api_client.py`
2. Update `base_url` in `__init__` method

For production:
```python
self.base_url = "https://your-api-domain.com"
```

## Troubleshooting

### Cannot connect to API
- Check if backend server is running
- Verify API URL in settings
- Check internet connection

### Login fails
- Verify email and password
- Check if account is verified
- Ensure backend is accessible

### Automation errors
- Check CodeTantra credentials
- Verify Playwright browsers are installed
- Check logs in AppData folder

### Insufficient credits
- Purchase more credits on website
- Check current balance in header

## Logs

Logs are saved to:
```
%APPDATA%\CodeTantraAutomation\logs\
```

Each automation run creates a new log file with timestamp.

## Updates

The app checks for updates from GitHub Releases.

To update manually:
1. Download latest installer
2. Run installer (it will upgrade existing installation)

## Development

### Project Structure
```
desktop-app/
├── main.py              - Main GUI application
├── api_client.py        - API communication
├── config_manager.py    - Settings management
├── automation_runner.py - Automation integration
├── requirements.txt     - Dependencies
├── installer.iss        - Installer script
└── README.md           - This file
```

### Adding Features
1. Create new module in desktop-app/
2. Import in main.py
3. Add UI elements in show_main_screen()
4. Test thoroughly

## Building for Distribution

### Step 1: Create Executable
```bash
pyinstaller --onefile --windowed --name CodeTantraAutomation --icon=icon.ico main.py
```

### Step 2: Test Executable
```bash
cd dist
CodeTantraAutomation.exe
```

### Step 3: Create Installer
```bash
# Open installer.iss in Inno Setup
# Click Compile
```

### Step 4: Upload to GitHub Releases
1. Create new release on GitHub
2. Upload installer .exe file
3. Add release notes

## Security

- Credentials are stored locally only
- Passwords are not sent to any server except authentication
- Token is stored in AppData
- All API communication uses HTTPS in production

## License

Educational purposes only. Use responsibly.

## Support

For issues:
1. Check logs in AppData folder
2. Verify API connection
3. Contact support with log files

