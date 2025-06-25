#!/usr/bin/env python3
"""
Test Script for Enhanced RAG Pipeline

Demonstrates the advanced text processing capabilities with verse boundary
preservation and Sanskrit term handling.
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / 'backend'
sys.path.append(str(backend_dir))

from rag.text_processor import AdvancedSpiritualTextProcessor, TextType

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_enhanced_processing():
    """Test the enhanced processing pipeline"""
    logger.info("=== Testing Enhanced Text Processing Pipeline ===")
    
    # Initialize enhanced processor
    processor = AdvancedSpiritualTextProcessor()
    
    # Find sample text files
    data_dir = Path("data/sources")
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return
    
    # Process all text files
    for text_file in data_dir.glob("*.txt"):
        logger.info(f"\n--- Processing {text_file.name} with Enhanced Pipeline ---")
        
        try:
            # Load content
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Process with enhanced pipeline
            enhanced_chunks = processor.process_text_advanced(content, str(text_file))
            
            logger.info(f"Created {len(enhanced_chunks)} enhanced chunks")
            
            # Analyze results
            total_sanskrit_terms = sum(len(chunk.sanskrit_terms) for chunk in enhanced_chunks)
            total_verse_refs = sum(len(chunk.verse_references) for chunk in enhanced_chunks)
            total_semantic_tags = sum(len(chunk.semantic_tags) for chunk in enhanced_chunks)
            avg_quality = sum(chunk.quality_score for chunk in enhanced_chunks) / len(enhanced_chunks)
            
            logger.info(f"Analysis Results:")
            logger.info(f"  Total Sanskrit terms: {total_sanskrit_terms}")
            logger.info(f"  Total verse references: {total_verse_refs}")
            logger.info(f"  Total semantic tags: {total_semantic_tags}")
            logger.info(f"  Average quality score: {avg_quality:.2f}")
            
            # Show sample enhanced chunk
            if enhanced_chunks:
                sample = enhanced_chunks[0]
                logger.info(f"\nSample Enhanced Chunk:")
                logger.info(f"  ID: {sample.chunk_id}")
                logger.info(f"  Text Type: {sample.text_type.value}")
                logger.info(f"  Quality Score: {sample.quality_score:.2f}")
                logger.info(f"  Sanskrit Terms: {sample.sanskrit_terms[:5]}...")  # First 5
                logger.info(f"  Semantic Tags: {sample.semantic_tags}")
                logger.info(f"  Verse References: {[str(ref) for ref in sample.verse_references]}")
                logger.info(f"  Content Preview: {sample.content[:150]}...")
            
            # Test quality filtering
            high_quality_chunks = processor.filter_high_quality_chunks(enhanced_chunks, min_quality=1.2)
            logger.info(f"High-quality chunks (score >= 1.2): {len(high_quality_chunks)}/{len(enhanced_chunks)}")
            
            # Test export functionality
            export_data = processor.export_chunks_for_vector_storage(enhanced_chunks[:3])  # First 3
            logger.info(f"Export format sample keys: {list(export_data[0].keys()) if export_data else 'None'}")
            
        except Exception as e:
            logger.error(f"Error processing {text_file}: {e}")
            import traceback
            traceback.print_exc()
    
    logger.info("\n=== Enhanced Text Processing Test Complete ===")


def test_verse_boundary_preservation():
    """Test specific verse boundary preservation"""
    logger.info("\n=== Testing Verse Boundary Preservation ===")
    
    processor = AdvancedSpiritualTextProcessor()
    
    # Test Bhagavad Gita content
    gita_content = """Chapter 2: Contents of the Gita Summarized

2.47 You have a right to perform your prescribed duty, but not to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.

2.48 Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure. Such equanimity is called yoga.

2.49 Far inferior indeed is mere action to the yoga of wisdom, O Arjuna. Seek refuge in wisdom. Pitiable are those who are motivated by the fruits of action."""
    
    chunks = processor.process_text_advanced(gita_content, "test_gita.txt", max_chunk_size=300)
    
    logger.info(f"Gita Test Results:")
    logger.info(f"  Created {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks):
        logger.info(f"  Chunk {i+1}:")
        logger.info(f"    Quality: {chunk.quality_score:.2f}")
        logger.info(f"    Verses: {[str(ref) for ref in chunk.verse_references]}")
        logger.info(f"    Sanskrit: {chunk.sanskrit_terms}")
        logger.info(f"    Tags: {chunk.semantic_tags}")
        logger.info(f"    Content: {chunk.content[:100]}...")


if __name__ == "__main__":
    try:
        test_enhanced_processing()
        test_verse_boundary_preservation()
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
