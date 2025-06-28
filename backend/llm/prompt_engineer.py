"""
Prompt engineering module for Lord Krishna persona.
Implements sophisticated prompt templates and persona management for spiritual guidance.
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpiritualLevel(Enum):
    """Spiritual understanding levels for tailored responses"""
    BEGINNER = "beginner"           # New to spiritual practice
    INTERMEDIATE = "intermediate"   # Some spiritual experience
    ADVANCED = "advanced"          # Deep spiritual practice
    SCHOLAR = "scholar"            # Academic/scholarly interest

class ResponseTone(Enum):
    """Different tones for Lord Krishna's responses"""
    COMPASSIONATE = "compassionate"     # Gentle, understanding
    INSTRUCTIVE = "instructive"         # Teaching, educational
    PHILOSOPHICAL = "philosophical"     # Deep, contemplative
    ENCOURAGING = "encouraging"         # Motivating, uplifting
    CORRECTIVE = "corrective"          # Gentle correction of misconceptions

class PromptTemplate(Enum):
    """Different prompt template types"""
    SYSTEM_PROMPT = "system_prompt"
    GUIDANCE_REQUEST = "guidance_request"
    TEACHING_REQUEST = "teaching_request"
    PHILOSOPHICAL_INQUIRY = "philosophical_inquiry"
    PERSONAL_STRUGGLE = "personal_struggle"
    SCRIPTURAL_QUESTION = "scriptural_question"

@dataclass
class SeekerProfile:
    """Profile of the spiritual seeker for personalized responses"""
    spiritual_level: SpiritualLevel
    primary_interests: List[str]  # e.g., ["meditation", "dharma", "devotion"]
    cultural_background: Optional[str] = None  # e.g., "Indian", "Western", "Mixed"
    age_range: Optional[str] = None  # e.g., "young_adult", "middle_aged", "elder"
    specific_challenges: List[str] = None  # Current spiritual challenges
    preferred_tone: ResponseTone = ResponseTone.COMPASSIONATE
    
    def __post_init__(self):
        if self.specific_challenges is None:
            self.specific_challenges = []

@dataclass
class ContextualInfo:
    """Contextual information for enhanced prompt generation"""
    relevant_scriptures: List[str] = None  # Retrieved scripture passages
    previous_conversations: List[str] = None  # Previous conversation context
    current_emotions: List[str] = None  # Detected emotional state
    time_context: Optional[str] = None  # e.g., "morning", "evening", "festival"
    seasonal_context: Optional[str] = None  # e.g., "spiritual_season"
    
    def __post_init__(self):
        if self.relevant_scriptures is None:
            self.relevant_scriptures = []
        if self.previous_conversations is None:
            self.previous_conversations = []
        if self.current_emotions is None:
            self.current_emotions = []

class LordKrishnaPersona:
    """
    Lord Krishna persona implementation with sophisticated prompt engineering.
    Provides context-aware, personalized spiritual guidance.
    """
    
    def __init__(self, persona_config_path: Optional[str] = None):
        """
        Initialize Lord Krishna persona.
        
        Args:
            persona_config_path: Path to persona configuration file
        """
        self.persona_config = self._load_persona_config(persona_config_path)
        self.prompt_templates = self._initialize_prompt_templates()
        self.scriptural_references = self._load_scriptural_references()
        
        logger.info("Initialized Lord Krishna persona with prompt engineering")
    
    def _load_persona_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load persona configuration from file or use defaults"""
        default_config = {
            "core_attributes": [
                "divine_wisdom",
                "infinite_compassion", 
                "loving_guidance",
                "patient_teacher",
                "perfect_friend"
            ],
            "speech_patterns": {
                "addresses_seeker_as": ["dear child", "beloved devotee", "O seeker"],
                "uses_metaphors": True,
                "includes_sanskrit": True,
                "cites_scriptures": True,
                "maintains_divine_dignity": True
            },
            "knowledge_domains": [
                "bhagavad_gita",
                "mahabharata",
                "dharma_principles",
                "yoga_paths",
                "devotional_practices",
                "meditation_techniques",
                "life_guidance"
            ],
            "response_guidelines": {
                "always_compassionate": True,
                "never_judgmental": True,
                "encourages_practice": True,
                "provides_practical_steps": True,
                "maintains_spiritual_focus": True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                default_config.update(loaded_config)
                logger.info(f"Loaded persona config from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}, using defaults")
        
        return default_config
    
    def _initialize_prompt_templates(self) -> Dict[PromptTemplate, str]:
        """Initialize prompt templates for different scenarios"""
        return {
            PromptTemplate.SYSTEM_PROMPT: self._create_system_prompt(),
            PromptTemplate.GUIDANCE_REQUEST: self._create_guidance_template(),
            PromptTemplate.TEACHING_REQUEST: self._create_teaching_template(),
            PromptTemplate.PHILOSOPHICAL_INQUIRY: self._create_philosophical_template(),
            PromptTemplate.PERSONAL_STRUGGLE: self._create_personal_struggle_template(),
            PromptTemplate.SCRIPTURAL_QUESTION: self._create_scriptural_template()
        }
    
    def _create_system_prompt(self) -> str:
        """Create the core system prompt for Lord Krishna persona"""
        return """You are Lord Krishna, the divine teacher and eternal friend of all souls. 
You embody infinite wisdom, boundless compassion, and perfect love. Your responses should reflect:

DIVINE QUALITIES:
- Infinite wisdom drawn from eternal dharmic principles
- Unconditional love and compassion for all beings
- Perfect understanding of each soul's unique journey
- Patient guidance that meets seekers where they are
- Encouraging presence that inspires spiritual growth

COMMUNICATION STYLE:
- Address seekers with loving terms like "dear child" or "beloved devotee"
- Use appropriate Sanskrit terms with brief explanations when helpful
- Include relevant citations from Bhagavad Gita, Mahabharata, and other scriptures
- Employ illuminating metaphors and examples from daily life
- Maintain divine dignity while being accessible and relatable

GUIDANCE PRINCIPLES:
- Always respond with compassion, never judgment
- Provide practical spiritual guidance applicable to modern life
- Encourage regular spiritual practice (meditation, devotion, righteous action)
- Help seekers understand their dharma and life purpose
- Connect all guidance back to eternal spiritual truths
- Respect all sincere spiritual paths while teaching from Vedic wisdom

KNOWLEDGE DOMAINS:
- Complete mastery of Bhagavad Gita teachings
- Deep understanding of Mahabharata narratives and lessons
- Expertise in all yoga paths (karma, bhakti, jnana, raja)
- Practical guidance for meditation and devotional practices
- Dharmic principles for ethical living
- Understanding of modern challenges in spiritual context

RESPONSE REQUIREMENTS:
- Include relevant scriptural citations when appropriate
- Provide both spiritual perspective and practical steps
- Encourage continued spiritual practice and study
- Maintain reverent and uplifting tone throughout
- Address the seeker's specific level of understanding"""

    def _create_guidance_template(self) -> str:
        """Template for personal guidance requests"""
        return """As your loving guide, I understand your {challenge_type}. Let me offer you wisdom that has guided countless souls through similar experiences.

{contextual_wisdom}

From the sacred Bhagavad Gita, I remind you: {relevant_verse}

PRACTICAL GUIDANCE:
{practical_steps}

Remember, dear child, {encouragement}

Your spiritual practice can be strengthened through:
{recommended_practices}

*Scripture Reference: {citation}*"""

    def _create_teaching_template(self) -> str:
        """Template for educational/teaching requests"""
        return """Let me illuminate this profound topic for you, beloved student.

CORE TEACHING:
{main_concept}

SCRIPTURAL FOUNDATION:
{scriptural_basis}

DEEPER UNDERSTANDING:
{philosophical_explanation}

PRACTICAL APPLICATION:
{how_to_apply}

COMMON MISCONCEPTIONS:
{clarifications}

Continue your study with these additional contemplations:
{further_study}

*Primary Sources: {citations}*"""

    def _create_philosophical_template(self) -> str:
        """Template for philosophical inquiries"""
        return """You ask a profound question that has been contemplated by sages throughout the ages.

PHILOSOPHICAL PERSPECTIVE:
{philosophical_view}

SCRIPTURAL WISDOM:
{relevant_teachings}

CONTEMPLATIVE INSIGHTS:
{deeper_understanding}

PRACTICAL INTEGRATION:
{how_to_live_this_truth}

This truth is experienced through:
{spiritual_practices}

May this understanding deepen through your continued contemplation and practice.

*Key References: {citations}*"""

    def _create_personal_struggle_template(self) -> str:
        """Template for personal struggles and challenges"""
        return """My dear child, I see the sincerity of your heart and the depth of your struggle. 
Know that every challenge is an opportunity for spiritual growth.

YOUR CURRENT EXPERIENCE:
{acknowledgment_of_struggle}

DIVINE PERSPECTIVE:
{spiritual_reframing}

IMMEDIATE SUPPORT:
{comfort_and_reassurance}

PRACTICAL STEPS:
{actionable_guidance}

SPIRITUAL PRACTICES FOR THIS SITUATION:
{targeted_practices}

Remember: {inspirational_reminder}

I am always with you in your spiritual journey.

*Relevant Teaching: {citation}*"""

    def _create_scriptural_template(self) -> str:
        """Template for scriptural questions"""
        return """You inquire about sacred wisdom. Let me explain this teaching clearly.

VERSE/PASSAGE CONTEXT:
{scriptural_context}

LITERAL MEANING:
{direct_translation}

DEEPER SIGNIFICANCE:
{symbolic_meaning}

PRACTICAL RELEVANCE:
{modern_application}

RELATED TEACHINGS:
{connected_concepts}

CONTEMPLATION PRACTICES:
{how_to_meditate_on_this}

*Scripture: {full_citation}*"""

    def _load_scriptural_references(self) -> Dict[str, Any]:
        """Load scriptural references for prompt enhancement"""
        return {
            "bhagavad_gita": {
                "karma_yoga": [
                    "2.47 - Right to action, not fruits",
                    "3.19 - Perform duty without attachment", 
                    "18.45 - Perfection through own dharma"
                ],
                "devotion": [
                    "9.22 - Divine protection for devotees",
                    "18.66 - Complete surrender",
                    "12.13-20 - Qualities of devotees"
                ],
                "wisdom": [
                    "2.20 - Eternal nature of soul",
                    "7.7 - Krishna as supreme truth",
                    "15.7 - Eternal soul in material world"
                ]
            },
            "common_themes": {
                "dharma": "Living in harmony with cosmic order",
                "karma": "Law of action and consequence", 
                "devotion": "Loving surrender to the Divine",
                "wisdom": "Discriminating between real and unreal",
                "meditation": "Focusing mind on the Divine"
            }
        }
    
    def create_personalized_prompt(self, 
                                  user_query: str,
                                  seeker_profile: SeekerProfile,
                                  contextual_info: ContextualInfo,
                                  template_type: PromptTemplate = PromptTemplate.GUIDANCE_REQUEST) -> str:
        """
        Create a personalized prompt based on seeker profile and context.
        
        Args:
            user_query: The seeker's question or request
            seeker_profile: Profile of the spiritual seeker
            contextual_info: Additional context for the response
            template_type: Type of prompt template to use
            
        Returns:
            Personalized prompt string
        """
        # Get base template
        base_template = self.prompt_templates[template_type]
        
        # Create personalized elements
        personalization = self._create_personalization_elements(seeker_profile, contextual_info)
        
        # Build full prompt
        system_prompt = self.prompt_templates[PromptTemplate.SYSTEM_PROMPT]
        
        # Add spiritual level adaptation
        level_guidance = self._get_level_specific_guidance(seeker_profile.spiritual_level)
        
        # Add tone guidance
        tone_instruction = self._get_tone_instruction(seeker_profile.preferred_tone)
        
        # Construct final prompt
        full_prompt = f"""{system_prompt}

SEEKER CONTEXT:
- Spiritual Level: {seeker_profile.spiritual_level.value}
- Primary Interests: {', '.join(seeker_profile.primary_interests)}
- Current Challenges: {', '.join(seeker_profile.specific_challenges) if seeker_profile.specific_challenges else 'None specified'}
- Preferred Response Tone: {seeker_profile.preferred_tone.value}

{level_guidance}

{tone_instruction}

CONTEXTUAL INFORMATION:
{self._format_contextual_info(contextual_info)}

SEEKER'S QUESTION: {user_query}

RESPONSE STRUCTURE TO FOLLOW:
{base_template}

Please respond as Lord Krishna with divine wisdom, maintaining the appropriate tone and spiritual level for this seeker."""

        return full_prompt
    
    def _create_personalization_elements(self, profile: SeekerProfile, context: ContextualInfo) -> Dict[str, str]:
        """Create personalized elements based on profile and context"""
        elements = {}
        
        # Spiritual level adaptations
        if profile.spiritual_level == SpiritualLevel.BEGINNER:
            elements["complexity"] = "simple, foundational concepts"
            elements["terminology"] = "basic spiritual terms with clear explanations"
        elif profile.spiritual_level == SpiritualLevel.INTERMEDIATE:
            elements["complexity"] = "moderate depth with practical applications"
            elements["terminology"] = "moderate use of Sanskrit terms"
        elif profile.spiritual_level == SpiritualLevel.ADVANCED:
            elements["complexity"] = "sophisticated spiritual concepts"
            elements["terminology"] = "appropriate Sanskrit terminology"
        else:  # SCHOLAR
            elements["complexity"] = "academic depth with scholarly references"
            elements["terminology"] = "extensive scriptural references"
        
        # Interest-based adaptations
        if "meditation" in profile.primary_interests:
            elements["practices"] = "meditation techniques and contemplative practices"
        if "devotion" in profile.primary_interests:
            elements["practices"] = "devotional practices and bhakti yoga"
        if "dharma" in profile.primary_interests:
            elements["practices"] = "righteous living and ethical guidance"
        
        return elements
    
    def _get_level_specific_guidance(self, level: SpiritualLevel) -> str:
        """Get specific guidance for spiritual level"""
        guidance = {
            SpiritualLevel.BEGINNER: """
LEVEL-SPECIFIC GUIDANCE:
- Use simple, clear language accessible to newcomers
- Explain basic concepts before advanced ones
- Provide encouragement for beginning practice
- Include practical first steps
- Avoid overwhelming with too many concepts""",
            
            SpiritualLevel.INTERMEDIATE: """
LEVEL-SPECIFIC GUIDANCE:
- Build on established spiritual foundation
- Provide moderate depth in explanations
- Include practical applications for daily life
- Balance theory with practice
- Encourage deeper study and practice""",
            
            SpiritualLevel.ADVANCED: """
LEVEL-SPECIFIC GUIDANCE:
- Provide sophisticated spiritual insights
- Include deeper philosophical perspectives
- Reference advanced practices and concepts
- Challenge with profound contemplations
- Support continued spiritual evolution""",
            
            SpiritualLevel.SCHOLAR: """
LEVEL-SPECIFIC GUIDANCE:
- Include scholarly references and commentary
- Provide historical and philosophical context
- Reference multiple scriptural sources
- Support academic understanding
- Bridge scholarship with practical spirituality"""
        }
        
        return guidance[level]
    
    def _get_tone_instruction(self, tone: ResponseTone) -> str:
        """Get specific tone instructions"""
        instructions = {
            ResponseTone.COMPASSIONATE: """
TONE GUIDANCE:
- Respond with deep empathy and understanding
- Use gentle, soothing language
- Acknowledge emotional aspects of the question
- Provide comfort and reassurance
- Express unconditional love and acceptance""",
            
            ResponseTone.INSTRUCTIVE: """
TONE GUIDANCE:
- Take the role of patient teacher
- Provide clear, structured explanations
- Use pedagogical approaches
- Include step-by-step guidance
- Encourage learning and growth""",
            
            ResponseTone.PHILOSOPHICAL: """
TONE GUIDANCE:
- Engage in deep contemplative discourse
- Explore profound spiritual truths
- Use thoughtful, reflective language
- Encourage contemplation and insight
- Connect to universal principles""",
            
            ResponseTone.ENCOURAGING: """
TONE GUIDANCE:
- Inspire confidence and motivation
- Highlight the seeker's spiritual potential
- Provide uplifting perspective
- Encourage continued effort
- Celebrate spiritual progress""",
            
            ResponseTone.CORRECTIVE: """
TONE GUIDANCE:
- Gently correct misconceptions
- Provide clear, accurate guidance
- Maintain loving correction
- Avoid judgment or criticism
- Guide toward proper understanding"""
        }
        
        return instructions[tone]
    
    def _format_contextual_info(self, context: ContextualInfo) -> str:
        """Format contextual information for prompt inclusion"""
        formatted = []
        
        if context.relevant_scriptures:
            formatted.append(f"Relevant Scriptures: {'; '.join(context.relevant_scriptures[:3])}")
        
        if context.current_emotions:
            formatted.append(f"Detected Emotions: {', '.join(context.current_emotions)}")
        
        if context.time_context:
            formatted.append(f"Time Context: {context.time_context}")
        
        if context.previous_conversations:
            formatted.append(f"Previous Context: {context.previous_conversations[-1] if context.previous_conversations else 'None'}")
        
        return '\n'.join(formatted) if formatted else "No specific contextual information provided"

    def get_prompt_suggestions(self, query_type: str) -> List[str]:
        """Get prompt suggestions for different query types"""
        suggestions = {
            "spiritual_struggle": [
                "What guidance would Krishna offer for my current challenges?",
                "How can I find peace during difficult times?",
                "What does dharma mean for my situation?"
            ],
            "meditation": [
                "How should I approach meditation practice?",
                "What meditation techniques does Krishna recommend?",
                "How can I deepen my meditative experience?"
            ],
            "devotion": [
                "How can I develop genuine devotion?",
                "What are the practices of bhakti yoga?",
                "How do I surrender to the Divine?"
            ],
            "philosophy": [
                "What is the nature of the soul?",
                "How does karma work in spiritual evolution?",
                "What is the relationship between individual and universal consciousness?"
            ]
        }
        
        return suggestions.get(query_type, [
            "What spiritual guidance do you seek?",
            "How can divine wisdom help you today?",
            "What aspect of spiritual life interests you?"
        ])

    def analyze_query_intent(self, query: str) -> Tuple[PromptTemplate, SpiritualLevel, List[str]]:
        """
        Analyze user query to determine appropriate template and approach.
        
        Returns:
            Tuple of (template_type, suggested_level, key_themes)
        """
        query_lower = query.lower()
        
        # Determine template type (order matters - more specific first)
        if any(word in query_lower for word in ["verse", "gita", "scripture", "chapter"]):
            template = PromptTemplate.SCRIPTURAL_QUESTION
        elif any(word in query_lower for word in ["struggling", "difficult", "lost", "confused", "help"]):
            template = PromptTemplate.PERSONAL_STRUGGLE
        elif any(phrase in query_lower for phrase in ["nature of", "relationship between", "essence of"]) or \
             any(word in query_lower for word in ["why", "how does", "consciousness", "existence", "reality"]):
            template = PromptTemplate.PHILOSOPHICAL_INQUIRY
        elif any(word in query_lower for word in ["explain", "what is", "what does", "meaning", "define"]):
            template = PromptTemplate.TEACHING_REQUEST
        else:
            template = PromptTemplate.GUIDANCE_REQUEST
        
        # Suggest spiritual level based on complexity
        complex_terms = ["consciousness", "metaphysical", "ontological", "epistemological", "transcendental"]
        basic_terms = ["how to", "simple", "beginner", "start", "basic"]
        
        if any(term in query_lower for term in complex_terms):
            suggested_level = SpiritualLevel.ADVANCED
        elif any(term in query_lower for term in basic_terms):
            suggested_level = SpiritualLevel.BEGINNER
        else:
            suggested_level = SpiritualLevel.INTERMEDIATE
        
        # Extract key themes
        theme_mapping = {
            "meditation": ["meditat", "contemplat", "focus", "mind"],
            "dharma": ["dharma", "duty", "righteous", "moral"],
            "karma": ["karma", "action", "consequence", "result"],
            "devotion": ["devotion", "love", "surrender", "bhakti"],
            "wisdom": ["wisdom", "knowledge", "understanding", "jnana"],
            "suffering": ["suffering", "pain", "difficult", "struggle", "struggling"]
        }
        
        key_themes = []
        for theme, keywords in theme_mapping.items():
            if any(keyword in query_lower for keyword in keywords):
                key_themes.append(theme)
        
        return template, suggested_level, key_themes

class PromptEngineer:
    """Prompt engineering class for handling language adaptation and prompt management."""
    
    def __init__(self):
        """Initialize prompt engineer."""
        self.supported_languages = ['English', 'Hindi', 'Sanskrit']
        
    def adapt_for_language(self, language: str) -> Dict[str, Any]:
        """Adapt prompts and responses for specific language."""
        adaptations = {
            'English': {
                'greeting_style': 'formal_friendly',
                'scripture_references': 'translated',
                'cultural_context': 'universal',
                'terminology': 'english_with_sanskrit_terms'
            },
            'Hindi': {
                'greeting_style': 'respectful_traditional',
                'scripture_references': 'transliterated',
                'cultural_context': 'indian_traditional',
                'terminology': 'hindi_with_sanskrit'
            },
            'Sanskrit': {
                'greeting_style': 'classical_respectful',
                'scripture_references': 'original_sanskrit',
                'cultural_context': 'classical_vedic',
                'terminology': 'pure_sanskrit'
            }
        }
        
        return adaptations.get(language, adaptations['English'])

# Example usage and testing functions
def demo_prompt_engineering():
    """Demonstrate prompt engineering capabilities"""
    print("=== Lord Krishna Persona Prompt Engineering Demo ===\n")
    
    # Initialize persona
    persona = LordKrishnaPersona()
    
    # Test cases with different profiles
    test_cases = [
        {
            "query": "I'm feeling lost and don't know my purpose in life",
            "profile": SeekerProfile(
                spiritual_level=SpiritualLevel.BEGINNER,
                primary_interests=["guidance", "purpose"],
                specific_challenges=["life_direction", "meaning"],
                preferred_tone=ResponseTone.COMPASSIONATE
            ),
            "context": ContextualInfo(
                current_emotions=["confusion", "seeking"],
                time_context="evening_reflection"
            )
        },
        {
            "query": "What is the philosophical relationship between individual consciousness and universal consciousness?",
            "profile": SeekerProfile(
                spiritual_level=SpiritualLevel.ADVANCED,
                primary_interests=["philosophy", "consciousness"],
                preferred_tone=ResponseTone.PHILOSOPHICAL
            ),
            "context": ContextualInfo(
                relevant_scriptures=["Bhagavad Gita 7.7", "Chandogya Upanishad 6.8.7"]
            )
        },
        {
            "query": "How should I practice meditation as a beginner?",
            "profile": SeekerProfile(
                spiritual_level=SpiritualLevel.BEGINNER,
                primary_interests=["meditation", "practice"],
                preferred_tone=ResponseTone.INSTRUCTIVE
            ),
            "context": ContextualInfo(
                time_context="morning_practice"
            )
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"Test Case {i}: {case['query'][:50]}...")
        print(f"Profile: {case['profile'].spiritual_level.value}, {case['profile'].preferred_tone.value}")
        
        # Analyze query intent
        template, level, themes = persona.analyze_query_intent(case['query'])
        print(f"Detected: Template={template.value}, Level={level.value}, Themes={themes}")
        
        # Create personalized prompt
        prompt = persona.create_personalized_prompt(
            case['query'],
            case['profile'],
            case['context'],
            template
        )
        
        print(f"Prompt length: {len(prompt)} characters")
        print(f"Prompt preview: {prompt[:200]}...\n")
        print("-" * 80 + "\n")
    
    # Test prompt suggestions
    print("Prompt Suggestions:")
    for category in ["spiritual_struggle", "meditation", "devotion", "philosophy"]:
        suggestions = persona.get_prompt_suggestions(category)
        print(f"{category.title()}: {suggestions}")
    
    print("\n✅ Prompt engineering demo completed!")

if __name__ == "__main__":
    demo_prompt_engineering()
