
"""
CodeTantra Automation Tool - Easy Runner
Run the main automation script with proper error handling
"""

import sys
import os
import asyncio
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if credentials file exists
    if not Path("credentials.py").exists():
        print("❌ credentials.py not found!")
        print("📝 Please create credentials.py from credentials_template.py")
        print("   Copy credentials_template.py to credentials.py and fill in your details")
        return False
    
    # Check if main script exists
    if not Path("codetantra_playwright.py").exists():
        print("❌ codetantra_playwright.py not found!")
        return False
    
    print("✅ All requirements met!")
    return True

def main():
    """Main function"""
    print("🚀 CodeTantra Automation Tool")
    print("=" * 40)
    
    if not check_requirements():
        print("\n❌ Setup incomplete. Please fix the issues above.")
        return 1
    
    try:
        # Import and run the main automation
        from codetantra_playwright import CodeTantraPlaywrightAutomation
        
        print("\n🎯 Starting automation...")
        print("Press Ctrl+C to stop at any time")
        print("-" * 40)
        
        # Create automation instance
        automation = CodeTantraPlaywrightAutomation(auto_login=True)
        
        # Run the automation
        asyncio.run(automation.run_automation())
        
        print("\n✅ Automation completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Automation stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("📝 Check the console output above for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())
