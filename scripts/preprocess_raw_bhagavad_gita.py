#!/usr/bin/env python3
"""
Preprocess raw Bhagavad Gita JSON to create clean RAG-optimized format
for ingestion into Cosmos DB. Removes donor acknowledgment spam while
preserving Sanskrit, translation, and purport content.

Input: raw-bg/bhagavad_gita_complete.json
Output: sources/bhagavad_gita_clean.jsonl (for RAG ingestion)
"""

import json
import re
import os
from typing import Dict, List, Any

def clean_text(text: str) -> str:
    """Remove donor acknowledgment spam and normalize text."""
    if not text:
        return ""
    
    # First, remove everything starting from "TEXT" pattern (which marks start of spam)
    # This catches patterns like "Chapter TwoTEXT 2 DonateThanks to..."
    text = re.sub(r'TEXT\s+\d+.*', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Also remove standalone chapter markers that might remain
    text = re.sub(r'Chapter\s+(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen|Fourteen|Fifteen|Sixteen|Seventeen|Eighteen)\s*', '', text, flags=re.IGNORECASE)
    
    # Remove other donor spam patterns
    spam_patterns = [
        r'DonateThanks to.*',
        r'Donate\s*Thanks to.*', 
        r'His Divine Grace A\.C\. Bhaktivedanta.*',
        r'Content used with permission.*',
        r'International Society for Krishna Consciousness.*'
    ]
    
    cleaned = text
    for pattern in spam_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove excessive repetition - split into sentences and deduplicate
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    unique_sentences = []
    seen_sentences = set()
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and sentence not in seen_sentences:
            unique_sentences.append(sentence)
            seen_sentences.add(sentence)
    
    # Rejoin sentences
    result = ' '.join(unique_sentences).strip()
    
    # Clean up excessive whitespace
    result = re.sub(r'\s+', ' ', result)
    
    return result

def create_rag_chunks(verse_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create RAG-optimized chunks from a single verse."""
    verse_num = verse_data.get('verse_number', '')
    chapter_match = re.match(r'Bg\. (\d+)\.', verse_num)
    chapter_num = int(chapter_match.group(1)) if chapter_match else 0
    
    sanskrit = verse_data.get('sanskrit_verse', '').strip()
    translation = clean_text(verse_data.get('translation', ''))
    purport = clean_text(verse_data.get('purport', ''))
    synonyms = clean_text(verse_data.get('synonyms', ''))
    
    chunks = []
    
    # Strategy 1: Verse-focused chunk (Sanskrit + Translation)
    if sanskrit and translation:
        verse_chunk = {
            'id': f"bg_{verse_num.lower().replace(' ', '_').replace('.', '_')}_verse",
            'book': 'Bhagavad Gita',
            'chapter': chapter_num,
            'verse': verse_num,
            'content_type': 'verse',
            'sanskrit': sanskrit,
            'translation': translation,
            'content': f"Verse {verse_num}:\n\nSanskrit: {sanskrit}\n\nTranslation: {translation}",
            'metadata': {
                'verse_citation': verse_num,
                'book_title': 'Bhagavad Gita',
                'chapter_number': chapter_num,
                'has_sanskrit': True,
                'has_translation': True,
                'content_focus': 'verse_text'
            }
        }
        chunks.append(verse_chunk)
    
    # Strategy 2: Commentary-focused chunk (Translation + Purport)
    if translation and purport:
        commentary_chunk = {
            'id': f"bg_{verse_num.lower().replace(' ', '_').replace('.', '_')}_commentary",
            'book': 'Bhagavad Gita',
            'chapter': chapter_num,
            'verse': verse_num,
            'content_type': 'commentary',
            'translation': translation,
            'purport': purport,
            'content': f"Verse {verse_num} Commentary:\n\nTranslation: {translation}\n\nPurport: {purport}",
            'metadata': {
                'verse_citation': verse_num,
                'book_title': 'Bhagavad Gita',
                'chapter_number': chapter_num,
                'has_translation': True,
                'has_purport': True,
                'content_focus': 'commentary'
            }
        }
        chunks.append(commentary_chunk)
    
    # Strategy 3: Complete verse chunk (all content combined)
    all_content_parts = []
    if sanskrit:
        all_content_parts.append(f"Sanskrit: {sanskrit}")
    if translation:
        all_content_parts.append(f"Translation: {translation}")
    if synonyms:
        all_content_parts.append(f"Word meanings: {synonyms}")
    if purport:
        all_content_parts.append(f"Purport: {purport}")
    
    if len(all_content_parts) >= 2:  # At least Sanskrit/translation or translation/purport
        complete_chunk = {
            'id': f"bg_{verse_num.lower().replace(' ', '_').replace('.', '_')}_complete",
            'book': 'Bhagavad Gita',
            'chapter': chapter_num,
            'verse': verse_num,
            'content_type': 'complete',
            'sanskrit': sanskrit,
            'translation': translation,
            'purport': purport,
            'synonyms': synonyms,
            'content': f"Verse {verse_num}:\n\n" + '\n\n'.join(all_content_parts),
            'metadata': {
                'verse_citation': verse_num,
                'book_title': 'Bhagavad Gita',
                'chapter_number': chapter_num,
                'has_sanskrit': bool(sanskrit),
                'has_translation': bool(translation),
                'has_purport': bool(purport),
                'has_synonyms': bool(synonyms),
                'content_focus': 'complete'
            }
        }
        chunks.append(complete_chunk)
    
    return chunks

def process_bhagavad_gita():
    """Process the raw Bhagavad Gita JSON and create clean JSONL output."""
    
    # Input and output paths
    raw_file = '/Users/vedprakashmishra/vimarsh/data/sources/raw-bg/bhagavad_gita_complete.json'
    output_file = '/Users/vedprakashmishra/vimarsh/data/sources/bhagavad_gita_clean.jsonl'
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print(f"Loading raw Bhagavad Gita from: {raw_file}")
    
    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    all_chunks = []
    processed_verses = 0
    
    # Process each chapter
    chapters = raw_data.get('chapters', {})
    for chapter_key, chapter_data in chapters.items():
        chapter_num = chapter_data.get('chapter_number', 0)
        chapter_title = chapter_data.get('title', '')
        verses = chapter_data.get('verses', [])
        
        print(f"Processing Chapter {chapter_num}: {chapter_title} ({len(verses)} verses)")
        
        for verse_data in verses:
            try:
                verse_chunks = create_rag_chunks(verse_data)
                all_chunks.extend(verse_chunks)
                processed_verses += 1
            except Exception as e:
                verse_num = verse_data.get('verse_number', 'unknown')
                print(f"Error processing verse {verse_num}: {e}")
    
    # Write output JSONL file
    print(f"Writing {len(all_chunks)} chunks to: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
    
    print(f"✅ Successfully processed {processed_verses} verses into {len(all_chunks)} RAG chunks")
    print(f"✅ Clean Bhagavad Gita data saved to: {output_file}")
    
    # Show sample of output
    print(f"\n📋 Sample chunks created:")
    for i, chunk in enumerate(all_chunks[:3]):
        print(f"{i+1}. ID: {chunk['id']}")
        print(f"   Type: {chunk['content_type']}")
        print(f"   Verse: {chunk['verse']}")
        print(f"   Content preview: {chunk['content'][:100]}...")
        print()

if __name__ == "__main__":
    process_bhagavad_gita()
