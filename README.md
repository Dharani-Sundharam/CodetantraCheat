# 🚀 CodeTantra Automation Tool

A powerful automation tool for CodeTantra that intelligently handles different types of coding problems with smart copy-paste functionality and automatic submission.

## ✨ Features

### 🎯 **Smart Problem Detection**
- **Type 1 Problems**: Fully editable code - complete replacement
- **Type 2 Problems**: Static code with editable sections - smart insertion
- **Automatic Detection**: Uses RESET button method for reliable type detection

### 🔧 **Intelligent Code Handling**
- **Fast Typing**: Ultra-fast code input with 1ms character delay
- **Auto-Close Bracket Handling**: Smart management of CodeMirror's auto-closing features
- **Strategy B for Type 2**: Comment static lines + type complete code
- **Error Recovery**: Skip problematic problems and continue

### 📝 **Code Completion Strategies**

#### **Type 1 (Fully Editable)**
1. Extract complete code from answers account
2. Clear target editor completely
3. Type complete code with auto-close handling
4. Clean up extra brackets (5-second Delete)
5. Submit and verify

#### **Type 2 (Static + Editable)**
1. Select all existing content
2. Comment everything with `Ctrl+/`
3. Move to end and add 3 new lines
4. Type complete code from answers
5. Clean up extra brackets (5-second Delete)
6. Submit and verify

### 🛡️ **Robust Error Handling**
- **Skip on Failure**: Automatically skips problematic problems
- **Retry Logic**: Up to 3 submission attempts with cleanup
- **Error Logging**: Detailed error tracking for each problem
- **Graceful Recovery**: Continue processing even if individual problems fail

### ✅ **Submission Verification**
- **Test Case Success**: Checks for "out of X test case(s) passed"
- **Multiple Patterns**: Handles hidden and shown test cases
- **Success Confirmation**: Verifies submission before moving to next problem

## 🚀 Quick Start

### **Prerequisites**
```bash
pip install -r requirements.txt
```

### **Configuration**
1. Update `credentials.py` with your login details:
```python
ANSWERS_ACCOUNT = {
    "email": "your_answers_email@example.com",
    "password": "your_password"
}

TARGET_ACCOUNT = {
    "email": "your_target_email@example.com", 
    "password": "your_password"
}
```

### **Run Automation**
```bash
python codetantra_playwright.py
```

## 📁 Project Structure

```
CodetantraCheat/
├── codetantra_playwright.py    # Main automation script
├── credentials.py              # Login credentials
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows batch file
├── README.md                   # This file
├── QUICK_START.md             # Quick start guide
├── SETUP_GUIDE.md             # Detailed setup guide
└── debug_scripts/             # Debug and utility scripts
    ├── codemirror_test.py     # CodeMirror testing
    ├── debug_page.py          # Page debugging
    ├── debug_problem_number.py # Problem number debugging
    ├── test_connection.py     # Connection testing
    └── setup_playwright.py    # Playwright setup
```

## 🎯 How It Works

### **1. Problem Detection**
- Uses RESET button to determine if code is fully editable (Type 1) or has static sections (Type 2)
- Automatically detects the problem type and applies appropriate strategy

### **2. Code Extraction**
- Extracts complete code from answers account
- Handles CodeMirror editor within iframe
- Preserves exact formatting and structure

### **3. Smart Pasting**
- **Type 1**: Complete code replacement
- **Type 2**: Comment static lines + add complete code below
- Ultra-fast typing with auto-close bracket handling

### **4. Submission & Verification**
- Automatic submission with retry logic
- 5-second Delete cleanup to remove extra brackets
- Verification using test case success messages
- Skip problematic problems and continue

## ⚙️ Configuration Options

### **Speed Settings**
- **Character Delay**: 1ms (ultra-fast)
- **Line Break Delay**: 5ms (very fast)
- **Cleanup Duration**: 5 seconds (thorough)

### **Error Handling**
- **Max Retries**: 3 attempts per submission
- **Skip on Error**: Automatically skip problematic problems
- **Error Logging**: Detailed error tracking

### **Verification Patterns**
- `"out of 1 hidden test case(s) passed"`
- `"out of 2 shown test case(s) passed"`
- `"test case(s) passed"` (general pattern)
- `"Test case passed successfully"` (fallback)

## 🔧 Troubleshooting

### **Common Issues**

1. **Login Problems**
   - Check credentials in `credentials.py`
   - Ensure accounts are accessible
   - Verify browser compatibility

2. **Code Not Pasting**
   - Tool automatically falls back to fast typing
   - Check iframe loading in browser
   - Verify CodeMirror editor detection

3. **Submission Failures**
   - Tool automatically retries with cleanup
   - Check for submit button availability
   - Verify test case success patterns

4. **Problem Skipping**
   - Normal behavior for problematic problems
   - Check error log for details
   - Tool continues with next problem

### **Debug Mode**
Use scripts in `debug_scripts/` folder for troubleshooting:
- `codemirror_test.py`: Test CodeMirror extraction
- `debug_page.py`: Debug page elements
- `test_connection.py`: Test account connections

## 📊 Performance

- **Typing Speed**: ~1000 characters per second
- **Problem Processing**: ~30-60 seconds per problem
- **Error Recovery**: Automatic skip and continue
- **Success Rate**: High with automatic retry logic

## 🛡️ Safety Features

- **Error Isolation**: Problems fail independently
- **Graceful Degradation**: Continue processing on errors
- **Detailed Logging**: Track all issues and successes
- **Automatic Cleanup**: Remove extra characters before submission

## 📈 Usage Statistics

The tool tracks and reports:
- ✅ **Problems Solved**: Successfully completed
- ⚠️ **Problems Skipped**: Failed but continued
- ❌ **Problems Failed**: Critical failures
- 📝 **Error Log**: Detailed error information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes only. Please use responsibly and in accordance with CodeTantra's terms of service.

## ⚠️ Disclaimer

This tool is designed for educational and testing purposes. Users are responsible for ensuring compliance with CodeTantra's terms of service and academic integrity policies.

---

**Happy Coding! 🚀**