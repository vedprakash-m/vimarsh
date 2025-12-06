#!/usr/bin/env python3
"""
Re-embedding Script for Gemini Embedding Model Migration

Migrates all personality content vectors from deprecated text-embedding-004
to gemini-embedding-001 with Matryoshka Representation Learning (MRL).

This script:
1. Backs up existing embeddings to a local file
2. Re-generates embeddings using gemini-embedding-001 with 768-dim MRL
3. L2-normalizes all embeddings for optimal cosine similarity
4. Updates documents in Cosmos DB with new embeddings
5. Validates the migration and generates a report

Usage:
    python reembed_with_gemini_embedding_001.py --dry-run      # Preview without changes
    python reembed_with_gemini_embedding_001.py --domain spiritual  # Re-embed specific domain
    python reembed_with_gemini_embedding_001.py --all          # Re-embed everything
    python reembed_with_gemini_embedding_001.py --validate     # Validate existing embeddings

Author: Vimarsh Team
Date: December 2025
"""

import os
import sys
import json
import asyncio
import argparse
import logging
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

# Azure Cosmos DB
try:
    from azure.cosmos import CosmosClient
    from azure.cosmos.exceptions import CosmosHttpResponseError
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False
    print("⚠️ Azure Cosmos DB SDK not available. Install with: pip install azure-cosmos")

# Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Google Generative AI not available. Install with: pip install google-generativeai")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'reembedding_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# Domain to personality mapping
DOMAIN_PERSONALITIES = {
    'spiritual': ['krishna', 'buddha', 'jesus', 'rumi', 'vivekananda'],
    'philosophical': ['marcus_aurelius', 'lao_tzu', 'confucius', 'aristotle', 'plato', 'socrates'],
    'leadership': ['chanakya', 'lincoln', 'franklin', 'washington', 'gandhi', 'mlk'],
    'scientific': ['einstein', 'newton', 'tesla', 'archimedes', 'da_vinci'],
    'literary': ['tagore', 'shakespeare'],
    'psychology': ['freud']
}

# Flatten for quick lookup
ALL_PERSONALITIES = [p for domain in DOMAIN_PERSONALITIES.values() for p in domain]


@dataclass
class MigrationStats:
    """Statistics for the migration process"""
    total_documents: int = 0
    processed: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    domains_processed: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.domains_processed is None:
            self.domains_processed = []
        if self.errors is None:
            self.errors = []
    
    @property
    def success_rate(self) -> float:
        if self.processed == 0:
            return 0.0
        return (self.successful / self.processed) * 100
    
    @property
    def duration_seconds(self) -> float:
        if not self.start_time or not self.end_time:
            return 0.0
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time)
        return (end - start).total_seconds()


class EmbeddingMigrator:
    """
    Handles the migration of embeddings from text-embedding-004 to gemini-embedding-001
    """
    
    # Configuration - Extreme rate limit protection for Gemini API free tier
    NEW_MODEL = "models/gemini-embedding-001"
    OUTPUT_DIMENSIONALITY = 768  # MRL dimension for Cosmos DB compatibility
    BATCH_SIZE = 1  # Process 1 document at a time (extremely conservative)
    RATE_LIMIT_DELAY = 10.0  # 10 seconds between EVERY API call (was 5.0)
    MAX_RETRIES = 5  # More retries for transient failures
    BATCH_DELAY = 60.0  # 60 second pause between batches (was 30.0)
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.cosmos_client = None
        self.database = None
        self.container = None
        self.stats = MigrationStats()
        self.backup_dir = Path(__file__).parent / 'backups' / f'embeddings_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        # Initialize clients
        self._init_cosmos()
        self._init_gemini()
    
    def _init_cosmos(self) -> None:
        """Initialize Cosmos DB connection"""
        if not COSMOS_AVAILABLE:
            raise RuntimeError("Azure Cosmos DB SDK not available")
        
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("AZURE_COSMOS_CONNECTION_STRING environment variable not set")
        
        try:
            self.cosmos_client = CosmosClient.from_connection_string(connection_string)
            database_name = os.getenv('AZURE_COSMOS_DATABASE', 'vimarsh-multi-personality')
            container_name = os.getenv('AZURE_COSMOS_CONTAINER', 'personality_vectors')
            
            self.database = self.cosmos_client.get_database_client(database_name)
            self.container = self.database.get_container_client(container_name)
            
            logger.info(f"✅ Connected to Cosmos DB: {database_name}/{container_name}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
            raise
    
    def _init_gemini(self) -> None:
        """Initialize Gemini API"""
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Google Generative AI SDK not available")
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        try:
            genai.configure(api_key=api_key)
            logger.info(f"✅ Gemini API configured with model: {self.NEW_MODEL}")
        except Exception as e:
            logger.error(f"❌ Failed to configure Gemini API: {e}")
            raise
    
    def _normalize_embedding(self, embedding: List[float]) -> List[float]:
        """L2-normalize embedding vector for optimal cosine similarity"""
        if not embedding:
            return embedding
        
        norm = math.sqrt(sum(x * x for x in embedding))
        if norm == 0:
            return embedding
        
        return [x / norm for x in embedding]
    
    async def generate_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT", retries: int = 0) -> Optional[List[float]]:
        """Generate embedding using gemini-embedding-001 with MRL"""
        try:
            # Rate limiting - skip on retries since we already waited in exponential backoff
            if retries == 0:
                await asyncio.sleep(self.RATE_LIMIT_DELAY)
            
            # Generate embedding
            result = genai.embed_content(
                model=self.NEW_MODEL,
                content=text,
                task_type=task_type,
                output_dimensionality=self.OUTPUT_DIMENSIONALITY
            )
            
            embedding = result['embedding']
            
            # L2-normalize for MRL dimensions < 3072
            normalized = self._normalize_embedding(embedding)
            
            return normalized
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if retries < self.MAX_RETRIES:
                # Handle rate limits with exponential backoff
                if 'rate' in error_msg or 'quota' in error_msg or '429' in error_msg or 'resource_exhausted' in error_msg:
                    # Exponential backoff: 60s, 120s, 240s, 480s, 960s (very aggressive for free tier)
                    wait_time = 60 * (2 ** retries)
                    logger.warning(f"⚠️ Rate limit hit (attempt {retries + 1}/{self.MAX_RETRIES}), waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    # General error: shorter exponential backoff
                    wait_time = 10 * (2 ** retries)
                    logger.warning(f"⚠️ API error (attempt {retries + 1}/{self.MAX_RETRIES}): {str(e)[:100]}")
                    await asyncio.sleep(wait_time)
                
                return await self.generate_embedding(text, task_type, retries + 1)
            
            logger.error(f"❌ Failed to generate embedding after {self.MAX_RETRIES} retries: {e}")
            return None
    
    def get_documents_by_personality(self, personality: str) -> List[Dict[str, Any]]:
        """Retrieve all documents for a specific personality"""
        try:
            # Query using personality_id field which contains just the personality name
            query = f"SELECT * FROM c WHERE c.personality_id = '{personality}'"
            documents = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            logger.info(f"📚 Found {len(documents)} documents for {personality}")
            return documents
        except Exception as e:
            logger.error(f"❌ Failed to query documents for {personality}: {e}")
            return []
    
    def get_documents_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Retrieve all documents for a specific domain"""
        if domain not in DOMAIN_PERSONALITIES:
            logger.error(f"❌ Unknown domain: {domain}")
            return []
        
        all_documents = []
        for personality in DOMAIN_PERSONALITIES[domain]:
            documents = self.get_documents_by_personality(personality)
            all_documents.extend(documents)
        
        logger.info(f"📚 Total {len(all_documents)} documents for domain '{domain}'")
        return all_documents
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Retrieve all documents from the container"""
        try:
            query = "SELECT * FROM c"
            documents = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            logger.info(f"📚 Found {len(documents)} total documents")
            return documents
        except Exception as e:
            logger.error(f"❌ Failed to query all documents: {e}")
            return []
    
    def backup_embeddings(self, documents: List[Dict[str, Any]]) -> bool:
        """Backup existing embeddings to local file"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_data = []
            for doc in documents:
                if 'embedding' in doc:
                    backup_data.append({
                        'id': doc.get('id'),
                        'personality': doc.get('personality'),
                        'embedding': doc.get('embedding'),
                        'embedding_model': doc.get('embedding_model', 'text-embedding-004'),
                        'backup_timestamp': datetime.now(timezone.utc).isoformat()
                    })
            
            backup_file = self.backup_dir / 'embeddings_backup.json'
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"✅ Backed up {len(backup_data)} embeddings to {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to backup embeddings: {e}")
            return False
    
    async def migrate_document(self, document: Dict[str, Any]) -> bool:
        """Migrate a single document's embedding"""
        doc_id = document.get('id', 'unknown')
        personality = document.get('personality', 'unknown')
        
        try:
            # Get text content
            content = document.get('content') or document.get('chunk_text', '')
            if not content:
                logger.warning(f"⚠️ No content for document {doc_id}")
                self.stats.skipped += 1
                return False
            
            # Generate new embedding
            new_embedding = await self.generate_embedding(content, "RETRIEVAL_DOCUMENT")
            if not new_embedding:
                logger.error(f"❌ Failed to generate embedding for {doc_id}")
                self.stats.failed += 1
                self.stats.errors.append(f"Failed to generate embedding for {doc_id}")
                return False
            
            # Update document
            if not self.dry_run:
                document['embedding'] = new_embedding
                document['embedding_model'] = 'gemini-embedding-001'
                document['embedding_dimensions'] = len(new_embedding)
                document['embedding_normalized'] = True
                document['embedding_migrated_at'] = datetime.now(timezone.utc).isoformat()
                document['has_embedding'] = True
                
                self.container.upsert_item(document)
            
            self.stats.successful += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate document {doc_id}: {e}")
            self.stats.failed += 1
            self.stats.errors.append(f"Document {doc_id}: {str(e)}")
            return False
    
    async def migrate_batch(self, documents: List[Dict[str, Any]], batch_num: int, total_batches: int) -> None:
        """Migrate a batch of documents"""
        logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(documents)} documents)")
        
        for i, doc in enumerate(documents):
            self.stats.processed += 1
            await self.migrate_document(doc)
            
            if (i + 1) % 10 == 0:
                logger.info(f"   Progress: {i + 1}/{len(documents)} in batch {batch_num}")
        
        # Pause between batches to avoid rate limits
        if batch_num < total_batches:
            logger.info(f"   ⏸️ Pausing {self.BATCH_DELAY}s before next batch...")
            await asyncio.sleep(self.BATCH_DELAY)
    
    async def run_migration(self, domain: Optional[str] = None, personality: Optional[str] = None) -> MigrationStats:
        """Run the full migration process"""
        self.stats.start_time = datetime.now(timezone.utc).isoformat()
        
        logger.info("=" * 60)
        logger.info("🚀 GEMINI EMBEDDING MODEL MIGRATION")
        logger.info(f"   Target Model: {self.NEW_MODEL}")
        logger.info(f"   Output Dimensions: {self.OUTPUT_DIMENSIONALITY} (MRL)")
        logger.info(f"   Dry Run: {self.dry_run}")
        logger.info("=" * 60)
        
        # Get documents to migrate
        if personality:
            documents = self.get_documents_by_personality(personality)
            self.stats.domains_processed = [personality]
        elif domain:
            documents = self.get_documents_by_domain(domain)
            self.stats.domains_processed = [domain]
        else:
            documents = self.get_all_documents()
            self.stats.domains_processed = list(DOMAIN_PERSONALITIES.keys())
        
        self.stats.total_documents = len(documents)
        
        if not documents:
            logger.warning("⚠️ No documents found to migrate")
            self.stats.end_time = datetime.now(timezone.utc).isoformat()
            return self.stats
        
        # Backup existing embeddings
        logger.info("\n📂 STEP 1: Backing up existing embeddings...")
        if not self.backup_embeddings(documents):
            logger.error("❌ Backup failed, aborting migration")
            self.stats.end_time = datetime.now(timezone.utc).isoformat()
            return self.stats
        
        # Process in batches
        logger.info(f"\n🔄 STEP 2: Re-embedding {len(documents)} documents...")
        
        batches = [documents[i:i + self.BATCH_SIZE] for i in range(0, len(documents), self.BATCH_SIZE)]
        total_batches = len(batches)
        
        for batch_num, batch in enumerate(batches, 1):
            await self.migrate_batch(batch, batch_num, total_batches)
            
            # Progress summary every 5 batches
            if batch_num % 5 == 0:
                logger.info(f"\n📊 Overall Progress: {self.stats.processed}/{self.stats.total_documents} "
                          f"({self.stats.success_rate:.1f}% success rate)")
        
        self.stats.end_time = datetime.now(timezone.utc).isoformat()
        
        # Generate report
        self._generate_report()
        
        return self.stats
    
    def _generate_report(self) -> None:
        """Generate migration report"""
        report = f"""
{'=' * 60}
📊 MIGRATION REPORT
{'=' * 60}

Migration Summary:
- Total Documents: {self.stats.total_documents}
- Processed: {self.stats.processed}
- Successful: {self.stats.successful}
- Failed: {self.stats.failed}
- Skipped: {self.stats.skipped}
- Success Rate: {self.stats.success_rate:.2f}%
- Duration: {self.stats.duration_seconds:.1f} seconds

Model Migration:
- From: text-embedding-004
- To: {self.NEW_MODEL}
- Dimensions: {self.OUTPUT_DIMENSIONALITY} (MRL, L2-normalized)

Domains Processed:
{chr(10).join(f'  - {d}' for d in self.stats.domains_processed)}

Backup Location: {self.backup_dir}
"""
        
        if self.stats.errors:
            report += f"\nErrors ({len(self.stats.errors)}):\n"
            for error in self.stats.errors[:10]:  # Show first 10 errors
                report += f"  - {error}\n"
            if len(self.stats.errors) > 10:
                report += f"  ... and {len(self.stats.errors) - 10} more\n"
        
        logger.info(report)
        
        # Save report to file
        report_file = self.backup_dir / 'migration_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.stats), f, indent=2, default=str)
        
        logger.info(f"📝 Report saved to {report_file}")
    
    async def validate_embeddings(self) -> Dict[str, Any]:
        """Validate that all embeddings use the new model"""
        logger.info("\n🔍 Validating embeddings...")
        
        documents = self.get_all_documents()
        
        validation = {
            'total': len(documents),
            'new_model': 0,
            'old_model': 0,
            'missing': 0,
            'dimension_768': 0,
            'normalized': 0,
            'by_personality': {}
        }
        
        for doc in documents:
            personality = doc.get('personality', 'unknown')
            if personality not in validation['by_personality']:
                validation['by_personality'][personality] = {'new': 0, 'old': 0, 'missing': 0}
            
            if 'embedding' not in doc or not doc['embedding']:
                validation['missing'] += 1
                validation['by_personality'][personality]['missing'] += 1
            elif doc.get('embedding_model') == 'gemini-embedding-001':
                validation['new_model'] += 1
                validation['by_personality'][personality]['new'] += 1
                
                if len(doc['embedding']) == 768:
                    validation['dimension_768'] += 1
                if doc.get('embedding_normalized'):
                    validation['normalized'] += 1
            else:
                validation['old_model'] += 1
                validation['by_personality'][personality]['old'] += 1
        
        # Report
        logger.info(f"""
Validation Results:
- Total Documents: {validation['total']}
- Using gemini-embedding-001: {validation['new_model']} ({validation['new_model']/validation['total']*100:.1f}%)
- Using old model: {validation['old_model']} ({validation['old_model']/validation['total']*100:.1f}%)
- Missing embeddings: {validation['missing']}
- 768-dimensional: {validation['dimension_768']}
- Normalized: {validation['normalized']}
""")
        
        return validation


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Migrate embeddings from text-embedding-004 to gemini-embedding-001'
    )
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying database')
    parser.add_argument('--domain', type=str, choices=list(DOMAIN_PERSONALITIES.keys()), help='Migrate specific domain')
    parser.add_argument('--personality', type=str, help='Migrate specific personality')
    parser.add_argument('--all', action='store_true', help='Migrate all documents')
    parser.add_argument('--validate', action='store_true', help='Validate existing embeddings')
    
    args = parser.parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
    
    try:
        migrator = EmbeddingMigrator(dry_run=args.dry_run)
        
        if args.validate:
            await migrator.validate_embeddings()
        elif args.all:
            await migrator.run_migration()
        elif args.domain:
            await migrator.run_migration(domain=args.domain)
        elif args.personality:
            await migrator.run_migration(personality=args.personality)
        else:
            parser.print_help()
            print("\n⚠️ Please specify --all, --domain, --personality, or --validate")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
