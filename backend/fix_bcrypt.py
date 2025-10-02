"""
Fix bcrypt compatibility issues
Run this script to fix bcrypt installation
"""

import subprocess
import sys
import os

def fix_bcrypt():
    """Fix bcrypt compatibility issues"""
    print("Fixing bcrypt compatibility issues...")
    
    try:
        # Uninstall problematic packages
        print("1. Uninstalling problematic packages...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "bcrypt", "passlib"], 
                      check=False, capture_output=True)
        
        # Install compatible versions
        print("2. Installing compatible bcrypt version...")
        subprocess.run([sys.executable, "-m", "pip", "install", "bcrypt==4.0.1"], 
                      check=True)
        
        print("3. Installing passlib with bcrypt...")
        subprocess.run([sys.executable, "-m", "pip", "install", "passlib[bcrypt]==1.7.4"], 
                      check=True)
        
        print("bcrypt compatibility fixed!")
        print("You can now run the backend without issues.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error fixing bcrypt: {e}")
        print("Try running manually:")
        print("pip uninstall -y bcrypt passlib")
        print("pip install bcrypt==4.0.1")
        print("pip install passlib[bcrypt]==1.7.4")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    fix_bcrypt()
