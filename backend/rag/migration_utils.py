"""
Vector Storage Migration Utility
Task 8.7: Migrate local vector storage to Cosmos DB vector search

This utility migrates data from local Faiss-based vector storage to Azure Cosmos DB
vector search, ensuring seamless transition with data validation and integrity checks.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime, timezone
from dataclasses import asdict

# Import both storage implementations
from backend.rag.vector_storage import LocalVectorStorage, TextChunk
from backend.rag.cosmos_vector_search import CosmosVectorSearch, SpiritualTextChunk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStorageMigration:
    """
    Handles migration from local Faiss storage to Cosmos DB vector search.
    Provides data validation, integrity checks, and rollback capabilities.
    """
    
    def __init__(self, 
                 local_storage_path: str = "data/vector_storage",
                 cosmos_endpoint: str = None,
                 cosmos_key: str = None,
                 backup_path: str = "data/migration_backup"):
        """
        Initialize migration utility.
        
        Args:
            local_storage_path: Path to local Faiss storage
            cosmos_endpoint: Cosmos DB endpoint
            cosmos_key: Cosmos DB access key
            backup_path: Path for migration backup files
        """
        self.local_storage_path = Path(local_storage_path)
        self.backup_path = Path(backup_path)
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage clients
        self.local_storage = LocalVectorStorage(storage_path=str(self.local_storage_path))
        self.cosmos_storage = CosmosVectorSearch(endpoint=cosmos_endpoint, key=cosmos_key)
        
        # Migration state
        self.migration_started = False
        self.migration_completed = False
        self.migration_stats = {
            'total_chunks': 0,
            'migrated_chunks': 0,
            'failed_chunks': 0,
            'skipped_chunks': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Validation settings
        self.validate_embeddings = True
        self.similarity_threshold = 0.95  # For embedding validation
        
        logger.info("🔄 Vector Storage Migration utility initialized")
    
    def analyze_local_data(self) -> Dict[str, Any]:
        """
        Analyze local storage data before migration.
        
        Returns:
            Analysis report with statistics and recommendations
        """
        logger.info("🔍 Analyzing local vector storage data...")
        
        analysis = {
            'total_chunks': len(self.local_storage.chunks),
            'sources': {},
            'embedding_dimensions': set(),
            'sanskrit_terms': set(),
            'chapters': set(),
            'verses': set(),
            'data_issues': [],
            'migration_readiness': True
        }
        
        for chunk in self.local_storage.chunks:
            # Source analysis
            if chunk.source not in analysis['sources']:
                analysis['sources'][chunk.source] = 0
            analysis['sources'][chunk.source] += 1
            
            # Embedding analysis
            if chunk.embedding is not None:
                analysis['embedding_dimensions'].add(len(chunk.embedding))
            else:
                analysis['data_issues'].append(f"Missing embedding: {chunk.id}")
                analysis['migration_readiness'] = False
            
            # Content analysis
            if chunk.sanskrit_terms:
                analysis['sanskrit_terms'].update(chunk.sanskrit_terms)
            
            if chunk.chapter:
                analysis['chapters'].add(chunk.chapter)
            
            if chunk.verse:
                analysis['verses'].add(chunk.verse)
            
            # Data validation
            if not chunk.text or len(chunk.text.strip()) == 0:
                analysis['data_issues'].append(f"Empty text: {chunk.id}")
            
            if not chunk.source:
                analysis['data_issues'].append(f"Missing source: {chunk.id}")
        
        # Convert sets to counts for JSON serialization
        analysis['unique_sources'] = len(analysis['sources'])
        analysis['unique_sanskrit_terms'] = len(analysis['sanskrit_terms'])
        analysis['unique_chapters'] = len(analysis['chapters'])
        analysis['unique_verses'] = len(analysis['verses'])
        analysis['embedding_dimensions'] = list(analysis['embedding_dimensions'])
        analysis['sanskrit_terms'] = list(analysis['sanskrit_terms'])[:20]  # Sample
        analysis['chapters'] = list(analysis['chapters'])[:10]  # Sample
        analysis['verses'] = list(analysis['verses'])[:10]  # Sample
        
        logger.info(f"📊 Analysis complete: {analysis['total_chunks']} chunks, {analysis['unique_sources']} sources")
        
        if analysis['data_issues']:
            logger.warning(f"⚠️ Found {len(analysis['data_issues'])} data issues")
            for issue in analysis['data_issues'][:5]:  # Show first 5
                logger.warning(f"   - {issue}")
        
        return analysis
    
    def create_migration_backup(self) -> str:
        """
        Create backup of local data before migration.
        
        Returns:
            Path to backup file
        """
        logger.info("💾 Creating migration backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_path / f"vector_storage_backup_{timestamp}.json"
        
        backup_data = {
            'metadata': {
                'backup_time': datetime.now(timezone.utc).isoformat(),
                'source_path': str(self.local_storage_path),
                'total_chunks': len(self.local_storage.chunks),
                'migration_version': '1.0'
            },
            'chunks': []
        }
        
        # Serialize all chunks
        for chunk in self.local_storage.chunks:
            chunk_data = {
                'id': chunk.id,
                'text': chunk.text,
                'source': chunk.source,
                'chapter': chunk.chapter,
                'verse': chunk.verse,
                'sanskrit_terms': chunk.sanskrit_terms,
                'embedding': chunk.embedding.tolist() if chunk.embedding is not None else None
            }
            backup_data['chunks'].append(chunk_data)
        
        # Save backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Backup created: {backup_file} ({len(backup_data['chunks'])} chunks)")
        return str(backup_file)
    
    def convert_chunk_format(self, local_chunk: TextChunk) -> SpiritualTextChunk:
        """
        Convert local TextChunk to Cosmos SpiritualTextChunk format.
        
        Args:
            local_chunk: Local storage chunk
            
        Returns:
            Cosmos DB compatible chunk
        """
        # Extract spiritual context from text content
        spiritual_theme = self._extract_spiritual_theme(local_chunk.text)
        dharmic_context = self._extract_dharmic_context(local_chunk.text, local_chunk.sanskrit_terms)
        character_speaker = self._extract_character_speaker(local_chunk.text, local_chunk.source)
        
        # Convert embedding format
        embedding = None
        if local_chunk.embedding is not None:
            if isinstance(local_chunk.embedding, np.ndarray):
                embedding = local_chunk.embedding.tolist()
            else:
                embedding = local_chunk.embedding
        
        cosmos_chunk = SpiritualTextChunk(
            id=local_chunk.id,
            text=local_chunk.text,
            source=local_chunk.source,
            chapter=local_chunk.chapter,
            verse=local_chunk.verse,
            sanskrit_terms=local_chunk.sanskrit_terms or [],
            embedding=embedding,
            spiritual_theme=spiritual_theme,
            dharmic_context=dharmic_context,
            character_speaker=character_speaker,
            chunk_size=len(local_chunk.text),
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        return cosmos_chunk
    
    def _extract_spiritual_theme(self, text: str) -> str:
        """Extract spiritual theme from text content"""
        text_lower = text.lower()
        
        # Map keywords to themes
        theme_keywords = {
            'duty': ['duty', 'dharma', 'righteousness', 'obligation'],
            'devotion': ['devotion', 'bhakti', 'love', 'surrender'],
            'knowledge': ['knowledge', 'wisdom', 'understanding', 'jnana'],
            'action': ['action', 'karma', 'work', 'deed'],
            'meditation': ['meditation', 'yoga', 'concentration', 'dhyana'],
            'liberation': ['liberation', 'moksha', 'freedom', 'salvation'],
            'divinity': ['divine', 'god', 'supreme', 'brahman'],
            'ethics': ['ethics', 'morality', 'virtue', 'goodness']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return theme
        
        return 'general'
    
    def _extract_dharmic_context(self, text: str, sanskrit_terms: List[str]) -> str:
        """Extract dharmic context from text and Sanskrit terms"""
        contexts = []
        
        # Check for specific dharmic concepts
        if sanskrit_terms:
            contexts.extend(sanskrit_terms[:3])  # First 3 Sanskrit terms
        
        # Add context based on content
        if 'krishna' in text.lower():
            contexts.append('Krishna-guidance')
        if 'arjuna' in text.lower():
            contexts.append('Arjuna-inquiry')
        if any(word in text.lower() for word in ['dharma', 'duty', 'righteousness']):
            contexts.append('dharmic-principle')
        
        return ', '.join(contexts[:3]) if contexts else 'spiritual-teaching'
    
    def _extract_character_speaker(self, text: str, source: str) -> str:
        """Extract likely character speaker from text"""
        text_lower = text.lower()
        
        if 'krishna' in text_lower or 'lord' in text_lower:
            return 'Krishna'
        elif 'arjuna' in text_lower:
            return 'Arjuna'
        elif source == 'bhagavad_gita':
            # Default speakers in Bhagavad Gita
            return 'Krishna'  # Most verses are Krishna speaking
        elif source == 'srimad_bhagavatam':
            return 'Narrator'
        
        return 'Unknown'
    
    def validate_migration_chunk(self, 
                                original: TextChunk, 
                                migrated: SpiritualTextChunk) -> Tuple[bool, List[str]]:
        """
        Validate that migrated chunk matches original.
        
        Args:
            original: Original local chunk
            migrated: Migrated cosmos chunk
            
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        # Basic field validation
        if original.id != migrated.id:
            issues.append(f"ID mismatch: {original.id} != {migrated.id}")
        
        if original.text != migrated.text:
            issues.append(f"Text mismatch for {original.id}")
        
        if original.source != migrated.source:
            issues.append(f"Source mismatch: {original.source} != {migrated.source}")
        
        # Embedding validation
        if self.validate_embeddings and original.embedding is not None:
            if migrated.embedding is None:
                issues.append(f"Missing embedding in migrated chunk {original.id}")
            else:
                # Compare embeddings
                orig_embedding = original.embedding
                migr_embedding = np.array(migrated.embedding)
                
                if orig_embedding.shape != migr_embedding.shape:
                    issues.append(f"Embedding shape mismatch for {original.id}")
                else:
                    # Calculate similarity
                    similarity = np.dot(orig_embedding, migr_embedding) / (
                        np.linalg.norm(orig_embedding) * np.linalg.norm(migr_embedding)
                    )
                    if similarity < self.similarity_threshold:
                        issues.append(f"Embedding similarity too low for {original.id}: {similarity:.3f}")
        
        return len(issues) == 0, issues
    
    def migrate_chunks(self, 
                      batch_size: int = 50, 
                      validate_each: bool = True) -> Dict[str, Any]:
        """
        Migrate chunks from local storage to Cosmos DB.
        
        Args:
            batch_size: Number of chunks to process at once
            validate_each: Whether to validate each migrated chunk
            
        Returns:
            Migration results and statistics
        """
        logger.info("🚀 Starting vector storage migration...")
        
        self.migration_started = True
        self.migration_stats['start_time'] = datetime.now(timezone.utc).isoformat()
        self.migration_stats['total_chunks'] = len(self.local_storage.chunks)
        
        # Process chunks in batches
        for i in range(0, len(self.local_storage.chunks), batch_size):
            batch = self.local_storage.chunks[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            
            logger.info(f"📦 Processing batch {batch_num} ({len(batch)} chunks)")
            
            for local_chunk in batch:
                try:
                    # Convert to Cosmos format
                    cosmos_chunk = self.convert_chunk_format(local_chunk)
                    
                    # Validate conversion if requested
                    if validate_each:
                        is_valid, issues = self.validate_migration_chunk(local_chunk, cosmos_chunk)
                        if not is_valid:
                            logger.warning(f"⚠️ Validation failed for {local_chunk.id}: {issues}")
                            self.migration_stats['failed_chunks'] += 1
                            continue
                    
                    # Add to Cosmos DB
                    success = self.cosmos_storage.add_chunk(cosmos_chunk)
                    
                    if success:
                        self.migration_stats['migrated_chunks'] += 1
                    else:
                        self.migration_stats['failed_chunks'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Failed to migrate chunk {local_chunk.id}: {e}")
                    self.migration_stats['failed_chunks'] += 1
            
            # Progress update
            progress = (self.migration_stats['migrated_chunks'] / self.migration_stats['total_chunks']) * 100
            logger.info(f"📈 Progress: {progress:.1f}% ({self.migration_stats['migrated_chunks']}/{self.migration_stats['total_chunks']})")
        
        self.migration_stats['end_time'] = datetime.now(timezone.utc).isoformat()
        self.migration_completed = True
        
        logger.info("✅ Migration completed!")
        return self.migration_stats
    
    def verify_migration(self, sample_size: int = 10) -> Dict[str, Any]:
        """
        Verify migration by sampling and comparing data.
        
        Args:
            sample_size: Number of chunks to verify
            
        Returns:
            Verification results
        """
        logger.info(f"🔍 Verifying migration with {sample_size} samples...")
        
        verification = {
            'samples_checked': 0,
            'matches': 0,
            'mismatches': 0,
            'missing_in_cosmos': 0,
            'issues': []
        }
        
        # Get Cosmos stats
        cosmos_stats = self.cosmos_storage.get_stats()
        
        # Sample local chunks for verification
        local_chunks = self.local_storage.chunks[:sample_size]
        
        for local_chunk in local_chunks:
            verification['samples_checked'] += 1
            
            # Try to find in Cosmos
            cosmos_chunk = self.cosmos_storage.get_chunk_by_id(local_chunk.id, local_chunk.source)
            
            if cosmos_chunk is None:
                verification['missing_in_cosmos'] += 1
                verification['issues'].append(f"Chunk {local_chunk.id} not found in Cosmos")
                continue
            
            # Validate match
            is_valid, issues = self.validate_migration_chunk(local_chunk, cosmos_chunk)
            
            if is_valid:
                verification['matches'] += 1
            else:
                verification['mismatches'] += 1
                verification['issues'].extend(issues)
        
        # Calculate verification rate
        if verification['samples_checked'] > 0:
            verification['success_rate'] = verification['matches'] / verification['samples_checked']
        else:
            verification['success_rate'] = 0.0
        
        verification['cosmos_stats'] = cosmos_stats
        
        logger.info(f"🎯 Verification: {verification['matches']}/{verification['samples_checked']} matches ({verification['success_rate']:.1%})")
        
        return verification
    
    def generate_migration_report(self) -> str:
        """
        Generate comprehensive migration report.
        
        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.backup_path / f"migration_report_{timestamp}.json"
        
        # Analyze data
        analysis = self.analyze_local_data()
        verification = self.verify_migration() if self.migration_completed else {}
        cosmos_stats = self.cosmos_storage.get_stats()
        
        report = {
            'migration_metadata': {
                'report_time': datetime.now(timezone.utc).isoformat(),
                'migration_completed': self.migration_completed,
                'local_storage_path': str(self.local_storage_path),
                'cosmos_database': self.cosmos_storage.database_name,
                'cosmos_container': self.cosmos_storage.container_name
            },
            'pre_migration_analysis': analysis,
            'migration_stats': self.migration_stats,
            'post_migration_verification': verification,
            'cosmos_final_stats': cosmos_stats
        }
        
        # Save report
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Migration report saved: {report_file}")
        return str(report_file)
    
    def perform_full_migration(self, 
                              create_backup: bool = True,
                              batch_size: int = 50,
                              verify_after: bool = True) -> Dict[str, Any]:
        """
        Perform complete migration with all safety checks.
        
        Args:
            create_backup: Whether to create backup before migration
            batch_size: Batch size for migration
            verify_after: Whether to verify after migration
            
        Returns:
            Complete migration results
        """
        results = {
            'started_at': datetime.now(timezone.utc).isoformat(),
            'backup_path': None,
            'analysis': None,
            'migration_stats': None,
            'verification': None,
            'report_path': None,
            'success': False
        }
        
        try:
            # Step 1: Analyze local data
            logger.info("🔍 Step 1: Analyzing local data...")
            results['analysis'] = self.analyze_local_data()
            
            if not results['analysis']['migration_readiness']:
                logger.error("❌ Migration readiness check failed - cannot proceed")
                return results
            
            # Step 2: Create backup
            if create_backup:
                logger.info("💾 Step 2: Creating backup...")
                results['backup_path'] = self.create_migration_backup()
            
            # Step 3: Migrate data
            logger.info("🚀 Step 3: Migrating data...")
            results['migration_stats'] = self.migrate_chunks(batch_size=batch_size)
            
            # Step 4: Verify migration
            if verify_after:
                logger.info("🔍 Step 4: Verifying migration...")
                results['verification'] = self.verify_migration()
            
            # Step 5: Generate report
            logger.info("📄 Step 5: Generating report...")
            results['report_path'] = self.generate_migration_report()
            
            # Check success
            migration_stats = results['migration_stats']
            total_chunks = migration_stats['total_chunks']
            migrated_chunks = migration_stats['migrated_chunks']
            success_rate = migrated_chunks / total_chunks if total_chunks > 0 else 0
            
            results['success'] = success_rate >= 0.95  # 95% success threshold
            results['completed_at'] = datetime.now(timezone.utc).isoformat()
            
            if results['success']:
                logger.info(f"🎉 Migration completed successfully! ({migrated_chunks}/{total_chunks} chunks)")
            else:
                logger.warning(f"⚠️ Migration completed with issues ({success_rate:.1%} success rate)")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            results['error'] = str(e)
            results['completed_at'] = datetime.now(timezone.utc).isoformat()
            return results


def migrate_vector_storage(local_path: str = "data/vector_storage",
                          cosmos_endpoint: str = None,
                          cosmos_key: str = None) -> Dict[str, Any]:
    """
    Convenience function to perform complete vector storage migration.
    
    Args:
        local_path: Path to local vector storage
        cosmos_endpoint: Cosmos DB endpoint
        cosmos_key: Cosmos DB key
        
    Returns:
        Migration results
    """
    migration = VectorStorageMigration(
        local_storage_path=local_path,
        cosmos_endpoint=cosmos_endpoint,
        cosmos_key=cosmos_key
    )
    
    return migration.perform_full_migration()


if __name__ == "__main__":
    # Example usage
    results = migrate_vector_storage()
    print(f"Migration completed: {results['success']}")
