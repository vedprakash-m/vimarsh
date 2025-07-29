#!/usr/bin/env python3
"""
Test script for Content Sourcing Pipeline
Validates functionality with safe, limited downloads.
"""

import asyncio
import logging
from pathlib import Path
import json

from content_sourcing_pipeline import EnhancedContentSourcingPipeline, ContentSource

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_single_source():
    """Test downloading from a single reliable source."""
    logger.info("🧪 Testing single source download...")
    
    # Use a small, reliable source for testing
    test_source = ContentSource(
        personality="Marcus Aurelius",
        domain="philosophical",
        work_title="Meditations",
        edition_translation="George W. Chrystal (translation)",
        repository="Project Gutenberg",
        download_url="http://www.gutenberg.org/ebooks/55317",
        format_type="html",
        authenticity_notes="Public domain. Multiple machine-readable formats available.",
        public_domain=True,
        priority=1,
        content_quality="high",
        estimated_chunks=300
    )
    
    pipeline = EnhancedContentSourcingPipeline(Path("./test_downloads"))
    pipeline.base_path.mkdir(exist_ok=True)
    
    content = await pipeline.download_content_with_retry(test_source)
    
    if content:
        logger.info(f"✅ Successfully downloaded {len(content)} characters")
        logger.info(f"📝 First 200 characters: {content[:200]}...")
        
        # Test chunking
        chunks = pipeline._chunk_text(content)
        logger.info(f"📚 Created {len(chunks)} chunks from content")
        
        # Test conversion to sacred text format
        processed_content = {
            test_source.source_id: {
                'personality': test_source.personality,
                'domain': test_source.domain,
                'work_title': test_source.work_title,
                'content': content,
                'source_metadata': {
                    'edition_translation': test_source.edition_translation,
                    'repository': test_source.repository,
                    'authenticity_notes': test_source.authenticity_notes,
                    'public_domain': test_source.public_domain
                }
            }
        }
        
        sacred_entries = pipeline.convert_to_sacred_text_entries(processed_content)
        logger.info(f"🔄 Converted to {len(sacred_entries)} sacred text entries")
        
        # Save test results
        with open("test_results.json", 'w', encoding='utf-8') as f:
            json.dump({
                "source_info": {
                    "personality": test_source.personality,
                    "work_title": test_source.work_title,
                    "content_length": len(content),
                    "chunks_created": len(chunks),
                    "sacred_entries": len(sacred_entries)
                },
                "sample_content": content[:500],
                "sample_chunks": chunks[:2] if chunks else [],
                "sample_sacred_entry": sacred_entries[0] if sacred_entries else None
            }, f, indent=2, ensure_ascii=False)
        
        return True
    else:
        logger.error("❌ Failed to download test content")
        return False

async def test_multiple_priorities():
    """Test downloading from multiple sources with different priorities."""
    logger.info("🧪 Testing multiple source downloads...")
    
    pipeline = EnhancedContentSourcingPipeline(Path("./test_multi_downloads"))
    pipeline.base_path.mkdir(exist_ok=True)
    
    # Get only high-priority, small sources for testing
    all_sources = pipeline.get_priority_sources()
    test_sources = [s for s in all_sources if s.priority == 1][:3]  # Test first 3 priority sources
    
    logger.info(f"📚 Testing with {len(test_sources)} sources:")
    for source in test_sources:
        logger.info(f"  - {source.personality}: {source.work_title}")
    
    # Process with limited sources
    processed_content = await pipeline.process_priority_sources(max_sources=len(test_sources))
    
    logger.info(f"✅ Processing complete!")
    logger.info(f"📊 Statistics: {pipeline.processing_stats}")
    
    if processed_content:
        # Convert to sacred text entries
        sacred_entries = pipeline.convert_to_sacred_text_entries(processed_content)
        
        # Save detailed test results
        test_results = {
            "test_metadata": {
                "sources_attempted": len(test_sources),
                "sources_successful": len(processed_content),
                "sacred_entries_created": len(sacred_entries),
                "processing_stats": pipeline.processing_stats
            },
            "source_details": [],
            "sample_entries": sacred_entries[:3] if sacred_entries else []
        }
        
        for source_id, content_data in processed_content.items():
            test_results["source_details"].append({
                "source_id": source_id,
                "personality": content_data["personality"],
                "work_title": content_data["work_title"],
                "content_length": len(content_data["content"]),
                "domain": content_data["domain"]
            })
        
        with open("multi_source_test_results.json", 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        logger.info("💾 Test results saved to multi_source_test_results.json")
        return True
    else:
        logger.error("❌ No content was successfully processed")
        return False

def test_content_statistics():
    """Test content statistics generation."""
    logger.info("🧪 Testing content statistics...")
    
    from content_sourcing_pipeline import get_content_statistics
    
    stats = get_content_statistics()
    
    logger.info("📊 Content Statistics:")
    logger.info(f"  Total sources: {stats['total_sources']}")
    logger.info(f"  By domain: {stats['by_domain']}")
    logger.info(f"  By personality: {stats['by_personality']}")
    logger.info(f"  By priority: {stats['by_priority']}")
    logger.info(f"  Estimated total chunks: {stats['estimated_total_chunks']}")
    
    # Save statistics
    with open("content_statistics.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    return stats

async def validate_urls():
    """Validate that source URLs are accessible."""
    logger.info("🧪 Validating source URLs...")
    
    pipeline = EnhancedContentSourcingPipeline(Path("./url_validation"))
    sources = pipeline.get_priority_sources()
    
    import aiohttp
    
    validation_results = {
        "total_urls": len(sources),
        "accessible": 0,
        "inaccessible": 0,
        "url_status": []
    }
    
    async with aiohttp.ClientSession() as session:
        for source in sources[:5]:  # Test first 5 URLs only
            try:
                async with session.head(source.download_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    is_accessible = response.status == 200
                    
                    validation_results["url_status"].append({
                        "personality": source.personality,
                        "url": source.download_url,
                        "status_code": response.status,
                        "accessible": is_accessible
                    })
                    
                    if is_accessible:
                        validation_results["accessible"] += 1
                        logger.info(f"✅ {source.personality}: {response.status}")
                    else:
                        validation_results["inaccessible"] += 1
                        logger.warning(f"⚠️ {source.personality}: {response.status}")
                        
            except Exception as e:
                validation_results["inaccessible"] += 1
                validation_results["url_status"].append({
                    "personality": source.personality,
                    "url": source.download_url,
                    "error": str(e),
                    "accessible": False
                })
                logger.error(f"❌ {source.personality}: {str(e)}")
    
    success_rate = (validation_results["accessible"] / 5) * 100
    logger.info(f"📊 URL Validation Results: {success_rate:.1f}% accessible")
    
    with open("url_validation_results.json", 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2, ensure_ascii=False)
    
    return validation_results

async def main():
    """Run all tests."""
    logger.info("🚀 Starting Content Sourcing Pipeline Tests")
    
    test_results = {
        "single_source_test": False,
        "multiple_source_test": False,
        "url_validation_passed": False,
        "statistics_generated": False
    }
    
    try:
        # Test 1: Single source download
        logger.info("\n" + "="*50)
        logger.info("TEST 1: Single Source Download")
        logger.info("="*50)
        test_results["single_source_test"] = await test_single_source()
        
        # Test 2: Multiple source processing
        logger.info("\n" + "="*50)
        logger.info("TEST 2: Multiple Source Processing")
        logger.info("="*50)
        test_results["multiple_source_test"] = await test_multiple_priorities()
        
        # Test 3: URL validation
        logger.info("\n" + "="*50)
        logger.info("TEST 3: URL Validation")
        logger.info("="*50)
        url_results = await validate_urls()
        test_results["url_validation_passed"] = url_results["accessible"] > 0
        
        # Test 4: Statistics generation
        logger.info("\n" + "="*50)
        logger.info("TEST 4: Statistics Generation")
        logger.info("="*50)
        stats = test_content_statistics()
        test_results["statistics_generated"] = stats["total_sources"] > 0
        
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {str(e)}")
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
    logger.info("="*50)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! Content sourcing pipeline is ready.")
    else:
        logger.warning("⚠️ Some tests failed. Review the results before proceeding.")
    
    return test_results

if __name__ == "__main__":
    asyncio.run(main())
