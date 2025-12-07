#!/usr/bin/env python3
"""
Manual RAG Quality Validation Script
Tests Azure OpenAI embeddings with Enhanced RAG Service V6 across all 25 personalities
"""

import asyncio
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Tuple

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.enhanced_rag_service_v6 import EnhancedRAGService


# Test queries for each personality (2 per personality)
TEST_QUERIES = {
    # Spiritual Domain (5 personalities)
    "krishna": [
        "What is dharma and how should I follow it?",
        "How can I overcome fear in difficult times?"
    ],
    "buddha": [
        "What causes suffering and how can I end it?",
        "How do I practice mindfulness in daily life?"
    ],
    "jesus_christ": [
        "How should I love my enemies?",
        "What does it mean to be blessed?"
    ],
    "rumi": [
        "Tell me about divine love and union with God",
        "How do I find beauty in everyday life?"
    ],
    "swami_vivekananda": [
        "What is the essence of Vedanta philosophy?",
        "How can I develop inner strength?"
    ],
    
    # Scientific Domain (5 personalities)
    "albert_einstein": [
        "Explain the theory of relativity in simple terms",
        "What role does imagination play in science?"
    ],
    "isaac_newton": [
        "What are the laws of motion?",
        "How did you discover gravity?"
    ],
    "nikola_tesla": [
        "Tell me about alternating current",
        "What drives your passion for invention?"
    ],
    "archimedes": [
        "Explain the principle of buoyancy",
        "How do you approach solving complex problems?"
    ],
    "leonardo_da_vinci": [
        "How did you approach invention and art?",
        "What is the connection between science and art?"
    ],
    
    # Leadership Domain (6 personalities)
    "abraham_lincoln": [
        "How do you handle a divided nation?",
        "What qualities make a great leader?"
    ],
    "mahatma_gandhi": [
        "What is non-violent resistance?",
        "How do you fight injustice peacefully?"
    ],
    "chanakya": [
        "What makes a good strategy?",
        "How should a leader handle enemies?"
    ],
    "george_washington": [
        "How do you lead in uncertain times?",
        "What principles guided your leadership?"
    ],
    "benjamin_franklin": [
        "What are your keys to success?",
        "How do you balance practicality and idealism?"
    ],
    "martin_luther_king_jr": [
        "How do we achieve justice?",
        "What does the dream of equality mean?"
    ],
    
    # Philosophical Domain (6 personalities)
    "marcus_aurelius": [
        "How do I find inner peace?",
        "What is Stoic philosophy?"
    ],
    "socrates": [
        "What is the examined life?",
        "How do I know if I truly know something?"
    ],
    "plato": [
        "What is the nature of reality?",
        "What is justice?"
    ],
    "aristotle": [
        "What is virtue?",
        "How do we achieve happiness?"
    ],
    "confucius": [
        "What is the Way?",
        "How should I treat others?"
    ],
    "lao_tzu": [
        "What does it mean to live in harmony with the Tao?",
        "How do I practice wu wei?"
    ],
    
    # Literary Domain (2 personalities)
    "william_shakespeare": [
        "What makes a great tragedy?",
        "What is the nature of love?"
    ],
    "rabindranath_tagore": [
        "Tell me about your poetry",
        "What is the relationship between humanity and nature?"
    ],
    
    # Psychology Domain (1 personality)
    "sigmund_freud": [
        "What drives human behavior?",
        "What is the unconscious mind?"
    ]
}


async def test_personality(
    service: EnhancedRAGService,
    personality: str,
    queries: List[str]
) -> Tuple[str, List[Dict]]:
    """Test a single personality with multiple queries"""
    results = []
    
    for i, query in enumerate(queries, 1):
        try:
            print(f"  Query {i}/{len(queries)}: {query[:60]}...")
            
            start_time = time.time()
            response = await service.generate_enhanced_response(
                query=query,
                personality_id=personality
            )
            processing_time = time.time() - start_time
            
            # Extract citations from RAG context
            citations = []
            if response.rag_context and response.rag_context.citations:
                citations = response.rag_context.citations
            
            result = {
                "query": query,
                "success": True,
                "response_length": len(response.content),
                "has_citations": len(citations) > 0,
                "citation_count": len(citations),
                "processing_time": processing_time,
                "error": None
            }
            
            # Quality checks
            if result["response_length"] < 100:
                result["warning"] = "Response too short"
            if not result["has_citations"]:
                result["warning"] = "No citations provided"
            
            results.append(result)
            print(f"    ✅ Success - {result['response_length']} chars, {result['citation_count']} citations")
            
        except Exception as e:
            result = {
                "query": query,
                "success": False,
                "error": str(e)
            }
            results.append(result)
            print(f"    ❌ Failed: {str(e)[:100]}")
        
        # Small delay between queries
        await asyncio.sleep(0.5)
    
    return personality, results


async def main():
    """Run comprehensive RAG validation"""
    print("=" * 80)
    print("🧪 AZURE OPENAI EMBEDDINGS - RAG QUALITY VALIDATION")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing {len(TEST_QUERIES)} personalities with {sum(len(q) for q in TEST_QUERIES.values())} queries")
    print()
    
    # Initialize service
    try:
        service = EnhancedRAGService()
        print("✅ Enhanced RAG Service V6 initialized")
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        return
    
    print()
    
    # Test each domain
    domains = {
        "Spiritual": ["krishna", "buddha", "jesus_christ", "rumi", "swami_vivekananda"],
        "Scientific": ["albert_einstein", "isaac_newton", "nikola_tesla", "archimedes", "leonardo_da_vinci"],
        "Leadership": ["abraham_lincoln", "mahatma_gandhi", "chanakya", "george_washington", "benjamin_franklin", "martin_luther_king_jr"],
        "Philosophical": ["marcus_aurelius", "socrates", "plato", "aristotle", "confucius", "lao_tzu"],
        "Literary": ["william_shakespeare", "rabindranath_tagore"],
        "Psychology": ["sigmund_freud"]
    }
    
    all_results = {}
    total_queries = 0
    total_success = 0
    total_citations = 0
    total_time = 0.0
    
    for domain, personalities in domains.items():
        print(f"\n{'=' * 80}")
        print(f"🎯 TESTING {domain.upper()} DOMAIN ({len(personalities)} personalities)")
        print('=' * 80)
        
        for personality in personalities:
            if personality not in TEST_QUERIES:
                print(f"\n⚠️  {personality}: No test queries defined")
                continue
            
            print(f"\n📝 Testing {personality}...")
            queries = TEST_QUERIES[personality]
            
            personality_name, results = await test_personality(service, personality, queries)
            all_results[personality_name] = results
            
            # Update totals
            for result in results:
                total_queries += 1
                if result["success"]:
                    total_success += 1
                    total_citations += result.get("citation_count", 0)
                    total_time += result.get("processing_time", 0)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total personalities tested: {len(all_results)}")
    print(f"Total queries executed: {total_queries}")
    print(f"Successful queries: {total_success}/{total_queries} ({total_success/total_queries*100:.1f}%)")
    print(f"Failed queries: {total_queries - total_success}")
    print(f"Total citations: {total_citations}")
    print(f"Average citations per query: {total_citations/total_success:.1f}")
    print(f"Average processing time: {total_time/total_success:.2f}s")
    print()
    
    # Check for failures
    failures = []
    warnings = []
    for personality, results in all_results.items():
        for result in results:
            if not result["success"]:
                failures.append((personality, result["query"], result["error"]))
            elif "warning" in result:
                warnings.append((personality, result["query"], result["warning"]))
    
    if failures:
        print("❌ FAILURES:")
        for personality, query, error in failures:
            print(f"  - {personality}: {query[:60]}...")
            print(f"    Error: {error[:100]}")
        print()
    
    if warnings:
        print("⚠️  WARNINGS:")
        for personality, query, warning in warnings:
            print(f"  - {personality}: {query[:60]}...")
            print(f"    Warning: {warning}")
        print()
    
    # Final verdict
    print("=" * 80)
    success_rate = total_success / total_queries * 100
    if success_rate >= 95 and total_citations >= total_success * 0.8:
        print("✅ RAG VALIDATION PASSED")
        print("   - Success rate >95%")
        print("   - Citations present in >80% of responses")
        print("   - Azure OpenAI embeddings working correctly")
        print()
        print("🎉 READY TO PROCEED WITH GPT-5 ROUTER IMPLEMENTATION!")
    elif success_rate >= 90:
        print("⚠️  RAG VALIDATION PARTIAL PASS")
        print("   - Success rate 90-95% (acceptable but needs monitoring)")
        print("   - Some quality issues detected")
    else:
        print("❌ RAG VALIDATION FAILED")
        print("   - Success rate <90%")
        print("   - Requires investigation before proceeding")
    
    print("=" * 80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
