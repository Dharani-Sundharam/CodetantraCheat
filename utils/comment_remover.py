"""
Comment Remover Utility
Removes comments from code in various programming languages
"""

import re
from typing import List, Tuple

class CommentRemover:
    def __init__(self):
        self.language_patterns = {
            'java': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'string_literals': r'"(?:[^"\\]|\\.)*"',
                'char_literals': r"'(?:[^'\\]|\\.)*'"
            },
            'cpp': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'string_literals': r'"(?:[^"\\]|\\.)*"',
                'char_literals': r"'(?:[^'\\]|\\.)*'"
            },
            'c': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'string_literals': r'"(?:[^"\\]|\\.)*"',
                'char_literals': r"'(?:[^'\\]|\\.)*'"
            },
            'python': {
                'single_line': r'#.*$',
                'multi_line': r'""".*?"""',
                'multi_line_alt': r"'''.*?'''",
                'string_literals': r'"(?:[^"\\]|\\.)*"',
                'char_literals': r"'(?:[^'\\]|\\.)*'"
            },
            'javascript': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'string_literals': r'"(?:[^"\\]|\\.)*"',
                'char_literals': r"'(?:[^'\\]|\\.)*'"
            },
            'typescript': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'string_literals': r'"(?:[^"\\]|\\.)*"',
                'char_literals': r"'(?:[^'\\]|\\.)*'"
            }
        }
    
    def detect_language(self, code: str) -> str:
        """Detect programming language from code"""
        code_lower = code.lower()
        
        # Java detection
        if any(keyword in code_lower for keyword in ['public class', 'import java', 'System.out.println', 'public static void main']):
            return 'java'
        
        # C++ detection
        if any(keyword in code_lower for keyword in ['#include <iostream>', '#include <cstdio>', 'using namespace std', 'cout <<', 'cin >>']):
            return 'cpp'
        
        # C detection
        if any(keyword in code_lower for keyword in ['#include <stdio.h>', '#include <stdlib.h>', 'printf(', 'scanf(']):
            return 'c'
        
        # Python detection
        if any(keyword in code_lower for keyword in ['def ', 'import ', 'from ', 'print(', 'if __name__']):
            return 'python'
        
        # JavaScript detection
        if any(keyword in code_lower for keyword in ['function ', 'var ', 'let ', 'const ', 'console.log']):
            return 'javascript'
        
        # TypeScript detection
        if any(keyword in code_lower for keyword in ['interface ', 'type ', 'enum ', 'export ']):
            return 'typescript'
        
        # Default to Java if uncertain
        return 'java'
    
    def remove_comments(self, code: str, language: str = None) -> str:
        """
        Remove comments from code
        Args:
            code: Source code string
            language: Programming language (auto-detected if None)
        Returns:
            Code with comments removed
        """
        if not code.strip():
            return code
        
        if language is None:
            language = self.detect_language(code)
        
        if language not in self.language_patterns:
            return code
        
        patterns = self.language_patterns[language]
        lines = code.split('\n')
        result_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for multi-line comments
            if language in ['java', 'cpp', 'c', 'javascript', 'typescript']:
                # Handle /* */ comments
                if '/*' in line:
                    # Find the end of multi-line comment
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
            if language == 'python':
                # Python # comments
                if '#' in line:
                    # Check if # is inside a string
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
                        elif char == '#' and not in_string:
                            comment_pos = j
                            break
                    
                    if comment_pos != -1:
                        line = line[:comment_pos].rstrip()
            else:
                # C-style // comments
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
    
    def clean_code(self, code: str) -> str:
        """
        Clean code by removing comments and extra whitespace
        Args:
            code: Source code string
        Returns:
            Cleaned code
        """
        # Remove comments
        cleaned = self.remove_comments(code)
        
        # Remove excessive blank lines (more than 2 consecutive)
        lines = cleaned.split('\n')
        result_lines = []
        blank_count = 0
        
        for line in lines:
            if line.strip() == '':
                blank_count += 1
                if blank_count <= 2:
                    result_lines.append(line)
            else:
                blank_count = 0
                result_lines.append(line)
        
        return '\n'.join(result_lines)

def remove_comments_from_code(code: str, language: str = None) -> str:
    """
    Convenience function to remove comments from code
    Args:
        code: Source code string
        language: Programming language (auto-detected if None)
    Returns:
        Code with comments removed
    """
    remover = CommentRemover()
    return remover.remove_comments(code, language)

def clean_code(code: str) -> str:
    """
    Convenience function to clean code
    Args:
        code: Source code string
    Returns:
        Cleaned code
    """
    remover = CommentRemover()
    return remover.clean_code(code)

if __name__ == "__main__":
    # Test the comment remover
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
    print(clean_code(test_code))
