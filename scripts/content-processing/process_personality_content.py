#!/usr/bin/env python3
"""
Process Personality Content Script

This script processes all acquired personality content into chunks for RAG.
Run this to complete Phase 4 of the personality addition plan.
"""

import sys
import os
import logging
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.personality_content_processor import PersonalityContentProcessor

def main():
    """Main processing function"""
    print("🚀 Starting Personality Content Processing (Phase 4)")
    print("=" * 60)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Create processor
        processor = PersonalityContentProcessor()
        
        # Process all personalities
        print("📚 Processing content for all 25 personalities...")
        results = processor.process_all_personalities()
        
        # Display results summary
        print("\n" + "=" * 60)
        print("📊 PROCESSING RESULTS SUMMARY")
        print("=" * 60)
        
        total_chunks = 0
        total_tokens = 0
        total_sources = 0
        successful_personalities = 0
        
        for personality_id, result in results.items():
            status = "✅" if not result.errors else "⚠️"
            print(f"{status} {personality_id}:")
            print(f"   Sources: {result.total_sources}")
            print(f"   Chunks: {result.total_chunks}")
            print(f"   Tokens: {result.total_tokens:,}")
            print(f"   Quality: {result.average_quality_score:.2f}")
            print(f"   Time: {result.processing_time_seconds:.1f}s")
            
            if result.errors:
                print(f"   Errors: {len(result.errors)}")
                for error in result.errors[:3]:  # Show first 3 errors
                    print(f"     - {error}")
            
            print()
            
            total_chunks += result.total_chunks
            total_tokens += result.total_tokens
            total_sources += result.total_sources
            
            if not result.errors:
                successful_personalities += 1
        
        print("=" * 60)
        print("🎯 OVERALL SUMMARY")
        print("=" * 60)
        print(f"Personalities processed: {len(results)}")
        print(f"Successful: {successful_personalities}")
        print(f"Total sources: {total_sources}")
        print(f"Total chunks: {total_chunks:,}")
        print(f"Total tokens: {total_tokens:,}")
        print(f"Average chunks per personality: {total_chunks / len(results):.1f}")
        
        # Estimate content size
        estimated_embeddings_size = total_chunks * 1536 * 4 / (1024**3)  # OpenAI embeddings in GB
        print(f"Estimated embeddings size: {estimated_embeddings_size:.2f} GB")
        
        print("\n✅ Content processing complete!")
        print("📁 Processed chunks saved to: data/sources/processed_chunks/")
        print("\n🔥 Next steps:")
        print("1. Generate vector embeddings for chunks")
        print("2. Set up vector database storage")
        print("3. Implement enhanced RAG pipeline")
        print("4. Test content-backed responses")
        
        return True
        
    except Exception as e:
        logger.error(f"Content processing failed: {e}")
        print(f"\n❌ Processing failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
