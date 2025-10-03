"""
Code Question Handler Module
Handles different types of code completion questions with smart strategies
"""

import asyncio
import pyperclip
from comment_remover import CommentRemover


class CodeQuestionHandler:
    def __init__(self, page_answers, page_target, comment_remover=None):
        self.page_answers = page_answers
        self.page_target = page_target
        self.comment_remover = comment_remover or CommentRemover()
    
    
    
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
            print("🔍 Detecting code completion type...")
            
            iframe_target = self.page_target.frame_locator("#course-iframe")
            
            # Step 1: Find and click RESET button
            reset_button = iframe_target.get_by_role("button", name="RESET")
            
            try:
                await reset_button.wait_for(state="visible", timeout=5000)
            except Exception:
                print("  ⚠ RESET button not found - assuming Type 1")
                return {"type": "type1", "static_lines": []}
            
            # Step 2: Click RESET
            await reset_button.click()
            await self.page_target.wait_for_timeout(2000)
            
            # Step 3: Try to clear all code
            editor = iframe_target.locator("div.cm-content[contenteditable='true']")
            await editor.click()
            await self.page_target.wait_for_timeout(500)
            
            # Select all and delete
            await editor.press("Control+a")
            await self.page_target.wait_for_timeout(300)
            await editor.press("Delete")
            await self.page_target.wait_for_timeout(1000)
            
            # Step 4: Check remaining content (static lines)
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
                return {"type": "type2", "static_lines": static_lines}
            
        except Exception as e:
            print(f"⚠ Error detecting code type: {e}")
            return {"type": "type1", "static_lines": []}
    
    async def extract_all_lines_from_answers(self):
        """Extract all lines from answers account using Ctrl+A + Ctrl+C method"""
        try:
            print("📋 Extracting structured lines from answers account...")
            
            # First, maximize and zoom the answers page for better code visibility
            # Zoom functionality removed as requested
            
            iframe = self.page_answers.frame_locator("#course-iframe")
            editor = iframe.locator("div.cm-content[contenteditable='true']")
            await editor.wait_for(state="visible", timeout=10000)
            await editor.scroll_into_view_if_needed()
            
            # Use the same Ctrl+A + Ctrl+C method as get_code_from_answers
            success = False
            
            # Approach 1: Try JavaScript focus first
            try:
                await editor.evaluate("element => element.focus()")
                success = True
            except Exception:
                pass
            
            # Approach 2: If JavaScript failed, try clicking
            if not success:
                try:
                    await editor.click(timeout=5000)
                    success = True
                except Exception:
                    pass
            
            # Approach 3: If both failed, try clicking on the iframe first
            if not success:
                try:
                    iframe_element = self.page_answers.locator("#course-iframe")
                    await iframe_element.click()
                    await self.page_answers.wait_for_timeout(200)
                    await editor.click(timeout=3000)
                    success = True
                except Exception:
                    pass
            
            # Wait a moment for focus
            await self.page_answers.wait_for_timeout(300)
            
            # Try to select all text
            try:
                if success:
                    await editor.press("Control+a")
                else:
                    await self.page_answers.keyboard.press("Control+a")
            except Exception:
                await self.page_answers.keyboard.press("Control+a")
            
            # Wait a moment for selection
            await self.page_answers.wait_for_timeout(200)
            
            # Try to copy
            try:
                if success:
                    await editor.press("Control+c")
                else:
                    await self.page_answers.keyboard.press("Control+c")
            except Exception:
                await self.page_answers.keyboard.press("Control+c")
            
            # Wait a moment for clipboard operation
            await self.page_answers.wait_for_timeout(300)
            
            # Get the copied content from clipboard
            try:
                copied_content = pyperclip.paste()
                
                if copied_content and copied_content.strip():
                    # Convert to structured lines format
                    lines = copied_content.split('\n')
                    structured_lines = []
                    
                    for i, line_text in enumerate(lines):
                        structured_lines.append({
                            'line_number': i,
                            'text': line_text,
                            'stripped': line_text.strip()
                        })
                    
                    print(f"✓ Extracted {len(structured_lines)} structured lines")
                    return structured_lines
                else:
                    print("⚠ No content found in clipboard")
                    return None
                    
            except Exception as e:
                print(f"⚠ Error reading from clipboard: {e}")
                return None
            
        except Exception as e:
            print(f"⚠ Could not extract structured lines: {e}")
            return None
    
    async def get_code_from_answers(self):
        """Extract code from the answers account editor using Ctrl+A + Ctrl+C method"""
        try:
            print("📋 Extracting code from answers account...")
            
            # Switch to iframe first
            iframe = self.page_answers.frame_locator("#course-iframe")
            
            # Find the CodeMirror editor content
            editor = iframe.locator("div.cm-content[contenteditable='true']")
            await editor.wait_for(state="visible", timeout=10000)
            await editor.scroll_into_view_if_needed()
            
            # Try multiple approaches to focus and copy
            success = False
            
            # Approach 1: Try JavaScript focus first
            try:
                await editor.evaluate("element => element.focus()")
                success = True
            except Exception:
                pass
            
            # Approach 2: If JavaScript failed, try clicking
            if not success:
                try:
                    await editor.click(timeout=5000)
                    success = True
                except Exception:
                    pass
            
            # Approach 3: If both failed, try clicking on the iframe first
            if not success:
                try:
                    iframe_element = self.page_answers.locator("#course-iframe")
                    await iframe_element.click()
                    await self.page_answers.wait_for_timeout(200)
                    await editor.click(timeout=3000)
                    success = True
                except Exception:
                    pass
            
            # Wait a moment for focus
            await self.page_answers.wait_for_timeout(300)
            
            # Try to select all text
            try:
                if success:
                    await editor.press("Control+a")
                else:
                    await self.page_answers.keyboard.press("Control+a")
            except Exception:
                await self.page_answers.keyboard.press("Control+a")
            
            # Wait a moment for selection
            await self.page_answers.wait_for_timeout(200)
            
            # Try to copy
            try:
                if success:
                    await editor.press("Control+c")
                else:
                    await self.page_answers.keyboard.press("Control+c")
            except Exception:
                await self.page_answers.keyboard.press("Control+c")
            
            # Wait a moment for clipboard operation
            await self.page_answers.wait_for_timeout(300)
            
            # Get the copied content from clipboard
            try:
                copied_content = pyperclip.paste()
                
                if copied_content and copied_content.strip():
                    print(f"✓ Code extracted ({len(copied_content.split(chr(10)))} lines)")
                    return copied_content
                else:
                    print("⚠ No content found in clipboard")
                    return None
                    
            except Exception as e:
                print(f"⚠ Error reading from clipboard: {e}")
                return None
            
        except Exception as e:
            print(f"⚠ Could not extract code: {e}")
            return None
    
    def detect_multiline_comment_strategy(self, answers_lines, static_lines):
        """Detect if static lines are commented with /* ... */ in answers"""
        try:
            # Build full code from answers
            full_code = "\n".join(line['text'] for line in answers_lines)
            
            # Check for multiline comments
            has_multiline_start = '/*' in full_code
            has_multiline_end = '*/' in full_code
            
            if not (has_multiline_start and has_multiline_end):
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
                return "strategy_b"
            else:
                return "strategy_a"
            
        except Exception as e:
            return "strategy_a"
    
    def compare_and_find_extra_code(self, answers_lines, static_lines):
        """Compare answers and static lines to find extra code"""
        try:
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
            
            return extra_code
            
        except Exception as e:
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
            if not code or not code.strip():
                return False
            
            # Detect language and clean the code using comment remover
            detected_lang = self.detect_code_language(code)
            try:
                cleaned_code = self.comment_remover.remove_comments(code, detected_lang)
                code = cleaned_code
            except Exception as e:
                pass
            
            # First, maximize and zoom the target page for better code visibility
            # Zoom functionality removed as requested
            
            # Switch to iframe first
            iframe = self.page_target.frame_locator("#course-iframe")
            
            # Find the CodeMirror editor with better waiting
            editor = iframe.locator("div.cm-content[contenteditable='true']")
            await editor.wait_for(state="visible", timeout=10000)
            await editor.scroll_into_view_if_needed()
            
            # Click to focus the editor
            await editor.click()
            await self.page_target.wait_for_timeout(500)
            
            # Clear existing content more reliably
            await editor.press("Control+a")
            await self.page_target.wait_for_timeout(300)
            await editor.press("Delete")
            await self.page_target.wait_for_timeout(500)
            
            # Type code line-by-line (clipboard paste removed as requested)
            lines = code.split('\n')
            print(f"  Typing {len(lines)} lines...")
            
            for i, line in enumerate(lines):
                if line.strip():
                    try:
                        # Use the safer typing method
                        await self.type_code_safely(editor, line, delay=20)
                    except Exception:
                        # Try simple typing as fallback
                        try:
                            await editor.type(line, delay=30)
                        except Exception:
                            continue
                else:
                    pass
                
                # Add newline if not the last line
                if i < len(lines) - 1:
                    await editor.press("Enter")
                
                # Small delay between lines for stability
                await self.page_target.wait_for_timeout(100)
            
            # Typing is done - now delete trailing characters immediately
            # Press delete repeatedly for 12 seconds with 20ms intervals
            import time
            start_time = time.time()
            delete_duration = 12  # 12 seconds
            
            print("  Deleting trailing characters (12 seconds, 20ms intervals)...")
            while time.time() - start_time < delete_duration:
                await editor.press("Delete")
                await self.page_target.wait_for_timeout(20)  # 20ms interval
            print("  ✓ Deletion complete")
            
            # Verify the paste was successful
            await self.page_target.wait_for_timeout(1000)
            pasted_content = await editor.text_content()
            
            if pasted_content and len(pasted_content.strip()) > 0:
                print(f"✓ Code typed successfully ({len(lines)} lines)")
                return True
            else:
                print("⚠ Type verification failed - no content detected")
                return False
            
        except Exception as e:
            print(f"⚠ Error typing code: {e}")
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
            # Zoom functionality removed as requested
            
            iframe_target = self.page_target.frame_locator("#course-iframe")
            editor = iframe_target.locator("div.cm-content[contenteditable='true']")
            
            # Step 1: Focus the editor and select all content
            await editor.click()
            await self.page_target.wait_for_timeout(500)
            
            # Select all existing content (static lines)
            await editor.press("Control+a")
            await self.page_target.wait_for_timeout(500)
            
            # Step 2: Comment everything using Ctrl+/
            await editor.press("Control+/")
            await self.page_target.wait_for_timeout(800)
            
            # Step 3: Move to end and add 3 new lines
            await editor.press("Control+End")
            await self.page_target.wait_for_timeout(200)
            
            # Press Enter 3 times to create space
            await editor.press("Enter")
            await self.page_target.wait_for_timeout(100)
            await editor.press("Enter")
            await self.page_target.wait_for_timeout(100)
            await editor.press("Enter")
            await self.page_target.wait_for_timeout(100)
            
            # Step 4: Build complete code from answers and clean it
            complete_code = "\n".join(line['text'] for line in answers_lines)
            
            if not complete_code.strip():
                print("  ⚠ No code found in answers")
                return False
            
            # Step 5: Detect language and clean the code using comment remover
            detected_lang = self.detect_code_language(complete_code)
            print(f"  Language: {detected_lang} | Cleaning code...")
            try:
                cleaned_code = self.comment_remover.remove_comments(complete_code, detected_lang)
            except Exception as e:
                print(f"  ⚠ Comment removal failed: {e}")
                cleaned_code = complete_code
            
            # Step 6: Type cleaned code with better error handling
            lines = cleaned_code.split('\n')
            print(f"  Typing {len(lines)} lines...")
            
            for i, line in enumerate(lines):
                if line.strip():
                    try:
                        # Type with moderate speed for reliability
                        await self.type_code_safely(editor, line, delay=10)
                    except Exception:
                        # Try simple typing as fallback
                        try:
                            await editor.type(line, delay=20)
                        except Exception:
                            continue
                else:
                    pass
                
                if i < len(lines) - 1:
                    await editor.press("Enter")
                    await self.page_target.wait_for_timeout(50)  # Slightly slower for reliability
            
            
            # Verify what was actually typed
            try:
                actual_content = await editor.text_content()
                if len(actual_content) < len(cleaned_code) * 0.8:  # If less than 80% of expected
                    print(f"  ⚠ Warning: Only {len(actual_content)} chars typed, expected ~{len(cleaned_code)}")
                else:
                    print(f"✓ Strategy B: Code typed successfully ({len(actual_content)} chars)")
            except Exception:
                print("✓ Strategy B: Code typed successfully")
            
            return True
            
        except Exception as e:
            print(f"✗ Strategy B failed: {e}")
            return False
    
    async def handle_type2_code_completion(self):
        """Handle Type 2 code completion with smart strategies"""
        try:
            print("\n🎯 TYPE 2 CODE COMPLETION DETECTED")
            
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
            success = await self.paste_code_strategy_b(answers_lines, static_lines)
            
            if success:
                print("✓ Type 2 code pasted successfully!")
            else:
                print("✗ Type 2 code paste failed")
            
            return success
            
        except Exception as e:
            print(f"✗ Type 2 handling failed: {e}")
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
            return False
