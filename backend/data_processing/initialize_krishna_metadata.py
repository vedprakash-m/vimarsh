#!/usr/bin/env python3
"""
Initialize metadata for existing Krishna content in Cosmos DB.
This script creates metadata records for the 2025 Krishna documents that were migrated.
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from azure.cosmos.aio import CosmosClient

# Add the backend directory to Python path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from data_processing.metadata_manager import MetadataManager, BookMetadata, PersonalitySourceMapping

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KrishnaMetadataInitializer:
    """Initialize metadata for existing Krishna content."""
    
    def __init__(self):
        self.cosmos_client = None
        self.db = None
        self.metadata_manager = MetadataManager()
        
    async def initialize_cosmos_connection(self):
        """Initialize Cosmos DB connection"""
        try:
            cosmos_endpoint = os.getenv('COSMOS_ENDPOINT')
            cosmos_key = os.getenv('COSMOS_KEY')
            
            if not cosmos_endpoint or not cosmos_key:
                raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY environment variables are required")
            
            self.cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
            self.db = self.cosmos_client.get_database_client('vimarsh-multi-personality')
            logger.info("✅ Connected to Cosmos DB")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
            raise
            
    async def analyze_existing_krishna_content(self) -> Dict[str, int]:
        """Analyze existing Krishna content to understand structure"""
        try:
            container = self.db.get_container_client('personality-vectors')
            
            # Query Krishna documents
            query = "SELECT c.id, c.type, c.source, c.personality FROM c WHERE c.personality = 'krishna'"
            items = container.query_items(query=query, enable_cross_partition_query=True)
            
            document_analysis = {
                'total_documents': 0,
                'by_type': {},
                'by_source': {},
                'sample_ids': []
            }
            
            async for item in items:
                document_analysis['total_documents'] += 1
                
                # Analyze by type
                doc_type = item.get('type', 'unknown')
                document_analysis['by_type'][doc_type] = document_analysis['by_type'].get(doc_type, 0) + 1
                
                # Analyze by source
                source = item.get('source', 'unknown')
                document_analysis['by_source'][source] = document_analysis['by_source'].get(source, 0) + 1
                
                # Collect sample IDs
                if len(document_analysis['sample_ids']) < 10:
                    document_analysis['sample_ids'].append(item['id'])
            
            logger.info(f"📊 Analyzed {document_analysis['total_documents']} Krishna documents")
            logger.info(f"   Types: {document_analysis['by_type']}")
            logger.info(f"   Sources: {document_analysis['by_source']}")
            
            return document_analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze Krishna content: {e}")
            raise
            
    def create_krishna_book_metadata(self) -> List[BookMetadata]:
        """Create book metadata for existing Krishna sources"""
        books = []
        
        # Bhagavad Gita
        bhagavad_gita = BookMetadata(
            book_id="bhagavad_gita",
            title="The Bhagavad Gita",
            author="Attributed to Vyasa",
            source_url="https://archive.org/details/bhagavad-gita-as-it-is",
            language="sanskrit_english",
            translation="A.C. Bhaktivedanta Swami Prabhupada",
            publication_year=1972,
            total_chapters=18,
            total_verses=700,
            copyright_status="public_domain",
            quality_score=0.95,
            authenticity_verified=True,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            notes="Primary source for Krishna's teachings. Includes original Sanskrit, transliteration, and detailed purports."
        )
        books.append(bhagavad_gita)
        
        # Isopanishad 
        isopanishad = BookMetadata(
            book_id="isopanishad",
            title="Sri Isopanishad",
            author="Unknown (Vedic literature)",
            source_url="https://archive.org/details/isopanishad",
            language="sanskrit_english",
            translation="A.C. Bhaktivedanta Swami Prabhupada",
            publication_year=1974,
            total_chapters=1,
            total_verses=18,
            copyright_status="public_domain",
            quality_score=0.90,
            authenticity_verified=True,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            notes="One of the principal Upanishads, focusing on the Supreme Personality of Godhead."
        )
        books.append(isopanishad)
        
        return books
        
    def create_krishna_personality_mapping(self, document_analysis: Dict[str, int]) -> PersonalitySourceMapping:
        """Create personality mapping for Krishna"""
        return PersonalitySourceMapping(
            personality_id="krishna",
            personality_name="Lord Krishna",
            description="The Supreme Personality of Godhead, divine teacher of the Bhagavad Gita",
            primary_sources=["bhagavad_gita", "isopanishad"],
            secondary_sources=[],
            total_documents=document_analysis['total_documents'],
            quality_metrics={
                "authenticity_score": 0.95,
                "completeness_score": 0.90,
                "source_diversity": 0.80,
                "translation_quality": 0.95
            },
            content_types=document_analysis['by_type'],
            last_updated=datetime.utcnow(),
            notes="Existing Krishna content from legacy migration. Includes verses, commentary, and complete sections."
        )
        
    async def initialize_metadata(self):
        """Initialize metadata for Krishna content"""
        try:
            logger.info("🚀 Starting Krishna metadata initialization...")
            
            # 1. Analyze existing content
            document_analysis = await self.analyze_existing_krishna_content()
            
            # 2. Create book metadata
            krishna_books = self.create_krishna_book_metadata()
            
            # 3. Create personality mapping
            krishna_mapping = self.create_krishna_personality_mapping(document_analysis)
            
            # 4. Save metadata
            for book in krishna_books:
                self.metadata_manager.add_book(book)
                logger.info(f"📚 Added book metadata: {book.title}")
            
            self.metadata_manager.add_personality_mapping(krishna_mapping)
            logger.info(f"👤 Added personality mapping: {krishna_mapping.personality_name}")
            
            # 5. Save all metadata to files
            await self.metadata_manager.save_all_metadata()
            logger.info("💾 Saved all metadata to files")
            
            # 6. Create vector mappings for existing documents
            await self.create_vector_mappings(document_analysis)
            
            logger.info("🎉 Krishna metadata initialization completed!")
            
        except Exception as e:
            logger.error(f"❌ Metadata initialization failed: {e}")
            raise
            
    async def create_vector_mappings(self, document_analysis: Dict[str, int]):
        """Create vector mappings for existing Krishna documents"""
        try:
            container = self.db.get_container_client('personality-vectors')
            
            # Query all Krishna documents
            query = "SELECT c.id, c.type, c.source FROM c WHERE c.personality = 'krishna'"
            items = container.query_items(query=query, enable_cross_partition_query=True)
            
            vector_mappings = []
            
            async for item in items:
                doc_id = item['id']
                doc_type = item.get('type', 'unknown')
                source = item.get('source', '')
                
                # Determine book_id based on document ID patterns
                book_id = "bhagavad_gita"  # Default
                if "iso" in doc_id.lower() or "isopanishad" in doc_id.lower():
                    book_id = "isopanishad"
                
                vector_mapping = {
                    "vector_id": doc_id,
                    "personality_id": "krishna",
                    "book_id": book_id,
                    "content_type": doc_type,
                    "source_reference": source,
                    "created_at": datetime.utcnow().isoformat(),
                    "quality_score": 0.90  # Default for existing content
                }
                
                vector_mappings.append(vector_mapping)
            
            # Save vector mappings
            self.metadata_manager.vector_mappings = vector_mappings
            await self.metadata_manager.save_all_metadata()
            
            logger.info(f"🔗 Created {len(vector_mappings)} vector mappings")
            
        except Exception as e:
            logger.error(f"❌ Failed to create vector mappings: {e}")
            raise
            
    async def cleanup(self):
        """Clean up resources"""
        if self.cosmos_client:
            await self.cosmos_client.close()

async def main():
    """Main function"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    initializer = KrishnaMetadataInitializer()
    
    try:
        await initializer.initialize_cosmos_connection()
        await initializer.initialize_metadata()
        
        logger.info("✅ Krishna metadata initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Krishna metadata initialization failed: {e}")
        raise
    finally:
        await initializer.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
