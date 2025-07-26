#!/usr/bin/env python3
"""
Enhanced Comprehensive Krishna Content Integration
==================================================

This script integrates both Bhagavad Gita and Sri Isopanisad content 
for Krishna's personality, providing complete Vedic wisdom coverage.

Author: Vimarsh AI System
Date: Current
Purpose: Fulfill user request to include Sri Isopanisad along with Bhagavad Gita
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_scripture_content(file_path: str, scripture_name: str) -> List[Dict[str, Any]]:
    """Load scripture content from JSONL file."""
    content = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        verse_data = json.loads(line.strip())
                        content.append(verse_data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parsing {scripture_name} line {line_num}: {e}")
                        continue
        
        logger.info(f"Loaded {len(content)} verses from {scripture_name}")
        return content
        
    except FileNotFoundError:
        logger.error(f"{scripture_name} file not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Error loading {scripture_name}: {e}")
        return []

def convert_gita_to_krishna_format(gita_verse: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Bhagavad Gita verse to Krishna personality format."""
    
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
        "tags": ["dharma", "spiritual_wisdom", "divine_teaching", "arjuna_dialogue", "bhagavad_gita"],
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

def convert_isopanisad_to_krishna_format(iso_verse: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Sri Isopanisad verse to Krishna personality format."""
    
    # Extract verse information
    verse_citation = iso_verse.get('verse', 'Unknown')
    chapter = iso_verse.get('chapter', 1)  # Isopanisad is single chapter
    sanskrit = iso_verse.get('sanskrit', '')
    translation = iso_verse.get('translation', '')
    content_type = iso_verse.get('content_type', 'verse')
    
    # Create comprehensive content text
    content_parts = []
    if sanskrit:
        content_parts.append(f"Sanskrit: {sanskrit}")
    if translation:
        content_parts.append(f"Translation: {translation}")
    
    # Add purport/commentary if available
    if 'purport' in iso_verse and iso_verse['purport']:
        content_parts.append(f"Purport: {iso_verse['purport']}")
    
    content_text = "\n\n".join(content_parts)
    
    # Create Krishna-formatted entry
    krishna_entry = {
        "id": f"krishna_iso_{verse_citation.lower().replace(' ', '_').replace('.', '_')}_{content_type}",
        "personality": "krishna",
        "content": content_text,
        "source": "Sri Isopanisad",
        "chapter": chapter,
        "verse": verse_citation,
        "citation": f"Sri Isopanisad {verse_citation}",
        "authority_level": "primary",
        "content_type": content_type,
        "tags": ["vedantic_wisdom", "upanishad", "supreme_truth", "divine_proprietorship", "sri_isopanisad"],
        "metadata": {
            "scripture_title": "Sri Isopanisad",
            "verse_citation": verse_citation,
            "chapter_number": chapter,
            "has_sanskrit": bool(sanskrit),
            "has_translation": bool(translation),
            "has_purport": 'purport' in iso_verse and bool(iso_verse.get('purport')),
            "content_focus": content_type,
            "original_id": iso_verse.get('id', '')
        }
    }
    
    return krishna_entry

def select_representative_gita_verses(gita_content: List[Dict[str, Any]], max_verses: int = 90) -> List[Dict[str, Any]]:
    """
    Select representative verses from the comprehensive Gita.
    Reduced to 90 to make room for Sri Isopanisad content.
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
    
    logger.info(f"Selected {len(selected_verses)} priority Gita verses")
    
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
    
    logger.info(f"Selected total of {len(selected_verses)} representative Gita verses")
    return selected_verses

def select_isopanisad_verses(iso_content: List[Dict[str, Any]], max_verses: int = 19) -> List[Dict[str, Any]]:
    """
    Select verses from Sri Isopanisad.
    Since it's only 18 verses + invocation, we can include most of them.
    """
    
    # Priority verses from Isopanisad (most essential teachings)
    priority_verses = [
        "Iso Invocation",  # Om purnam adah purnam idam - completeness teaching
        "Iso 1",          # Everything belongs to the Lord - proprietorship
        "Iso 2",          # One should live for hundred years
        "Iso 3",          # Demonic worlds for those who kill the soul
        "Iso 4",          # The Supreme Lord is everywhere
        "Iso 5",          # The Lord moves and moves not
        "Iso 6",          # One who sees everything in relation to the Supreme
        "Iso 7",          # When one sees all living entities as spiritual sparks
        "Iso 8",          # Such a person must be the most learned
        "Iso 9",          # Those who worship the unmanifested
        "Iso 10",         # Different results from material and spiritual knowledge
        "Iso 11",         # One should know both sambhuti and asambhuti
        "Iso 12",         # One who worships both vidya and avidya
        "Iso 15",         # O Lord, sustainer of all, remove the covering
        "Iso 16",         # O my Lord, You are the maintainer of the entire universe
        "Iso 17",         # Let this temporary body be burnt to ashes
        "Iso 18",         # O Lord, lead us from the unreal to the real
    ]
    
    # Filter to get complete verses (not just commentary)
    complete_verses = [v for v in iso_content if v.get('content_type') == 'complete']
    
    # Include priority verses first
    selected_verses = []
    priority_set = set(priority_verses)
    
    for verse in complete_verses:
        if verse.get('verse') in priority_set:
            selected_verses.append(verse)
            priority_set.remove(verse.get('verse'))
    
    # Add remaining verses if we have space
    for verse in complete_verses:
        if len(selected_verses) < max_verses and verse not in selected_verses:
            selected_verses.append(verse)
    
    logger.info(f"Selected {len(selected_verses)} Sri Isopanisad verses")
    return selected_verses

def combine_krishna_content(gita_content: List[Dict[str, Any]], iso_content: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Combine Bhagavad Gita and Sri Isopanisad content for Krishna personality."""
    
    # Select representative content
    selected_gita = select_representative_gita_verses(gita_content, max_verses=90)
    selected_iso = select_isopanisad_verses(iso_content, max_verses=19)
    
    # Convert to Krishna format
    krishna_content = []
    
    # Add Bhagavad Gita content
    for verse in selected_gita:
        krishna_entry = convert_gita_to_krishna_format(verse)
        krishna_content.append(krishna_entry)
    
    # Add Sri Isopanisad content
    for verse in selected_iso:
        krishna_entry = convert_isopanisad_to_krishna_format(verse)
        krishna_content.append(krishna_entry)
    
    # Statistics
    stats = {
        "gita_verses": len(selected_gita),
        "isopanisad_verses": len(selected_iso),
        "total_verses": len(krishna_content)
    }
    
    return krishna_content, stats

def backup_current_krishna_content(krishna_db_path: str) -> bool:
    """Create backup of current Krishna content."""
    try:
        backup_path = krishna_db_path.replace('.json', '_backup_before_enhanced_integration.json')
        
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
    """Update the Krishna database with enhanced content."""
    try:
        # Create backup first
        backup_current_krishna_content(krishna_db_path)
        
        # Write new comprehensive content
        with open(krishna_db_path, 'w', encoding='utf-8') as f:
            json.dump(new_content, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated Krishna database with {len(new_content)} enhanced verses")
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
        backup_path = spiritual_db_path.replace('.json', '_backup_before_enhanced_integration.json')
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
    """Main function to integrate enhanced Krishna content (Gita + Isopanisad)."""
    
    # Define paths
    current_dir = Path(__file__).parent.parent.parent  # Go up to workspace root
    gita_source_path = current_dir / "data" / "sources" / "bhagavad_gita_clean.jsonl"
    iso_source_path = current_dir / "data" / "sources" / "sri_isopanisad_clean.jsonl"
    krishna_db_path = current_dir / "backend" / "data" / "vimarsh-db" / "krishna-texts.json"
    spiritual_db_path = current_dir / "backend" / "data" / "vimarsh-db" / "spiritual-texts.json"
    
    logger.info("🕉️ Starting enhanced Krishna content integration (Gita + Isopanisad)")
    logger.info(f"Gita Source: {gita_source_path}")
    logger.info(f"Isopanisad Source: {iso_source_path}")
    logger.info(f"Krishna DB: {krishna_db_path}")
    logger.info(f"Spiritual DB: {spiritual_db_path}")
    
    # Step 1: Load both scripture contents
    logger.info("📚 Loading comprehensive scripture content...")
    gita_content = load_scripture_content(str(gita_source_path), "Bhagavad Gita")
    iso_content = load_scripture_content(str(iso_source_path), "Sri Isopanisad")
    
    if not gita_content:
        logger.error("❌ Failed to load Bhagavad Gita content")
        return False
    
    if not iso_content:
        logger.error("❌ Failed to load Sri Isopanisad content")
        return False
    
    # Step 2: Combine and convert content
    logger.info("🔄 Combining Gita and Isopanisad content for Krishna personality...")
    krishna_content, stats = combine_krishna_content(gita_content, iso_content)
    
    # Step 3: Update Krishna database
    logger.info("💾 Updating Krishna database with enhanced content...")
    if not update_krishna_database(krishna_content, str(krishna_db_path)):
        logger.error("❌ Failed to update Krishna database")
        return False
    
    # Step 4: Update main spiritual texts database
    logger.info("🔄 Updating main spiritual texts database...")
    if not update_spiritual_texts_db(krishna_content, str(spiritual_db_path)):
        logger.error("❌ Failed to update spiritual texts database")
        return False
    
    # Success summary
    logger.info("✅ Enhanced Krishna content integration completed successfully!")
    logger.info("📊 Statistics:")
    logger.info(f"   • Bhagavad Gita verses: {stats['gita_verses']}")
    logger.info(f"   • Sri Isopanisad verses: {stats['isopanisad_verses']}")
    logger.info(f"   • Total Krishna entries: {stats['total_verses']}")
    logger.info("   • Enhanced with Vedantic philosophy from Isopanisad")
    logger.info("   • Comprehensive coverage: Practical + Philosophical wisdom")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    print("\n🕉️ Krishna's enhanced wisdom has been successfully integrated!")
    print("The system now contains both Bhagavad Gita and Sri Isopanisad teachings!")
    print("Complete Vedic wisdom: Practical guidance + Philosophical foundation! 🙏")
