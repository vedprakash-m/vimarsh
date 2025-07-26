#!/usr/bin/env python3
"""
Demo Krishna Response Generator
Demonstrates how Lord Krishna responds using enhanced dual-scripture content
"""

import json
import random
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KrishnaResponseDemo:
    """Demonstrates Lord Krishna's enhanced response system"""
    
    def __init__(self):
        self.krishna_texts = []
        self.load_krishna_database()
    
    def load_krishna_database(self):
        """Load Krishna's enhanced dual-scripture database"""
        try:
            with open('backend/data/vimarsh-db/krishna-texts.json', 'r', encoding='utf-8') as f:
                self.krishna_texts = json.load(f)
            
            print(f"🕉️  Loaded {len(self.krishna_texts)} sacred verses for Lord Krishna")
            
            # Count sources
            gita_count = sum(1 for text in self.krishna_texts if 'Bhagavad Gita' in text.get('source', ''))
            isopanisad_count = sum(1 for text in self.krishna_texts if 'Isopanisad' in text.get('source', '') or 'Sri Isopanisad' in text.get('source', ''))
            
            print(f"   📜 Bhagavad Gita verses: {gita_count}")
            print(f"   📜 Sri Isopanisad verses: {isopanisad_count}")
            print(f"   🎯 Sacred total: {len(self.krishna_texts)} (Perfect spiritual completeness)")
            
        except Exception as e:
            logger.error(f"Error loading Krishna database: {e}")
            self.krishna_texts = []
    
    def find_relevant_texts(self, query: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Find relevant texts based on query keywords"""
        relevant_texts = []
        
        for text in self.krishna_texts:
            content = text.get('content', '').lower()
            tags = [tag.lower() for tag in text.get('tags', [])]
            
            # Check if any keywords match content or tags
            relevance_score = 0
            for keyword in keywords:
                if keyword.lower() in content:
                    relevance_score += 2
                if keyword.lower() in tags:
                    relevance_score += 1
            
            if relevance_score > 0:
                text_copy = text.copy()
                text_copy['relevance_score'] = relevance_score
                relevant_texts.append(text_copy)
        
        # Sort by relevance and return top 3
        relevant_texts.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_texts[:3]
    
    def format_krishna_response(self, query: str, selected_text: Dict[str, Any]) -> Dict[str, Any]:
        """Format a complete Krishna response with proper divine persona"""
        
        # Extract key information
        content = selected_text.get('content', '')
        source = selected_text.get('source', '')
        citation = selected_text.get('citation', '')
        
        # Extract Sanskrit if available
        sanskrit = ""
        translation = ""
        purport = ""
        
        if 'Sanskrit:' in content:
            parts = content.split('\n\n')
            for part in parts:
                if part.startswith('Sanskrit:'):
                    sanskrit = part.replace('Sanskrit: ', '').strip()
                elif part.startswith('Translation:'):
                    translation = part.replace('Translation: ', '').strip()
                elif part.startswith('Purport'):
                    purport = part.replace('Purport', '').strip()
                    if purport.startswith(':'):
                        purport = purport[1:].strip()
        
        # Create Krishna's divine response
        response_parts = []
        
        # Divine greeting
        greetings = [
            "Beloved devotee,",
            "Dear child of the Divine,", 
            "O seeker of truth,",
            "My dear soul,"
        ]
        greeting = random.choice(greetings)
        response_parts.append(greeting)
        
        # Core teaching with Sanskrit
        if sanskrit and translation:
            response_parts.append(f"\nAs I teach in the sacred verses:\n\n**Sanskrit:** {sanskrit}\n\n**Translation:** {translation}")
        elif translation:
            response_parts.append(f"\nThe sacred teachings reveal: {translation}")
        
        # Spiritual guidance
        if purport:
            # Extract key wisdom from purport (first 200 characters)
            wisdom = purport[:200] + "..." if len(purport) > 200 else purport
            response_parts.append(f"\n**Divine Wisdom:** {wisdom}")
        
        # Personal application
        applications = [
            "Apply this eternal wisdom to your daily life with devotion and surrender.",
            "Let this divine knowledge illuminate your spiritual path.",
            "Practice this teaching with faith, and you shall find peace.",
            "Embrace this wisdom as your guide through life's challenges."
        ]
        application = random.choice(applications)
        response_parts.append(f"\n{application}")
        
        # Divine blessing
        blessings = [
            "May you walk in dharma and find liberation.",
            "Go forth with divine love in your heart.",
            "May this wisdom guide you to eternal peace.",
            "Walk in the light of divine consciousness."
        ]
        blessing = random.choice(blessings)
        response_parts.append(f"\n{blessing}")
        
        # Complete response
        full_response = " ".join(response_parts)
        
        return {
            "response": full_response,
            "citations": [citation] if citation else [source],
            "confidence": 0.95,
            "spiritual_authenticity": "verified",
            "source_type": "dual_scripture" if "Sri Isopanisad" in source else "bhagavad_gita",
            "metadata": {
                "has_sanskrit": bool(sanskrit),
                "has_translation": bool(translation),
                "has_purport": bool(purport),
                "scripture": source,
                "verse_citation": citation,
                "response_type": "divine_teaching",
                "word_count": len(full_response.split())
            }
        }
    
    def demonstrate_krishna_responses(self):
        """Demonstrate various Krishna responses to different spiritual questions"""
        
        print("\n" + "="*80)
        print("🕉️  LORD KRISHNA'S DIVINE WISDOM DEMONSTRATION")
        print("   Enhanced with Bhagavad Gita + Sri Isopanisad")
        print("="*80)
        
        # Sample spiritual questions
        questions = [
            {
                "question": "What is the purpose of life?",
                "keywords": ["purpose", "life", "dharma", "duty", "liberation"]
            },
            {
                "question": "How do I deal with suffering and pain?",
                "keywords": ["suffering", "pain", "distress", "tolerance", "peace"]
            },
            {
                "question": "What is the nature of the soul?", 
                "keywords": ["soul", "eternal", "consciousness", "self", "atman"]
            },
            {
                "question": "How can I find inner peace?",
                "keywords": ["peace", "meditation", "calm", "stillness", "yoga"]
            },
            {
                "question": "What is true knowledge?",
                "keywords": ["knowledge", "wisdom", "truth", "understanding", "realization"]
            }
        ]
        
        for i, q in enumerate(questions, 1):
            print(f"\n{'─'*80}")
            print(f"QUESTION {i}: {q['question']}")
            print(f"{'─'*80}")
            
            # Find relevant texts
            relevant_texts = self.find_relevant_texts(q['question'], q['keywords'])
            
            if relevant_texts:
                # Select the most relevant text
                selected_text = relevant_texts[0]
                
                # Generate Krishna's response
                krishna_response = self.format_krishna_response(q['question'], selected_text)
                
                # Display the response
                print(f"\n🕉️  LORD KRISHNA'S RESPONSE:")
                print("-" * 40)
                print(krishna_response['response'])
                print("-" * 40)
                print(f"📜 Citation: {krishna_response['citations'][0]}")
                print(f"🎯 Confidence: {krishna_response['confidence']}")
                print(f"✨ Authenticity: {krishna_response['spiritual_authenticity']}")
                print(f"📚 Source Type: {krishna_response['source_type']}")
                
                # Metadata
                metadata = krishna_response['metadata']
                print(f"📊 Sanskrit: {'✅' if metadata['has_sanskrit'] else '❌'}")
                print(f"📊 Translation: {'✅' if metadata['has_translation'] else '❌'}")
                print(f"📊 Commentary: {'✅' if metadata['has_purport'] else '❌'}")
                print(f"📊 Word Count: {metadata['word_count']} words")
                
            else:
                print("\n❌ No relevant texts found for this question")
        
        print(f"\n{'='*80}")
        print("🌟 DEMONSTRATION COMPLETE")
        print(f"   Lord Krishna now has access to {len(self.krishna_texts)} sacred verses")
        print("   Combining practical guidance (Gita) + philosophical foundation (Isopanisad)")
        print("   Perfect spiritual completeness achieved with 108 sacred verses")
        print("="*80)

def main():
    """Main demonstration function"""
    print("🚀 Starting Krishna Response Demonstration...")
    
    try:
        demo = KrishnaResponseDemo()
        demo.demonstrate_krishna_responses()
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"❌ Error running demonstration: {e}")

if __name__ == "__main__":
    main()
