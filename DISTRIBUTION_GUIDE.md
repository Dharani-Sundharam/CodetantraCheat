# CodeTantra Automation - Distribution Guide

## 📦 How to Create a Distribution Package

### Step 1: Prepare the Files
Make sure you have all the necessary files in your project folder:

```
CodeTantraAutomation/
├── desktop-app/
│   ├── main.py
│   ├── automation_runner.py
│   ├── api_client.py
│   ├── config_manager.py
│   ├── code_question_handler.py
│   ├── comment_remover.py
│   ├── codetantra_playwright.py
│   ├── config.py
│   ├── credentials_template.py
│   └── credentials.py (empty template)
├── install.bat
├── run.bat
├── requirements.txt
├── README.md
└── DISTRIBUTION_GUIDE.md
```

### Step 2: Create the Zip Package
1. **Select all files** in the main folder
2. **Right-click** and choose "Send to" → "Compressed (zipped) folder"
3. **Name it** something like `CodeTantraAutomation_v1.0.zip`

### Step 3: Test the Distribution
1. **Extract** the zip to a test folder
2. **Run** `install.bat` to verify installation works
3. **Run** `run.bat` to verify the application starts
4. **Check** that disclaimer appears and credentials need setup

## 🎯 User Instructions (Include with Distribution)

### For End Users:
1. **Extract** the zip file to any folder
2. **Run** `install.bat` as Administrator (if needed)
3. **Copy** `desktop-app/credentials_template.py` to `desktop-app/credentials.py`
4. **Edit** `desktop-app/credentials.py` with your account details
5. **Run** `run.bat` to start the application
6. **Accept** the disclaimer to continue

### System Requirements:
- Windows 10/11
- Python 3.8+ (will be checked during installation)
- Internet connection (for browser installation)
- Administrator rights (for browser installation)

## ✅ Distribution Checklist

Before distributing, ensure:

- [ ] All source code is included
- [ ] `install.bat` works without Git
- [ ] `run.bat` works with local files
- [ ] `requirements.txt` is present
- [ ] `credentials_template.py` is included
- [ ] `credentials.py` is empty (no real credentials)
- [ ] README.md has zip distribution instructions
- [ ] Disclaimer is prominently displayed
- [ ] Test the complete installation process
- [ ] Verify the application starts correctly

## 🚨 Security Notes

- **Never include** real credentials in the distribution
- **Always use** the template file for credentials
- **Include** the disclaimer prominently
- **Test** that no accounts are pre-logged
- **Verify** that users must configure their own credentials

## 📋 Version Information

When creating a new distribution:
1. Update version numbers in relevant files
2. Update the README with any new features
3. Test the complete installation process
4. Create a new zip with version number in filename
5. Document any changes in a changelog

---

**Remember**: This software is for educational purposes only. Always include the disclaimer and ensure users understand the legal implications of use.
