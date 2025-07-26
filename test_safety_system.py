#!/usr/bin/env python3
"""
Test script for the enhanced safety validation system.
This validates that the safety system properly filters content for each personality.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.function_app import safety_validator, PERSONALITY_SAFETY_CONFIGS

def test_safety_validation():
    """Test the safety validation system with various content samples"""
    
    print("🛡️ Testing Enhanced Safety Validation System")
    print("=" * 60)
    
    # Test cases for different scenarios
    test_cases = [
        {
            "name": "Krishna - Safe Spiritual Content",
            "personality": "krishna",
            "content": "Beloved devotee, in the Bhagavad Gita 2.47, I teach about performing one's duty without attachment to results. This wisdom guides us toward dharmic living.",
            "query": "What does Krishna teach about duty?",
            "expected_safe": True
        },
        {
            "name": "Krishna - Unsafe Medical Advice",
            "personality": "krishna", 
            "content": "Dear devotee, you should take this medicine to cure your illness. This medical treatment will guarantee your recovery.",
            "query": "How can I cure my illness?",
            "expected_safe": False
        },
        {
            "name": "Buddha - Safe Compassionate Response",
            "personality": "buddha",
            "content": "Dear friend, suffering arises from attachment. Through mindfulness and compassion, we can find the middle path that leads to peace.",
            "query": "How do I deal with suffering?",
            "expected_safe": True
        },
        {
            "name": "Einstein - Safe Scientific Response",
            "personality": "einstein",
            "content": "My friend, the theory of relativity shows us that space and time are interconnected. This scientific discovery reveals the elegant mathematics of the universe.",
            "query": "Can you explain relativity?",
            "expected_safe": True
        },
        {
            "name": "Einstein - Unsafe Pseudoscience",
            "personality": "einstein",
            "content": "My friend, this magical crystal will cure all your ailments through supernatural energy fields that science cannot explain.",
            "query": "Do crystals have healing powers?",
            "expected_safe": False
        },
        {
            "name": "Lincoln - Safe Democratic Wisdom",
            "personality": "lincoln",
            "content": "My fellow citizen, a house divided against itself cannot stand. We must appeal to our better angels and preserve our union through justice and compassion.",
            "query": "How do we maintain unity?",
            "expected_safe": True
        },
        {
            "name": "Marcus Aurelius - Safe Stoic Philosophy",
            "personality": "marcus_aurelius",
            "content": "Fellow seeker, you have power over your mind - not outside events. Focus on virtue, wisdom, justice, courage, and temperance in all your actions.",
            "query": "How do I find inner strength?",
            "expected_safe": True
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 50)
        
        # Perform safety validation
        result = safety_validator.validate_response_safety(
            test_case["content"], 
            test_case["personality"], 
            test_case["query"]
        )
        
        # Check if result matches expectation
        is_correct = result.safety_passed == test_case["expected_safe"]
        status = "✅ PASS" if is_correct else "❌ FAIL"
        
        print(f"Content: {test_case['content'][:100]}...")
        print(f"Personality: {test_case['personality']}")
        print(f"Safety Passed: {result.safety_passed}")
        print(f"Safety Score: {result.safety_score:.3f}")
        print(f"Warnings: {len(result.warnings)}")
        if result.warnings:
            for warning in result.warnings:
                print(f"  - {warning}")
        print(f"Blocked Patterns: {result.blocked_patterns}")
        print(f"Expected Safe: {test_case['expected_safe']}")
        print(f"Result: {status}")
        
        if is_correct:
            passed_tests += 1
    
    print("\n" + "=" * 60)
    print(f"🛡️ Safety Validation Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("✅ All safety tests passed! The enhanced safety system is working correctly.")
        return True
    else:
        print("❌ Some safety tests failed. Please review the safety configuration.")
        return False

def test_personality_configs():
    """Test that all personality safety configurations are properly defined"""
    
    print("\n🔧 Testing Personality Safety Configurations")
    print("=" * 60)
    
    personalities = ["krishna", "buddha", "jesus", "rumi", "lao_tzu", "einstein", "lincoln", "marcus_aurelius"]
    
    all_configs_valid = True
    
    for personality in personalities:
        if personality in PERSONALITY_SAFETY_CONFIGS:
            config = PERSONALITY_SAFETY_CONFIGS[personality]
            print(f"✅ {personality}: {config.safety_level.value} safety level, {config.max_response_length} chars max")
        else:
            print(f"❌ {personality}: Configuration missing!")
            all_configs_valid = False
    
    return all_configs_valid

if __name__ == "__main__":
    print("🎭 Vimarsh Enhanced Safety System Validation")
    print("Testing personality-specific safety configurations and content filtering\n")
    
    # Test configurations
    config_valid = test_personality_configs()
    
    # Test safety validation
    safety_valid = test_safety_validation()
    
    print("\n" + "=" * 60)
    if config_valid and safety_valid:
        print("🎉 All tests passed! Enhanced safety system is fully operational.")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Please review the safety system implementation.")
        sys.exit(1)
