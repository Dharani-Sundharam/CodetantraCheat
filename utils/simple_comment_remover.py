#!/usr/bin/env python3
"""
Simple Comment Remover - Easy to use version
"""

from comment_remover import CommentRemover

def main():
    """Simple interactive comment remover"""
    remover = CommentRemover()
    
    print("Simple Comment Remover")
    print("=" * 30)
    print("Enter your code below:")
    print("(Press Enter twice when done)")
    print("=" * 30)
    
    # Collect lines until two empty lines
    lines = []
    empty_count = 0
    
    while True:
        try:
            line = input()
            
            if line.strip() == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return
        except EOFError:
            break
    
    if not lines:
        print("No code entered!")
        return
    
    code = '\n'.join(lines)
    
    # Ask for language
    print("\nProgramming language? (java/cpp/python/javascript/c or press Enter for auto-detect)")
    language = input("Language: ").strip().lower()
    
    if not language:
        # Auto-detect based on code content
        if 'public class' in code.lower():
            language = 'java'
        elif '#include <iostream>' in code.lower():
            language = 'cpp'
        elif 'def ' in code.lower():
            language = 'python'
        elif 'function ' in code.lower():
            language = 'javascript'
        else:
            language = 'c'
    
    print(f"\nRemoving comments from {language} code...")
    
    try:
        cleaned = remover.process_text(code, language)
        
        print("\nCleaned Code:")
        print("=" * 50)
        print(cleaned)
        print("=" * 50)
        
        # Ask if user wants to save
        save = input("\nSave to file? (y/n): ").strip().lower()
        if save == 'y':
            filename = input("Filename (e.g., cleaned_code.java): ").strip()
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(cleaned)
                print(f"Saved to {filename}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
