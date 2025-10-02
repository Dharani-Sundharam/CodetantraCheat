"""
Code Question Handler Module
Handles different types of code completion questions with smart strategies
"""

import asyncio
from comment_remover import CommentRemover


class CodeQuestionHandler:
    def __init__(self, page_answers, page_target, comment_remover=None):
        self.page_answers = page_answers
        self.page_target = page_target
        self.comment_remover = comment_remover or CommentRemover()
    
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
            await page.evaluate(f"document.documentElement.style.zoom = '{zoom_level}'")
            
            print(f"  ✓ Window maximized and zoomed to {zoom_level*100}%")
            
        except Exception as e:
            print(f"  ⚠ Could not maximize/zoom window: {e}")
    
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
    
    async def detect_code_completion_type(self):
        """Detect if code completion is Type 1 (fully editable) or Type 2 (has static lines)"""
        try:
            print("🔍 Detecting code completion type using RESET method...")
            
            iframe_target = self.page_target.frame_locator("#course-iframe")
            
            # Step 1: Find and click RESET button
            print("  Looking for RESET button in target account...")
            reset_button = iframe_target.get_by_role("button", name="RESET")
            
            try:
                await reset_button.wait_for(state="visible", timeout=5000)
                print("  ✓ RESET button found")
            except Exception as e:
                print(f"  ⚠ RESET button not found - assuming Type 1")
                return {"type": "type1", "static_lines": []}
            
            # Step 2: Click RESET
            print("  Clicking RESET button...")
            await reset_button.click()
            await self.page_target.wait_for_timeout(2000)
            
            # Step 3: Try to clear all code
            print("  Attempting to clear all code...")
            editor = iframe_target.locator("div.cm-content[contenteditable='true']")
            await editor.click()
            await self.page_target.wait_for_timeout(500)
            
            # Select all and delete
            await editor.press("Control+a")
            await self.page_target.wait_for_timeout(300)
            await editor.press("Delete")
            await self.page_target.wait_for_timeout(1000)
            
            # Step 4: Check remaining content (static lines)
            print("  Checking for static lines...")
            lines = iframe_target.locator("div.cm-line")
            line_count = await lines.count()
            
            static_lines = []
            for i in range(line_count):
                try:
                    line = lines.nth(i)
                    line_text = await line.text_content()
                    if line_text and line_text.strip():
                        static_lines.append({
                            'line_number': i,
                            'text': line_text,
                            'stripped': line_text.strip()
                        })
                except:
                    continue
            
            # Step 5: Determine type
            if len(static_lines) == 0:
                print("  ✓ TYPE 1: Fully editable (no static lines)")
                return {"type": "type1", "static_lines": []}
            else:
                print(f"  ✓ TYPE 2: Has {len(static_lines)} static lines")
                for sl in static_lines:
                    print(f"    Static line {sl['line_number']}: {repr(sl['stripped'])}")
                return {"type": "type2", "static_lines": static_lines}
            
        except Exception as e:
            print(f"⚠ Error detecting code type: {e}")
            return {"type": "type1", "static_lines": []}
    
    async def extract_all_lines_from_answers(self):
        """Extract all lines from answers account with structure"""
        try:
            print("Extracting structured lines from answers account...")
            
            # First, maximize and zoom the answers page for better code visibility
            await self.maximize_and_zoom_browser(self.page_answers, zoom_level=0.5)
            
            iframe = self.page_answers.frame_locator("#course-iframe")
            editor = iframe.locator("div.cm-content[contenteditable='true']")
            await editor.wait_for(state="visible", timeout=10000)
            await editor.scroll_into_view_if_needed()
            
            # Scroll to top to ensure we get all lines
            await self.page_answers.evaluate("window.scrollTo(0, 0)")
            await self.page_answers.wait_for_timeout(500)
            
            # Scroll through the entire editor to ensure all lines are loaded
            await self.scroll_through_editor_iframe(iframe)
            
            lines = iframe.locator("div.cm-line")
            line_count = await lines.count()
            
            if line_count == 0:
                print("⚠ No code lines found in answers editor")
                return None
            
            structured_lines = []
            for i in range(line_count):
                try:
                    line = lines.nth(i)
                    line_text = await line.text_content()
                    if line_text is None:
                        line_text = ""
                    
                    structured_lines.append({
                        'line_number': i,
                        'text': line_text,
                        'stripped': line_text.strip()
                    })
                except Exception as line_error:
                    print(f"⚠ Error extracting line {i}: {line_error}")
                    structured_lines.append({
                        'line_number': i,
                        'text': "",
                        'stripped': ""
                    })
            
            print(f"✓ Extracted {len(structured_lines)} structured lines from answers")
            return structured_lines
            
        except Exception as e:
            print(f"⚠ Could not extract structured lines: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
    
    def detect_multiline_comment_strategy(self, answers_lines, static_lines):
        """Detect if static lines are commented with /* ... */ in answers"""
        try:
            print("🔍 Detecting comment strategy...")
            
            # Build full code from answers
            full_code = "\n".join(line['text'] for line in answers_lines)
            
            # Check for multiline comments
            has_multiline_start = '/*' in full_code
            has_multiline_end = '*/' in full_code
            
            if not (has_multiline_start and has_multiline_end):
                print("  ✓ No multiline comments detected - using Strategy A")
                return "strategy_a"
            
            # Check if static lines are inside comments
            in_comment = False
            static_texts = [sl['stripped'] for sl in static_lines]
            commented_static_count = 0
            
            for line in answers_lines:
                text = line['stripped']
                
                if '/*' in text:
                    in_comment = True
                    continue
                
                if '*/' in text:
                    in_comment = False
                    continue
                
                # Check if this line matches a static line and is in a comment
                if in_comment:
                    for static_text in static_texts:
                        if static_text in text or text in static_text:
                            commented_static_count += 1
                            break
            
            # If most static lines are commented, use Strategy B
            if commented_static_count >= len(static_lines) * 0.7:  # 70% threshold
                print(f"  ✓ {commented_static_count}/{len(static_lines)} static lines are commented - using Strategy B")
                return "strategy_b"
            else:
                print(f"  ✓ Only {commented_static_count}/{len(static_lines)} static lines are commented - using Strategy A")
                return "strategy_a"
            
        except Exception as e:
            print(f"⚠ Error detecting strategy: {e}")
            return "strategy_a"
    
    def compare_and_find_extra_code(self, answers_lines, static_lines):
        """Compare answers and static lines to find extra code"""
        try:
            print("📊 Comparing lines to find extra code...")
            
            static_texts = [sl['stripped'] for sl in static_lines]
            extra_code = []
            
            for ans_line in answers_lines:
                text = ans_line['stripped']
                
                # Skip empty lines
                if not text:
                    continue
                
                # Skip comment markers
                if text in ['/*', '*/'] or text.startswith('/*') or text.endswith('*/'):
                    continue
                
                # Check if this line matches any static line
                is_static = False
                for static_text in static_texts:
                    if static_text == text or static_text in text or text in static_text:
                        is_static = True
                        break
                
                # If not static, it's extra code
                if not is_static:
                    extra_code.append(ans_line)
                    print(f"  Extra code line {ans_line['line_number']}: {repr(text)}")
            
            print(f"✓ Found {len(extra_code)} extra code lines")
            return extra_code
            
        except Exception as e:
            print(f"⚠ Error comparing lines: {e}")
            return []
    
    async def type_code_safely(self, editor, text, delay=10):
        """Type code safely with basic auto-close handling"""
        try:
            # Simple approach: type character by character with error handling
            for i, char in enumerate(text):
                try:
                    await editor.type(char, delay=delay)
                    
                    # Handle basic auto-close for empty pairs
                    if i + 1 < len(text):
                        next_char = text[i + 1]
                        if ((char == '{' and next_char == '}') or 
                            (char == '(' and next_char == ')') or 
                            (char == '[' and next_char == ']') or
                            (char == '"' and next_char == '"') or
                            (char == "'" and next_char == "'")):
                            # Skip the next character since it will be auto-inserted
                            continue
                            
                except Exception as e:
                    print(f"    ⚠ Error typing character '{char}' at position {i}: {e}")
                    # Continue with next character
                    continue
                    
        except Exception as e:
            print(f"  ⚠ Error in type_code_safely: {e}")
            raise
    
    async def paste_code_to_target(self, code):
        """Paste code into the target account editor with enhanced reliability"""
        try:
            print("Pasting code to target account...")
            
            if not code or not code.strip():
                print("⚠ No code to paste")
                return False
            
            # Detect language and clean the code using comment remover
            detected_lang = self.detect_code_language(code)
            print(f"  Detected language: {detected_lang}")
            print("  Cleaning code using comment remover...")
            try:
                cleaned_code = self.comment_remover.remove_comments(code, detected_lang)
                print(f"  ✓ Code cleaned - removed comments")
                code = cleaned_code
            except Exception as e:
                print(f"  ⚠ Comment removal failed: {e}, using original code")
            
            # First, maximize and zoom the target page for better code visibility
            await self.maximize_and_zoom_browser(self.page_target, zoom_level=0.6)
            
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
            
            # Method 2: Line-by-line typing with better error handling
            print("  Pasting line by line with improved error handling...")
            lines = code.split('\n')
            print(f"  Total lines to type: {len(lines)}")
            
            for i, line in enumerate(lines):
                if line.strip():
                    print(f"  Typing line {i+1}/{len(lines)}: {line[:50]}{'...' if len(line) > 50 else ''}")
                    try:
                        # Use the safer typing method
                        await self.type_code_safely(editor, line, delay=20)
                        print(f"  ✓ Line {i+1} typed successfully")
                    except Exception as e:
                        print(f"  ⚠ Error typing line {i+1}: {e}")
                        # Try simple typing as fallback
                        try:
                            print(f"  Retrying line {i+1} with simple typing...")
                            await editor.type(line, delay=30)
                            print(f"  ✓ Line {i+1} typed with fallback method")
                        except Exception as e2:
                            print(f"  ✗ Failed to type line {i+1}: {e2}")
                            continue
                else:
                    print(f"  Skipping empty line {i+1}")
                
                # Add newline if not the last line
                if i < len(lines) - 1:
                    await editor.press("Enter")
                
                # Small delay between lines for stability
                await self.page_target.wait_for_timeout(100)
            
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
    
    def extract_uncommented_code_from_answers(self, answers_lines):
        """Extract only the uncommented code from answers (skip /* */ blocks)"""
        result_lines = []
        in_multiline_comment = False
        
        for line in answers_lines:
            text = line['text']
            stripped = line['stripped']
            
            # Check for multiline comment start
            if '/*' in stripped:
                in_multiline_comment = True
                continue
            
            # Check for multiline comment end
            if '*/' in stripped:
                in_multiline_comment = False
                continue
            
            # Skip lines inside multiline comments
            if in_multiline_comment:
                continue
            
            # Skip single-line comments (optional)
            if stripped.startswith('//'):
                continue
            
            # Add non-commented lines
            if stripped:  # Only add non-empty lines
                result_lines.append(line)
        
        return result_lines
    
    async def paste_code_strategy_b(self, answers_lines, static_lines):
        """Strategy B: Comment static lines, then paste complete code with Ctrl+V"""
        try:
            print("📝 Using Strategy B: Comment static lines then paste complete code...")
            
            # First, maximize and zoom the target page for better code visibility
            await self.maximize_and_zoom_browser(self.page_target, zoom_level=0.6)
            
            iframe_target = self.page_target.frame_locator("#course-iframe")
            editor = iframe_target.locator("div.cm-content[contenteditable='true']")
            
            # Step 1: Focus the editor and select all content
            print("  Focusing editor and selecting all content...")
            await editor.click()
            await self.page_target.wait_for_timeout(500)
            
            # Select all existing content (static lines)
            await editor.press("Control+a")
            await self.page_target.wait_for_timeout(500)
            print("  ✓ Selected all static lines")
            
            # Step 2: Comment everything using Ctrl+/
            print("  Commenting all lines with Ctrl+/...")
            await editor.press("Control+/")
            await self.page_target.wait_for_timeout(800)
            print("  ✓ All lines commented with //")
            
            # Step 3: Move to end and add 3 new lines
            print("  Moving to end and adding 3 new lines...")
            await editor.press("Control+End")
            await self.page_target.wait_for_timeout(200)
            
            # Press Enter 3 times to create space
            await editor.press("Enter")
            await self.page_target.wait_for_timeout(100)
            await editor.press("Enter")
            await self.page_target.wait_for_timeout(100)
            await editor.press("Enter")
            await self.page_target.wait_for_timeout(100)
            print("  ✓ Added 3 new lines for code placement")
            
            # Step 4: Build complete code from answers and clean it
            print("  Building complete code from answers...")
            complete_code = "\n".join(line['text'] for line in answers_lines)
            
            if not complete_code.strip():
                print("  ⚠ No code found in answers")
                return False
            
            # Step 5: Detect language and clean the code using comment remover
            detected_lang = self.detect_code_language(complete_code)
            print(f"  Detected language: {detected_lang}")
            print("  Cleaning code using comment remover...")
            try:
                cleaned_code = self.comment_remover.remove_comments(complete_code, detected_lang)
                print(f"  ✓ Code cleaned - removed comments")
            except Exception as e:
                print(f"  ⚠ Comment removal failed: {e}, using original code")
                cleaned_code = complete_code
            
            print(f"  Ready to type {len(cleaned_code.split(chr(10)))} lines of clean code")
            
            # Step 6: Type cleaned code with better error handling
            print("  Typing cleaned code...")
            print(f"  Total lines to type: {len(cleaned_code.split(chr(10)))}")
            lines = cleaned_code.split('\n')
            
            for i, line in enumerate(lines):
                if line.strip():
                    print(f"  Typing line {i+1}/{len(lines)}: {line[:50]}{'...' if len(line) > 50 else ''}")
                    try:
                        # Type with moderate speed for reliability
                        await self.type_code_safely(editor, line, delay=10)
                        print(f"  ✓ Line {i+1} typed successfully")
                    except Exception as e:
                        print(f"  ⚠ Error typing line {i+1}: {e}")
                        # Try simple typing as fallback
                        try:
                            print(f"  Retrying line {i+1} with simple typing...")
                            await editor.type(line, delay=20)
                            print(f"  ✓ Line {i+1} typed with fallback method")
                        except Exception as e2:
                            print(f"  ✗ Failed to type line {i+1}: {e2}")
                            continue
                else:
                    print(f"  Skipping empty line {i+1}")
                
                if i < len(lines) - 1:
                    await editor.press("Enter")
                    await self.page_target.wait_for_timeout(50)  # Slightly slower for reliability
            print("  ✓ All code typed successfully")
            
            # Verify what was actually typed
            try:
                actual_content = await editor.text_content()
                print(f"  Verification: {len(actual_content)} characters typed")
                if len(actual_content) < len(cleaned_code) * 0.8:  # If less than 80% of expected
                    print(f"  ⚠ Warning: Only {len(actual_content)} chars typed, expected ~{len(cleaned_code)}")
                    print(f"  First 100 chars: {actual_content[:100]}")
                else:
                    print(f"  ✓ Verification passed: {len(actual_content)} characters")
            except Exception as e:
                print(f"  ⚠ Could not verify typed content: {e}")
            
            print("✓ Strategy B: Code typed successfully")
            return True
            
        except Exception as e:
            print(f"✗ Strategy B failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def handle_type2_code_completion(self):
        """Handle Type 2 code completion with smart strategies"""
        try:
            print("\n🎯 TYPE 2 CODE COMPLETION DETECTED")
            print("="*60)
            
            # Step 1: Detect type and get static lines
            type_info = await self.detect_code_completion_type()
            
            if type_info['type'] == 'type1':
                print("⚠ False alarm - This is actually Type 1")
                # Fall back to Type 1 handling
                code = await self.get_code_from_answers()
                if code:
                    return await self.paste_code_to_target(code)
                return False
            
            static_lines = type_info['static_lines']
            
            # Step 2: Extract structured lines from answers
            answers_lines = await self.extract_all_lines_from_answers()
            if not answers_lines:
                print("✗ Failed to extract lines from answers")
                return False
            
            # Step 3: Use Strategy B - Comment static lines then paste complete code
            print("📝 Using Strategy B: Comment static lines + paste complete code")
            success = await self.paste_code_strategy_b(answers_lines, static_lines)
            
            if success:
                print("✓ Type 2 code pasted successfully!")
            else:
                print("✗ Type 2 code paste failed")
            
            return success
            
        except Exception as e:
            print(f"✗ Type 2 handling failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def handle_code_completion_question(self):
        """Main handler for code completion questions"""
        try:
            print("✓ Code completion question detected")
            
            # Detect if Type 1 or Type 2
            type_info = await self.detect_code_completion_type()
            
            if type_info['type'] == 'type2':
                # Handle Type 2 with smart strategies
                return await self.handle_type2_code_completion()
            else:
                # Handle Type 1 (simple copy-paste)
                print("✓ TYPE 1: Simple copy-paste")
                code = await self.get_code_from_answers()
                if not code:
                    print("⚠ No code found in answers account")
                    return False
                
                paste_success = await self.paste_code_to_target(code)
                if paste_success:
                    print("✓ Code copied and pasted successfully!")
                    return True
                else:
                    print("⚠ Failed to paste code to target account")
                    return False
                    
        except Exception as e:
            print(f"⚠ Error handling code completion: {e}")
            import traceback
            traceback.print_exc()
            return False
