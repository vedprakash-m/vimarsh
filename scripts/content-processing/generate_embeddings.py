#!/usr/bin/env python3
"""
CLI Script for Vector Embedding Generation
Generates embeddings for personality chunks using Google's text-embedding-004 model
"""

import os
import sys
import asyncio

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend')
sys.path.append(backend_path)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'))

from services.embedding_generator import EmbeddingGenerator

async def main():
    """Main CLI execution"""
    
    print("🚀 Vector Embedding Generator")
    print("=" * 50)
    
    # Check environment variables - support both connection string and endpoint+key methods
    has_connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
    has_endpoint_key = os.getenv("COSMOS_ENDPOINT") and os.getenv("COSMOS_KEY")
    has_gemini = os.getenv("GEMINI_API_KEY")
    
    if not has_gemini:
        print(f"❌ Missing required environment variable: GEMINI_API_KEY")
        sys.exit(1)
        
    if not (has_connection_string or has_endpoint_key):
        print(f"❌ Missing required Cosmos DB credentials")
        print("\nPlease set one of the following combinations:")
        print("  Option 1: export AZURE_COSMOS_CONNECTION_STRING=<your_connection_string>")
        print("  Option 2: export COSMOS_ENDPOINT=<endpoint> and COSMOS_KEY=<key>")
        print("\n💥 Embedding generation failed or incomplete.")
        print("Please check errors and retry.")
        sys.exit(1)
    
    try:
        generator = EmbeddingGenerator()
        
        # Check current status first
        print("📊 Checking current embedding status...")
        status = await generator.get_embedding_status()
        
        print(f"\n📊 Current Status:")
        print(f"Total chunks: {status['total_chunks']:,}")
        print(f"Pending: {status['overall_status'].get('pending', 0):,}")
        print(f"Complete: {status['overall_status'].get('complete', 0):,}")
        print(f"Failed: {status['overall_status'].get('failed', 0):,}")
        print(f"Completion: {status['completion_percentage']:.1f}%")
        
        if status['overall_status'].get('pending', 0) == 0:
            print("\n✅ All embeddings already generated!")
            
            # Show personality breakdown
            print(f"\n📊 Personality Breakdown:")
            for personality_id, stats in status['personality_breakdown'].items():
                total = stats['pending'] + stats['complete']
                print(f"  {personality_id}: {stats['complete']:,} chunks (100% complete)")
            
            return
        
        print(f"\n🔄 Starting embedding generation for {status['overall_status'].get('pending', 0):,} pending chunks...")
        
        # Generate embeddings
        summary = await generator.generate_embeddings_for_all_chunks()
        
        print("\n" + "=" * 60)
        print("✅ EMBEDDING GENERATION COMPLETE!")
        print("=" * 60)
        
        # Handle both success and failure cases
        if 'statistics' in summary:
            print(f"📊 Total chunks: {summary['statistics']['total_chunks']:,}")
            print(f"✅ Successfully processed: {summary['statistics']['processed_chunks']:,}")
            print(f"❌ Failed: {summary['statistics']['failed_chunks']:,}")
            print(f"📈 Success rate: {summary['success_rate']:.1f}%")
            print(f"⏱️ Processing time: {summary['processing_time_seconds']:.2f} seconds")
            print(f"🚀 Processing rate: {summary['processing_rate']:.1f} chunks/second")
            print(f"🔗 API calls made: {summary['statistics']['api_calls_made']:,}")
            print(f"📝 Total tokens processed: {summary['statistics']['total_tokens_processed']:,}")
        else:
            print(f"❌ Summary: {summary}")
            if 'error' in summary:
                print(f"Error details: {summary['error']}")
            return False
        
        print(f"\n👥 Personalities processed ({summary['statistics']['personalities_count']}):")
        for personality in sorted(summary['personalities_processed']):
            print(f"  ✅ {personality}")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Implement enhanced RAG pipeline")
        print(f"2. Test content-backed responses")
        print(f"3. Update frontend integration")
        print(f"4. Deploy to production")
        
        print(f"\n🎉 Ready for Phase 6: Enhanced RAG Pipeline!")
    
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
