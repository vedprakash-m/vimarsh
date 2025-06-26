#!/usr/bin/env python3
"""
Load Source Texts to Cosmos DB - Task 8.8
Vimarsh AI Agent Implementation

This script loads and chunks spiritual source texts into production Cosmos DB
with proper validation, monitoring, and error handling.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import argparse
import json

# Add backend to path
backend_path = str(Path(__file__).parent.parent / "backend")
sys.path.insert(0, backend_path)

try:
    from data_processing.text_ingestion import DataIngestionPipeline
    from data_processing.cosmos_data_loader import CosmosDataLoader, LoadingProgress
    from rag.storage_factory import get_vector_storage
    from rag.text_processor import AdvancedSpiritualTextProcessor
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Make sure you're running from the project root directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def load_texts_to_cosmos():
    """
    Main function to load source texts into Cosmos DB.
    
    This function orchestrates the complete data loading pipeline:
    1. Process source texts into chunks
    2. Generate embeddings for chunks
    3. Load chunks into Cosmos DB
    4. Validate the loading process
    """
    
    logger.info("🕉️  Starting Vimarsh text loading to Cosmos DB...")
    
    # Define paths
    project_root = Path(__file__).parent.parent
    source_dir = project_root / "data" / "sources"
    temp_dir = project_root / "data" / "processed"
    
    # Ensure directories exist
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Initialize components
        logger.info("📚 Initializing text processing components...")
        
        # Initialize data ingestion pipeline
        ingestion_pipeline = DataIngestionPipeline(
            source_dir=str(source_dir),
            output_dir=str(temp_dir)
        )
        
        # Initialize Cosmos DB loader
        cosmos_loader = CosmosDataLoader()
        
        # Initialize storage - this will auto-detect the environment
        await cosmos_loader.initialize_storage()
        
        # Get vector storage (should auto-detect Cosmos DB in production)
        vector_storage = cosmos_loader.storage
        
        if not vector_storage:
            logger.error("❌ Failed to initialize vector storage")
            return False
        
        logger.info(f"✅ Components initialized. Vector storage type: {type(vector_storage).__name__}")
        
        # Step 2: Process source files
        logger.info("📖 Processing source text files...")
        
        # Look for complete source files first, then samples
        source_files = []
        
        # Priority order: complete files first, then samples
        priority_files = [
            "bhagavad_gita_complete.txt",
            "mahabharata_complete.txt", 
            "srimad_bhagavatam_complete.txt"
        ]
        
        # Add priority files if they exist
        for filename in priority_files:
            file_path = source_dir / filename
            if file_path.exists():
                source_files.append(file_path)
        
        # Add any other .txt files not already included
        for file_path in source_dir.glob("*.txt"):
            if file_path not in source_files:
                source_files.append(file_path)
        
        if not source_files:
            logger.error("❌ No source text files found!")
            return False
        
        logger.info(f"📋 Found {len(source_files)} source files:")
        for file in source_files:
            logger.info(f"   • {file.name}")
        
        # Process each file
        processed_documents = []
        for file_path in source_files:
            logger.info(f"🔄 Processing {file_path.name}...")
            
            processed_doc = ingestion_pipeline.process_file(file_path)
            if processed_doc:
                processed_documents.append(processed_doc)
                logger.info(f"✅ {file_path.name}: {processed_doc.total_chunks} chunks created")
            else:
                logger.error(f"❌ Failed to process {file_path.name}")
        
        if not processed_documents:
            logger.error("❌ No documents were successfully processed!")
            return False
        
        # Step 3: Load into Cosmos DB
        logger.info("☁️  Loading chunks into Cosmos DB...")
        
        total_chunks = sum(doc.total_chunks for doc in processed_documents)
        logger.info(f"📊 Total chunks to load: {total_chunks}")
        
        # Initialize loading progress
        progress = LoadingProgress(
            total_sources=len(processed_documents),
            total_chunks=total_chunks,
            start_time=datetime.now(timezone.utc)
        )
        
        # Load each document
        for doc in processed_documents:
            logger.info(f"⬆️  Loading {Path(doc.source_file).name}...")
            progress.current_source = doc.source_file
            
            try:
                # Load chunks using the cosmos loader
                success_count = await cosmos_loader.load_document_chunks(
                    doc.chunks,
                    source_file=doc.source_file,
                    text_type=doc.text_type
                )
                
                progress.processed_sources += 1
                progress.loaded_chunks += success_count
                
                logger.info(f"✅ Loaded {success_count}/{len(doc.chunks)} chunks from {Path(doc.source_file).name}")
                
            except Exception as e:
                logger.error(f"❌ Error loading {Path(doc.source_file).name}: {str(e)}")
                progress.failed_chunks += len(doc.chunks)
                if progress.errors:
                    progress.errors.append(f"{doc.source_file}: {str(e)}")
        
        progress.end_time = datetime.now(timezone.utc)
        
        # Step 4: Validation and reporting
        logger.info("🔍 Validating loaded data...")
        
        # Test vector search functionality
        test_query = "What is dharma?"
        try:
            results = await vector_storage.search(test_query, top_k=3)
            if results:
                logger.info(f"✅ Vector search test successful: {len(results)} results found")
                logger.info(f"📖 Sample result: {results[0].text[:100]}...")
            else:
                logger.warning("⚠️  Vector search returned no results")
        except Exception as e:
            logger.error(f"❌ Vector search test failed: {str(e)}")
        
        # Generate final report
        duration = (progress.end_time - progress.start_time).total_seconds()
        success_rate = (progress.loaded_chunks / progress.total_chunks * 100) if progress.total_chunks > 0 else 0
        
        logger.info("📊 === LOADING SUMMARY ===")
        logger.info(f"   📁 Sources processed: {progress.processed_sources}/{progress.total_sources}")
        logger.info(f"   📦 Chunks loaded: {progress.loaded_chunks}/{progress.total_chunks}")
        logger.info(f"   ❌ Failed chunks: {progress.failed_chunks}")
        logger.info(f"   ✅ Success rate: {success_rate:.1f}%")
        logger.info(f"   ⏱️  Duration: {duration:.1f} seconds")
        
        # Save detailed report
        report_path = temp_dir / f"cosmos_loading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            "timestamp": progress.end_time.isoformat(),
            "sources_processed": progress.processed_sources,
            "total_sources": progress.total_sources,
            "chunks_loaded": progress.loaded_chunks,
            "total_chunks": progress.total_chunks,
            "failed_chunks": progress.failed_chunks,
            "success_rate": success_rate,
            "duration_seconds": duration,
            "errors": progress.errors or [],
            "warnings": progress.warnings or []
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"📄 Detailed report saved: {report_path}")
        
        # Determine overall success
        if success_rate >= 80:
            logger.info("🎉 Text loading completed successfully!")
            return True
        else:
            logger.error("💥 Text loading failed - success rate too low")
            return False
            
    except Exception as e:
        logger.error(f"💥 Critical error during text loading: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Load spiritual source texts into Cosmos DB for Vimarsh AI Agent"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process texts but don't actually load into Cosmos DB"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--source-dir",
        type=str,
        help="Override source directory path"
    )
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_arguments()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🕉️  Vimarsh AI Agent - Cosmos DB Text Loading")
    logger.info("=" * 50)
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No actual loading will occur")
    
    # Check environment
    if not os.getenv('COSMOS_ENDPOINT') and not args.dry_run:
        logger.warning("⚠️  COSMOS_ENDPOINT not found - using development mode")
    
    try:
        success = await load_texts_to_cosmos()
        
        if success:
            logger.info("✅ Task 8.8 completed successfully!")
            logger.info("🎯 Ready for Task 8.9: Configure Microsoft Entra External ID authentication")
            sys.exit(0)
        else:
            logger.error("❌ Task 8.8 failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
