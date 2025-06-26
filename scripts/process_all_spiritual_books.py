#!/usr/bin/env python3
"""
Complete Spiritual Scriptures Processing Pipeline
Processes Bhagavad Gita and Sri Isopanisad (Srimad Bhagavatam later)
Creates clean RAG chunks and manages scripture registry
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpiritualScripturesProcessor:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.sources_dir = self.base_dir / "data" / "sources"
        self.output_dir = self.sources_dir
        self.registry_file = self.sources_dir / "scriptures_registry.json"
        
        # Scripture configurations (Srimad Bhagavatam excluded for now due to donor spam)
        self.scriptures_config = {
            "bhagavad_gita": {
                "title": "Bhagavad Gita As It Is",
                "author": "A.C. Bhaktivedanta Swami Prabhupada",
                "source_file": "raw-bg/bhagavad_gita_complete.json",
                "output_file": "bhagavad_gita_clean.jsonl",
                "scripture_code": "bg",
                "type": "dialogue"
            },
            "sri_isopanisad": {
                "title": "Sri Isopanisad",
                "author": "A.C. Bhaktivedanta Swami Prabhupada",
                "source_file": "raw-iso/sri_isopanisad_complete.json", 
                "output_file": "sri_isopanisad_clean.jsonl",
                "scripture_code": "iso",
                "type": "upanisad"
            }
            # "srimad_bhagavatam": Excluded due to donor spam - will be added later after cleaning
        }
        
    def clean_text(self, text: str) -> str:
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

    def process_verse(self, verse_data: Dict[str, Any], scripture_code: str, scripture_title: str, chapter_num: int) -> List[Dict[str, Any]]:
        """Process a single verse into multiple RAG chunks."""
        chunks = []
        
        # Handle different verse numbering formats
        verse_ref = (
            verse_data.get('verse_number') or 
            verse_data.get('mantra_number') or 
            f'{scripture_code}.{chapter_num}.?'
        )
        
        # Clean all text fields - handle both verse and mantra formats
        sanskrit = self.clean_text(
            verse_data.get('sanskrit_verse') or 
            verse_data.get('sanskrit_mantra') or ''
        )
        translation = self.clean_text(verse_data.get('translation', ''))
        purport = self.clean_text(verse_data.get('purport', ''))
        synonyms = self.clean_text(verse_data.get('synonyms', ''))
        
        # Chunk 1: Verse-only (Sanskrit + translation)
        if sanskrit or translation:
            content = f"Verse {verse_ref}:\n\n"
            if sanskrit:
                content += f"Sanskrit: {sanskrit}\n\n"
            if translation:
                content += f"Translation: {translation}"
            
            chunks.append({
                "id": f"{scripture_code}_{verse_ref.replace(' ', '_').replace('.', '_')}_verse",
                "scripture": scripture_title,
                "chapter": chapter_num,
                "verse": verse_ref,
                "content_type": "verse",
                "sanskrit": sanskrit,
                "translation": translation,
                "content": content,
                "metadata": {
                    "verse_citation": verse_ref,
                    "scripture_title": scripture_title,
                    "chapter_number": chapter_num,
                    "has_sanskrit": bool(sanskrit),
                    "has_translation": bool(translation),
                    "content_focus": "verse_text"
                }
            })
        
        # Chunk 2: Commentary-only (translation + purport)
        if translation or purport:
            content = f"Verse {verse_ref} Commentary:\n\n"
            if translation:
                content += f"Translation: {translation}\n\n"
            if purport:
                content += f"Purport: {purport}"
            
            chunks.append({
                "id": f"{scripture_code}_{verse_ref.replace(' ', '_').replace('.', '_')}_commentary",
                "scripture": scripture_title,
                "chapter": chapter_num,
                "verse": verse_ref,
                "content_type": "commentary",
                "translation": translation,
                "purport": purport,
                "content": content,
                "metadata": {
                    "verse_citation": verse_ref,
                    "scripture_title": scripture_title,
                    "chapter_number": chapter_num,
                    "has_translation": bool(translation),
                    "has_purport": bool(purport),
                    "content_focus": "commentary"
                }
            })
        
        # Chunk 3: Complete verse (all elements)
        if sanskrit or translation or purport or synonyms:
            content = f"Verse {verse_ref}:\n\n"
            if sanskrit:
                content += f"Sanskrit: {sanskrit}\n\n"
            if translation:
                content += f"Translation: {translation}\n\n"
            if synonyms:
                content += f"Word meanings: {synonyms}\n\n"
            if purport:
                content += f"Purport: {purport}"
            
            chunks.append({
                "id": f"{scripture_code}_{verse_ref.replace(' ', '_').replace('.', '_')}_complete",
                "scripture": scripture_title,
                "chapter": chapter_num,
                "verse": verse_ref,
                "content_type": "complete",
                "sanskrit": sanskrit,
                "translation": translation,
                "purport": purport,
                "synonyms": synonyms,
                "content": content,
                "metadata": {
                    "verse_citation": verse_ref,
                    "scripture_title": scripture_title,
                    "chapter_number": chapter_num,
                    "has_sanskrit": bool(sanskrit),
                    "has_translation": bool(translation),
                    "has_purport": bool(purport),
                    "has_synonyms": bool(synonyms),
                    "content_focus": "complete"
                }
            })
        
        return chunks

    def process_scripture(self, scripture_id: str) -> Dict[str, Any]:
        """Process a single scripture and return statistics."""
        config = self.scriptures_config[scripture_id]
        source_path = self.sources_dir / config["source_file"]
        output_path = self.output_dir / config["output_file"]
        
        logger.info(f"Processing {config['title']}...")
        
        if not source_path.exists():
            logger.error(f"Source file not found: {source_path}")
            return {"status": "error", "message": "Source file not found"}
        
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading {source_path}: {e}")
            return {"status": "error", "message": str(e)}
        
        all_chunks = []
        total_verses = 0
        chapters_processed = 0
        
        # Handle different JSON structures
        if isinstance(data, dict) and 'chapters' in data:
            # Bhagavad Gita structure: chapters as dict
            chapters_dict = data['chapters']
            chapters = []
            for chapter_key, chapter_data in chapters_dict.items():
                if isinstance(chapter_data, dict):
                    chapters.append(chapter_data)
        elif isinstance(data, dict) and 'mantras' in data:
            # Sri Isopanisad structure: mantras at root level
            chapters = [{
                'chapter_number': 1,
                'title': data.get('title', 'Sri Isopanisad'),
                'verses': data['mantras']  # Map mantras to verses for consistent processing
            }]
        elif isinstance(data, list):
            chapters = data
        else:
            chapters = [data]  # Single chapter
        
        for chapter_data in chapters:
            if isinstance(chapter_data, str):
                continue  # Skip string entries
            chapter_num = chapter_data.get('chapter_number', chapters_processed + 1)
            verses = chapter_data.get('verses', [])
            
            logger.info(f"Processing Chapter {chapter_num}: {chapter_data.get('title', 'Unknown')} ({len(verses)} verses)")
            
            for verse_data in verses:
                chunks = self.process_verse(verse_data, config['scripture_code'], config['title'], chapter_num)
                all_chunks.extend(chunks)
                total_verses += 1
            
            chapters_processed += 1
        
        # Write processed chunks
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
        
        logger.info(f"✅ Successfully processed {total_verses} verses into {len(all_chunks)} chunks")
        logger.info(f"✅ Clean {config['title']} data saved to: {output_path}")
        
        return {
            "status": "success",
            "chapters_processed": chapters_processed,
            "verses_processed": total_verses,
            "chunks_created": len(all_chunks),
            "output_file": str(output_path),
            "processed_date": datetime.now().isoformat()
        }

    def load_registry(self) -> Dict[str, Any]:
        """Load the scriptures registry."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading registry: {e}")
        
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "scriptures": {}
        }

    def save_registry(self, registry: Dict[str, Any]):
        """Save the scriptures registry."""
        registry["last_updated"] = datetime.now().isoformat()
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

    def update_scripture_registry(self, scripture_id: str, processing_result: Dict[str, Any]):
        """Update the registry with scripture processing information."""
        registry = self.load_registry()
        config = self.scriptures_config[scripture_id]
        
        scripture_entry = {
            "scripture_id": scripture_id,
            "title": config["title"],
            "author": config["author"],
            "type": config["type"],
            "language": "Sanskrit/English",
            "scripture_code": config["scripture_code"],
            "source_format": "raw_json",
            "embedding_model": "text-embedding-ada-002",  # Default, can be updated later
            "status": "processed" if processing_result["status"] == "success" else "error",
            "metadata_enriched": False,  # To be updated when web scraping is added
            "web_sources": [],  # To be populated with web scraping
            **processing_result
        }
        
        registry["scriptures"][scripture_id] = scripture_entry
        self.save_registry(registry)
        logger.info(f"Updated registry for {scripture_id}")

    def process_all_scriptures(self):
        """Process all configured scriptures."""
        logger.info("🚀 Starting spiritual scriptures processing pipeline...")
        
        total_scriptures = len(self.scriptures_config)
        successful_scriptures = 0
        
        for scripture_id in self.scriptures_config:
            logger.info(f"\n� Processing scripture {successful_scriptures + 1}/{total_scriptures}: {scripture_id}")
            
            result = self.process_scripture(scripture_id)
            self.update_scripture_registry(scripture_id, result)
            
            if result["status"] == "success":
                successful_scriptures += 1
                logger.info(f"✅ {scripture_id} processed successfully")
            else:
                logger.error(f"❌ {scripture_id} processing failed: {result.get('message', 'Unknown error')}")
        
        logger.info(f"\n🎉 Pipeline complete! {successful_scriptures}/{total_scriptures} scriptures processed successfully")
        logger.info(f"📊 Registry saved to: {self.registry_file}")
        
        return successful_scriptures == total_scriptures

    def get_processing_summary(self) -> Dict[str, Any]:
        """Get a summary of all processed scriptures."""
        registry = self.load_registry()
        
        total_chunks = 0
        total_verses = 0
        scriptures_summary = []
        
        for scripture_id, scripture_data in registry.get("scriptures", {}).items():
            if scripture_data.get("status") == "success":
                total_chunks += scripture_data.get("chunks_created", 0)
                total_verses += scripture_data.get("verses_processed", 0)
                
                scriptures_summary.append({
                    "title": scripture_data.get("title"),
                    "chapters": scripture_data.get("chapters_processed", 0),
                    "verses": scripture_data.get("verses_processed", 0),
                    "chunks": scripture_data.get("chunks_created", 0)
                })
        
        return {
            "total_scriptures": len(registry.get("scriptures", {})),
            "total_verses": total_verses,
            "total_chunks": total_chunks,
            "scriptures": scriptures_summary,
            "registry_path": str(self.registry_file)
        }

def main():
    """Main entry point."""
    base_dir = "/Users/vedprakashmishra/vimarsh"
    processor = SpiritualScripturesProcessor(base_dir)
    
    # Process all scriptures
    success = processor.process_all_scriptures()
    
    # Show summary
    summary = processor.get_processing_summary()
    
    print("\n" + "="*60)
    print("📋 PROCESSING SUMMARY")
    print("="*60)
    print(f"Total Scriptures: {summary['total_scriptures']}")
    print(f"Total Verses: {summary['total_verses']}")
    print(f"Total RAG Chunks: {summary['total_chunks']}")
    print(f"Registry: {summary['registry_path']}")
    print("\nScriptures processed:")
    for scripture in summary['scriptures']:
        print(f"  • {scripture['title']}: {scripture['chapters']} chapters, {scripture['verses']} verses, {scripture['chunks']} chunks")
    
    if success:
        print("\n🎉 All scriptures processed successfully!")
        print("📝 Next steps:")
        print("   1. Generate embeddings for vector storage")
        print("   2. Upload to Azure Cosmos DB")
        print("   3. Set up web scraping for metadata enrichment")
        print("   4. Clean and process Srimad Bhagavatam later")
    else:
        print("\n⚠️ Some scriptures failed to process. Check logs for details.")

if __name__ == "__main__":
    main()
