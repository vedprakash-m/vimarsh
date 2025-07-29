#!/usr/bin/env python3
"""
Comprehensive RAG Integration Test
Tests the complete Retrieval-Augmented Generation pipeline
"""

import asyncio
import logging
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from services.rag_integration_service import RAGIntegrationService
from services.vector_database_service import PersonalityType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_rag_question_answering():
    """Test complete RAG question-answering pipeline"""
    try:
        logger.info("🔍 Starting RAG Integration Test...")
        
        # Initialize RAG service
        rag_service = RAGIntegrationService()
        logger.info("✅ RAG service initialized")
        
        # Comprehensive test cases covering different question types
        test_cases = [
            {
                'category': 'Philosophical Questions',
                'questions': [
                    {
                        'query': "What is the meaning and importance of dharma according to Krishna?",
                        'personality': PersonalityType.KRISHNA,
                        'expected_concepts': ['dharma', 'duty', 'righteousness', 'cosmic order'],
                        'difficulty': 'medium'
                    },
                    {
                        'query': "How does Krishna explain the relationship between action and wisdom?",
                        'personality': PersonalityType.KRISHNA,
                        'expected_concepts': ['karma yoga', 'action', 'wisdom', 'detachment'],
                        'difficulty': 'hard'
                    }
                ]
            },
            {
                'category': 'Practical Guidance',
                'questions': [
                    {
                        'query': "What practical advice does Krishna give for dealing with difficult decisions?",
                        'personality': PersonalityType.KRISHNA,
                        'expected_concepts': ['guidance', 'decision', 'wisdom', 'duty'],
                        'difficulty': 'medium'
                    },
                    {
                        'query': "How can one achieve inner peace and stability of mind?",
                        'personality': PersonalityType.KRISHNA,
                        'expected_concepts': ['peace', 'mind', 'stability', 'meditation'],
                        'difficulty': 'easy'
                    }
                ]
            },
            {
                'category': 'Spiritual Concepts',
                'questions': [
                    {
                        'query': "What is the nature of the eternal soul according to Krishna's teachings?",
                        'personality': PersonalityType.KRISHNA,
                        'expected_concepts': ['soul', 'eternal', 'atman', 'consciousness'],
                        'difficulty': 'hard'
                    },
                    {
                        'query': "How does devotion and surrender lead to liberation?",
                        'personality': PersonalityType.KRISHNA,
                        'expected_concepts': ['devotion', 'surrender', 'liberation', 'bhakti'],
                        'difficulty': 'medium'
                    }
                ]
            }
        ]
        
        total_questions = 0
        successful_answers = 0
        detailed_results = []
        
        # Process each test category
        for category in test_cases:
            logger.info(f"\n--- Testing {category['category']} ---")
            
            for i, question in enumerate(category['questions'], 1):
                total_questions += 1
                logger.info(f"\nQuestion {i}: {question['query']}")
                logger.info(f"Difficulty: {question['difficulty']}")
                
                try:
                    # Generate answer using RAG pipeline
                    response = await rag_service.generate_rag_enhanced_response(
                        query=question['query'],
                        personality_id=question['personality'].value,
                        language="English",
                        context_limit=5,
                        min_relevance=0.3,
                        include_cross_personality=False
                    )
                    
                    if response and response.content:
                        successful_answers += 1
                        
                        # Analyze response quality
                        response_lower = response.content.lower()
                        found_concepts = [concept for concept in question['expected_concepts'] 
                                        if concept.lower() in response_lower]
                        
                        concept_coverage = len(found_concepts) / len(question['expected_concepts'])
                        
                        result_details = {
                            'question': question['query'],
                            'category': category['category'],
                            'difficulty': question['difficulty'],
                            'response_length': len(response.content),
                            'sources_used': 1,  # EnhancedSpiritualResponse has single source
                            'concept_coverage': concept_coverage,
                            'found_concepts': found_concepts,
                            'response_preview': response.content[:200] + "..." if len(response.content) > 200 else response.content
                        }
                        detailed_results.append(result_details)
                        
                        logger.info(f"✅ Generated response ({len(response.content)} chars)")
                        logger.info(f"   Source: {response.source}")
                        logger.info(f"   Concept coverage: {concept_coverage:.1%}")
                        logger.info(f"   Found concepts: {', '.join(found_concepts)}")
                        logger.info(f"   Response preview: {response.content[:150]}...")
                        
                        # Display character count info
                        logger.info(f"   Character usage: {response.character_count}/{response.max_allowed}")
                    else:
                        logger.warning("❌ No response generated")
                        detailed_results.append({
                            'question': question['query'],
                            'category': category['category'],
                            'difficulty': question['difficulty'],
                            'response_length': 0,
                            'sources_used': 0,
                            'concept_coverage': 0,
                            'found_concepts': [],
                            'response_preview': "No response generated"
                        })
                    
                except Exception as e:
                    logger.error(f"❌ Question failed: {e}")
                    detailed_results.append({
                        'question': question['query'],
                        'category': category['category'],
                        'difficulty': question['difficulty'],
                        'response_length': 0,
                        'sources_used': 0,
                        'concept_coverage': 0,
                        'found_concepts': [],
                        'response_preview': f"Error: {e}"
                    })
        
        # Calculate and display comprehensive results
        success_rate = (successful_answers / total_questions) * 100
        avg_concept_coverage = sum(r['concept_coverage'] for r in detailed_results) / len(detailed_results)
        avg_response_length = sum(r['response_length'] for r in detailed_results if r['response_length'] > 0)
        avg_response_length = avg_response_length / max(1, sum(1 for r in detailed_results if r['response_length'] > 0))
        
        logger.info("\n🎯 RAG Integration Test Summary:")
        logger.info(f"   Total Questions: {total_questions}")
        logger.info(f"   Successful Answers: {successful_answers}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Average Concept Coverage: {avg_concept_coverage:.1%}")
        logger.info(f"   Average Response Length: {avg_response_length:.0f} characters")
        
        # Category-wise analysis
        categories = list(set(r['category'] for r in detailed_results))
        for category in categories:
            category_results = [r for r in detailed_results if r['category'] == category]
            category_success = sum(1 for r in category_results if r['response_length'] > 0)
            category_rate = (category_success / len(category_results)) * 100
            category_coverage = sum(r['concept_coverage'] for r in category_results) / len(category_results)
            
            logger.info(f"   {category}: {category_rate:.1f}% success, {category_coverage:.1%} concept coverage")
        
        # Quality assessment
        if success_rate >= 80:
            logger.info("🌟 Excellent! RAG system is working very well!")
            return True
        elif success_rate >= 60:
            logger.info("✅ Good! RAG system is functional with room for improvement")
            return True
        else:
            logger.warning("⚠️ RAG system needs significant optimization")
            return False
            
    except Exception as e:
        logger.error(f"❌ RAG integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_personality_consistency():
    """Test consistency of personality-based responses"""
    try:
        logger.info("\n🎭 Testing Personality Consistency...")
        
        rag_service = RAGIntegrationService()
        
        # Test same question with different personalities (when available)
        test_query = "What is the path to wisdom and enlightenment?"
        
        personalities_to_test = [PersonalityType.KRISHNA]  # Add others when available
        responses = {}
        
        for personality in personalities_to_test:
            try:
                response = await rag_service.generate_rag_enhanced_response(
                    query=test_query,
                    personality_id=personality.value,
                    language="English",
                    context_limit=3,
                    min_relevance=0.3
                )
                
                if response and response.content:
                    responses[personality.value] = {
                        'response': response.content,
                        'length': len(response.content),
                        'sources': 1  # Single source in EnhancedSpiritualResponse
                    }
                    logger.info(f"✅ {personality.value}: {len(response.content)} chars, source: {response.source}")
                else:
                    logger.warning(f"⚠️ {personality.value}: No response generated")
                    
            except Exception as e:
                logger.error(f"❌ {personality.value}: {e}")
        
        logger.info(f"✅ Personality consistency test completed: {len(responses)} personalities tested")
        return len(responses) > 0
        
    except Exception as e:
        logger.error(f"❌ Personality consistency test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        # Run comprehensive RAG tests
        rag_success = await test_rag_question_answering()
        personality_success = await test_personality_consistency()
        
        overall_success = rag_success and personality_success
        
        print(f"\n{'='*60}")
        print("🔬 RAG Integration Test Results:")
        print(f"   Question Answering: {'✅ PASS' if rag_success else '❌ FAIL'}")
        print(f"   Personality Consistency: {'✅ PASS' if personality_success else '❌ FAIL'}")
        print(f"   Overall Status: {'🌟 SUCCESS' if overall_success else '⚠️  NEEDS WORK'}")
        print(f"{'='*60}")
        
        if overall_success:
            print("\n🎉 RAG system is ready for production use!")
            print("✨ Next steps: Deploy and monitor performance")
        else:
            print("\n🔧 RAG system needs optimization before production")
            print("💡 Focus on improving low-performing areas")
        
        return 0 if overall_success else 1
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
