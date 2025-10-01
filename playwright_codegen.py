"""
Playwright Code Generator
Helps generate selectors and test element detection
"""

import asyncio
from playwright.async_api import async_playwright


async def codegen_helper():
    """Interactive code generator to help find elements"""
    print("="*60)
    print("PLAYWRIGHT CODE GENERATOR")
    print("="*60)
    
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("Please navigate to the page you want to inspect...")
            input("Press ENTER when ready...")
            
            print("\n" + "="*60)
            print("ELEMENT INSPECTION MODE")
            print("="*60)
            print("Commands:")
            print("  'iframe' - Switch to iframe inspection")
            print("  'buttons' - List all buttons")
            print("  'inputs' - List all input fields")
            print("  'divs' - List all divs with specific text")
            print("  'click <selector>' - Click an element")
            print("  'text <text>' - Find elements containing text")
            print("  'quit' - Exit")
            print("="*60)
            
            iframe_mode = False
            current_frame = None
            
            while True:
                try:
                    command = input("\nEnter command: ").strip().lower()
                    
                    if command == "quit":
                        break
                    elif command == "iframe":
                        print("Switching to iframe mode...")
                        try:
                            iframe = page.frame_locator("#course-iframe")
                            current_frame = iframe
                            iframe_mode = True
                            print("✓ Switched to course iframe")
                        except Exception as e:
                            print(f"✗ Could not find iframe: {e}")
                    elif command == "buttons":
                        print("\nFinding all buttons...")
                        if iframe_mode and current_frame:
                            buttons = current_frame.locator("button")
                        else:
                            buttons = page.locator("button")
                        
                        count = await buttons.count()
                        print(f"Found {count} buttons:")
                        
                        for i in range(min(count, 20)):  # Show first 20
                            button = buttons.nth(i)
                            text = await button.text_content()
                            title = await button.get_attribute("title")
                            classes = await button.get_attribute("class")
                            print(f"  {i}: text='{text}', title='{title}', classes='{classes}'")
                            
                    elif command == "inputs":
                        print("\nFinding all input fields...")
                        if iframe_mode and current_frame:
                            inputs = current_frame.locator("input")
                        else:
                            inputs = page.locator("input")
                        
                        count = await inputs.count()
                        print(f"Found {count} input fields:")
                        
                        for i in range(count):
                            input_elem = inputs.nth(i)
                            input_type = await input_elem.get_attribute("type")
                            input_name = await input_elem.get_attribute("name")
                            input_id = await input_elem.get_attribute("id")
                            input_class = await input_elem.get_attribute("class")
                            print(f"  {i}: type='{input_type}', name='{input_name}', id='{input_id}', class='{input_class}'")
                            
                    elif command.startswith("click "):
                        selector = command[6:]
                        print(f"Clicking: {selector}")
                        try:
                            if iframe_mode and current_frame:
                                element = current_frame.locator(selector)
                            else:
                                element = page.locator(selector)
                            
                            await element.click()
                            print("✓ Clicked successfully")
                        except Exception as e:
                            print(f"✗ Click failed: {e}")
                            
                    elif command.startswith("text "):
                        search_text = command[5:]
                        print(f"Searching for text: '{search_text}'")
                        try:
                            if iframe_mode and current_frame:
                                elements = current_frame.locator(f"text={search_text}")
                            else:
                                elements = page.locator(f"text={search_text}")
                            
                            count = await elements.count()
                            print(f"Found {count} elements containing '{search_text}':")
                            
                            for i in range(min(count, 10)):  # Show first 10
                                element = elements.nth(i)
                                tag_name = await element.evaluate("el => el.tagName")
                                text_content = await element.text_content()
                                print(f"  {i}: <{tag_name}> {text_content[:100]}...")
                                
                        except Exception as e:
                            print(f"✗ Search failed: {e}")
                            
                    elif command == "divs":
                        print("\nFinding divs with specific content...")
                        try:
                            if iframe_mode and current_frame:
                                divs = current_frame.locator("div")
                            else:
                                divs = page.locator("div")
                            
                            count = await divs.count()
                            print(f"Found {count} divs. Searching for relevant ones...")
                            
                            relevant_divs = []
                            for i in range(min(count, 50)):  # Check first 50
                                div = divs.nth(i)
                                text = await div.text_content()
                                if text and ("flight" in text.lower() or "reservation" in text.lower() or "ddl" in text.lower()):
                                    classes = await div.get_attribute("class")
                                    relevant_divs.append((i, text[:100], classes))
                            
                            print(f"Found {len(relevant_divs)} relevant divs:")
                            for i, text, classes in relevant_divs:
                                print(f"  {i}: classes='{classes}' text='{text}...'")
                                
                        except Exception as e:
                            print(f"✗ Search failed: {e}")
                            
                    else:
                        print("Unknown command. Try: iframe, buttons, inputs, divs, click <selector>, text <text>, quit")
                        
                except Exception as e:
                    print(f"Error: {e}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            print("\nClosing browser...")
            await browser.close()


async def test_element_detection():
    """Test specific element detection for Code Tantra"""
    print("="*60)
    print("TESTING ELEMENT DETECTION")
    print("="*60)
    
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("Please navigate to the Code Tantra page manually...")
            input("Press ENTER when ready...")
            
            print("\nPress ENTER to close browser...")
            input()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()


def main():
    """Main entry point"""
    print("Choose an option:")
    print("1. Interactive Code Generator")
    print("2. Test Element Detection")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(codegen_helper())
    elif choice == "2":
        asyncio.run(test_element_detection())
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
