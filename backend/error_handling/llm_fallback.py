"""
Fallback Response System for LLM Failures in Vimarsh AI Agent

This module provides comprehensive fallback mechanisms when the primary LLM
(Gemini Pro) fails, ensuring users always receive meaningful spiritual guidance
even during service disruptions.
"""

import asyncio
import json
import logging
import random
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
import re

try:
    from .error_classifier import ErrorCategory, ErrorSeverity
    from .graceful_degradation import GracefulDegradationManager
except ImportError:
    from error_classifier import ErrorCategory, ErrorSeverity
    from graceful_degradation import GracefulDegradationManager


class FallbackStrategy(Enum):
    """Types of fallback strategies for LLM failures"""
    CACHED_RESPONSES = "cached_responses"
    TEMPLATE_RESPONSES = "template_responses"
    SIMPLIFIED_REASONING = "simplified_reasoning"
    EXTERNAL_LLM = "external_llm"
    HUMAN_ESCALATION = "human_escalation"
    EDUCATIONAL_CONTENT = "educational_content"
    MEDITATION_GUIDANCE = "meditation_guidance"


class FallbackTrigger(Enum):
    """Conditions that trigger fallback responses"""
    LLM_TIMEOUT = "llm_timeout"
    LLM_ERROR = "llm_error"
    RATE_LIMIT = "rate_limit"
    INVALID_RESPONSE = "invalid_response"
    SAFETY_VIOLATION = "safety_violation"
    NETWORK_ERROR = "network_error"
    SERVICE_UNAVAILABLE = "service_unavailable"


@dataclass
class SpiritualQuery:
    """Represents a user's spiritual query"""
    text: str
    language: str = "en"
    context: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FallbackResponse:
    """Represents a fallback response to a spiritual query"""
    content: str
    strategy: FallbackStrategy
    confidence: float  # 0.0 to 1.0
    citations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    fallback_reason: str = ""
    escalation_required: bool = False


@dataclass
class TemplatePattern:
    """Template pattern for generating fallback responses"""
    pattern_id: str
    triggers: List[str]  # Keywords or patterns that trigger this template
    template: str
    confidence: float
    citations: List[str] = field(default_factory=list)
    language: str = "en"
    category: str = "general"


class LLMFallbackSystem:
    """
    Comprehensive fallback system for LLM failures in spiritual guidance
    """
    
    def __init__(self, 
                 templates_path: Optional[str] = None,
                 cache_path: Optional[str] = None,
                 enable_external_llm: bool = False):
        """
        Initialize the LLM fallback system
        
        Args:
            templates_path: Path to template files
            cache_path: Path to cached responses
            enable_external_llm: Whether to use external LLM as fallback
        """
        self.templates_path = Path(templates_path) if templates_path else Path("fallback_templates")
        self.cache_path = Path(cache_path) if cache_path else Path("response_cache")
        self.enable_external_llm = enable_external_llm
        
        self.templates_path.mkdir(exist_ok=True)
        self.cache_path.mkdir(exist_ok=True)
        
        # Core components
        self.degradation = GracefulDegradationManager()
        self.logger = logging.getLogger(__name__)
        
        # Fallback data structures
        self.template_patterns: Dict[str, TemplatePattern] = {}
        self.cached_responses: Dict[str, Dict] = {}
        self.spiritual_content: Dict[str, List[str]] = {}
        
        # Statistics and monitoring
        self.fallback_stats: Dict[str, int] = {}
        self.last_cache_update = datetime.now()
        
        # Initialize fallback content
        self._initialize_templates()
        self._initialize_spiritual_content()
        self._load_cached_responses()
    
    async def get_fallback_response(self,
                                  query: SpiritualQuery,
                                  failure_reason: FallbackTrigger,
                                  original_error: Optional[Exception] = None) -> FallbackResponse:
        """
        Get fallback response for a failed LLM request
        
        Args:
            query: The original spiritual query
            failure_reason: Why the primary LLM failed
            original_error: The original error (if any)
            
        Returns:
            FallbackResponse: Appropriate fallback response
        """
        try:
            self.logger.info(f"Generating fallback response for trigger: {failure_reason.value}")
            
            # Update statistics
            self._update_fallback_stats(failure_reason)
            
            # Try multiple fallback strategies in order of preference
            strategies = self._determine_fallback_strategies(failure_reason, query)
            
            for strategy in strategies:
                try:
                    response = await self._execute_fallback_strategy(strategy, query, failure_reason)
                    if response and response.confidence > 0.3:  # Minimum confidence threshold
                        response.fallback_reason = f"LLM failure: {failure_reason.value}"
                        return response
                except Exception as e:
                    self.logger.warning(f"Fallback strategy {strategy.value} failed: {e}")
                    continue
            
            # Last resort: generic spiritual guidance
            return await self._generate_generic_response(query, failure_reason)
            
        except Exception as e:
            self.logger.error(f"Critical failure in fallback system: {e}")
            return self._emergency_response(query)
    
    def _determine_fallback_strategies(self, 
                                     failure_reason: FallbackTrigger,
                                     query: SpiritualQuery) -> List[FallbackStrategy]:
        """Determine appropriate fallback strategies based on failure type"""
        
        # Strategy preferences based on failure type
        strategy_map = {
            FallbackTrigger.LLM_TIMEOUT: [
                FallbackStrategy.CACHED_RESPONSES,
                FallbackStrategy.TEMPLATE_RESPONSES,
                FallbackStrategy.SIMPLIFIED_REASONING,
                FallbackStrategy.EDUCATIONAL_CONTENT
            ],
            FallbackTrigger.LLM_ERROR: [
                FallbackStrategy.CACHED_RESPONSES,
                FallbackStrategy.EXTERNAL_LLM,
                FallbackStrategy.TEMPLATE_RESPONSES,
                FallbackStrategy.EDUCATIONAL_CONTENT
            ],
            FallbackTrigger.RATE_LIMIT: [
                FallbackStrategy.CACHED_RESPONSES,
                FallbackStrategy.EXTERNAL_LLM,
                FallbackStrategy.TEMPLATE_RESPONSES,
                FallbackStrategy.SIMPLIFIED_REASONING
            ],
            FallbackTrigger.INVALID_RESPONSE: [
                FallbackStrategy.TEMPLATE_RESPONSES,
                FallbackStrategy.CACHED_RESPONSES,
                FallbackStrategy.SIMPLIFIED_REASONING,
                FallbackStrategy.EDUCATIONAL_CONTENT
            ],
            FallbackTrigger.SAFETY_VIOLATION: [
                FallbackStrategy.TEMPLATE_RESPONSES,
                FallbackStrategy.EDUCATIONAL_CONTENT,
                FallbackStrategy.MEDITATION_GUIDANCE,
                FallbackStrategy.HUMAN_ESCALATION
            ],
            FallbackTrigger.NETWORK_ERROR: [
                FallbackStrategy.CACHED_RESPONSES,
                FallbackStrategy.TEMPLATE_RESPONSES,
                FallbackStrategy.EDUCATIONAL_CONTENT,
                FallbackStrategy.MEDITATION_GUIDANCE
            ],
            FallbackTrigger.SERVICE_UNAVAILABLE: [
                FallbackStrategy.CACHED_RESPONSES,
                FallbackStrategy.EXTERNAL_LLM,
                FallbackStrategy.TEMPLATE_RESPONSES,
                FallbackStrategy.SIMPLIFIED_REASONING
            ]
        }
        
        base_strategies = strategy_map.get(failure_reason, [
            FallbackStrategy.TEMPLATE_RESPONSES,
            FallbackStrategy.EDUCATIONAL_CONTENT,
            FallbackStrategy.MEDITATION_GUIDANCE
        ])
        
        # Filter based on availability and configuration
        available_strategies = []
        for strategy in base_strategies:
            if self._is_strategy_available(strategy):
                available_strategies.append(strategy)
        
        return available_strategies
    
    def _is_strategy_available(self, strategy: FallbackStrategy) -> bool:
        """Check if a fallback strategy is available"""
        
        availability_checks = {
            FallbackStrategy.CACHED_RESPONSES: lambda: len(self.cached_responses) > 0,
            FallbackStrategy.TEMPLATE_RESPONSES: lambda: len(self.template_patterns) > 0,
            FallbackStrategy.SIMPLIFIED_REASONING: lambda: True,  # Always available
            FallbackStrategy.EXTERNAL_LLM: lambda: self.enable_external_llm,
            FallbackStrategy.HUMAN_ESCALATION: lambda: True,  # Always available
            FallbackStrategy.EDUCATIONAL_CONTENT: lambda: len(self.spiritual_content) > 0,
            FallbackStrategy.MEDITATION_GUIDANCE: lambda: True,  # Always available
        }
        
        check_func = availability_checks.get(strategy)
        if check_func:
            try:
                return check_func()
            except Exception:
                return False
        return False
    
    async def _execute_fallback_strategy(self,
                                       strategy: FallbackStrategy,
                                       query: SpiritualQuery,
                                       failure_reason: FallbackTrigger) -> Optional[FallbackResponse]:
        """Execute a specific fallback strategy"""
        
        strategy_handlers = {
            FallbackStrategy.CACHED_RESPONSES: self._handle_cached_responses,
            FallbackStrategy.TEMPLATE_RESPONSES: self._handle_template_responses,
            FallbackStrategy.SIMPLIFIED_REASONING: self._handle_simplified_reasoning,
            FallbackStrategy.EXTERNAL_LLM: self._handle_external_llm,
            FallbackStrategy.HUMAN_ESCALATION: self._handle_human_escalation,
            FallbackStrategy.EDUCATIONAL_CONTENT: self._handle_educational_content,
            FallbackStrategy.MEDITATION_GUIDANCE: self._handle_meditation_guidance,
        }
        
        handler = strategy_handlers.get(strategy)
        if handler:
            return await handler(query, failure_reason)
        
        return None
    
    async def _handle_cached_responses(self,
                                     query: SpiritualQuery,
                                     failure_reason: FallbackTrigger) -> Optional[FallbackResponse]:
        """Handle fallback using cached responses"""
        try:
            # Generate cache key based on query
            cache_key = self._generate_cache_key(query.text, query.language)
            
            # Check for exact match
            if cache_key in self.cached_responses:
                cached = self.cached_responses[cache_key]
                return FallbackResponse(
                    content=cached['content'],
                    strategy=FallbackStrategy.CACHED_RESPONSES,
                    confidence=cached.get('confidence', 0.8),
                    citations=cached.get('citations', []),
                    metadata={'cache_hit': 'exact', 'cached_at': cached.get('timestamp')}
                )
            
            # Look for similar queries
            similar_response = self._find_similar_cached_response(query.text)
            if similar_response:
                return FallbackResponse(
                    content=similar_response['content'],
                    strategy=FallbackStrategy.CACHED_RESPONSES,
                    confidence=similar_response.get('confidence', 0.6) * 0.8,  # Reduce confidence for similarity
                    citations=similar_response.get('citations', []),
                    metadata={'cache_hit': 'similar', 'similarity_score': similar_response.get('similarity', 0.7)}
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Cache fallback failed: {e}")
            return None
    
    async def _handle_template_responses(self,
                                       query: SpiritualQuery,
                                       failure_reason: FallbackTrigger) -> Optional[FallbackResponse]:
        """Handle fallback using template responses"""
        try:
            # Find matching template patterns
            matching_patterns = self._find_matching_templates(query.text, query.language)
            
            if not matching_patterns:
                return None
            
            # Select best matching pattern
            best_pattern = max(matching_patterns, key=lambda p: p.confidence)
            
            # Generate response from template
            response_content = self._generate_from_template(best_pattern, query)
            
            return FallbackResponse(
                content=response_content,
                strategy=FallbackStrategy.TEMPLATE_RESPONSES,
                confidence=best_pattern.confidence,
                citations=best_pattern.citations,
                metadata={
                    'template_id': best_pattern.pattern_id,
                    'template_category': best_pattern.category
                }
            )
            
        except Exception as e:
            self.logger.error(f"Template fallback failed: {e}")
            return None
    
    async def _handle_simplified_reasoning(self,
                                         query: SpiritualQuery,
                                         failure_reason: FallbackTrigger) -> Optional[FallbackResponse]:
        """Handle fallback using simplified reasoning"""
        try:
            # Analyze query for key spiritual concepts
            spiritual_concepts = self._extract_spiritual_concepts(query.text)
            
            if not spiritual_concepts:
                return None
            
            # Generate simplified response based on concepts
            response_content = self._generate_simplified_response(spiritual_concepts, query.language)
            
            return FallbackResponse(
                content=response_content,
                strategy=FallbackStrategy.SIMPLIFIED_REASONING,
                confidence=0.6,
                citations=self._get_general_citations(),
                metadata={
                    'concepts_identified': spiritual_concepts,
                    'reasoning_method': 'concept_based'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Simplified reasoning fallback failed: {e}")
            return None
    
    async def _handle_external_llm(self,
                                 query: SpiritualQuery,
                                 failure_reason: FallbackTrigger) -> Optional[FallbackResponse]:
        """Handle fallback using external LLM service"""
        try:
            if not self.enable_external_llm:
                return None
            
            # This would integrate with a secondary LLM service
            # For now, we'll simulate with a placeholder
            self.logger.info("External LLM fallback would be called here")
            
            # In real implementation, this would call OpenAI, Claude, etc.
            # For demonstration, return a mock response
            return FallbackResponse(
                content="I apologize for the temporary service disruption. While I work to restore full functionality, please know that Krishna's wisdom teaches us patience in times of difficulty. 'For the soul there is neither birth nor death. It is not slain when the body is slain.' - Bhagavad Gita 2.20",
                strategy=FallbackStrategy.EXTERNAL_LLM,
                confidence=0.7,
                citations=["Bhagavad Gita 2.20"],
                metadata={'external_service': 'backup_llm', 'simulated': True}
            )
            
        except Exception as e:
            self.logger.error(f"External LLM fallback failed: {e}")
            return None
    
    async def _handle_human_escalation(self,
                                     query: SpiritualQuery,
                                     failure_reason: FallbackTrigger) -> Optional[FallbackResponse]:
        """Handle fallback by escalating to human experts"""
        try:
            # Create escalation ticket
            escalation_id = await self._create_escalation_ticket(query, failure_reason)
            
            escalation_message = self._get_escalation_message(query.language)
            
            return FallbackResponse(
                content=escalation_message,
                strategy=FallbackStrategy.HUMAN_ESCALATION,
                confidence=0.9,  # High confidence in human expertise
                citations=[],
                metadata={
                    'escalation_id': escalation_id,
                    'escalation_type': 'llm_failure',
                    'estimated_response_time': '24-48 hours'
                },
                escalation_required=True
            )
            
        except Exception as e:
            self.logger.error(f"Human escalation fallback failed: {e}")
            return None
    
    async def _handle_educational_content(self,
                                        query: SpiritualQuery,
                                        failure_reason: FallbackTrigger) -> Optional[FallbackResponse]:
        """Handle fallback using educational spiritual content"""
        try:
            # Select appropriate educational content
            content_category = self._categorize_spiritual_query(query.text)
            educational_content = self._get_educational_content(content_category, query.language)
            
            if not educational_content:
                return None
            
            return FallbackResponse(
                content=educational_content['content'],
                strategy=FallbackStrategy.EDUCATIONAL_CONTENT,
                confidence=0.7,
                citations=educational_content.get('citations', []),
                metadata={
                    'content_category': content_category,
                    'educational_type': educational_content.get('type', 'general')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Educational content fallback failed: {e}")
            return None
    
    async def _handle_meditation_guidance(self,
                                        query: SpiritualQuery,
                                        failure_reason: FallbackTrigger) -> Optional[FallbackResponse]:
        """Handle fallback using meditation and mindfulness guidance"""
        try:
            # Generate appropriate meditation guidance
            guidance_type = self._determine_meditation_type(query.text)
            meditation_content = self._generate_meditation_guidance(guidance_type, query.language)
            
            return FallbackResponse(
                content=meditation_content,
                strategy=FallbackStrategy.MEDITATION_GUIDANCE,
                confidence=0.8,
                citations=self._get_meditation_citations(),
                metadata={
                    'guidance_type': guidance_type,
                    'practice_duration': '5-10 minutes'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Meditation guidance fallback failed: {e}")
            return None
    
    def _initialize_templates(self):
        """Initialize template patterns for fallback responses"""
        
        # General spiritual guidance templates
        self.template_patterns.update({
            "general_guidance": TemplatePattern(
                pattern_id="general_guidance",
                triggers=["guidance", "help", "advice", "what should", "how to"],
                template="In times of uncertainty, Krishna's wisdom reminds us to {action}. As stated in the Bhagavad Gita, '{quote}'. Trust in the divine plan and continue on your spiritual path with devotion and patience.",
                confidence=0.7,
                citations=["Bhagavad Gita"],
                category="guidance"
            ),
            
            "dharma_questions": TemplatePattern(
                pattern_id="dharma_questions",
                triggers=["dharma", "duty", "righteous", "moral", "ethical"],
                template="Your question about dharma is profound. Krishna teaches that our highest duty is to act according to our nature while offering all actions to the Divine. '{quote}' Consider your situation with a pure heart and act according to divine will.",
                confidence=0.8,
                citations=["Bhagavad Gita"],
                category="dharma"
            ),
            
            "suffering_comfort": TemplatePattern(
                pattern_id="suffering_comfort",
                triggers=["pain", "suffering", "sad", "difficult", "hard", "struggle"],
                template="I understand you are experiencing difficulty. Krishna's teachings offer comfort: '{quote}'. Remember that all experiences, both joyful and challenging, are opportunities for spiritual growth. This too shall pass.",
                confidence=0.8,
                citations=["Bhagavad Gita"],
                category="comfort"
            ),
            
            "devotion_practice": TemplatePattern(
                pattern_id="devotion_practice",
                triggers=["devotion", "bhakti", "worship", "prayer", "spiritual practice"],
                template="Your desire to deepen your devotional practice is commendable. Krishna says: '{quote}'. Begin with simple, sincere practices - chanting His names, reading sacred texts, and offering your daily actions to Him.",
                confidence=0.8,
                citations=["Bhagavad Gita"],
                category="practice"
            )
        })
    
    def _initialize_spiritual_content(self):
        """Initialize spiritual educational content"""
        
        self.spiritual_content = {
            "wisdom": [
                "The soul is neither born, and nor does it die; nor having been, does it ever cease to be. The soul is without birth, eternal, immortal, and ageless. It is not destroyed when the body is destroyed.",
                "You have the right to perform your actions, but you are not entitled to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.",
                "The mind is restless, turbulent, obstinate and very strong, O Krishna, and to subdue it, I think, is more difficult than controlling the wind."
            ],
            "dharma": [
                "Better is one's own dharma, though imperfectly performed, than the dharma of another well performed. Destruction in one's own dharma is better, for the dharma of another is fraught with danger.",
                "Dharma exists for the welfare of all beings. Hence, any act that harms any being is not dharmic.",
                "The true dharma is that which leads to the welfare of all living beings."
            ],
            "comfort": [
                "For the soul there is neither birth nor death. It is not slain when the body is slain.",
                "That which is real never ceases to be; that which is unreal never comes into being.",
                "As a person puts on new garments, giving up old ones, the soul similarly accepts new material bodies, giving up the old and useless ones."
            ],
            "practice": [
                "Whatever you do, whatever you eat, whatever you offer in sacrifice, whatever you give away, whatever penances you practice—do that as an offering to God.",
                "Engage your mind always in thinking of Me, become My devotee, offer obeisances to Me and worship Me. Being completely absorbed in Me, surely you will come to Me.",
                "Those who worship Me with devotion, they are in Me and I am in them."
            ]
        }
    
    def _load_cached_responses(self):
        """Load cached responses from storage"""
        try:
            cache_file = self.cache_path / "responses.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.cached_responses = json.load(f)
                self.logger.info(f"Loaded {len(self.cached_responses)} cached responses")
            else:
                self.logger.info("No cached responses found, starting with empty cache")
        except Exception as e:
            self.logger.error(f"Failed to load cached responses: {e}")
            self.cached_responses = {}
    
    async def cache_successful_response(self,
                                      query: str,
                                      response: str,
                                      language: str = "en",
                                      confidence: float = 0.9,
                                      citations: List[str] = None):
        """Cache a successful response for future fallback use"""
        try:
            cache_key = self._generate_cache_key(query, language)
            
            cache_entry = {
                'content': response,
                'confidence': confidence,
                'citations': citations or [],
                'timestamp': datetime.now().isoformat(),
                'language': language,
                'usage_count': 0
            }
            
            self.cached_responses[cache_key] = cache_entry
            
            # Periodically save to disk
            if len(self.cached_responses) % 10 == 0:
                await self._save_cache()
                
        except Exception as e:
            self.logger.error(f"Failed to cache response: {e}")
    
    async def _save_cache(self):
        """Save cached responses to disk"""
        try:
            cache_file = self.cache_path / "responses.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cached_responses, f, indent=2, ensure_ascii=False)
            self.last_cache_update = datetime.now()
            self.logger.info(f"Saved {len(self.cached_responses)} cached responses")
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")
    
    def _generate_cache_key(self, query: str, language: str) -> str:
        """Generate a cache key for a query"""
        # Normalize query for consistent caching
        normalized = re.sub(r'\s+', ' ', query.lower().strip())
        # Simple hash for now - in production, use more sophisticated similarity
        return f"{language}:{hash(normalized)}"
    
    def _find_similar_cached_response(self, query: str) -> Optional[Dict]:
        """Find cached response similar to the given query"""
        # Simple similarity check based on common words
        query_words = set(query.lower().split())
        
        best_match = None
        best_similarity = 0.0
        
        for cache_key, cached in self.cached_responses.items():
            # Extract original query words from cache metadata if available
            if 'original_query' in cached:
                cached_words = set(cached['original_query'].lower().split())
            else:
                # Fallback: use first part of cache key
                cached_words = set(cache_key.split(':')[1].split())
            
            # Calculate simple word overlap similarity
            if len(query_words) > 0 and len(cached_words) > 0:
                intersection = query_words.intersection(cached_words)
                similarity = len(intersection) / len(query_words.union(cached_words))
                
                if similarity > best_similarity and similarity > 0.3:  # Minimum similarity threshold
                    best_similarity = similarity
                    best_match = cached.copy()
                    best_match['similarity'] = similarity
        
        return best_match
    
    def _find_matching_templates(self, query: str, language: str) -> List[TemplatePattern]:
        """Find template patterns that match the query"""
        matching_patterns = []
        query_lower = query.lower()
        
        for pattern in self.template_patterns.values():
            if pattern.language != language:
                continue
                
            # Check if any trigger words/phrases match
            for trigger in pattern.triggers:
                if trigger.lower() in query_lower:
                    matching_patterns.append(pattern)
                    break
        
        return matching_patterns
    
    def _generate_from_template(self, pattern: TemplatePattern, query: SpiritualQuery) -> str:
        """Generate response content from a template pattern"""
        # Get appropriate quote and action based on pattern category
        quotes_by_category = {
            "guidance": "You have the right to perform your actions, but you are not entitled to the fruits of action.",
            "dharma": "Better is one's own dharma, though imperfectly performed, than the dharma of another well performed.",
            "comfort": "For the soul there is neither birth nor death. It is not slain when the body is slain.",
            "practice": "Whatever you do, whatever you eat, whatever you offer in sacrifice, whatever you give away, whatever penances you practice—do that as an offering to God."
        }
        
        actions_by_category = {
            "guidance": "seek wisdom through self-reflection and spiritual practice",
            "dharma": "follow your righteous path with dedication and devotion",
            "comfort": "find peace in the eternal nature of the soul",
            "practice": "cultivate devotion through daily spiritual practices"
        }
        
        quote = quotes_by_category.get(pattern.category, "Surrender all actions to Me and take refuge in Me alone.")
        action = actions_by_category.get(pattern.category, "trust in divine guidance")
        
        # Replace template variables
        content = pattern.template.format(
            quote=quote,
            action=action,
            query=query.text[:100]  # Truncated query reference
        )
        
        return content
    
    def _extract_spiritual_concepts(self, query: str) -> List[str]:
        """Extract spiritual concepts from a query"""
        spiritual_keywords = {
            "soul": ["soul", "atman", "spirit", "eternal"],
            "dharma": ["dharma", "duty", "righteous", "moral", "ethical"],
            "karma": ["karma", "action", "deed", "consequence"],
            "devotion": ["devotion", "bhakti", "love", "worship", "prayer"],
            "wisdom": ["wisdom", "knowledge", "understanding", "truth"],
            "meditation": ["meditation", "dhyana", "mindfulness", "concentration"],
            "suffering": ["suffering", "pain", "sorrow", "difficulty"],
            "moksha": ["liberation", "moksha", "freedom", "enlightenment"]
        }
        
        identified_concepts = []
        query_lower = query.lower()
        
        for concept, keywords in spiritual_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    identified_concepts.append(concept)
                    break
        
        return identified_concepts
    
    def _generate_simplified_response(self, concepts: List[str], language: str) -> str:
        """Generate simplified response based on identified spiritual concepts"""
        if not concepts:
            return "While I cannot provide a complete response at this moment, I encourage you to continue your spiritual journey with faith and devotion. Krishna's wisdom is always available to guide us."
        
        primary_concept = concepts[0]
        
        concept_responses = {
            "soul": "The nature of the soul is eternal and unchanging. Krishna teaches that we are not this temporary body, but the eternal soul within. Focus on your spiritual growth and connection with the Divine.",
            
            "dharma": "Your question touches on dharma - righteous living. Krishna's guidance is to perform your duty with devotion, without attachment to results. Follow your righteous path with sincere dedication.",
            
            "karma": "Krishna teaches about karma - the law of action and reaction. Perform your actions as service to the Divine, without attachment to outcomes. This purifies the heart and brings peace.",
            
            "devotion": "Devotion to Krishna is the most direct path to spiritual fulfillment. Begin with simple practices: chanting His names, reading sacred texts, and offering your actions to Him with love.",
            
            "wisdom": "True wisdom comes through spiritual practice and divine grace. Study the sacred texts, practice meditation, and seek the guidance of realized souls on your spiritual journey.",
            
            "meditation": "Meditation helps quiet the mind and connect with your inner divine nature. Start with simple breath awareness and gradually deepen your practice with devotion to Krishna.",
            
            "suffering": "Suffering is a teacher that draws us closer to the Divine. Remember that you are the eternal soul, beyond temporary difficulties. Take refuge in Krishna's love and guidance.",
            
            "moksha": "Liberation is the ultimate goal of spiritual life. Through devotion, righteous action, and wisdom, we can transcend the cycle of birth and death and return to our eternal home with Krishna."
        }
        
        return concept_responses.get(primary_concept, 
            "Your spiritual inquiry is valuable. Continue seeking with a sincere heart, and Krishna's wisdom will illuminate your path.")
    
    def _categorize_spiritual_query(self, query: str) -> str:
        """Categorize the spiritual query for appropriate educational content"""
        query_lower = query.lower()
        
        category_keywords = {
            "wisdom": ["wisdom", "knowledge", "understanding", "truth", "meaning"],
            "dharma": ["dharma", "duty", "righteous", "right", "wrong", "moral"],
            "comfort": ["suffering", "pain", "difficult", "sad", "loss", "grief"],
            "practice": ["practice", "meditation", "prayer", "devotion", "spiritual"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return "wisdom"  # Default category
    
    def _get_educational_content(self, category: str, language: str) -> Optional[Dict]:
        """Get educational content for a specific category"""
        if category not in self.spiritual_content:
            category = "wisdom"
        
        content_list = self.spiritual_content[category]
        if not content_list:
            return None
        
        # Select random content from category
        selected_content = random.choice(content_list)
        
        return {
            'content': f"Here is some wisdom from the sacred texts to guide you:\n\n\"{selected_content}\"\n\nMay this bring you peace and understanding on your spiritual journey.",
            'citations': ["Bhagavad Gita", "Sacred Hindu Texts"],
            'type': category
        }
    
    def _determine_meditation_type(self, query: str) -> str:
        """Determine appropriate type of meditation guidance"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["anxiety", "stress", "worry", "fear"]):
            return "calming"
        elif any(word in query_lower for word in ["focus", "concentration", "attention"]):
            return "concentration"
        elif any(word in query_lower for word in ["love", "devotion", "heart", "krishna"]):
            return "devotional"
        else:
            return "general"
    
    def _generate_meditation_guidance(self, guidance_type: str, language: str) -> str:
        """Generate meditation guidance based on type"""
        
        guidance_templates = {
            "calming": """Let us find peace together through this simple meditation:

1. Find a quiet place and sit comfortably
2. Close your eyes and take three deep breaths
3. Gently repeat: "Om Shanti Shanti Shanti" (Peace Peace Peace)
4. Allow Krishna's love to surround you with tranquility
5. Rest in this peaceful awareness for a few minutes

Remember: "You have the right to perform your actions, but you are not entitled to the fruits of action." Release your worries to the Divine.""",

            "concentration": """Here is a concentration practice to strengthen your focus:

1. Sit with your spine straight and eyes closed
2. Focus on your breath entering and leaving the nostrils
3. When your mind wanders, gently return to the breath
4. You may also focus on the name "Krishna" with each breath
5. Practice for 5-10 minutes daily

Krishna teaches: "For him who has conquered the mind, the mind is the best of friends." Cultivate this friendship through patient practice.""",

            "devotional": """Let us connect with Krishna through loving meditation:

1. Sit comfortably and bring Krishna's image to your heart
2. Softly chant: "Hare Krishna, Hare Krishna, Krishna Krishna, Hare Hare"
3. Feel devotion and love flowing from your heart to Krishna
4. Offer all your thoughts and feelings to Him
5. Rest in this loving connection

"Those who worship Me with devotion, they are in Me and I am in them." Let this love transform your heart.""",

            "general": """Here is a simple meditation to begin your practice:

1. Sit quietly in a peaceful place
2. Close your eyes and breathe naturally
3. Observe your breath without changing it
4. When thoughts arise, acknowledge them and return to breathing
5. End with a prayer of gratitude to the Divine

Krishna says: "Yoga is a light, which once lit will never dim. The better your practice, the brighter your flame." Begin today with sincere effort."""
        }
        
        return guidance_templates.get(guidance_type, guidance_templates["general"])
    
    def _get_general_citations(self) -> List[str]:
        """Get general citations for simplified responses"""
        return ["Bhagavad Gita", "Sacred Hindu Texts", "Krishna's Teachings"]
    
    def _get_meditation_citations(self) -> List[str]:
        """Get citations for meditation guidance"""
        return ["Bhagavad Gita", "Meditation Practices", "Krishna's Teachings"]
    
    async def _create_escalation_ticket(self, query: SpiritualQuery, failure_reason: FallbackTrigger) -> str:
        """Create escalation ticket for human review"""
        # In production, this would integrate with a ticketing system
        ticket_id = f"ESC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash(query.text) % 10000:04d}"
        
        # Log escalation details
        escalation_data = {
            'ticket_id': ticket_id,
            'query': query.text,
            'language': query.language,
            'user_id': query.user_id,
            'failure_reason': failure_reason.value,
            'timestamp': datetime.now().isoformat(),
            'priority': 'normal'
        }
        
        self.logger.info(f"Created escalation ticket: {ticket_id}")
        
        # In production: send to human expert queue
        # await self.expert_queue.add_ticket(escalation_data)
        
        return ticket_id
    
    def _get_escalation_message(self, language: str) -> str:
        """Get appropriate escalation message for the user"""
        
        messages = {
            "en": """I apologize, but I'm experiencing technical difficulties and cannot provide you with the spiritual guidance you deserve at this moment. 

Your question has been forwarded to our team of spiritual scholars who will provide you with a thoughtful, authentic response within 24-48 hours.

In the meantime, I encourage you to:
• Spend time in quiet reflection or meditation
• Read from the Bhagavad Gita or other sacred texts
• Trust that Krishna's guidance will come to you in the perfect time

Thank you for your patience and understanding. 🙏""",
            
            "hi": """मुझे खुशी है कि आपने मुझसे पूछा, लेकिन इस समय मैं तकनीकी कठिनाइयों का सामना कर रहा हूं और आपको उचित आध्यात्मिक मार्गदर्शन नहीं दे सकता।

आपका प्रश्न हमारे आध्यात्मिक विद्वानों की टीम को भेजा गया है जो 24-48 घंटों में आपको एक विचारशील, प्रामाणिक उत्तर देंगे।

इस बीच, मैं आपको प्रोत्साहित करता हूं:
• शांत चिंतन या ध्यान में समय बिताएं
• भगवद गीता या अन्य पवित्र ग्रंथों को पढ़ें
• विश्वास रखें कि कृष्ण का मार्गदर्शन सही समय पर आपके पास आएगा

आपके धैर्य और समझ के लिए धन्यवाद। 🙏"""
        }
        
        return messages.get(language, messages["en"])
    
    async def _generate_generic_response(self, 
                                       query: SpiritualQuery,
                                       failure_reason: FallbackTrigger) -> FallbackResponse:
        """Generate generic response when all other strategies fail"""
        
        generic_messages = {
            "en": """I apologize for the temporary difficulty in providing specific guidance. While my systems recover, please remember these eternal truths from Krishna's teachings:

"You have the right to perform your actions, but you are not entitled to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty."

Continue your spiritual journey with faith and devotion. The Divine is always with you, guiding you through every challenge and blessing.

🙏 Om Shanti Shanti Shanti""",
            
            "hi": """विशिष्ट मार्गदर्शन प्रदान करने में अस्थायी कठिनाई के लिए मैं क्षमा चाहता हूं। जब तक मेरे सिस्टम ठीक हो रहे हैं, कृपया कृष्ण की शिक्षाओं से इन शाश्वत सत्यों को याद रखें:

"तुम्हारा अधिकार केवल कर्म करने में है, फल में कभी नहीं। इसलिए तुम कर्मों के फल के हेतु मत बनो और न ही तुम्हारी अकर्म में आसक्ति हो।"

श्रद्धा और भक्ति के साथ अपनी आध्यात्मिक यात्रा जारी रखें। परमात्मा हमेशा आपके साथ है, हर चुनौती और आशीर्वाद के माध्यम से आपका मार्गदर्शन करता है।

🙏 ॐ शांति शांति शांति"""
        }
        
        message = generic_messages.get(query.language, generic_messages["en"])
        
        return FallbackResponse(
            content=message,
            strategy=FallbackStrategy.TEMPLATE_RESPONSES,
            confidence=0.5,
            citations=["Bhagavad Gita 2.47"],
            metadata={'response_type': 'generic', 'failure_reason': failure_reason.value}
        )
    
    def _emergency_response(self, query: SpiritualQuery) -> FallbackResponse:
        """Emergency response when everything else fails"""
        
        emergency_message = """I sincerely apologize, but I am experiencing significant technical difficulties at this moment. 

Please know that your spiritual inquiry is important and valued. I encourage you to:

• Take this as an opportunity for quiet reflection
• Trust that the Divine works in mysterious ways
• Consider this moment of silence as sacred space for inner listening

"Be fearless and pure; never waver in your determination or your dedication to the spiritual life." - Bhagavad Gita

🙏 May peace be with you"""
        
        return FallbackResponse(
            content=emergency_message,
            strategy=FallbackStrategy.TEMPLATE_RESPONSES,
            confidence=0.3,
            citations=["Bhagavad Gita"],
            metadata={'response_type': 'emergency'},
            escalation_required=True
        )
    
    def _update_fallback_stats(self, failure_reason: FallbackTrigger):
        """Update fallback usage statistics"""
        reason_key = failure_reason.value
        self.fallback_stats[reason_key] = self.fallback_stats.get(reason_key, 0) + 1
        
        # Log statistics periodically
        total_fallbacks = sum(self.fallback_stats.values())
        if total_fallbacks % 10 == 0:
            self.logger.info(f"Fallback stats: {self.fallback_stats}")
    
    async def get_fallback_statistics(self) -> Dict[str, Any]:
        """Get fallback system usage statistics"""
        total_fallbacks = sum(self.fallback_stats.values())
        
        return {
            'total_fallbacks': total_fallbacks,
            'fallback_reasons': dict(self.fallback_stats),
            'cached_responses': len(self.cached_responses),
            'template_patterns': len(self.template_patterns),
            'last_cache_update': self.last_cache_update.isoformat(),
            'strategies_available': {
                strategy.value: self._is_strategy_available(strategy)
                for strategy in FallbackStrategy
            }
        }
    
    async def cleanup_old_cache(self, max_age_days: int = 30):
        """Clean up old cached responses"""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            old_keys = []
            for key, cached in self.cached_responses.items():
                cached_time = datetime.fromisoformat(cached.get('timestamp', '1970-01-01'))
                if cached_time < cutoff_date:
                    old_keys.append(key)
            
            for key in old_keys:
                del self.cached_responses[key]
            
            if old_keys:
                await self._save_cache()
                self.logger.info(f"Cleaned up {len(old_keys)} old cached responses")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old cache: {e}")
