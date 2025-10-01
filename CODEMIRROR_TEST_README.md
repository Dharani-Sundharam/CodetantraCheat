# 🧪 CodeMirror Smart Extraction Test

## Overview

This test script (`codemirror_test.py`) is designed to test and demonstrate **SMART code extraction** from CodeTantra's CodeMirror editor with support for **two different types** of code completion problems.

## 🎯 Two Types of Code Completion

### **Type 1: Fully Editable Code**
- **Description**: The entire CodeMirror editor is editable
- **Strategy**: Extract all lines and paste everything
- **Use Case**: Simple code completion problems
- **Detection**: No read-only lines detected (no red overlay)

### **Type 2: Template with Read-Only Sections**
- **Description**: Code has static structure with red overlay (read-only)
- **Strategy**: Smart extraction of ONLY editable sections
- **Use Cases**:
  1. **Partial Template**: Editable sections in middle of static structure
  2. **Commented Template**: Static parts commented with `/* ... */` in answers
- **Detection**: Red overlay, reduced opacity, or read-only markers detected

## 🚀 Features

✅ **Auto-Login** - Uses credentials from `credentials.py`  
✅ **Smart Detection** - Automatically detects Type 1 vs Type 2  
✅ **Read-Only Detection** - Identifies red overlay sections  
✅ **Comment Handling** - Detects and removes multiline comments  
✅ **Line-by-Line Analysis** - Shows which lines are editable/read-only  
✅ **Clipboard Copy** - Copies extracted code to clipboard  
✅ **Verification** - Verifies clipboard content  

## 📋 How It Works

### Detection Process:
1. **Open CodeMirror editor** in CodeTantra
2. **Analyze all lines** for read-only indicators:
   - Red overlay styling
   - Reduced opacity (< 0.6)
   - Non-editable CSS classes
3. **Classify as Type 1 or Type 2**
4. **Extract accordingly**:
   - **Type 1**: Extract all lines
   - **Type 2**: Extract only editable lines
5. **Handle comments** (if present):
   - Detect `/* ... */` multiline comments
   - Remove commented sections
   - Extract only actual code

### Extraction Logic:

```
Type 1 (Fully Editable):
┌─────────────────────┐
│ Line 1 (editable)   │ ✓ Extract
│ Line 2 (editable)   │ ✓ Extract
│ Line 3 (editable)   │ ✓ Extract
└─────────────────────┘

Type 2 (Template with Read-Only):
┌─────────────────────┐
│ Line 1 (readonly)   │ ✗ Skip (red overlay)
│ Line 2 (editable)   │ ✓ Extract
│ Line 3 (editable)   │ ✓ Extract
│ Line 4 (readonly)   │ ✗ Skip (red overlay)
└─────────────────────┘

Type 2 with Comments:
┌─────────────────────┐
│ /*                  │ ✗ Skip (comment start)
│ Line 1 (readonly)   │ ✗ Skip (inside comment)
│ */                  │ ✗ Skip (comment end)
│ Line 2 (editable)   │ ✓ Extract
│ Line 3 (editable)   │ ✓ Extract
└─────────────────────┘
```

## 🔧 Usage

### **Step 1: Install Dependencies**
```bash
pip install playwright pyperclip
playwright install firefox
```

### **Step 2: Setup Credentials** (Optional)
Create `credentials.py`:
```python
LOGIN_URL = "https://rmd.codetantra.com/login.jsp"

ANSWERS_ACCOUNT = {
    'username': 'your_email@example.com',
    'password': 'your_password'
}
```

### **Step 3: Run the Test**
```bash
python codemirror_test.py
```

### **Step 4: Follow the Prompts**
1. Browser will open automatically
2. Login (automatic if credentials.py exists)
3. Navigate to a **code completion problem**
4. Press ENTER when ready
5. Watch the smart extraction work!

## 📊 Example Output

### Type 1 Detection:
```
🔍 Testing CodeMirror extraction...
✓ CodeMirror editor found
✓ Scrolled to editor

📊 Analyzing code structure...
🎯 TYPE 1 DETECTED: Fully editable code

📝 Extracting fully editable code...
✓ Found 10 lines in editor
  Line 1: 'public class Main {'
  Line 2: '    public static void main(String[] args) {'
  ...
✓ Type 1 extraction successful!
```

### Type 2 Detection:
```
🔍 Testing CodeMirror extraction...
✓ CodeMirror editor found
✓ Scrolled to editor

📊 Analyzing code structure...
🎯 TYPE 2 DETECTED: Template with read-only sections (red overlay)

📝 Extracting code from template with read-only sections...
✓ Found 15 lines in editor
✓ Read-only lines: 8
  Line 1 [READ-ONLY]: 'public class Main {'
  Line 2 [READ-ONLY]: '    public static void main(String[] args) {'
  Line 3 [EDITABLE]: '        // Your code here'
  Line 4 [EDITABLE]: '        System.out.println("Hello");'
  ...

🔍 DETECTED: Read-only sections are NOT commented
   Strategy: Extract ONLY editable sections

✓ Type 2 extraction successful!
✓ Total lines: 15
✓ Editable lines: 7
✓ Read-only lines: 8
```

## 🎓 Testing Strategy

### Test Type 1:
1. Find a problem with fully editable code
2. Run the test script
3. Verify it detects Type 1
4. Check that ALL lines are extracted

### Test Type 2 (No Comments):
1. Find a problem with red overlay sections
2. Run the test script
3. Verify it detects Type 2
4. Check that ONLY editable lines are extracted

### Test Type 2 (With Comments):
1. Find a problem where template is commented out
2. Run the test script
3. Verify it detects comments
4. Check that commented sections are removed

## 🔍 Debugging

The script provides detailed output:
- Line-by-line extraction status
- Read-only vs editable classification
- Comment detection results
- Final extracted code preview
- Clipboard verification

## ⚠️ Important Notes

1. **Read-Only Detection**: Uses multiple methods (opacity, color, CSS classes)
2. **Comment Detection**: Looks for `/* ... */` multiline comments
3. **Fallback**: If detection fails, falls back to Type 1 extraction
4. **Browser**: Uses Firefox (best for CodeTantra)

## 🔄 Integration with Main Automation

Once tested and working, this logic can be integrated into:
- `codetantra_playwright.py` - Main automation tool
- `get_code_from_answers()` - Code extraction function
- `paste_code_to_target()` - Smart pasting function

## 📝 Next Steps

1. **Test on both types** of problems
2. **Verify extraction accuracy**
3. **Check clipboard content**
4. **Refine detection logic** if needed
5. **Integrate into main automation**

## 🎉 Success Criteria

✅ Type 1 problems extract all code  
✅ Type 2 problems extract only editable sections  
✅ Comments are properly detected and removed  
✅ Clipboard contains correct code  
✅ No errors or exceptions  

Happy Testing! 🚀

