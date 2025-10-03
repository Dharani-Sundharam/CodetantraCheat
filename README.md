# CodeTantra Automation

A powerful automation tool for CodeTantra platform that helps automate coding assignments and assessments.

## 🚀 Quick Start

### For Users:
1. **Download** `install.bat` and `run.bat` files
2. **Run** `install.bat` to clone repository and install dependencies
3. **Configure** your credentials in `CodeTantraAutomation/credentials.py`
4. **Run** `run.bat` to start the application

### For Developers:
1. **Clone** the repository: `git clone -b desktop-app <repository-url>`
2. **Install** Python 3.8+ and dependencies: `pip install -r requirements.txt`
3. **Configure** credentials in `credentials.py`
4. **Run** the application: `python desktop-app/main.py`

## 📋 System Requirements

- **Windows 10/11**
- **Python 3.8+**
- **Internet connection** (for API calls and browser installation)
- **Administrator rights** (for browser installation)

## 🛠️ Installation

### Automatic Installation (Recommended)
```bash
# Run the installer (clones repo and installs everything)
install.bat
```

### Manual Installation
```bash
# Clone the repository
git clone -b desktop-app <repository-url>
cd CodeTantraAutomation

# Install Python packages
pip install -r requirements.txt

# Install browsers
python -m playwright install firefox chromium webkit
```

## 🎯 Usage

### Starting the Application
```bash
# Simple way (from parent directory)
run.bat

# Or directly (from CodeTantraAutomation directory)
python desktop-app/main.py
```

### Configuration
1. **Edit** `CodeTantraAutomation/credentials.py` with your CodeTantra credentials
2. **Configure** `CodeTantraAutomation/config.py` for API settings
3. **Run** the application

## 🔒 Application Features

### Core Functionality
- **Automated problem solving** - Handles various question types
- **Browser automation** - Uses Playwright for reliable automation
- **API integration** - Real-time credit tracking and user management
- **Modern UI** - Dark-themed desktop interface

## 📁 Project Structure

```
CodeTantraAutomation/
├── desktop-app/              # Main application
│   ├── main.py              # Desktop UI
│   ├── automation_runner.py # Automation orchestrator
│   ├── code_question_handler.py # Code handling
│   ├── api_client.py        # API communication
│   ├── config_manager.py    # Configuration management
│   ├── config.py           # Application configuration
│   ├── credentials.py      # User credentials
│   ├── comment_remover.py  # Code processing utility
│   └── codetantra_playwright.py # Main automation logic
├── install.bat            # Installation script
├── run.bat               # Application launcher
└── README.md             # This file
```

## 🔧 Features

### Automation Capabilities
- **Code completion** questions
- **Multiple choice** questions  
- **Fill in the blank** questions
- **Automatic submission** and verification
- **Error handling** and retry logic

### User Interface
- **Modern dark theme** Tkinter interface
- **Real-time progress** tracking
- **Detailed reporting** and statistics
- **Credit system** integration
- **API connectivity** status

### Browser Automation
- **Playwright integration** for reliable automation
- **Multi-browser support** (Firefox, Chromium, WebKit)
- **Automatic browser** installation
- **Cross-platform** compatibility

## 📊 Credit System

The application includes a credit system that:
- **Tracks usage** by question type
- **Calculates costs** automatically
- **Integrates with API** for real-time deduction
- **Provides detailed** usage reports

### Credit Rates:
- **Code-based questions**: 5 credits
- **Non-code questions**: 3 credits
- **Failed/unsolved**: 1 credit

## 🛡️ Application Protection

### Built-in Features
1. **API Authentication**
   - Secure login system
   - Token-based authentication
   - User session management

2. **Credential Security**
   - Local credential storage
   - Password masking in UI
   - Secure configuration management

3. **Error Handling**
   - Comprehensive error catching
   - Graceful failure handling
   - User-friendly error messages

4. **Data Validation**
   - Input validation
   - Configuration verification
   - API response validation

## 🔧 Troubleshooting

### Common Issues

#### "Python not found"
- Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

#### "Packages not installed"
- Run `install.bat` to install all dependencies
- Or install manually: `pip install -r requirements.txt`

#### "Browser installation failed"
- Check internet connection
- Run as administrator
- Try manual installation: `python -m playwright install firefox`

#### "Application crashes or errors"
- Check Python version compatibility
- Verify all dependencies are installed
- Check configuration files for errors

### Getting Help
1. **Check** the troubleshooting section above
2. **Verify** system requirements
3. **Test** the application with sample data
4. **Contact** support if issues persist

## 📝 Configuration

### Credentials (`CodeTantraAutomation/credentials.py`)
```python
LOGIN_URL = "https://your-codetantra-url.com"
ANSWERS_ACCOUNT = {
    "username": "your_username",
    "password": "your_password"
}
TARGET_ACCOUNT = {
    "username": "your_username", 
    "password": "your_password"
}
```

### API Configuration (`CodeTantraAutomation/config.py`)
```python
API_BASE_URL = "https://your-api-url.com"
API_KEY = "your_api_key"
CREDIT_SYSTEM_ENABLED = True
```

## 🚨 Important Notes

### Legal and Ethical Use
- **Use responsibly** and in accordance with platform terms
- **Respect** academic integrity policies
- **Follow** local laws and regulations
- **Don't abuse** the automation system

### Best Practices
- **Keep credentials** secure and private
- **Don't share** your API keys
- **Use** official sources only
- **Test** with sample data first

## 📄 License

This project is for educational purposes only. Please use responsibly and in accordance with all applicable terms of service and laws.

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

## 📞 Support

For support and questions:
- **Check** the troubleshooting section
- **Review** the documentation
- **Open** an issue on GitHub
- **Contact** the development team

---

**CodeTantra Automation v1.0.0**  
*Automate with confidence, learn with integrity*