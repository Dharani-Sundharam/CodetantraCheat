"""
Code Tantra Automation Tool
Educational purpose: Automates copying answers between two Firefox browser sessions
"""

import time
import sys
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
try:
    from credentials import LOGIN_URL, ANSWERS_ACCOUNT, TARGET_ACCOUNT
    AUTO_LOGIN = True
except ImportError:
    AUTO_LOGIN = False
    print("⚠ credentials.py not found. Manual login will be required.")


class CodeTantraAutomation:
    def __init__(self, auto_login=False):
        self.driver_answers = None  # Browser with answers
        self.driver_target = None   # Browser to paste answers
        self.auto_login = auto_login
        
    def setup_browsers(self):
        """Initialize two separate Firefox browser instances"""
        print("Setting up Firefox browsers...")

        # Firefox options
        options = Options()
        # options.add_argument('--headless')  # Uncomment for headless mode

        # Get screen size and split in half
        import ctypes
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        half_width = screen_width // 2
        window_height = screen_height - 40  # Leave some space for taskbar

        # Create first browser (answers - left half)
        self.driver_answers = webdriver.Firefox(options=options)
        self.driver_answers.set_window_position(0, 0)
        self.driver_answers.set_window_size(half_width, window_height)
        print("✓ First Firefox window opened (answers account - left)")

        # Create second browser (target - right half)
        self.driver_target = webdriver.Firefox(options=options)
        self.driver_target.set_window_position(half_width, 0)
        self.driver_target.set_window_size(half_width, window_height)
        print("✓ Second Firefox window opened (target account - right)")
        
    def navigate_to_codetantra(self, url):
        """Navigate both browsers to Code Tantra"""
        print(f"\nNavigating to: {url}")
        self.driver_answers.get(url)
        self.driver_target.get(url)
        print("✓ Both browsers navigated to Code Tantra")
        
    def login_to_account(self, driver, username, password, account_name):
        """Automatically log in to a Code Tantra account using form submission"""
        try:
            print(f"\nLogging in to {account_name}...")

            # Wait for login page to load
            wait = WebDriverWait(driver, 10)

            # Try to find the username field - inspect the actual page elements
            print("  Looking for username field...")

            # Check what input fields exist on the page
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"  Found {len(all_inputs)} input fields")

            for i, input_field in enumerate(all_inputs):
                input_type = input_field.get_attribute("type")
                input_name = input_field.get_attribute("name")
                input_id = input_field.get_attribute("id")
                print(f"    Input {i}: type={input_type}, name={input_name}, id={input_id}")

            # Try common selectors for username field
            username_selectors = [
                (By.ID, "user_id"),
                (By.ID, "username"),
                (By.ID, "email"),
                (By.NAME, "user_id"),
                (By.NAME, "username"),
                (By.NAME, "email"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[type='text']")
            ]

            username_field = None
            for by_method, selector_value in username_selectors:
                try:
                    username_field = driver.find_element(by_method, selector_value)
                    print(f"  ✓ Found username field: {by_method}='{selector_value}'")
                    break
                except:
                    continue

            if not username_field:
                print("  ⚠ Could not find username field")
                return False

            # Clear and enter username
            username_field.clear()
            username_field.send_keys(username)
            print(f"  ✓ Username entered: {username}")

            # Find password field
            password_selectors = [
                (By.ID, "password"),
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "input[type='password']")
            ]

            password_field = None
            for by_method, selector_value in password_selectors:
                try:
                    password_field = driver.find_element(by_method, selector_value)
                    print(f"  ✓ Found password field: {by_method}='{selector_value}'")
                    break
                except:
                    continue

            if not password_field:
                print("  ⚠ Could not find password field")
                return False

            # Clear and enter password
            password_field.clear()
            password_field.send_keys(password)
            print("  ✓ Password entered")

            # Find and click submit button
            submit_selectors = [
                (By.ID, "submit_login"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.CSS_SELECTOR, "button.btn"),
                (By.CSS_SELECTOR, "button"),
                (By.TAG_NAME, "button")
            ]

            submit_button = None
            for by_method, selector_value in submit_selectors:
                try:
                    submit_button = driver.find_element(by_method, selector_value)
                    print(f"  ✓ Found submit button: {by_method}='{selector_value}'")
                    break
                except:
                    continue

            if not submit_button:
                print("  ⚠ Could not find submit button")
                return False

            # Click submit
            submit_button.click()
            print("  ✓ Submit button clicked")

            # Wait for login to complete
            time.sleep(5)

            # Check if login was successful (not on login page anymore)
            if "login" not in driver.current_url.lower():
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
            
    def scroll_to_element(self, driver, element):
        """Scroll to make an element visible"""
        try:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠ Could not scroll to element: {e}")
            
    def find_element_with_scroll(self, driver, by, selector, scroll_attempts=3):
        """Find an element, scrolling down if not found initially"""
        for attempt in range(scroll_attempts):
            try:
                element = driver.find_element(by, selector)
                return element
            except NoSuchElementException:
                if attempt < scroll_attempts - 1:
                    # Scroll down
                    driver.execute_script("window.scrollBy(0, 300);")
                    time.sleep(0.5)
                else:
                    raise
        return None
        
    def wait_for_manual_login(self):
        """Wait for user to manually log in to both accounts"""
        print("\n" + "="*60)
        print("MANUAL LOGIN REQUIRED")
        print("="*60)
        print("Please log in to both browser windows:")
        print("  - Left window: Account WITH answers")
        print("  - Right window: Account WITHOUT answers (target)")
        print("\nPress ENTER when both accounts are logged in and ready...")
        input()
        print("✓ Login confirmed. Starting automation...\n")
        
    def get_current_problem_title(self, driver):
        """Extract the current problem button title from the iframe"""
        try:
            print("  Looking for problem button in iframe...")
            
            # Switch to the course iframe
            try:
                course_iframe = driver.find_element(By.ID, "course-iframe")
                driver.switch_to.frame(course_iframe)
                print("  ✓ Switched to course iframe")
            except Exception as e:
                print(f"  ⚠ Could not find or switch to course iframe: {e}")
                return None
            
            # Look for the current problem button (the one that's selected/active)
            try:
                # Try to find the active/selected button
                active_button = driver.find_element(By.CSS_SELECTOR, "button.min-w-0.flex-1.text-left.text-sm.font-semibold.hover\\:underline")
                
                button_title = active_button.get_attribute("title")
                button_text = active_button.text
                
                if button_title:
                    print(f"  ✓ Found problem button: '{button_title}'")
                    print(f"  Button text: '{button_text}'")
                    
                    # Switch back to main content
                    driver.switch_to.default_content()
                    return button_title
                else:
                    print("  ⚠ Button found but no title attribute")
                    driver.switch_to.default_content()
                    return None
                    
            except Exception as e:
                print(f"  ⚠ Could not find problem button: {e}")
                
                # Try to find any button with title containing problem info
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in all_buttons:
                    title = button.get_attribute("title")
                    if title and ("DDL" in title or "Flight" in title or "Reservation" in title):
                        print(f"  Found button: title='{title}', text='{button.text}'")
                        driver.switch_to.default_content()
                        return title
                
                driver.switch_to.default_content()
                return None
                
        except Exception as e:
            print(f"⚠ Error getting problem title: {e}")
            # Make sure we're back in main content
            try:
                driver.switch_to.default_content()
            except:
                pass
            return None
            
    def sync_to_same_problem(self):
        """Ensure both browsers are on the same problem"""
        print("Synchronizing problems...")
        
        max_attempts = 20
        attempts = 0
        
        while attempts < max_attempts:
            title_answers = self.get_current_problem_title(self.driver_answers)
            title_target = self.get_current_problem_title(self.driver_target)
            
            print(f"  Answers problem: '{title_answers}'")
            print(f"  Target problem: '{title_target}'")
            
            if title_answers and title_target and title_answers == title_target:
                print("✓ Both accounts are on the same problem\n")
                return True
            elif not title_answers:
                print("⚠ Could not get problem title from answers account")
                return False
            elif not title_target:
                print("⚠ Could not get problem title from target account")
                return False
                
            # If target is behind, click Next on target
            print("  Problems don't match. Navigating target account...")
            try:
                # Switch to iframe first
                course_iframe = self.driver_target.find_element(By.ID, "course-iframe")
                self.driver_target.switch_to.frame(course_iframe)
                
                next_button = self.find_element_with_scroll(
                    self.driver_target,
                    By.CSS_SELECTOR,
                    "button.btn.btn-xs.btn-info.rounded.gap-0[accesskey='n']"
                )
                self.scroll_to_element(self.driver_target, next_button)
                next_button.click()
                
                # Switch back to main content
                self.driver_target.switch_to.default_content()
                time.sleep(2)
            except NoSuchElementException:
                print("⚠ Could not find Next button on target")
                self.driver_target.switch_to.default_content()
                return False
                
            attempts += 1
            
        print("⚠ Could not sync problems after multiple attempts")
        return False
        
    def get_code_from_answers(self):
        """Extract code from the answers account editor"""
        try:
            print("Extracting code from answers account...")
            
            # Switch to iframe first
            course_iframe = self.driver_answers.find_element(By.ID, "course-iframe")
            self.driver_answers.switch_to.frame(course_iframe)
            
            # Find the CodeMirror editor content
            editor = self.find_element_with_scroll(
                self.driver_answers,
                By.CSS_SELECTOR,
                "div.cm-content[contenteditable='true']"
            )
            
            # Get all lines
            lines = editor.find_elements(By.CSS_SELECTOR, "div.cm-line")
            
            code_text = []
            for line in lines:
                # Extract text content, handling special characters
                line_text = line.get_attribute("innerText")
                if line_text is None:
                    line_text = ""
                code_text.append(line_text)
            
            full_code = "\n".join(code_text)
            print(f"✓ Extracted {len(code_text)} lines of code")
            
            # Switch back to main content
            self.driver_answers.switch_to.default_content()
            return full_code
            
        except NoSuchElementException as e:
            print(f"⚠ Could not extract code: {e}")
            self.driver_answers.switch_to.default_content()
            return None
            
    def paste_code_to_target(self, code):
        """Paste code into the target account editor"""
        try:
            print("Pasting code to target account...")
            
            # Switch to iframe first
            course_iframe = self.driver_target.find_element(By.ID, "course-iframe")
            self.driver_target.switch_to.frame(course_iframe)
            
            # Find the CodeMirror editor
            editor = self.find_element_with_scroll(
                self.driver_target,
                By.CSS_SELECTOR,
                "div.cm-content[contenteditable='true']"
            )
            
            # Scroll to editor
            self.scroll_to_element(self.driver_target, editor)
            
            # Click to focus
            editor.click()
            time.sleep(0.5)
            
            # Select all existing content
            editor.send_keys(Keys.CONTROL + "a")
            time.sleep(0.3)
            
            # Delete existing content
            editor.send_keys(Keys.DELETE)
            time.sleep(0.3)
            
            # Paste new code line by line to avoid issues
            lines = code.split('\n')
            for i, line in enumerate(lines):
                editor.send_keys(line)
                if i < len(lines) - 1:
                    editor.send_keys(Keys.ENTER)
                time.sleep(0.05)  # Small delay between lines
            
            print("✓ Code pasted successfully")
            
            # Switch back to main content
            self.driver_target.switch_to.default_content()
            return True
            
        except Exception as e:
            print(f"⚠ Error pasting code: {e}")
            self.driver_target.switch_to.default_content()
            return False
            
    def submit_solution(self):
        """Click the submit button on target account"""
        try:
            print("Submitting solution...")
            
            # Switch to iframe first
            course_iframe = self.driver_target.find_element(By.ID, "course-iframe")
            self.driver_target.switch_to.frame(course_iframe)
            
            submit_button = self.find_element_with_scroll(
                self.driver_target,
                By.CSS_SELECTOR,
                "button.btn.no-animation.btn-xs.rounded.\\!btn-success[accesskey='s']"
            )
            self.scroll_to_element(self.driver_target, submit_button)
            submit_button.click()
            print("✓ Submit button clicked")
            
            # Switch back to main content
            self.driver_target.switch_to.default_content()
            time.sleep(3)  # Wait for submission to process
            return True
            
        except NoSuchElementException:
            print("⚠ Could not find Submit button")
            self.driver_target.switch_to.default_content()
            return False
            
    def check_submission_success(self):
        """Check if submission was successful by looking for badge-success"""
        try:
            print("Checking submission result...")
            
            # Switch to iframe first
            course_iframe = self.driver_target.find_element(By.ID, "course-iframe")
            self.driver_target.switch_to.frame(course_iframe)
            
            # Wait for the result badge to appear
            wait = WebDriverWait(self.driver_target, 10)
            badge = wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "div.badge.badge-secondary.badge-sm.badge-success"
                ))
            )
            
            time_text = badge.text
            print(f"✓ Submission SUCCESSFUL! Time: {time_text}")
            
            # Switch back to main content
            self.driver_target.switch_to.default_content()
            return True
            
        except TimeoutException:
            print("⚠ Submission may have failed or timed out")
            
            # Check for error badges
            try:
                error_badge = self.driver_target.find_element(
                    By.CSS_SELECTOR,
                    "div.badge.badge-secondary.badge-sm.badge-error"
                )
                print(f"✗ Submission FAILED: {error_badge.text}")
            except NoSuchElementException:
                print("? Could not determine submission result")
            
            self.driver_target.switch_to.default_content()
            return False
            
    def move_to_next_problem(self):
        """Click Next button on both accounts"""
        try:
            print("\nMoving to next problem...")
            
            # Click Next on answers account
            course_iframe_answers = self.driver_answers.find_element(By.ID, "course-iframe")
            self.driver_answers.switch_to.frame(course_iframe_answers)
            
            next_answers = self.find_element_with_scroll(
                self.driver_answers,
                By.CSS_SELECTOR,
                "button.btn.btn-xs.btn-info.rounded.gap-0[accesskey='n']"
            )
            self.scroll_to_element(self.driver_answers, next_answers)
            next_answers.click()
            
            self.driver_answers.switch_to.default_content()
            time.sleep(1)
            
            # Click Next on target account
            course_iframe_target = self.driver_target.find_element(By.ID, "course-iframe")
            self.driver_target.switch_to.frame(course_iframe_target)
            
            next_target = self.find_element_with_scroll(
                self.driver_target,
                By.CSS_SELECTOR,
                "button.btn.btn-xs.btn-info.rounded.gap-0[accesskey='n']"
            )
            self.scroll_to_element(self.driver_target, next_target)
            next_target.click()
            
            self.driver_target.switch_to.default_content()
            time.sleep(2)
            
            print("✓ Moved to next problem\n")
            return True
            
        except NoSuchElementException:
            print("⚠ Could not find Next button. Might be at the last problem.")
            self.driver_answers.switch_to.default_content()
            self.driver_target.switch_to.default_content()
            return False
            
    def process_single_problem(self):
        """Process one problem: sync, copy, paste, submit, verify"""
        print("\n" + "="*60)
        print("PROCESSING NEW PROBLEM")
        print("="*60)
        
        # Step 1: Sync to same problem
        if not self.sync_to_same_problem():
            print("✗ Failed to sync problems")
            return False
            
        # Step 2: Get code from answers
        code = self.get_code_from_answers()
        if not code:
            print("✗ Failed to extract code")
            return False
            
        # Step 3: Paste code to target
        if not self.paste_code_to_target(code):
            print("✗ Failed to paste code")
            return False
            
        # Step 4: Submit
        if not self.submit_solution():
            print("✗ Failed to submit")
            return False
            
        # Step 5: Check success
        success = self.check_submission_success()
        
        return success
        
    def run_automation(self, num_problems=None):
        """Main automation loop"""
        print("\n" + "="*60)
        print("STARTING AUTOMATION")
        print("="*60)
        
        problems_completed = 0
        problems_failed = 0
        
        try:
            while True:
                if num_problems and problems_completed >= num_problems:
                    print(f"\n✓ Completed {num_problems} problems as requested")
                    break
                    
                # Process current problem
                success = self.process_single_problem()
                
                if success:
                    problems_completed += 1
                    print(f"\n✓ Problem {problems_completed} completed successfully!")
                else:
                    problems_failed += 1
                    print(f"\n⚠ Problem failed (Total failures: {problems_failed})")
                    
                # Move to next
                if not self.move_to_next_problem():
                    print("\n✓ Reached end of problems")
                    break
                    
                # Small pause between problems
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n⚠ Automation stopped by user")
            
        print("\n" + "="*60)
        print("AUTOMATION COMPLETE")
        print("="*60)
        print(f"Problems completed: {problems_completed}")
        print(f"Problems failed: {problems_failed}")
        print("="*60)
        
    def cleanup(self):
        """Keep browsers open"""
        print("\nKeeping browsers open...")
        print("✓ Browsers will remain open for manual use")


def main():
    """Main entry point"""
    print("="*60)
    print("CODE TANTRA AUTOMATION TOOL")
    print("Educational Purpose Only")
    print("="*60)
    
    automation = CodeTantraAutomation(auto_login=AUTO_LOGIN)
    
    try:
        # Setup
        automation.setup_browsers()
        
        # Navigate to Code Tantra
        if AUTO_LOGIN:
            print(f"\nUsing automatic login with credentials from credentials.py")
            automation.navigate_to_codetantra(LOGIN_URL)
            time.sleep(2)
            
            # Login to answers account
            if automation.login_to_account(
                automation.driver_answers,
                ANSWERS_ACCOUNT['username'],
                ANSWERS_ACCOUNT['password'],
                "Answers Account"
            ):
                print("\n✓ Answers account ready")
            else:
                print("\n⚠ Answers account login may have failed. Check credentials.")
                
            # Login to target account
            if automation.login_to_account(
                automation.driver_target,
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
                automation.navigate_to_codetantra(url)
            else:
                print("Please manually navigate both browsers to the correct page")
            
            # Wait for login
            automation.wait_for_manual_login()
        
        # Ask how many problems to process
        print("How many problems to process? (Press ENTER for all):")
        num_input = input().strip()
        num_problems = int(num_input) if num_input else None
        
        # Run automation
        automation.run_automation(num_problems)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        automation.cleanup()
        

if __name__ == "__main__":
    main()
