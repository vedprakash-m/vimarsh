"""
Sacred Text Data Loader for Vimarsh Vector Database
Populates Cosmos DB with structured spiritual content from Hindu sacred texts.
"""

import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib
from pathlib import Path
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SacredTextEntry:
    """Structured representation of sacred text content."""
    id: str
    text: str
    source: str
    chapter: Optional[str] = None
    verse: Optional[str] = None
    sanskrit: Optional[str] = None
    translation: Optional[str] = None
    spiritual_theme: Optional[str] = None
    dharmic_context: Optional[str] = None
    keywords: List[str] = None
    language: str = "English"
    
    @property
    def title(self) -> str:
        """Generate title from source, chapter, and verse."""
        if self.chapter and self.verse:
            return f"{self.source} {self.chapter}.{self.verse}"
        elif self.chapter:
            return f"{self.source} Chapter {self.chapter}"
        else:
            return self.source
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "title": self.title,  # Add title field
            "text": self.text,
            "content": self.text,  # Map text to content for compatibility
            "source": self.source,
            "chapter": self.chapter,
            "verse": self.verse,
            "sanskrit": self.sanskrit,
            "translation": self.translation,
            "spiritual_theme": self.spiritual_theme,
            "dharmic_context": self.dharmic_context,
            "keywords": self.keywords or [],
            "language": self.language,
            "content_type": "sacred_text",
            "created_at": "2025-07-02T00:00:00Z"
        }

class SacredTextDataLoader:
    """Loads and structures sacred text data for vector database."""
    
    def __init__(self):
        self.sacred_texts = []
        
    def generate_text_id(self, source: str, chapter: str = None, verse: str = None) -> str:
        """Generate unique ID for text entry."""
        identifier = f"{source}"
        if chapter:
            identifier += f"_ch{chapter}"
        if verse:
            identifier += f"_v{verse}"
        
        # Create hash for uniqueness
        hash_obj = hashlib.md5(identifier.encode())
        return f"sacred_{hash_obj.hexdigest()[:12]}"
    
    def load_bhagavad_gita_texts(self) -> List[SacredTextEntry]:
        """Load comprehensive Bhagavad Gita verses."""
        logger.info("Loading Bhagavad Gita texts...")
        
        gita_texts = [
            # Chapter 2 - Sankhya Yoga (The Yoga of Knowledge)
            {
                "text": "You have a right to perform your prescribed duty, but not to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.",
                "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
                "chapter": "2", "verse": "47",
                "spiritual_theme": "Karma Yoga",
                "dharmic_context": "Duty without attachment",
                "keywords": ["duty", "karma", "action", "detachment", "results"]
            },
            {
                "text": "Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure. Such equanimity is called yoga.",
                "sanskrit": "योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय। सिद्ध्यसिद्ध्योः समो भूत्वा समत्वं योग उच्यते॥",
                "chapter": "2", "verse": "48",
                "spiritual_theme": "Equanimity",
                "dharmic_context": "Balance in action",
                "keywords": ["yoga", "equanimity", "balance", "success", "failure"]
            },
            {
                "text": "One who is not disturbed by the incessant flow of desires can alone achieve peace, and not the person who strives to satisfy such desires.",
                "sanskrit": "आपूर्यमाणमचलप्रतिष्ठं समुद्रमापः प्रविशन्ति यद्वत्। तद्वत्कामा यं प्रविशन्ति सर्वे स शान्तिमाप्नोति न कामकामी॥",
                "chapter": "2", "verse": "70",
                "spiritual_theme": "Inner Peace",
                "dharmic_context": "Desire and contentment",
                "keywords": ["peace", "desires", "contentment", "tranquility", "self-control"]
            },
            
            # Chapter 3 - Karma Yoga (The Yoga of Action)
            {
                "text": "It is better to engage in one's own occupation, even though one may perform it imperfectly, than to accept another's occupation and perform it perfectly.",
                "sanskrit": "श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्। स्वधर्मे निधनं श्रेयः परधर्मो भयावहः॥",
                "chapter": "3", "verse": "35",
                "spiritual_theme": "Svadharma",
                "dharmic_context": "Personal duty and calling",
                "keywords": ["svadharma", "duty", "occupation", "calling", "authenticity"]
            },
            {
                "text": "All living entities are forced to act helplessly according to the qualities they have acquired from the modes of material nature; therefore no one can refrain from doing something, not even for a moment.",
                "sanskrit": "न हि कश्चित्क्षणमपि जातु तिष्ठत्यकर्मकृत्। कार्यते ह्यवशः कर्म सर्वः प्रकृतिजैर्गुणैः॥",
                "chapter": "3", "verse": "5",
                "spiritual_theme": "Nature of Action",
                "dharmic_context": "Inherent activity",
                "keywords": ["action", "nature", "qualities", "modes", "activity"]
            },
            
            # Chapter 4 - Jnana Yoga (The Yoga of Knowledge)
            {
                "text": "Whenever and wherever there is a decline in religious practice, O descendant of Bharata, and a predominant rise of irreligion—at that time I descend Myself.",
                "sanskrit": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत। अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥",
                "chapter": "4", "verse": "7",
                "spiritual_theme": "Divine Intervention",
                "dharmic_context": "Protection of dharma",
                "keywords": ["dharma", "divine", "intervention", "protection", "righteousness"]
            },
            {
                "text": "To deliver the pious and to annihilate the miscreants, as well as to reestablish the principles of religion, I Myself appear, millennium after millennium.",
                "sanskrit": "परित्राणाय साधूनां विनाशाय च दुष्कृताम्। धर्मसंस्थापनार्थाय सम्भवामि युगे युगे॥",
                "chapter": "4", "verse": "8",
                "spiritual_theme": "Divine Purpose",
                "dharmic_context": "Cosmic justice",
                "keywords": ["protection", "justice", "dharma", "cosmic", "divine purpose"]
            },
            
            # Chapter 6 - Dhyana Yoga (The Yoga of Meditation)
            {
                "text": "When meditation is mastered, the mind is unwavering like the flame of a lamp in a windless place.",
                "sanskrit": "यथा दीपो निवातस्थो नेङ्गते सोपमा स्मृता। योगिनो यतचित्तस्य युञ्जतो योगमात्मनः॥",
                "chapter": "6", "verse": "19",
                "spiritual_theme": "Meditation",
                "dharmic_context": "Mental stability",
                "keywords": ["meditation", "mind", "concentration", "stability", "focus"]
            },
            {
                "text": "For one who has conquered the mind, the mind is the best of friends; but for one who has failed to do so, his very mind will be the greatest enemy.",
                "sanskrit": "बन्धुरात्मात्मनस्तस्य येनात्मैवात्मना जितः। अनात्मनस्तु शत्रुत्वे वर्ते तात्मैव शत्रुवत्॥",
                "chapter": "6", "verse": "6",
                "spiritual_theme": "Mind Control",
                "dharmic_context": "Self-mastery",
                "keywords": ["mind", "control", "self-mastery", "friend", "enemy"]
            },
            
            # Chapter 7 - Jnana-Vijnana Yoga (The Yoga of Knowledge and Wisdom)
            {
                "text": "Among thousands of persons, hardly one strives for perfection, and of those who have achieved perfection, hardly one knows Me in truth.",
                "sanskrit": "मनुष्याणां सहस्रेषु कश्चिद्यतति सिद्धये। यततामपि सिद्धानां कश्चिन्मां वेत्ति तत्त्वतः॥",
                "chapter": "7", "verse": "3",
                "spiritual_theme": "Divine Knowledge",
                "dharmic_context": "Spiritual rarity",
                "keywords": ["perfection", "knowledge", "truth", "realization", "divinity"]
            },
            
            # Chapter 18 - Moksha Yoga (The Yoga of Liberation)
            {
                "text": "Abandon all varieties of religion and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear.",
                "sanskrit": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज। अहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
                "chapter": "18", "verse": "66",
                "spiritual_theme": "Complete Surrender",
                "dharmic_context": "Ultimate liberation",
                "keywords": ["surrender", "liberation", "forgiveness", "fearlessness", "moksha"]
            }
        ]
        
        entries = []
        for text_data in gita_texts:
            entry = SacredTextEntry(
                id=self.generate_text_id("Bhagavad Gita", text_data["chapter"], text_data["verse"]),
                text=text_data["text"],
                source="Bhagavad Gita",
                chapter=text_data["chapter"],
                verse=text_data["verse"],
                sanskrit=text_data["sanskrit"],
                spiritual_theme=text_data["spiritual_theme"],
                dharmic_context=text_data["dharmic_context"],
                keywords=text_data["keywords"],
                language="English"
            )
            entries.append(entry)
        
        logger.info(f"Loaded {len(entries)} Bhagavad Gita texts")
        return entries
    
    def load_upanishad_texts(self) -> List[SacredTextEntry]:
        """Load key Upanishad teachings."""
        logger.info("Loading Upanishad texts...")
        
        upanishad_texts = [
            {
                "text": "That which is the finest essence—this whole world has that as its soul. That is Reality. That is Atman. That art thou.",
                "sanskrit": "तत्त्वमसि",
                "source": "Chandogya Upanishad",
                "chapter": "6", "verse": "8.7",
                "spiritual_theme": "Self-Realization",
                "dharmic_context": "Identity with Brahman",
                "keywords": ["atman", "brahman", "reality", "essence", "identity"]
            },
            {
                "text": "Lead me from the unreal to the real. Lead me from darkness to light. Lead me from death to immortality.",
                "sanskrit": "असतो मा सद्गमय। तमसो मा ज्योतिर्गमय। मृत्योर्मा अमृतं गमय॥",
                "source": "Brihadaranyaka Upanishad",
                "chapter": "1", "verse": "3.28",
                "spiritual_theme": "Spiritual Aspiration",
                "dharmic_context": "Journey to truth",
                "keywords": ["truth", "light", "immortality", "spiritual journey", "transformation"]
            },
            {
                "text": "I am Brahman. This is the great statement of the Upanishads.",
                "sanskrit": "अहं ब्रह्मास्मि",
                "source": "Brihadaranyaka Upanishad",
                "chapter": "1", "verse": "4.10",
                "spiritual_theme": "Self-Realization",
                "dharmic_context": "Ultimate identity",
                "keywords": ["brahman", "self", "identity", "realization", "consciousness"]
            }
        ]
        
        entries = []
        for text_data in upanishad_texts:
            entry = SacredTextEntry(
                id=self.generate_text_id(text_data["source"], text_data["chapter"], text_data["verse"]),
                text=text_data["text"],
                source=text_data["source"],
                chapter=text_data["chapter"],
                verse=text_data["verse"],
                sanskrit=text_data["sanskrit"],
                spiritual_theme=text_data["spiritual_theme"],
                dharmic_context=text_data["dharmic_context"],
                keywords=text_data["keywords"],
                language="English"
            )
            entries.append(entry)
        
        logger.info(f"Loaded {len(entries)} Upanishad texts")
        return entries
    
    def load_practical_guidance_texts(self) -> List[SacredTextEntry]:
        """Load practical spiritual guidance content."""
        logger.info("Loading practical guidance texts...")
        
        practical_texts = [
            {
                "text": "To overcome anxiety and worry, practice living in the present moment. Surrender your concerns to the Divine and focus on performing your duties with devotion.",
                "source": "Spiritual Guidance",
                "spiritual_theme": "Anxiety Management",
                "dharmic_context": "Present moment awareness",
                "keywords": ["anxiety", "worry", "present moment", "surrender", "devotion"]
            },
            {
                "text": "True success comes not from achieving material goals, but from aligning your actions with your dharma and serving others with a pure heart.",
                "source": "Spiritual Guidance", 
                "spiritual_theme": "Success Redefined",
                "dharmic_context": "Dharmic achievement",
                "keywords": ["success", "dharma", "service", "pure heart", "alignment"]
            },
            {
                "text": "In relationships, practice compassion and understanding. See the divine spark in every person and respond with love rather than judgment.",
                "source": "Spiritual Guidance",
                "spiritual_theme": "Relationships",
                "dharmic_context": "Divine recognition",
                "keywords": ["relationships", "compassion", "understanding", "divine spark", "love"]
            },
            {
                "text": "When facing difficult decisions, quiet your mind through meditation, seek wisdom from sacred texts, and listen to your inner voice of dharma.",
                "source": "Spiritual Guidance",
                "spiritual_theme": "Decision Making",
                "dharmic_context": "Inner wisdom",
                "keywords": ["decisions", "meditation", "wisdom", "inner voice", "dharma"]
            },
            {
                "text": "Begin each day with gratitude, dedicate your work as service to the Divine, and end with reflection on how you can better serve others.",
                "source": "Spiritual Guidance",
                "spiritual_theme": "Daily Practice",
                "dharmic_context": "Devotional living",
                "keywords": ["gratitude", "service", "devotion", "reflection", "daily practice"]
            }
        ]
        
        entries = []
        for i, text_data in enumerate(practical_texts):
            entry = SacredTextEntry(
                id=self.generate_text_id("Spiritual Guidance", str(i+1)),
                text=text_data["text"],
                source=text_data["source"],
                spiritual_theme=text_data["spiritual_theme"],
                dharmic_context=text_data["dharmic_context"],
                keywords=text_data["keywords"],
                language="English"
            )
            entries.append(entry)
        
        logger.info(f"Loaded {len(entries)} practical guidance texts")
        return entries
    
    def load_all_sacred_texts(self) -> List[SacredTextEntry]:
        """Load all sacred text content."""
        logger.info("Loading all sacred text content...")
        
        all_texts = []
        all_texts.extend(self.load_bhagavad_gita_texts())
        all_texts.extend(self.load_upanishad_texts())
        all_texts.extend(self.load_practical_guidance_texts())
        
        self.sacred_texts = all_texts
        logger.info(f"Total loaded texts: {len(all_texts)}")
        return all_texts
    
    def save_to_json(self, filename: str = "sacred_texts_data.json") -> str:
        """Save loaded texts to JSON file."""
        data = {
            "metadata": {
                "total_texts": len(self.sacred_texts),
                "created_at": "2025-07-02T00:00:00Z",
                "version": "1.0",
                "description": "Sacred text content for Vimarsh spiritual guidance system"
            },
            "texts": [text.to_dict() for text in self.sacred_texts]
        }
        
        filepath = Path(__file__).parent / "data" / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Sacred texts saved to: {filepath}")
        return str(filepath)

async def main():
    """Main function to load and save sacred text data."""
    loader = SacredTextDataLoader()
    texts = loader.load_all_sacred_texts()
    filepath = loader.save_to_json()
    
    print(f"✅ Loaded {len(texts)} sacred text entries")
    print(f"📄 Data saved to: {filepath}")
    print("🕉️ Ready for vector database population")

if __name__ == "__main__":
    asyncio.run(main())
