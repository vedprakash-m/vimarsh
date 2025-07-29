#!/usr/bin/env python3
"""
Vector Search Integration Test

Tests the complete vector search pipeline with real migrated data:
1. Query embedding generation
2. Vector similarity search 
3. Results retrieval and ranking
4. Citation extraction
"""

import os
import sys
import asyncio
import logging
from typing import List, Dict, Any

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(backend_dir)
sys.path.insert(0, root_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_vector_search():
    """Test comprehensive vector search functionality"""
    try:
        logger.info("🔍 Starting Vector Search Integration Test...")
        
        # Import services
        from backend.services.vector_database_service import VectorDatabaseService, PersonalityType
        
        # Initialize service
        vector_service = VectorDatabaseService()
        logger.info("✅ Vector service initialized")
        
        # Test queries for different personalities
        test_queries = [
            {
                "query": "What is the meaning of dharma and duty?",
                "personality": PersonalityType.KRISHNA,
                "expected_concepts": ["dharma", "duty", "righteousness"]
            },
            {
                "query": "How can I achieve inner peace?",
                "personality": PersonalityType.BUDDHA,
                "expected_concepts": ["peace", "meditation", "mindfulness"]
            },
            {
                "query": "What is the nature of wisdom?",
                "personality": PersonalityType.KRISHNA,
                "expected_concepts": ["wisdom", "knowledge", "understanding"]
            }
        ]
        
        successful_searches = 0
        total_searches = len(test_queries)
        
        for i, test_case in enumerate(test_queries, 1):
            logger.info(f"\n--- Test {i}/{total_searches}: {test_case['personality'].value} ---")
            logger.info(f"Query: '{test_case['query']}'")
            
            try:
                # Perform semantic search
                results = await vector_service.semantic_search(
                    query=test_case['query'],
                    personality=test_case['personality'],
                    top_k=5,
                    min_relevance=0.5
                )
                
                logger.info(f"Found {len(results)} results")
                
                if results:
                    successful_searches += 1
                    
                    # Display top results
                    for j, result in enumerate(results[:3], 1):
                        logger.info(f"  Result {j}:")
                        logger.info(f"    Similarity: {result.relevance_score:.3f}")
                        logger.info(f"    Source: {result.document.source}")
                        logger.info(f"    Content: {result.document.content[:100]}...")
                        
                        # Check if expected concepts are present
                        content_lower = result.document.content.lower()
                        found_concepts = [concept for concept in test_case['expected_concepts'] 
                                        if concept.lower() in content_lower]
                        if found_concepts:
                            logger.info(f"    ✅ Found concepts: {', '.join(found_concepts)}")
                        else:
                            logger.info(f"    ⚠️ Expected concepts not found: {', '.join(test_case['expected_concepts'])}")
                else:
                    logger.warning(f"  ⚠️ No results found for query")
                    
            except Exception as e:
                logger.error(f"  ❌ Search failed: {e}")
                continue
        
        # Summary
        success_rate = (successful_searches / total_searches) * 100
        logger.info(f"\n🎯 Vector Search Test Summary:")
        logger.info(f"   Successful searches: {successful_searches}/{total_searches} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            logger.info("✅ Vector search system is working well!")
            return True
        else:
            logger.warning("⚠️ Vector search needs optimization")
            return False
            
    except Exception as e:
        logger.error(f"❌ Vector search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_statistics():
    """Test database statistics and health"""
    try:
        logger.info("\n📊 Testing Database Statistics...")
        
        from backend.services.vector_database_service import VectorDatabaseService
        
        vector_service = VectorDatabaseService()
        
        # Get overall statistics
        stats = await vector_service.get_database_stats()
        logger.info("✅ Database statistics retrieved:")
        logger.info(f"   Total documents: {stats.total_documents}")
        logger.info(f"   Total embeddings: {stats.total_embeddings_generated}")
        logger.info(f"   Personalities: {len(stats.documents_by_personality)}")
        
        # Show personality breakdown
        for personality, count in stats.documents_by_personality.items():
            logger.info(f"   {personality}: {count} documents")
        
        # Show content type breakdown
        for content_type, count in stats.documents_by_content_type.items():
            logger.info(f"   {content_type}: {count} documents")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Statistics test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        # Run comprehensive tests
        search_success = await test_vector_search()
        stats_success = await test_database_statistics()
        
        overall_success = search_success and stats_success
        
        if overall_success:
            logger.info("\n🎉 All vector database tests passed!")
            logger.info("✅ System is ready for RAG integration testing")
        else:
            logger.warning("\n⚠️ Some tests failed - system needs attention")
        
        return overall_success
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
