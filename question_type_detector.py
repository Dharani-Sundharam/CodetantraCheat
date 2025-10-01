"""
Interactive Question Type Detector for Code Tantra
Detects and displays the type of question currently visible in the browser
"""

import asyncio
from playwright.async_api import async_playwright
import tkinter as tk
from tkinter import messagebox

# Import credentials
try:
    from credentials import ANSWERS_ACCOUNT
    print("✓ Loaded credentials")
except:
    print("✗ Could not load credentials.py")
    exit(1)

class QuestionTypeDetector:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        
    async def setup_browser(self):
        """Initialize browser"""
        print("Setting up browser...")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.firefox.launch(headless=False)
        context = await self.browser.new_context()
        self.page = await context.new_page()
        
        print("✓ Browser opened")
        
    async def login(self):
        """Login to Code Tantra"""
        try:
            print("Logging in...")
            
            # Navigate to login page
            await self.page.goto("https://rmd.codetantra.com/login.jsp")
            await self.page.wait_for_load_state("networkidle")
            
            # Fill username
            username_field = self.page.get_by_placeholder("Email/User Id")
            await username_field.fill(ANSWERS_ACCOUNT['username'])
            print(f"✓ Username entered: {ANSWERS_ACCOUNT['username']}")
            
            # Fill password
            password_field = self.page.get_by_placeholder("Password", exact=True)
            await password_field.fill(ANSWERS_ACCOUNT['password'])
            print("✓ Password entered")
            
            # Click login
            login_button = self.page.get_by_role("button", name="LOGIN")
            await login_button.click()
            print("✓ Login button clicked")
            
            # Wait for login
            await self.page.wait_for_timeout(5000)
            
            if "login" not in self.page.url.lower():
                print("✓ Successfully logged in")
                return True
            else:
                print("⚠ Login may have failed")
                return False
                
        except Exception as e:
            print(f"✗ Error logging in: {e}")
            return False
    
    async def detect_question_type(self):
        """Detect the type of question on current page"""
        try:
            print("\n" + "="*60)
            print("DETECTING QUESTION TYPE")
            print("="*60)
            
            # Check for iframe
            iframe = self.page.frame_locator("#course-iframe")
            
            # Check for CodeMirror editor (Complete the code)
            editor = iframe.locator("div.cm-content[contenteditable='true']")
            editor_count = await editor.count()
            
            if editor_count > 0:
                print("🎯 QUESTION TYPE: CODE COMPLETION")
                print("   - Found CodeMirror editor")
                print("   - This is a 'Complete the code' question")
                return "code_completion", []
            
            # Check for multiple choice options
            radio_options = iframe.locator("input[type='radio']")
            checkbox_options = iframe.locator("input[type='checkbox']")
            
            radio_count = await radio_options.count()
            checkbox_count = await checkbox_options.count()
            
            if radio_count > 0 or checkbox_count > 0:
                # Get selected options
                selected_options = await self.get_selected_options(iframe)
                
                if len(selected_options) > 1:
                    print("🎯 QUESTION TYPE: MULTIPLE CHOICE")
                    print(f"   - Found {checkbox_count} checkboxes")
                    print(f"   - {len(selected_options)} options currently selected")
                    print("   - More than one correct answer")
                    print(f"   - Selected options: {selected_options}")
                    return "multiple_choice", selected_options
                elif len(selected_options) == 1:
                    print("🎯 QUESTION TYPE: SINGLE CHOICE")
                    print(f"   - Found {radio_count} radio buttons")
                    print("   - 1 option currently selected")
                    print("   - Only one correct answer")
                    print(f"   - Selected option: {selected_options[0]}")
                    return "single_choice", selected_options
                else:
                    print("🎯 QUESTION TYPE: MULTIPLE CHOICE (UNANSWERED)")
                    print(f"   - Found {radio_count + checkbox_count} options")
                    print("   - No options currently selected")
                    print("   - Multiple choice question")
                    return "multiple_choice_unanswered", []
            
            # Check for other elements
            buttons = await iframe.locator("button").count()
            inputs = await iframe.locator("input").count()
            textareas = await iframe.locator("textarea").count()
            
            print("🎯 QUESTION TYPE: UNKNOWN")
            print(f"   - Found {buttons} buttons")
            print(f"   - Found {inputs} input fields")
            print(f"   - Found {textareas} textareas")
            print("   - No recognizable question pattern")
            return "unknown", []
            
        except Exception as e:
            print(f"✗ Error detecting question type: {e}")
            return "error", []
    
    async def get_selected_options(self, iframe):
        """Get currently selected options"""
        try:
            selected_options = []
            
            # Get all checked options
            checked_options = iframe.locator("input:checked")
            count = await checked_options.count()
            
            for i in range(count):
                option = checked_options.nth(i)
                # Get the label text or value
                label = await option.evaluate("""
                    (el) => {
                        const label = el.closest('label') || 
                                   el.parentElement.querySelector('label') ||
                                   el.parentElement;
                        return label ? label.textContent.trim() : el.value || '';
                    }
                """)
                selected_options.append(label)
            
            return selected_options
            
        except Exception as e:
            print(f"⚠ Error getting selected options: {e}")
            return []
    
    async def get_question_details(self):
        """Get detailed information about the current question"""
        try:
            iframe = self.page.frame_locator("#course-iframe")
            
            print("\n" + "="*60)
            print("QUESTION DETAILS")
            print("="*60)
            
            # Get page title/heading
            try:
                title = await iframe.locator("h1, h2, h3").first.text_content()
                print(f"Title: {title}")
            except:
                print("Title: Not found")
            
            # Get all text content (first 500 chars)
            try:
                full_text = await iframe.evaluate("() => document.body.textContent")
                preview = full_text[:500].replace('\n', ' ').strip()
                print(f"Content preview: {preview}...")
            except:
                print("Content: Could not extract")
            
            # Get all input elements
            try:
                inputs = await iframe.locator("input").all()
                print(f"\nInput elements found: {len(inputs)}")
                for i, inp in enumerate(inputs[:5]):  # Show first 5
                    input_type = await inp.get_attribute("type")
                    input_id = await inp.get_attribute("id")
                    print(f"  {i+1}. Type: {input_type}, ID: {input_id}")
            except:
                print("Input elements: Could not extract")
            
            # Get all buttons
            try:
                buttons = await iframe.locator("button").all()
                print(f"\nButtons found: {len(buttons)}")
                for i, btn in enumerate(buttons[:5]):  # Show first 5
                    btn_text = await btn.text_content()
                    print(f"  {i+1}. Text: '{btn_text}'")
            except:
                print("Buttons: Could not extract")
                
        except Exception as e:
            print(f"✗ Error getting question details: {e}")
    
    async def interactive_mode(self):
        """Interactive mode for testing different pages"""
        print("\n" + "="*60)
        print("INTERACTIVE QUESTION TYPE DETECTOR")
        print("="*60)
        print("Navigate to any question page in the browser")
        print("Press ENTER to detect question type")
        print("Type 'details' for detailed analysis")
        print("Type 'quit' to exit")
        print("="*60)
        
        while True:
            user_input = input("\nPress ENTER to detect (or 'details'/'quit'): ").strip().lower()
            
            if user_input == 'quit':
                break
            elif user_input == 'details':
                await self.get_question_details()
            else:
                question_type, selected_options = await self.detect_question_type()
                
                # Show popup with result
                try:
                    root = tk.Tk()
                    root.withdraw()
                    
                    if selected_options:
                        options_text = "\n".join([f"• {opt}" for opt in selected_options])
                        message = f"Question Type: {question_type.upper()}\n\nSelected Options:\n{options_text}"
                    else:
                        message = f"Question Type: {question_type.upper()}\n\nNo options selected"
                    
                    messagebox.showinfo(
                        "Question Type Detected",
                        message + "\n\nCheck console for detailed information."
                    )
                    root.destroy()
                except:
                    print(f"\n🎯 RESULT: {question_type.upper()}")
                    if selected_options:
                        print(f"Selected options: {selected_options}")
    
    async def cleanup(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("✓ Browser closed")

async def main():
    """Main entry point"""
    detector = QuestionTypeDetector()
    
    try:
        await detector.setup_browser()
        
        if await detector.login():
            await detector.interactive_mode()
        else:
            print("✗ Login failed. Please check credentials.")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await detector.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
