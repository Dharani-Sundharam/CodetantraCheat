"""
Interactive debug script to extract problem numbers from Code Tantra
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time
import re

# Import credentials
try:
    from credentials import ANSWERS_ACCOUNT
    print("✓ Loaded credentials")
except:
    print("✗ Could not load credentials.py")
    exit(1)

print("Debug: Opening browser...")

try:
    # Use webdriver-manager to auto-install geckodriver
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service)
    print("✓ Firefox opened")
    
    # Navigate to login page
    driver.get("https://rmd.codetantra.com/login.jsp")
    print("✓ Navigated to Code Tantra")
    
    time.sleep(3)
    
    # Login using the same method as debug_page.py
    print("Logging in...")
    
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    wait = WebDriverWait(driver, 10)

    # Try to find the username field
    print("  Looking for username field...")
    all_inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"  Found {len(all_inputs)} input fields")

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
        exit(1)

    username_field.clear()
    username_field.send_keys(ANSWERS_ACCOUNT['username'])
    print(f"  ✓ Username entered: {ANSWERS_ACCOUNT['username']}")

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
        exit(1)

    password_field.clear()
    password_field.send_keys(ANSWERS_ACCOUNT['password'])
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
        exit(1)

    submit_button.click()
    print("  ✓ Submit button clicked")
    
    time.sleep(5)
    print(f"✓ Logged in - Current URL: {driver.current_url}")
    
    print("\n" + "="*60)
    print("INTERACTIVE PROBLEM NUMBER EXTRACTOR")
    print("="*60)
    print("Navigate to any problem page in the browser")
    print("Press ENTER to extract the problem number")
    print("Type 'quit' to exit")
    print("="*60)
    
    while True:
        user_input = input("\nPress ENTER to extract problem number (or 'quit' to exit): ").strip().lower()
        
        if user_input == 'quit':
            break
        
        print("\nExtracting problem number...")
        
        try:
            # Check for iframe
            course_iframe = driver.find_element(By.ID, "course-iframe")
            print("✓ Found course iframe")
            
            # Switch to iframe
            driver.switch_to.frame(course_iframe)
            print("✓ Switched to iframe")
            
            # Find all buttons
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"Found {len(all_buttons)} buttons in iframe")
            
            problem_number = None
            problem_text = None
            
            # Look for button with pattern x.x.x
            for button in all_buttons:
                text = button.text.strip()
                
                # Extract pattern like "4.7.4" from "4.7.4. Object Serialization..."
                match = re.match(r'^(\d+(?:\.\d+)+)', text)
                if match:
                    problem_number = match.group(1)
                    problem_text = text
                    break
            
            # Switch back to main content
            driver.switch_to.default_content()
            
            if problem_number:
                print("\n" + "="*60)
                print("✓ FOUND PROBLEM NUMBER!")
                print("="*60)
                print(f"Problem Number: {problem_number}")
                print(f"Full Text: {problem_text}")
                print("="*60)
            else:
                print("\n⚠ No problem number found on this page")
                print("Make sure you're on a problem page (not course list)")
                
        except Exception as e:
            print(f"✗ Error extracting problem number: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nClosing browser...")
    driver.quit()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

