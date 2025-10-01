#!/usr/bin/env python3
"""
Universal Comment Remover
Removes comments from code in various programming languages
"""

import re
import sys
import argparse
from pathlib import Path

class CommentRemover:
    def __init__(self):
        # Language-specific comment patterns
        self.language_patterns = {
            # Languages with // and /* */ comments
            'c': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.c', '.h']
            },
            'cpp': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.cpp', '.cc', '.cxx', '.hpp', '.hxx']
            },
            'java': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.java']
            },
            'javascript': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.js', '.jsx', '.ts', '.tsx']
            },
            'csharp': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.cs']
            },
            'go': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.go']
            },
            'rust': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.rs']
            },
            'php': {
                'single_line': r'//.*$|#.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.php']
            },
            'swift': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.swift']
            },
            'kotlin': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.kt', '.kts']
            },
            'dart': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.dart']
            },
            
            # Languages with # comments
            'python': {
                'single_line': r'#.*$',
                'multi_line': r'""".*?"""|\'\'\'.*?\'\'\'',
                'extensions': ['.py', '.pyw']
            },
            'ruby': {
                'single_line': r'#.*$',
                'multi_line': r'=begin.*?=end',
                'extensions': ['.rb']
            },
            'perl': {
                'single_line': r'#.*$',
                'multi_line': r'=begin.*?=cut',
                'extensions': ['.pl', '.pm']
            },
            'bash': {
                'single_line': r'#.*$',
                'multi_line': r'',
                'extensions': ['.sh', '.bash']
            },
            'powershell': {
                'single_line': r'#.*$',
                'multi_line': r'<#.*?#>',
                'extensions': ['.ps1', '.psm1']
            },
            'yaml': {
                'single_line': r'#.*$',
                'multi_line': r'',
                'extensions': ['.yml', '.yaml']
            },
            'toml': {
                'single_line': r'#.*$',
                'multi_line': r'',
                'extensions': ['.toml']
            },
            'ini': {
                'single_line': r'#.*$|;.*$',
                'multi_line': r'',
                'extensions': ['.ini', '.cfg', '.conf']
            },
            
            # Languages with -- comments
            'sql': {
                'single_line': r'--.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.sql']
            },
            'lua': {
                'single_line': r'--.*$',
                'multi_line': r'--\[\[.*?\]\]',
                'extensions': ['.lua']
            },
            'haskell': {
                'single_line': r'--.*$',
                'multi_line': r'\{-.*?-\}',
                'extensions': ['.hs']
            },
            
            # Languages with % comments
            'matlab': {
                'single_line': r'%.*$',
                'multi_line': r'',
                'extensions': ['.m']
            },
            'erlang': {
                'single_line': r'%.*$',
                'multi_line': r'',
                'extensions': ['.erl', '.hrl']
            },
            
            # Languages with ' comments
            'vb': {
                'single_line': r"'.*$",
                'multi_line': r'',
                'extensions': ['.vb', '.vbs']
            },
            
            # Languages with <!-- --> comments
            'html': {
                'single_line': r'',
                'multi_line': r'<!--.*?-->',
                'extensions': ['.html', '.htm']
            },
            'xml': {
                'single_line': r'',
                'multi_line': r'<!--.*?-->',
                'extensions': ['.xml']
            },
            
            # Languages with <!-- --> and /* */ comments
            'css': {
                'single_line': r'',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.css']
            },
            'scss': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.scss', '.sass']
            },
            'less': {
                'single_line': r'//.*$',
                'multi_line': r'/\*.*?\*/',
                'extensions': ['.less']
            }
        }
    
    def detect_language(self, file_path):
        """Detect programming language based on file extension"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        for lang, config in self.language_patterns.items():
            if extension in config['extensions']:
                return lang
        
        return 'unknown'
    
    def remove_comments(self, code, language='auto', file_path=None):
        """Remove comments from code"""
        if language == 'auto' and file_path:
            language = self.detect_language(file_path)
        
        if language not in self.language_patterns:
            print(f"⚠ Warning: Unknown language '{language}', using C-style comments")
            language = 'c'
        
        patterns = self.language_patterns[language]
        
        # Remove multi-line comments first (to avoid conflicts)
        if patterns['multi_line']:
            code = re.sub(patterns['multi_line'], '', code, flags=re.DOTALL)
        
        # Remove single-line comments
        if patterns['single_line']:
            code = re.sub(patterns['single_line'], '', code, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            cleaned_line = line.rstrip()
            # Only keep non-empty lines
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def process_file(self, input_file, output_file=None, language='auto'):
        """Process a single file"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            cleaned_code = self.remove_comments(code, language, input_file)
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_code)
                print(f"✅ Cleaned code saved to: {output_file}")
            else:
                print("🧹 Cleaned Code:")
                print("=" * 50)
                print(cleaned_code)
                print("=" * 50)
            
            return cleaned_code
            
        except Exception as e:
            print(f"❌ Error processing file: {e}")
            return None
    
    def process_text(self, text, language='c'):
        """Process text directly"""
        return self.remove_comments(text, language)
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return list(self.language_patterns.keys())

def main():
    parser = argparse.ArgumentParser(description='Remove comments from code in various programming languages')
    parser.add_argument('input', help='Input file path or text to process')
    parser.add_argument('-o', '--output', help='Output file path (optional)')
    parser.add_argument('-l', '--language', default='auto', 
                       help='Programming language (auto-detect if not specified)')
    parser.add_argument('-t', '--text', action='store_true', 
                       help='Process input as text instead of file path')
    parser.add_argument('--list-languages', action='store_true',
                       help='List all supported programming languages')
    
    args = parser.parse_args()
    
    remover = CommentRemover()
    
    if args.list_languages:
        print("🌍 Supported Programming Languages:")
        print("=" * 40)
        for lang in sorted(remover.get_supported_languages()):
            extensions = ', '.join(remover.language_patterns[lang]['extensions'])
            print(f"  {lang:12} - {extensions}")
        return
    
    if args.text:
        # Process as text
        cleaned = remover.process_text(args.input, args.language)
        if cleaned:
            print("🧹 Cleaned Code:")
            print("=" * 50)
            print(cleaned)
            print("=" * 50)
    else:
        # Process as file
        if not Path(args.input).exists():
            print(f"❌ File not found: {args.input}")
            return
        
        detected_lang = remover.detect_language(args.input)
        print(f"🔍 Detected language: {detected_lang}")
        
        remover.process_file(args.input, args.output, args.language)

if __name__ == "__main__":
    main()
