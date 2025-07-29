#!/usr/bin/env python3
"""Debug personality assignment issue"""

import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../.env')

def debug_personality_assignment():
    """Debug the personality assignment logic"""
    
    # Load the integration results
    results_file = Path("vimarsh_content_integration/content_integration_results.json")
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entries = data.get('sacred_text_entries', [])
    print(f"📊 Total entries: {len(entries)}")
    
    # Check first 10 entries
    print("\n🔍 First 10 entries personality assignment:")
    print("=" * 80)
    
    for i, entry in enumerate(entries[:10]):
        original_personality = entry.get('personality')
        keywords = entry.get('keywords', [])
        source = entry.get('source', '')
        
        # Simulate the validation logic
        if not original_personality:
            if keywords:
                derived_personality = keywords[0].title()
            else:
                derived_personality = 'Unknown'
        else:
            derived_personality = original_personality
            
        print(f"Entry {i+1}:")
        print(f"  ID: {entry.get('id', 'N/A')}")
        print(f"  Original personality: {original_personality}")
        print(f"  Keywords: {keywords}")
        print(f"  Source: {source[:50]}...")
        print(f"  Derived personality: {derived_personality}")
        print("-" * 40)
    
    # Check personality distribution based on keywords
    print("\n📈 Personality distribution (based on keywords):")
    print("=" * 80)
    
    personality_counts = {}
    entries_without_keywords = 0
    
    for entry in entries:
        keywords = entry.get('keywords', [])
        if keywords:
            personality = keywords[0].title()
            personality_counts[personality] = personality_counts.get(personality, 0) + 1
        else:
            entries_without_keywords += 1
    
    for personality, count in sorted(personality_counts.items()):
        print(f"{personality}: {count} entries")
    
    if entries_without_keywords > 0:
        print(f"Entries without keywords: {entries_without_keywords}")
    
    # Check for specific personality keywords
    print("\n🎯 Specific personality analysis:")
    print("=" * 80)
    
    target_personalities = ['buddha', 'einstein', 'newton', 'rumi', 'marcus', 'lao', 'confucius', 'lincoln']
    
    for target in target_personalities:
        count = sum(1 for entry in entries if target.lower() in [k.lower() for k in entry.get('keywords', [])])
        print(f"{target.title()}: {count} entries")

if __name__ == "__main__":
    debug_personality_assignment()
