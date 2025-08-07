#!/usr/bin/env python3
"""
Test script for personality-content integration

This script tests how different personalities process content from their respective domains
and ensures that content is properly associated with the right personalities.
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(__file__))

from data_processing.text_processor import create_text_processor
from services.personality_service import PersonalityService
from models.personality_models import get_personality_list, get_personalities_by_domain
from services.llm_service import LLMService as EnhancedSimpleLLMService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_personality_content_matching():
    """Test that content is properly matched to appropriate personalities"""
    
    print("🧪 Testing Personality-Content Integration")
    print("=" * 60)
    
    # Sample content for different domains
    test_content = {
        "spiritual": {
            "text": """
            Chapter 2, Verse 47: You have a right to perform your prescribed duty, 
            but not to the fruits of action. This teaching about dharma and karma yoga 
            shows the path to moksha through selfless service.
            """,
            "expected_personalities": ["krishna"],
            "source": "Bhagavad Gita"
        },
        "scientific": {
            "text": """
            Einstein's theory of relativity demonstrates that space and time are 
            interconnected. The equation E=mc² shows the equivalence of mass and energy.
            Quantum mechanics reveals the probabilistic nature of reality at the atomic scale.
            """,
            "expected_personalities": ["einstein"],
            "source": "Physics Research"
        },
        "historical": {
            "text": """
            The Gettysburg Address, delivered by President Lincoln in 1863, redefined 
            the purpose of the Civil War. This speech emphasized that the nation must 
            have a new birth of freedom and government of the people, by the people, for the people.
            """,
            "expected_personalities": ["lincoln"],
            "source": "Historical Speech"
        },
        "philosophical": {
            "text": """
            The nature of virtue and the good life requires careful consideration. 
            As Marcus Aurelius wrote in his Meditations, we must focus on what is 
            within our control and accept what is not. Stoic philosophy teaches us 
            to live according to reason and virtue.
            """,
            "expected_personalities": ["marcus_aurelius"],
            "source": "Philosophical Text"
        }
    }
    
    processor = create_text_processor()
    
    for domain, content_info in test_content.items():
        print(f"\n🎭 Testing {domain.upper()} content:")
        print("-" * 40)
        
        # Process the content
        result = processor.process_text_with_domain(
            content_info["text"], 
            content_info["source"], 
            domain
        )
        
        print(f"✅ Domain detected: {processor.detect_domain(content_info['text'])}")
        print(f"📊 Quality score: {result.quality_metrics.get('avg_quality', 0):.1f}")
        print(f"🔑 Key terms: {result.chunks[0].key_terms[:5] if result.chunks else []}")
        print(f"📚 Citations: {result.chunks[0].citations[:3] if result.chunks else []}")
        
        # Test with appropriate personality
        expected_personality = content_info["expected_personalities"][0]
        print(f"🤖 Testing with {expected_personality} personality...")
        
        try:
            llm_service = EnhancedSimpleLLMService()
            response = await llm_service.generate_personality_response(
                query="What does this text teach us?",
                context="teaching",
                personality_id=expected_personality
            )
            
            print(f"💬 Response preview: {response.content[:100]}...")
            print(f"🎯 Confidence: {response.confidence}")
            
        except Exception as e:
            print(f"❌ Error with personality {expected_personality}: {e}")

async def test_content_personality_association():
    """Test associating content with multiple personalities"""
    
    print("\n🔗 Testing Content-Personality Association")
    print("=" * 60)
    
    # Get available personalities
    filters = {}
    personalities = get_personality_list()
    
    print(f"📋 Found {len(personalities)} active personalities:")
    
    # Group personalities by domain
    domain_personalities = {}
    for personality in personalities:
        domain = personality['domain']
        if domain not in domain_personalities:
            domain_personalities[domain] = []
        domain_personalities[domain].append(personality)
    
    for domain, domain_personalities_list in domain_personalities.items():
        print(f"\n🏷️  {domain.upper()} Domain:")
        for personality in domain_personalities_list:
            print(f"   - {personality['name']} (ID: {personality['id']})")
    
    # Test content processing for each domain
    processor = create_text_processor()
    
    sample_texts = {
        "spiritual": "The path to enlightenment requires devotion and wisdom",
        "scientific": "The hypothesis was tested through controlled experiments",
        "historical": "The treaty was signed in 1776 establishing independence",
        "philosophical": "The nature of reality requires careful contemplation"
    }
    
    print(f"\n📝 Testing content processing for each domain:")
    
    for domain, text in sample_texts.items():
        print(f"\n{domain.upper()}:")
        result = processor.process_text_with_domain(text, f"{domain}_sample", domain)
        
        if result.chunks:
            chunk = result.chunks[0]
            print(f"   Quality: {chunk:.1f}")
            print(f"   Key terms: {chunk.key_terms[:3]}")
            print(f"   Associated personalities: {[p.display_name for p in domain_personalities.get(domain, [])]}")

async def test_cross_domain_content():
    """Test how the system handles content that spans multiple domains"""
    
    print("\n🌐 Testing Cross-Domain Content")
    print("=" * 60)
    
    cross_domain_text = """
    Einstein once said that science without religion is lame, and religion without science is blind.
    This philosophical insight from the great physicist shows how spiritual wisdom and scientific
    knowledge can complement each other. Throughout history, many great thinkers have sought to
    bridge these domains of human understanding.
    """
    
    processor = create_text_processor()
    
    # Test domain detection
    detected_domain = processor.detect_domain(cross_domain_text)
    print(f"🔍 Detected primary domain: {detected_domain}")
    
    # Process with different domain hints
    domains_to_test = ["scientific", "spiritual", "philosophical", "historical"]
    
    for domain in domains_to_test:
        print(f"\n📊 Processing as {domain.upper()}:")
        result = processor.process_text_with_domain(cross_domain_text, "cross_domain", domain)
        
        if result.chunks:
            chunk = result.chunks[0]
            print(f"   Quality: {chunk:.1f}")
            print(f"   Key terms: {chunk.key_terms[:4]}")
            print(f"   Domain-specific processing: {chunk.chunk_type}")

if __name__ == "__main__":
    asyncio.run(test_personality_content_matching())
    asyncio.run(test_content_personality_association())
    asyncio.run(test_cross_domain_content())