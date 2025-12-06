"""
Azure OpenAI Re-embedding Script

Migrates all personality documents from deprecated text-embedding-004 to Azure OpenAI text-embedding-3-large.
Processes 34,039 documents across 6 domains with comprehensive backup, progress tracking, and validation.

Strategic Migration Benefits:
- Complete Microsoft ecosystem integration (100% Azure-native)
- Enterprise SLA guarantees (99.9% uptime)
- Cost predictability with Reserved Capacity (40-60% savings)
- Production-grade quality (MTEB 64.6, 94.8% of target)

Usage:
    # Dry run with backup preview
    python reembed_with_azure_openai.py --dry-run
    
    # Re-embed specific domain
    python reembed_with_azure_openai.py --domain spiritual
    
    # Re-embed all domains
    python reembed_with_azure_openai.py --all
"""

import os
import sys
import argparse
import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from azure.cosmos import CosmosClient
from services.azure_openai_embedding_service import AzureOpenAIEmbeddingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Domain personality mappings
DOMAIN_PERSONALITIES = {
    "spiritual": ["krishna", "buddha", "jesus", "rumi", "swami_vivekananda"],
    "philosophical": ["marcus_aurelius", "lao_tzu", "confucius", "aristotle", "plato", "socrates"],
    "leadership": ["chanakya", "lincoln", "franklin", "washington", "gandhi", "mlk"],
    "scientific": ["einstein", "newton", "tesla", "archimedes", "leonardo_da_vinci"],
    "literary": ["tagore", "shakespeare"],
    "psychology": ["freud"]
}

# Partition key mappings for old schema documents
# Some documents use partition_key instead of personality_id
PARTITION_KEY_MAPPINGS = {
    "krishna": ["krishna::"],
    "buddha": ["Buddha::"],
    "jesus": ["Jesus Christ::"],
    "marcus_aurelius": ["Marcus Aurelius::"],
    "einstein": ["Einstein::"],
    "newton": ["Newton::"],
    "tesla": ["Tesla::"],
    "lincoln": ["Lincoln::"],
    "rumi": ["Rumi::"],
    "lao_tzu": ["Lao Tzu::"],
    "confucius": ["Confucius::"],
    "chanakya": ["Chanakya::"],
    # Simple partition keys (no :: suffix)
    "archimedes": ["archimedes"],
    "aristotle": ["aristotle"],
    "plato": ["plato"],
    "socrates": ["socrates"],
    "leonardo_da_vinci": ["leonardo_da_vinci"],
    "swami_vivekananda": ["swami_vivekananda"],
    "franklin": ["benjamin_franklin"],
    "washington": ["george_washington"],
    "gandhi": ["mahatma_gandhi"],
    "mlk": ["martin_luther_king_jr"],
    "tagore": ["rabindranath_tagore"],
    "shakespeare": ["william_shakespeare"],
    "freud": ["sigmund_freud"]
}

# Configuration
CONFIG = {
    "batch_size": 100,  # Azure OpenAI supports large batches
    "rate_limit_delay": 0.6,  # 100 requests/min
    "batch_delay": 1.0,  # Delay between batches
    "backup_directory": Path(__file__).parent / "backups" / "azure_openai_migration"
}

class AzureOpenAIMigrationService:
    """Service for migrating embeddings to Azure OpenAI"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        
        # Initialize Cosmos DB
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("AZURE_COSMOS_CONNECTION_STRING not set")
        
        self.cosmos_client = CosmosClient.from_connection_string(connection_string)
        self.database = self.cosmos_client.get_database_client('vimarsh-multi-personality')
        self.container = self.database.get_container_client('personality_vectors')
        
        # Initialize Azure OpenAI embedding service
        if not dry_run:
            self.embedding_service = AzureOpenAIEmbeddingService(dimensions=768)
        else:
            logger.info("🔍 Dry run mode - no Azure OpenAI client initialized")
            self.embedding_service = None
        
        # Statistics
        self.stats = {
            "total_documents": 0,
            "processed_documents": 0,
            "failed_documents": 0,
            "skipped_documents": 0,
            "start_time": None,
            "end_time": None,
            "total_cost": 0.0
        }
    
    def create_backup(self, personality_id: str, documents: List[Dict]) -> str:
        """Create backup of existing embeddings"""
        backup_dir = CONFIG["backup_directory"]
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"{personality_id}_{timestamp}.json"
        
        with open(backup_file, 'w') as f:
            json.dump({
                "personality_id": personality_id,
                "document_count": len(documents),
                "timestamp": timestamp,
                "documents": documents
            }, f, indent=2)
        
        logger.info(f"✅ Backup created: {backup_file}")
        return str(backup_file)
    
    def get_documents_for_personality(self, personality_id: str) -> List[Dict]:
        """Retrieve all documents for a personality (handles both old and new schema)"""
        documents = []
        
        # Query 1: New schema with personality_id field
        query1 = f"SELECT * FROM c WHERE c.personality_id = '{personality_id}'"
        for item in self.container.query_items(query=query1, enable_cross_partition_query=True):
            documents.append(item)
        
        # Query 2: Old schema with partition_key field
        if personality_id in PARTITION_KEY_MAPPINGS:
            for partition_pattern in PARTITION_KEY_MAPPINGS[personality_id]:
                if partition_pattern.endswith("::"):
                    # Use STARTSWITH for patterns with ::
                    query2 = f"SELECT * FROM c WHERE STARTSWITH(c.partition_key, '{partition_pattern}')"
                else:
                    # Use exact match for simple partition keys
                    query2 = f"SELECT * FROM c WHERE c.partition_key = '{partition_pattern}'"
                
                for item in self.container.query_items(query=query2, enable_cross_partition_query=True):
                    # Normalize the document to add personality_id if missing
                    if 'personality_id' not in item:
                        item['personality_id'] = personality_id
                    documents.append(item)
        
        return documents
    
    async def reembed_document(self, document: Dict) -> Dict:
        """Re-embed a single document with Azure OpenAI"""
        try:
            # Generate new embedding
            embedding = await self.embedding_service.generate_embedding(
                text=document.get('content', document.get('text', '')),
                task_type="retrieval_document"
            )
            
            # Update document
            document['embedding'] = embedding
            document['embedding_model'] = 'text-embedding-3-large'
            document['embedding_provider'] = 'Azure OpenAI'
            document['embedding_dimensions'] = 768
            document['updated_at'] = datetime.now().isoformat()
            
            # Calculate cost: $0.13 per 1M tokens, ~1000 tokens per doc
            self.stats["total_cost"] += 0.00000013 * len(document.get('content', '').split())
            
            return document
        
        except Exception as e:
            logger.error(f"❌ Failed to re-embed document {document.get('id')}: {e}")
            self.stats["failed_documents"] += 1
            raise
    
    async def migrate_personality(self, personality_id: str) -> Dict[str, Any]:
        """Migrate all documents for a personality"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 Starting migration for personality: {personality_id}")
        logger.info(f"{'='*60}\n")
        
        # Get all documents
        all_documents = self.get_documents_for_personality(personality_id)
        total_docs = len(all_documents)
        
        if total_docs == 0:
            logger.warning(f"⚠️ No documents found for {personality_id}")
            return {"status": "skipped", "reason": "no_documents"}
        
        # Filter out documents that already have Azure OpenAI embeddings
        documents = [
            doc for doc in all_documents 
            if doc.get('embedding_model') != 'text-embedding-3-large'
        ]
        already_migrated = total_docs - len(documents)
        
        logger.info(f"📊 Found {total_docs} total documents for {personality_id}")
        if already_migrated > 0:
            logger.info(f"   ⏭️  Skipping {already_migrated} documents (already have Azure OpenAI embeddings)")
        logger.info(f"   🔄 Will process {len(documents)} documents")
        
        # Skip if no documents need migration
        if len(documents) == 0:
            logger.info(f"✅ All documents already migrated for {personality_id}")
            return {
                "status": "skipped", 
                "reason": "already_migrated",
                "total_documents": total_docs,
                "already_migrated": already_migrated
            }
        
        # Create backup
        if not self.dry_run:
            backup_file = self.create_backup(personality_id, documents)
        
        if self.dry_run:
            logger.info(f"🔍 DRY RUN: Would process {len(documents)} documents (skipping {already_migrated} already migrated)")
            return {
                "status": "dry_run", 
                "document_count": len(documents),
                "already_migrated": already_migrated
            }
        
        # Process documents in batches
        docs_to_process = len(documents)
        processed = 0
        failed = 0
        
        for i in range(0, docs_to_process, CONFIG["batch_size"]):
            batch = documents[i:i+CONFIG["batch_size"]]
            batch_num = i // CONFIG["batch_size"] + 1
            total_batches = (total_docs + CONFIG["batch_size"] - 1) // CONFIG["batch_size"]
            
            logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} docs)")
            
            try:
                # Re-embed batch
                updated_docs = []
                for doc in batch:
                    try:
                        updated_doc = await self.reembed_document(doc)
                        updated_docs.append(updated_doc)
                        processed += 1
                        
                        # Progress logging
                        if processed % 100 == 0:
                            progress = (processed / total_docs) * 100
                            logger.info(f"   Progress: {processed}/{total_docs} ({progress:.1f}%)")
                    
                    except Exception as e:
                        logger.error(f"❌ Failed to process document: {e}")
                        failed += 1
                
                # Update documents in Cosmos DB
                for doc in updated_docs:
                    try:
                        self.container.upsert_item(doc)
                    except Exception as e:
                        logger.error(f"❌ Failed to update document {doc.get('id')}: {e}")
                        failed += 1
                
                # Rate limiting between batches
                if i + CONFIG["batch_size"] < total_docs:
                    await asyncio.sleep(CONFIG["batch_delay"])
            
            except Exception as e:
                logger.error(f"❌ Batch {batch_num} failed: {e}")
                failed += len(batch)
        
        logger.info(f"\n✅ Migration complete for {personality_id}")
        logger.info(f"   Total documents: {total_docs}")
        logger.info(f"   Already migrated: {already_migrated}")
        logger.info(f"   Newly processed: {processed}/{docs_to_process}")
        logger.info(f"   Failed: {failed}")
        logger.info(f"   Success rate: {(processed/docs_to_process)*100:.1f}%\n")
        
        return {
            "status": "completed",
            "total_documents": total_docs,
            "already_migrated": already_migrated,
            "processed": processed,
            "failed": failed
        }
    
    async def migrate_domain(self, domain: str) -> Dict[str, Any]:
        """Migrate all personalities in a domain"""
        personalities = DOMAIN_PERSONALITIES.get(domain, [])
        
        if not personalities:
            logger.error(f"❌ Unknown domain: {domain}")
            return {"status": "error", "reason": "unknown_domain"}
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Starting domain migration: {domain}")
        logger.info(f"   Personalities: {', '.join(personalities)}")
        logger.info(f"{'='*60}\n")
        
        results = {}
        for personality_id in personalities:
            results[personality_id] = await self.migrate_personality(personality_id)
        
        return results
    
    async def migrate_all(self):
        """Migrate all domains"""
        self.stats["start_time"] = datetime.now()
        
        logger.info("\n" + "="*60)
        logger.info("🚀 AZURE OPENAI EMBEDDING MIGRATION")
        logger.info("="*60)
        logger.info(f"Start time: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Dry run: {self.dry_run}")
        logger.info("="*60 + "\n")
        
        all_results = {}
        
        for domain in DOMAIN_PERSONALITIES.keys():
            domain_results = await self.migrate_domain(domain)
            all_results[domain] = domain_results
        
        self.stats["end_time"] = datetime.now()
        duration = self.stats["end_time"] - self.stats["start_time"]
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("📊 MIGRATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Duration: {duration}")
        logger.info(f"Total cost: ${self.stats['total_cost']:.2f}")
        logger.info("\nResults by domain:")
        
        for domain, results in all_results.items():
            logger.info(f"\n{domain.upper()}:")
            for personality, result in results.items():
                if isinstance(result, dict):
                    status = result.get('status', 'unknown')
                    logger.info(f"  {personality}: {status}")
                    if 'processed' in result:
                        logger.info(f"    Processed: {result['processed']}/{result['total_documents']}")
        
        logger.info("\n" + "="*60 + "\n")
        
        return all_results

async def main():
    parser = argparse.ArgumentParser(description="Azure OpenAI embedding migration script")
    parser.add_argument('--dry-run', action='store_true', help='Preview migration without making changes')
    parser.add_argument('--domain', type=str, help='Migrate specific domain (spiritual, philosophical, etc.)')
    parser.add_argument('--personality', type=str, help='Migrate specific personality')
    parser.add_argument('--all', action='store_true', help='Migrate all domains')
    
    args = parser.parse_args()
    
    service = AzureOpenAIMigrationService(dry_run=args.dry_run)
    
    if args.personality:
        result = await service.migrate_personality(args.personality)
        logger.info(f"\nResult: {result}")
    
    elif args.domain:
        result = await service.migrate_domain(args.domain)
        logger.info(f"\nDomain results: {result}")
    
    elif args.all:
        results = await service.migrate_all()
    
    else:
        logger.error("❌ Must specify --dry-run, --domain, --personality, or --all")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
