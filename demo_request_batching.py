#!/usr/bin/env python3
"""
Demo script for Request Batching and Deduplication System
Task 7.6: Cost optimization through intelligent batching and query deduplication

This script demonstrates:
1. Request batching for multiple queries
2. Query deduplication for identical requests
3. Cost savings through optimization
4. Performance improvements through parallel processing
"""

import asyncio
import sys
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

from cost_management.request_batcher import RequestBatcher, with_request_batching
from datetime import timedelta


def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def print_results(results, title: str):
    """Print formatted results"""
    print(f"\n{title}:")
    print("-" * 40)
    for i, result in enumerate(results, 1):
        status = "✅ DEDUPLICATED" if result.was_deduplicated else "🔄 PROCESSED"
        cost = f"${result.cost:.4f}" if result.cost > 0 else "$0.0000"
        time_ms = f"{result.processing_time*1000:.1f}ms"
        print(f"{i:2d}. {status} | {cost} | {time_ms} | {result.content[:50]}...")


def print_statistics(stats: dict):
    """Print formatted statistics"""
    print(f"\n📊 COST MANAGEMENT STATISTICS")
    print("-" * 40)
    print(f"Total Requests:       {stats['total_requests']}")
    print(f"Batched Requests:     {stats['batched_requests']}")
    print(f"Deduplicated:         {stats['deduplicated_requests']}")
    print(f"Batches Processed:    {stats['batches_processed']}")
    print(f"Average Batch Size:   {stats['average_batch_size']}")
    print(f"Deduplication Rate:   {stats['deduplication_hit_rate']:.1f}%")
    print(f"Batch Efficiency:     {stats['batch_efficiency']:.1f}%")
    print(f"Cost Saved:           ${stats['cost_saved']:.4f}")
    print(f"Active Cache Entries: {stats['active_cache_entries']}")


async def demo_basic_batching():
    """Demonstrate basic request batching"""
    print_header("DEMO 1: Basic Request Batching")
    
    # Create batcher with small batch size for quick demo
    batcher = RequestBatcher(
        batch_size=3,
        batch_timeout=1.0,
        dedup_window=timedelta(minutes=5)
    )
    
    print("Submitting 5 spiritual queries simultaneously...")
    
    queries = [
        ("What is the meaning of dharma?", "dharma"),
        ("How should one practice meditation?", "meditation"),
        ("What is the path to moksha?", "dharma"),
        ("How to develop devotion to Krishna?", "bhakti"),
        ("What are the principles of karma yoga?", "dharma")
    ]
    
    start_time = time.time()
    tasks = []
    
    for query, context in queries:
        task = batcher.submit_request(query, context, "demo_user")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    processing_time = time.time() - start_time
    
    print_results(results, "BATCH PROCESSING RESULTS")
    print(f"\n⏱️  Total Processing Time: {processing_time:.2f} seconds")
    print_statistics(batcher.get_statistics())
    
    return batcher


async def demo_deduplication(batcher: RequestBatcher):
    """Demonstrate query deduplication"""
    print_header("DEMO 2: Query Deduplication")
    
    print("Submitting duplicate queries to test deduplication...")
    
    # Submit duplicate queries that should be deduplicated
    duplicate_queries = [
        ("What is the meaning of dharma?", "dharma"),  # Duplicate from demo 1
        ("How to practice daily meditation?", "meditation"),  # New query
        ("What is the meaning of dharma?", "dharma"),  # Another duplicate
        ("What are the benefits of yoga?", "yoga"),  # New query
        ("How to practice daily meditation?", "meditation"),  # Duplicate of #2
    ]
    
    start_time = time.time()
    tasks = []
    
    for query, context in duplicate_queries:
        task = batcher.submit_request(query, context, "demo_user_2")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    processing_time = time.time() - start_time
    
    print_results(results, "DEDUPLICATION RESULTS")
    print(f"\n⏱️  Total Processing Time: {processing_time:.2f} seconds")
    print_statistics(batcher.get_statistics())
    
    return batcher


async def demo_high_throughput(batcher: RequestBatcher):
    """Demonstrate high throughput scenario"""
    print_header("DEMO 3: High Throughput with Mixed Optimization")
    
    print("Simulating high-throughput scenario with 15 queries...")
    
    # Mix of new and duplicate queries
    queries = [
        ("What is karma?", "dharma"),
        ("How to chant mantras?", "meditation"),
        ("What is karma?", "dharma"),  # Duplicate
        ("What is the Bhagavad Gita?", "scripture"),
        ("How to practice ahimsa?", "dharma"),
        ("What is karma?", "dharma"),  # Another duplicate
        ("How to chant mantras?", "meditation"),  # Duplicate
        ("What is divine love?", "bhakti"),
        ("How to surrender to God?", "bhakti"),
        ("What is the Bhagavad Gita?", "scripture"),  # Duplicate
        ("How to practice pranayama?", "yoga"),
        ("What is divine love?", "bhakti"),  # Duplicate
        ("How to serve humanity?", "karma_yoga"),
        ("What is the purpose of life?", "dharma"),
        ("How to practice pranayama?", "yoga"),  # Duplicate
    ]
    
    start_time = time.time()
    tasks = []
    
    for i, (query, context) in enumerate(queries):
        task = batcher.submit_request(query, context, f"user_{i%5}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    processing_time = time.time() - start_time
    
    print_results(results, "HIGH THROUGHPUT RESULTS")
    print(f"\n⏱️  Total Processing Time: {processing_time:.2f} seconds")
    
    # Analyze results
    deduplicated = sum(1 for r in results if r.was_deduplicated)
    processed = sum(1 for r in results if not r.was_deduplicated)
    
    print(f"\n📈 OPTIMIZATION ANALYSIS")
    print("-" * 40)
    print(f"Requests Processed:   {processed}")
    print(f"Requests Deduplicated: {deduplicated}")
    print(f"Optimization Rate:    {(deduplicated/len(results)*100):.1f}%")
    
    print_statistics(batcher.get_statistics())


@with_request_batching(enable_deduplication=True)
async def spiritual_guidance_query(query: str, context: str = "general") -> str:
    """Example function using the decorator"""
    # Simulate LLM processing time
    await asyncio.sleep(0.1)
    return f"Spiritual guidance for '{query}' in {context} context: Practice with devotion and understanding."


async def demo_decorator():
    """Demonstrate decorator usage"""
    print_header("DEMO 4: Decorator Integration")
    
    print("Using @with_request_batching decorator...")
    
    queries = [
        ("How to find inner peace?", "meditation"),
        ("What is the essence of yoga?", "yoga"),
        ("How to find inner peace?", "meditation"),  # Duplicate
        ("How to practice gratitude?", "bhakti"),
    ]
    
    start_time = time.time()
    tasks = []
    
    for query, context in queries:
        task = spiritual_guidance_query(query, context)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    processing_time = time.time() - start_time
    
    print(f"\nDECORATOR RESULTS:")
    print("-" * 40)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result}")
    
    print(f"\n⏱️  Total Processing Time: {processing_time:.2f} seconds")
    
    # Get statistics from global batcher
    from cost_management.request_batcher import get_request_batcher
    global_batcher = get_request_batcher()
    print_statistics(global_batcher.get_statistics())


async def main():
    """Run all demos"""
    print_header("🕉️  VIMARSH AI - REQUEST BATCHING & DEDUPLICATION DEMO")
    print("Task 7.6: AI Cost Optimization through Intelligent Request Management")
    print("\nThis demo showcases cost optimization features:")
    print("• Request batching for improved throughput")
    print("• Query deduplication for cost savings") 
    print("• Intelligent caching with similarity matching")
    print("• Context-aware processing optimization")
    print("• Decorator integration for seamless usage")
    
    try:
        # Run all demos
        batcher = await demo_basic_batching()
        await asyncio.sleep(0.5)  # Brief pause between demos
        
        batcher = await demo_deduplication(batcher)
        await asyncio.sleep(0.5)
        
        await demo_high_throughput(batcher)
        await asyncio.sleep(0.5)
        
        await demo_decorator()
        
        print_header("✅ COST OPTIMIZATION DEMO COMPLETED")
        print("Key Benefits Demonstrated:")
        print("• 🚀 Improved throughput through batching")
        print("• 💰 Cost savings through deduplication")
        print("• ⚡ Faster responses for cached queries")
        print("• 🎯 Context-aware optimization")
        print("• 🔧 Easy integration with decorators")
        print("\nTask 7.6 (Request Batching & Deduplication) is ready for production!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
