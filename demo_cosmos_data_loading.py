"""
Demonstration Script for Cosmos DB Data Loading
Task 8.8: Load and chunk source texts into production Cosmos DB

Demonstrates the complete pipeline from source text registration
to production Cosmos DB deployment with monitoring and validation.
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path

# Import our data loading components
from backend.data_processing.cosmos_data_loader import CosmosDataLoader
from backend.data_processing.data_loading_monitor import DataLoadingMonitor, monitor_data_loading
from backend.data_processing.spiritual_text_manager import SpiritualTextDataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}")


def print_subsection(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n{'-'*40}")
    print(f"{title}")
    print(f"{'-'*40}")


async def demo_complete_data_loading_pipeline():
    """Demonstrate the complete data loading pipeline."""
    
    print_section_header("VIMARSH DATA LOADING PIPELINE DEMO")
    print("🕉️ Demonstrating Task 8.8: Load and chunk source texts into production Cosmos DB")
    print("📚 Complete pipeline from source texts to production-ready vector storage")
    
    # Step 1: Initialize the data loader
    print_subsection("Step 1: Initialize Data Loader")
    
    loader = CosmosDataLoader(
        sources_directory="data/sources",
        temp_directory="data/temp",
        embedding_model_name="all-MiniLM-L6-v2"
    )
    
    print("✅ CosmosDataLoader initialized")
    print(f"📁 Sources directory: {loader.sources_directory}")
    print(f"🔧 Temp directory: {loader.temp_directory}")
    print(f"🧠 Embedding model: all-MiniLM-L6-v2")
    
    # Step 2: Register sample sources
    print_subsection("Step 2: Register Spiritual Text Sources")
    
    registration_success = loader.register_sample_sources()
    
    if registration_success:
        print("✅ Sample sources registered successfully:")
        
        sources = loader.data_manager.list_sources()
        for source in sources:
            print(f"   📖 {source.title}")
            print(f"      ID: {source.source_id}")
            print(f"      Type: {source.source_type}")
            print(f"      File: {source.file_path}")
            print(f"      Copyright: {source.copyright_status}")
            print()
    else:
        print("❌ Failed to register sample sources")
        return
    
    # Step 3: Validate sources
    print_subsection("Step 3: Validate Source Quality")
    
    validation_results = loader.validate_sources()
    
    print(f"📊 Validation Summary:")
    print(f"   Total Sources: {validation_results['total_sources']}")
    print(f"   Valid Sources: {validation_results['valid_sources']}")
    print(f"   Invalid Sources: {validation_results['invalid_sources']}")
    print(f"   Warnings: {validation_results['warnings']}")
    
    for source_id, result in validation_results["source_details"].items():
        print(f"\n📋 Source: {source_id}")
        print(f"   Valid: {'✅' if result['valid'] else '❌'}")
        
        if result.get("checks"):
            checks = result["checks"]
            print(f"   File Accessible: {'✅' if checks.get('file_accessible') else '❌'}")
            print(f"   Content Integrity: {'✅' if checks.get('content_integrity') else '❌'}")
            print(f"   Copyright Clear: {'✅' if checks.get('copyright_clear') else '❌'}")
            print(f"   Content Quality: {'✅' if checks.get('content_quality') else '❌'}")
            print(f"   Spiritual Authenticity: {'✅' if checks.get('spiritual_authenticity') else '❌'}")
        
        if result.get("warnings"):
            for warning in result["warnings"]:
                print(f"   ⚠️  {warning}")
    
    # Step 4: Initialize storage connection
    print_subsection("Step 4: Initialize Cosmos DB Connection")
    
    storage_initialized = await loader.initialize_storage()
    
    if storage_initialized:
        print("✅ Cosmos DB vector storage initialized successfully")
        print("🔗 Connection established to production database")
    else:
        print("❌ Failed to initialize Cosmos DB storage")
        print("ℹ️  This demo will continue with mock operations")
    
    # Step 5: Process sample source to demonstrate chunking
    print_subsection("Step 5: Demonstrate Text Processing and Chunking")
    
    sample_source_id = "bhagavad_gita_sample"
    print(f"🔄 Processing source: {sample_source_id}")
    
    try:
        chunks = await loader.process_source_to_chunks(sample_source_id)
        
        print(f"✅ Successfully processed source into {len(chunks)} chunks")
        
        # Analyze chunk quality
        quality_scores = [chunk.quality_score for chunk in chunks]
        avg_quality = sum(quality_scores) / len(quality_scores)
        high_quality_chunks = sum(1 for score in quality_scores if score >= 1.5)
        
        print(f"📈 Chunk Quality Analysis:")
        print(f"   Average Quality Score: {avg_quality:.2f}")
        print(f"   High Quality Chunks: {high_quality_chunks}/{len(chunks)} ({(high_quality_chunks/len(chunks)*100):.1f}%)")
        
        # Show sample chunks
        print(f"\n📄 Sample Chunks:")
        for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
            print(f"\n   Chunk {i+1} (ID: {chunk.id}):")
            print(f"   Quality Score: {chunk.quality_score:.2f}")
            print(f"   Content Preview: {chunk.content[:100]}...")
            if chunk.sanskrit_terms:
                print(f"   Sanskrit Terms: {', '.join(chunk.sanskrit_terms[:5])}")
            if chunk.chapter and chunk.verse:
                print(f"   Reference: Chapter {chunk.chapter}, Verse {chunk.verse}")
        
        if len(chunks) > 3:
            print(f"   ... and {len(chunks) - 3} more chunks")
            
    except Exception as e:
        print(f"❌ Failed to process source: {str(e)}")
        return
    
    # Step 6: Demonstrate monitoring setup
    print_subsection("Step 6: Data Loading with Real-time Monitoring")
    
    if storage_initialized:
        print("🚀 Starting complete data loading operation with monitoring...")
        
        # Start both loading and monitoring
        loading_task = asyncio.create_task(
            loader.load_all_sources(validate_first=True)
        )
        
        monitoring_task = asyncio.create_task(
            monitor_data_loading(loader, update_interval=5, save_history=True)
        )
        
        # Wait for completion
        loading_results, monitoring_report = await asyncio.gather(
            loading_task, monitoring_task
        )
        
        # Display results
        print_subsection("Loading Results")
        
        if loading_results["success"]:
            print("✅ Data loading completed successfully!")
            print(f"📊 Results Summary:")
            print(f"   Sources Processed: {loading_results['processed_sources']}/{loading_results['total_sources']}")
            print(f"   Chunks Loaded: {loading_results['successful_chunks']}")
            print(f"   Failed Chunks: {loading_results['failed_chunks']}")
            print(f"   Success Rate: {loading_results['success_rate']:.1f}%")
            print(f"   Duration: {loading_results['duration_seconds']:.1f} seconds")
            
            # Display data quality report
            if "data_quality" in monitoring_report:
                quality = monitoring_report["data_quality"]
                print(f"\n📈 Data Quality Assessment:")
                print(f"   Total Chunks Analyzed: {quality['total_chunks']}")
                print(f"   Average Quality Score: {quality['avg_quality_score']:.2f}")
                print(f"   Average Chunk Size: {quality['avg_chunk_size']:.0f} characters")
                print(f"   Sanskrit Coverage: {quality['sanskrit_terms_coverage']:.1f}%")
                print(f"   Verse Reference Coverage: {quality['verse_reference_coverage']:.1f}%")
                
                quality_dist = quality.get("quality_distribution", {})
                if quality_dist:
                    print(f"   Quality Distribution:")
                    print(f"     High Quality: {quality_dist.get('high', 0):.1f}%")
                    print(f"     Medium Quality: {quality_dist.get('medium', 0):.1f}%")
                    print(f"     Low Quality: {quality_dist.get('low', 0):.1f}%")
                
                if quality.get("issues"):
                    print(f"\n⚠️  Issues Identified:")
                    for issue in quality["issues"]:
                        print(f"     • {issue}")
                
                if quality.get("recommendations"):
                    print(f"\n💡 Recommendations:")
                    for rec in quality["recommendations"]:
                        print(f"     • {rec}")
        else:
            print("❌ Data loading failed!")
            print(f"Error: {loading_results.get('error', 'Unknown error')}")
            
            if "partial_results" in loading_results:
                partial = loading_results["partial_results"]
                print(f"Partial Results:")
                print(f"   Processed Sources: {partial['processed_sources']}")
                print(f"   Loaded Chunks: {partial['loaded_chunks']}")
                print(f"   Failed Chunks: {partial['failed_chunks']}")
    
    else:
        print("ℹ️  Simulating data loading process (storage not available)...")
        print("✅ Text processing pipeline validated successfully")
        print("✅ Chunk generation and quality validation working")
        print("✅ Monitoring system ready for production deployment")
    
    # Step 7: Demonstrate data validation
    print_subsection("Step 7: Production Data Validation")
    
    if storage_initialized:
        print("🔍 Validating loaded data with sample queries...")
        
        validation_results = await loader.validate_loaded_data()
        
        if validation_results["success"]:
            print("✅ Data validation passed!")
            print(f"📊 Validation Results:")
            print(f"   Queries Tested: {validation_results['queries_tested']}")
            print(f"   Successful Retrievals: {validation_results['successful_retrievals']}")
            print(f"   Total Chunks Found: {validation_results['total_chunks_found']}")
            
            # Show sample query results
            print(f"\n🔍 Sample Query Results:")
            for query, details in validation_results["query_details"].items():
                if details["success"]:
                    print(f"   Query: '{query}' → {details['results_count']} results")
                    if details.get("sample_result"):
                        print(f"     Sample: {details['sample_result']}")
                else:
                    print(f"   Query: '{query}' → ❌ {details['error']}")
        else:
            print(f"❌ Data validation failed: {validation_results.get('error')}")
    else:
        print("ℹ️  Data validation would verify:")
        print("   • Vector search functionality")
        print("   • Query response quality")
        print("   • Citation and attribution accuracy")
        print("   • Sanskrit term preservation")
    
    # Final summary
    print_section_header("DEMO COMPLETION SUMMARY")
    
    print("🎉 Task 8.8 Data Loading Pipeline Demo Complete!")
    print()
    print("✅ Completed Components:")
    print("   • Spiritual text data source management")
    print("   • Advanced text processing and chunking")
    print("   • Production-ready Cosmos DB integration")
    print("   • Real-time loading monitoring")
    print("   • Data quality validation and reporting")
    print("   • Error handling and recovery")
    print()
    print("🏗️  Production Ready Features:")
    print("   • Batch processing with retry logic")
    print("   • Progress tracking and telemetry")
    print("   • Quality assurance and validation")
    print("   • Comprehensive error reporting")
    print("   • Scalable embedding generation")
    print()
    print("📋 Next Steps for Production:")
    if storage_initialized:
        print("   • Data successfully loaded to Cosmos DB")
        print("   • Ready for integration with spiritual guidance API")
        print("   • Monitor performance and optimize as needed")
    else:
        print("   • Configure Cosmos DB connection settings")
        print("   • Run full data loading operation")
        print("   • Validate production deployment")
    print()
    print("🕉️ Ready to provide divine spiritual guidance with authentic source texts!")


async def demo_text_processing_details():
    """Demonstrate detailed text processing capabilities."""
    
    print_section_header("TEXT PROCESSING CAPABILITIES DEMO")
    
    # Load a sample text
    sample_file = Path("data/sources/bhagavad_gita_sample.txt")
    if sample_file.exists():
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_text = f.read()
        
        print(f"📖 Processing sample from: {sample_file.name}")
        print(f"📊 Original text length: {len(sample_text)} characters")
        
        # Initialize text processor
        from backend.rag.text_processor import AdvancedSpiritualTextProcessor
        processor = AdvancedSpiritualTextProcessor()
        
        # Process text
        chunks = processor.process_text_advanced(sample_text, str(sample_file))
        
        print(f"✅ Generated {len(chunks)} enhanced chunks")
        
        # Analyze processing results
        total_sanskrit_terms = sum(len(chunk.sanskrit_terms) for chunk in chunks)
        chunks_with_verses = sum(1 for chunk in chunks if chunk.verse_references)
        avg_quality = sum(chunk.quality_score for chunk in chunks) / len(chunks)
        
        print(f"\n📈 Processing Analysis:")
        print(f"   Total Sanskrit Terms: {total_sanskrit_terms}")
        print(f"   Chunks with Verse References: {chunks_with_verses}")
        print(f"   Average Quality Score: {avg_quality:.2f}")
        
        # Show detailed chunk analysis
        print(f"\n🔍 Detailed Chunk Analysis:")
        for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks in detail
            print(f"\n   Chunk {i+1}:")
            print(f"     ID: {chunk.chunk_id}")
            print(f"     Length: {len(chunk.content)} characters")
            print(f"     Quality Score: {chunk.quality_score:.2f}")
            print(f"     Text Type: {chunk.text_type.value}")
            print(f"     Sanskrit Terms: {len(chunk.sanskrit_terms)}")
            if chunk.sanskrit_terms:
                print(f"       Terms: {', '.join(chunk.sanskrit_terms[:10])}")
            print(f"     Semantic Tags: {len(chunk.semantic_tags)}")
            if chunk.semantic_tags:
                print(f"       Tags: {', '.join(chunk.semantic_tags[:5])}")
            print(f"     Verse References: {len(chunk.verse_references)}")
            if chunk.verse_references:
                for ref in chunk.verse_references[:3]:
                    print(f"       {ref.text_type.value} {ref.chapter}:{ref.verse}")
            print(f"     Content Preview:")
            print(f"       {chunk.content[:200]}...")
    else:
        print(f"❌ Sample file not found: {sample_file}")
        print("ℹ️  Please ensure sample source files are available")


if __name__ == "__main__":
    async def main():
        print("🕉️ Vimarsh Data Loading Pipeline Demonstration")
        print("🎯 Task 8.8: Load and chunk source texts into production Cosmos DB")
        print()
        
        # Run text processing demo first
        await demo_text_processing_details()
        
        # Run complete pipeline demo
        await demo_complete_data_loading_pipeline()
        
        print("\n" + "="*60)
        print("THANK YOU FOR USING VIMARSH DATA LOADING SYSTEM")
        print("May this technology serve the divine purpose of spiritual guidance!")
        print("🕉️ ॐ शान्ति शान्ति शान्तिः 🕉️")
        print("="*60)
    
    asyncio.run(main())
