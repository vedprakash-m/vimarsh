"""
Test fixtures and mock data for Vimarsh backend testing.

Contains sample spiritual texts, mock responses, and test data
for comprehensive testing while maintaining cultural authenticity.
"""

# Sample spiritual texts for testing (keeping reverent tone)
SAMPLE_BHAGAVAD_GITA_VERSES = {
    "2.47": {
        "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
        "translation": "You have a right to perform your prescribed duty, but not to the fruits of action.",
        "source": "Bhagavad Gita 2.47",
        "context": "Lord Krishna teaching about selfless action",
        "keywords": ["duty", "karma", "selfless action", "dharma"]
    },
    "4.7": {
        "sanskrit": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत",
        "translation": "Whenever righteousness declines and unrighteousness prevails, O Bharata, at that time I manifest Myself.",
        "source": "Bhagavad Gita 4.7",
        "context": "Divine intervention and protection of dharma",
        "keywords": ["dharma", "divine intervention", "righteousness", "avatar"]
    },
    "18.66": {
        "sanskrit": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज",
        "translation": "Abandon all varieties of religion and just surrender unto Me. I shall deliver you from all sinful reactions.",
        "source": "Bhagavad Gita 18.66",
        "context": "Ultimate surrender and divine grace",
        "keywords": ["surrender", "divine grace", "liberation", "devotion"]
    }
}

SAMPLE_MAHABHARATA_EXCERPTS = {
    "udyoga_parva_29": {
        "text": "Dharma exists for the welfare of all beings. Hence, that by which the welfare of all living beings is sustained, that is dharma.",
        "source": "Mahabharata, Udyoga Parva 29",
        "context": "Definition of dharma",
        "keywords": ["dharma", "welfare", "universal good", "righteousness"]
    },
    "vana_parva_313": {
        "text": "The ultimate dharma is ahimsa (non-violence), truth, and compassion towards all living beings.",
        "source": "Mahabharata, Vana Parva 313",
        "context": "Core principles of dharma",
        "keywords": ["ahimsa", "truth", "compassion", "non-violence"]
    }
}

# Mock user queries for testing
SAMPLE_USER_QUERIES = {
    "duty_question": {
        "query": "What is my duty in life?",
        "language": "English",
        "expected_themes": ["dharma", "purpose", "righteousness"],
        "expected_sources": ["Bhagavad Gita"]
    },
    "attachment_question": {
        "query": "How do I overcome attachment to results?",
        "language": "English", 
        "expected_themes": ["karma yoga", "selfless action", "detachment"],
        "expected_sources": ["Bhagavad Gita 2.47"]
    },
    "hindi_devotion_question": {
        "query": "भक्ति का सच्चा अर्थ क्या है?",
        "language": "Hindi",
        "expected_themes": ["bhakti", "devotion", "love"],
        "expected_sources": ["Bhagavad Gita", "Srimad Bhagavatam"]
    },
    "anger_management": {
        "query": "How to control anger according to Krishna?",
        "language": "English",
        "expected_themes": ["emotional control", "peace", "wisdom"],
        "expected_sources": ["Bhagavad Gita"]
    },
    "dharma_modern": {
        "query": "What is dharma in today's world?",
        "language": "English",
        "expected_themes": ["dharma", "modern context", "righteousness", "duty"],
        "expected_sources": ["Bhagavad Gita", "Mahabharata"]
    }
}

# Mock Lord Krishna persona responses
SAMPLE_KRISHNA_RESPONSES = {
    "duty_response": {
        "response": "O beloved soul, your duty is determined by your nature and circumstances. As I taught Arjuna, one must perform their prescribed duties without attachment to results. Your dharma is unique to you, arising from your capabilities, your position in life, and the needs of the world around you.",
        "citations": ["Bhagavad Gita 2.47", "Bhagavad Gita 18.47"],
        "tone_markers": ["divine_wisdom", "compassionate_guidance", "authoritative_teaching"],
        "language": "English"
    },
    "attachment_response": {
        "response": "Dear child, attachment to results is the root of suffering. Work with full dedication, but surrender the fruits to Me. This is the path of Karma Yoga - acting in accordance with dharma while maintaining inner detachment.",
        "citations": ["Bhagavad Gita 2.47", "Bhagavad Gita 3.9"],
        "tone_markers": ["loving_guidance", "practical_wisdom", "divine_assurance"],
        "language": "English"
    },
    "dharma_modern": {
        "response": "O Arjuna, in today's world, dharma remains the eternal principle of righteous living. Your dharma encompasses both your personal duties and your responsibility to serve the greater good. Whether you are a student, professional, parent, or leader, perform your role with integrity, compassion, and dedication.",
        "citations": ["Bhagavad Gita 2.47", "Bhagavad Gita 4.7"],
        "tone_markers": ["timeless_wisdom", "practical_guidance", "divine_authority"],
        "language": "English"
    },
    "hindi_response": {
        "response": "हे अर्जुन, तुम्हारा धर्म तुम्हारे स्वभाव और परिस्थितियों से निर्धारित होता है। अपने कर्तव्य का पालन करो लेकिन फल की चिंता मत करो।",
        "citations": ["Bhagavad Gita 2.47"],
        "tone_markers": ["divine_wisdom", "compassionate_guidance"],
        "language": "Hindi"
    }
}

# Sample spiritual responses for testing
SAMPLE_SPIRITUAL_RESPONSES = {
    "purpose_response": {
        "response": "Dear devotee, your purpose in life is to realize your true divine nature and serve the Supreme with love and devotion. As I taught Arjuna, fulfill your dharmic duties while offering all actions to the Divine.",
        "citations": [
            {
                "source": "Bhagavad Gita 2.47",
                "text": "You have a right to perform your prescribed duty, but not to the fruits of action.",
                "relevance_score": 0.95
            }
        ],
        "metadata": {
            "language": "English",
            "processing_time_ms": 450,
            "model_version": "gemini-pro-v1.0",
            "confidence_score": 0.92,
            "spiritual_authenticity": "validated",
            "features_used": {
                "voice_synthesis": False,
                "personalization": True,
                "context_aware": True
            }
        }
    },
    "peace_response": {
        "response": "Beloved soul, inner peace comes through detachment from the fruits of action and surrender to the Divine will. Practice meditation, chant the holy names, and see the divine presence in all beings.",
        "citations": [
            {
                "source": "Bhagavad Gita 2.48",
                "text": "Perform your duty equipoised, O Arjuna, abandoning all attachment to success or failure.",
                "relevance_score": 0.88
            }
        ],
        "metadata": {
            "language": "English",
            "processing_time_ms": 380,
            "model_version": "gemini-pro-v1.0",
            "confidence_score": 0.89,
            "spiritual_authenticity": "validated",
            "features_used": {
                "voice_synthesis": False,
                "personalization": True,
                "context_aware": True
            }
        }
    }
}

# Error scenarios for testing error handling
ERROR_TEST_SCENARIOS = {
    "llm_timeout": {
        "error_type": "TimeoutError",
        "description": "LLM API timeout during response generation",
        "expected_fallback": "graceful_degradation"
    },
    "invalid_query": {
        "error_type": "ValidationError", 
        "description": "Query contains inappropriate content",
        "expected_fallback": "respectful_rejection"
    },
    "api_rate_limit": {
        "error_type": "RateLimitError",
        "description": "API rate limit exceeded",
        "expected_fallback": "retry_with_backoff"
    },
    "vector_search_failure": {
        "error_type": "SearchError",
        "description": "Vector database unavailable",
        "expected_fallback": "cached_response_or_graceful_degradation"
    }
}

# Voice interface test data
VOICE_TEST_DATA = {
    "sanskrit_pronunciations": {
        "dharma": {"ipa": "ˈdʱɐr.mɐ", "difficulty": "medium"},
        "karma": {"ipa": "ˈkɐr.mɐ", "difficulty": "easy"},
        "bhagavad": {"ipa": "ˈbʱɐ.ɡɐ.ʋɐd", "difficulty": "hard"},
        "krishna": {"ipa": "ˈkr̩ʂ.ɳɐ", "difficulty": "medium"}
    },
    "multilingual_test_phrases": {
        "english": ["spiritual guidance", "divine wisdom", "inner peace"],
        "hindi": ["आध्यात्मिक मार्गदर्शन", "दिव्य ज्ञान", "आंतरिक शांति"]
    }
}

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "response_time_targets": {
        "text_query": 3.0,  # seconds
        "voice_query": 5.0,  # seconds  
        "citation_extraction": 0.5,  # seconds
        "vector_search": 0.5  # seconds
    },
    "throughput_targets": {
        "concurrent_users": 10,
        "queries_per_minute": 100
    }
}

# Cultural authenticity validation data
AUTHENTICITY_MARKERS = {
    "appropriate_tone": [
        "divine", "compassionate", "wise", "loving", "peaceful",
        "authoritative", "gentle", "profound", "sacred"
    ],
    "inappropriate_tone": [
        "casual", "slang", "profane", "disrespectful", "flippant",
        "modern_colloquial", "irreverent"
    ],
    "required_elements": [
        "proper_citations", "sanskrit_accuracy", "cultural_context",
        "spiritual_depth", "practical_guidance"
    ]
}

# Consolidated spiritual texts for integration testing
SAMPLE_SPIRITUAL_TEXTS = {
    "bhagavad_gita": """Chapter 2, Verse 47: कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥

You have a right to perform your prescribed duty, but not to the fruits of action. 
Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.

Chapter 4, Verse 7: यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।
अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥

Whenever righteousness declines and unrighteousness prevails, O Bharata, 
at that time I manifest Myself.

Chapter 18, Verse 66: सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।
अहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥

Abandon all varieties of religion and just surrender unto Me. 
I shall deliver you from all sinful reactions. Do not fear.""",
    
    "upanishads": """From the Isha Upanishad: ईशावास्यमिदं सर्वं यत्किञ्च जगत्यां जगत्।
तेन त्यक्तेन भुञ्जीथा मा गृधः कस्यस्विद्धनम्॥

Everything in this universe is controlled and owned by the Lord. 
One should therefore accept only those things necessary for himself, 
which are set aside as his quota, and one should not accept other things, 
knowing well to whom they belong.

From the Katha Upanishad: उत्तिष्ठत जाग्रत प्राप्य वरान्निबोधत।
क्षुरस्य धारा निशिता दुरत्यया दुर्गं पथस्तत्कवयो वदन्ति॥

Arise! Awake! Approach the great teachers and learn! 
The wise say that the path is sharp like the edge of a razor, 
difficult to traverse.""",
}

def create_test_spiritual_content(query: str, response_type: str = "guidance") -> dict:
    """Create test spiritual content for various test scenarios."""
    return {
        "query": query,
        "response": SAMPLE_KRISHNA_RESPONSES.get("dharma_modern", {}).get("response", ""),
        "sources": ["Bhagavad Gita 2.47"],
        "type": response_type,
        "authenticity_score": 0.95
    }

def create_mock_rag_response(query: str) -> dict:
    """Create mock RAG response for testing."""
    return {
        "query": query,
        "retrieved_chunks": [
            {
                "text": SAMPLE_BHAGAVAD_GITA_VERSES["2.47"]["translation"],
                "source": "Bhagavad Gita 2.47",
                "similarity": 0.85
            }
        ],
        "response": SAMPLE_KRISHNA_RESPONSES["dharma_modern"]["response"],
        "sources": ["Bhagavad Gita 2.47"]
    }
