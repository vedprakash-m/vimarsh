"""
Test script for Citation Grounding Checker

Tests the basic functionality of the citation validation service
to ensure it's working correctly after implementation.
"""

import asyncio
import os
import sys

# Add the parent directory to the path to import our service
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.citation_grounding_checker import CitationGroundingChecker, CitationValidationLevel

async def test_citation_grounding():
    """Test the citation grounding checker with sample data"""
    
    print("🔍 Testing Citation Grounding Checker...")
    
    # Initialize the checker
    checker = CitationGroundingChecker(CitationValidationLevel.MODERATE)
    
    # Test data - response with citations
    test_response = "As taught in the Bhagavad Gita, one must perform their duty without attachment to results. This principle of nishkama karma leads to spiritual liberation."
    
    test_citations = [
        "Bhagavad Gita 2.47",
        "Bhagavad Gita 3.19",
        "Buddha Teachings on Mindfulness"
    ]
    
    print(f"📊 Validation Level: {checker.validation_level.value}")
    print(f"📚 Source texts loaded: {len(checker.source_cache)}")
    print(f"🎯 Testing with response: '{test_response[:60]}...'")
    print(f"📝 Citations to validate: {test_citations}")
    
    # Run validation
    try:
        report = await checker.validate_response_grounding(
            response_text=test_response,
            citations=test_citations,
            response_id="test_001"
        )
        
        print(f"\n✅ Validation completed successfully!")
        print(f"📈 Overall Precision: {report.overall_precision:.1%}")
        print(f"🎯 Confidence Level: {report.confidence_level}")
        print(f"⚠️  Hallucination Risk: {report.hallucination_risk}")
        print(f"💡 Recommendation: {report.recommendation}")
        print(f"✅ Valid Citations: {report.valid_citations}/{report.total_citations}")
        
        # Show individual citation results
        print(f"\n📝 Individual Citation Results:")
        for i, validation in enumerate(report.citation_validations, 1):
            print(f"  {i}. {validation.citation}")
            print(f"     Valid: {validation.is_valid} (confidence: {validation.confidence_score:.2f})")
            print(f"     Method: {validation.validation_method}")
            if validation.concerns:
                print(f"     Concerns: {', '.join(validation.concerns)}")
            print()
        
        # Test batch validation
        batch_responses = [
            {
                'id': 'batch_1',
                'response': 'The path to wisdom requires discipline and self-reflection.',
                'citations': ['Marcus Aurelius Meditations']
            },
            {
                'id': 'batch_2', 
                'response': 'Innovation comes from seeing what others cannot see.',
                'citations': ['Tesla Teachings', 'Einstein Relativity']
            }
        ]
        
        print("🔄 Testing batch validation...")
        batch_reports = await checker.batch_validate(batch_responses)
        
        print(f"✅ Batch validation completed! Processed {len(batch_reports)} responses")
        
        for report in batch_reports:
            print(f"  {report.response_id}: {report.valid_citations}/{report.total_citations} valid (precision: {report.overall_precision:.1%})")
        
        # Show service statistics
        stats = checker.get_validation_stats()
        print(f"\n📊 Service Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print(f"\n🎉 Citation Grounding Checker test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_citation_grounding())
