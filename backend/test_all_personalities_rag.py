#!/usr/bin/env python3
"""
Comprehensive RAG Test - All 25 Personalities
Tests RAG functionality and embedding quality for all personalities
"""

import asyncio
import json
import logging
import statistics
from services.enhanced_rag_service_v6 import EnhancedRAGService

logging.basicConfig(level=logging.WARNING)  # Suppress verbose logs
logger = logging.getLogger(__name__)


async def check_personality_embeddings(service: EnhancedRAGService, personality_id: str) -> dict:
    """Check embedding quality for a personality"""
    try:
        query = f"SELECT TOP 1 c.embedding FROM c WHERE c.personality_id = '{personality_id}' AND IS_DEFINED(c.embedding)"
        results = list(service.container.query_items(query=query, enable_cross_partition_query=True))
        
        if not results:
            return {"status": "❌ missing", "chunks": 0}
        
        emb = results[0].get('embedding', [])
        non_zero = sum(1 for v in emb if v != 0)
        
        # Count total chunks
        count_query = f"SELECT VALUE COUNT(1) FROM c WHERE c.personality_id = '{personality_id}' AND IS_DEFINED(c.embedding)"
        count_results = list(service.container.query_items(query=count_query, enable_cross_partition_query=True))
        chunk_count = count_results[0] if count_results else 0
        
        if non_zero == 0:
            return {"status": "❌ zero", "chunks": chunk_count}
        
        avg_mag = statistics.mean([abs(v) for v in emb])
        return {
            "status": "✅ healthy",
            "chunks": chunk_count,
            "avg_mag": round(avg_mag, 6),
            "non_zero": non_zero
        }
    except Exception as e:
        return {"status": f"❌ error: {str(e)[:50]}", "chunks": 0}


async def test_rag_for_personality(service: EnhancedRAGService, personality_id: str, query: str) -> dict:
    """Test RAG for a single personality"""
    try:
        response = await service.generate_rag_response(
            user_query=query,
            personality=personality_id
        )
        
        # Extract metrics
        chunks_used = response.get('chunks_used', 0)
        similarity = response.get('avg_similarity', 0.0)
        has_citations = len(response.get('citations', [])) > 0
        confidence = response.get('confidence', 0.0)
        
        # Determine RAG status
        rag_working = chunks_used > 0 and similarity > 0.0
        
        return {
            "personality": personality_id,
            "rag_working": rag_working,
            "chunks": chunks_used,
            "similarity": round(similarity, 3),
            "confidence": round(confidence, 3),
            "citations": has_citations
        }
    except Exception as e:
        return {
            "personality": personality_id,
            "rag_working": False,
            "error": str(e)[:100]
        }


async def test_all_personalities():
    """Test all 25 personalities"""
    
    # All 25 personalities grouped by domain
    personalities = {
        "Spiritual (5)": [
            ("krishna", "How can I overcome attachment?"),
            ("buddha", "What is the path to enlightenment?"),
            ("jesus_christ", "How should I love my enemies?"),
            ("rumi", "What is the nature of divine love?"),
            ("swami_vivekananda", "How can I serve humanity?")
        ],
        "Philosophical (6)": [
            ("marcus_aurelius", "How do I live virtuously?"),
            ("lao_tzu", "What is the way of nature?"),
            ("confucius", "What makes a person virtuous?"),
            ("aristotle", "What is the good life?"),
            ("plato", "What is justice?"),
            ("socrates", "How do I know myself?")
        ],
        "Leadership (6)": [
            ("chanakya", "What makes a good ruler?"),
            ("abraham_lincoln", "What is the nature of leadership?"),
            ("benjamin_franklin", "What are the virtues of success?"),
            ("george_washington", "What is duty?"),
            ("mahatma_gandhi", "What is non-violence?"),
            ("martin_luther_king_jr", "What is justice?")
        ],
        "Scientific (5)": [
            ("albert_einstein", "What is the nature of reality?"),
            ("isaac_newton", "How does the universe work?"),
            ("nikola_tesla", "What is the future of energy?"),
            ("archimedes", "What is the lever principle?"),
            ("leonardo_da_vinci", "How do art and science connect?")
        ],
        "Literary (2)": [
            ("rabindranath_tagore", "What is beauty?"),
            ("william_shakespeare", "What is love?")
        ],
        "Psychology (1)": [
            ("sigmund_freud", "What drives human behavior?")
        ]
    }
    
    service = EnhancedRAGService()
    
    print("\n" + "=" * 80)
    print("🔍 COMPREHENSIVE RAG TEST - ALL 25 PERSONALITIES")
    print("=" * 80)
    
    all_results = {}
    total_passed = 0
    total_failed = 0
    
    # Previously problematic personalities (had zero embeddings)
    zero_embedding_personalities = [
        "swami_vivekananda", "aristotle", "plato", "socrates",
        "benjamin_franklin", "george_washington", "martin_luther_king_jr",
        "archimedes", "leonardo_da_vinci", "rabindranath_tagore",
        "william_shakespeare", "sigmund_freud", "jesus_christ"
    ]
    
    for domain, tests in personalities.items():
        print(f"\n📂 {domain}")
        print("-" * 80)
        
        domain_results = []
        
        for personality_id, query in tests:
            # Check embedding quality first
            emb_status = await check_personality_embeddings(service, personality_id)
            
            # Test RAG
            rag_result = await test_rag_for_personality(service, personality_id, query)
            
            # Combine results
            result = {**emb_status, **rag_result}
            domain_results.append(result)
            
            # Track previously problematic personalities
            was_problematic = personality_id in zero_embedding_personalities
            status_icon = "🔄" if was_problematic else "  "
            
            # Determine pass/fail
            passed = result['rag_working'] and 'healthy' in result['status']
            if passed:
                total_passed += 1
                print(f"{status_icon}✅ {personality_id:25} | Chunks: {result['chunks']:5} | Sim: {result['similarity']:.3f} | {result['status']}")
            else:
                total_failed += 1
                error_msg = result.get('error', 'No error')[:50]
                print(f"{status_icon}❌ {personality_id:25} | {result['status']} | {error_msg}")
        
        all_results[domain] = domain_results
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    total_tests = total_passed + total_failed
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n✅ Passed: {total_passed}/{total_tests}")
    print(f"❌ Failed: {total_failed}/{total_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print(f"\n🔄 Previously Problematic Personalities (13):")
    print(f"   (Had zero embeddings - re-embedded on 2025-12-06)")
    
    for domain, results in all_results.items():
        for result in results:
            if result['personality'] in zero_embedding_personalities:
                status = "✅ FIXED" if result['rag_working'] else "❌ STILL BROKEN"
                print(f"   {status} - {result['personality']}: {result['similarity']:.3f} similarity, {result['chunks']} chunks")
    
    if total_passed == total_tests:
        print("\n🎉 SUCCESS! RAG is working for ALL 25 personalities!")
        print("   Zero-embedding remediation was successful.")
    elif total_passed >= total_tests * 0.8:
        print(f"\n⚠️  MOSTLY WORKING ({success_rate:.0f}% success rate)")
        print(f"   {total_failed} personalities still have issues")
    else:
        print(f"\n❌ FAILED - Only {success_rate:.0f}% success rate")
        print(f"   {total_failed} personalities have issues")
    
    print("\n" + "=" * 80)
    
    return all_results


if __name__ == "__main__":
    asyncio.run(test_all_personalities())
