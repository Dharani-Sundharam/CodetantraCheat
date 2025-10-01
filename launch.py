#!/usr/bin/env python3
"""
CodeTantra Automation Tool - Universal Launcher
Choose between different UI options
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed"""
    missing = []
    
    try:
        import streamlit
    except ImportError:
        missing.append("streamlit")
    
    try:
        import pandas
    except ImportError:
        missing.append("pandas")
    
    try:
        import plotly
    except ImportError:
        missing.append("plotly")
    
    return missing

def install_dependencies():
    """Install missing dependencies"""
    print("📦 Installing missing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def launch_basic_ui():
    """Launch the basic UI"""
    print("🎨 Launching Basic UI...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 UI stopped")

def launch_advanced_ui():
    """Launch the advanced UI"""
    print("🚀 Launching Advanced UI...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app_advanced.py",
            "--server.port", "8502",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 UI stopped")

def launch_terminal():
    """Launch the terminal version"""
    print("💻 Launching Terminal Version...")
    try:
        subprocess.run([sys.executable, "run.py"])
    except KeyboardInterrupt:
        print("\n👋 Terminal version stopped")

def main():
    """Main launcher function"""
    print("🎯 CodeTantra Automation Tool - Universal Launcher")
    print("=" * 60)
    
    # Check if main files exist
    if not Path("codetantra_playwright.py").exists():
        print("❌ Main automation script not found!")
        return 1
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"📦 Missing dependencies: {', '.join(missing)}")
        if input("Install missing dependencies? (y/n): ").lower() == 'y':
            if not install_dependencies():
                return 1
        else:
            print("❌ Cannot proceed without dependencies")
            return 1
    
    # Show options
    print("\n🎨 Choose your interface:")
    print("1. 🌟 Basic UI (Simple & Clean)")
    print("2. 🚀 Advanced UI (Full Featured)")
    print("3. 💻 Terminal UI (Command Line)")
    print("4. ❌ Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            launch_basic_ui()
            break
        elif choice == "2":
            launch_advanced_ui()
            break
        elif choice == "3":
            launch_terminal()
            break
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
