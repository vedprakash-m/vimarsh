#!/usr/bin/env python3
"""
Cosmos DB Integration for Sourced Content
Loads the 1,534 sacred text entries from content sourcing into Cosmos DB.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import List, Dict
import sys

# Load environment variables from root .env file
try:
    from dotenv import load_dotenv
    # Load from root directory .env file
    root_env_path = Path(__file__).parent.parent.parent / '.env'
    if root_env_path.exists():
        load_dotenv(root_env_path)
        print(f"✅ Loaded environment variables from: {root_env_path}")
    else:
        print(f"⚠️ .env file not found at: {root_env_path}")
except ImportError:
    print("⚠️ python-dotenv not available. Install with: pip install python-dotenv")

try:
    from azure.cosmos import CosmosClient, PartitionKey
    from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosHttpResponseError
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False
    print("⚠️ Azure Cosmos DB SDK not available. Install with: pip install azure-cosmos")

# Try to import embedding service for vector generation
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from services.azure_openai_embedding_service import AzureOpenAIEmbeddingService
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    print("⚠️ Azure OpenAI embedding service not available. Vector search will not work.")

# Try to import config manager
try:
    from config.config_manager import get_cosmos_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CosmosDBIntegration:
    """Handles integration of sourced content with Cosmos DB including vector embeddings."""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.container = None
        self.integration_results = None
        self.embedding_service = None
        
    def initialize_embedding_service(self) -> bool:
        """Initialize the Azure OpenAI embedding service for vector generation."""
        if not EMBEDDING_AVAILABLE:
            logger.warning("⚠️ Embedding service not available - entries will not have vector embeddings")
            return False
            
        try:
            logger.info("🔧 Initializing Azure OpenAI embedding service...")
            self.embedding_service = AzureOpenAIEmbeddingService()
            logger.info("✅ Azure OpenAI embedding service initialized (text-embedding-3-large, dim=768)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize embedding service: {str(e)}")
            return False
        
    def load_integration_results(self) -> bool:
        """Load the integration results from content sourcing."""
        results_file = Path("vimarsh_content_integration/content_integration_results.json")
        
        if not results_file.exists():
            logger.error("❌ Integration results file not found! Run integrate_sourced_content.py first.")
            return False
        
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                self.integration_results = json.load(f)
            
            sacred_entries = self.integration_results.get('sacred_text_entries', [])
            logger.info(f"✅ Loaded {len(sacred_entries)} sacred text entries for database integration")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading integration results: {str(e)}")
            return False
    
    def setup_cosmos_client(self) -> bool:
        """Set up Cosmos DB client and container."""
        if not COSMOS_AVAILABLE:
            logger.error("❌ Azure Cosmos DB SDK not available")
            return False
        
        try:
            # Try to get connection string first (preferred method)
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING') or os.getenv('COSMOSDB_CONNECTION_STRING')
            
            if connection_string:
                # Parse connection string to get endpoint and key
                logger.info("✅ Using Cosmos DB connection string from environment")
                self.client = CosmosClient.from_connection_string(connection_string)
            else:
                # Fallback to individual endpoint and key
                endpoint = os.getenv('COSMOS_ENDPOINT')
                key = os.getenv('COSMOS_KEY')
                
                if not endpoint or not key:
                    logger.error("❌ Cosmos DB credentials not found in environment")
                    logger.info("   Set AZURE_COSMOS_CONNECTION_STRING or both COSMOS_ENDPOINT and COSMOS_KEY")
                    logger.info("   Example connection string format:")
                    logger.info("     AZURE_COSMOS_CONNECTION_STRING=AccountEndpoint=https://your-account.documents.azure.com:443/;AccountKey=your-key==;")
                    return False
                
                self.client = CosmosClient(endpoint, key)
            
            logger.info("✅ Cosmos DB client initialized")
            
            # Get database and container names from environment
            database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
            container_name = os.getenv('AZURE_COSMOS_CONTAINER_NAME', 'personality-vectors')
            
            # Get or create database
            try:
                self.database = self.client.create_database_if_not_exists(id=database_name)
                logger.info(f"✅ Connected to database: {database_name}")
            except Exception as e:
                logger.error(f"❌ Error accessing database {database_name}: {str(e)}")
                return False
            
            # Get or create container with vector support
            try:
                # Create container with vector policy for embedding support
                container_properties = {
                    "id": container_name,
                    "partitionKey": {
                        "paths": ["/personality"],
                        "kind": "Hash"
                    },
                    "vectorEmbeddingPolicy": {
                        "vectorEmbeddings": [
                            {
                                "path": "/embedding",
                                "dataType": "float32",
                                "distanceFunction": "cosine",
                                "dimensions": 768
                            }
                        ]
                    }
                }
                
                try:
                    self.container = self.database.create_container(
                        id=container_name,
                        partition_key=PartitionKey(path="/personality"),
                        offer_throughput=400
                    )
                    logger.info(f"✅ Created new container: {container_name}")
                except Exception as create_error:
                    # Container might already exist, try to get it
                    try:
                        self.container = self.database.get_container_client(container_name)
                        logger.info(f"✅ Connected to existing container: {container_name}")
                    except Exception as get_error:
                        logger.error(f"❌ Error accessing container {container_name}: {str(get_error)}")
                        return False
            except Exception as e:
                logger.error(f"❌ Error setting up container {container_name}: {str(e)}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up Cosmos DB: {str(e)}")
            return False
    
    def generate_embeddings_batch(self, entries: List[Dict], batch_size: int = 10) -> List[Dict]:
        """Generate embeddings for entries in batches for better performance."""
        if not self.embedding_service:
            logger.warning("⚠️ No embedding service available - skipping embedding generation")
            return entries
            
        logger.info(f"🧠 Generating embeddings for {len(entries)} entries in batches of {batch_size}")
        
        total_batches = (len(entries) + batch_size - 1) // batch_size
        processed_entries = []
        
        for batch_num in range(0, len(entries), batch_size):
            batch = entries[batch_num:batch_num + batch_size]
            current_batch = (batch_num // batch_size) + 1
            
            logger.info(f"   📦 Processing embedding batch {current_batch}/{total_batches} ({len(batch)} entries)")
            
            # Extract content for batch processing
            batch_contents = []
            batch_entries = []
            
            for entry in batch:
                content = entry.get('content', '')
                if content and len(content) >= 50:  # Only process meaningful content
                    batch_contents.append(content)
                    batch_entries.append(entry)
            
            if not batch_contents:
                logger.warning(f"   ⚠️ No valid content in batch {current_batch}")
                processed_entries.extend(batch)
                continue
            
            try:
                # Generate embeddings for the batch
                successful_embeddings = 0
                
                for i, (content, entry) in enumerate(zip(batch_contents, batch_entries)):
                    try:
                        # Azure OpenAI embedding service is async
                        import asyncio
                        embedding = asyncio.run(self.embedding_service.generate_embedding(content))
                        
                        if embedding:
                            entry['embedding'] = embedding
                            entry['embedding_model'] = 'text-embedding-3-large'
                            entry['embedding_dimensions'] = len(embedding)
                            entry['has_embedding'] = True
                            successful_embeddings += 1
                        else:
                            entry['has_embedding'] = False
                            logger.debug(f"     ⚠️ Failed to generate embedding for entry {entry.get('id', i)}")
                            
                    except Exception as e:
                        entry['has_embedding'] = False
                        logger.debug(f"     ❌ Embedding error for entry {entry.get('id', i)}: {str(e)}")
                
                logger.info(f"   ✅ Generated {successful_embeddings}/{len(batch_entries)} embeddings")
                processed_entries.extend(batch)
                
                # Add entries without content
                for entry in batch:
                    if entry not in batch_entries:
                        entry['has_embedding'] = False
                        processed_entries.append(entry)
                
                # Small delay between batches to avoid rate limiting
                if current_batch < total_batches:
                    import time
                    time.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"     ❌ Batch embedding generation failed: {str(e)}")
                # Add entries to processed list even if embedding failed
                for entry in batch:
                    entry['has_embedding'] = False
                processed_entries.extend(batch)
        
        embeddings_count = sum(1 for entry in processed_entries if entry.get('has_embedding'))
        logger.info(f"🧠 Embedding generation complete: {embeddings_count}/{len(processed_entries)} entries have embeddings")
        
        return processed_entries

    def validate_entries(self, entries: List[Dict]) -> List[Dict]:
        """Validate and prepare entries for Cosmos DB with vector embeddings."""
        logger.info(f"🔧 Validating {len(entries)} entries...")
        
        # Step 1: Basic validation and field normalization
        validated_entries = []
        
        for i, entry in enumerate(entries):
            try:
                # Ensure required fields
                if not entry.get('id'):
                    entry['id'] = f"sourced_entry_{i}"
                
                # Add partition key if missing
                if not entry.get('personality'):
                    # Extract from keywords or source
                    keywords = entry.get('keywords', [])
                    if keywords:
                        entry['personality'] = keywords[0].title()
                    else:
                        entry['personality'] = 'Unknown'
                
                # Ensure content field
                if not entry.get('content') and entry.get('text'):
                    entry['content'] = entry['text']
                elif not entry.get('text') and entry.get('content'):
                    entry['text'] = entry['content']
                
                # Add metadata for tracking
                entry['source_type'] = 'authenticated_public_domain'
                entry['integration_date'] = '2025-07-28'
                entry['content_sourcing_version'] = '1.0'
                
                # Validate content length
                content_length = len(entry.get('content', ''))
                if content_length < 50:
                    logger.warning(f"⚠️ Skipping entry {entry['id']} - too short ({content_length} chars)")
                    continue
                
                validated_entries.append(entry)
                
            except Exception as e:
                logger.error(f"❌ Error validating entry {i}: {str(e)}")
                continue
        
        logger.info(f"✅ Validated {len(validated_entries)} entries")
        
        # Step 2: Generate embeddings in batches
        if self.embedding_service:
            validated_entries = self.generate_embeddings_batch(validated_entries)
        else:
            # Mark all entries as having no embeddings
            for entry in validated_entries:
                entry['has_embedding'] = False
        
        embeddings_count = sum(1 for entry in validated_entries if entry.get('has_embedding'))
        logger.info(f"🎯 Final validation complete: {len(validated_entries)} entries, {embeddings_count} with embeddings")
        
        return validated_entries
    
    async def insert_entries_batch(self, entries: List[Dict], batch_size: int = 25) -> Dict[str, int]:
        """Insert entries into Cosmos DB in batches."""
        results = {
            'inserted': 0,
            'failed': 0,
            'duplicates': 0
        }
        
        total_batches = (len(entries) + batch_size - 1) // batch_size
        
        for batch_num in range(0, len(entries), batch_size):
            batch = entries[batch_num:batch_num + batch_size]
            current_batch = (batch_num // batch_size) + 1
            
            logger.info(f"📦 Processing batch {current_batch}/{total_batches} ({len(batch)} entries)")
            
            for entry in batch:
                try:
                    # Try to insert the entry
                    self.container.create_item(body=entry)
                    results['inserted'] += 1
                    
                    if results['inserted'] % 50 == 0:
                        logger.info(f"   ✅ Inserted {results['inserted']} entries so far...")
                    
                except CosmosResourceExistsError:
                    # Entry already exists
                    results['duplicates'] += 1
                    logger.debug(f"   ⚠️ Duplicate entry: {entry['id']}")
                    
                except CosmosHttpResponseError as e:
                    results['failed'] += 1
                    logger.error(f"   ❌ Failed to insert {entry['id']}: {str(e)}")
                    
                except Exception as e:
                    results['failed'] += 1
                    logger.error(f"   ❌ Unexpected error inserting {entry['id']}: {str(e)}")
            
            # Small delay between batches to avoid throttling
            if current_batch < total_batches:
                await asyncio.sleep(0.5)
        
        return results
    
    def generate_integration_report(self, results: Dict[str, int]) -> str:
        """Generate a detailed integration report."""
        total_entries = self.integration_results.get('total_entries_created', 0)
        sacred_entries = self.integration_results.get('sacred_text_entries', [])
        
        # Count entries with embeddings
        embeddings_count = sum(1 for entry in sacred_entries if entry.get('has_embedding'))
        
        report = f"""
# Cosmos DB Integration Report - {total_entries} Entries

## Integration Summary
- **Total entries processed**: {len(sacred_entries)}  
- **Successfully inserted**: {results['inserted']}
- **Duplicates skipped**: {results['duplicates']}
- **Failed insertions**: {results['failed']}
- **Success rate**: {(results['inserted'] / len(sacred_entries) * 100):.1f}%

## Vector Embeddings Summary
- **Entries with embeddings**: {embeddings_count}
- **Embedding coverage**: {(embeddings_count / len(sacred_entries) * 100):.1f}%
- **Embedding model**: gemini-embedding-001 (MRL)
- **Vector dimensions**: 768 (MRL-truncated, L2-normalized)
- **Vector search ready**: {'✅ Yes' if embeddings_count > 0 else '❌ No'}

## Personality Coverage in Database
"""
        
        # Count entries by personality
        personality_counts = {}
        for entry in sacred_entries:
            personality = entry.get('personality', 'Unknown')
            personality_counts[personality] = personality_counts.get(personality, 0) + 1
        
        for personality, count in sorted(personality_counts.items()):
            report += f"- **{personality}**: {count} entries\n"
        
        report += """
## Database Schema
Each entry includes:
- `id`: Unique identifier
- `content`/`text`: Main content
- `personality`: Partition key for efficient queries
- `domain`: Content domain (spiritual, scientific, etc.)
- `source`: Original work title
- `source_metadata`: Repository and authenticity info
- `embedding`: 768-dimensional vector for semantic search
- `embedding_model`: Model used for vector generation
- `has_embedding`: Boolean indicating vector search capability
- `integration_date`: Content sourcing date
- `source_type`: "authenticated_public_domain"

## Vector Search Capabilities
With embeddings generated, the system now supports:
- **Semantic similarity search** across personalities
- **Multi-personality RAG queries** (Buddha, Einstein, Newton, etc.)
- **Cross-domain content retrieval** (spiritual, scientific, philosophical)
- **Citation-backed responses** with source provenance

## Query Examples
```sql
-- Get all Buddha content with vector search capability
SELECT * FROM c WHERE c.personality = "Buddha" AND c.has_embedding = true

-- Vector similarity search (requires embedding comparison)
SELECT * FROM c 
WHERE VectorDistance(c.embedding, @query_vector) < 0.8
ORDER BY VectorDistance(c.embedding, @query_vector)

-- Content by domain with embeddings
SELECT * FROM c WHERE c.domain = "spiritual" AND c.has_embedding = true
```

## Next Steps
1. ✅ Sacred text entries loaded into Cosmos DB with vector embeddings
2. 🔄 Update RAG pipeline to query new multi-personality content
3. 🧪 Test semantic search across all 8 personalities
4. 📊 Monitor vector search performance and relevance scores
5. 🚀 Deploy enhanced multi-personality RAG system
"""
        
        return report
    
    async def run_integration(self) -> bool:
        """Run the complete Cosmos DB integration process with vector embeddings."""
        logger.info("🚀 Starting Cosmos DB integration for sourced content with vector embeddings")
        
        # Step 1: Load integration results
        if not self.load_integration_results():
            return False
        
        # Step 2: Initialize embedding service for vector generation
        embedding_initialized = self.initialize_embedding_service()
        if not embedding_initialized:
            logger.warning("⚠️ Proceeding without embeddings - vector search will not be available")
        
        # Step 3: Setup Cosmos DB connection
        if not self.setup_cosmos_client():
            return False
        
        # Step 4: Get sacred text entries
        sacred_entries = self.integration_results.get('sacred_text_entries', [])
        if not sacred_entries:
            logger.error("❌ No sacred text entries found in integration results")
            return False
        
        logger.info(f"📚 Preparing to insert {len(sacred_entries)} entries with vector embeddings")
        
        # Step 5: Validate entries and generate embeddings
        validated_entries = self.validate_entries(sacred_entries)
        if not validated_entries:
            logger.error("❌ No valid entries to insert")
            return False
        
        # Step 6: Insert entries in batches
        insertion_results = await self.insert_entries_batch(validated_entries)
        
        # Step 7: Generate report
        report = self.generate_integration_report(insertion_results)
        
        # Save report
        report_file = Path("cosmos_integration_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Step 8: Summary
        embeddings_count = sum(1 for entry in validated_entries if entry.get('has_embedding'))
        logger.info("🎉 Cosmos DB integration complete!")
        logger.info(f"✅ Inserted: {insertion_results['inserted']} entries")
        logger.info(f"🧠 Embeddings: {embeddings_count} vector embeddings generated")
        logger.info(f"⚠️ Duplicates: {insertion_results['duplicates']} entries")
        logger.info(f"❌ Failed: {insertion_results['failed']} entries")
        logger.info(f"📄 Report saved to: {report_file}")
        
        success_rate = (insertion_results['inserted'] / len(validated_entries)) * 100
        embedding_rate = (embeddings_count / len(validated_entries)) * 100
        
        if success_rate >= 90 and embedding_rate >= 80:
            logger.info("🎯 Integration highly successful with vector search ready!")
            return True
        elif success_rate >= 70:
            logger.info("✅ Integration successful with some issues")
            if embedding_rate < 50:
                logger.warning("⚠️ Low embedding coverage - vector search may be limited")
            return True
        else:
            logger.warning("⚠️ Integration completed with significant issues")
            return False

async def main():
    """Main integration workflow with vector embeddings."""
    print("🕉️ VIMARSH COSMOS DB INTEGRATION WITH VECTOR EMBEDDINGS")
    print("=" * 60)
    print()
    
    if not COSMOS_AVAILABLE:
        print("❌ Azure Cosmos DB SDK not installed!")
        print("   Install with: pip install azure-cosmos")
        return False
    
    if not EMBEDDING_AVAILABLE:
        print("⚠️ Gemini embedding service not available!")
        print("   Vector search will not be available without embeddings")
        print("   Proceeding with basic content insertion only...")
        print()
    
    integration = CosmosDBIntegration()
    success = await integration.run_integration()
    
    if success:
        print("\n🎉 COSMOS DB INTEGRATION SUCCESSFUL!")
        print("   Sacred text entries are now available for multi-personality queries")
        
        if EMBEDDING_AVAILABLE:
            print("   🧠 Vector embeddings generated for semantic search")
            print("   🔍 RAG system ready for: Buddha, Einstein, Newton, Rumi, etc.")
        else:
            print("   ⚠️ No vector embeddings - only basic text search available")
            
        print("   Next: Update RAG pipeline to include new personalities with vector search")
    else:
        print("\n❌ COSMOS DB INTEGRATION FAILED!")
        print("   Check logs and configuration, then retry")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
