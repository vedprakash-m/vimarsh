#!/usr/bin/env python3
"""
Three-Personality System Validation Test
Tests Krishna, Buddha, and Jesus personalities for content access and safety
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.function_app import safety_validator, PERSONALITY_SAFETY_CONFIGS
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def test_personality_content_files():
    """Test that each personality has content files available"""
    print("🧪 Testing Personality Content Files")
    print("=" * 60)
    
    personalities = ['krishna', 'buddha', 'jesus']
    results = {}
    
    for personality in personalities:
        print(f"\n📚 Testing {personality.title()} content files...")
        
        try:
            # Check for personality-specific content files  
            content_file = f"backend/data/vimarsh-db/{personality}-texts.json"
            full_path = os.path.abspath(content_file)
            print(f"  🔍 Looking for: {full_path}")
            
            if os.path.exists(content_file):
                with open(content_file, 'r', encoding='utf-8') as f:
                    import json
                    content = json.load(f)
                    content_count = len(content)
                    
                print(f"  ✅ Found {content_count} texts for {personality}")
                
                # Show a sample text
                if content and len(content) > 0:
                    sample = content[0]
                    print(f"  📖 Sample: {sample.get('title', 'Untitled')[:50]}...")
                
                results[personality] = {
                    'content_available': True,
                    'content_count': content_count,
                    'status': 'PASS'
                }
            else:
                print(f"  ⚠️  No content file found: {content_file}")
                results[personality] = {
                    'content_available': False,
                    'content_count': 0,
                    'status': 'FAIL'
                }
                
        except Exception as e:
            print(f"  ❌ Error accessing {personality} content: {e}")
            results[personality] = {
                'content_available': False,
                'content_count': 0,
                'status': 'ERROR',
                'error': str(e)
            }
    
    return results

def test_personality_safety_configs():
    """Test that each personality has proper safety configuration"""
    print("\n🛡️ Testing Personality Safety Configurations")
    print("=" * 60)
    
    personalities = ['krishna', 'buddha', 'jesus']
    results = {}
    
    for personality in personalities:
        print(f"\n🔒 Testing {personality.title()} safety config...")
        
        if personality in PERSONALITY_SAFETY_CONFIGS:
            config = PERSONALITY_SAFETY_CONFIGS[personality]
            print("  ✅ Safety config found")
            print(f"  📏 Max length: {config.max_response_length}")
            print(f"  🔒 Safety level: {config.safety_level}")
            print(f"  🚫 Blocked patterns: {len(config.blocked_patterns)}")
            
            # Test safety validation with personality-appropriate content
            if personality == 'krishna':
                test_content = "Beloved devotee, in the sacred Bhagavad Gita I teach that peace comes from divine wisdom and spiritual dharma."
            elif personality == 'buddha':
                test_content = "Dear friend, through mindfulness and compassion, we can find peace on the path to wisdom."
            else:  # jesus
                test_content = "My child, come to me and find rest, for God's love brings peace to all who believe."
                
            test_query = "How can I find peace?"
            validation_result = safety_validator.validate_response_safety(test_content, personality, test_query)
            
            print(f"  🧪 Safety test - Safe: {validation_result.safety_passed}")
            print(f"  📊 Safety score: {validation_result.safety_score:.3f}")
            
            results[personality] = {
                'config_available': True,
                'safety_test_passed': validation_result.safety_passed,
                'safety_score': validation_result.safety_score,
                'status': 'PASS' if validation_result.safety_passed else 'FAIL'
            }
        else:
            print(f"  ❌ No safety config found for {personality}")
            results[personality] = {
                'config_available': False,
                'safety_test_passed': False,
                'safety_score': 0.0,
                'status': 'FAIL'
            }
    
    return results

def test_personality_responses():
    """Test basic response generation for each personality"""
    print("\n💬 Testing Personality Response Generation")
    print("=" * 60)
    
    personalities = ['krishna', 'buddha', 'jesus']
    results = {}
    
    # Note: This is a simplified test since we don't have LLM integration here
    # In production, this would call the actual LLM service
    
    for personality in personalities:
        print(f"\n🎭 Testing {personality.title()} response pattern...")
        
        # Simulate response validation
        mock_responses = {
            'krishna': "Beloved devotee, in the Bhagavad Gita I teach that peace comes from understanding your eternal nature and performing your duty without attachment to results.",
            'buddha': "Dear friend, suffering arises from attachment. Through mindfulness and compassion, we can find peace by letting go of our clinging to impermanent things.",
            'jesus': "My child, come to me all who are weary and burdened, and I will give you rest. Find peace in God's love and forgiveness."
        }
        
        test_response = mock_responses.get(personality, "")
        if test_response:
            # Validate the mock response
            validation_result = safety_validator.validate_response_safety(test_response, personality, "How can I find peace in difficult times?")
            
            print("  ✅ Mock response generated")
            print(f"  🛡️ Safety validation: {validation_result.safety_passed}")
            print(f"  📊 Safety score: {validation_result.safety_score:.3f}")
            print(f"  📝 Response length: {len(test_response)} chars")
            
            results[personality] = {
                'response_generated': True,
                'safety_passed': validation_result.safety_passed,
                'safety_score': validation_result.safety_score,
                'response_length': len(test_response),
                'status': 'PASS' if validation_result.safety_passed else 'FAIL'
            }
        else:
            print(f"  ❌ No response pattern available for {personality}")
            results[personality] = {
                'response_generated': False,
                'safety_passed': False,
                'safety_score': 0.0,
                'response_length': 0,
                'status': 'FAIL'
            }
    
    return results

def generate_test_report(content_results, safety_results, response_results):
    """Generate a comprehensive test report"""
    print("\n📋 THREE-PERSONALITY SYSTEM TEST REPORT")
    print("=" * 60)
    
    personalities = ['krishna', 'buddha', 'jesus']
    overall_status = "PASS"
    
    for personality in personalities:
        print(f"\n🎭 {personality.upper()} PERSONALITY")
        print("-" * 40)
        
        # Content access test
        content_status = content_results.get(personality, {}).get('status', 'UNKNOWN')
        content_count = content_results.get(personality, {}).get('content_count', 0)
        print(f"📚 Content Access: {content_status} ({content_count} texts)")
        
        # Safety configuration test
        safety_status = safety_results.get(personality, {}).get('status', 'UNKNOWN')
        safety_score = safety_results.get(personality, {}).get('safety_score', 0.0)
        print(f"🛡️ Safety Config: {safety_status} (score: {safety_score:.3f})")
        
        # Response generation test
        response_status = response_results.get(personality, {}).get('status', 'UNKNOWN')
        response_length = response_results.get(personality, {}).get('response_length', 0)
        print(f"💬 Response Test: {response_status} ({response_length} chars)")
        
        # Overall personality status
        personality_pass = all([
            content_status in ['PASS', 'UNKNOWN'],  # Content might not be required for all
            safety_status == 'PASS',
            response_status == 'PASS'
        ])
        
        if not personality_pass:
            overall_status = "FAIL"
        
        print(f"✅ Overall: {'PASS' if personality_pass else 'FAIL'}")
    
    print(f"\n🎯 FINAL RESULT: {overall_status}")
    print("=" * 60)
    
    if overall_status == "PASS":
        print("🎉 All three personalities are functioning correctly!")
        print("✅ Ready to proceed to Phase 2 (Scientific & Historical Personalities)")
    else:
        print("❌ Some issues detected. Please review and fix before proceeding.")
    
    return overall_status == "PASS"

def main():
    """Main test execution"""
    print("🎭 Vimarsh Three-Personality System Validation")
    print("Testing Krishna, Buddha, and Jesus personalities")
    print("=" * 60)
    
    try:
        # Run all tests
        content_results = test_personality_content_files()
        safety_results = test_personality_safety_configs()
        response_results = test_personality_responses()
        
        # Generate comprehensive report
        success = generate_test_report(content_results, safety_results, response_results)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
