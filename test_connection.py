"""
Quick test to verify browser connection and element detection
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Import credentials
try:
    from credentials import ANSWERS_ACCOUNT
    print("✓ Loaded credentials")
except:
    print("✗ Could not load credentials.py")
    exit(1)

print("Testing browser connection...")

# Try to connect to existing browser or create new one
try:
    driver = webdriver.Firefox()
    print("✓ Firefox opened")
    
    # Navigate to login page
    driver.get("https://rmd.codetantra.com/login.jsp")
    print("✓ Navigated to Code Tantra")
    
    time.sleep(3)
    
    # Try to login using the same method as main automation
    print("\nAttempting login...")
    try:
        # Wait for login page to load
        wait = WebDriverWait(driver, 20)

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
            raise Exception("Username field not found")

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
            raise Exception("Password field not found")

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
            raise Exception("Submit button not found")

        # Click submit
        submit_button.click()
        print("  ✓ Submit button clicked")

        # Wait for login to complete
        time.sleep(5)

        # Check if login was successful (not on login page anymore)
        if "login" not in driver.current_url.lower():
            print("✓ Successfully logged in!")
            print(f"Current URL: {driver.current_url}")
        else:
            print("⚠ Still on login page - login may have failed")
            
    except Exception as e:
        print(f"✗ Login failed: {e}")
        import traceback
        traceback.print_exc()
    
    time.sleep(3)
    
    # Test multiple alternative approaches to find the problem content
    print("\nTesting multiple approaches to find problem content...")
    
    # Approach 1: JavaScript search
    print("\n1. JavaScript search for text...")
    try:
        js_result = driver.execute_script("""
            var elements = document.querySelectorAll('*');
            for (var i = 0; i < elements.length; i++) {
                var text = elements[i].textContent || elements[i].innerText;
                if (text && text.includes('flight reservation system')) {
                    return {
                        tagName: elements[i].tagName,
                        className: elements[i].className,
                        id: elements[i].id,
                        textPreview: text.substring(0, 200),
                        fullText: text
                    };
                }
            }
            return null;
        """)
        
        if js_result:
            print(f"✓ JavaScript found element: {js_result['tagName']}")
            print(f"  Classes: {js_result['className']}")
            print(f"  ID: {js_result['id']}")
            print(f"  Text preview: {js_result['textPreview']}")
        else:
            print("✗ JavaScript search found nothing")
    except Exception as e:
        print(f"✗ JavaScript search failed: {e}")
    
    # Approach 2: Search by text content using XPath
    print("\n2. XPath text search...")
    try:
        xpath_text = "//*[contains(text(), 'flight reservation system')]"
        elements = driver.find_elements(By.XPATH, xpath_text)
        print(f"✓ Found {len(elements)} elements containing 'flight reservation system'")
        
        for i, elem in enumerate(elements[:3]):
            tag_name = elem.tag_name
            text_content = elem.get_attribute("innerText")[:100] if elem.get_attribute("innerText") else "No text"
            print(f"  Element {i} ({tag_name}): {text_content}...")
            
    except Exception as e:
        print(f"✗ XPath text search failed: {e}")
    
    # Approach 3: Search all paragraphs
    print("\n3. Search all paragraphs...")
    try:
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        print(f"✓ Found {len(paragraphs)} paragraph elements")
        
        for i, p in enumerate(paragraphs):
            text_content = p.get_attribute("innerText")
            if text_content and "flight reservation system" in text_content.lower():
                print(f"✓ Found problem text in paragraph {i}")
                print(f"  Text: {text_content[:200]}...")
                print(f"  Classes: {p.get_attribute('class')}")
                break
    except Exception as e:
        print(f"✗ Paragraph search failed: {e}")
    
    # Approach 4: Search all divs with specific text
    print("\n4. Search all divs...")
    try:
        all_divs = driver.find_elements(By.TAG_NAME, "div")
        print(f"✓ Found {len(all_divs)} div elements")
        
        found_count = 0
        for i, div in enumerate(all_divs):
            try:
                text_content = div.get_attribute("innerText")
                if text_content and "flight reservation system" in text_content.lower():
                    found_count += 1
                    print(f"✓ Found problem text in div {i} (found {found_count})")
                    print(f"  Classes: {div.get_attribute('class')}")
                    print(f"  Text preview: {text_content[:100]}...")
                    
                    if found_count >= 3:  # Show first 3 matches
                        break
            except:
                continue
                
        if found_count == 0:
            print("✗ No divs found containing problem text")
    except Exception as e:
        print(f"✗ Div search failed: {e}")
    
    # Approach 5: Get page source and search
    print("\n5. Page source search...")
    try:
        page_source = driver.page_source
        if "flight reservation system" in page_source:
            print("✓ Problem text found in page source")
            
            # Find the position in the HTML
            pos = page_source.find("flight reservation system")
            start = max(0, pos - 200)
            end = min(len(page_source), pos + 200)
            context = page_source[start:end]
            print(f"  Context around text: ...{context}...")
        else:
            print("✗ Problem text NOT found in page source")
    except Exception as e:
        print(f"✗ Page source search failed: {e}")
    
    # Approach 6: Check current page info
    print("\n6. Current page information...")
    try:
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        print(f"Page source length: {len(driver.page_source)} characters")
        
        # Check if we're on the right page
        if "codetantra" in driver.current_url.lower():
            print("✓ On Code Tantra website")
        else:
            print("⚠ Not on Code Tantra website")
            
    except Exception as e:
        print(f"✗ Page info check failed: {e}")
    
    # Test 3: Look for navigation buttons (based on HTML structure)
    print("\nLooking for navigation elements...")
    
    # Look for buttons with specific classes from the HTML
    button_selectors = [
        "button[title='Contents list']",
        "button.btn.btn-circle",
        "button.tab",
        "button[class*='btn']"
    ]
    
    for selector in button_selectors:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"✓ Found {len(buttons)} elements with selector: {selector}")
            
            for i, button in enumerate(buttons[:3]):  # Show first 3
                button_text = button.get_attribute("innerText")
                button_title = button.get_attribute("title")
                button_class = button.get_attribute("class")
                print(f"  Button {i}: text='{button_text}', title='{button_title}', class='{button_class}'")
                
        except Exception as e:
            print(f"✗ Error with selector {selector}: {e}")
    
    # Test 4: Look for any elements containing "flight" or "reservation"
    print("\nSearching for any elements containing 'flight' or 'reservation'...")
    try:
        # Search in all elements
        all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'flight') or contains(text(), 'reservation')]")
        print(f"✓ Found {len(all_elements)} elements containing 'flight' or 'reservation'")
        
        for i, elem in enumerate(all_elements[:5]):  # Show first 5
            tag_name = elem.tag_name
            text_content = elem.get_attribute("innerText")[:100] if elem.get_attribute("innerText") else "No text"
            print(f"  Element {i} ({tag_name}): {text_content}...")
            
    except Exception as e:
        print(f"✗ Error searching for flight/reservation text: {e}")
    
    input("\nPress ENTER to close browser...")
    driver.quit()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
