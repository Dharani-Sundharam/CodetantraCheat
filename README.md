# CodeTantra Automation Tool

A powerful automation tool that intelligently handles different types of code completion problems on CodeTantra platform using Playwright browser automation.

## 🚀 Features

- **Smart Code Type Detection**: Automatically detects Type 1 (fully editable) vs Type 2 (template-based) code problems
- **Intelligent Code Extraction**: Extracts complete code from answers account with proper scrolling and zoom
- **Comment Removal**: Automatically cleans code by removing comments using language-specific patterns
- **Robust Error Handling**: Comprehensive error handling with detailed logging and fallback mechanisms
- **Multi-Language Support**: Supports Java, C++, C, Python, JavaScript, and more
- **Auto-Close Bracket Handling**: Smart handling of CodeMirror's auto-closing brackets and quotes
- **Progress Tracking**: Real-time progress monitoring with detailed console output

## 📁 Project Structure

```
CodeTantraCheat/
├── codetantra_playwright.py    # Main automation script
├── config.py                   # Configuration settings
├── credentials.py              # Login credentials (create this)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── scripts/                    # Additional scripts
│   ├── codetantra_automation.py
│   └── run.bat
├── utils/                      # Utility tools
│   ├── comment_remover.py
│   ├── interactive_comment_remover.py
│   ├── simple_comment_remover.py
│   ├── comment_remover.bat
│   └── question_type_detector.py
├── debug_scripts/              # Debug and testing tools
│   ├── codemirror_test.py
│   ├── debug_page.py
│   ├── debug_problem_number.py
│   ├── playwright_codegen.py
│   ├── setup_playwright.py
│   └── test_connection.py
└── docs/                       # Documentation
    ├── QUICK_START.md
    ├── SETUP_GUIDE.md
    └── [other documentation files]
```

## 🛠️ Installation

1. **Clone or download** this repository
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Create credentials file**:
   ```bash
   cp credentials_template.py credentials.py
   ```
4. **Edit credentials.py** with your CodeTantra login details

## ⚙️ Configuration

### 1. Credentials Setup
Create `credentials.py` with your login information:
```python
# CodeTantra login credentials
ANSWERS_ACCOUNT = {
    "username": "your_answers_username",
    "password": "your_answers_password"
}

TARGET_ACCOUNT = {
    "username": "your_target_username", 
    "password": "your_target_password"
}

LOGIN_URL = "https://your-codetantra-url.com"
```

### 2. Configuration Options
Edit `config.py` to customize:
- Browser settings
- Timing delays
- Error handling preferences
- Debug options

## 🚀 Usage

### Quick Start
```bash
python codetantra_playwright.py
```

### Advanced Usage
```bash
# Run with specific number of problems
python codetantra_playwright.py --problems 5

# Run with debug mode
python codetantra_playwright.py --debug

# Run with custom settings
python codetantra_playwright.py --answers-account user1 --target-account user2
```

## 🎯 How It Works

### 1. **Type Detection**
- Uses RESET button method to detect code type
- Type 1: Fully editable code (clear and paste)
- Type 2: Template-based code (comment static lines, then paste)

### 2. **Code Extraction**
- Maximizes browser window for better visibility
- Scrolls through entire editor to load all content
- Extracts code line by line with structure preservation

### 3. **Code Processing**
- Detects programming language automatically
- Removes comments using language-specific patterns
- Handles auto-closing brackets intelligently

### 4. **Code Pasting**
- Type 1: Direct paste with error handling
- Type 2: Comment static lines, then paste complete code
- Verifies successful pasting

### 5. **Submission & Verification**
- Submits solution with retry mechanism
- Verifies test case success
- Provides detailed progress reporting

## 🔧 Utility Tools

### Comment Remover
```bash
# Interactive mode
python utils/interactive_comment_remover.py

# Simple mode
python utils/simple_comment_remover.py

# Command line mode
python utils/comment_remover.py code.java -l java -o clean_code.java
```

### Question Type Detector
```bash
python utils/question_type_detector.py
```

## 📊 Supported Languages

- **Java** - Primary support with full auto-detection
- **C/C++** - Complete support with #include detection
- **Python** - Full support with def/import detection
- **JavaScript** - Complete support with function detection
- **And more** - Extensible language detection system

## 🐛 Debugging

### Debug Scripts
- `debug_scripts/codemirror_test.py` - Test CodeMirror extraction
- `debug_scripts/debug_page.py` - Debug page elements
- `debug_scripts/test_connection.py` - Test browser connection

### Console Output
The tool provides detailed console output:
```
Setting up Playwright browsers...
  Maximizing window and setting zoom to 60%...
  ✓ Window maximized and zoomed to 60%
✓ First browser window opened (answers account - left)

Extracting structured lines from answers account...
  Detected language: java
  Cleaning code using comment remover...
  ✓ Code cleaned - removed comments
  Total lines to type: 15
  Typing line 1/15: public class Main {
  ✓ Line 1 typed successfully
```

## ⚠️ Important Notes

1. **Educational Purpose Only**: This tool is for educational purposes
2. **Use Responsibly**: Follow your institution's academic integrity policies
3. **Browser Requirements**: Requires Firefox browser
4. **Network**: Stable internet connection required
5. **Credentials**: Keep your credentials secure

## 🔒 Security

- Credentials are stored locally in `credentials.py`
- No data is sent to external servers
- All processing happens locally on your machine

## 📝 Troubleshooting

### Common Issues

1. **Browser not launching**:
   - Install Firefox browser
   - Check Playwright installation: `playwright install firefox`

2. **Login failures**:
   - Verify credentials in `credentials.py`
   - Check if CodeTantra URL is correct

3. **Code not typing completely**:
   - Check browser zoom settings
   - Verify CodeMirror editor is accessible
   - Check console output for specific errors

4. **Submission failures**:
   - Ensure both accounts are on the same problem
   - Check if submit button is visible
   - Verify test case requirements

### Getting Help

1. Check console output for detailed error messages
2. Use debug scripts to isolate issues
3. Verify all dependencies are installed
4. Check browser and network connectivity

## 📄 License

This project is for educational purposes only. Use responsibly and in accordance with your institution's academic integrity policies.

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

---

**Disclaimer**: This tool is designed for educational purposes. Users are responsible for ensuring their use complies with their institution's academic integrity policies.