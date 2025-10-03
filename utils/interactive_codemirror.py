"""
Interactive CodeMirror Copy Tool
Keeps browser open and allows you to copy CodeMirror content on demand
Press ENTER to copy current CodeMirror content to clipboard
Press 'q' + ENTER to quit
"""

import asyncio
from playwright.async_api import async_playwright
import pyperclip
import sys
import re

try:
    from credentials import LOGIN_URL, ANSWERS_ACCOUNT
    AUTO_LOGIN = True
except ImportError:
    AUTO_LOGIN = False
    print("⚠ credentials.py not found. Manual login will be required.")

class InteractiveCodeMirror:
    def __init__(self, auto_login=False):
        self.browser = None
        self.page = None
        self.playwright = None
        self.auto_login = auto_login
        self.copy_count = 0
        
    async def setup_browser(self):
        """Setup browser and navigate to CodeTantra"""
        print("Setting up browser...")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.firefox.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        print("✓ Browser opened")
        return self.playwright
        
    async def navigate_to_codetantra(self, url):
        """Navigate to CodeTantra"""
        print(f"Navigating to: {url}")
        await self.page.goto(url)
        print("✓ Navigated to CodeTantra")
        
    async def login_to_account(self, username, password):
        """Automatically log in to CodeTantra"""
        try:
            print(f"\nLogging in as {username}...")
            await self.page.wait_for_load_state("networkidle")
            
            # Fill username
            username_field = self.page.get_by_placeholder("Email/User Id")
            await username_field.fill(username)
            print(f"  ✓ Username entered")
            
            # Fill password
            password_field = self.page.get_by_placeholder("Password", exact=True)
            await password_field.fill(password)
            print("  ✓ Password entered")
            
            # Click LOGIN button
            login_button = self.page.get_by_role("button", name="LOGIN")
            await login_button.click()
            print("  ✓ LOGIN button clicked")
            
            # Wait for login
            await self.page.wait_for_timeout(5000)
            
            # Check success
            current_url = self.page.url
            if "login" not in current_url.lower():
                print(f"✓ Successfully logged in!")
                return True
            else:
                print(f"⚠ Login may have failed")
                return False
                
        except Exception as e:
            print(f"✗ Error logging in: {e}")
            return False
    
    async def copy_codemirror_content(self):
        """Copy current CodeMirror content to clipboard using Ctrl+A and Ctrl+C"""
        try:
            print(f"\n📋 Copying CodeMirror content (Copy #{self.copy_count + 1})...")
            
            # Switch to iframe first
            iframe = self.page.frame_locator("#course-iframe")
            
            # Find the CodeMirror editor content
            editor = iframe.locator("div.cm-content[contenteditable='true']")
            
            # Wait for editor to be visible
            try:
                await editor.wait_for(state="visible", timeout=5000)
                print("✓ CodeMirror editor found")
            except Exception as e:
                print(f"⚠ CodeMirror editor not found: {e}")
                print("Make sure you're on a code completion problem")
                return False
            
            # Try multiple approaches to focus and copy
            success = False
            
            # Approach 1: Try JavaScript focus first
            try:
                await editor.evaluate("element => element.focus()")
                print("✓ Editor focused using JavaScript")
                success = True
            except Exception as e:
                print(f"⚠ JavaScript focus failed: {e}")
            
            # Approach 2: If JavaScript failed, try clicking
            if not success:
                try:
                    await editor.click(timeout=5000)
                    print("✓ Editor focused using click")
                    success = True
                except Exception as e:
                    print(f"⚠ Click focus failed: {e}")
            
            # Approach 3: If both failed, try clicking on the iframe first
            if not success:
                try:
                    iframe_element = self.page.locator("#course-iframe")
                    await iframe_element.click()
                    print("✓ Clicked on iframe")
                    await self.page.wait_for_timeout(200)
                    await editor.click(timeout=3000)
                    print("✓ Editor focused after iframe click")
                    success = True
                except Exception as e:
                    print(f"⚠ Iframe click approach failed: {e}")
            
            # Wait a moment for focus
            await self.page.wait_for_timeout(300)
            
            # Try to select all text
            try:
                if success:
                    await editor.press("Control+a")
                    print("✓ Selected all text (Ctrl+A)")
                else:
                    # Use page keyboard as fallback
                    await self.page.keyboard.press("Control+a")
                    print("✓ Selected all text using page keyboard (Ctrl+A)")
            except Exception as e:
                print(f"⚠ Ctrl+A failed: {e}")
                # Try alternative method
                await self.page.keyboard.press("Control+a")
                print("✓ Selected all text using page keyboard fallback (Ctrl+A)")
            
            # Wait a moment for selection
            await self.page.wait_for_timeout(200)
            
            # Try to copy
            try:
                if success:
                    await editor.press("Control+c")
                    print("✓ Copied to clipboard (Ctrl+C)")
                else:
                    # Use page keyboard as fallback
                    await self.page.keyboard.press("Control+c")
                    print("✓ Copied to clipboard using page keyboard (Ctrl+C)")
            except Exception as e:
                print(f"⚠ Ctrl+C failed: {e}")
                # Try alternative method
                await self.page.keyboard.press("Control+c")
                print("✓ Copied to clipboard using page keyboard fallback (Ctrl+C)")
            
            # Wait a moment for clipboard operation
            await self.page.wait_for_timeout(300)
            
            # Get the copied content from clipboard
            try:
                copied_content = pyperclip.paste()
                
                if copied_content and copied_content.strip():
                    self.copy_count += 1
                    
                    print(f"✓ Code copied to clipboard! (Copy #{self.copy_count})")
                    print(f"📌 Lines: {len(copied_content.split(chr(10)))}")
                    print("✓ You can now paste (Ctrl+V) in any application")
                    
                    # Show preview
                    print("\n📄 Code preview:")
                    print("-" * 50)
                    preview = copied_content[:200] + "..." if len(copied_content) > 200 else copied_content
                    print(preview)
                    print("-" * 50)
                    
                    return True
                else:
                    print("⚠ No content found in clipboard")
                    return False
                    
            except Exception as e:
                print(f"⚠ Error reading from clipboard: {e}")
                return False
                
        except Exception as e:
            print(f"✗ Error copying CodeMirror content: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    async def interactive_loop(self):
        """Main interactive loop"""
        print("\n" + "="*60)
        print("INTERACTIVE CODEMIRROR COPY TOOL")
        print("="*60)
        print("Instructions:")
        print("• Navigate to any CodeMirror editor in the browser")
        print("• Press ENTER to copy the current content to clipboard")
        print("• Press 'q' + ENTER to quit")
        print("• The browser will stay open for you to navigate")
        print("• Uses Ctrl+A + Ctrl+C method for reliable copying")
        print("="*60)
        
        while True:
            try:
                user_input = input("\nPress ENTER to copy CodeMirror content (or 'q' to quit): ").strip().lower()
                
                if user_input == 'q':
                    print("👋 Goodbye!")
                    break
                elif user_input == '':
                    # Copy current CodeMirror content
                    success = await self.copy_codemirror_content()
                    if success:
                        print(f"✅ Successfully copied! (Total copies: {self.copy_count})")
                    else:
                        print("❌ Failed to copy. Make sure you're on a CodeMirror editor.")
                else:
                    print("Invalid input. Press ENTER to copy or 'q' to quit.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"⚠ Error: {e}")
    
    async def cleanup(self):
        """Keep browser open but clean up resources properly"""
        try:
            print("\n🧹 Cleaning up resources...")
            
            if self.page:
                print("✓ Closing page...")
                await self.page.close()
                self.page = None
            
            if hasattr(self, 'context') and self.context:
                print("✓ Closing context...")
                await self.context.close()
                self.context = None
            
            if self.browser:
                print("✓ Closing browser...")
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                print("✓ Closing Playwright...")
                await self.playwright.stop()
                self.playwright = None
                
            print("✓ All resources cleaned up")
            
        except Exception as e:
            print(f"⚠ Error during cleanup: {e}")

async def main():
    """Main entry point"""
    print("=" * 60)
    print("INTERACTIVE CODEMIRROR COPY TOOL")
    print("=" * 60)
    print("This tool keeps the browser open and lets you copy")
    print("CodeMirror content on demand by pressing ENTER")
    print("=" * 60)
    
    tool = InteractiveCodeMirror(auto_login=AUTO_LOGIN)
    
    try:
        # Setup
        await tool.setup_browser()
        
        # Login
        if AUTO_LOGIN:
            print(f"\n🔐 Using automatic login from credentials.py")
            await tool.navigate_to_codetantra(LOGIN_URL)
            await asyncio.sleep(2)
            
            if await tool.login_to_account(
                ANSWERS_ACCOUNT['username'],
                ANSWERS_ACCOUNT['password']
            ):
                print("✓ Logged in successfully!")
            else:
                print("⚠ Login failed. Please login manually.")
        else:
            print("\nEnter CodeTantra URL (or press ENTER for manual navigation):")
            url = input().strip()
            if url:
                await tool.navigate_to_codetantra(url)
            else:
                print("Please navigate to CodeTantra manually")
        
        # Start interactive loop
        await tool.interactive_loop()
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await tool.cleanup()

if __name__ == "__main__":
    # Check dependencies
    try:
        import pyperclip
    except ImportError:
        print("Installing pyperclip...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"])
        import pyperclip
    
    asyncio.run(main())
