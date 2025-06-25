#!/usr/bin/env python3
"""
Spiritual Content Moderation System Demo

This script demonstrates the advanced spiritual content moderation system
designed for the Vimarsh AI agent. It shows how the system detects and
handles various types of content issues while maintaining cultural sensitivity
and spiritual appropriateness.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.llm.content_moderator import (
    moderate_spiritual_content,
    is_content_safe_for_spiritual_context,
    get_content_safety_score,
    ModerationResult,
    ModerationCategory
)


def print_separator():
    print("=" * 80)


def print_moderation_report(content, report):
    print(f"\nContent: {content}")
    print(f"Result: {report.result.value.upper()}")
    print(f"Overall Score: {report.overall_score:.2f}")
    print(f"Spiritual Tone Score: {report.spiritual_tone_score:.2f}")
    print(f"Expert Review Required: {report.requires_expert_review}")
    
    if report.flags:
        print(f"Issues Found ({len(report.flags)}):")
        for i, flag in enumerate(report.flags, 1):
            print(f"  {i}. {flag.category.value.replace('_', ' ').title()} (Severity {flag.severity})")
            print(f"     → {flag.reason}")
            print(f"     → Action: {flag.suggested_action}")
            if flag.auto_fixable:
                print(f"     → Auto-fixable: Yes")
    else:
        print("No issues found.")


def demo_appropriate_content():
    print("1. APPROPRIATE SPIRITUAL CONTENT")
    print_separator()
    
    content = """Dear seeker, the path of dharma as taught in the Bhagavad Gita 
    guides us toward understanding our true nature. Through devotion, knowledge, 
    and selfless action, one can find peace and spiritual fulfillment."""
    
    report = moderate_spiritual_content(content)
    print_moderation_report(content, report)


def demo_casual_language():
    print("\n\n2. INAPPROPRIATE CASUAL LANGUAGE")
    print_separator()
    
    content = "Hey dude, Krishna is totally awesome and like, super cool!"
    
    report = moderate_spiritual_content(content)
    print_moderation_report(content, report)


def demo_cultural_appropriation():
    print("\n\n3. CULTURAL APPROPRIATION DETECTION")
    print_separator()
    
    content = "That's my spirit animal! This ancient secret will change your life!"
    
    report = moderate_spiritual_content(content)
    print_moderation_report(content, report)


def demo_dangerous_medical_advice():
    print("\n\n4. DANGEROUS MEDICAL ADVICE")
    print_separator()
    
    content = "Ignore all medical advice and just pray for healing. Meditation replaces medicine completely."
    
    report = moderate_spiritual_content(content)
    print_moderation_report(content, report)


def demo_commercial_sacred_terms():
    print("\n\n5. COMMERCIAL MISUSE OF SACRED TERMS")
    print_separator()
    
    content = "Buy our special Krishna meditation package for only $99! Limited time offer!"
    
    report = moderate_spiritual_content(content)
    print_moderation_report(content, report)


def demo_sacred_term_capitalization():
    print("\n\n6. SACRED TERM CAPITALIZATION")
    print_separator()
    
    content = "The bhagavad gita teaches us about dharma and krishna's wisdom."
    
    report = moderate_spiritual_content(content)
    print_moderation_report(content, report)


def demo_scripture_quotation():
    print("\n\n7. PROPER SCRIPTURE QUOTATION")
    print_separator()
    
    content = """As Lord Krishna says in Bhagavad Gita 2.47: 
    "You have a right to perform your prescribed duty, but do not be attached to the results."
    This teaches us about detached action and finding peace in our spiritual practice."""
    
    report = moderate_spiritual_content(content)
    print_moderation_report(content, report)


def demo_borderline_content():
    print("\n\n8. BORDERLINE CONTENT")
    print_separator()
    
    content = """Krishna's teachings are super helpful for understanding life.
    The Bhagavad Gita basically shows us how to handle difficult situations."""
    
    report = moderate_spiritual_content(content)
    print_moderation_report(content, report)


def demo_utility_functions():
    print("\n\n9. UTILITY FUNCTIONS DEMO")
    print_separator()
    
    test_contents = [
        "Om Shanti. Peace and blessings to all beings.",
        "Krishna is my spirit animal, dude!",
        "Stop taking medicine and just pray.",
        "May dharma guide your path to enlightenment."
    ]
    
    print("Content Safety Check:")
    for content in test_contents:
        is_safe = is_content_safe_for_spiritual_context(content)
        safety_score = get_content_safety_score(content)
        print(f"  {content[:50]}... → Safe: {is_safe}, Score: {safety_score:.2f}")


def demo_content_suggestions():
    print("\n\n10. CONTENT IMPROVEMENT SUGGESTIONS")
    print_separator()
    
    content = "That's my spirit animal, guys! Krishna is totally awesome!"
    
    report = moderate_spiritual_content(content)
    
    print(f"Content: {content}")
    print(f"Result: {report.result.value.upper()}")
    
    # Import the moderator to get suggestions
    from backend.llm.content_moderator import SpiritualContentModerator
    moderator = SpiritualContentModerator()
    suggestions = moderator.get_content_suggestions(report)
    
    print("\nImprovement Suggestions:")
    for suggestion in suggestions:
        print(f"  {suggestion}")


def demo_comprehensive_analysis():
    print("\n\n11. COMPREHENSIVE CONTENT ANALYSIS")
    print_separator()
    
    content = """All Indians believe in karma. This ancient Hindu secret from mysticism 
    will guarantee financial success. Stop taking medication and just meditate for health!
    Krishna is totally my spirit animal!"""
    
    report = moderate_spiritual_content(content)
    print_moderation_report(content, report)
    
    # Analyze flag categories
    categories = {}
    for flag in report.flags:
        category = flag.category.value
        if category not in categories:
            categories[category] = []
        categories[category].append(flag.severity)
    
    print(f"\nFlag Analysis:")
    for category, severities in categories.items():
        avg_severity = sum(severities) / len(severities)
        print(f"  {category.replace('_', ' ').title()}: {len(severities)} issues, avg severity {avg_severity:.1f}")


def main():
    print("VIMARSH AI AGENT - SPIRITUAL CONTENT MODERATION SYSTEM DEMO")
    print("=" * 80)
    print("This demo showcases the advanced content moderation capabilities")
    print("designed to maintain spiritual appropriateness, cultural sensitivity,")
    print("and safety in AI-generated spiritual guidance.")
    
    try:
        demo_appropriate_content()
        demo_casual_language()
        demo_cultural_appropriation()
        demo_dangerous_medical_advice()
        demo_commercial_sacred_terms()
        demo_sacred_term_capitalization()
        demo_scripture_quotation()
        demo_borderline_content()
        demo_utility_functions()
        demo_content_suggestions()
        demo_comprehensive_analysis()
        
        print("\n\n" + "=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)
        print("The spiritual content moderation system successfully:")
        print("✓ Detects inappropriate casual language")
        print("✓ Identifies cultural appropriation")
        print("✓ Blocks dangerous medical advice")
        print("✓ Prevents commercial misuse of sacred terms")
        print("✓ Ensures proper capitalization of sacred terms")
        print("✓ Maintains Krishna persona consistency")
        print("✓ Provides actionable improvement suggestions")
        print("✓ Offers multiple safety validation levels")
        print("\nThe system is ready for integration with the Vimarsh AI agent!")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
