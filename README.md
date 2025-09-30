# Code Tantra Automation Tool

Python automation tool for Code Tantra using Selenium WebDriver with Firefox.

## ⚠️ Disclaimer

This tool is for **educational purposes only**. Use responsibly and in accordance with your institution's academic integrity policies.

## Features

- Opens two separate Firefox browser windows side-by-side
- Syncs both accounts to the same problem
- Automatically copies code from the "answers" account
- Pastes code into the target account
- Submits solutions and verifies success
- Processes multiple problems automatically
- Handles navigation between problems

## Requirements

- Python 3.7+
- Firefox browser installed
- geckodriver (automatically managed by webdriver-manager)

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Make sure Firefox is installed on your system

## Usage

### Option 1: Automatic Login (Recommended)

1. Copy the credentials template:
```bash
cp credentials.example.py credentials.py
```

2. Edit `credentials.py` with your actual credentials:
```python
ANSWERS_ACCOUNT = {
    'username': 'your_answers_account@rmd.ac.in',
    'password': 'your_password'
}

TARGET_ACCOUNT = {
    'username': 'your_target_account@rmd.ac.in',
    'password': 'your_password'
}
```

3. Run the script:
```bash
python codetantra_automation.py
```

4. The script will automatically:
   - Navigate to https://rmd.codetantra.com/login.jsp
   - Log in to both accounts
   - Wait for you to navigate to the problems section
   - Start automation when you press ENTER

### Option 2: Manual Login

1. Delete or rename `credentials.py`
2. Run the script:
```bash
python codetantra_automation.py
```
3. Follow the prompts:
   - Enter Code Tantra URL (optional)
   - **Log in manually** to both browser windows:
     - Left window: Account WITH answers
     - Right window: Account WITHOUT answers (target)
   - Press ENTER when both accounts are logged in
   - Specify number of problems to process (or ENTER for all)

## Key Features

- ✅ **Automatic login** with credentials from `credentials.py`
- ✅ **Smart scrolling** to find Next/Prev buttons anywhere on page
- ✅ Handles problem synchronization with Next/Prev buttons
- ✅ Extracts code from CodeMirror editor
- ✅ Pastes line-by-line to avoid issues
- ✅ Verifies successful submission (badge-success)
- ✅ Processes multiple problems automatically
- ✅ Side-by-side windows for easy monitoring
- ✅ Graceful error handling
- ✅ Customizable via `config.py`

## How It Works

1. **Synchronization**: Compares problem titles between both accounts using the button element with class `min-w-0 flex-1 text-left text-sm font-semibold hover:underline`

2. **Navigation**: Uses Next/Prev buttons with accesskey attributes to navigate between problems

3. **Code Extraction**: Reads content from CodeMirror editor (`div.cm-content[contenteditable='true']`)

4. **Code Pasting**: Writes to CodeMirror editor in target account, handling line-by-line to avoid issues

5. **Submission**: Clicks Submit button with class `btn no-animation btn-xs rounded !btn-success`

6. **Verification**: Checks for `badge-success` class to confirm successful submission

## Troubleshooting

- **Firefox not found**: Make sure Firefox is installed and in your PATH
- **Login fails**: Check credentials in `credentials.py` are correct
- **Elements not found**: Website structure may have changed; check CSS selectors in `config.py`
- **Paste not working**: The script uses keyboard shortcuts; ensure focus is on the editor
- **Next button not found**: The script now scrolls to find buttons; if still failing, check selector
- **Red lines issue**: The script replaces all content; unchangeable lines should remain as they are in the template

## Security Note

⚠️ **IMPORTANT**: The `credentials.py` file contains your passwords.
- Never commit this file to Git (it's in `.gitignore`)
- Keep it secure on your local machine
- Use strong, unique passwords
- Consider using environment variables for extra security

## Customization

You can modify the script to:
- Change browser window positions/sizes
- Add delays between actions
- Enable headless mode (uncomment the headless option)
- Add logging to file
- Handle different problem types

## Notes

- The script waits for manual login to avoid storing credentials
- Both browser windows are positioned side-by-side for easy monitoring
- Small delays are added between actions to ensure page loads
- The script gracefully handles errors and continues to next problems

## License

For educational use only.
