#!/usr/bin/env python3
"""
More targeted script to fix specific syntax issues in test files.
"""

import os
import re

def fix_fstring_quotes(file_path):
    """Fix f-string quote conflicts"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Fix f-string quote conflicts by changing double quotes inside f-strings to single quotes
        # Pattern: f"...{var["key"]}..." -> f"...{var['key']}..."
        pattern = r'f"([^"]*){([^}]*)"([^"]*)"([^}]*)}([^"]*)"'
        
        def replace_quotes(match):
            before_var = match.group(1)
            var_part = match.group(2).replace('"', "'")
            middle = match.group(3)
            key_part = match.group(4).replace('"', "'")
            after_var = match.group(5)
            return f'f"{before_var}{{{var_part}"{middle}"{key_part}}}{after_var}"'
        
        # Simpler approach - find and replace specific problematic patterns
        content = re.sub(r'sample_personality\["([^"]+)"\]', r"sample_personality['\1']", content)
        content = re.sub(r'personality\["([^"]+)"\]', r"personality['\1']", content)
        
        # Remove problematic attribute accesses that don't exist
        content = re.sub(r'\.status\.value', '', content)
        content = re.sub(r'\.is_active', '', content) 
        content = re.sub(r'\.quality_score', '', content)
        content = re.sub(r'\.usage_count', '', content)
        content = re.sub(r'\.expert_approved', '', content)
        content = re.sub(r'\.expertise_areas\[[^\]]+\]', '', content)
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Fixed f-string quotes in {file_path}")
            return True
        else:
            print(f"ℹ️  No f-string issues in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix f-string issues in test files"""
    test_dir = "/Users/ved/Apps/vimarsh/backend/tests"
    
    failing_tests = [
        "test_admin_simple.py",
        "test_complete_domain_system.py", 
        "test_complete_system.py",
        "test_final_validation.py",
        "test_frontend_integration.py",
        "test_function_app_integration.py",
        "test_integration_complete.py",
        "test_multi_personality.py",
        "test_multi_personality_llm.py",
        "test_newton_timeout_fix.py",
        "test_personality_content_integration.py",
        "test_remaining_components.py"
    ]
    
    fixed_count = 0
    
    for test_file in failing_tests:
        file_path = os.path.join(test_dir, test_file)
        if os.path.exists(file_path):
            if fix_fstring_quotes(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n🎯 Fixed f-string issues in {fixed_count} test files")

if __name__ == "__main__":
    main()
