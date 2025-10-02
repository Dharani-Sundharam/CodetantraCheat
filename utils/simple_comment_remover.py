"""
Simple Comment Remover
A lightweight version for quick comment removal
"""

import re

def remove_comments_simple(code: str) -> str:
    """
    Simple comment removal for common languages
    Args:
        code: Source code string
    Returns:
        Code with comments removed
    """
    if not code.strip():
        return code
    
    lines = code.split('\n')
    result_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Handle multi-line comments /* */
        if '/*' in line:
            comment_start = line.find('/*')
            comment_end = line.find('*/', comment_start)
            
            if comment_end != -1:
                # Single line multi-line comment
                before_comment = line[:comment_start]
                after_comment = line[comment_end + 2:]
                line = before_comment + after_comment
            else:
                # Multi-line comment spanning multiple lines
                before_comment = line[:comment_start]
                result_lines.append(before_comment)
                
                # Skip lines until we find the end
                i += 1
                while i < len(lines) and '*/' not in lines[i]:
                    i += 1
                
                if i < len(lines):
                    # Found the end, add the rest of the line
                    end_line = lines[i]
                    after_comment = end_line[end_line.find('*/') + 2:]
                    result_lines.append(after_comment)
                i += 1
                continue
        
        # Handle single line comments
        if '//' in line:
            # Check if // is inside a string
            in_string = False
            quote_char = None
            comment_pos = -1
            
            for j, char in enumerate(line):
                if char in ['"', "'"] and (j == 0 or line[j-1] != '\\'):
                    if not in_string:
                        in_string = True
                        quote_char = char
                    elif char == quote_char:
                        in_string = False
                        quote_char = None
                elif char == '/' and j < len(line) - 1 and line[j+1] == '/' and not in_string:
                    comment_pos = j
                    break
            
            if comment_pos != -1:
                line = line[:comment_pos].rstrip()
        
        # Add non-empty lines
        if line.strip():
            result_lines.append(line)
        elif line.strip() == '' and result_lines and result_lines[-1].strip():
            # Preserve empty lines between code blocks
            result_lines.append('')
        
        i += 1
    
    return '\n'.join(result_lines)

if __name__ == "__main__":
    # Test the simple comment remover
    test_code = '''
    // This is a single line comment
    public class Test {
        /* This is a
           multi-line comment */
        public static void main(String[] args) {
            System.out.println("Hello World"); // Another comment
        }
    }
    '''
    
    print("Original code:")
    print(test_code)
    print("\nCleaned code:")
    print(remove_comments_simple(test_code))
