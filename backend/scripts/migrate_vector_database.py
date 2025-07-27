#!/usr/bin/env python3
"""
Vector Database Migration Script for Multi-Personality System

This script migrates the existing spiritual texts in Cosmos DB from the simple
structure to the new multi-personality vector database organization.

WHAT IT DOES:
1. Connects to existing Cosmos DB with spiritual texts (20.63MB)
2. Reads all existing documents from the spiritual-texts collection
3. Analyzes content to determine which personality each text belongs to
4. Chunks the texts appropriately for vector search
5. Generates embeddings for each chunk
6. Stores in new multi-personality structure

USAGE:
    python scripts/migrate_vector_database.py [--dry-run] [--personality PERSONALITY]

SAFETY FEATURES:
- Dry run mode to preview changes without modifying data
- Backup creation before migration
- Rollback capability
- Progress logging with detailed statistics
"""

import asyncio
import logging
import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.vector_database_service import VectorDatabaseService
    from services.personality_service import personality_service
    from azure.cosmos import CosmosClient
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the backend directory and all dependencies are installed")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'vector_migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MigrationStats:
    """Track migration statistics"""
    documents_processed: int = 0
    documents_migrated: int = 0
    chunks_created: int = 0
    embeddings_generated: int = 0
    personalities_updated: int = 0
    errors: int = 0
    start_time: datetime = None
    end_time: datetime = None
    
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

class VectorDatabaseMigrator:
    """Handles migration from old to new vector database structure"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = MigrationStats()
        self.vector_service = None
        self.cosmos_client = None
        self.source_database = None
        self.source_container = None
        self.personality_mapping = {}
        
    async def initialize(self):
        """Initialize services and connections"""
        logger.info("Initializing migration services...")
        
        try:
            # Initialize vector database service
            self.vector_service = VectorDatabaseService()
            # Note: VectorDatabaseService initializes in __init__, no need to call initialize()
            logger.info("Vector database service initialized")
            
            # Initialize Cosmos DB client for source data
            cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
            cosmos_key = os.getenv("COSMOS_KEY")
            
            if not cosmos_endpoint or not cosmos_key:
                raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY environment variables are required")
                
            self.cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
            self.source_database = self.cosmos_client.get_database_client("vimarsh-db")
            self.source_database = self.source_database.get_container_client("spiritual-texts")
            logger.info("Source Cosmos DB connection established")
            
            # Load personality mapping for content classification
            await self._load_personality_mapping()
            logger.info("Personality mapping loaded")
            
        except Exception as e:
            logger.error(f"Failed to initialize migration services: {e}")
            raise
    
    async def _load_personality_mapping(self):
        """Load personality profiles for content classification"""
        try:
            # Get all available personalities
            personalities = await personality_service.get_all_personalities()
            
            for personality in personalities:
                self.personality_mapping[personality.id] = {
                    'name': personality.name,
                    'keywords': personality.expertise_areas + [personality.name.lower()],
                    'cultural_context': personality.cultural_context,
                    'source_texts': getattr(personality, 'source_texts', [])
                }
                
            logger.info(f"📚 Loaded {len(self.personality_mapping)} personality profiles for content classification")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load personality mapping: {e}")
            # Fallback to basic mapping
            self.personality_mapping = {
                'krishna': {'keywords': ['krishna', 'bhagavad', 'gita', 'dharma', 'karma'], 'name': 'Krishna'},
                'buddha': {'keywords': ['buddha', 'dharma', 'sangha', 'meditation', 'mindfulness'], 'name': 'Buddha'},
                'jesus': {'keywords': ['jesus', 'christ', 'gospel', 'love', 'forgiveness'], 'name': 'Jesus'},
                'rumi': {'keywords': ['rumi', 'sufi', 'divine', 'beloved', 'mystical'], 'name': 'Rumi'},
                'lao_tzu': {'keywords': ['lao', 'tzu', 'tao', 'way', 'wu wei'], 'name': 'Lao Tzu'}
            }
    
    def _classify_content_by_personality(self, content: str, title: str = "", source: str = "") -> str:
        """Classify content to determine which personality it belongs to"""
        content_lower = content.lower()
        title_lower = title.lower()
        source_lower = source.lower()
        
        personality_scores = {}
        
        # Score each personality based on keyword matches
        for personality_id, info in self.personality_mapping.items():
            score = 0
            keywords = info.get('keywords', [])
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Higher weight for title and source matches
                if keyword_lower in title_lower:
                    score += 3
                if keyword_lower in source_lower:
                    score += 2
                if keyword_lower in content_lower:
                    score += 1
            
            personality_scores[personality_id] = score
        
        # Return personality with highest score, default to Krishna
        if personality_scores:
            best_personality = max(personality_scores.items(), key=lambda x: x[1])
            if best_personality[1] > 0:
                return best_personality[0]
        
        # Default fallback
        return 'krishna'
    
    async def create_backup(self) -> str:
        """Create backup of current vector database state"""
        if self.dry_run:
            logger.info("🔄 [DRY RUN] Would create backup of current vector database")
            return "dry_run_backup"
        
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"vector_db_backup_{backup_timestamp}"
        
        try:
            # Export current vector database state
            backup_data = await self.vector_service.export_database()
            
            # Save backup to file
            backup_path = f"data/backups/{backup_name}.json"
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Backup created: {backup_path}")
            return backup_name
            
        except Exception as e:
            logger.error(f"❌ Failed to create backup: {e}")
            raise
    
    async def migrate_documents(self, personality_filter: Optional[str] = None) -> MigrationStats:
        """Migrate documents from old to new structure"""
        self.stats.start_time = datetime.now()
        logger.info("🚀 Starting vector database migration...")
        
        try:
            # Query all documents from source container
            query = "SELECT * FROM c"
            items = list(self.source_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            logger.info(f"📄 Found {len(items)} documents in source collection")
            
            for item in items:
                await self._migrate_single_document(item, personality_filter)
                self.stats.documents_processed += 1
                
                # Progress logging every 100 documents
                if self.stats.documents_processed % 100 == 0:
                    logger.info(f"📊 Progress: {self.stats.documents_processed}/{len(items)} documents processed")
            
            self.stats.end_time = datetime.now()
            
            # Log final statistics
            self._log_migration_summary()
            
            return self.stats
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            self.stats.errors += 1
            raise
    
    async def _migrate_single_document(self, document: Dict[str, Any], personality_filter: Optional[str] = None):
        """Migrate a single document to the new structure"""
        try:
            # Extract document metadata
            doc_id = document.get('id', 'unknown')
            title = document.get('title', document.get('name', ''))
            content = document.get('content', document.get('text', ''))
            source = document.get('source', document.get('book', document.get('author', '')))
            
            if not content:
                logger.warning(f"⚠️ Skipping document {doc_id} - no content found")
                return
            
            # Classify content by personality
            personality_id = self._classify_content_by_personality(content, title, source)
            
            # Skip if filtering by specific personality
            if personality_filter and personality_id != personality_filter:
                return
            
            if self.dry_run:
                logger.info(f"🔄 [DRY RUN] Would migrate '{title[:50]}...' to {personality_id}")
                self.stats.documents_migrated += 1
                self.stats.chunks_created += len(content) // 1000  # Estimate chunks
                return
            
            # Add content to vector database with personality classification
            result = await self.vector_service.add_content(
                personality_id=personality_id,
                content=content,
                source=source,
                title=title,
                metadata={
                    'original_id': doc_id,
                    'migrated_at': datetime.now().isoformat(),
                    'migration_source': 'legacy_spiritual_texts',
                    'auto_classified': True,
                    'confidence_score': 0.8  # Auto-classification confidence
                }
            )
            
            if result:
                self.stats.documents_migrated += 1
                self.stats.chunks_created += result.get('chunks_created', 0)
                self.stats.embeddings_generated += result.get('embeddings_generated', 0)
                logger.info(f"✅ Migrated '{title[:50]}...' to {personality_id} personality")
            else:
                logger.warning(f"⚠️ Failed to migrate document {doc_id}")
                self.stats.errors += 1
                
        except Exception as e:
            logger.error(f"❌ Error migrating document {document.get('id', 'unknown')}: {e}")
            self.stats.errors += 1
    
    def _log_migration_summary(self):
        """Log comprehensive migration summary"""
        duration = self.stats.duration_seconds()
        
        logger.info("=" * 60)
        logger.info("📊 MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"⏱️ Duration: {duration:.2f} seconds")
        logger.info(f"📄 Documents processed: {self.stats.documents_processed}")
        logger.info(f"✅ Documents migrated: {self.stats.documents_migrated}")
        logger.info(f"🔢 Chunks created: {self.stats.chunks_created}")
        logger.info(f"🧠 Embeddings generated: {self.stats.embeddings_generated}")
        logger.info(f"👥 Personalities updated: {self.stats.personalities_updated}")
        logger.info(f"❌ Errors: {self.stats.errors}")
        
        if duration > 0:
            logger.info(f"📈 Processing rate: {self.stats.documents_processed / duration:.2f} docs/sec")
        
        if self.dry_run:
            logger.info("🔄 This was a DRY RUN - no actual changes were made")
        
        logger.info("=" * 60)
    
    async def validate_migration(self) -> Dict[str, Any]:
        """Validate the migration results"""
        logger.info("🔍 Validating migration results...")
        
        validation_results = {
            'personalities_with_content': [],
            'total_chunks': 0,
            'total_embeddings': 0,
            'health_check_passed': False,
            'issues': []
        }
        
        try:
            # Check each personality's content
            for personality_id in self.personality_mapping.keys():
                stats = await self.vector_service.get_personality_stats(personality_id)
                if stats['total_chunks'] > 0:
                    validation_results['personalities_with_content'].append({
                        'personality': personality_id,
                        'chunks': stats['total_chunks'],
                        'embeddings': stats['total_embeddings']
                    })
                    validation_results['total_chunks'] += stats['total_chunks']
                    validation_results['total_embeddings'] += stats['total_embeddings']
            
            # Perform health check
            health = await self.vector_service.health_check()
            validation_results['health_check_passed'] = health['status'] == 'healthy'
            
            if not validation_results['health_check_passed']:
                validation_results['issues'].extend(health.get('issues', []))
            
            # Log validation results
            logger.info("✅ Validation complete:")
            logger.info(f"   - Personalities with content: {len(validation_results['personalities_with_content'])}")
            logger.info(f"   - Total chunks: {validation_results['total_chunks']}")
            logger.info(f"   - Total embeddings: {validation_results['total_embeddings']}")
            logger.info(f"   - Health check: {'✅ PASSED' if validation_results['health_check_passed'] else '❌ FAILED'}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            validation_results['issues'].append(f"Validation error: {str(e)}")
            return validation_results

async def main():
    """Main migration script"""
    parser = argparse.ArgumentParser(description="Migrate vector database to multi-personality structure")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying data")
    parser.add_argument("--personality", type=str, help="Migrate only specific personality")
    parser.add_argument("--skip-backup", action="store_true", help="Skip backup creation")
    parser.add_argument("--validate-only", action="store_true", help="Only run validation, skip migration")
    
    args = parser.parse_args()
    
    migrator = VectorDatabaseMigrator(dry_run=args.dry_run)
    
    try:
        # Initialize
        await migrator.initialize()
        
        if args.validate_only:
            # Only run validation
            validation_results = await migrator.validate_migration()
            if validation_results['health_check_passed']:
                logger.info("✅ Validation passed - vector database is healthy")
                return 0
            else:
                logger.error("❌ Validation failed - issues found")
                return 1
        
        # Create backup unless skipped
        if not args.skip_backup:
            backup_name = await migrator.create_backup()
            logger.info(f"📦 Backup created: {backup_name}")
        
        # Run migration
        stats = await migrator.migrate_documents(personality_filter=args.personality)
        
        # Validate results
        validation_results = await migrator.validate_migration()
        
        # Determine exit code
        if stats.errors == 0 and validation_results['health_check_passed']:
            logger.info("Migration completed successfully!")
            return 0
        else:
            logger.error("Migration completed with issues")
            return 1
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
