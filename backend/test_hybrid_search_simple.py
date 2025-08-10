"""
Simplified test script for Hybrid Search Service

Tests basic functionality of the hybrid search implementation.
"""

import asyncio
import os
import sys

# Add the parent directory to the path to import our service
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.hybrid_search_service import HybridSearchService

async def test_hybrid_search():
    """Test the hybrid search service with simple queries"""
    
    print("🔍 Testing Hybrid Search Service...")
    
    # Initialize the service
    hybrid_search = HybridSearchService()
    
    # Wait for initialization
    await asyncio.sleep(2)
    
    print(f"🔧 Service initialized: {getattr(hybrid_search, 'is_initialized', 'unknown')}")
    
    # Simple test queries
    test_queries = [
        "dharma and duty",
        "wisdom and knowledge", 
        "love and compassion"
    ]
    
    print(f"🎯 Testing {len(test_queries)} basic queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: '{query}'")
        
        try:
            # Perform basic hybrid search
            results = await hybrid_search.hybrid_search(
                query=query,
                top_k=3
            )
            
            print(f"✅ Search completed")
            print(f"📊 Results count: {len(results) if results else 0}")
            
            if results and len(results) > 0:
                top_result = results[0]
                print(f"   📈 Top score: {getattr(top_result, 'hybrid_score', 'unknown')}")
                print(f"   🔍 Search method: {getattr(top_result, 'search_method', 'unknown')}")
                print(f"   📍 Rank: {getattr(top_result, 'rank_position', 'unknown')}")
                
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
    
    # Test personality-specific search
    print(f"\n🎭 Testing personality-specific search...")
    
    personality_tests = [
        "Krishna",
        "Buddha", 
        "Einstein"
    ]
    
    for personality in personality_tests:
        print(f"\n👤 Testing personality: {personality}")
        
        try:
            results = await hybrid_search.hybrid_search(
                query="wisdom",
                personality=personality,
                top_k=2
            )
            
            print(f"   ✅ Found {len(results) if results else 0} results")
            
            if results and len(results) > 0:
                print(f"      Best score: {getattr(results[0], 'hybrid_score', 'unknown')}")
            
        except Exception as e:
            print(f"   ❌ Personality search failed: {e}")
    
    # Test service statistics
    print(f"\n📊 Getting service statistics...")
    
    try:
        stats = await hybrid_search.get_search_stats()
        print(f"✅ Stats retrieved:")
        print(f"   Initialized: {stats.get('initialized', 'unknown')}")
        print(f"   Total docs: {stats.get('total_docs', 'unknown')}")
        print(f"   Vocabulary size: {stats.get('vocabulary_size', 'unknown')}")
        print(f"   Vector service: {stats.get('vector_service_available', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Could not get stats: {e}")
    
    print(f"\n🎉 Hybrid Search test completed!")

if __name__ == "__main__":
    asyncio.run(test_hybrid_search())
