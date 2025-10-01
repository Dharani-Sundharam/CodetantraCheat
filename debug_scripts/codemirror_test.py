"""
CodeMirror Test Script - SMART COPY/PASTE
Tests copying content from CodeMirror editor with support for:
1. Fully editable code (Type 1)
2. Template with read-only sections (Type 2 - red overlay)
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

class CodeMirrorTester:
    def __init__(self, auto_login=False):
        self.browser = None
        self.page = None
        self.auto_login = auto_login
        
    async def setup_browser(self):
        """Setup browser and navigate to CodeTantra"""
        print("Setting up browser...")
        
        playwright = await async_playwright().start()
        self.browser = await playwright.firefox.launch(headless=False)
        context = await self.browser.new_context()
        self.page = await context.new_page()
        
        print("✓ Browser opened")
        return playwright
        
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
    
    async def wait_for_navigation(self):
        """Wait for manual navigation to problem"""
        print("\n" + "="*60)
        print("Navigate to a CODE COMPLETION problem")
        print("(One with CodeMirror editor)")
        print("Press ENTER when ready to test...")
        print("="*60)
        input()
        
    async def detect_code_type_using_reset(self, iframe):
        """Detect Type 1 vs Type 2 using RESET button method"""
        try:
            print("🔍 Detecting code type using RESET button method...")
            
            # Step 1: Find and click RESET button
            print("  Looking for RESET button...")
            reset_button = iframe.get_by_role("button", name="RESET")
            
            try:
                await reset_button.wait_for(state="visible", timeout=5000)
                print("  ✓ RESET button found")
            except Exception as e:
                print(f"  ⚠ RESET button not found: {e}")
                print("  Falling back to visual detection...")
                return await self.detect_readonly_lines_visual(iframe)
            
            # Step 2: Click RESET to clear the code
            print("  Clicking RESET button...")
            await reset_button.click()
            await self.page.wait_for_timeout(2000)  # Wait for reset to complete
            
            # Step 3: Try to clear all code in CodeMirror editor
            print("  Attempting to clear all code...")
            editor = iframe.locator("div.cm-content[contenteditable='true']")
            await editor.click()
            await self.page.wait_for_timeout(500)
            
            # Select all and delete
            await editor.press("Control+a")
            await self.page.wait_for_timeout(300)
            await editor.press("Delete")
            await self.page.wait_for_timeout(1000)
            
            # Step 4: Check if editor is completely empty
            print("  Checking if editor is completely clearable...")
            lines = iframe.locator("div.cm-line")
            line_count = await lines.count()
            
            # Get all line content
            remaining_content = []
            for i in range(line_count):
                try:
                    line = lines.nth(i)
                    line_text = await line.text_content()
                    if line_text and line_text.strip():
                        remaining_content.append(line_text.strip())
                except:
                    continue
            
            # Step 5: Determine type based on clearability
            if len(remaining_content) == 0 or (len(remaining_content) == 1 and remaining_content[0] == ""):
                print("  ✓ Editor completely clearable - TYPE 1 DETECTED")
                return {
                    'type': 'type1',
                    'method': 'reset_test',
                    'clearable': True,
                    'remaining_lines': 0
                }
            else:
                print(f"  ⚠ Editor not fully clearable - TYPE 2 DETECTED")
                print(f"  Remaining content: {remaining_content}")
                return {
                    'type': 'type2',
                    'method': 'reset_test',
                    'clearable': False,
                    'remaining_lines': len(remaining_content),
                    'remaining_content': remaining_content
                }
            
        except Exception as e:
            print(f"⚠ Error in RESET button detection: {e}")
            print("  Falling back to visual detection...")
            return await self.detect_readonly_lines_visual(iframe)
    
    async def detect_readonly_lines_visual(self, iframe):
        """Fallback: Detect read-only lines using visual analysis"""
        try:
            print("  Using visual detection as fallback...")
            # Check for read-only lines using multiple methods
            readonly_info = await self.page.evaluate("""
                () => {
                    const iframe = document.getElementById('course-iframe');
                    if (!iframe) return null;
                    
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                    const lines = iframeDoc.querySelectorAll('div.cm-line');
                    
                    let readonlyLines = [];
                    let hasReadonly = false;
                    
                    lines.forEach((line, index) => {
                        // Check for red overlay, disabled class, or non-editable markers
                        const hasRedOverlay = line.querySelector('[style*="color: red"], [style*="color:red"], [style*="opacity"], .cm-nonEditableLineOverlay');
                        const computedStyle = window.getComputedStyle(line);
                        const opacity = parseFloat(computedStyle.opacity);
                        const color = computedStyle.color;
                        
                        // Check if line has reduced opacity (common for read-only)
                        const isReadonly = hasRedOverlay || opacity < 0.6 || color.includes('rgba');
                        
                        if (isReadonly) {
                            hasReadonly = true;
                        }
                        
                        readonlyLines.push({
                            index: index,
                            readonly: isReadonly,
                            opacity: opacity,
                            color: color
                        });
                    });
                    
                    return {
                        hasReadonly: hasReadonly,
                        lines: readonlyLines
                    };
                }
            """)
            
            if readonly_info and readonly_info['hasReadonly']:
                return {
                    'type': 'type2',
                    'method': 'visual_detection',
                    'clearable': False,
                    'readonly_info': readonly_info
                }
            else:
                return {
                    'type': 'type1',
                    'method': 'visual_detection',
                    'clearable': True,
                    'readonly_info': readonly_info
                }
            
        except Exception as e:
            print(f"⚠ Error in visual detection: {e}")
            return {
                'type': 'type1',
                'method': 'fallback',
                'clearable': True,
                'error': str(e)
            }
    
    async def test_codemirror_extraction(self):
        """Test extracting content from CodeMirror editor with SMART detection using RESET button"""
        try:
            print("\n🔍 Testing CodeMirror extraction...")
            
            # Switch to iframe first
            iframe = self.page.frame_locator("#course-iframe")
            
            # Find the CodeMirror editor content
            editor = iframe.locator("div.cm-content[contenteditable='true']")
            
            # Wait for editor to be visible
            try:
                await editor.wait_for(state="visible", timeout=10000)
                print("✓ CodeMirror editor found")
            except Exception as e:
                print(f"⚠ CodeMirror editor not found: {e}")
                print("Make sure you're on a code completion problem")
                return None
            
            # Scroll to editor
            await editor.scroll_into_view_if_needed()
            print("✓ Scrolled to editor")
            
            # STEP 1: Detect type using RESET button method
            print("\n📊 Detecting code type using RESET button method...")
            type_info = await self.detect_code_type_using_reset(iframe)
            
            if type_info['type'] == 'type2':
                print(f"🎯 TYPE 2 DETECTED: Template with read-only sections")
                print(f"   Method: {type_info['method']}")
                print(f"   Clearable: {type_info['clearable']}")
                if 'remaining_content' in type_info:
                    print(f"   Remaining after clear: {type_info['remaining_content']}")
                return await self.extract_type2_code(iframe, type_info)
            else:
                print(f"🎯 TYPE 1 DETECTED: Fully editable code")
                print(f"   Method: {type_info['method']}")
                print(f"   Clearable: {type_info['clearable']}")
                return await self.extract_type1_code(iframe)
            
        except Exception as e:
            print(f"✗ Error extracting from CodeMirror: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def extract_type1_code(self, iframe):
        """Extract Type 1: Fully editable code (simple extraction)"""
        try:
            print("📝 Extracting fully editable code...")
            
            # Get all lines
            lines = iframe.locator("div.cm-line")
            line_count = await lines.count()
            
            if line_count == 0:
                print("⚠ No code lines found in editor")
                return None
                
            print(f"✓ Found {line_count} lines in editor")
            
            # Extract code line by line
            code_text = []
            for i in range(line_count):
                try:
                    line = lines.nth(i)
                    line_text = await line.text_content()
                    if line_text is None:
                        line_text = ""
                    code_text.append(line_text)
                    print(f"  Line {i+1}: {repr(line_text)}")
                except Exception as line_error:
                    print(f"⚠ Error extracting line {i+1}: {line_error}")
                    code_text.append("")
            
            # Join lines and clean up
            full_code = "\n".join(code_text)
            cleaned_code = "\n".join(line.rstrip() for line in full_code.split('\n'))
            
            print(f"\n✓ Type 1 extraction successful!")
            print(f"✓ Total lines: {len(code_text)}")
            print(f"✓ Code preview:")
            print("-" * 50)
            print(cleaned_code)
            print("-" * 50)
            
            return {
                'type': 'type1',
                'code': cleaned_code,
                'lines': code_text,
                'method': 'full_replacement'
            }
            
        except Exception as e:
            print(f"✗ Error in Type 1 extraction: {e}")
            return None
    
    async def extract_type2_code(self, iframe, type_info):
        """Extract Type 2: Template with read-only sections (smart extraction)"""
        try:
            print("📝 Extracting code from template with read-only sections...")
            
            # Get all lines
            lines = iframe.locator("div.cm-line")
            line_count = await lines.count()
            
            if line_count == 0:
                print("⚠ No code lines found in editor")
                return None
            
            print(f"✓ Found {line_count} lines in editor")
            
            # If we have remaining content from RESET test, use that info
            if 'remaining_content' in type_info and type_info['remaining_content']:
                print(f"✓ Using RESET test results - {len(type_info['remaining_content'])} read-only lines detected")
                remaining_content = type_info['remaining_content']
                
                # Extract all lines and classify them
                all_lines = []
                editable_lines = []
                readonly_lines = []
                
                for i in range(line_count):
                    try:
                        line = lines.nth(i)
                        line_text = await line.text_content()
                        if line_text is None:
                            line_text = ""
                        
                        # Check if this line is in the remaining content (read-only)
                        is_readonly = any(remaining.strip() in line_text.strip() for remaining in remaining_content)
                        
                        line_info = {
                            'index': i,
                            'text': line_text,
                            'readonly': is_readonly
                        }
                        
                        all_lines.append(line_info)
                        
                        if is_readonly:
                            readonly_lines.append(line_info)
                            print(f"  Line {i+1} [READ-ONLY]: {repr(line_text)}")
                        else:
                            editable_lines.append(line_info)
                            print(f"  Line {i+1} [EDITABLE]: {repr(line_text)}")
                            
                    except Exception as line_error:
                        print(f"⚠ Error extracting line {i+1}: {line_error}")
                
                # Extract only editable lines
                extracted_code = "\n".join(l['text'] for l in editable_lines)
                
            else:
                # Fallback to visual detection if RESET method didn't provide enough info
                print("  Using visual detection fallback...")
                if 'readonly_info' in type_info and type_info['readonly_info']:
                    readonly_info = type_info['readonly_info']
                    print(f"✓ Read-only lines: {sum(1 for l in readonly_info['lines'] if l['readonly'])}")
                    
                    # Extract all lines with metadata
                    all_lines = []
                    editable_lines = []
                    readonly_lines = []
                    
                    for i in range(line_count):
                        try:
                            line = lines.nth(i)
                            line_text = await line.text_content()
                            if line_text is None:
                                line_text = ""
                            
                            is_readonly = readonly_info['lines'][i]['readonly'] if i < len(readonly_info['lines']) else False
                            
                            line_info = {
                                'index': i,
                                'text': line_text,
                                'readonly': is_readonly
                            }
                            
                            all_lines.append(line_info)
                            
                            if is_readonly:
                                readonly_lines.append(line_info)
                                print(f"  Line {i+1} [READ-ONLY]: {repr(line_text)}")
                            else:
                                editable_lines.append(line_info)
                                print(f"  Line {i+1} [EDITABLE]: {repr(line_text)}")
                                
                        except Exception as line_error:
                            print(f"⚠ Error extracting line {i+1}: {line_error}")
                    
                    # Check for multiline comments (/* ... */)
                    full_code = "\n".join(l['text'] for l in all_lines)
                    is_commented = self.detect_multiline_comments(full_code, all_lines)
                    
                    if is_commented:
                        print("\n🔍 DETECTED: Read-only sections are commented with /* ... */")
                        print("   Strategy: Extract only NON-commented editable code")
                        extracted_code = self.extract_uncommented_code(full_code, editable_lines)
                    else:
                        print("\n🔍 DETECTED: Read-only sections are NOT commented")
                        print("   Strategy: Extract ONLY editable sections")
                        extracted_code = "\n".join(l['text'] for l in editable_lines)
                else:
                    # Last resort: extract all lines
                    print("  ⚠ No specific detection info available, extracting all lines")
                    all_lines = []
                    for i in range(line_count):
                        try:
                            line = lines.nth(i)
                            line_text = await line.text_content()
                            if line_text is None:
                                line_text = ""
                            all_lines.append({'index': i, 'text': line_text, 'readonly': False})
                        except:
                            continue
                    extracted_code = "\n".join(l['text'] for l in all_lines)
                    editable_lines = all_lines
                    readonly_lines = []
            
            print(f"\n✓ Type 2 extraction successful!")
            print(f"✓ Total lines: {len(all_lines) if 'all_lines' in locals() else line_count}")
            print(f"✓ Editable lines: {len(editable_lines) if 'editable_lines' in locals() else 'unknown'}")
            print(f"✓ Read-only lines: {len(readonly_lines) if 'readonly_lines' in locals() else 'unknown'}")
            print(f"✓ Extracted code preview:")
            print("-" * 50)
            print(extracted_code)
            print("-" * 50)
            
            return {
                'type': 'type2',
                'code': extracted_code,
                'all_lines': all_lines if 'all_lines' in locals() else [],
                'editable_lines': editable_lines if 'editable_lines' in locals() else [],
                'readonly_lines': readonly_lines if 'readonly_lines' in locals() else [],
                'is_commented': is_commented if 'is_commented' in locals() else False,
                'method': 'selective_extraction',
                'detection_method': type_info['method']
            }
            
        except Exception as e:
            print(f"✗ Error in Type 2 extraction: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def detect_multiline_comments(self, code, all_lines):
        """Detect if code has multiline comments /* ... */"""
        # Check for multiline comment markers
        has_comment_start = '/*' in code
        has_comment_end = '*/' in code
        return has_comment_start and has_comment_end
    
    def extract_uncommented_code(self, full_code, editable_lines):
        """Extract only uncommented code from editable sections"""
        lines = []
        in_comment = False
        
        for line_info in editable_lines:
            text = line_info['text'].strip()
            
            # Check for comment start
            if '/*' in text:
                in_comment = True
                continue
            
            # Check for comment end
            if '*/' in text:
                in_comment = False
                continue
            
            # Skip lines inside comments
            if in_comment:
                continue
            
            # Add non-commented lines
            if text and not text.startswith('//'):
                lines.append(line_info['text'])
        
        return "\n".join(lines)
    
    async def copy_to_clipboard(self, result):
        """Copy extracted code to clipboard"""
        try:
            if not result or 'code' not in result:
                print("⚠ No code to copy")
                return False
                
            code = result['code']
            print("\n📋 Copying to clipboard...")
            print(f"📌 Method: {result['method']}")
            print(f"📌 Type: {result['type']}")
            
            pyperclip.copy(code)
            print("✓ Code copied to clipboard!")
            print("✓ You can now paste (Ctrl+V) in any application")
            return True
        except Exception as e:
            print(f"✗ Error copying to clipboard: {e}")
            return False
    
    async def test_paste_verification(self):
        """Test pasting and verify content"""
        try:
            print("\n🔍 Testing clipboard content...")
            clipboard_content = pyperclip.paste()
            
            if clipboard_content:
                print("✓ Clipboard content found:")
                print("-" * 50)
                print(clipboard_content)
                print("-" * 50)
                return True
            else:
                print("⚠ Clipboard is empty")
                return False
                
        except Exception as e:
            print(f"✗ Error reading clipboard: {e}")
            return False
    
    async def cleanup(self):
        """Keep browser open for manual use"""
        print("✓ Browser will remain open for manual use")
        print("✓ You can continue using the browser manually")
        # Don't close the browser - keep it open

async def main():
    """Main test function with SMART copy/paste using RESET button detection"""
    print("=" * 60)
    print("SMART CODEMIRROR EXTRACTION TEST")
    print("=" * 60)
    print("This script tests SMART copying from CodeMirror editor")
    print("Detection Method: RESET button test")
    print("Supports:")
    print("  • Type 1: Fully editable code (clears completely)")
    print("  • Type 2: Templates with read-only sections (can't clear all)")
    print("=" * 60)
    
    tester = CodeMirrorTester(auto_login=AUTO_LOGIN)
    playwright = None
    
    try:
        # Setup
        playwright = await tester.setup_browser()
        
        # Login
        if AUTO_LOGIN:
            print(f"\n🔐 Using automatic login from credentials.py")
            await tester.navigate_to_codetantra(LOGIN_URL)
            await asyncio.sleep(2)
            
            if await tester.login_to_account(
                ANSWERS_ACCOUNT['username'],
                ANSWERS_ACCOUNT['password']
            ):
                print("✓ Logged in successfully!")
                await tester.wait_for_navigation()
            else:
                print("⚠ Login failed. Please login manually.")
                await tester.wait_for_navigation()
        else:
            print("\nEnter CodeTantra URL (or press ENTER for manual navigation):")
            url = input().strip()
            if url:
                await tester.navigate_to_codetantra(url)
            else:
                print("Please navigate to CodeTantra manually")
            
            await tester.wait_for_navigation()
        
        # Test extraction (SMART detection)
        result = await tester.test_codemirror_extraction()
        
        if result:
            # Copy to clipboard
            if await tester.copy_to_clipboard(result):
                print("\n✅ SUCCESS! Code extracted and copied to clipboard")
                
                # Test verification
                await tester.test_paste_verification()
                
                # Show summary
                print("\n" + "="*60)
                print("TEST COMPLETE - SUMMARY")
                print("="*60)
                print(f"Detection Type: {result['type'].upper()}")
                print(f"Extraction Method: {result['method']}")
                if result['type'] == 'type2':
                    print(f"Total Lines: {len(result['all_lines'])}")
                    print(f"Editable Lines: {len(result['editable_lines'])}")
                    print(f"Read-only Lines: {len(result['readonly_lines'])}")
                    print(f"Has Comments: {'Yes' if result['is_commented'] else 'No'}")
                else:
                    print(f"Total Lines: {len(result['lines'])}")
                print("="*60)
                print("The extracted code is now in your clipboard.")
                print("Try pasting it (Ctrl+V) in any text editor to verify!")
            else:
                print("\n❌ FAILED to copy to clipboard")
        else:
            print("\n❌ FAILED to extract code from CodeMirror")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\nTest completed!")
        await tester.cleanup()
        print("\n" + "="*60)
        print("BROWSER KEPT OPEN")
        print("="*60)
        print("The browser will remain open for you to:")
        print("• Test different problems")
        print("• Verify the extraction results")
        print("• Continue manual testing")
        print("• Close manually when done")
        print("="*60)
        # Don't stop playwright - keep browser open

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
