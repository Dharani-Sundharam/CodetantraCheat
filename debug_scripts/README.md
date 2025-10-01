# 🔧 Debug Scripts

This folder contains utility and debug scripts for the CodeTantra Automation Tool.

## 📁 Scripts Overview

### **codemirror_test.py**
- **Purpose**: Test CodeMirror extraction and clipboard functionality
- **Features**: 
  - Auto-login to both accounts
  - Type 1/Type 2 detection using RESET button
  - Code extraction and clipboard testing
  - Smart extraction with comment detection
- **Usage**: `python codemirror_test.py`

### **debug_page.py**
- **Purpose**: Debug page elements and iframe detection
- **Features**:
  - Inspect page structure
  - Test iframe loading
  - Check element visibility
- **Usage**: `python debug_page.py`

### **debug_problem_number.py**
- **Purpose**: Debug problem number detection
- **Features**:
  - Test problem number extraction
  - Verify problem matching between accounts
- **Usage**: `python debug_problem_number.py`

### **test_connection.py**
- **Purpose**: Test account connections and login
- **Features**:
  - Test login to both accounts
  - Verify browser connectivity
  - Check iframe loading
- **Usage**: `python test_connection.py`

### **setup_playwright.py**
- **Purpose**: Setup and install Playwright browsers
- **Features**:
  - Install required browsers
  - Verify Playwright installation
  - Test browser compatibility
- **Usage**: `python setup_playwright.py`

### **playwright_codegen.py**
- **Purpose**: Generate Playwright code for testing
- **Features**:
  - Record browser interactions
  - Generate automation code
  - Test element selectors
- **Usage**: `python playwright_codegen.py`

## 🚀 Quick Debug Guide

### **1. Test Basic Connection**
```bash
python test_connection.py
```

### **2. Test CodeMirror Extraction**
```bash
python codemirror_test.py
```

### **3. Debug Page Elements**
```bash
python debug_page.py
```

### **4. Test Problem Detection**
```bash
python debug_problem_number.py
```

## 🔍 Troubleshooting

### **Common Debug Scenarios**

1. **Login Issues**
   - Run `test_connection.py`
   - Check credentials in main `credentials.py`
   - Verify browser compatibility

2. **Code Extraction Problems**
   - Run `codemirror_test.py`
   - Check iframe loading
   - Verify CodeMirror editor detection

3. **Page Element Issues**
   - Run `debug_page.py`
   - Inspect page structure
   - Check element selectors

4. **Problem Detection Issues**
   - Run `debug_problem_number.py`
   - Verify problem number extraction
   - Check account synchronization

## 📝 Debug Tips

- **Browser Console**: Check browser console for JavaScript errors
- **Element Inspector**: Use browser dev tools to inspect elements
- **Network Tab**: Check for failed requests or timeouts
- **Error Logs**: Review detailed error messages in console output

## ⚠️ Notes

- Debug scripts use the same credentials as the main tool
- Some scripts may require manual intervention
- Always test in a safe environment first
- Debug scripts are for troubleshooting only

---

**Happy Debugging! 🔧**
