#!/usr/bin/env python3
"""
Multi-Personality Content Integration Script
Merges personality teachings into the existing spiritual texts database
"""

import json
import os
import sys
from pathlib import Path

def load_json_file(file_path: str) -> list:
    """Load JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return []

def save_json_file(data: list, file_path: str):
    """Save JSON data to file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def integrate_personality_content(target_personality=None):
    """Integrate personality content into spiritual texts
    
    Args:
        target_personality: If specified, only integrate this personality's content
    """
    # Base paths
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    backend_data_dir = base_dir / "backend" / "data"
    sources_dir = data_dir / "sources"
    db_dir = backend_data_dir / "vimarsh-db"
    
    # Load existing spiritual texts
    spiritual_texts_path = db_dir / "spiritual-texts.json"
    existing_texts = load_json_file(str(spiritual_texts_path))
    
    print(f"Loaded {len(existing_texts)} existing spiritual texts")
    
    # Define available personalities and their files
    personality_files = {
        'buddha': 'buddha_teachings.json',
        'jesus': 'jesus_teachings.json', 
        'einstein': 'einstein_teachings.json',
        'lincoln': 'lincoln_teachings.json',
        'marcus_aurelius': 'marcus_aurelius_teachings.json',
        'lao_tzu': 'lao_tzu_teachings.json',
        'rumi': 'rumi_teachings.json'
    }
    
    # Load personality content
    personality_content = {}
    for personality, filename in personality_files.items():
        if target_personality and personality != target_personality:
            continue
            
        file_path = sources_dir / filename
        content = load_json_file(str(file_path))
        if content:
            personality_content[personality] = content
            print(f"Loaded {len(content)} {personality.title()} teachings")
    
    # If target personality specified but not found, exit
    if target_personality and target_personality not in personality_content:
        print(f"❌ No content found for personality: {target_personality}")
        return
    
    # Combine all texts
    all_texts = existing_texts.copy()
    
    # Add personality content
    for personality, texts in personality_content.items():
        for text in texts:
            # Ensure consistent structure with existing texts
            if 'personality' not in text:
                text['personality'] = personality
            all_texts.append(text)
    
    # Tag existing texts as Krishna (if not already tagged)
    for text in all_texts:
        if 'personality' not in text and text.get('source') == 'Bhagavad Gita':
            text['personality'] = 'krishna'
        elif 'personality' not in text and text.get('source') == 'Srimad Bhagavatam':
            text['personality'] = 'krishna'
        elif 'personality' not in text:
            text['personality'] = 'krishna'  # Default to Krishna for existing content
    
    print(f"Combined total: {len(all_texts)} spiritual texts")
    
    # Save updated spiritual texts
    save_json_file(all_texts, str(spiritual_texts_path))
    print(f"✅ Updated spiritual-texts.json with {len(all_texts)} total texts")
    
    # Also update the main spiritual_texts.json if it exists
    main_spiritual_path = data_dir / "spiritual_texts.json"
    if main_spiritual_path.exists():
        save_json_file(all_texts, str(main_spiritual_path))
        print("✅ Updated main spiritual_texts.json")
    
    # Create personality-specific files for easier management
    personalities = {}
    for text in all_texts:
        personality = text.get('personality', 'krishna')
        if personality not in personalities:
            personalities[personality] = []
        personalities[personality].append(text)
    
    # Save personality-specific files
    for personality, texts in personalities.items():
        personality_file = db_dir / f"{personality}-texts.json"
        save_json_file(texts, str(personality_file))
        print(f"✅ Created {personality}-texts.json with {len(texts)} texts")
    
    print("\n🎉 Content integration completed successfully!")
    print("Summary:")
    for personality, texts in personalities.items():
        print(f"  - {personality.title()}: {len(texts)} texts")

if __name__ == "__main__":
    import sys
    target_personality = sys.argv[1] if len(sys.argv) > 1 else None
    integrate_personality_content(target_personality)
