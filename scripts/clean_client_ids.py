#!/usr/bin/env python3
"""
Script to clean up hardcoded Client IDs from documentation files
Replace actual Client IDs with placeholders for security
"""

import os
import re
import glob

# Define the actual Client IDs to replace
CLIENT_IDS_TO_REPLACE = [
    'e4bd74b8-9a82-40c6-8d52-3e231733095e',
    'e4bd74b8-9a82-40c6-8d52-3e231733095e'
]

# Placeholder to use instead
PLACEHOLDER = '<your-client-id>'

def clean_documentation_files():
    """Clean hardcoded Client IDs from documentation files"""
    
    # File patterns to clean (documentation only, not config files)
    doc_patterns = [
        '*.md',
        'docs/**/*.md',
    ]
    
    files_cleaned = []
    
    for pattern in doc_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Replace each Client ID with placeholder
                for client_id in CLIENT_IDS_TO_REPLACE:
                    content = content.replace(client_id, PLACEHOLDER)
                
                # Only write if content changed
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    files_cleaned.append(file_path)
                    print(f"✅ Cleaned: {file_path}")
                    
            except Exception as e:
                print(f"❌ Error cleaning {file_path}: {e}")
    
    return files_cleaned

def main():
    print("🧹 Cleaning hardcoded Client IDs from documentation files...")
    print("=" * 60)
    
    cleaned_files = clean_documentation_files()
    
    print("\n" + "=" * 60)
    print(f"🏁 Cleanup complete! Cleaned {len(cleaned_files)} files")
    
    if cleaned_files:
        print("\n📋 Files cleaned:")
        for file_path in cleaned_files:
            print(f"  - {file_path}")
        
        print(f"\n🔒 Replaced actual Client IDs with: {PLACEHOLDER}")
        print("💡 Actual Client IDs are now managed in frontend/src/config/authIds.ts")
    else:
        print("\n✨ No documentation files needed cleaning")

if __name__ == "__main__":
    main()
