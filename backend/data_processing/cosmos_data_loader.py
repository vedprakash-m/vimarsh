"""
Cosmos DB Data Loader for Spiritual Texts
Task 8.8: Load and chunk source texts into production Cosmos DB

Manages the complete flow from source texts to production-ready chunks in Cosmos DB,
including validation, monitoring, and error handling.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
from dataclasses import dataclass, asdict

# Import our modules
from spiritual_text_manager import SpiritualTextDataManager, SpiritualTextSource
from text_ingestion import DataIngestionPipeline, ProcessedDocument
from backend.rag.storage_factory import get_vector_storage, VectorStorageInterface
from backend.rag.text_processor import AdvancedSpiritualTextProcessor, EnhancedTextChunk
from backend.rag.cosmos_vector_search import SpiritualTextChunk
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadingProgress:
    """Tracks progress of data loading operation."""
    
    total_sources: int = 0
    processed_sources: int = 0
    total_chunks: int = 0
    loaded_chunks: int = 0
    failed_chunks: int = 0
    
    current_source: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.start_time is None:
            self.start_time = datetime.now(timezone.utc)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_chunks == 0:
            return 0.0
        return (self.loaded_chunks / self.total_chunks) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total_processed = self.loaded_chunks + self.failed_chunks
        if total_processed == 0:
            return 100.0
        return (self.loaded_chunks / total_processed) * 100
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate operation duration in seconds."""
        if self.start_time is None:
            return None
        end = self.end_time or datetime.now(timezone.utc)
        return (end - self.start_time).total_seconds()


class CosmosDataLoader:
    """
    Main class for loading spiritual text data into Cosmos DB.
    
    Handles the complete pipeline from source registration to production deployment,
    with comprehensive monitoring and validation.
    """
    
    def __init__(self, 
                 sources_directory: str = "data/sources",
                 temp_directory: str = "data/temp",
                 embedding_model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the Cosmos DB data loader.
        
        Args:
            sources_directory: Directory containing source text files
            temp_directory: Temporary directory for processing
            embedding_model_name: Name of the embedding model to use
        """
        self.sources_directory = Path(sources_directory)
        self.temp_directory = Path(temp_directory)
        
        # Initialize components
        self.data_manager = SpiritualTextDataManager(str(self.sources_directory))
        self.text_processor = AdvancedSpiritualTextProcessor()
        self.ingestion_pipeline = DataIngestionPipeline(
            str(self.sources_directory), 
            str(self.temp_directory)
        )
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # Storage interface (will be initialized when needed)
        self.storage: Optional[VectorStorageInterface] = None
        
        # Progress tracking
        self.progress = LoadingProgress()
        
        logger.info(f"CosmosDataLoader initialized with sources: {self.sources_directory}")
    
    async def initialize_storage(self) -> bool:
        """
        Initialize the Cosmos DB vector storage.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing Cosmos DB vector storage...")
            self.storage = await get_vector_storage()
            
            # Test connection
            if hasattr(self.storage, 'test_connection'):
                connection_ok = await self.storage.test_connection()
                if not connection_ok:
                    logger.error("Cosmos DB connection test failed")
                    return False
            
            logger.info("Cosmos DB vector storage initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB storage: {str(e)}")
            self.progress.errors.append(f"Storage initialization failed: {str(e)}")
            return False
    
    def register_sample_sources(self) -> bool:
        """
        Register sample spiritual text sources for loading.
        
        Returns:
            True if sources registered successfully, False otherwise
        """
        try:
            logger.info("Registering sample spiritual text sources...")
            
            # Register Bhagavad Gita sample
            bhagavad_gita_source = SpiritualTextSource(
                source_id="bhagavad_gita_sample",
                title="Bhagavad Gita (Sample)",
                author="Sage Vyasa",
                translator="Multiple Sources",
                source_type="bhagavad_gita",
                language="English",
                file_path="bhagavad_gita_sample.txt",
                copyright_status="public_domain",
                attribution_required=True,
                attribution_text="From the Bhagavad Gita, ancient Hindu scripture"
            )
            
            # Register Mahabharata sample
            mahabharata_source = SpiritualTextSource(
                source_id="mahabharata_sample",
                title="Mahabharata (Sample)",
                author="Sage Vyasa",
                translator="Multiple Sources",
                source_type="mahabharata",
                language="English",
                file_path="mahabharata_sample.txt",
                copyright_status="public_domain",
                attribution_required=True,
                attribution_text="From the Mahabharata, ancient Hindu epic"
            )
            
            # Register sources
            success = True
            success &= self.data_manager.register_source(bhagavad_gita_source)
            success &= self.data_manager.register_source(mahabharata_source)
            
            if success:
                logger.info("Sample sources registered successfully")
                return True
            else:
                logger.error("Failed to register some sources")
                return False
                
        except Exception as e:
            logger.error(f"Failed to register sample sources: {str(e)}")
            self.progress.errors.append(f"Source registration failed: {str(e)}")
            return False
    
    def validate_sources(self) -> Dict[str, Any]:
        """
        Validate all registered sources for production readiness.
        
        Returns:
            Validation summary with details
        """
        logger.info("Validating registered sources...")
        
        sources = self.data_manager.list_sources()
        validation_results = {
            "total_sources": len(sources),
            "valid_sources": 0,
            "invalid_sources": 0,
            "warnings": 0,
            "source_details": {}
        }
        
        for source in sources:
            logger.info(f"Validating source: {source.source_id}")
            result = self.data_manager.validate_source(source.source_id)
            
            validation_results["source_details"][source.source_id] = result
            
            if result["valid"]:
                validation_results["valid_sources"] += 1
            else:
                validation_results["invalid_sources"] += 1
            
            validation_results["warnings"] += len(result.get("warnings", []))
        
        logger.info(f"Validation complete: {validation_results['valid_sources']}/{validation_results['total_sources']} sources valid")
        return validation_results
    
    async def process_source_to_chunks(self, source_id: str) -> List[SpiritualTextChunk]:
        """
        Process a single source into production-ready chunks.
        
        Args:
            source_id: ID of the source to process
            
        Returns:
            List of SpiritualTextChunk objects ready for storage
        """
        logger.info(f"Processing source to chunks: {source_id}")
        
        # Get source information
        source = self.data_manager.get_source(source_id)
        if not source:
            raise ValueError(f"Source not found: {source_id}")
        
        # Load source content
        content = self.data_manager.load_source_content(source_id)
        if not content:
            raise ValueError(f"Failed to load content for source: {source_id}")
        
        # Process into enhanced chunks
        enhanced_chunks = self.text_processor.process_text_advanced(
            content, 
            source.file_path,
            max_chunk_size=800  # Optimal for production
        )
        
        # Convert to SpiritualTextChunk format for Cosmos DB
        spiritual_chunks = []
        
        for i, chunk in enumerate(enhanced_chunks):
            try:
                # Generate embedding
                embedding = self.embedding_model.encode(chunk.content, convert_to_numpy=True)
                
                # Create SpiritualTextChunk
                spiritual_chunk = SpiritualTextChunk(
                    id=f"{source_id}_{i:04d}",
                    content=chunk.content,
                    source_id=source_id,
                    source_file=source.file_path,
                    source_type=source.source_type,
                    
                    # Extract verse information
                    chapter=chunk.verse_references[0].chapter if chunk.verse_references else None,
                    verse=chunk.verse_references[0].verse if chunk.verse_references else None,
                    
                    # Metadata
                    sanskrit_terms=chunk.sanskrit_terms,
                    semantic_tags=chunk.semantic_tags,
                    quality_score=chunk.quality_score,
                    
                    # Embedding vector
                    vector=embedding.tolist(),
                    
                    # Attribution and legal
                    attribution_text=source.attribution_text,
                    copyright_status=source.copyright_status,
                    
                    # Processing metadata
                    created_at=datetime.now(timezone.utc).isoformat(),
                    chunk_index=i,
                    total_chunks=len(enhanced_chunks)
                )
                
                spiritual_chunks.append(spiritual_chunk)
                
            except Exception as e:
                logger.error(f"Failed to process chunk {i} from source {source_id}: {str(e)}")
                self.progress.failed_chunks += 1
                self.progress.errors.append(f"Chunk processing failed: {source_id}_{i:04d} - {str(e)}")
        
        logger.info(f"Processed {len(spiritual_chunks)} chunks from source {source_id}")
        return spiritual_chunks
    
    async def load_chunks_to_cosmos(self, chunks: List[SpiritualTextChunk]) -> Tuple[int, int]:
        """
        Load chunks into Cosmos DB vector storage.
        
        Args:
            chunks: List of chunks to load
            
        Returns:
            Tuple of (successful_loads, failed_loads)
        """
        if not self.storage:
            raise RuntimeError("Storage not initialized. Call initialize_storage() first.")
        
        logger.info(f"Loading {len(chunks)} chunks to Cosmos DB...")
        
        successful_loads = 0
        failed_loads = 0
        
        # Load in batches for better performance
        batch_size = 10
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_start = i + 1
            batch_end = min(i + batch_size, len(chunks))
            
            logger.info(f"Loading batch {batch_start}-{batch_end} of {len(chunks)}")
            
            try:
                # Convert to storage format and load
                for chunk in batch:
                    try:
                        await self.storage.add_chunk(chunk)
                        successful_loads += 1
                        self.progress.loaded_chunks += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to load chunk {chunk.id}: {str(e)}")
                        failed_loads += 1
                        self.progress.failed_chunks += 1
                        self.progress.errors.append(f"Chunk load failed: {chunk.id} - {str(e)}")
                
                # Small delay between batches to avoid overwhelming the service
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Batch load failed for chunks {batch_start}-{batch_end}: {str(e)}")
                failed_loads += len(batch)
                self.progress.failed_chunks += len(batch)
                self.progress.errors.append(f"Batch load failed: {batch_start}-{batch_end} - {str(e)}")
        
        logger.info(f"Chunk loading complete: {successful_loads} successful, {failed_loads} failed")
        return successful_loads, failed_loads
    
    async def load_all_sources(self, validate_first: bool = True) -> Dict[str, Any]:
        """
        Load all registered and validated sources into Cosmos DB.
        
        Args:
            validate_first: Whether to validate sources before loading
            
        Returns:
            Summary of the loading operation
        """
        logger.info("Starting complete data loading operation...")
        
        self.progress = LoadingProgress()  # Reset progress
        
        try:
            # Initialize storage
            if not await self.initialize_storage():
                return {"success": False, "error": "Failed to initialize storage"}
            
            # Validate sources if requested
            if validate_first:
                validation_results = self.validate_sources()
                if validation_results["invalid_sources"] > 0:
                    self.progress.warnings.append(f"{validation_results['invalid_sources']} sources failed validation")
            
            # Get all validated sources
            sources = self.data_manager.list_sources(validated_only=validate_first)
            self.progress.total_sources = len(sources)
            
            if len(sources) == 0:
                return {"success": False, "error": "No validated sources found to load"}
            
            logger.info(f"Loading {len(sources)} validated sources...")
            
            total_successful_chunks = 0
            total_failed_chunks = 0
            
            # Process each source
            for source in sources:
                self.progress.current_source = source.source_id
                logger.info(f"Processing source: {source.source_id}")
                
                try:
                    # Process source to chunks
                    chunks = await self.process_source_to_chunks(source.source_id)
                    self.progress.total_chunks += len(chunks)
                    
                    # Load chunks to Cosmos DB
                    successful, failed = await self.load_chunks_to_cosmos(chunks)
                    
                    total_successful_chunks += successful
                    total_failed_chunks += failed
                    
                    self.progress.processed_sources += 1
                    logger.info(f"Completed source {source.source_id}: {successful} successful, {failed} failed")
                    
                except Exception as e:
                    logger.error(f"Failed to process source {source.source_id}: {str(e)}")
                    self.progress.errors.append(f"Source processing failed: {source.source_id} - {str(e)}")
            
            # Finalize progress
            self.progress.end_time = datetime.now(timezone.utc)
            self.progress.current_source = None
            
            # Prepare summary
            summary = {
                "success": True,
                "total_sources": self.progress.total_sources,
                "processed_sources": self.progress.processed_sources,
                "total_chunks": self.progress.total_chunks,
                "successful_chunks": total_successful_chunks,
                "failed_chunks": total_failed_chunks,
                "success_rate": self.progress.success_rate,
                "duration_seconds": self.progress.duration,
                "errors": self.progress.errors,
                "warnings": self.progress.warnings
            }
            
            logger.info(f"Data loading operation complete: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Data loading operation failed: {str(e)}")
            self.progress.errors.append(f"Operation failed: {str(e)}")
            self.progress.end_time = datetime.now(timezone.utc)
            
            return {
                "success": False,
                "error": str(e),
                "partial_results": {
                    "processed_sources": self.progress.processed_sources,
                    "loaded_chunks": self.progress.loaded_chunks,
                    "failed_chunks": self.progress.failed_chunks,
                    "errors": self.progress.errors
                }
            }
    
    def get_loading_progress(self) -> Dict[str, Any]:
        """
        Get current loading progress.
        
        Returns:
            Progress information dictionary
        """
        return {
            "total_sources": self.progress.total_sources,
            "processed_sources": self.progress.processed_sources,
            "total_chunks": self.progress.total_chunks,
            "loaded_chunks": self.progress.loaded_chunks,
            "failed_chunks": self.progress.failed_chunks,
            "current_source": self.progress.current_source,
            "progress_percentage": self.progress.progress_percentage,
            "success_rate": self.progress.success_rate,
            "duration_seconds": self.progress.duration,
            "is_complete": self.progress.end_time is not None
        }
    
    async def validate_loaded_data(self) -> Dict[str, Any]:
        """
        Validate data that has been loaded into Cosmos DB.
        
        Returns:
            Validation results
        """
        if not self.storage:
            return {"success": False, "error": "Storage not initialized"}
        
        logger.info("Validating loaded data in Cosmos DB...")
        
        try:
            # Get some sample queries to test retrieval
            test_queries = [
                "dharma and duty",
                "Krishna's teachings",
                "yoga and meditation",
                "Arjuna's questions"
            ]
            
            validation_results = {
                "queries_tested": len(test_queries),
                "successful_retrievals": 0,
                "failed_retrievals": 0,
                "query_details": {},
                "total_chunks_found": 0
            }
            
            for query in test_queries:
                try:
                    results = await self.storage.search(query, top_k=5)
                    
                    validation_results["successful_retrievals"] += 1
                    validation_results["total_chunks_found"] += len(results)
                    validation_results["query_details"][query] = {
                        "success": True,
                        "results_count": len(results),
                        "sample_result": results[0].content[:100] + "..." if results else None
                    }
                    
                except Exception as e:
                    validation_results["failed_retrievals"] += 1
                    validation_results["query_details"][query] = {
                        "success": False,
                        "error": str(e)
                    }
            
            validation_results["success"] = validation_results["failed_retrievals"] == 0
            logger.info(f"Data validation complete: {validation_results}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def load_document_chunks(self, 
                                  enhanced_chunks: List[EnhancedTextChunk], 
                                  source_file: str,
                                  text_type: Any) -> int:
        """
        Load enhanced text chunks from ingestion pipeline into Cosmos DB.
        
        Args:
            enhanced_chunks: List of EnhancedTextChunk from text ingestion
            source_file: Path to the source file
            text_type: Type of text (TextType enum)
            
        Returns:
            Number of successfully loaded chunks
        """
        if not self.storage:
            logger.error("Storage not initialized. Call initialize_storage() first.")
            return 0
        
        logger.info(f"Converting {len(enhanced_chunks)} enhanced chunks to spiritual chunks...")
        
        # Convert enhanced chunks to spiritual chunks
        spiritual_chunks = []
        for i, chunk in enumerate(enhanced_chunks):
            try:
                # Generate embedding for the chunk
                embedding = self.embedding_model.encode(chunk.text).tolist()
                
                # Create spiritual chunk
                spiritual_chunk = SpiritualTextChunk(
                    id=f"{Path(source_file).stem}_{i:04d}",
                    text=chunk.text,
                    source=str(source_file),
                    chapter=chunk.metadata.get('chapter'),
                    verse=chunk.metadata.get('verse'),
                    sanskrit_terms=chunk.metadata.get('sanskrit_terms', []),
                    embedding=embedding,
                    spiritual_theme=chunk.metadata.get('spiritual_theme'),
                    dharmic_context=chunk.metadata.get('dharmic_context')
                )
                
                spiritual_chunks.append(spiritual_chunk)
                
            except Exception as e:
                logger.error(f"Failed to convert chunk {i}: {str(e)}")
                self.progress.failed_chunks += 1
                self.progress.errors.append(f"Chunk conversion failed: {source_file}_{i:04d} - {str(e)}")
        
        # Load the spiritual chunks
        successful_loads, failed_loads = await self.load_chunks_to_cosmos(spiritual_chunks)
        
        logger.info(f"Document loading complete: {successful_loads}/{len(enhanced_chunks)} chunks loaded")
        return successful_loads


async def main():
    """Main function for running the Cosmos DB data loader."""
    logger.info("Starting Cosmos DB data loading process...")
    
    # Initialize loader
    loader = CosmosDataLoader()
    
    # Register sample sources
    if not loader.register_sample_sources():
        logger.error("Failed to register sources, aborting...")
        return
    
    # Load all sources
    results = await loader.load_all_sources(validate_first=True)
    
    if results["success"]:
        logger.info("Data loading completed successfully!")
        
        # Validate loaded data
        validation = await loader.validate_loaded_data()
        if validation["success"]:
            logger.info("Data validation passed!")
        else:
            logger.warning(f"Data validation issues: {validation}")
    else:
        logger.error(f"Data loading failed: {results}")
    
    # Print final summary
    print("\n" + "="*60)
    print("COSMOS DB DATA LOADING SUMMARY")
    print("="*60)
    print(f"Success: {results['success']}")
    if results["success"]:
        print(f"Sources Processed: {results['processed_sources']}/{results['total_sources']}")
        print(f"Chunks Loaded: {results['successful_chunks']}")
        print(f"Failed Chunks: {results['failed_chunks']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Duration: {results['duration_seconds']:.1f} seconds")
    else:
        print(f"Error: {results.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main())
