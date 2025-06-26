#!/usr/bin/env python3
"""
Load Weighted RAG Texts to Cosmos DB - Task 8.8
Vimarsh AI Agent Implementation

This script loads pre-processed weighted RAG format texts (JSONL) into production Cosmos DB
optimized for spiritual guidance applications.
"""

import os
import sys
import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from sentence_transformers import SentenceTransformer
import argparse

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from rag.storage_factory import get_vector_storage
from rag.cosmos_vector_search import SpiritualTextChunk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeightedTextLoader:
    """
    Loads pre-processed weighted RAG format texts into Cosmos DB.
    Optimized for spiritual texts with commentary focus.
    """
    
    def __init__(self):
        """Initialize the weighted text loader."""
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_storage = None
        self.stats = {
            'files_processed': 0,
            'total_verses': 0,
            'successful_loads': 0,
            'failed_loads': 0,
            'books': {}
        }
    
    async def initialize_storage(self):
        """Initialize vector storage connection."""
        logger.info("🔌 Initializing vector storage connection...")
        self.vector_storage = get_vector_storage()
        logger.info(f"✅ Vector storage initialized: {type(self.vector_storage).__name__}")
    
    def load_jsonl_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Load a JSONL file and return list of verse objects.
        
        Args:
            file_path: Path to the JSONL file
            
        Returns:
            List of verse dictionaries
        """
        verses = []
        logger.info(f"📖 Loading {file_path.name}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        verse_data = json.loads(line)
                        verses.append(verse_data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️  Invalid JSON on line {line_num}: {e}")
                        continue
            
            logger.info(f"✅ Loaded {len(verses)} verses from {file_path.name}")
            return verses
            
        except Exception as e:
            logger.error(f"❌ Failed to load {file_path.name}: {e}")
            return []
    
    def create_spiritual_chunk(self, verse_data: Dict[str, Any], source_book: str, file_path: Path) -> SpiritualTextChunk:
        """
        Convert verse data to SpiritualTextChunk for Cosmos DB.
        
        Args:
            verse_data: Verse data from JSONL
            source_book: Name of the source book
            file_path: Path to the source file (to determine variant type)
            
        Returns:
            SpiritualTextChunk ready for storage
        """
        # Extract verse reference
        verse_ref = verse_data.get('verse', 'Unknown')
        chapter = verse_data.get('chapter', 'Unknown')
        
        # Use the weighted content (commentary-focused)
        content = verse_data.get('content', '')
        
        # Extract Sanskrit terms from the content
        sanskrit_terms = self.extract_sanskrit_terms(content)
        
        # Determine spiritual theme
        spiritual_theme = self.determine_spiritual_theme(content, verse_ref)
        
        # Determine variant type from filename
        variant_type = 'commentary_focused' if 'commentary_focused' in file_path.name else 'balanced'
        
        # Create unique ID including variant type
        chunk_id = f"{source_book.lower()}_{variant_type}_{chapter}_{verse_ref}".replace(' ', '_').replace('.', '_')
        
        # Generate embedding
        embedding = self.embedding_model.encode(content).tolist()
        
        return SpiritualTextChunk(
            id=chunk_id,
            text=content,
            source=f"{source_book} {chapter}.{verse_ref} ({variant_type})",
            chapter=str(chapter),
            verse=str(verse_ref),
            sanskrit_terms=sanskrit_terms,
            embedding=embedding,
            spiritual_theme=spiritual_theme,
            dharmic_context=self.determine_dharmic_context(content)
        )
    
    def extract_sanskrit_terms(self, content: str) -> List[str]:
        """Extract Sanskrit terms from content."""
        import re
        
        # Look for capitalized Sanskrit terms and transliterations
        sanskrit_terms = []
        
        # Common patterns for Sanskrit terms
        patterns = [
            r'\b[A-Z][a-z]*-[a-z]+\b',  # Krishna-consciousness, etc.
            r'\b[A-Z][a-z]*ā[a-z]*\b',   # Terms with ā
            r'\b[A-Z][a-z]*ī[a-z]*\b',   # Terms with ī
            r'\b[A-Z][a-z]*ū[a-z]*\b',   # Terms with ū
            r'\bKṛṣṇa\b', r'\bViṣṇu\b', r'\bBrahman\b',  # Common terms
            r'\bdharma\b', r'\bkarma\b', r'\byoga\b',
            r'\bArjuna\b', r'\bBhagavān\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            sanskrit_terms.extend([match for match in matches if len(match) > 2])
        
        # Remove duplicates and return
        return list(set(sanskrit_terms))
    
    def determine_spiritual_theme(self, content: str, verse_ref: str) -> str:
        """Determine the spiritual theme of the content."""
        content_lower = content.lower()
        
        # Theme mapping based on content analysis
        if any(term in content_lower for term in ['duty', 'dharma', 'righteousness']):
            return 'dharma'
        elif any(term in content_lower for term in ['devotion', 'bhakti', 'love', 'surrender']):
            return 'bhakti'
        elif any(term in content_lower for term in ['knowledge', 'wisdom', 'understanding', 'jñāna']):
            return 'jnana'
        elif any(term in content_lower for term in ['action', 'karma', 'work', 'activity']):
            return 'karma'
        elif any(term in content_lower for term in ['meditation', 'yoga', 'mind', 'consciousness']):
            return 'yoga'
        elif any(term in content_lower for term in ['soul', 'ātmā', 'eternal', 'spiritual']):
            return 'atma'
        else:
            return 'general'
    
    def determine_dharmic_context(self, content: str) -> str:
        """Determine the dharmic context."""
        content_lower = content.lower()
        
        if any(term in content_lower for term in ['battlefield', 'war', 'arjuna', 'kuru']):
            return 'battlefield_guidance'
        elif any(term in content_lower for term in ['family', 'household', 'society']):
            return 'social_dharma'
        elif any(term in content_lower for term in ['teacher', 'student', 'learning']):
            return 'educational'
        elif any(term in content_lower for term in ['supreme', 'absolute', 'transcendent']):
            return 'transcendental'
        else:
            return 'universal'
    
    async def load_book(self, file_path: Path) -> bool:
        """
        Load a complete book into Cosmos DB.
        
        Args:
            file_path: Path to the JSONL file
            
        Returns:
            True if successful, False otherwise
        """
        book_name = self.determine_book_name(file_path.name)
        logger.info(f"📚 Loading {book_name}...")
        
        # Load verses from JSONL
        verses = self.load_jsonl_file(file_path)
        if not verses:
            logger.error(f"❌ No verses loaded from {file_path.name}")
            return False
        
        # Process each verse
        chunks_to_load = []
        for verse_data in verses:
            try:
                chunk = self.create_spiritual_chunk(verse_data, book_name, file_path)
                chunks_to_load.append(chunk)
            except Exception as e:
                logger.warning(f"⚠️  Failed to process verse {verse_data.get('verse', 'unknown')}: {e}")
                self.stats['failed_loads'] += 1
        
        # Load chunks into Cosmos DB
        logger.info(f"⬆️  Loading {len(chunks_to_load)} chunks for {book_name}...")
        
        successful_loads = 0
        for chunk in chunks_to_load:
            try:
                await self.vector_storage.add_chunk(chunk)
                successful_loads += 1
            except Exception as e:
                logger.warning(f"⚠️  Failed to load chunk {chunk.id}: {e}")
                self.stats['failed_loads'] += 1
        
        # Update statistics
        self.stats['files_processed'] += 1
        self.stats['total_verses'] += len(verses)
        self.stats['successful_loads'] += successful_loads
        self.stats['books'][book_name] = {
            'verses': len(verses),
            'loaded': successful_loads,
            'failed': len(chunks_to_load) - successful_loads
        }
        
        success_rate = (successful_loads / len(chunks_to_load) * 100) if chunks_to_load else 0
        logger.info(f"✅ {book_name}: {successful_loads}/{len(chunks_to_load)} chunks loaded ({success_rate:.1f}%)")
        
        return success_rate >= 80
    
    def determine_book_name(self, filename: str) -> str:
        """Determine book name from filename."""
        filename_lower = filename.lower()
        
        if 'bhagavad' in filename_lower or 'gita' in filename_lower:
            return 'Bhagavad Gita'
        elif 'bhagavatam' in filename_lower or 'srimad' in filename_lower:
            return 'Srimad Bhagavatam'
        elif 'sri_isopanisad' in filename_lower or 'isopanisad' in filename_lower:
            return 'Śrī Īśopaniṣad'
        else:
            return filename.replace('.jsonl', '').replace('_', ' ').title()
    
    async def validate_loading(self) -> bool:
        """Validate that the loading was successful."""
        logger.info("🔍 Validating loaded data...")
        
        # Test vector search
        test_queries = [
            "What is dharma?",
            "How to control the mind?",
            "What is devotion to Krishna?"
        ]
        
        for query in test_queries:
            try:
                results = await self.vector_storage.search(query, top_k=3)
                if results:
                    logger.info(f"✅ Search test '{query}': {len(results)} results")
                    # Log first result for verification
                    logger.info(f"   📖 Sample: {results[0].text[:100]}...")
                else:
                    logger.warning(f"⚠️  Search test '{query}': No results")
            except Exception as e:
                logger.error(f"❌ Search test '{query}' failed: {e}")
                return False
        
        return True
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate loading summary report."""
        total_chunks = self.stats['successful_loads'] + self.stats['failed_loads']
        success_rate = (self.stats['successful_loads'] / total_chunks * 100) if total_chunks > 0 else 0
        
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'files_processed': self.stats['files_processed'],
            'total_verses': self.stats['total_verses'],
            'successful_loads': self.stats['successful_loads'],
            'failed_loads': self.stats['failed_loads'],
            'success_rate': success_rate,
            'books': self.stats['books']
        }


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Load weighted RAG format spiritual texts into Cosmos DB"
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default="data/sources",
        help="Directory containing weighted JSONL files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process texts but don't load into Cosmos DB"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🕉️  Vimarsh AI Agent - Weighted Text Loading")
    logger.info("=" * 50)
    
    try:
        # Initialize loader
        loader = WeightedTextLoader()
        await loader.initialize_storage()
        
        # Find weighted JSONL files
        source_dir = Path(args.source_dir)
        if not source_dir.exists():
            logger.error(f"❌ Source directory not found: {source_dir}")
            return False
        
        # Load BOTH commentary-focused AND balanced files for dual-file strategy
        jsonl_files = []
        commentary_files = list(source_dir.glob("*commentary_focused*.jsonl"))
        balanced_files = list(source_dir.glob("*balanced*.jsonl"))
        
        # Load both types for comprehensive coverage
        jsonl_files.extend(commentary_files)
        jsonl_files.extend(balanced_files)
        
        if not jsonl_files:
            # Look for any JSONL files
            jsonl_files = list(source_dir.glob("*.jsonl"))
        
        if not jsonl_files:
            logger.error(f"❌ No JSONL files found in {source_dir}")
            return False
        
        logger.info(f"📋 Found {len(jsonl_files)} files to process:")
        for file in jsonl_files:
            logger.info(f"   • {file.name}")
        
        if args.dry_run:
            logger.info("🔍 DRY RUN MODE - No actual loading will occur")
            return True
        
        # Load each book
        success_count = 0
        for jsonl_file in jsonl_files:
            success = await loader.load_book(jsonl_file)
            if success:
                success_count += 1
        
        # Validate loading
        if success_count > 0:
            validation_success = await loader.validate_loading()
            if validation_success:
                logger.info("✅ Validation successful!")
            else:
                logger.warning("⚠️  Validation had issues")
        
        # Generate and save report
        report = loader.generate_report()
        report_path = Path("data/processed") / f"cosmos_weighted_loading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Final summary
        logger.info("📊 === LOADING SUMMARY ===")
        logger.info(f"   📚 Books processed: {report['files_processed']}")
        logger.info(f"   📖 Total verses: {report['total_verses']}")
        logger.info(f"   ✅ Successful loads: {report['successful_loads']}")
        logger.info(f"   ❌ Failed loads: {report['failed_loads']}")
        logger.info(f"   📈 Success rate: {report['success_rate']:.1f}%")
        logger.info(f"   📄 Report saved: {report_path}")
        
        if report['success_rate'] >= 80:
            logger.info("🎉 Task 8.8 completed successfully!")
            logger.info("🎯 Ready for Task 8.9: Configure Microsoft Entra External ID authentication")
            return True
        else:
            logger.error("💥 Task 8.8 failed - success rate too low")
            return False
            
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
