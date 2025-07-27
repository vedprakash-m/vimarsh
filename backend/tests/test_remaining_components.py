"""
Test Remaining Components for Vimarsh Multi-Personality Platform

This script tests the newly implemented components:
- Domain-specific text processing
- Knowledge base management
- Content management integration
- Multi-domain RAG system
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from data_processing.domain_processors import DomainProcessorFactory, process_text_with_auto_domain as process_text
from services.knowledge_base_manager import knowledge_base_manager
from services.personality_service import personality_service

logger = logging.getLogger(__name__)


async def test_domain_processors():
    """Test domain-specific text processors"""
    print("\n🧪 Testing Domain-Specific Text Processors...")
    
    # Test cases for different domains
    test_cases = [
        {
            "domain": "spiritual",
            "text": """The Bhagavad Gita teaches us about dharma and karma. In verse 2.47, Krishna says: 
            "You have a right to perform your prescribed duty, but not to the fruits of action. 
            Never consider yourself to be the cause of the results of your activities, and never 
            be attached to not doing your duty." This wisdom guides us toward liberation and moksha.""",
            "source": "Bhagavad Gita"
        },
        {
            "domain": "scientific",
            "text": """Einstein's theory of relativity revolutionized our understanding of space and time. 
            The equation E=mc² demonstrates the relationship between energy and matter. According to 
            the principle of relativity, the laws of physics are the same in all inertial reference 
            frames. This theory has been confirmed through numerous experiments and observations.""",
            "source": "Relativity Theory"
        },
        {
            "domain": "historical",
            "text": """Fellow citizens, we are now engaged in a great civil war, testing whether this nation 
            or any nation conceived in liberty and dedicated to the proposition that all men are 
            created equal can long endure. The Constitution of the United States guarantees freedom 
            and democracy for all people.""",
            "source": "Lincoln Speech"
        },
        {
            "domain": "philosophical",
            "text": """The virtue of wisdom leads us to understand the nature of justice and truth. 
            Therefore, we must examine our beliefs through reason and logic. If we accept that 
            knowledge comes from experience, then we must conclude that virtue can be taught. 
            Thus, the pursuit of wisdom is the highest good.""",
            "source": "Philosophical Treatise"
        }
    ]
    
    successful_tests = 0
    
    for test_case in test_cases:
        try:
            print(f"\n🔬 Testing {test_case['domain']} domain...")
            
            # Process text using domain processor
            result = process_text(
                text=test_case["text"],
                domain=test_case["domain"],
                source=test_case["source"]
            )
            
            print(f"✅ Processing successful:")
            print(f"   - Chunks created: {len(result.chunks)}")
            print(f"   - Average quality: {result.quality_metrics.get('avg_quality', 0):.1f}%")
            
            # Show first chunk details
            if result.chunks:
                chunk = result.chunks[0]
                print(f"   - Citations found: {len(chunk.citations)}")
                print(f"   - Key terms: {len(chunk.key_terms)}")
                print(f"   - Chunk type: {chunk.chunk_type}")
                
                if chunk.citations:
                    print(f"   - Sample citations: {chunk.citations[:3]}")
                if chunk.key_terms:
                    print(f"   - Sample terms: {chunk.key_terms[:5]}")
            
            successful_tests += 1
            
        except Exception as e:
            print(f"❌ Failed for {test_case['domain']}: {e}")
    
    print(f"\n📊 Domain Processing Results: {successful_tests}/{len(test_cases)} successful")
    return successful_tests == len(test_cases)


async def test_knowledge_base_manager():
    """Test knowledge base management"""
    print("\n🧪 Testing Knowledge Base Manager...")
    
    try:
        # Get a test personality
        personalities = await personality_service.get_active_personalities()
        if not personalities:
            print("❌ No active personalities found for testing")
            return False
        
        test_personality = personalities[0]
        print(f"🎯 Testing with personality: {test_personality.display_name}")
        
        # Test content addition
        test_content = """This is a test content for knowledge base management. 
        It contains multiple sentences to test the chunking and embedding process. 
        The content should be processed according to the personality's domain and 
        stored with appropriate metadata and embeddings."""
        
        chunks_added = await knowledge_base_manager.add_content_to_knowledge_base(
            personality_id=test_personality.id,
            content=test_content,
            source="Test Content",
            domain=test_personality.domain.value,
            metadata={"test": True, "created_by": "test_script"}
        )
        
        print(f"✅ Added {chunks_added} chunks to knowledge base")
        
        # Test knowledge retrieval
        if chunks_added > 0:
            retrieval_result = await knowledge_base_manager.retrieve_knowledge(
                query="test content management",
                personality_id=test_personality.id,
                k=5,
                similarity_threshold=0.1  # Low threshold for testing
            )
            
            print(f"✅ Knowledge retrieval:")
            print(f"   - Retrieved chunks: {len(retrieval_result.chunks)}")
            print(f"   - Retrieval time: {retrieval_result.retrieval_time:.3f}s")
            print(f"   - Total results: {retrieval_result.total_results}")
            
            if retrieval_result.similarity_scores:
                print(f"   - Best similarity: {max(retrieval_result.similarity_scores):.3f}")
        
        # Test knowledge base stats
        stats = await knowledge_base_manager.get_knowledge_base_stats(test_personality.id)
        if stats:
            print(f"✅ Knowledge base stats:")
            print(f"   - Total chunks: {stats.total_chunks}")
            print(f"   - Domains: {stats.domains}")
            print(f"   - Average quality: {stats.avg_quality_score:.1f}%")
            print(f"   - Embedding model: {stats.embedding_model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Knowledge base manager test failed: {e}")
        return False


async def test_cross_personality_search():
    """Test cross-personality knowledge search"""
    print("\n🧪 Testing Cross-Personality Search...")
    
    try:
        # Test cross-personality search
        results = await knowledge_base_manager.cross_personality_search(
            query="wisdom and knowledge",
            domains=["spiritual", "philosophical"],
            k=3,
            similarity_threshold=0.1  # Low threshold for testing
        )
        
        print(f"✅ Cross-personality search results:")
        print(f"   - Personalities with results: {len(results)}")
        
        for personality_id, result in results.items():
            personality = await personality_service.get_personality(personality_id)
            personality_name = personality.display_name if personality else personality_id
            print(f"   - {personality_name}: {len(result.chunks)} chunks")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Cross-personality search failed: {e}")
        return False


async def test_domain_factory():
    """Test domain processor factory"""
    print("\n🧪 Testing Domain Processor Factory...")
    
    try:
        # Test available domains
        available_domains = DomainProcessorFactory.get_available_domains()
        print(f"✅ Available domains: {available_domains}")
        
        # Test processor creation
        successful_processors = 0
        for domain in available_domains:
            try:
                processor = DomainProcessorFactory.get_processor(domain)
                print(f"✅ Created {domain} processor: {processor.__class__.__name__}")
                successful_processors += 1
            except Exception as e:
                print(f"❌ Failed to create {domain} processor: {e}")
        
        print(f"📊 Processor creation: {successful_processors}/{len(available_domains)} successful")
        return successful_processors == len(available_domains)
        
    except Exception as e:
        print(f"❌ Domain factory test failed: {e}")
        return False


async def test_integration():
    """Test integration between components"""
    print("\n🧪 Testing Component Integration...")
    
    try:
        # Get personalities
        personalities = await personality_service.get_active_personalities()
        if not personalities:
            print("❌ No personalities for integration test")
            return False
        
        # Test end-to-end flow: process content -> add to knowledge base -> retrieve
        test_personality = personalities[0]
        
        # 1. Process content with domain processor
        test_text = "This is integration test content with wisdom and knowledge for testing the complete flow."
        
        processing_result = process_text(
            text=test_text,
            domain=test_personality.domain.value,
            source="Integration Test",
            metadata={"integration_test": True}
        )
        
        print(f"✅ Step 1 - Content processing: {len(processing_result.chunks)} chunks")
        
        # 2. Add to knowledge base
        chunks_added = await knowledge_base_manager.add_content_to_knowledge_base(
            personality_id=test_personality.id,
            content=test_text,
            source="Integration Test",
            domain=test_personality.domain.value,
            metadata={"integration_test": True}
        )
        
        print(f"✅ Step 2 - Knowledge base addition: {chunks_added} chunks added")
        
        # 3. Retrieve from knowledge base
        retrieval_result = await knowledge_base_manager.retrieve_knowledge(
            query="integration test content",
            personality_id=test_personality.id,
            k=5,
            similarity_threshold=0.1
        )
        
        print(f"✅ Step 3 - Knowledge retrieval: {len(retrieval_result.chunks)} chunks retrieved")
        
        # Check if we got back what we put in
        integration_successful = (
            len(processing_result.chunks) > 0 and
            chunks_added > 0 and
            len(retrieval_result.chunks) > 0
        )
        
        print(f"🎯 Integration test: {'✅ PASSED' if integration_successful else '❌ FAILED'}")
        return integration_successful
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


async def main():
    """Run all component tests"""
    print("🚀 Starting Remaining Components Test Suite")
    print("=" * 60)
    
    test_results = {}
    
    try:
        # Test 1: Domain Processors
        test_results["domain_processors"] = await test_domain_processors()
        
        # Test 2: Knowledge Base Manager
        test_results["knowledge_base_manager"] = await test_knowledge_base_manager()
        
        # Test 3: Cross-Personality Search
        test_results["cross_personality_search"] = await test_cross_personality_search()
        
        # Test 4: Domain Factory
        test_results["domain_factory"] = await test_domain_factory()
        
        # Test 5: Integration
        test_results["integration"] = await test_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 REMAINING COMPONENTS TEST RESULTS")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name.replace('_', ' ').title()}")
            if result:
                passed_tests += 1
        
        print(f"\n🎯 Overall Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🏆 ALL TESTS PASSED - New components are fully functional!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ MOSTLY FUNCTIONAL - Core new features working")
        else:
            print("⚠️ NEEDS ATTENTION - Multiple component failures")
        
        # Feature Status Summary
        print("\n📋 NEW COMPONENT STATUS:")
        print("✅ Domain-specific text processing - WORKING" if test_results.get("domain_processors") else "❌ Domain-specific text processing - FAILED")
        print("✅ Knowledge base management - WORKING" if test_results.get("knowledge_base_manager") else "❌ Knowledge base management - FAILED")
        print("✅ Cross-personality search - WORKING" if test_results.get("cross_personality_search") else "❌ Cross-personality search - FAILED")
        print("✅ Domain processor factory - WORKING" if test_results.get("domain_factory") else "❌ Domain processor factory - FAILED")
        print("✅ Component integration - WORKING" if test_results.get("integration") else "❌ Component integration - FAILED")
        
        print(f"\n🎉 Remaining components test complete!")
        print(f"📈 New components readiness: {(passed_tests/total_tests)*100:.1f}%")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())