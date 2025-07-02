#!/usr/bin/env python3
"""
Fix import statements in error handling modules
"""

import os
import re

def fix_imports_in_file(file_path, fixes):
    """Fix import statements in a single file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        for old_import, new_import in fixes:
            content = content.replace(old_import, new_import)
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Fixed imports in {os.path.basename(file_path)}")
            return True
        else:
            print(f"⚪ No changes needed in {os.path.basename(file_path)}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all import statements in error handling modules"""
    
    # Define the import fixes needed
    import_fixes = [
        # Fix error_classifier imports
        ("from error_classifier import", "from .error_classifier import"),
        ("from graceful_degradation import", "from .graceful_degradation import"),
        ("from intelligent_retry import", "from .intelligent_retry import"),
        ("from llm_fallback import", "from .llm_fallback import"),
        ("from circuit_breaker import", "from .circuit_breaker import"),
        ("from error_analytics import", "from .error_analytics import"),
    ]
    
    # Get all Python files in error_handling directory
    error_handling_dir = "/Users/vedprakashmishra/vimarsh/backend/error_handling"
    
    python_files = []
    for file in os.listdir(error_handling_dir):
        if file.endswith('.py') and not file.startswith('test_') and file != '__init__.py':
            python_files.append(os.path.join(error_handling_dir, file))
    
    print(f"🔧 Fixing imports in {len(python_files)} files...")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path, import_fixes):
            fixed_count += 1
    
    print(f"\n🎉 Fixed imports in {fixed_count} files")

if __name__ == "__main__":
    main()
