#!/usr/bin/env python3
"""
Integrate Comprehensive Bhagavad Gita Content
===============================================

This script replaces the current limited Krishna content (7 verses) with 
comprehensive Bhagavad Gita content from the uploaded full text.

Author: Vimarsh AI System
Date: Current
Purpose: Address user request for comprehensive Gita integration instead of limited verses
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_comprehensive_gita(file_path: str) -> List[Dict[str, Any]]:
    """Load the comprehensive Bhagavad Gita from JSONL file."""
    gita_content = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        verse_data = json.loads(line.strip())
                        gita_content.append(verse_data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parsing line {line_num}: {e}")
                        continue
        
        logger.info(f"Loaded {len(gita_content)} verses from comprehensive Gita")
        return gita_content
        
    except FileNotFoundError:
        logger.error(f"Comprehensive Gita file not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Error loading comprehensive Gita: {e}")
        return []

def convert_to_krishna_format(gita_verse: Dict[str, Any]) -> Dict[str, Any]:
    """Convert comprehensive Gita verse to Krishna personality format."""
    
    # Extract verse information
    verse_citation = gita_verse.get('verse', 'Unknown')
    chapter = gita_verse.get('chapter', 0)
    sanskrit = gita_verse.get('sanskrit', '')
    translation = gita_verse.get('translation', '')
    content_type = gita_verse.get('content_type', 'verse')
    
    # Create comprehensive content text
    content_parts = []
    if sanskrit:
        content_parts.append(f"Sanskrit: {sanskrit}")
    if translation:
        content_parts.append(f"Translation: {translation}")
    
    # Add purport/commentary if available
    if 'purport' in gita_verse and gita_verse['purport']:
        content_parts.append(f"Purport: {gita_verse['purport']}")
    
    content_text = "\n\n".join(content_parts)
    
    # Create Krishna-formatted entry
    krishna_entry = {
        "id": f"krishna_{verse_citation.lower().replace(' ', '_').replace('.', '_')}_{content_type}",
        "personality": "krishna",
        "content": content_text,
        "source": "Bhagavad Gita As It Is",
        "chapter": chapter,
        "verse": verse_citation,
        "citation": f"Bhagavad Gita {verse_citation}",
        "authority_level": "primary",
        "content_type": content_type,
        "tags": ["dharma", "spiritual_wisdom", "divine_teaching", "arjuna_dialogue"],
        "metadata": {
            "scripture_title": "Bhagavad Gita As It Is",
            "verse_citation": verse_citation,
            "chapter_number": chapter,
            "has_sanskrit": bool(sanskrit),
            "has_translation": bool(translation),
            "has_purport": 'purport' in gita_verse and bool(gita_verse.get('purport')),
            "content_focus": content_type,
            "original_id": gita_verse.get('id', '')
        }
    }
    
    return krishna_entry

def select_representative_verses(gita_content: List[Dict[str, Any]], max_verses: int = 108) -> List[Dict[str, Any]]:
    """
    Select representative verses from the comprehensive Gita.
    108 is a sacred number in Hinduism, representing completeness.
    """
    
    # Key verses that should definitely be included (most important teachings)
    priority_verses = [
        "Bg. 2.47",  # You have the right to perform action, but not to the fruits of action
        "Bg. 18.66", # Surrender unto Me and I shall deliver you from all sins
        "Bg. 4.7",   # Whenever dharma declines, I incarnate
        "Bg. 4.8",   # To deliver the pious and annihilate the miscreants
        "Bg. 7.19",  # After many births, one surrenders to Me
        "Bg. 9.22",  # To those always devoted, I carry what they lack
        "Bg. 2.20",  # The soul is eternal, unborn, undying
        "Bg. 2.14",  # Contact with matter brings pleasure and pain
        "Bg. 15.7",  # The living entities are My eternal fragmental parts
        "Bg. 10.10", # To those constantly devoted, I give understanding
        "Bg. 6.19",  # As a lamp in a windless place does not flicker
        "Bg. 12.6-7", # Those who worship Me with devotion are quickly delivered
        "Bg. 4.11",  # In whatever way people surrender to Me, I reward them
        "Bg. 9.26",  # If offered with love, I accept a leaf, flower, fruit, water
        "Bg. 8.7",   # Remember Me at the time of death
        "Bg. 3.21",  # Whatever great men do, others follow
        "Bg. 2.62-63", # Contemplating objects, attachment develops
        "Bg. 18.78", # Where Krishna and Arjuna are, there is victory
    ]
    
    # Filter to get complete verses (not just commentary)
    complete_verses = [v for v in gita_content if v.get('content_type') == 'complete']
    
    # First, include all priority verses
    selected_verses = []
    priority_set = set(priority_verses)
    
    for verse in complete_verses:
        if verse.get('verse') in priority_set:
            selected_verses.append(verse)
            priority_set.remove(verse.get('verse'))
    
    logger.info(f"Selected {len(selected_verses)} priority verses")
    
    # Then select representative verses from each chapter
    remaining_slots = max_verses - len(selected_verses)
    verses_per_chapter = remaining_slots // 18  # 18 chapters in Bhagavad Gita
    
    chapter_verses = {}
    for verse in complete_verses:
        chapter = verse.get('chapter', 0)
        if chapter not in chapter_verses:
            chapter_verses[chapter] = []
        if verse.get('verse') not in [v.get('verse') for v in selected_verses]:
            chapter_verses[chapter].append(verse)
    
    # Select representative verses from each chapter
    for chapter in sorted(chapter_verses.keys()):
        if chapter == 0:
            continue
        
        chapter_list = chapter_verses[chapter]
        # Take first few verses of each chapter as they often contain key teachings
        for i in range(min(verses_per_chapter, len(chapter_list))):
            if len(selected_verses) < max_verses:
                selected_verses.append(chapter_list[i])
    
    logger.info(f"Selected total of {len(selected_verses)} representative verses from comprehensive Gita")
    return selected_verses

def backup_current_krishna_content(krishna_db_path: str) -> bool:
    """Create backup of current Krishna content."""
    try:
        backup_path = krishna_db_path.replace('.json', '_backup_before_comprehensive_gita.json')
        
        if os.path.exists(krishna_db_path):
            import shutil
            shutil.copy2(krishna_db_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return True
        else:
            logger.warning(f"Krishna database not found for backup: {krishna_db_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False

def update_krishna_database(new_content: List[Dict[str, Any]], krishna_db_path: str) -> bool:
    """Update the Krishna database with comprehensive content."""
    try:
        # Create backup first
        backup_current_krishna_content(krishna_db_path)
        
        # Write new comprehensive content
        with open(krishna_db_path, 'w', encoding='utf-8') as f:
            json.dump(new_content, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated Krishna database with {len(new_content)} comprehensive verses")
        logger.info(f"Database saved to: {krishna_db_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating Krishna database: {e}")
        return False

def update_spiritual_texts_db(krishna_content: List[Dict[str, Any]], spiritual_db_path: str) -> bool:
    """Update the main spiritual texts database."""
    try:
        # Load existing spiritual texts
        if os.path.exists(spiritual_db_path):
            with open(spiritual_db_path, 'r', encoding='utf-8') as f:
                spiritual_texts = json.load(f)
        else:
            spiritual_texts = []
        
        # Remove old Krishna entries
        spiritual_texts = [text for text in spiritual_texts if text.get('personality') != 'krishna']
        
        # Add new Krishna entries
        spiritual_texts.extend(krishna_content)
        
        # Create backup
        backup_path = spiritual_db_path.replace('.json', '_backup_before_comprehensive_gita.json')
        if os.path.exists(spiritual_db_path):
            import shutil
            shutil.copy2(spiritual_db_path, backup_path)
        
        # Write updated database
        with open(spiritual_db_path, 'w', encoding='utf-8') as f:
            json.dump(spiritual_texts, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated main spiritual database with {len(krishna_content)} Krishna verses")
        logger.info(f"Total spiritual texts: {len(spiritual_texts)}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating spiritual texts database: {e}")
        return False

def main():
    """Main function to integrate comprehensive Bhagavad Gita."""
    
    # Define paths
    current_dir = Path(__file__).parent.parent.parent  # Go up to workspace root
    gita_source_path = current_dir / "data" / "sources" / "bhagavad_gita_clean.jsonl"
    krishna_db_path = current_dir / "backend" / "data" / "vimarsh-db" / "krishna-texts.json"
    spiritual_db_path = current_dir / "backend" / "data" / "vimarsh-db" / "spiritual-texts.json"
    
    logger.info("🕉️ Starting comprehensive Bhagavad Gita integration")
    logger.info(f"Source: {gita_source_path}")
    logger.info(f"Krishna DB: {krishna_db_path}")
    logger.info(f"Spiritual DB: {spiritual_db_path}")
    
    # Step 1: Load comprehensive Gita content
    logger.info("📚 Loading comprehensive Bhagavad Gita content...")
    gita_content = load_comprehensive_gita(str(gita_source_path))
    
    if not gita_content:
        logger.error("❌ Failed to load comprehensive Gita content")
        return False
    
    # Step 2: Select representative verses (108 sacred number)
    logger.info("🎯 Selecting representative verses from comprehensive Gita...")
    selected_verses = select_representative_verses(gita_content, max_verses=108)
    
    # Step 3: Convert to Krishna personality format
    logger.info("🔄 Converting verses to Krishna personality format...")
    krishna_content = []
    for verse in selected_verses:
        krishna_entry = convert_to_krishna_format(verse)
        krishna_content.append(krishna_entry)
    
    # Step 4: Update Krishna database
    logger.info("💾 Updating Krishna database...")
    if not update_krishna_database(krishna_content, str(krishna_db_path)):
        logger.error("❌ Failed to update Krishna database")
        return False
    
    # Step 5: Update main spiritual texts database
    logger.info("🔄 Updating main spiritual texts database...")
    if not update_spiritual_texts_db(krishna_content, str(spiritual_db_path)):
        logger.error("❌ Failed to update spiritual texts database")
        return False
    
    # Success summary
    logger.info("✅ Comprehensive Bhagavad Gita integration completed successfully!")
    logger.info(f"📊 Statistics:")
    logger.info(f"   • Total verses processed: {len(gita_content)}")
    logger.info(f"   • Representative verses selected: {len(selected_verses)}")
    logger.info(f"   • Krishna entries created: {len(krishna_content)}")
    logger.info(f"   • Previous limited content (7 verses) replaced with comprehensive selection")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    print("\n🕉️ Krishna's comprehensive wisdom has been successfully integrated!")
    print("The system now contains authentic Bhagavad Gita teachings instead of limited verses.")
