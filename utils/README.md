# Comment Remover Utilities

This directory contains utilities for removing comments from code in various programming languages.

## Files

### `comment_remover.py`
**Main comment remover class with full language support**
- Supports Java, C++, C, Python, JavaScript, TypeScript
- Handles single-line and multi-line comments
- Preserves string literals and character literals
- Auto-detects programming language
- Removes excessive blank lines

### `simple_comment_remover.py`
**Lightweight version for quick comment removal**
- Basic comment removal for C-style languages
- Handles `//` and `/* */` comments
- Preserves string literals
- Faster processing for simple cases

### `interactive_comment_remover.py`
**Command-line interactive tool**
- Interactive interface for removing comments
- Auto-detects language
- Shows before/after comparison
- Provides statistics

### `comment_remover.bat`
**Windows batch file for easy execution**
- Double-click to run interactive tool
- No command-line knowledge required

## Usage

### Python Import
```python
from comment_remover import CommentRemover, clean_code

# Auto-detect language and clean
cleaned = clean_code(your_code)

# Specify language
remover = CommentRemover()
cleaned = remover.remove_comments(your_code, 'java')
```

### Command Line
```bash
# Interactive mode
python interactive_comment_remover.py

# Windows batch file
comment_remover.bat
```

### Simple Usage
```python
from simple_comment_remover import remove_comments_simple

cleaned = remove_comments_simple(your_code)
```

## Supported Languages

- **Java** - `//` and `/* */` comments
- **C++** - `//` and `/* */` comments  
- **C** - `//` and `/* */` comments
- **Python** - `#` and `"""` comments
- **JavaScript** - `//` and `/* */` comments
- **TypeScript** - `//` and `/* */` comments

## Features

- **Smart Detection** - Automatically detects programming language
- **String Preservation** - Doesn't remove comments inside strings
- **Multi-line Support** - Handles comments spanning multiple lines
- **Whitespace Cleanup** - Removes excessive blank lines
- **Error Handling** - Robust parsing with fallbacks

## Examples

### Input
```java
// This is a comment
public class Test {
    /* Multi-line
       comment */
    public static void main(String[] args) {
        System.out.println("Hello"); // Another comment
    }
}
```

### Output
```java
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
```

## Integration with CodeTantra Automation

The comment remover is used in the automation process to:
1. Clean code copied from answers account
2. Remove comments before typing into target account
3. Ensure clean code submission
4. Improve automation reliability

## Requirements

- Python 3.6+
- No external dependencies

## Notes

- Comments inside string literals are preserved
- Multi-line comments are properly handled
- Empty lines are cleaned up but some preserved for readability
- Language detection is based on common keywords and patterns
