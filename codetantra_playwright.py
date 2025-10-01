"""
Code Tantra Automation Tool - Playwright Version
Educational purpose: Automates copying answers between two browser sessions
"""

import asyncio
import time
import re
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
import ctypes
import tkinter as tk
from tkinter import messagebox

try:
    from credentials import LOGIN_URL, ANSWERS_ACCOUNT, TARGET_ACCOUNT
    AUTO_LOGIN = True
except ImportError:
    AUTO_LOGIN = False
    print("⚠ credentials.py not found. Manual login will be required.")


class CodeTantraPlaywrightAutomation:
    def __init__(self, auto_login=False):
        self.browser_answers = None
        self.browser_target = None
        self.page_answers = None
        self.page_target = None
        self.auto_login = auto_login
        
    async def setup_browsers(self):
        """Initialize two separate browser instances"""
        print("Setting up Playwright browsers...")

        # Get screen size and split in half
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        half_width = screen_width // 2
        window_height = screen_height - 40  # Leave some space for taskbar

        # Create first browser (answers - left half)
        self.browser_answers = await self.playwright.firefox.launch(headless=False)
        context_answers = await self.browser_answers.new_context(
            viewport={'width': half_width, 'height': window_height}
        )
        self.page_answers = await context_answers.new_page()
        
        # Position and resize using JavaScript
        await self.page_answers.evaluate(f"""
            window.resizeTo({half_width}, {window_height});
            window.moveTo(0, 0);
        """)
        print("✓ First browser window opened (answers account - left)")

        # Create second browser (target - right half)
        self.browser_target = await self.playwright.firefox.launch(headless=False)
        context_target = await self.browser_target.new_context(
            viewport={'width': half_width, 'height': window_height}
        )
        self.page_target = await context_target.new_page()
        
        # Position and resize using JavaScript
        await self.page_target.evaluate(f"""
            window.resizeTo({half_width}, {window_height});
            window.moveTo({half_width}, 0);
        """)
        print("✓ Second browser window opened (target account - right)")
        
    async def navigate_to_codetantra(self, url):
        """Navigate both browsers to Code Tantra"""
        print(f"\nNavigating to: {url}")
        await self.page_answers.goto(url)
        await self.page_target.goto(url)
        print("✓ Both browsers navigated to Code Tantra")
        
    async def login_to_account(self, page, username, password, account_name):
        """Automatically log in to a Code Tantra account"""
        try:
            print(f"\nLogging in to {account_name}...")

            # Wait for login page to load
            await page.wait_for_load_state("networkidle")

            # Use Playwright's better locators from codegen
            print("  Filling username...")
            username_field = page.get_by_placeholder("Email/User Id")
            await username_field.fill(username)
            print(f"  ✓ Username entered: {username}")

            print("  Filling password...")
            password_field = page.get_by_placeholder("Password", exact=True)
            await password_field.fill(password)
            print("  ✓ Password entered")

            # Click LOGIN button
            print("  Clicking LOGIN button...")
            login_button = page.get_by_role("button", name="LOGIN")
            await login_button.click()
            print("  ✓ LOGIN button clicked")

            # Wait for login to complete
            await page.wait_for_timeout(5000)

            # Check if login was successful (not on login page anymore)
            current_url = page.url
            if "login" not in current_url.lower():
                print(f"✓ Successfully logged in to {account_name}")
                return True
            else:
                print(f"⚠ Login may have failed for {account_name}")
                return False

        except Exception as e:
            print(f"✗ Error logging in to {account_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    async def navigate_to_problem_via_menu(self, page, problem_number):
        """Navigate to specific problem using menu tree (e.g., 7.3.2) and wait for page to load"""
        try:
            print(f"  Navigating via menu to problem: {problem_number}")
            
            iframe = page.frame_locator("#course-iframe")
            
            # Click Contents list to open menu
            contents_button = iframe.get_by_role("button", name="Contents list")
            await contents_button.click()
            await page.wait_for_timeout(500)
            
            # Parse problem number (e.g., "7.3.2" -> ["7", "7.3", "7.3.2"])
            parts = problem_number.split(".")
            hierarchy = []
            for i in range(1, len(parts) + 1):
                hierarchy.append(".".join(parts[:i]))
            
            print(f"  Menu hierarchy: {hierarchy}")
            
            # Navigate through each level
            for level in hierarchy:
                # Find button that starts with this level number
                buttons = iframe.get_by_role("button")
                count = await buttons.count()
                
                for i in range(count):
                    button = buttons.nth(i)
                    text = await button.text_content()
                    
                    if text and text.strip().startswith(f"{level}."):
                        print(f"  Clicking menu item: {text}")
                        await button.click()
                        await page.wait_for_timeout(500)
                        break
            
            print("  ✓ Menu navigation complete, waiting for page to load...")
            
            # Wait for the problem button to appear (dynamic wait)
            max_attempts = 60  # 30 seconds max
            attempt = 0
            
            while attempt < max_attempts:
                result = await page.evaluate("""
                    () => {
                        const iframe = document.getElementById('course-iframe');
                        if (!iframe) return false;
                        
                        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                        const targetButton = iframeDoc.querySelector('button.min-w-0.flex-1.text-left.text-sm.font-semibold.hover\\\\:underline');
                        
                        return targetButton !== null;
                    }
                """)
                
                if result:
                    print("  ✓ Problem page loaded")
                    return True
                
                await page.wait_for_timeout(500)
                attempt += 1
                
                if attempt % 4 == 0:
                    print(f"  Waiting for problem to load... ({attempt * 0.5:.1f}s)")
            
            print("  ⚠ Problem page did not load in time")
            return False
            
        except Exception as e:
            print(f"  ⚠ Menu navigation failed: {e}")
            return False
    
    def get_current_problem_number_selenium(self, page):
        """Extract problem number using Selenium-style approach via JavaScript"""
        try:
            print("  Looking for problem number in iframe...")
            
            # Execute JavaScript to find problem number
            js_code = """
            async () => {
                const iframe = document.getElementById('course-iframe');
                if (!iframe) return null;
                
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                const buttons = iframeDoc.querySelectorAll('button');
                
                for (let button of buttons) {
                    const text = button.textContent.trim();
                    const match = text.match(/^(\\d+(?:\\.\\d+)+)/);
                    if (match) {
                        return {
                            number: match[1],
                            fullText: text
                        };
                    }
                }
                return null;
            }
            """
            
            # Run synchronously using page.evaluate
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(
                page.evaluate(js_code)
            )
            
            if result:
                print(f"  ✓ Found problem number: '{result['number']}'")
                print(f"  Full text: '{result['fullText']}'")
                return result['number']
            else:
                print("  ⚠ No problem number found")
                return None
                
        except Exception as e:
            print(f"⚠ Error getting problem number: {e}")
            return None
    
    async def get_current_problem_number(self, page):
        """Extract the CURRENT problem number from the specific button in iframe with dynamic waiting"""
        try:
            print("  Looking for problem number in iframe...")
            
            # Wait dynamically for the problem button to appear (max 30 seconds)
            max_attempts = 60  # 60 attempts * 0.5 seconds = 30 seconds max
            attempt = 0
            
            while attempt < max_attempts:
                result = await page.evaluate("""
                    () => {
                        const iframe = document.getElementById('course-iframe');
                        if (!iframe) return null;
                        
                        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                        
                        // Look for the specific button with these classes that shows the current problem
                        const targetButton = iframeDoc.querySelector('button.min-w-0.flex-1.text-left.text-sm.font-semibold.hover\\\\:underline');
                        
                        if (targetButton) {
                            const text = targetButton.textContent.trim();
                            const match = text.match(/^(\\d+(?:\\.\\d+)+)/);
                            if (match) {
                                return {
                                    type: 'problem',
                                    number: match[1],
                                    fullText: text
                                };
                            }
                        }
                        
                        // If no x.x.x pattern, check for module question (e.g., "Day of the Week")
                        const questionDivs = iframeDoc.querySelectorAll('div[role="button"]');
                        for (let div of questionDivs) {
                            const h3 = div.querySelector('h3');
                            if (h3) {
                                const titleText = h3.textContent.trim();
                                // Return question title as identifier
                                if (titleText && !titleText.match(/^\\d+/)) {
                                    return {
                                        type: 'module',
                                        number: titleText,
                                        fullText: titleText
                                    };
                                }
                            }
                        }
                        
                        return null;
                    }
                """)
                
                if result:
                    if result.get('type') == 'module':
                        print(f"  ✓ Found module question: '{result['number']}'")
                    else:
                        print(f"  ✓ Found problem number: '{result['number']}'")
                    print(f"  Full text: '{result['fullText']}'")
                    return result['number']
                
                # Wait 500ms before trying again
                await page.wait_for_timeout(500)
                attempt += 1
                if attempt % 4 == 0:  # Print progress every 2 seconds
                    print(f"  Waiting for problem to load... ({attempt * 0.5:.1f}s)")
            
            print("  ⚠ No problem number found after waiting")
            return None
                
        except Exception as e:
            print(f"⚠ Error getting problem number: {e}")
            return None
            
    async def check_problems_match(self):
        """Check if both browsers are on the same problem"""
        print("Checking if problems match...")
        
        num_answers = await self.get_current_problem_number(self.page_answers)
        num_target = await self.get_current_problem_number(self.page_target)
        
        print(f"  Answers problem: {num_answers}")
        print(f"  Target problem: {num_target}")
        
        if num_answers and num_target and num_answers == num_target:
            print("✓ Both accounts are on the same problem")
            
            # Check if we've reached a Quiz (unit finished) - COMMENTED OUT
            # if await self.check_for_quiz():
            #     print("🎯 QUIZ DETECTED - Unit finished!")
            #     self.show_unit_finished_popup()
            #     return False  # Stop automation
            
            # If it's a module question (not x.x.x), click to get back to x.x.x format
            if not re.match(r'^\d+\.\d+\.\d+', num_answers):
                print("  Module question detected - clicking to get x.x.x format...")
                await self.click_module_question(self.page_answers)
                await self.click_module_question(self.page_target)
                print("  ✓ Clicked module questions to return to x.x.x format\n")
            
            return True
        else:
            return False
    
    # COMMENTED OUT - Quiz detection functions
    # async def check_for_quiz(self):
    #     """Check if current page shows a Quiz with strict pattern matching"""
    #     try:
    #         # Check both pages for exact "Unit X - Quiz Y" pattern
    #         quiz_answers = await self.page_answers.evaluate("""
    #             () => {
    #                 const iframe = document.getElementById('course-iframe');
    #                 if (!iframe) return false;
    #                 const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    #                 const text = iframeDoc.body.textContent;
    #                 // Look for pattern like "Unit 2 - Quiz 1" or "Unit 10 - Quiz 5"
    #                 const quizPattern = /Unit\\s+\\d+\\s*-\\s*Quiz\\s+\\d+/i;
    #                 return quizPattern.test(text);
    #             }
    #         """)
    #         
    #         quiz_target = await self.page_target.evaluate("""
    #             () => {
    #                 const iframe = document.getElementById('course-iframe');
    #                 if (!iframe) return false;
    #                 const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    #                 const text = iframeDoc.body.textContent;
    #                 // Look for pattern like "Unit 2 - Quiz 1" or "Unit 10 - Quiz 5"
    #                 const quizPattern = /Unit\\s+\\d+\\s*-\\s*Quiz\\s+\\d+/i;
    #                 return quizPattern.test(text);
    #             }
    #         """)
    #         
    #         if quiz_answers or quiz_target:
    #             print("  🎯 QUIZ DETECTED: Found 'Unit X - Quiz Y' pattern")
    #             return True
    #         else:
    #             return False
    #         
    #     except Exception as e:
    #         print(f"  ⚠ Error checking for quiz: {e}")
    #         return False
    
    # def show_unit_finished_popup(self):
    #     """Show tkinter popup when unit is finished"""
    #     try:
    #         # Create root window (hidden)
    #         root = tk.Tk()
    #         root.withdraw()  # Hide the main window
    #         
    #         # Show message box
    #         messagebox.showinfo(
    #             "Unit Completed! 🎉",
    #             "A UNIT has been finished!\n\n"
    #             "Please manually navigate both accounts to the NEXT UNIT.\n\n"
    #             "Click OK when ready to continue automation."
    #         )
    #         
    #         # Destroy the root window
    #         root.destroy()
    #         
    #     except Exception as e:
    #         print(f"⚠ Could not show popup: {e}")
    #         print("\n" + "="*60)
    #         print("🎉 UNIT COMPLETED!")
    #         print("="*60)
    #         print("Please navigate both accounts to the next unit manually.")
    #         input("Press ENTER when ready to continue...")
    
    async def click_module_question(self, page):
        """Click on module question to get back to x.x.x format"""
        try:
            iframe = page.frame_locator("#course-iframe")
            
            # Find and click the div with role="button" that contains the question
            question_div = iframe.locator('div[role="button"]').first
            await question_div.click()
            print(f"    ✓ Clicked module question")
            
            # Wait for page to load
            await page.wait_for_timeout(1000)
            
        except Exception as e:
            print(f"    ⚠ Could not click module question: {e}")
        
    async def detect_question_type(self, page):
        """Detect the type of question on the page"""
        try:
            iframe = page.frame_locator("#course-iframe")
            
            # Check for CodeMirror editor (Complete the code)
            editor = iframe.locator("div.cm-content[contenteditable='true']")
            if await editor.count() > 0:
                return "code_completion"
            
            # Check for multiple choice options
            options = iframe.locator("input[type='radio'], input[type='checkbox']")
            option_count = await options.count()
            
            if option_count > 0:
                # Check if any are already selected (multiple choice)
                selected_count = await iframe.locator("input[type='radio']:checked, input[type='checkbox']:checked").count()
                if selected_count > 1:
                    return "multiple_choice"
                else:
                    return "single_choice"
            
            return "unknown"
            
        except Exception as e:
            print(f"⚠ Error detecting question type: {e}")
            return "unknown"
    
    async def get_code_from_answers(self):
        """Extract code from the answers account editor with enhanced error handling"""
        try:
            print("Extracting code from answers account...")
            
            # Switch to iframe first
            iframe = self.page_answers.frame_locator("#course-iframe")
            
            # Find the CodeMirror editor content with better waiting
            editor = iframe.locator("div.cm-content[contenteditable='true']")
            await editor.wait_for(state="visible", timeout=10000)
            
            # Scroll to editor to ensure it's visible
            await editor.scroll_into_view_if_needed()
            
            # Get all lines with better error handling
            lines = iframe.locator("div.cm-line")
            line_count = await lines.count()
            
            if line_count == 0:
                print("⚠ No code lines found in editor")
                return None
            
            code_text = []
            for i in range(line_count):
                try:
                    line = lines.nth(i)
                    line_text = await line.text_content()
                    if line_text is None:
                        line_text = ""
                    code_text.append(line_text)
                except Exception as line_error:
                    print(f"⚠ Error extracting line {i}: {line_error}")
                    code_text.append("")  # Add empty line to maintain structure
            
            full_code = "\n".join(code_text)
            
            # Clean up the code (remove extra whitespace but preserve structure)
            cleaned_code = "\n".join(line.rstrip() for line in full_code.split('\n'))
            
            print(f"✓ Extracted {len(code_text)} lines of code")
            print(f"✓ Code preview: {cleaned_code[:100]}{'...' if len(cleaned_code) > 100 else ''}")
            return cleaned_code
            
        except Exception as e:
            print(f"⚠ Could not extract code: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    async def paste_code_to_target(self, code):
        """Paste code into the target account editor with enhanced reliability"""
        try:
            print("Pasting code to target account...")
            
            if not code or not code.strip():
                print("⚠ No code to paste")
                return False
            
            # Switch to iframe first
            iframe = self.page_target.frame_locator("#course-iframe")
            
            # Find the CodeMirror editor with better waiting
            editor = iframe.locator("div.cm-content[contenteditable='true']")
            await editor.wait_for(state="visible", timeout=10000)
            
            # Scroll to editor to ensure it's visible
            await editor.scroll_into_view_if_needed()
            
            # Click to focus the editor
            await editor.click()
            await self.page_target.wait_for_timeout(500)
            
            # Clear existing content more reliably
            print("  Clearing existing content...")
            await editor.press("Control+a")
            await self.page_target.wait_for_timeout(300)
            await editor.press("Delete")
            await self.page_target.wait_for_timeout(500)
            
            # Method 1: Try using clipboard (Ctrl+V) first
            try:
                print("  Attempting clipboard paste...")
                # Set clipboard content using JavaScript with proper escaping
                await self.page_target.evaluate("""
                    (code) => {
                        navigator.clipboard.writeText(code).then(() => {
                            console.log('Code copied to clipboard');
                        }).catch(err => {
                            console.log('Clipboard failed:', err);
                        });
                    }
                """, code)
                
                await self.page_target.wait_for_timeout(500)
                await editor.press("Control+v")
                await self.page_target.wait_for_timeout(1000)
                
                # Verify paste was successful
                pasted_content = await editor.text_content()
                if pasted_content and len(pasted_content.strip()) > 0:
                    print("✓ Code pasted successfully via clipboard")
                    return True
                else:
                    print("⚠ Clipboard paste failed, trying line-by-line...")
                    
            except Exception as clipboard_error:
                print(f"⚠ Clipboard paste failed: {clipboard_error}")
                print("  Trying line-by-line method...")
            
            # Method 2: Line-by-line typing as fallback
            print("  Pasting line by line...")
            lines = code.split('\n')
            
            for i, line in enumerate(lines):
                try:
                    # Type the line
                    await editor.type(line)
                    
                    # Add newline if not the last line
                    if i < len(lines) - 1:
                        await editor.press("Enter")
                    
                    # Small delay between lines for stability
                    await self.page_target.wait_for_timeout(100)
                    
                except Exception as line_error:
                    print(f"⚠ Error pasting line {i+1}: {line_error}")
                    continue
            
            # Verify the paste was successful
            await self.page_target.wait_for_timeout(1000)
            pasted_content = await editor.text_content()
            
            if pasted_content and len(pasted_content.strip()) > 0:
                print(f"✓ Code pasted successfully ({len(lines)} lines)")
                print(f"✓ Paste verification: {pasted_content[:100]}{'...' if len(pasted_content) > 100 else ''}")
                return True
            else:
                print("⚠ Paste verification failed - no content detected")
                return False
            
        except Exception as e:
            print(f"⚠ Error pasting code: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_selected_answers(self, page):
        """Get selected answers from answers account"""
        try:
            iframe = page.frame_locator("#course-iframe")
            
            # Get all checked options
            checked_options = iframe.locator("input:checked")
            count = await checked_options.count()
            
            answers = []
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
                answers.append(label)
            
            return answers
            
        except Exception as e:
            print(f"⚠ Error getting selected answers: {e}")
            return []
    
    async def select_answers_on_target(self, answers):
        """Select the same answers on target account"""
        try:
            print("Selecting answers on target account...")
            iframe = self.page_target.frame_locator("#course-iframe")
            
            # Get all available options
            all_options = iframe.locator("input[type='radio'], input[type='checkbox']")
            option_count = await all_options.count()
            
            for i in range(option_count):
                option = all_options.nth(i)
                
                # Get the label text for this option
                label_text = await option.evaluate("""
                    (el) => {
                        const label = el.closest('label') || 
                                   el.parentElement.querySelector('label') ||
                                   el.parentElement;
                        return label ? label.textContent.trim() : el.value || '';
                    }
                """)
                
                # Check if this option should be selected
                if any(answer in label_text for answer in answers):
                    await option.check()
                    print(f"  ✓ Selected: {label_text}")
            
            print("✓ Answers selected successfully")
            return True
            
        except Exception as e:
            print(f"⚠ Error selecting answers: {e}")
            return False
    
    async def handle_question_answer(self):
        """Main function to handle different question types with copy-paste enabled"""
        try:
            # Detect question type on answers account
            question_type = await self.detect_question_type(self.page_answers)
            print(f"Question type detected: {question_type}")
            
            if question_type == "code_completion":
                print("✓ Code completion question detected - COPYING CODE")
                
                # Extract code from answers account
                code = await self.get_code_from_answers()
                if not code:
                    print("⚠ No code found in answers account")
                    return False
                
                # Paste code to target account
                paste_success = await self.paste_code_to_target(code)
                if paste_success:
                    print("✓ Code copied and pasted successfully!")
                    return True
                else:
                    print("⚠ Failed to paste code to target account")
                    return False
                    
            elif question_type in ["single_choice", "multiple_choice"]:
                # Handle multiple choice questions
                answers = await self.get_selected_answers(self.page_answers)
                if answers:
                    print(f"✓ Found {len(answers)} selected answers: {answers}")
                    return await self.select_answers_on_target(answers)
                else:
                    print("⚠ No answers found on answers account")
                    return False
                    
            else:
                print("⚠ Unknown question type - SKIPPING")
                return "skip"  # Skip unknown question types
                
        except Exception as e:
            print(f"⚠ Error handling question: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    async def submit_solution(self):
        """Click the submit button on target account with proper delay"""
        try:
            print("Submitting solution...")
            
            # Switch to iframe first
            iframe = self.page_target.frame_locator("#course-iframe")
            
            # Wait for submit button to be available (up to 30 seconds)
            print("  Waiting for submit button to be available...")
            try:
                submit_button = iframe.locator("[id=\"__ss-content-actions\"]").get_by_role("button", name="Submit")
                await submit_button.wait_for(state="visible", timeout=30000)  # 30 second timeout
                print("  ✓ Submit button found")
            except Exception as e:
                print(f"  ⚠ Submit button not found within 30 seconds: {e}")
                return False
            
            # Click the submit button
            await submit_button.scroll_into_view_if_needed()
            await submit_button.click()
            print("✓ Submit button clicked")
            
            # Wait longer for submission to process
            print("  Waiting for submission to process...")
            await self.page_target.wait_for_timeout(5000)  # 5 second wait after click
            return True
            
        except Exception as e:
            print(f"⚠ Could not find or click Submit button: {e}")
            return False
            
    async def check_submission_success(self):
        """Check if submission was successful by looking for badge-success"""
        try:
            print("Checking submission result...")
            
            # Switch to iframe first
            iframe = self.page_target.frame_locator("#course-iframe")
            
            # Wait for the result badge to appear
            badge = iframe.locator("div.badge.badge-secondary.badge-sm.badge-success")
            await badge.wait_for(timeout=10000)
            
            time_text = await badge.text_content()
            print(f"✓ Submission SUCCESSFUL! Time: {time_text}")
            return True
            
        except Exception as e:
            print(f"⚠ Submission may have failed or timed out: {e}")
            
            # Check for error badges
            try:
                error_badge = iframe.locator("div.badge.badge-secondary.badge-sm.badge-error")
                if await error_badge.count() > 0:
                    error_text = await error_badge.text_content()
                    print(f"✗ Submission FAILED: {error_text}")
            except:
                print("? Could not determine submission result")
                
            return False
            
    async def move_to_next_problem(self):
        """Click Next button on both accounts and verify they match"""
        try:
            print("\nMoving to next problem...")
            
            # Click Next on answers account
            iframe_answers = self.page_answers.frame_locator("#course-iframe")
            next_answers = iframe_answers.get_by_role("button", name="Next")
            await next_answers.scroll_into_view_if_needed()
            await next_answers.click()
            print("  ✓ Clicked Next on answers account")
            
            # Click Next on target account
            iframe_target = self.page_target.frame_locator("#course-iframe")
            next_target = iframe_target.get_by_role("button", name="Next")
            await next_target.scroll_into_view_if_needed()
            await next_target.click()
            print("  ✓ Clicked Next on target account")
            
            # Wait for both pages to load and verify they match
            print("  Waiting for pages to load...")
            await asyncio.sleep(1)  # Small initial wait
            
            # Verify both are on the same problem
            if await self.check_problems_match():
                print("✓ Both accounts moved to the same next problem\n")
                return True
            else:
                print("⚠ WARNING: Accounts are on different problems after clicking Next!")
                return False
            
        except Exception as e:
            print(f"⚠ Could not find Next button: {e}")
            return False
            
    async def process_single_problem(self):
        """Process one problem: verify, answer, submit"""
        print("\n" + "="*60)
        print("PROCESSING NEW PROBLEM")
        print("="*60)
        
        # Verify both are on same problem
        if not await self.check_problems_match():
            print("⚠ Problems don't match - skipping")
            return False
        
        print("✓ Problem verified - processing answer...")
        
        # Handle the question (copy/paste or select answers)
        result = await self.handle_question_answer()
        
        if result == "skip":
            print("✓ Question skipped - moving to next")
            return "skipped"  # Special return value for skipped questions
            
        elif result == True:
            print("✓ Answer processed successfully")
            
            # Try to submit the solution (if submit fails, Next button will auto-submit)
            print("  Attempting to submit...")
            submit_success = await self.submit_solution()
            
            if submit_success:
                print("✓ Solution submitted manually")
                # Check if submission was successful
                if await self.check_submission_success():
                    print("✓ Submission successful!")
                    return True
                else:
                    print("⚠ Manual submission may have failed - Next button will auto-submit")
                    return True  # Continue anyway, Next will handle it
            else:
                print("⚠ Submit button not found - Next button will auto-submit")
                return True  # Continue anyway, Next will handle it
        else:
            print("⚠ Failed to process answer")
            return False
        
    async def run_automation(self, num_problems=None):
        """Main automation loop"""
        print("\n" + "="*60)
        print("STARTING AUTOMATION - FULL MODE")
        print("(Copy/paste ENABLED - full automation active)")
        print("="*60)
        
        # Initial check if problems match
        print("\nInitial problem check:")
        if not await self.check_problems_match():
            print("\n" + "="*60)
            print("⚠ WARNING: Accounts are on DIFFERENT problems!")
            print("="*60)
            print("Please manually navigate both accounts to the SAME problem.")
            input("Press ENTER when ready...")
            
            # Re-check
            if not await self.check_problems_match():
                print("✗ Still different. Exiting.")
                return
        
        print("✓ Both accounts on same problem - starting...")
        
        problems_completed = 0
        problems_failed = 0
        problems_skipped = 0
        
        try:
            while True:
                if num_problems and problems_completed >= num_problems:
                    print(f"\n✓ Completed {num_problems} problems as requested")
                    break
                    
                # Process current problem
                result = await self.process_single_problem()
                
                if result == True:
                    problems_completed += 1
                    print(f"\n✓ Problem {problems_completed} completed successfully!")
                elif result == "skipped":
                    problems_skipped += 1
                    print(f"\n✓ Problem skipped (Total skipped: {problems_skipped})")
                else:
                    problems_failed += 1
                    print(f"\n⚠ Problem failed (Total failures: {problems_failed})")
                    
                # Move to next
                if not await self.move_to_next_problem():
                    print("\n✓ Reached end of problems")
                    break
                    
                # Small pause between problems
                await asyncio.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n⚠ Automation stopped by user")
            
        print("\n" + "="*60)
        print("AUTOMATION COMPLETE")
        print("="*60)
        print(f"Problems completed: {problems_completed}")
        print(f"Problems skipped: {problems_skipped}")
        print(f"Problems failed: {problems_failed}")
        print("="*60)
        
    async def cleanup(self):
        """Keep browsers open"""
        print("\nKeeping browsers open...")
        print("✓ Browsers will remain open for manual use")


async def main():
    """Main entry point"""
    print("="*60)
    print("CODE TANTRA AUTOMATION TOOL - PLAYWRIGHT VERSION")
    print("Educational Purpose Only")
    print("="*60)
    
    automation = CodeTantraPlaywrightAutomation(auto_login=AUTO_LOGIN)
    
    async with async_playwright() as playwright:
        automation.playwright = playwright
        
        try:
            # Setup
            await automation.setup_browsers()
            
            # Navigate to Code Tantra
            if AUTO_LOGIN:
                print(f"\nUsing automatic login with credentials from credentials.py")
                await automation.navigate_to_codetantra(LOGIN_URL)
                await asyncio.sleep(2)
                
                # Login to answers account
                if await automation.login_to_account(
                    automation.page_answers,
                    ANSWERS_ACCOUNT['username'],
                    ANSWERS_ACCOUNT['password'],
                    "Answers Account"
                ):
                    print("\n✓ Answers account ready")
                else:
                    print("\n⚠ Answers account login may have failed. Check credentials.")
                    
                # Login to target account
                if await automation.login_to_account(
                    automation.page_target,
                    TARGET_ACCOUNT['username'],
                    TARGET_ACCOUNT['password'],
                    "Target Account"
                ):
                    print("\n✓ Target account ready")
                else:
                    print("\n⚠ Target account login may have failed. Check credentials.")
                    
                print("\n" + "="*60)
                print("Please navigate both accounts to the problems section")
                print("Press ENTER when both are ready to start automation...")
                input()
            else:
                print("\nEnter Code Tantra URL (or press ENTER for manual navigation):")
                url = input().strip()
                if url:
                    await automation.navigate_to_codetantra(url)
                else:
                    print("Please manually navigate both browsers to the correct page")
                
                print("\n" + "="*60)
                print("Please log in to both accounts and navigate to problems")
                print("Press ENTER when both are ready to start automation...")
                input()
            
            # Ask how many problems to process
            print("How many problems to process? (Press ENTER for all):")
            num_input = input().strip()
            num_problems = int(num_input) if num_input else None
            
            # Run automation
            await automation.run_automation(num_problems)
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            await automation.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
