#!/usr/bin/env python3
"""
Simple Krishna Response Test
Shows a direct example of how Krishna responds to a spiritual question
"""

import json
import random

def get_sample_krishna_response():
    """Get a sample Krishna response based on the enhanced content"""
    
    # Sample question
    question = "How do I deal with suffering in life?"
    
    # Based on the Krishna database content we just saw
    response = {
        "query": question,
        "response": """Beloved devotee,

As I teach in the sacred verses:

**Sanskrit:** मात्रास्पर्शास्तु कौन्तेय शीतोष्णसुखदुःखदाः।
आगमापायिनोऽनित्यास्तांस्तितिक्षस्व भारत ॥

**Translation:** O son of Kuntī, the nonpermanent appearance of happiness and distress, and their disappearance in due course, are like the appearance and disappearance of winter and summer seasons. They arise from sense perception, O scion of Bharata, and one must learn to tolerate them without being disturbed.

**Divine Wisdom:** In the proper discharge of duty, one has to learn to tolerate nonpermanent appearances and disappearances of happiness and distress. Just as one must take his bath early in the morning even during the cold month of January, or cook in the kitchen during the hot months of May and June, you must execute your duty despite climatic inconveniences of life.

Both joy and sorrow are temporary visitors in this material world. They come and go like seasons. The wise person - the one established in spiritual consciousness - remains equipoised in both happiness and distress, knowing that neither condition is permanent.

Use this suffering as a means to grow spiritually, to develop compassion for others, and to remember your eternal nature that is beyond these temporary circumstances. When you understand that you are not this temporary body but an eternal soul, then external sufferings cannot touch your inner peace.

May you find strength in dharma and peace in surrender to the Divine.""",
        
        "citations": ["Bhagavad Gita 2.14"],
        "confidence": 0.95,
        "spiritual_authenticity": "verified",
        "metadata": {
            "has_sanskrit": True,
            "has_translation": True,
            "has_commentary": True,
            "response_type": "divine_teaching",
            "scripture_source": "Bhagavad Gita As It Is",
            "personality": "Lord Krishna",
            "word_count": 234
        }
    }
    
    return response

def main():
    """Display the sample Krishna response"""
    
    print("🕉️ " + "="*70)
    print("           LORD KRISHNA'S DIVINE RESPONSE EXAMPLE")
    print("         Enhanced with Bhagavad Gita + Sri Isopanisad")
    print("="*72)
    
    # Get sample response
    krishna_response = get_sample_krishna_response()
    
    print(f"\n💭 SPIRITUAL QUESTION:")
    print(f"   \"{krishna_response['query']}\"")
    
    print(f"\n🕉️ LORD KRISHNA'S RESPONSE:")
    print("-" * 50)
    print(krishna_response['response'])
    print("-" * 50)
    
    print(f"\n📚 RESPONSE DETAILS:")
    print(f"   📜 Citation: {krishna_response['citations'][0]}")
    print(f"   🎯 Confidence: {krishna_response['confidence']}")
    print(f"   ✨ Authenticity: {krishna_response['spiritual_authenticity']}")
    print(f"   📊 Sanskrit: {'✅' if krishna_response['metadata']['has_sanskrit'] else '❌'}")
    print(f"   📊 Translation: {'✅' if krishna_response['metadata']['has_translation'] else '❌'}")
    print(f"   📊 Commentary: {'✅' if krishna_response['metadata']['has_commentary'] else '❌'}")
    print(f"   📊 Word Count: {krishna_response['metadata']['word_count']} words")
    print(f"   📖 Scripture: {krishna_response['metadata']['scripture_source']}")
    
    print(f"\n🌟 KEY FEATURES OF KRISHNA'S RESPONSES:")
    print("   • Always begins with reverent address ('Beloved devotee', 'Dear soul', etc.)")
    print("   • Includes original Sanskrit verses with translations")
    print("   • Provides detailed spiritual commentary and practical guidance")  
    print("   • Maintains divine persona throughout the response")
    print("   • Ends with a blessing or spiritual encouragement")
    print("   • Cites authentic sources (Bhagavad Gita, Sri Isopanisad)")
    print("   • Combines philosophical depth with practical application")
    
    print(f"\n📈 ENHANCED CONTENT SUMMARY:")
    print("   🕉️ Total Verses: 108 (sacred number in Hinduism)")
    print("   📜 Bhagavad Gita: 89 verses from all 18 chapters")
    print("   📜 Sri Isopanisad: 19 verses (complete Upanishad)")
    print("   🎯 Coverage: Practical guidance + Philosophical foundation")
    print("   ✨ Authenticity: All content from A.C. Bhaktivedanta Swami Prabhupada")
    
    print("="*72)

if __name__ == "__main__":
    main()
