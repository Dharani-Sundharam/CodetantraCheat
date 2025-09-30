"""
Configuration file for Code Tantra Automation
Modify these settings as needed
"""

# Browser Settings
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 1080
HEADLESS_MODE = False  # Set to True to run browsers in background

# Timing Settings (in seconds)
SYNC_DELAY = 2  # Delay after clicking Next/Prev during sync
SUBMIT_DELAY = 3  # Delay after clicking Submit
PAGE_LOAD_DELAY = 2  # Delay after moving to next problem
LINE_PASTE_DELAY = 0.05  # Delay between pasting each line

# Retry Settings
MAX_SYNC_ATTEMPTS = 20  # Maximum attempts to sync problems
RESULT_WAIT_TIMEOUT = 10  # Seconds to wait for submission result

# CSS Selectors (update these if website structure changes)
SELECTORS = {
    'problem_title': 'button.min-w-0.flex-1.text-left.text-sm.font-semibold.hover\\:underline',
    'next_button': "button.btn.btn-xs.btn-info.rounded.gap-0[accesskey='n']",
    'prev_button': "button.btn.btn-xs.btn-info.rounded.gap-0[accesskey='p']",
    'editor': "div.cm-content[contenteditable='true']",
    'editor_lines': "div.cm-line",
    'submit_button': "button.btn.no-animation.btn-xs.rounded.\\!btn-success[accesskey='s']",
    'success_badge': "div.badge.badge-secondary.badge-sm.badge-success",
    'error_badge': "div.badge.badge-secondary.badge-sm.badge-error",
}

# Logging
VERBOSE = True  # Set to False for less output
