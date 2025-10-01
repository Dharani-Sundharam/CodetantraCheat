"""
Setup script for Playwright automation
"""

import subprocess
import sys
import os

def install_requirements():
    """Install Python requirements"""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_playwright.txt"])
        print("✓ Python requirements installed")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False
    return True

def install_playwright_browsers():
    """Install Playwright browsers"""
    print("Installing Playwright browsers...")
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "firefox"])
        print("✓ Playwright browsers installed")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install browsers: {e}")
        return False
    return True

def main():
    """Main setup function"""
    print("="*60)
    print("PLAYWRIGHT AUTOMATION SETUP")
    print("="*60)
    
    # Check if credentials.py exists
    if not os.path.exists("credentials.py"):
        print("⚠ credentials.py not found!")
        print("Please create credentials.py with your login details:")
        print("""
LOGIN_URL = "https://rmd.codetantra.com/login.jsp"

ANSWERS_ACCOUNT = {
    'username': 'your_answers_email@domain.com',
    'password': 'your_answers_password'
}

TARGET_ACCOUNT = {
    'username': 'your_target_email@domain.com', 
    'password': 'your_target_password'
}
""")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Install browsers
    if not install_playwright_browsers():
        return
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("You can now run:")
    print("  python codetantra_playwright.py     # Main automation")
    print("  python playwright_codegen.py        # Element inspector")
    print("="*60)

if __name__ == "__main__":
    main()
