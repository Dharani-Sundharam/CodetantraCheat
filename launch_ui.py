#!/usr/bin/env python3
"""
CodeTantra Automation Tool - UI Launcher
Launches the modern web interface
"""

import subprocess
import sys
import os
from pathlib import Path

def check_streamlit():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_streamlit():
    """Install Streamlit if not available"""
    print("📦 Installing Streamlit...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit==1.28.0"])
        print("✅ Streamlit installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Streamlit")
        return False

def launch_ui():
    """Launch the Streamlit UI"""
    print("🚀 Launching CodeTantra Automation UI...")
    print("🌐 The interface will open in your default browser")
    print("📱 If it doesn't open automatically, go to: http://localhost:8501")
    print("⏹️ Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Launch Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 UI server stopped")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")

def main():
    """Main function"""
    print("🎨 CodeTantra Automation Tool - Modern UI")
    print("=" * 50)
    
    # Check if app.py exists
    if not Path("app.py").exists():
        print("❌ app.py not found!")
        print("📝 Make sure you're in the correct directory")
        return 1
    
    # Check if Streamlit is installed
    if not check_streamlit():
        print("📦 Streamlit not found. Installing...")
        if not install_streamlit():
            print("❌ Failed to install Streamlit. Please install manually:")
            print("   pip install streamlit==1.28.0")
            return 1
    
    # Launch the UI
    launch_ui()
    return 0

if __name__ == "__main__":
    sys.exit(main())
