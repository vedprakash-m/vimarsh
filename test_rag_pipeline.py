#!/usr/bin/env python3
"""
Test Script for RAG Pipeline

This script demonstrates the complete text processing pipeline
with sample spiritual texts.
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / 'backend'
sys.path.append(str(backend_dir))

from rag_pipeline.text_processor import SpiritualTextProcessor
from rag_pipeline.document_loader import SpiritualDocumentLoader
from rag_pipeline.vector_storage import LocalVectorStorage, MockEmbeddingGenerator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_text_processing():
    """Test the text processing pipeline"""
    logger.info("=== Testing Text Processing Pipeline ===")
    
    # Initialize components
    processor = SpiritualTextProcessor()
    loader = SpiritualDocumentLoader()
    storage = LocalVectorStorage(storage_path="data/vectors", dimension=384)
    embedding_gen = MockEmbeddingGenerator(dimension=384)
    
    # Find sample text files
    data_dir = Path("data/sources")
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return
    
    # Process all text files in the data directory
    all_chunks = []
    
    for text_file in data_dir.glob("*.txt"):
        logger.info(f"\n--- Processing {text_file.name} ---")
        
        try:
            # Load document
            content, metadata = loader.load_text_file(text_file)
            logger.info(f"Loaded {metadata.filename}: {len(content)} characters")
            logger.info(f"Detected as: {metadata.text_type} ({metadata.source_tradition})")
            logger.info(f"Language: {metadata.language}")
            
            # Validate content
            validation = loader.validate_spiritual_content(content, metadata)
            logger.info(f"Validation: {'PASS' if validation['is_valid'] else 'FAIL'} "
                       f"(confidence: {validation['confidence']:.2f})")
            
            if validation['issues']:
                logger.warning(f"Issues: {', '.join(validation['issues'])}")
            
            # Process text into chunks
            chunks = processor.process_text(content, source_file=metadata.filename)
            logger.info(f"Created {len(chunks)} chunks")
            
            # Show sample chunk info
            if chunks:
                sample_chunk = chunks[0]
                logger.info(f"Sample chunk: {sample_chunk.chunk_id}")
                logger.info(f"Verse range: {sample_chunk.verse_range}")
                logger.info(f"Sanskrit terms: {sample_chunk.sanskrit_terms[:5]}")  # First 5 terms
                logger.info(f"Content preview: {sample_chunk.content[:100]}...")
            
            all_chunks.extend(chunks)
            
        except Exception as e:
            logger.error(f"Error processing {text_file}: {e}")
    
    # Test vector storage if we have chunks
    if all_chunks:
        logger.info(f"\n--- Testing Vector Storage ---")
        logger.info(f"Total chunks to store: {len(all_chunks)}")
        
        try:
            # Check if FAISS is available
            import faiss
            faiss_available = True
        except ImportError:
            logger.warning("FAISS not available, skipping vector storage test")
            faiss_available = False
        
        if faiss_available:
            # Generate embeddings
            texts = [chunk.content for chunk in all_chunks]
            embeddings = embedding_gen.generate_embeddings(texts)
            logger.info(f"Generated embeddings: {embeddings.shape}")
            
            # Store in vector database
            storage.add_chunks(all_chunks, embeddings)
            
            # Get storage statistics
            stats = storage.get_statistics()
            logger.info(f"Storage stats: {stats}")
            
            # Test search
            test_queries = [
                "What does Krishna teach about duty?",
                "Tell me about dharma and righteousness",
                "What is the nature of the soul?",
                "How should one perform action without attachment?"
            ]
            
            for query in test_queries:
                logger.info(f"\n--- Searching for: '{query}' ---")
                query_embedding = embedding_gen.generate_embeddings([query])[0]
                results = storage.search(query_embedding, k=3)
                
                for i, (chunk_id, similarity, metadata) in enumerate(results):
                    logger.info(f"Result {i+1}: {chunk_id} (similarity: {similarity:.3f})")
                    logger.info(f"Source: {metadata['source_file']}")
                    logger.info(f"Preview: {metadata['content_preview']}")
                    logger.info(f"Verse: {metadata.get('chunk_metadata', {}).get('verse_range', 'N/A')}")
    
    logger.info("\n=== Text Processing Pipeline Test Complete ===")


def test_individual_components():
    """Test individual components separately"""
    logger.info("\n=== Testing Individual Components ===")
    
    # Test text processor
    logger.info("\n--- Testing SpiritualTextProcessor ---")
    processor = SpiritualTextProcessor()
    
    sample_text = """Chapter 2: The Yoga of Knowledge

2.47 You have a right to perform your prescribed duty, but not to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.

2.48 Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure. Such equanimity is called yoga."""
    
    # Test preprocessing
    processed = processor.preprocess_text(sample_text)
    logger.info(f"Preprocessing: {len(sample_text)} -> {len(processed)} chars")
    
    # Test Sanskrit term extraction
    terms = processor.extract_sanskrit_terms(sample_text)
    logger.info(f"Sanskrit terms found: {terms}")
    
    # Test verse boundary detection
    boundaries = processor.identify_verse_boundaries(sample_text)
    logger.info(f"Verse boundaries: {boundaries}")
    
    # Test chunking
    chunks = processor.chunk_by_verses(sample_text)
    logger.info(f"Created {len(chunks)} chunks")
    for chunk in chunks:
        logger.info(f"  {chunk.chunk_id}: {chunk.verse_range} ({len(chunk.content)} chars)")
    
    # Test document loader
    logger.info("\n--- Testing SpiritualDocumentLoader ---")
    loader = SpiritualDocumentLoader()
    
    # Test text type identification
    test_cases = [
        ("The Bhagavad Gita teaches about dharma", "gita.txt"),
        ("The great epic Mahabharata tells of war", "mahabharata.txt"),
        ("Random text without spiritual content", "random.txt")
    ]
    
    for content, filename in test_cases:
        result = loader.identify_text_type(content, filename)
        logger.info(f"'{filename}': {result}")
    
    # Test language detection
    test_texts = [
        "This is English text with common words",
        "dharma karma moksha samsara brahman",
        "Mixed content with both English and dharma terms"
    ]
    
    for text in test_texts:
        lang = loader.detect_language(text)
        logger.info(f"Language detected for '{text[:30]}...': {lang}")


if __name__ == "__main__":
    try:
        test_individual_components()
        test_text_processing()
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
