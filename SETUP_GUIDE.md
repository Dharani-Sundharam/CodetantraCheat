# Complete Setup Guide - Code Tantra Automation

## 📋 What You Need

- Windows PC (or Mac/Linux with minor adjustments)
- Python 3.7 or higher installed
- Firefox browser installed
- Two Code Tantra accounts:
  - One with completed problems (answers)
  - One where you want to submit

## 🎯 Your Accounts

Based on your setup:
- **Answers Account**: `mfra.ece2024@rmd.ac.in`
- **Target Account**: `gdha.ece2024@rmd.ac.in`
- **Login URL**: https://rmd.codetantra.com/login.jsp

## 📦 Installation

### Step 1: Verify Python
Open Command Prompt (cmd) and type:
```bash
python --version
```
You should see Python 3.7 or higher. If not, download from [python.org](https://www.python.org/)

### Step 2: Install Dependencies
In your project folder, run:
```bash
pip install -r requirements.txt
```

This installs:
- `selenium` - Browser automation
- `webdriver-manager` - Automatic Firefox driver management

### Step 3: Verify Firefox
Make sure Firefox is installed on your computer. The script uses Firefox because Code Tantra allows copy-paste in Firefox browsers.

## 🔐 Configure Credentials

Your credentials are already set in `credentials.py`:

```python
LOGIN_URL = "https://rmd.codetantra.com/login.jsp"

ANSWERS_ACCOUNT = {
    'username': 'mfra.ece2024@rmd.ac.in',
    'password': 'Rmdec@2001'
}

TARGET_ACCOUNT = {
    'username': 'gdha.ece2024@rmd.ac.in',
    'password': 'Dharani$#@!1'
}
```

**⚠️ SECURITY WARNING**:
- Never share `credentials.py`
- Never commit it to Git (it's in `.gitignore`)
- Keep it secure on your local machine

## 🚀 Running the Tool

### Quick Start (Using run.bat)
1. Double-click `run.bat`
2. Wait for two Firefox windows to open
3. Wait for automatic login to complete
4. Navigate both accounts to the problems section
5. Press ENTER when ready

### Manual Start
```bash
python codetantra_automation.py
```

## 📺 What to Expect

### When Script Starts:
```
============================================================
CODE TANTRA AUTOMATION TOOL
Educational Purpose Only
============================================================
Setting up Firefox browsers...
✓ First Firefox window opened (answers account - left)
✓ Second Firefox window opened (target account - right)

Using automatic login with credentials from credentials.py
Navigating to: https://rmd.codetantra.com/login.jsp
```

### During Login:
```
Logging in to Answers Account...
  ✓ Username entered: mfra.ece2024@rmd.ac.in
  ✓ Password entered
  ✓ Login button clicked
✓ Successfully logged in to Answers Account

Logging in to Target Account...
  ✓ Username entered: gdha.ece2024@rmd.ac.in
  ✓ Password entered
  ✓ Login button clicked
✓ Successfully logged in to Target Account
```

### Ready to Automate:
```
============================================================
Please navigate both accounts to the problems section
Press ENTER when both are ready to start automation...
```

**At this point:**
1. In the **LEFT window** (answers account), navigate to the programming problems
2. In the **RIGHT window** (target account), navigate to the same problems section
3. Press ENTER in the command prompt

### During Automation:
```
============================================================
PROCESSING NEW PROBLEM
============================================================
Synchronizing problems...
  Answers account: Understanding Date class
  Target account:  Understanding Date class
✓ Both accounts are on the same problem

Extracting code from answers account...
✓ Extracted 25 lines of code
Pasting code to target account...
✓ Code pasted successfully
Submitting solution...
✓ Submit button clicked
Checking submission result...
✓ Submission SUCCESSFUL! Time: 00:30

✓ Problem 1 completed successfully!

Moving to next problem...
✓ Moved to next problem
```

## 🎮 Controls

- **Press Ctrl+C** at any time to stop the automation
- The script will complete the current problem before stopping
- You can watch both windows to monitor progress

## 🔧 Troubleshooting

### Login Fails
**Problem**: Script says "Login may have failed"
**Solutions**:
1. Check credentials in `credentials.py` are correct
2. Try logging in manually in a browser first
3. Check if account is locked or requires password reset

### Can't Find Next Button
**Problem**: "Could not find Next button"
**Solutions**:
1. Script now auto-scrolls - give it a moment
2. Make sure you're on the problems page
3. Some pages might not have Next button (end of list)

### Code Not Pasting
**Problem**: Code doesn't appear in target account
**Solutions**:
1. Make sure Firefox is being used (not Chrome)
2. Check if Code Tantra page has loaded completely
3. Try increasing delays in `config.py`

### Submission Fails
**Problem**: Submission shows error or timeout
**Solutions**:
1. Check if the code in answers account is actually correct
2. Some problems have specific requirements
3. Website might be slow - increase `SUBMIT_DELAY` in `config.py`

### Firefox Doesn't Open
**Problem**: Script fails to start Firefox
**Solutions**:
1. Make sure Firefox is installed
2. Restart your computer
3. Try reinstalling Firefox
4. Check if geckodriver needs updating: `pip install --upgrade selenium`

## ⚙️ Customization

Edit `config.py` to change:

```python
# Window sizes
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 1080

# Timing (in seconds)
SYNC_DELAY = 2
SUBMIT_DELAY = 3
PAGE_LOAD_DELAY = 2

# Maximum sync attempts
MAX_SYNC_ATTEMPTS = 20
```

## 📊 Features Explained

### 1. Smart Scrolling
The script automatically scrolls to find buttons anywhere on the page. If Next/Prev/Submit buttons are below the fold, it will find them.

### 2. Problem Synchronization
Compares the problem titles in both accounts to ensure they're working on the same problem. Automatically navigates if they're different.

### 3. Code Extraction
Reads code from the CodeMirror editor in the answers account, preserving formatting and special characters.

### 4. Intelligent Pasting
Pastes code line-by-line to avoid issues with special characters or formatting.

### 5. Submission Verification
Checks for the green success badge to confirm submission worked. Continues even if some fail.

## 📝 Best Practices

1. **Start Small**: Test with 1-2 problems first
2. **Monitor Progress**: Watch both windows during execution
3. **Backup Work**: Keep a copy of your code elsewhere
4. **Academic Integrity**: Use responsibly for learning purposes
5. **Keep Updated**: Update dependencies occasionally with `pip install --upgrade -r requirements.txt`

## 🆘 Getting Help

If you encounter issues:

1. Check this guide first
2. Look at error messages in the console
3. Try running with fewer problems first
4. Check Code Tantra website hasn't changed structure
5. Verify credentials are correct

## 📚 Files Overview

- `codetantra_automation.py` - Main script
- `credentials.py` - Your login credentials (keep secure!)
- `config.py` - Timing and selector settings
- `requirements.txt` - Python dependencies
- `run.bat` - Windows quick-start script
- `README.md` - Full documentation
- `QUICK_START.md` - Quick reference
- `SETUP_GUIDE.md` - This file

## ✅ Success Checklist

Before running, verify:
- [ ] Python installed and working
- [ ] Firefox installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `credentials.py` exists with correct credentials
- [ ] Both accounts can log in manually
- [ ] Both accounts have access to problems section

## 🎓 Educational Note

This tool is for **educational purposes only**. It demonstrates:
- Web automation with Selenium
- Browser interaction
- HTML element detection
- Multi-window coordination
- Error handling in Python

Use it responsibly and in accordance with your institution's policies.

---

Good luck with your automation! 🚀
