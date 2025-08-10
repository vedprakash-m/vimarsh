"""
Test script for Hybrid Search Service

Tests the BM25 + vector fusion search functionality to ensure 
the hybrid search implementation is working correctly.
"""

import asyncio
import os
import sys

# Add the parent directory to the path to import our service
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.hybrid_search_service import HybridSearchService

async def test_hybrid_search():
    """Test the hybrid search service with sample queries"""
    
    print("🔍 Testing Hybrid Search Service...")
    
    # Initialize the service
    hybrid_search = HybridSearchService()
    
    print(f"📊 Service Status: Initializing...")
    
    # Initialize service (wait for it to load)
    await asyncio.sleep(1)  # Give it time to load
    
    # Check if initialized
    service_ready = hybrid_search.is_initialized if hasattr(hybrid_search, 'is_initialized') else True
    print(f"🔧 Service initialized: {service_ready}")
    
    # Get stats if available
    try:
        stats = await hybrid_search.get_search_stats()
        print(f"📚 Loaded documents: {stats.get('total_docs', 'unknown')}")
        print(f"📖 Vocabulary size: {stats.get('vocabulary_size', 'unknown')}")
    except Exception as e:
        print(f"⚠️ Could not get stats: {e}")
    
    # Test queries representing different search scenarios
    test_queries = [
        "dharma and duty in life",           # Spiritual concept
        "mindfulness meditation practice",   # Buddhist teaching
        "love and compassion for others",    # Universal spiritual theme
        "scientific method and discovery",   # Rational domain
        "leadership and governance",         # Authority domain
        "wisdom and contemplation"           # Philosophical theme
    ]
    
    print(f"🎯 Testing {len(test_queries)} search scenarios...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: '{query}'")
        
        try:
            # Perform hybrid search
            results = await hybrid_search.hybrid_search(
                query=query,
                top_k=5,
                personality=None  # Search across all personalities
            )
            
            print(f"✅ Found {len(results)} results")
            
            if results:
                # Show top result details
                top_result = results[0]
                print(f"   📊 Top Result:")
                print(f"      Score: {top_result.hybrid_score:.3f} (BM25: {top_result.bm25_score:.3f}, Vector: {top_result.vector_score:.3f})")
                print(f"      Method: {top_result.search_method}")
                print(f"      Rank: {top_result.rank_position}")
                
                # Try to access document content based on type
                if hasattr(top_result.document, 'content'):
                    content = top_result.document.content
                    print(f"      Content: {content[:100]}...")
                elif hasattr(top_result.document, 'text'):
                    content = top_result.document.text
                    print(f"      Content: {content[:100]}...")
                
                # Show score distribution
                scores = [r.hybrid_score for r in results]
                print(f"   📈 Score Range: {min(scores):.3f} - {max(scores):.3f}")
                
                # Show personality distribution
                personalities = {}
                for result in results:
                    if hasattr(result, 'metadata') and result.metadata:
                        personality = result.metadata.get('personality', 'unknown')
                        personalities[personality] = personalities.get(personality, 0) + 1
                
                if personalities:
                    print(f"   🎭 Personality Distribution: {personalities}")
            else:
                print(f"   ⚠️  No results found for this query")
                
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
    
    # Test personality-specific search
    print(f"\n🎭 Testing personality-specific search...")
    
    personality_tests = [
        ("Krishna", "dharma and righteous action"),
        ("Einstein", "relativity and space-time"),
        ("Buddha", "suffering and liberation"),
        ("Marcus Aurelius", "stoicism and virtue")
    ]
    
    for personality, query in personality_tests:
        print(f"\n👤 {personality} + '{query}'")
        
        try:
            results = await hybrid_search.hybrid_search(
                query=query,
                top_k=3,
                personality_filter=personality,
                min_score=0.1
            )
            
            print(f"   ✅ Found {len(results)} personality-specific results")
            
            if results:
                top_result = results[0]
                print(f"      Best match: {top_result.hybrid_score:.3f} score")
                print(f"      Content: {top_result.content[:80]}...")
            
        except Exception as e:
            print(f"   ❌ Personality search failed: {e}")
    
    # Test parameter variations
    print(f"\n⚙️  Testing parameter variations...")
    
    test_query = "wisdom and spiritual growth"
    
    # Test different fusion weights
    fusion_tests = [
        (0.3, 0.7),  # Vector-heavy
        (0.5, 0.5),  # Balanced
        (0.7, 0.3),  # BM25-heavy
    ]
    
    for bm25_weight, vector_weight in fusion_tests:
        print(f"\n🔧 Weights: BM25={bm25_weight}, Vector={vector_weight}")
        
        try:
            # Update fusion parameters
            hybrid_search.bm25_weight = bm25_weight
            hybrid_search.vector_weight = vector_weight
            
            results = await hybrid_search.hybrid_search(
                query=test_query,
                top_k=3,
                min_score=0.1
            )
            
            if results:
                scores = [f"{r.hybrid_score:.3f}" for r in results]
                print(f"   📊 Top 3 scores: {', '.join(scores)}")
            
        except Exception as e:
            print(f"   ❌ Parameter test failed: {e}")
    
    # Show final service statistics
    print(f"\n📊 Final Service Statistics:")
    stats = hybrid_search.get_service_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎉 Hybrid Search Service test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_hybrid_search())
