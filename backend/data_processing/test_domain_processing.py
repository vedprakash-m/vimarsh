#!/usr/bin/env python3
"""
Test script for multi-domain content processing system

This script tests the domain-specific processors to ensure they correctly
identify, process, and chunk content from different domains.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing.text_processor import create_text_processor, process_multi_domain_text
from data_processing.domain_processors import DomainProcessorFactory

def test_spiritual_processing():
    """Test spiritual content processing"""
    print("=== Testing Spiritual Content Processing ===")
    
    spiritual_text = """
    Chapter 2, Verse 47
    
    You have a right to perform your prescribed duty, but not to the fruits of action.
    Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.
    
    This verse from the Bhagavad Gita teaches about dharma and karma yoga. Krishna instructs Arjuna
    about the importance of performing one's duty without attachment to results. The concept of
    nishkama karma (desireless action) is central to spiritual growth and moksha.
    """
    
    processor = create_text_processor()
    
    # Test domain detection
    detected_domain = processor.detect_domain(spiritual_text)
    print(f"Detected domain: {detected_domain}")
    
    # Test processing
    result = processor.process_text_with_domain(spiritual_text, "Bhagavad Gita", "spiritual")
    
    print(f"Number of chunks: {len(result.chunks)}")
    print(f"Quality metrics: {result.quality_metrics}")
    print(f"Metadata: {result.metadata}")
    
    for i, chunk in enumerate(result.chunks):
        print(f"\nChunk {i+1}:")
        print(f"  Text: {chunk.text[:100]}...")
        print(f"  Key terms: {chunk.key_terms}")
        print(f"  Citations: {chunk.citations}")
        print(f"  Quality score: {chunk.quality_score}")
    
    print("\n" + "="*50 + "\n")


def test_scientific_processing():
    """Test scientific content processing"""
    print("=== Testing Scientific Content Processing ===")
    
    scientific_text = """
    Einstein's theory of relativity revolutionized our understanding of space and time.
    The famous equation E=mc² demonstrates the equivalence of mass and energy.
    
    According to Einstein (1905), the speed of light in a vacuum is constant for all observers.
    This principle led to the development of special relativity theory. Subsequent research
    by Hawking et al. (1975) expanded on these concepts in the context of black hole physics.
    
    The experimental data supports the hypothesis that quantum mechanics and general relativity
    are fundamental theories describing different aspects of physical reality.
    """
    
    processor = create_text_processor()
    
    # Test domain detection
    detected_domain = processor.detect_domain(scientific_text)
    print(f"Detected domain: {detected_domain}")
    
    # Test processing
    result = processor.process_text_with_domain(scientific_text, "Physics Paper", "scientific")
    
    print(f"Number of chunks: {len(result.chunks)}")
    print(f"Quality metrics: {result.quality_metrics}")
    print(f"Metadata: {result.metadata}")
    
    for i, chunk in enumerate(result.chunks):
        print(f"\nChunk {i+1}:")
        print(f"  Text: {chunk.text[:100]}...")
        print(f"  Key terms: {chunk.key_terms}")
        print(f"  Citations: {chunk.citations}")
        print(f"  Quality score: {chunk.quality_score}")
    
    print("\n" + "="*50 + "\n")


def test_historical_processing():
    """Test historical content processing"""
    print("=== Testing Historical Content Processing ===")
    
    historical_text = """
    The American Civil War (1861-1865) was a defining moment in United States history.
    President Abraham Lincoln issued the Emancipation Proclamation in 1863, declaring
    freedom for slaves in rebellious states.
    
    The Battle of Gettysburg in July 1863 marked a turning point in the war.
    According to historical records, this three-day battle resulted in over 50,000 casualties.
    Lincoln's Gettysburg Address, delivered later that year, redefined the war's purpose.
    
    The industrial revolution of the 19th century provided the North with significant
    advantages in manufacturing and transportation, contributing to the Union victory.
    """
    
    processor = create_text_processor()
    
    # Test domain detection
    detected_domain = processor.detect_domain(historical_text)
    print(f"Detected domain: {detected_domain}")
    
    # Test processing
    result = processor.process_text_with_domain(historical_text, "Civil War History", "historical")
    
    print(f"Number of chunks: {len(result.chunks)}")
    print(f"Quality metrics: {result.quality_metrics}")
    print(f"Metadata: {result.metadata}")
    
    for i, chunk in enumerate(result.chunks):
        print(f"\nChunk {i+1}:")
        print(f"  Text: {chunk.text[:100]}...")
        print(f"  Key terms: {chunk.key_terms}")
        print(f"  Citations: {chunk.citations}")
        print(f"  Quality score: {chunk.quality_score}")
    
    print("\n" + "="*50 + "\n")


def test_philosophical_processing():
    """Test philosophical content processing"""
    print("=== Testing Philosophical Content Processing ===")
    
    philosophical_text = """
    The nature of consciousness has been a central question in philosophy of mind.
    Descartes argued that the mind and body are distinct substances, leading to the
    mind-body problem that continues to challenge philosophers today.
    
    If consciousness is purely physical, then mental states should be reducible to
    brain states. However, the subjective nature of experience suggests otherwise.
    The concept of qualia - the qualitative aspects of conscious experience - 
    presents a significant challenge to materialist theories of mind.
    
    Kant's transcendental idealism proposed that we can never know things as they
    are in themselves, only as they appear to us through the structures of cognition.
    This epistemological limitation has profound implications for our understanding
    of reality and knowledge.
    """
    
    processor = create_text_processor()
    
    # Test domain detection
    detected_domain = processor.detect_domain(philosophical_text)
    print(f"Detected domain: {detected_domain}")
    
    # Test processing
    result = processor.process_text_with_domain(philosophical_text, "Philosophy of Mind", "philosophical")
    
    print(f"Number of chunks: {len(result.chunks)}")
    print(f"Quality metrics: {result.quality_metrics}")
    print(f"Metadata: {result.metadata}")
    
    for i, chunk in enumerate(result.chunks):
        print(f"\nChunk {i+1}:")
        print(f"  Text: {chunk.text[:100]}...")
        print(f"  Key terms: {chunk.key_terms}")
        print(f"  Citations: {chunk.citations}")
        print(f"  Quality score: {chunk.quality_score}")
    
    print("\n" + "="*50 + "\n")


def test_domain_detection():
    """Test automatic domain detection"""
    print("=== Testing Automatic Domain Detection ===")
    
    test_texts = [
        ("Krishna teaches Arjuna about dharma and yoga in the Bhagavad Gita", "spiritual"),
        ("The quantum mechanics experiment yielded significant data supporting the hypothesis", "scientific"),
        ("Napoleon's defeat at Waterloo in 1815 ended his empire", "historical"),
        ("The concept of justice requires careful ethical consideration", "philosophical")
    ]
    
    processor = create_text_processor()
    
    for text, expected_domain in test_texts:
        detected = processor.detect_domain(text)
        status = "✓" if detected == expected_domain else "✗"
        print(f"{status} Text: {text[:50]}...")
        print(f"   Expected: {expected_domain}, Detected: {detected}")
        print()


def test_content_validation():
    """Test content validation for different domains"""
    print("=== Testing Content Validation ===")
    
    processor = create_text_processor()
    
    # Test spiritual content validation
    spiritual_text = "Krishna teaches about dharma and karma yoga to Arjuna"
    validation = processor.validate_content_for_domain(spiritual_text, "spiritual")
    print(f"Spiritual validation: {validation}")
    
    # Test scientific content validation
    scientific_text = "The experiment tested the hypothesis using controlled variables"
    validation = processor.validate_content_for_domain(scientific_text, "scientific")
    print(f"Scientific validation: {validation}")
    
    print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    print("Multi-Domain Content Processing System Test")
    print("=" * 60)
    
    try:
        test_spiritual_processing()
        test_scientific_processing()
        test_historical_processing()
        test_philosophical_processing()
        test_domain_detection()
        test_content_validation()
        
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()