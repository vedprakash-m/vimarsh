#!/usr/bin/env python3
"""
Simple test of content sourcing pipeline
"""

import sys
from pathlib import Path
import json

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from content_sourcing_pipeline import get_content_statistics, EnhancedContentSourcingPipeline
    print("✅ Successfully imported content sourcing pipeline")
    
    # Test statistics
    stats = get_content_statistics()
    print(f"📊 Found {stats['total_sources']} content sources")
    print(f"📚 Domains: {list(stats['by_domain'].keys())}")
    print(f"👥 Personalities: {list(stats['by_personality'].keys())}")
    print(f"🎯 Estimated total chunks: {stats['estimated_total_chunks']}")
    
    # Test pipeline creation
    pipeline = EnhancedContentSourcingPipeline(Path("./test_temp"))
    sources = pipeline.get_priority_sources()
    print(f"🔍 Pipeline created with {len(sources)} sources")
    
    print("🎉 Content sourcing pipeline is working correctly!")
    
except Exception as e:
    print(f"❌ Error testing pipeline: {str(e)}")
    import traceback
    traceback.print_exc()
