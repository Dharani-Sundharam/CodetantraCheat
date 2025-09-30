# Quick Start Guide

## 🚀 Get Started in 4 Steps

### Step 1: Install Dependencies
Double-click `run.bat` or run:
```bash
pip install -r requirements.txt
```

### Step 2: Setup Credentials
```bash
# Copy the example file
cp credentials.example.py credentials.py

# Edit credentials.py with your accounts
notepad credentials.py
```

Put your actual credentials:
- **Answers account**: The account WITH completed problems
- **Target account**: The account WHERE you want to submit

### Step 3: Run the Tool
```bash
python codetantra_automation.py
```

### Step 4: Watch It Work!
1. Two Firefox windows will open side-by-side
2. Script will automatically log in to both accounts
3. Navigate both to the problems section (e.g., Java programming assignments)
4. Press ENTER when both are on the problem list
5. Sit back and watch the automation work!

## 🔄 Alternative: Manual Login

If you don't want to save credentials:
1. Delete `credentials.py`
2. Run the script
3. Log in manually when prompted

## 💡 Tips

- Make sure both accounts start at the problem list
- The left account should have completed problems (with answers)
- The right account should have incomplete problems
- You can stop anytime with `Ctrl+C`
- The script will show progress for each problem

## 🎯 What It Does

1. **Syncs** - Makes sure both accounts are on the same problem
2. **Copies** - Extracts code from the answers account
3. **Pastes** - Inputs code into the target account
4. **Submits** - Clicks the submit button
5. **Verifies** - Checks for the green success badge
6. **Repeats** - Moves to next problem automatically

## ⚠️ Common Issues

**Problem: Firefox doesn't open**
- Make sure Firefox is installed
- Restart your computer

**Problem: Can't find elements**
- Website structure may have changed
- Check CSS selectors in `config.py`

**Problem: Paste doesn't work**
- Code Tantra allows copy-paste in Firefox (that's why we use it)
- Make sure you're using Firefox, not Chrome

**Problem: Submission fails**
- Check if the code is correct in the answers account
- Some problems may have specific requirements

## 🛠️ Customization

Edit `config.py` to change:
- Window sizes and positions
- Timing delays
- CSS selectors (if website updates)
- Verbose logging level

Enjoy! 🎉
