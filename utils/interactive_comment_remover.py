
"""
Interactive Comment Remover
Simple interactive interface for removing comments
"""

from comment_remover import CommentRemover
import sys

def interactive_mode():
    """Interactive mode for comment removal"""
    remover = CommentRemover()
    
    print("Interactive Comment Remover")
    print("=" * 40)
    print("Enter your code and I'll remove the comments!")
    print("Type 'quit' to exit, 'help' for supported languages")
    print("Type 'END' on a new line when done entering code")
    print("=" * 40)
    
    while True:
        print("\nEnter your code (or 'quit' to exit):")
        print("(Type 'END' on a new line when done, or press Ctrl+C to quit)")
        
        try:
            lines = []
            while True:
                try:
                    line = input()
                    if line.strip().lower() == 'quit':
                        print("Goodbye!")
                        return
                    if line.strip().lower() == 'help':
                        print("\nSupported Languages:")
                        for lang in sorted(remover.get_supported_languages()):
                            print(f"  - {lang}")
                        continue
                    if line.strip() == 'END':
                        break
                    lines.append(line)
                except EOFError:
                    # Handle Ctrl+D or Ctrl+Z
                    break
                except KeyboardInterrupt:
                    # Handle Ctrl+C
                    print("\n\nGoodbye!")
                    return
            
            if not lines:
                print("No code entered, try again...")
                continue
                
            code = '\n'.join(lines)
            
            print("\nWhat programming language? (or 'auto' to detect)")
            print("Available: " + ", ".join(sorted(remover.get_supported_languages())))
            language = input("Language: ").strip().lower()
            
            if not language or language == 'auto':
                language = 'c'  # Default to C-style comments
            
            print(f"\nRemoving comments from {language} code...")
            cleaned = remover.process_text(code, language)
            
            print("\nCleaned Code:")
            print("-" * 40)
            print(cleaned)
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Command line mode
        from comment_remover import main as cli_main
        cli_main()
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
