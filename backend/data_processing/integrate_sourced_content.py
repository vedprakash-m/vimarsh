#!/usr/bin/env python3
"""
Integration Script for Sourced Content with Vimarsh Data Pipeline
Connects the enhanced content sourcing pipeline with existing data processing.
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import json

# Import existing pipeline components
from content_sourcing_pipeline import EnhancedContentSourcingPipeline
from sacred_text_loader import SacredTextEntry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentIntegrationManager:
    """Manages integration of sourced content with existing Vimarsh pipeline."""
    
    def __init__(self, base_data_path: Path):
        self.base_data_path = base_data_path
        self.sourcing_pipeline = EnhancedContentSourcingPipeline(
            base_path=base_data_path / "sourced_content"
        )
        self.sourcing_pipeline.base_path.mkdir(parents=True, exist_ok=True)
        
    async def source_and_integrate_all_content(self, exclude_personalities: List[str] = None) -> Dict[str, Any]:
        """Source content and integrate with existing pipeline."""
        if exclude_personalities is None:
            exclude_personalities = ["Krishna"]  # Already sourced as per instructions
            
        logger.info(f"🚀 Starting content sourcing and integration (excluding: {exclude_personalities})")
        
        # Get all sources except excluded personalities
        all_sources = self.sourcing_pipeline.get_priority_sources()
        filtered_sources = [s for s in all_sources if s.personality not in exclude_personalities]
        
        logger.info(f"📚 Processing {len(filtered_sources)} content sources")
        
        # Process content in priority order
        processed_content = await self.sourcing_pipeline.process_priority_sources(
            max_sources=len(filtered_sources)
        )
        
        # Convert to sacred text entries for database integration
        sacred_entries = self.sourcing_pipeline.convert_to_sacred_text_entries(processed_content)
        
        # Save integration results
        integration_results = {
            "sourced_content": processed_content,
            "sacred_text_entries": sacred_entries,
            "processing_statistics": self.sourcing_pipeline.processing_stats,
            "excluded_personalities": exclude_personalities,
            "total_entries_created": len(sacred_entries)
        }
        
        # Save to file for review
        results_file = self.base_data_path / "content_integration_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(integration_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Content integration complete!")
        logger.info(f"📊 Created {len(sacred_entries)} text entries from {len(processed_content)} sources")
        logger.info(f"💾 Results saved to: {results_file}")
        
        return integration_results
    
    async def source_specific_domains(self, domains: List[str]) -> Dict[str, Any]:
        """Source content for specific domains only."""
        logger.info(f"🎯 Sourcing content for domains: {domains}")
        
        all_sources = self.sourcing_pipeline.get_priority_sources()
        domain_sources = [s for s in all_sources if s.domain in domains]
        
        logger.info(f"📚 Found {len(domain_sources)} sources for specified domains")
        
        processed_content = {}
        for source in domain_sources:
            content = await self.sourcing_pipeline.download_content_with_retry(source)
            if content:
                processed_content[source.source_id] = {
                    'personality': source.personality,
                    'domain': source.domain,
                    'work_title': source.work_title,
                    'content': content,
                    'source_metadata': {
                        'edition_translation': source.edition_translation,
                        'repository': source.repository,
                        'authenticity_notes': source.authenticity_notes,
                        'public_domain': source.public_domain
                    }
                }
        
        sacred_entries = self.sourcing_pipeline.convert_to_sacred_text_entries(processed_content)
        
        return {
            "processed_content": processed_content,
            "sacred_entries": sacred_entries,
            "domains_processed": domains,
            "total_entries": len(sacred_entries)
        }
    
    def generate_integration_report(self) -> str:
        """Generate a detailed report of content sourcing capabilities."""
        sources = self.sourcing_pipeline.get_priority_sources()
        
        report = """
# Vimarsh Content Sourcing Integration Report

## Overview
This report details the integration of Gemini's research-backed content sourcing with Vimarsh's existing data pipeline.

## Content Sources Available

"""
        
        # Group by domain
        domains = {}
        for source in sources:
            if source.domain not in domains:
                domains[source.domain] = []
            domains[source.domain].append(source)
        
        for domain, domain_sources in domains.items():
            report += f"### {domain.title()} Domain\n\n"
            
            for source in domain_sources:
                report += f"**{source.personality}**: {source.work_title}\n"
                report += f"- Translation: {source.edition_translation}\n"
                report += f"- Repository: {source.repository}\n"
                report += f"- Priority: {source.priority}\n"
                report += f"- Quality: {source.content_quality}\n"
                report += f"- Estimated chunks: {source.estimated_chunks or 'Unknown'}\n"
                report += f"- Notes: {source.authenticity_notes}\n\n"
        
        report += """
## Integration Features

✅ **Authentic Source Prioritization**: All sources verified as public domain
✅ **Quality Control**: Multiple format support (PDF, HTML, text)
✅ **Error Handling**: Retry logic and graceful failure handling
✅ **Existing Pipeline Integration**: Compatible with SacredTextEntry format
✅ **Batch Processing**: Respectful server interaction with delays
✅ **Content Chunking**: Automatic text segmentation for optimal RAG performance

## Usage Instructions

1. **Full Integration**: Run `python integrate_sourced_content.py` for complete content sourcing
2. **Domain-Specific**: Use `source_specific_domains(['spiritual', 'philosophical'])` for targeted sourcing
3. **Quality Monitoring**: Check processing statistics for success/failure rates

## Quality Assurance

- All sources from Gemini's authenticated research report
- Public domain compliance verified
- Repository authenticity confirmed
- Content quality scoring implemented
- Automatic text validation and filtering
"""
        
        return report
    
    async def validate_content_quality(self, min_content_length: int = 1000) -> Dict[str, Any]:
        """Validate the quality of sourced content."""
        logger.info("🔍 Validating content quality...")
        
        sources = self.sourcing_pipeline.get_priority_sources()
        validation_results = {
            "total_sources": len(sources),
            "valid_sources": 0,
            "invalid_sources": 0,
            "validation_details": []
        }
        
        # Test a few sources for validation
        test_sources = sources[:5]  # Test first 5 sources
        
        for source in test_sources:
            try:
                content = await self.sourcing_pipeline.download_content_with_retry(source)
                is_valid = content and len(content) >= min_content_length
                
                validation_detail = {
                    "personality": source.personality,
                    "work_title": source.work_title,
                    "is_valid": is_valid,
                    "content_length": len(content) if content else 0,
                    "repository": source.repository
                }
                
                validation_results["validation_details"].append(validation_detail)
                
                if is_valid:
                    validation_results["valid_sources"] += 1
                else:
                    validation_results["invalid_sources"] += 1
                    
            except Exception as e:
                logger.error(f"❌ Validation failed for {source.personality}: {str(e)}")
                validation_results["validation_details"].append({
                    "personality": source.personality,
                    "work_title": source.work_title,
                    "is_valid": False,
                    "error": str(e)
                })
                validation_results["invalid_sources"] += 1
        
        validation_results["success_rate"] = (
            validation_results["valid_sources"] / len(test_sources) * 100
            if test_sources else 0
        )
        
        logger.info(f"✅ Validation complete: {validation_results['success_rate']:.1f}% success rate")
        return validation_results

async def main():
    """Main integration workflow."""
    base_path = Path("./vimarsh_content_integration")
    base_path.mkdir(exist_ok=True)
    
    manager = ContentIntegrationManager(base_path)
    
    # Generate integration report
    logger.info("📄 Generating integration report...")
    report = manager.generate_integration_report()
    with open(base_path / "integration_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    print("📄 Integration report saved to integration_report.md")
    
    # Validate content quality
    logger.info("🔍 Validating content sources...")
    validation_results = await manager.validate_content_quality()
    print(f"✅ Content validation complete: {validation_results['success_rate']:.1f}% success rate")
    
    # Option 1: Source all content (recommended for full setup)
    print("\n🚀 Starting full content sourcing...")
    integration_results = await manager.source_and_integrate_all_content()
    
    print(f"""
🎉 Content sourcing and integration complete!

📊 Results Summary:
- Sources processed: {len(integration_results['sourced_content'])}
- Text entries created: {integration_results['total_entries_created']}
- Processing statistics: {integration_results['processing_statistics']}

📁 Output files:
- Integration results: {base_path}/content_integration_results.json
- Integration report: {base_path}/integration_report.md
- Downloaded content: {base_path}/sourced_content/

✨ Next steps:
1. Review the integration results file
2. Load the sacred_text_entries into your Cosmos DB
3. Update your RAG pipeline to include the new content
""")

if __name__ == "__main__":
    asyncio.run(main())
