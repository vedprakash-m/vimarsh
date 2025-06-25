"""
Demo Script for Sanskrit Recognition Optimization

This script demonstrates the Sanskrit speech recognition optimization functionality
of the Vimarsh AI Agent, including phonetic transformations, context enhancement,
and statistical analysis.
"""

import asyncio
import logging
import time
from datetime import datetime

from sanskrit_optimizer import (
    SanskritRecognitionOptimizer,
    SanskritTerm,
    SanskritCategory,
    PhoneticRule,
    create_sanskrit_optimizer
)


async def demo_sanskrit_vocabulary():
    """Demonstrate Sanskrit vocabulary management"""
    
    print("📚 Sanskrit Vocabulary Demo")
    print("=" * 50)
    
    optimizer = create_sanskrit_optimizer()
    
    print(f"✅ Loaded Sanskrit vocabulary:")
    print(f"   Total terms: {len(optimizer.sanskrit_terms)}")
    print(f"   Phonetic rules: {len(optimizer.phonetic_rules)}")
    print(f"   Context clusters: {len(optimizer.context_clusters)}")
    
    # Show terms by category
    print(f"\n📖 Terms by Category:")
    
    categories = {}
    for term in optimizer.sanskrit_terms.values():
        category = term.category.value
        if category not in categories:
            categories[category] = []
        categories[category].append(term)
    
    for category, terms in categories.items():
        print(f"\n   {category.upper()} ({len(terms)} terms):")
        for term in terms[:5]:  # Show first 5 terms
            print(f"     • {term.term}")
            if term.devanagari:
                print(f"       Devanagari: {term.devanagari}")
            if term.literal_meaning:
                print(f"       Meaning: {term.literal_meaning}")
            print(f"       Priority: {term.recognition_priority:.1f}")
            print(f"       Variants: {', '.join(term.phonetic_variants[:3])}")
            print()
    
    return optimizer


async def demo_phonetic_transformations():
    """Demonstrate phonetic transformations"""
    
    print("🔊 Phonetic Transformations Demo")
    print("=" * 50)
    
    optimizer = create_sanskrit_optimizer()
    
    # Test various phonetic transformations
    test_cases = [
        "dhaarma",  # Extended vowels
        "kaarma",   # Extended vowels
        "yogaa",    # Extended vowels
        "shiva",    # Sibilant variations
        "vishnu",   # English speaker variations
        "ganesya",  # Common mispronunciation
        "mokshya",  # Aspirated consonants
        "pranayaam" # Multiple issues
    ]
    
    print("🧪 Testing phonetic transformations:")
    
    for test_case in test_cases:
        print(f"\n   Input: '{test_case}'")
        
        variants = optimizer.apply_phonetic_transformations(test_case)
        print(f"   Variants: {', '.join(variants)}")
        
        # Check if any variants match known terms
        matches = optimizer.find_sanskrit_matches(test_case)
        if matches:
            best_match = matches[0]
            print(f"   Best match: {best_match[0].term} (confidence: {best_match[1]:.2f})")
        else:
            print(f"   No matches found")
    
    # Show phonetic rules in action
    print(f"\n📝 Phonetic Rules Applied:")
    
    sample_rules = optimizer.phonetic_rules[:8]  # Show first 8 rules
    for rule in sample_rules:
        print(f"   Pattern: {rule.pattern} → {rule.replacement}")
        print(f"     Description: {rule.description}")
        if rule.context:
            print(f"     Context: {rule.context}")
        print()


async def demo_sanskrit_recognition():
    """Demonstrate Sanskrit term recognition"""
    
    print("🎯 Sanskrit Recognition Demo")
    print("=" * 50)
    
    optimizer = create_sanskrit_optimizer()
    
    # Test spiritual queries with Sanskrit terms
    test_queries = [
        "What is the meaning of dharma in the Bhagavad Gita?",
        "How can I practice yoga and pranayama daily?",
        "Please explain karma and its effects on our atman",
        "Tell me about Krishna's teachings on bhakti yoga",
        "What is samadhi in meditation practice?",
        "How do the Vedas describe the nature of Brahman?",
        "What does Om Namah Shivaya mean?",
        "Explain the concept of moksha and liberation",
        "How should I perform puja to Ganesha?",
        "What is the relationship between guru and disciple?"
    ]
    
    print("🔍 Analyzing spiritual queries:")
    
    all_recognized_terms = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}: '{query}'")
        
        # Find Sanskrit matches
        matches = optimizer.find_sanskrit_matches(query)
        
        if matches:
            print(f"   📋 Found {len(matches)} Sanskrit terms:")
            
            for term, confidence in matches:
                print(f"     • {term.term} (confidence: {confidence:.2f})")
                print(f"       Category: {term.category.value}")
                if term.devanagari:
                    print(f"       Devanagari: {term.devanagari}")
                if term.literal_meaning:
                    print(f"       Meaning: {term.literal_meaning}")
                
                # Update statistics
                optimizer.update_recognition_statistics(term.term, True, confidence)
                all_recognized_terms.append(term.term)
        else:
            print("   ❌ No Sanskrit terms found")
        
        print()
    
    return optimizer, all_recognized_terms


async def demo_context_enhancement():
    """Demonstrate context-based enhancement"""
    
    print("🌟 Context Enhancement Demo")
    print("=" * 50)
    
    optimizer = create_sanskrit_optimizer()
    
    # Test context scenarios
    scenarios = [
        {
            'name': 'Bhagavad Gita Discussion',
            'previous_terms': ['gita', 'krishna', 'arjuna', 'kurukshetra'],
            'query': 'What does dharma mean in this context?'
        },
        {
            'name': 'Yoga Practice Session',
            'previous_terms': ['yoga', 'asana', 'pranayama', 'meditation'],
            'query': 'How do I achieve samadhi through practice?'
        },
        {
            'name': 'Devotional Practice',
            'previous_terms': ['bhakti', 'devotion', 'krishna', 'love'],
            'query': 'What is the role of guru in spiritual life?'
        },
        {
            'name': 'Philosophical Discussion',
            'previous_terms': ['atman', 'brahman', 'consciousness', 'reality'],
            'query': 'How does maya affect our perception?'
        }
    ]
    
    print("🎭 Testing context scenarios:")
    
    for scenario in scenarios:
        print(f"\n📖 Scenario: {scenario['name']}")
        print(f"   Previous terms: {', '.join(scenario['previous_terms'])}")
        print(f"   Query: '{scenario['query']}'")
        
        # Analyze with context
        result = optimizer.enhance_recognition_with_context(
            scenario['query'], 
            scenario['previous_terms']
        )
        
        print(f"   📊 Context Analysis:")
        print(f"     Dominant context: {result['dominant_context']}")
        
        if result['context_scores']:
            print(f"     Context scores:")
            for context, score in result['context_scores'].items():
                print(f"       {context}: {score:.2f}")
        
        # Compare original vs enhanced matches
        if result['enhanced_matches']:
            print(f"   📈 Enhanced Matches:")
            for term, confidence in result['enhanced_matches'][:3]:
                # Find original confidence for comparison
                original_conf = None
                for orig_term, orig_conf in result['original_matches']:
                    if orig_term.term == term.term:
                        original_conf = orig_conf
                        break
                
                if original_conf:
                    boost = confidence - original_conf
                    print(f"     • {term.term}: {confidence:.2f} (+{boost:.2f} boost)")
                else:
                    print(f"     • {term.term}: {confidence:.2f}")
        
        print()


async def demo_pronunciation_variants():
    """Demonstrate pronunciation variant generation"""
    
    print("🗣️  Pronunciation Variants Demo")
    print("=" * 50)
    
    optimizer = create_sanskrit_optimizer()
    
    # Test key Sanskrit terms
    key_terms = [
        'dharma', 'karma', 'yoga', 'krishna', 'rama', 'shiva',
        'ganesha', 'hanuman', 'namaste', 'guru', 'moksha', 'samadhi'
    ]
    
    print("📋 Pronunciation variants for key terms:")
    
    for term in key_terms:
        variants = optimizer.generate_pronunciation_variants(term)
        
        print(f"\n   {term}:")
        
        if term in optimizer.sanskrit_terms:
            sanskrit_term = optimizer.sanskrit_terms[term]
            if sanskrit_term.devanagari:
                print(f"     Devanagari: {sanskrit_term.devanagari}")
            if sanskrit_term.iast:
                print(f"     IAST: {sanskrit_term.iast}")
        
        print(f"     Variants: {', '.join(variants)}")
        
        # Show phonetic and mispronunciation categories
        if term in optimizer.sanskrit_terms:
            sanskrit_term = optimizer.sanskrit_terms[term]
            if sanskrit_term.phonetic_variants:
                print(f"     Phonetic: {', '.join(sanskrit_term.phonetic_variants)}")
            if sanskrit_term.common_mispronunciations:
                print(f"     Common errors: {', '.join(sanskrit_term.common_mispronunciations)}")


async def demo_recognition_statistics():
    """Demonstrate recognition statistics and optimization"""
    
    print("📊 Recognition Statistics Demo")
    print("=" * 50)
    
    optimizer = create_sanskrit_optimizer()
    
    # Simulate recognition data
    print("🎯 Simulating recognition data...")
    
    simulation_data = [
        ('dharma', True, 0.92),
        ('karma', True, 0.88),
        ('yoga', True, 0.95),
        ('krishna', True, 0.90),
        ('moksha', False, 0.45),  # Failed recognition
        ('samadhi', True, 0.75),
        ('atman', True, 0.82),
        ('brahman', False, 0.38),  # Failed recognition
        ('pranayama', True, 0.79),
        ('guru', True, 0.91),
        ('dharma', True, 0.89),   # Repeat
        ('karma', True, 0.93),    # Repeat
        ('yoga', True, 0.97),     # Repeat
        ('moksha', True, 0.68),   # Improved
        ('ganesha', True, 0.85),
        ('shiva', True, 0.88)
    ]
    
    for term, success, confidence in simulation_data:
        optimizer.update_recognition_statistics(term, success, confidence)
    
    # Show comprehensive statistics
    stats = optimizer.get_statistics()
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total terms loaded: {stats['total_terms_loaded']}")
    print(f"   Recognition attempts: {stats['total_recognitions_attempted']}")
    print(f"   Successful recognitions: {stats['successful_recognitions']}")
    print(f"   Failed recognitions: {stats['failed_recognitions']}")
    print(f"   Overall success rate: {stats['overall_success_rate']:.2%}")
    
    print(f"\n📊 Category Performance:")
    for category, category_stats in stats['categories'].items():
        if category_stats['term_count'] > 0:
            print(f"   {category}:")
            print(f"     Terms: {category_stats['term_count']}")
            print(f"     Avg Priority: {category_stats['average_priority']:.2f}")
            print(f"     Avg Accuracy: {category_stats['average_accuracy']:.2f}")
    
    # Show optimization recommendations
    recommendations = optimizer.get_optimization_recommendations()
    
    print(f"\n🎯 Optimization Recommendations:")
    
    if recommendations['priority_terms']:
        print(f"   Priority terms needing attention:")
        for term_info in recommendations['priority_terms'][:5]:
            print(f"     • {term_info['term']}: accuracy {term_info['accuracy']:.2f}")
    
    if recommendations['problem_categories']:
        print(f"   Problem categories:")
        for cat_info in recommendations['problem_categories']:
            print(f"     • {cat_info['category']}: avg confidence {cat_info['average_confidence']:.2f}")
    
    if recommendations['suggested_improvements']:
        print(f"   Suggested improvements:")
        for improvement in recommendations['suggested_improvements']:
            print(f"     • {improvement}")
    
    if recommendations['training_focus']:
        print(f"   Training focus recommendations:")
        for focus in recommendations['training_focus']:
            print(f"     • {focus['term']}: priority {focus['priority']}")


async def demo_error_handling():
    """Demonstrate error handling and edge cases"""
    
    print("🛡️  Error Handling Demo")
    print("=" * 50)
    
    optimizer = create_sanskrit_optimizer()
    
    # Test edge cases
    edge_cases = [
        "",  # Empty string
        "   ",  # Whitespace only
        "12345",  # Numbers only
        "!@#$%",  # Special characters only
        "english text only",  # No Sanskrit terms
        "dhaaaaarrrrmaaaa",  # Extremely distorted
        "krshnkrshnkrshn",  # Corrupted repetition
        "very very very long text without any sanskrit terms at all just to test performance",
        "mixed dharmaCAPITALS123numbers!@#",  # Mixed case and special chars
    ]
    
    print("🧪 Testing edge cases:")
    
    for i, case in enumerate(edge_cases, 1):
        print(f"\n   Test {i}: '{case[:50]}{'...' if len(case) > 50 else ''}'")
        
        try:
            matches = optimizer.find_sanskrit_matches(case)
            
            if matches:
                print(f"     Found {len(matches)} matches:")
                for term, confidence in matches[:2]:  # Show top 2
                    print(f"       • {term.term}: {confidence:.2f}")
            else:
                print(f"     No matches found (expected)")
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    # Test performance with large text
    print(f"\n⚡ Performance test with large text:")
    
    large_text = ("What is dharma? " * 1000)  # Large repetitive text
    
    start_time = time.time()
    matches = optimizer.find_sanskrit_matches(large_text)
    end_time = time.time()
    
    processing_time = end_time - start_time
    print(f"   Processed {len(large_text)} characters in {processing_time:.3f} seconds")
    print(f"   Found {len(matches)} matches")
    print(f"   Performance: {len(large_text) / processing_time:.0f} chars/second")


async def main():
    """Main demo function"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Vimarsh AI Agent - Sanskrit Recognition Optimization Demo")
    print("=" * 70)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Run vocabulary demo
        optimizer = await demo_sanskrit_vocabulary()
        
        # Run phonetic transformations demo
        await demo_phonetic_transformations()
        
        # Run recognition demo
        optimizer, recognized_terms = await demo_sanskrit_recognition()
        
        # Run context enhancement demo
        await demo_context_enhancement()
        
        # Run pronunciation variants demo
        await demo_pronunciation_variants()
        
        # Run statistics demo
        await demo_recognition_statistics()
        
        # Run error handling demo
        await demo_error_handling()
        
        print("\n🎉 All Sanskrit optimization demos completed successfully!")
        print("=" * 70)
        
        # Final summary
        final_stats = optimizer.get_statistics()
        
        print(f"📈 Final Statistics:")
        print(f"   Sanskrit terms loaded: {final_stats['total_terms_loaded']}")
        print(f"   Recognition attempts: {final_stats['total_recognitions_attempted']}")
        print(f"   Overall success rate: {final_stats['overall_success_rate']:.2%}")
        print(f"   Categories supported: {len(final_stats['categories'])}")
        
        print(f"\n✅ Sanskrit recognition optimization system is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
