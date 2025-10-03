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
from comment_remover import CommentRemover

try:
    from credentials import LOGIN_URL, ANSWERS_ACCOUNT, TARGET_ACCOUNT
    AUTO_LOGIN = True
except ImportError:
    AUTO_LOGIN = False
    print("⚠ credentials.py not found. Manual login will be required.")

# Import the code question handler
try:
    from desktop_app.code_question_handler import CodeQuestionHandler
except ImportError:
    # Fallback for when running from root directory
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'desktop-app'))
    from code_question_handler import CodeQuestionHandler


class CodeTantraPlaywrightAutomation:
    def __init__(self, auto_login=False):
        self.browser_answers = None
        self.browser_target = None
        self.page_answers = None
        self.page_target = None
        self.auto_login = auto_login
        self.error_log = []  # Track errors with problem numbers
        self.comment_remover = CommentRemover()
        self.code_handler = None  # Will be initialized after browsers are set up
        
        # Problem tracking for detailed reporting
        self.problem_tracker = {
            'code_completion': {'solved': 0, 'failed': 0, 'skipped': 0},
            'multiple_choice': {'solved': 0, 'failed': 0, 'skipped': 0},
            'fill_blank': {'solved': 0, 'failed': 0, 'skipped': 0},
            'other': {'solved': 0, 'failed': 0, 'skipped': 0}
        }
    
    def track_problem_result(self, question_type: str, result: str):
        """Track problem result by type"""
        if question_type not in self.problem_tracker:
            question_type = 'other'
        
        if result in ['solved', 'failed', 'skipped']:
            self.problem_tracker[question_type][result] += 1
    
    def get_problem_summary(self):
        """Get detailed problem summary"""
        total_solved = sum(tracker['solved'] for tracker in self.problem_tracker.values())
        total_failed = sum(tracker['failed'] for tracker in self.problem_tracker.values())
        total_skipped = sum(tracker['skipped'] for tracker in self.problem_tracker.values())
        
        return {
            'total': {
                'solved': total_solved,
                'failed': total_failed,
                'skipped': total_skipped
            },
            'by_type': self.problem_tracker
        }
    
    async def maximize_and_zoom_browser(self, page, zoom_level=0.5):
        """Maximize browser window and set zoom level for better code visibility"""
        try:
            print(f"  Maximizing window and setting zoom to {zoom_level*100}%...")
            
            # Maximize the window
            await page.evaluate("""
                window.moveTo(0, 0);
                window.resizeTo(screen.width, screen.height);
            """)
            
            # Set zoom level for better code visibility
            await page.evaluate(f"document.body.style.zoom = '{zoom_level}'")
            
            # Also try setting viewport zoom
            await page.evaluate(f"document.documentElement.style.zoom = '{zoom_level}'")
            
            print(f"  ✓ Window maximized and zoomed to {zoom_level*100}%")
            
        except Exception as e:
            print(f"  ⚠ Could not maximize/zoom window: {e}")
    
    async def scroll_through_editor(self, editor):
        """Scroll through the entire editor to ensure all lines are loaded"""
        try:
            print("  Scrolling through editor to load all lines...")
            
            # Get the editor's scrollable container
            scroll_container = await editor.evaluate("""
                () => {
                    const editor = document.querySelector('div.cm-content[contenteditable="true"]');
                    if (!editor) return null;
                    
                    // Find the scrollable parent
                    let parent = editor.parentElement;
                    while (parent && parent !== document.body) {
                        const style = window.getComputedStyle(parent);
                        if (style.overflow === 'auto' || style.overflow === 'scroll' || 
                            style.overflowY === 'auto' || style.overflowY === 'scroll') {
                            return parent;
                        }
                        parent = parent.parentElement;
                    }
                    return editor;
                }
            """)
            
            if scroll_container:
                # Scroll to top first
                await editor.evaluate("arguments[0].scrollTop = 0", scroll_container)
                await self.page_answers.wait_for_timeout(200)
                
                # Scroll to bottom to load all content
                await editor.evaluate("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
                await self.page_answers.wait_for_timeout(500)
                
                # Scroll back to top
                await editor.evaluate("arguments[0].scrollTop = 0", scroll_container)
                await self.page_answers.wait_for_timeout(200)
                
                print("  ✓ Scrolled through entire editor")
            else:
                print("  ⚠ Could not find scrollable container")
                
        except Exception as e:
            print(f"  ⚠ Could not scroll through editor: {e}")
    
    async def scroll_through_editor_iframe(self, iframe):
        """Scroll through the entire editor in iframe to ensure all lines are loaded"""
        try:
            print("  Scrolling through iframe editor to load all lines...")
            
            # Scroll within the iframe
            await iframe.evaluate("""
                () => {
                    // Scroll to top
                    window.scrollTo(0, 0);
                    
                    // Find the CodeMirror editor
                    const editor = document.querySelector('div.cm-content[contenteditable="true"]');
                    if (editor) {
                        // Scroll the editor container
                        const scrollContainer = editor.closest('.cm-editor') || editor.parentElement;
                        if (scrollContainer) {
                            scrollContainer.scrollTop = 0;
                            
                            // Scroll to bottom to load all content
                            setTimeout(() => {
                                scrollContainer.scrollTop = scrollContainer.scrollHeight;
                            }, 100);
                            
                            // Scroll back to top
                            setTimeout(() => {
                                scrollContainer.scrollTop = 0;
                            }, 300);
                        }
                    }
                }
            """)
            
            await self.page_answers.wait_for_timeout(800)  # Wait for scrolling to complete
            print("  ✓ Scrolled through iframe editor")
                
        except Exception as e:
            print(f"  ⚠ Could not scroll through iframe editor: {e}")
    
    def detect_code_language(self, code):
        """Detect programming language from code content"""
        code_lower = code.lower()
        
        # Java indicators
        if any(keyword in code_lower for keyword in ['public class', 'system.out.println', 'import java', 'static void main']):
            return 'java'
        
        # C++ indicators
        if any(keyword in code_lower for keyword in ['#include <iostream>', 'using namespace std', 'cout <<', 'cin >>']):
            return 'cpp'
        
        # C indicators
        if any(keyword in code_lower for keyword in ['#include <stdio.h>', 'printf(', 'scanf(', 'int main()']):
            return 'c'
        
        # Python indicators
        if any(keyword in code_lower for keyword in ['def ', 'import ', 'print(', 'if __name__']):
            return 'python'
        
        # JavaScript indicators
        if any(keyword in code_lower for keyword in ['function ', 'console.log', 'var ', 'let ', 'const ']):
            return 'javascript'
        
        # Default to Java for CodeTantra
        return 'java'
        
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
        self.context_answers = await self.browser_answers.new_context(
            viewport={'width': half_width, 'height': window_height}
        )
        self.page_answers = await self.context_answers.new_page()
        
        # Position and resize using JavaScript
        await self.page_answers.evaluate(f"""
            window.resizeTo({half_width}, {window_height});
            window.moveTo(0, 0);
        """)
        
        # Maximize and zoom for better code visibility
        await self.maximize_and_zoom_browser(self.page_answers, zoom_level=0.6)
        
        print("✓ First browser window opened (answers account - left)")

        # Create second browser (target - right half)
        self.browser_target = await self.playwright.firefox.launch(headless=False)
        self.context_target = await self.browser_target.new_context(
            viewport={'width': half_width, 'height': window_height}
        )
        self.page_target = await self.context_target.new_page()
        
        # Position and resize using JavaScript
        await self.page_target.evaluate(f"""
            window.resizeTo({half_width}, {window_height});
            window.moveTo({half_width}, 0);
        """)
        
        # Maximize and zoom for better code visibility
        await self.maximize_and_zoom_browser(self.page_target, zoom_level=0.6)
        
        print("✓ Second browser window opened (target account - right)")
        
        # Initialize code question handler
        self.code_handler = CodeQuestionHandler(self.page_answers, self.page_target, self.comment_remover)
        
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
        """Main function to handle different question types with Type 2 support"""
        try:
            # Detect question type on answers account
            question_type = await self.detect_question_type(self.page_answers)
            print(f"Question type detected: {question_type}")
            
            if question_type == "code_completion":
                # Use the code question handler
                return await self.code_handler.handle_code_completion_question()
                    
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
    
    async def submit_solution(self, question_type=None):
        """Click the submit button with cleanup and retry if needed"""
        try:
            print("Submitting solution...")
            
            # Switch to iframe first
            iframe = self.page_target.frame_locator("#course-iframe")
            
            # Try submission up to 2 times with cleanup
            for attempt in range(2):
                print(f"  Attempt {attempt + 1}/2...")
                
                # Deletion already done after typing, no need to delete again before submission
                
                # Step 2: Wait for submit button to be available
                print("  Waiting for submit button to be available...")
                try:
                    submit_button = iframe.locator("[id=\"__ss-content-actions\"]").get_by_role("button", name="Submit")
                    await submit_button.wait_for(state="visible", timeout=30000)  # 30 second timeout
                    print("  ✓ Submit button found")
                except Exception as e:
                    print(f"  ⚠ Submit button not found within 30 seconds: {e}")
                    if attempt < 1:  # Not the last attempt (changed from 2 to 1 for 2 attempts total)
                        print("  Retrying with more cleanup...")
                        continue
                    return False
                
                # Step 3: Click the submit button
                await submit_button.scroll_into_view_if_needed()
                await submit_button.click()
                print("✓ Submit button clicked")
                
                # Step 4: Wait for submission to process
                print("  Waiting for submission to process...")
                await self.page_target.wait_for_timeout(5000)  # 5 second wait after click
                
                # Step 5: Check if submission was successful
                success = await self.check_submission_success()
                if success:
                    print("✓ Submission successful!")
                    return True
                else:
                    print("⚠ Submission failed, retrying with more cleanup...")
                    if attempt < 1:  # Not the last attempt (changed from 2 to 1 for 2 attempts total)
                        # Move to end and clean up more
                        await editor.press("Control+End")
                        await self.page_target.wait_for_timeout(200)
                        continue
                    else:
                        print("✗ All submission attempts failed")
                        return False
            
            return False
            
        except Exception as e:
            print(f"⚠ Could not find or click Submit button: {e}")
            return False
            
    async def check_submission_success(self):
        """Check if submission was successful - uses new test case verification"""
        try:
            # Use the new verification method that looks for "Test case passed successfully"
            return await self.verify_submission_with_test_case()
            
        except Exception as e:
            print(f"⚠ Submission verification error: {e}")
            return False
    
    async def cleanup_extra_brackets(self, editor):
        """Clean up any remaining auto-closed brackets by pressing Delete repeatedly for 12 seconds"""
        try:
            print("  🧹 Cleaning up extra brackets (12 seconds, 20ms intervals)...")
            
            import time
            
            # Focus the editor first
            await editor.click()
            await self.page_target.wait_for_timeout(100)
            
            # Press delete repeatedly for 12 seconds with 20ms intervals (no cursor positioning)
            start_time = time.time()
            delete_duration = 12  # 12 seconds
            interval = 0.02  # 20ms = 0.02 seconds
            
            while time.time() - start_time < delete_duration:
                await editor.press("Delete")
                await self.page_target.wait_for_timeout(20)  # 20ms interval
            
            print("  ✓ Cleanup complete (12 seconds of repeated Delete presses)")
            
        except Exception as e:
            print(f"  ⚠ Cleanup failed: {e}")
    
    async def verify_submission_with_test_case(self):
        """Verify submission by checking for test case success messages - prioritizes text-based verification"""
        try:
            print("🔍 Verifying submission result...")
            
            iframe = self.page_target.frame_locator("#course-iframe")
            
            # Wait a bit for results to load
            await self.page_target.wait_for_timeout(3000)
            
            # PRIMARY: Check for "Test case passed successfully" text (user's preferred method)
            try:
                success_text = iframe.get_by_text("Test case passed successfully")
                await success_text.wait_for(state="visible", timeout=5000)
                print("✓ SUCCESS: 'Test case passed successfully' found!")
                return True
            except:
                pass
            
            # SECONDARY: Check for hidden test case success (1 hidden test case)
            try:
                hidden_success = iframe.get_by_text("out of 1 hidden test case(s) passed")
                await hidden_success.wait_for(state="visible", timeout=5000)
                print("✓ SUCCESS: 'out of 1 hidden test case(s) passed' found!")
                return True
            except:
                pass
            
            # TERTIARY: Check for shown test case success (2 shown test cases)
            try:
                shown_success = iframe.get_by_text("out of 2 shown test case(s) passed")
                await shown_success.wait_for(state="visible", timeout=5000)
                print("✓ SUCCESS: 'out of 2 shown test case(s) passed' found!")
                return True
            except:
                pass
            
            # QUATERNARY: Check for other test case success patterns
            try:
                # Look for any pattern like "out of X test case(s) passed"
                test_success = iframe.get_by_text("test case(s) passed", exact=False)
                await test_success.wait_for(state="visible", timeout=3000)
                print("✓ SUCCESS: Test case success message found!")
                return True
            except:
                pass
            
            # Badge method removed as requested by user
            
            print("✗ FAILED: No test case success indicators found")
            return False
            
        except Exception as e:
            print(f"⚠ Could not verify submission: {e}")
            return False
    
    async def move_to_next_problem(self):
        """Click Next button on both accounts and verify they match"""
        try:
            print("\nMoving to next problem...")
            
            # Click Next on answers account
            iframe_answers = self.page_answers.frame_locator("#course-iframe")
            
            # Try multiple methods to find Next button
            try:
                # Method 1: By role
                next_answers = iframe_answers.get_by_role("button", name="Next")
                await next_answers.wait_for(state="visible", timeout=5000)
            except:
                try:
                    # Method 2: By text
                    next_answers = iframe_answers.get_by_text("Next", exact=True)
                    await next_answers.wait_for(state="visible", timeout=5000)
                except:
                    # Method 3: By CSS selector
                    next_answers = iframe_answers.locator("button:has-text('Next')")
                    await next_answers.wait_for(state="visible", timeout=5000)
            
            await next_answers.scroll_into_view_if_needed()
            await next_answers.click()
            print("  ✓ Clicked Next on answers account")
            
            # Click Next on target account
            iframe_target = self.page_target.frame_locator("#course-iframe")
            
            # Try multiple methods to find Next button
            try:
                # Method 1: By role
                next_target = iframe_target.get_by_role("button", name="Next")
                await next_target.wait_for(state="visible", timeout=5000)
            except:
                try:
                    # Method 2: By text
                    next_target = iframe_target.get_by_text("Next", exact=True)
                    await next_target.wait_for(state="visible", timeout=5000)
                except:
                    # Method 3: By CSS selector
                    next_target = iframe_target.locator("button:has-text('Next')")
                    await next_target.wait_for(state="visible", timeout=5000)
            
            await next_target.scroll_into_view_if_needed()
            await next_target.click()
            print("  ✓ Clicked Next on target account")
            
            # Wait for both pages to load and verify they match
            print("  Waiting for pages to load...")
            await asyncio.sleep(2)  # Increased wait time for page load
            
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
        """Process one problem: verify, answer, submit with error tracking"""
        # Process problem silently (no console output)
        
        # Get current problem number for tracking
        current_problem = await self.get_current_problem_number(self.page_target)
        
        # Verify both are on same problem
        if not await self.check_problems_match():
            error_msg = "Problems don't match between accounts"
            self.error_log.append({
                'problem': current_problem or "Unknown",
                'error': error_msg
            })
            return False
        
        # Detect question type for appropriate handling
        question_type = await self.detect_question_type(self.page_answers)
        
        try:
            # Handle the question (copy/paste or select answers)
            result = await self.handle_question_answer()
            
            if result == "skip":
                return "skipped"  # Special return value for skipped questions
                
            elif result == True:
                # Submit the solution
                try:
                    submit_success = await self.submit_solution(question_type)
                    
                    if submit_success:
                        # For code completion: verify with test cases
                        if question_type == "code_completion":
                            if await self.check_submission_success():
                                self.track_problem_result(question_type, 'solved')
                                # Deduct credits for solved problem
                                if hasattr(self, 'automation_runner'):
                                    self.automation_runner.deduct_credits_for_problem(question_type, True)
                                return True
                            else:
                                self.error_log.append({
                                    'problem': current_problem or "Unknown",
                                    'error': "Submission verification failed - test case not passed"
                                })
                                self.track_problem_result(question_type, 'skipped')
                                # Deduct credits for skipped problem
                                if hasattr(self, 'automation_runner'):
                                    self.automation_runner.deduct_credits_for_problem(question_type, False)
                                return "skipped"
                        else:
                            # For non-code questions: just wait a moment and proceed
                            await self.page_target.wait_for_timeout(2000)  # Wait 2 seconds
                            self.track_problem_result(question_type, 'solved')
                            # Deduct credits for solved problem
                            if hasattr(self, 'automation_runner'):
                                self.automation_runner.deduct_credits_for_problem(question_type, True)
                            return True
                    else:
                        self.error_log.append({
                            'problem': current_problem or "Unknown",
                            'error': "Submit button not found"
                        })
                        self.track_problem_result(question_type, 'skipped')
                        # Deduct credits for skipped problem
                        if hasattr(self, 'automation_runner'):
                            self.automation_runner.deduct_credits_for_problem(question_type, False)
                        return "skipped"
                except Exception as e:
                    self.error_log.append({
                        'problem': current_problem or "Unknown",
                        'error': f"Submission error: {str(e)}"
                    })
                    self.track_problem_result(question_type, 'skipped')
                    # Deduct credits for skipped problem
                    if hasattr(self, 'automation_runner'):
                        self.automation_runner.deduct_credits_for_problem(question_type, False)
                    return "skipped"
            else:
                error_msg = "Failed to process answer"
                self.error_log.append({
                    'problem': current_problem or "Unknown",
                    'error': error_msg
                })
                self.track_problem_result(question_type, 'failed')
                # Deduct credits for failed problem
                if hasattr(self, 'automation_runner'):
                    self.automation_runner.deduct_credits_for_problem(question_type, False)
                return False
                
        except Exception as e:
            error_msg = f"Exception during processing: {str(e)}"
            self.error_log.append({
                'problem': current_problem or "Unknown",
                'error': error_msg
            })
            self.track_problem_result(question_type, 'failed')
            # Deduct credits for failed problem
            if hasattr(self, 'automation_runner'):
                self.automation_runner.deduct_credits_for_problem(question_type, False)
            return False
    
    async def run_automation(self, num_problems=None):
        """Main automation loop"""
        # Keep checking until problems match (no early return)
        while not await self.check_problems_match():
            print("Problems don't match - waiting for user to sync...")
            await asyncio.sleep(3)  # Wait 3 seconds before checking again
        
        print("Problems matched - starting automation")
        
        # Both accounts are on same problem - proceed
        
        problems_completed = 0
        problems_failed = 0
        problems_skipped = 0
        total_problems_processed = 0
        
        try:
            while True:
                # Check if we have enough credits for the next problem
                if hasattr(self, 'automation_runner'):
                    current_credits = self.automation_runner.api_client.get_credits()
                    if current_credits is not None and current_credits < 1:
                        print("Insufficient credits to continue - stopping automation")
                        break
                    
                # Process current problem
                result = await self.process_single_problem()
                total_problems_processed += 1
                
                if result == True:
                    problems_completed += 1
                    print(f"✓ Problem {total_problems_processed} completed successfully")
                elif result == "skipped":
                    problems_skipped += 1
                    print(f"⏭️ Problem {total_problems_processed} skipped")
                else:
                    problems_failed += 1
                    print(f"✗ Problem {total_problems_processed} failed")
                
                # Check if we've reached the target number of total problems processed
                if num_problems and total_problems_processed >= num_problems:
                    print(f"✓ Processed {num_problems} problems as requested - stopping automation")
                    break
                    
                # Move to next
                if not await self.move_to_next_problem():
                    print("✓ Reached end of problems - stopping automation")
                    break
                    
                # Small pause between problems
                await asyncio.sleep(2)
                
        except KeyboardInterrupt:
            pass  # Automation stopped by user
            
        # Get detailed problem summary for UI reporting
        summary = self.get_problem_summary()
        
        # Store summary for UI display (no console output)
        self.final_summary = summary
        
        # Store error log for UI display (no console output)
        self.final_error_log = self.error_log
    
    async def cleanup(self):
        """Properly close browsers and contexts to avoid asyncio warnings"""
        try:
            print("\nCleaning up browser resources...")
            
            # Close pages first
            if hasattr(self, 'page_answers') and self.page_answers:
                print("✓ Closing answers page...")
                await self.page_answers.close()
                self.page_answers = None
            
            if hasattr(self, 'page_target') and self.page_target:
                print("✓ Closing target page...")
                await self.page_target.close()
                self.page_target = None
            
            # Close contexts
            if hasattr(self, 'context_answers') and self.context_answers:
                print("✓ Closing answers context...")
                await self.context_answers.close()
                self.context_answers = None
            
            if hasattr(self, 'context_target') and self.context_target:
                print("✓ Closing target context...")
                await self.context_target.close()
                self.context_target = None
            
            # Close browsers
            if hasattr(self, 'browser_answers') and self.browser_answers:
                print("✓ Closing answers browser...")
                await self.browser_answers.close()
                self.browser_answers = None
            
            if hasattr(self, 'browser_target') and self.browser_target:
                print("✓ Closing target browser...")
                await self.browser_target.close()
                self.browser_target = None
            
            print("✓ All browser resources cleaned up")
            
        except Exception as e:
            print(f"⚠ Error during cleanup: {e}")


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
