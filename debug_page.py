"""
Simple debug script to see what's actually on the page
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Import credentials
try:
    from credentials import ANSWERS_ACCOUNT
    print("✓ Loaded credentials")
except:
    print("✗ Could not load credentials.py")
    exit(1)

print("Debug: Opening browser...")

try:
    driver = webdriver.Firefox()
    print("✓ Firefox opened")
    
    # Navigate to login page
    driver.get("https://rmd.codetantra.com/login.jsp")
    print("✓ Navigated to Code Tantra")
    
    time.sleep(3)
    
    # Login using the same method as main automation
    print("Logging in...")
    
    # Wait for login page to load
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
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
        exit(1)

    # Clear and enter username
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

    # Clear and enter password
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

    # Click submit
    submit_button.click()
    print("  ✓ Submit button clicked")

    # Wait for login to complete
    time.sleep(20)
    
    print(f"Current URL: {driver.current_url}")
    print(f"Page title: {driver.title}")
    
    # Check for iframes first
    print("\nChecking for iframes...")
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Found {len(iframes)} iframes")
    
    for i, iframe in enumerate(iframes):
        iframe_id = iframe.get_attribute("id")
        iframe_src = iframe.get_attribute("src")
        print(f"  Iframe {i}: id='{iframe_id}', src='{iframe_src}'")
    
    # Look for the course iframe specifically
    try:
        course_iframe = driver.find_element(By.ID, "course-iframe")
        print(f"\n✓ Found course iframe: {course_iframe.get_attribute('src')}")
        
        # Switch to the iframe
        print("Switching to course iframe...")
        driver.switch_to.frame(course_iframe)
        print("✓ Switched to iframe")
        
        # Now get text from inside the iframe
        iframe_body = driver.find_element(By.TAG_NAME, "body")
        iframe_text = iframe_body.get_attribute("innerText")
        print(f"\nIframe has {len(iframe_text)} characters of text")
        
        # Show first 1000 characters from iframe
        print("\nFirst 1000 characters from iframe:")
        print("="*50)
        print(iframe_text[:1000])
        print("="*50)
        
        # Look for the specific button with title "DDL - Flight Reservation System"
        print("\nLooking for the problem button...")
        try:
            problem_button = driver.find_element(By.CSS_SELECTOR, 'button[title="DDL - Flight Reservation System"]')
            print("✓ FOUND the problem button!")
            print(f"  Button text: {problem_button.text}")
            print(f"  Button title: {problem_button.get_attribute('title')}")
            print(f"  Button classes: {problem_button.get_attribute('class')}")
            
            # Click the button to open the problem
            print("\nClicking the problem button...")
            problem_button.click()
            time.sleep(3)
            
            # Now get the content after clicking
            print("\nGetting problem content after clicking...")
            current_url = driver.current_url
            print(f"Current URL after click: {current_url}")
            
            # Get all text from the page after clicking
            page_text = driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
            print(f"\nPage content after clicking ({len(page_text)} characters):")
            print("="*80)
            print(page_text[:2000])  # Show first 2000 characters
            print("="*80)
            
            # Look for the specific problem content
            if "You are working on a flight reservation system" in page_text:
                print("\n✓ FOUND the problem content!")
                
                # Find the exact position
                pos = page_text.find("You are working on a flight reservation system")
                start = max(0, pos - 200)
                end = min(len(page_text), pos + 1000)
                context = page_text[start:end]
                print(f"\nProblem content context:")
                print("="*80)
                print(context)
                print("="*80)
            else:
                print("\n✗ Problem content not found after clicking")
                
                # Look for any content that might be the problem
                print("\nLooking for any content containing 'flight' or 'reservation':")
                lines = page_text.split('\n')
                for i, line in enumerate(lines):
                    if 'flight' in line.lower() or 'reservation' in line.lower():
                        print(f"Line {i}: {line.strip()}")
            
        except Exception as e:
            print(f"✗ Could not find or click the specific problem button: {e}")
            
            # Try to find any button with "flight" or "reservation" in title
            print("\nLooking for any button with 'flight' or 'reservation' in title...")
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for i, button in enumerate(all_buttons):
                title = button.get_attribute("title")
                text = button.text
                if title and ("flight" in title.lower() or "reservation" in title.lower()):
                    print(f"  Button {i}: title='{title}', text='{text}'")
                elif text and ("flight" in text.lower() or "reservation" in text.lower()):
                    print(f"  Button {i}: title='{title}', text='{text}'")
        
        # Check if our text exists in iframe
        if "flight reservation system" in iframe_text.lower():
            print("\n✓ FOUND 'flight reservation system' in iframe text!")
            
            # Find the position
            pos = iframe_text.lower().find("flight reservation system")
            start = max(0, pos - 100)
            end = min(len(iframe_text), pos + 200)
            context = iframe_text[start:end]
            print(f"\nContext around the text:")
            print("="*50)
            print(context)
            print("="*50)
        else:
            print("\n✗ 'flight reservation system' NOT found in iframe text")
            
            # Show what text we do have in iframe
            print("\nLooking for any text containing 'flight' or 'reservation' in iframe:")
            lines = iframe_text.split('\n')
            for i, line in enumerate(lines):
                if 'flight' in line.lower() or 'reservation' in line.lower():
                    print(f"Line {i}: {line.strip()}")
        
        # Show iframe structure
        print(f"\nIframe structure:")
        print(f"- Total divs: {len(driver.find_elements(By.TAG_NAME, 'div'))}")
        print(f"- Total paragraphs: {len(driver.find_elements(By.TAG_NAME, 'p'))}")
        print(f"- Total buttons: {len(driver.find_elements(By.TAG_NAME, 'button'))}")
        
        # Switch back to main content
        driver.switch_to.default_content()
        print("✓ Switched back to main content")
        
    except Exception as e:
        print(f"✗ Could not find or access course iframe: {e}")
        
        # Fallback: check main page
        print("\nChecking main page content...")
        body_text = driver.find_element(By.TAG_NAME, "body").get_attribute("innerText")
        print(f"Main page has {len(body_text)} characters of text")
        
        if "flight reservation system" in body_text.lower():
            print("✓ FOUND 'flight reservation system' in main page!")
        else:
            print("✗ 'flight reservation system' NOT found in main page")
    
    input("\nPress ENTER to close browser...")
    driver.quit()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
