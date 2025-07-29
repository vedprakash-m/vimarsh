#!/usr/bin/env python3
"""
Safe wrapper for running the embedding generator that handles Unicode encoding issues.
"""

import os
import sys
import subprocess

def main():
    """Run the embedding generator with proper Unicode handling."""
    
    # Set environment variables for UTF-8 encoding
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    # For Windows, set console to UTF-8 mode
    if sys.platform.startswith('win'):
        # Enable UTF-8 mode for Python
        env['PYTHONUTF8'] = '1'
        
        # Try to set console code page to UTF-8
        try:
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        except Exception:
            pass  # Ignore if chcp fails
    
    # Run the embedding generator
    try:
        result = subprocess.run([
            sys.executable, 
            'advanced_embeddings_generator.py'
        ], env=env, cwd=os.path.dirname(__file__))
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running embedding generator: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
