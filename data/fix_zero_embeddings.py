"""
Fix Zero Embeddings Script

Re-embeds 13 personalities that have corrupted (all-zero) embeddings.
Uses Azure OpenAI text-embedding-3-large with 768 dimensions.

Affected Personalities:
- Spiritual: swami_vivekananda, jesus_christ
- Philosophical: aristotle, plato, socrates
- Leadership: benjamin_franklin, george_washington, martin_luther_king_jr
- Scientific: archimedes, leonardo_da_vinci
- Literary: rabindranath_tagore, william_shakespeare
- Psychology: sigmund_freud

Usage:
    # Dry run (preview only)
    python fix_zero_embeddings.py --dry-run
    
    # Re-embed specific personality
    python fix_zero_embeddings.py --personality swami_vivekananda
    
    # Re-embed all 13 personalities
    python fix_zero_embeddings.py --all
    
    # Skip backup (faster, but risky)
    python fix_zero_embeddings.py --all --no-backup
"""

import os
import sys
import argparse
import asyncio
import logging
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from azure.cosmos import CosmosClient
from services.azure_openai_embedding_service import AzureOpenAIEmbeddingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Zero-embedding personalities (identified from investigation)
ZERO_EMBEDDING_PERSONALITIES = [
    "swami_vivekananda",
    "aristotle",
    "plato",
    "socrates",
    "benjamin_franklin",
    "george_washington",
    "martin_luther_king_jr",
    "archimedes",
    "leonardo_da_vinci",
    "rabindranath_tagore",
    "william_shakespeare",
    "sigmund_freud",
    "jesus_christ"
]

# Personality ID variations (for querying database)
PERSONALITY_VARIATIONS = {
    "swami_vivekananda": ["swami_vivekananda", "Swami Vivekananda"],
    "aristotle": ["aristotle", "Aristotle"],
    "plato": ["plato", "Plato"],
    "socrates": ["socrates", "Socrates"],
    "benjamin_franklin": ["benjamin_franklin", "Benjamin Franklin"],
    "george_washington": ["george_washington", "George Washington"],
    "martin_luther_king_jr": ["martin_luther_king_jr", "Martin Luther King Jr"],
    "archimedes": ["archimedes", "Archimedes"],
    "leonardo_da_vinci": ["leonardo_da_vinci", "Leonardo da Vinci"],
    "rabindranath_tagore": ["rabindranath_tagore", "Rabindranath Tagore"],
    "william_shakespeare": ["william_shakespeare", "William Shakespeare"],
    "sigmund_freud": ["sigmund_freud", "Sigmund Freud"],
    "jesus_christ": ["jesus_christ", "Jesus Christ", "Jesus"]
}

CONFIG = {
    "batch_size": 50,  # Process 50 documents at a time
    "rate_limit_delay": 0.6,  # 100 requests/min for Azure OpenAI
    "backup_directory": Path(__file__).parent / "backups" / "zero_embeddings_fix"
}


def validate_embedding(embedding: List[float], min_non_zero: int = 100) -> bool:
    """
    Validate that embedding contains real values (not all zeros)
    
    Args:
        embedding: Embedding vector to validate
        min_non_zero: Minimum number of non-zero values required
        
    Returns:
        True if embedding is valid, False if corrupted
    """
    if not embedding or len(embedding) != 768:
        logger.error(f"❌ Invalid embedding length: {len(embedding) if embedding else 0}")
        return False
    
    # Count non-zero values
    non_zero = sum(1 for v in embedding if v != 0)
    if non_zero < min_non_zero:
        logger.error(f"❌ Embedding has only {non_zero}/768 non-zero values (min: {min_non_zero})")
        return False
    
    # Check average magnitude
    avg_magnitude = statistics.mean([abs(v) for v in embedding])
    if avg_magnitude < 0.001:
        logger.error(f"❌ Embedding avg magnitude too low: {avg_magnitude}")
        return False
    
    return True


class ZeroEmbeddingFixer:
    """Service for fixing zero embeddings"""
    
    def __init__(self, dry_run: bool = False, skip_backup: bool = False):
        self.dry_run = dry_run
        self.skip_backup = skip_backup
        
        # Initialize Cosmos DB
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            raise ValueError("AZURE_COSMOS_CONNECTION_STRING not set")
        
        self.cosmos_client = CosmosClient.from_connection_string(connection_string)
        self.database = self.cosmos_client.get_database_client('vimarsh-multi-personality')
        self.container = self.database.get_container_client('personality_vectors')
        
        # Initialize Azure OpenAI embedding service
        if not dry_run:
            logger.info("🔧 Initializing Azure OpenAI embedding service...")
            self.embedding_service = AzureOpenAIEmbeddingService(dimensions=768)
            logger.info("✅ Azure OpenAI embedding service initialized")
        else:
            logger.info("🔍 Dry run mode - no embedding service initialized")
            self.embedding_service = None
        
        # Statistics
        self.stats = {
            "total_documents": 0,
            "processed_documents": 0,
            "failed_documents": 0,
            "skipped_documents": 0,
            "validated_documents": 0,
            "start_time": None,
            "end_time": None,
            "total_cost": 0.0,
            "personalities_fixed": []
        }
    
    def create_backup(self, personality_id: str, documents: List[Dict]) -> Optional[str]:
        """Create backup of existing documents"""
        if self.skip_backup:
            logger.info("⏭️  Skipping backup (--no-backup flag)")
            return None
        
        backup_dir = CONFIG["backup_directory"]
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"{personality_id}_{timestamp}.json"
        
        backup_data = {
            "personality_id": personality_id,
            "document_count": len(documents),
            "timestamp": timestamp,
            "documents": [
                {
                    "id": doc.get("id"),
                    "embedding": doc.get("embedding", []),
                    "embedding_model": doc.get("embedding_model"),
                    "embedding_provider": doc.get("embedding_provider"),
                    "content_preview": doc.get("content", "")[:200]
                }
                for doc in documents
            ]
        }
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        logger.info(f"✅ Backup created: {backup_file}")
        return str(backup_file)
    
    def get_documents_for_personality(self, personality_id: str) -> List[Dict]:
        """Retrieve all documents for a personality (handles naming variations)"""
        documents = []
        seen_ids = set()
        
        variations = PERSONALITY_VARIATIONS.get(personality_id, [personality_id])
        
        for variation in variations:
            # Query by personality_id field
            query1 = f"SELECT * FROM c WHERE c.personality_id = '{variation}' AND IS_DEFINED(c.embedding)"
            try:
                for item in self.container.query_items(query=query1, enable_cross_partition_query=True):
                    if item['id'] not in seen_ids:
                        documents.append(item)
                        seen_ids.add(item['id'])
            except Exception as e:
                logger.warning(f"⚠️  Query failed for personality_id='{variation}': {e}")
            
            # Query by personality field (legacy)
            query2 = f"SELECT * FROM c WHERE c.personality = '{variation}' AND IS_DEFINED(c.embedding)"
            try:
                for item in self.container.query_items(query=query2, enable_cross_partition_query=True):
                    if item['id'] not in seen_ids:
                        documents.append(item)
                        seen_ids.add(item['id'])
            except Exception as e:
                logger.warning(f"⚠️  Query failed for personality='{variation}': {e}")
        
        return documents
    
    async def reembed_document(self, document: Dict) -> Dict:
        """Re-embed a single document with validation"""
        try:
            # Get content (try multiple field names)
            content = document.get('chunk_text') or document.get('content') or document.get('text') or ''
            if not content:
                logger.warning(f"⚠️  Document {document.get('id')} has no content field (chunk_text, content, or text)")
                self.stats["skipped_documents"] += 1
                return document
            
            # Truncate content if too long (Azure OpenAI text-embedding-3-large max 8192 tokens)
            # Rough estimate: 1 token ≈ 4 characters, so 8192 tokens ≈ 32,768 characters
            max_chars = 30000  # Conservative limit to stay under 8192 tokens
            if len(content) > max_chars:
                logger.warning(f"⚠️  Truncating document {document.get('id')} from {len(content)} to {max_chars} chars")
                content = content[:max_chars]
            
            # Generate new embedding
            logger.debug(f"   Generating embedding for document {document.get('id')[:50]}...")
            embedding = await self.embedding_service.generate_embedding(
                text=content,
                task_type="retrieval_document"
            )
            
            # Validate embedding
            if not validate_embedding(embedding):
                raise ValueError(f"Generated embedding validation failed for {document.get('id')}")
            
            self.stats["validated_documents"] += 1
            
            # Update document
            document['embedding'] = embedding
            document['embedding_model'] = 'text-embedding-3-large'
            document['embedding_provider'] = 'Azure OpenAI'
            document['embedding_dimensions'] = 768
            document['updated_at'] = datetime.now().isoformat()
            document['zero_embedding_fix_applied'] = True
            document['zero_embedding_fix_date'] = datetime.now().isoformat()
            
            # Calculate cost: $0.13 per 1M tokens, ~1000 tokens per doc
            tokens = len(content.split())
            self.stats["total_cost"] += 0.00000013 * tokens
            
            return document
        
        except Exception as e:
            logger.error(f"❌ Failed to re-embed document {document.get('id')}: {e}")
            self.stats["failed_documents"] += 1
            raise
    
    async def fix_personality(self, personality_id: str) -> Dict[str, Any]:
        """Fix zero embeddings for a personality"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🔧 Fixing zero embeddings for: {personality_id}")
        logger.info(f"{'='*80}\n")
        
        # Get all documents
        all_documents = self.get_documents_for_personality(personality_id)
        total_docs = len(all_documents)
        
        if total_docs == 0:
            logger.warning(f"⚠️  No documents found for {personality_id}")
            return {"status": "error", "reason": "no_documents"}
        
        logger.info(f"📊 Found {total_docs} documents for {personality_id}")
        
        # Check for zero embeddings
        zero_embedding_docs = []
        for doc in all_documents:
            emb = doc.get('embedding', [])
            if emb and len(emb) == 768:
                non_zero = sum(1 for v in emb if v != 0)
                if non_zero == 0:
                    zero_embedding_docs.append(doc)
        
        logger.info(f"   🔍 Found {len(zero_embedding_docs)} documents with zero embeddings")
        
        if len(zero_embedding_docs) == 0:
            logger.info(f"✅ No zero embeddings found for {personality_id}")
            return {
                "status": "skipped",
                "reason": "no_zero_embeddings",
                "total_documents": total_docs
            }
        
        # Create backup
        if not self.dry_run and not self.skip_backup:
            self.create_backup(personality_id, zero_embedding_docs)
        
        if self.dry_run:
            logger.info(f"🔍 DRY RUN: Would process {len(zero_embedding_docs)} documents")
            return {
                "status": "dry_run",
                "document_count": len(zero_embedding_docs),
                "total_documents": total_docs
            }
        
        # Process documents in batches
        logger.info(f"🚀 Processing {len(zero_embedding_docs)} documents...")
        processed = 0
        failed = 0
        
        for i in range(0, len(zero_embedding_docs), CONFIG["batch_size"]):
            batch = zero_embedding_docs[i:i + CONFIG["batch_size"]]
            logger.info(f"   📦 Processing batch {i//CONFIG['batch_size'] + 1} ({len(batch)} documents)...")
            
            for doc in batch:
                try:
                    # Re-embed
                    updated_doc = await self.reembed_document(doc)
                    
                    # Update in Cosmos DB
                    self.container.upsert_item(updated_doc)
                    processed += 1
                    self.stats["processed_documents"] += 1
                    
                    # Rate limiting
                    await asyncio.sleep(CONFIG["rate_limit_delay"])
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process document: {e}")
                    failed += 1
                    continue
            
            logger.info(f"   ✅ Batch complete: {processed} processed, {failed} failed")
        
        logger.info(f"\n✅ Completed {personality_id}: {processed} fixed, {failed} failed\n")
        
        return {
            "status": "success",
            "personality_id": personality_id,
            "processed": processed,
            "failed": failed,
            "total_documents": total_docs,
            "zero_embedding_count": len(zero_embedding_docs)
        }
    
    async def fix_all_personalities(self, specific_personality: Optional[str] = None) -> Dict[str, Any]:
        """Fix zero embeddings for all affected personalities"""
        self.stats["start_time"] = datetime.now()
        
        personalities = [specific_personality] if specific_personality else ZERO_EMBEDDING_PERSONALITIES
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 ZERO EMBEDDINGS FIX - Starting")
        logger.info(f"{'='*80}")
        logger.info(f"📋 Personalities to fix: {len(personalities)}")
        logger.info(f"🔍 Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        logger.info(f"💾 Backup: {'DISABLED' if self.skip_backup else 'ENABLED'}")
        logger.info(f"{'='*80}\n")
        
        results = {}
        
        for personality in personalities:
            try:
                result = await self.fix_personality(personality)
                results[personality] = result
                
                if result["status"] == "success":
                    self.stats["personalities_fixed"].append(personality)
                
            except Exception as e:
                logger.error(f"❌ Failed to fix {personality}: {e}")
                results[personality] = {"status": "error", "error": str(e)}
        
        self.stats["end_time"] = datetime.now()
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print summary of fix operation"""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 ZERO EMBEDDINGS FIX - SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"⏱️  Duration: {duration:.2f} seconds")
        logger.info(f"📝 Total documents processed: {self.stats['processed_documents']}")
        logger.info(f"✅ Successfully validated: {self.stats['validated_documents']}")
        logger.info(f"❌ Failed: {self.stats['failed_documents']}")
        logger.info(f"⏭️  Skipped: {self.stats['skipped_documents']}")
        logger.info(f"💰 Estimated cost: ${self.stats['total_cost']:.4f}")
        logger.info(f"\n🎯 Personalities fixed: {len(self.stats['personalities_fixed'])}/{len(ZERO_EMBEDDING_PERSONALITIES)}")
        
        if self.stats['personalities_fixed']:
            logger.info(f"   ✅ {', '.join(self.stats['personalities_fixed'])}")
        
        # Show failures
        failures = [p for p, r in results.items() if r.get("status") == "error"]
        if failures:
            logger.info(f"\n❌ Failed personalities: {len(failures)}")
            logger.info(f"   {', '.join(failures)}")
        
        logger.info(f"{'='*80}\n")


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Fix zero embeddings for personalities")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--all", action="store_true", help="Fix all 13 personalities with zero embeddings")
    parser.add_argument("--personality", type=str, help="Fix specific personality")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup creation (faster but risky)")
    
    args = parser.parse_args()
    
    if not args.all and not args.personality:
        parser.error("Must specify either --all or --personality <name>")
    
    if args.personality and args.personality not in ZERO_EMBEDDING_PERSONALITIES:
        logger.error(f"❌ Unknown personality: {args.personality}")
        logger.info(f"💡 Valid personalities: {', '.join(ZERO_EMBEDDING_PERSONALITIES)}")
        return
    
    try:
        fixer = ZeroEmbeddingFixer(dry_run=args.dry_run, skip_backup=args.no_backup)
        await fixer.fix_all_personalities(specific_personality=args.personality)
        
        logger.info("✅ Zero embeddings fix completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
