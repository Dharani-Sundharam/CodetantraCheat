"""
Interactive Comment Remover
Command-line tool for removing comments from code
"""

import sys
from comment_remover import CommentRemover

def main():
    """Interactive comment remover"""
    print("CodeTantra Comment Remover")
    print("=" * 30)
    print("Enter your code (type 'END' on a new line when done):")
    print("Press Ctrl+C to exit")
    print()
    
    remover = CommentRemover()
    code_lines = []
    
    try:
        while True:
            try:
                line = input()
                if line.strip().upper() == 'END':
                    break
                code_lines.append(line)
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    
    if not code_lines:
        print("No code provided.")
        return
    
    code = '\n'.join(code_lines)
    
    print("\n" + "=" * 50)
    print("ORIGINAL CODE:")
    print("=" * 50)
    print(code)
    
    # Detect language
    language = remover.detect_language(code)
    print(f"\nDetected language: {language}")
    
    # Remove comments
    cleaned_code = remover.clean_code(code)
    
    print("\n" + "=" * 50)
    print("CLEANED CODE:")
    print("=" * 50)
    print(cleaned_code)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    original_lines = len(code.split('\n'))
    cleaned_lines = len(cleaned_code.split('\n'))
    removed_lines = original_lines - cleaned_lines
    print(f"Original lines: {original_lines}")
    print(f"Cleaned lines: {cleaned_lines}")
    print(f"Lines removed: {removed_lines}")

if __name__ == "__main__":
    main()
