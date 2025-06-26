#!/usr/bin/env python3
"""
Preprocess raw JSON texts for RAG ingestion into Cosmos DB.

This script takes the raw JSON format texts (which contain clean Sanskrit, translations, 
and purports but also donor spam) and processes them into clean, citation-friendly 
chunks suitable for RAG ingestion.

Key features:
- Removes donor spam while preserving spiritual content
- Creates proper verse citations (e.g., "Bg. 1.1", "SB 1.1.1")
- Structures content for optimal RAG retrieval
- Supports both verse-level and paragraph-level chunking
- Maintains spiritual context and grounding
"""

import json
import re
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configuration
RAW_DATA_DIR = "/Users/vedprakashmishra/vimarsh/data/sources"
OUTPUT_DIR = "/Users/vedprakashmishra/vimarsh/data/sources/processed_clean"

# Patterns to identify and remove donor spam
DONOR_SPAM_PATTERNS = [
    r"DonateThanks to.*?site\.",
    r"His Divine Grace A\.C\. Bhaktivedanta Swami.*?policy",
    r"Content used with permission.*?policy",
    r"Thanks to.*?supporting.*?site",
    r"Donate.*?Thanks to.*?site",
    # Pattern for repeated blocks
    r"(.{50,200})\1{2,}",  # Detects text repeated 3+ times
]

# Books configuration
BOOKS_CONFIG = {
    "bhagavad_gita": {
        "raw_file": "raw-bg/bhagavad_gita_complete.json",
        "title": "Bhagavad Gita",
        "citation_prefix": "Bg",
        "output_file": "bhagavad_gita_clean.jsonl"
    },
    # Will add other books once we have their raw JSON format
}

def clean_text(text: str) -> str:
    """Remove donor spam and clean up text."""
    if not text:
        return ""
    
    # Remove donor spam patterns
    for pattern in DONOR_SPAM_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
    text = re.sub(r'\n\s*\n', '\n', text)  # Multiple newlines to single
    text = text.strip()
    
    return text

def extract_verse_data(verse: Dict[str, Any], book_config: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Extract and clean verse data."""
    verse_number = verse.get('verse_number', '')
    if not verse_number:
        return None
    
    # Extract components
    sanskrit = clean_text(verse.get('sanskrit_verse', ''))
    translation = clean_text(verse.get('translation', ''))
    purport = clean_text(verse.get('purport', ''))
    synonyms = clean_text(verse.get('synonyms', ''))
    
    # Skip if essential content is missing
    if not (sanskrit or translation):
        return None
    
    # Create citation
    citation = verse_number
    
    return {
        'id': f"{book_config['citation_prefix'].lower()}_{verse_number.replace('.', '_').replace(' ', '_')}",
        'book': book_config['title'],
        'citation': citation,
        'verse_number': verse_number,
        'sanskrit': sanskrit,
        'translation': translation,
        'purport': purport,
        'synonyms': synonyms,
        'content_type': 'verse',
        'chunk_size': len(f"{sanskrit} {translation} {purport}".split()),
    }

def create_chunked_content(verse_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create different chunk sizes for optimal RAG retrieval."""
    chunks = []
    base_id = verse_data['id']
    citation = verse_data['citation']
    book = verse_data['book']
    
    # Verse-only chunk (Sanskrit + Translation)
    if verse_data['sanskrit'] or verse_data['translation']:
        verse_content = []
        if verse_data['sanskrit']:
            verse_content.append(f"Sanskrit: {verse_data['sanskrit']}")
        if verse_data['translation']:
            verse_content.append(f"Translation: {verse_data['translation']}")
        
        chunks.append({
            'id': f"{base_id}_verse",
            'book': book,
            'citation': citation,
            'content': "\n".join(verse_content),
            'content_type': 'verse_only',
            'chunk_size': len(" ".join(verse_content).split()),
            'contains_sanskrit': bool(verse_data['sanskrit']),
            'contains_translation': bool(verse_data['translation']),
            'contains_purport': False,
        })
    
    # Complete verse chunk (Sanskrit + Translation + Purport)
    complete_content = []
    if verse_data['sanskrit']:
        complete_content.append(f"Sanskrit: {verse_data['sanskrit']}")
    if verse_data['translation']:
        complete_content.append(f"Translation: {verse_data['translation']}")
    if verse_data['purport']:
        complete_content.append(f"Purport: {verse_data['purport']}")
    
    if complete_content:
        chunks.append({
            'id': f"{base_id}_complete",
            'book': book,
            'citation': citation,
            'content': "\n".join(complete_content),
            'content_type': 'complete_verse',
            'chunk_size': len(" ".join(complete_content).split()),
            'contains_sanskrit': bool(verse_data['sanskrit']),
            'contains_translation': bool(verse_data['translation']),
            'contains_purport': bool(verse_data['purport']),
        })
    
    # Purport-only chunk (for commentary-focused searches)
    if verse_data['purport']:
        chunks.append({
            'id': f"{base_id}_purport",
            'book': book,
            'citation': citation,
            'content': f"Commentary on {citation}: {verse_data['purport']}",
            'content_type': 'purport_only',
            'chunk_size': len(verse_data['purport'].split()),
            'contains_sanskrit': False,
            'contains_translation': False,
            'contains_purport': True,
        })
    
    return chunks

def process_book(book_key: str, book_config: Dict[str, str], dry_run: bool = False) -> Dict[str, int]:
    """Process a single book."""
    print(f"\n📖 Processing {book_config['title']}...")
    
    # Load raw JSON
    raw_file_path = os.path.join(RAW_DATA_DIR, book_config['raw_file'])
    if not os.path.exists(raw_file_path):
        print(f"❌ Raw file not found: {raw_file_path}")
        return {'verses': 0, 'chunks': 0, 'chapters': 0}
    
    with open(raw_file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Process chapters and verses
    all_chunks = []
    chapters_processed = 0
    verses_processed = 0
    
    chapters = raw_data.get('chapters', {})
    for chapter_num, chapter_data in chapters.items():
        print(f"  📄 Processing Chapter {chapter_num}...")
        chapters_processed += 1
        
        verses = chapter_data.get('verses', [])
        for verse in verses:
            verse_data = extract_verse_data(verse, book_config)
            if verse_data:
                verses_processed += 1
                chunks = create_chunked_content(verse_data)
                all_chunks.extend(chunks)
                
                if verses_processed % 50 == 0:
                    print(f"    ✅ Processed {verses_processed} verses...")
    
    print(f"  📊 Total: {chapters_processed} chapters, {verses_processed} verses, {len(all_chunks)} chunks")
    
    # Save output
    if not dry_run:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, book_config['output_file'])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        print(f"  💾 Saved to: {output_file}")
    else:
        print(f"  🔍 DRY RUN: Would save {len(all_chunks)} chunks to {book_config['output_file']}")
    
    return {
        'chapters': chapters_processed,
        'verses': verses_processed,
        'chunks': len(all_chunks)
    }

def main():
    """Main processing function."""
    print("🚀 Starting text preprocessing for RAG ingestion...")
    print(f"📂 Raw data directory: {RAW_DATA_DIR}")
    print(f"📂 Output directory: {OUTPUT_DIR}")
    
    # Check if we should do a dry run first
    dry_run = input("\n❓ Do you want to run a dry-run first? (y/N): ").lower().startswith('y')
    
    total_stats = {'chapters': 0, 'verses': 0, 'chunks': 0}
    
    for book_key, book_config in BOOKS_CONFIG.items():
        try:
            stats = process_book(book_key, book_config, dry_run=dry_run)
            for key, value in stats.items():
                total_stats[key] += value
        except Exception as e:
            print(f"❌ Error processing {book_config['title']}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📈 TOTAL SUMMARY:")
    print(f"  📚 Books processed: {len(BOOKS_CONFIG)}")
    print(f"  📄 Chapters: {total_stats['chapters']}")
    print(f"  📝 Verses: {total_stats['verses']}")
    print(f"  🧩 Chunks created: {total_stats['chunks']}")
    
    if dry_run:
        print(f"\n🔍 This was a DRY RUN. To actually process the files, run again and choose 'N' for dry-run.")
    else:
        print(f"\n✅ Processing complete! Clean files saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
