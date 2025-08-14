#!/usr/bin/env python3
"""
Upload Personality Chunks to Cosmos DB
Script to upload all processed chunks before embedding generation
"""

import asyncio
import sys
import os
from services.cosmos_chunk_uploader import CosmosChunkUploader

async def upload_chunks_to_cosmos():
    """Upload all processed personality chunks to Cosmos DB"""
    
    print("🚀 Starting upload of personality chunks to Cosmos DB")
    print("=" * 60)
    
    # Verify environment variables
    required_vars = ["COSMOS_ENDPOINT", "COSMOS_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following environment variables:")
        for var in missing_vars:
            print(f"  export {var}=<your_value>")
        return False
    
    try:
        # Initialize uploader
        uploader = CosmosChunkUploader()
        
        # Upload all chunks
        print("📤 Uploading chunks to Cosmos DB...")
        summary = await uploader.upload_all_personality_chunks()
        
        # Display results
        print("\n" + "=" * 60)
        print("✅ UPLOAD COMPLETE!")
        print("=" * 60)
        print(f"📊 Total chunks processed: {summary['statistics']['total_chunks']:,}")
        print(f"✅ Successfully uploaded: {summary['statistics']['successful_uploads']:,}")
        print(f"❌ Failed uploads: {summary['statistics']['failed_uploads']:,}")
        print(f"⏭️ Duplicates skipped: {summary['statistics']['duplicate_skips']:,}")
        print(f"⏱️ Processing time: {summary['processing_time_seconds']:.2f} seconds")
        print(f"📈 Success rate: {summary['success_rate']:.1f}%")
        
        # Get detailed status
        print(f"\n📋 PERSONALITY BREAKDOWN:")
        print("-" * 60)
        status = await uploader.get_upload_status()
        
        for personality_id, stats in status["personality_breakdown"].items():
            chunks = stats['total_chunks']
            pending = stats['embeddings_pending']
            complete = stats['embeddings_complete']
            
            print(f"{personality_id:25} | {chunks:>6,} chunks | {pending:>6,} pending embeddings")
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Generate vector embeddings for all chunks")
        print("2. Update chunks with embeddings in Cosmos DB")
        print("3. Implement enhanced RAG pipeline")
        print("4. Test content-backed responses")
        
        return summary['success_rate'] > 95.0
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def main():
    """Main execution function"""
    success = asyncio.run(upload_chunks_to_cosmos())
    
    if success:
        print(f"\n🎉 Chunks successfully uploaded to Cosmos DB!")
        print("Ready for embedding generation phase.")
        sys.exit(0)
    else:
        print(f"\n💥 Upload failed or incomplete.")
        print("Please check errors and retry.")
        sys.exit(1)

if __name__ == "__main__":
    main()
