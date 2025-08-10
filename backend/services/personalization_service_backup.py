#!/usr/bin/env python3
"""
Progressive Personalization Service - Adaptive User Experience
============================================================

Phase 2 feature implementation for progressive personalization with adaptive
UI adjustments and personality recommendations based on user interactions.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
from enum import Enum

from models.conversation_models import UserPreferences, create_user_preferences

logger = logging.getLogger(__name__)

class PersonalizationLevel(Enum):
    """Levels of personalization depth."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class AdaptationContext(Enum):
    """Context types for UI adaptation."""
    THEME_PREFERENCE = "theme_preference"
    INTERACTION_STYLE = "interaction_style"
    COMPLEXITY_LEVEL = "complexity_level"
    PERSONALITY_MATCH = "personality_match"
    RESPONSE_LENGTH = "response_length"

class ProgressivePersonalizationService:
    """Service for managing progressive personalization and adaptive UI."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # In-memory storage for MVP implementation
        self._user_profiles: Dict[str, UserPreferences] = {}
        self._interaction_history: Dict[str, List[Dict[str, Any]]] = {}
        self._adaptation_settings: Dict[str, Dict[str, Any]] = {}
        
    async def initialize_user_personalization(
        self,
        user_id: str,
        initial_preferences: Optional[Dict[str, Any]] = None
    ) -> UserPreferences:
        """Initialize personalization profile for a new user."""
        
        try:
            # Create initial personality profile
            profile = create_user_preferences(user_id=user_id)
            
            # Update with initial preferences if provided
            if initial_preferences:
                if "interests" in initial_preferences:
                    # Map interests to preferred personalities
                    interest_personality_map = {
                        "meditation": "krishna",
                        "dharma": "rama", 
                        "strength": "hanuman",
                        "knowledge": "saraswati"
                    }
                    for interest in initial_preferences["interests"]:
                        personality = interest_personality_map.get(interest, "krishna")
                        if personality not in profile.preferred_personalities:
                            profile.preferred_personalities.append(personality)
                
                if "communication" in initial_preferences:
                    comm_prefs = initial_preferences["communication"]
                    if "style" in comm_prefs:
                        profile.conversation_style = comm_prefs["style"]
            
            # Set default adaptation settings
            self._adaptation_settings[user_id] = {
                "personalization_level": PersonalizationLevel.BASIC.value,
                "theme_preference": "auto",
                "response_length": "medium",
                "complexity_level": "balanced",
                "enable_proactive_suggestions": True,
                "auto_personality_switching": False
            }
            
            # Initialize interaction history
            self._interaction_history[user_id] = []
            
            # Store profile
            self._user_profiles[user_id] = profile
            
            self.logger.info(f"✅ Initialized personalization for user {user_id}")
            return profile
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize personalization: {e}")
            raise
    
    async def track_user_interaction(
        self,
        user_id: str,
        interaction_type: str,
        context: Dict[str, Any],
        personality_id: Optional[str] = None,
        satisfaction_score: Optional[float] = None
    ) -> None:
        """Track user interaction for personalization learning."""
        
        try:
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "type": interaction_type,
                "context": context,
                "personality_id": personality_id,
                "satisfaction_score": satisfaction_score,
                "session_data": {
                    "response_time": context.get("response_time"),
                    "engagement_level": context.get("engagement_level"),
                    "user_feedback": context.get("feedback")
                }
            }
            
            if user_id not in self._interaction_history:
                self._interaction_history[user_id] = []
            
            self._interaction_history[user_id].append(interaction)
            
            # Trigger adaptation analysis if we have enough data
            if len(self._interaction_history[user_id]) % 10 == 0:
                await self._analyze_and_adapt(user_id)
            
            self.logger.info(f"📊 Tracked interaction for user {user_id}: {interaction_type}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to track interaction: {e}")
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        context: str = "general",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations based on user profile and history."""
        
        try:
            profile = self._user_profiles.get(user_id)
            if not profile:
                return []
            
            interactions = self._interaction_history.get(user_id, [])
            adaptation_settings = self._adaptation_settings.get(user_id, {})
            
            recommendations = []
            
            # Personality-based recommendations
            personality_recs = await self._get_personality_recommendations(
                profile, interactions, context
            )
            recommendations.extend(personality_recs)
            
            # Content complexity recommendations
            complexity_recs = await self._get_complexity_recommendations(
                interactions, adaptation_settings.get("complexity_level", "balanced")
            )
            recommendations.extend(complexity_recs)
            
            # Spiritual journey recommendations
            spiritual_recs = await self._get_spiritual_journey_recommendations(
                profile, interactions
            )
            recommendations.extend(spiritual_recs)
            
            # Interaction style recommendations
            interaction_recs = await self._get_interaction_style_recommendations(
                profile, interactions
            )
            recommendations.extend(interaction_recs)
            
            # Sort by relevance score and limit
            recommendations.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            result = recommendations[:limit]
            
            self.logger.info(f"🎯 Generated {len(result)} personalized recommendations for user {user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate recommendations: {e}")
            return []
    
    async def get_adaptive_ui_settings(self, user_id: str) -> Dict[str, Any]:
        """Get adaptive UI settings based on user behavior patterns."""
        
        try:
            interactions = self._interaction_history.get(user_id, [])
            current_settings = self._adaptation_settings.get(user_id, {})
            
            if not interactions:
                return self._get_default_ui_settings()
            
            # Analyze recent interactions for UI preferences
            recent_interactions = interactions[-20:]  # Last 20 interactions
            
            ui_settings = {
                "theme": await self._determine_theme_preference(recent_interactions),
                "layout_density": await self._determine_layout_density(recent_interactions),
                "navigation_style": await self._determine_navigation_style(recent_interactions),
                "content_presentation": await self._determine_content_presentation(recent_interactions),
                "interaction_hints": await self._determine_interaction_hints(recent_interactions),
                "personalization_level": current_settings.get("personalization_level", "basic")
            }
            
            self.logger.info(f"🎨 Generated adaptive UI settings for user {user_id}")
            return ui_settings
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get adaptive UI settings: {e}")
            return self._get_default_ui_settings()
    
    async def suggest_personality_switch(
        self,
        user_id: str,
        current_context: str,
        user_mood: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Suggest personality switch based on context and user patterns."""
        
        try:
            profile = self._user_profiles.get(user_id)
            interactions = self._interaction_history.get(user_id, [])
            
            if not profile or not interactions:
                return None
            
            # Analyze recent interaction patterns
            recent_interactions = interactions[-10:]
            current_personality_performance = await self._analyze_personality_performance(
                recent_interactions
            )
            
            # Consider context and mood
            context_personality_map = {
                "stress": ["hanuman", "krishna"],
                "learning": ["saraswati", "krishna"],
                "decision_making": ["krishna", "rama"],
                "emotional_support": ["krishna", "rama"],
                "motivation": ["hanuman", "arjuna"],
                "spiritual_practice": ["krishna", "shiva"]
            }
            
            suggested_personalities = context_personality_map.get(current_context, ["krishna"])
            
            # Filter based on user's preferred personalities
            preferred = set(profile.preferred_personalities)
            filtered_suggestions = [p for p in suggested_personalities if p in preferred]
            
            if not filtered_suggestions:
                filtered_suggestions = suggested_personalities
            
            # Choose best personality based on performance and context
            best_personality = filtered_suggestions[0]
            confidence_score = await self._calculate_personality_confidence(
                best_personality, current_context, recent_interactions
            )
            
            if confidence_score > 0.7:  # High confidence threshold
                suggestion = {
                    "suggested_personality": best_personality,
                    "confidence_score": confidence_score,
                    "reason": f"Based on {current_context} context and your interaction patterns",
                    "context": current_context,
                    "user_mood": user_mood,
                    "expected_benefits": await self._get_personality_benefits(best_personality, current_context)
                }
                
                self.logger.info(f"🎭 Suggested personality switch for user {user_id}: {best_personality}")
                return suggestion
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to suggest personality switch: {e}")
            return None
    
    async def update_personalization_level(
        self,
        user_id: str,
        new_level: PersonalizationLevel
    ) -> bool:
        """Update user's personalization level."""
        
        try:
            if user_id not in self._adaptation_settings:
                self._adaptation_settings[user_id] = {}
            
            self._adaptation_settings[user_id]["personalization_level"] = new_level.value
            
            # Trigger re-analysis for new level
            await self._analyze_and_adapt(user_id)
            
            self.logger.info(f"🔧 Updated personalization level for user {user_id}: {new_level.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update personalization level: {e}")
            return False
    
    async def get_personalization_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user's personalization patterns."""
        
        try:
            profile = self._user_profiles.get(user_id)
            interactions = self._interaction_history.get(user_id, [])
            settings = self._adaptation_settings.get(user_id, {})
            
            if not interactions:
                return {"error": "No interaction data available"}
            
            # Calculate insights
            total_interactions = len(interactions)
            recent_interactions = interactions[-30:]  # Last 30 interactions
            
            personality_usage = {}
            interaction_types = {}
            satisfaction_scores = []
            
            for interaction in interactions:
                # Personality usage
                personality = interaction.get("personality_id", "unknown")
                personality_usage[personality] = personality_usage.get(personality, 0) + 1
                
                # Interaction types
                int_type = interaction.get("type", "unknown")
                interaction_types[int_type] = interaction_types.get(int_type, 0) + 1
                
                # Satisfaction scores
                if interaction.get("satisfaction_score"):
                    satisfaction_scores.append(interaction["satisfaction_score"])
            
            # Calculate trends
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
            most_used_personality = max(personality_usage.items(), key=lambda x: x[1])[0] if personality_usage else None
            
            insights = {
                "total_interactions": total_interactions,
                "recent_activity": len(recent_interactions),
                "most_used_personality": most_used_personality,
                "personality_distribution": personality_usage,
                "interaction_type_distribution": interaction_types,
                "average_satisfaction": round(avg_satisfaction, 2),
                "personalization_level": settings.get("personalization_level", "basic"),
                "adaptation_trends": await self._calculate_adaptation_trends(interactions),
                "engagement_patterns": await self._analyze_engagement_patterns(interactions)
            }
            
            self.logger.info(f"📈 Generated personalization insights for user {user_id}")
            return insights
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate insights: {e}")
            return {"error": str(e)}
    
    # Helper methods
    async def _analyze_and_adapt(self, user_id: str) -> None:
        """Analyze user patterns and update adaptations."""
        try:
            interactions = self._interaction_history.get(user_id, [])
            if len(interactions) < 5:  # Need minimum data
                return
            
            # Update adaptation settings based on patterns
            recent_interactions = interactions[-20:]
            
            # Analyze response length preferences
            avg_response_length = await self._analyze_response_length_preference(recent_interactions)
            
            # Analyze complexity preferences
            complexity_preference = await self._analyze_complexity_preference(recent_interactions)
            
            # Update settings
            if user_id not in self._adaptation_settings:
                self._adaptation_settings[user_id] = {}
            
            self._adaptation_settings[user_id].update({
                "preferred_response_length": avg_response_length,
                "preferred_complexity": complexity_preference,
                "last_adaptation": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to analyze and adapt: {e}")
    
    async def _get_personality_recommendations(
        self, profile: UserPreferences, interactions: List[Dict[str, Any]], context: str
    ) -> List[Dict[str, Any]]:
        """Get personality-based recommendations."""
        recommendations = []
        
        # Recommend based on successful personality interactions
        personality_scores = {}
        for interaction in interactions[-20:]:  # Recent interactions
            personality = interaction.get("personality_id")
            satisfaction = interaction.get("satisfaction_score", 0)
            if personality and satisfaction:
                personality_scores[personality] = personality_scores.get(personality, [])
                personality_scores[personality].append(satisfaction)
        
        # Calculate average scores
        for personality, scores in personality_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score > 0.7:  # High satisfaction
                recommendations.append({
                    "type": "personality",
                    "suggestion": f"Continue conversations with {personality.title()}",
                    "relevance_score": avg_score,
                    "reason": f"You've had positive interactions with {personality.title()}"
                })
        
        return recommendations[:2]  # Limit to top 2
    
    async def _get_complexity_recommendations(
        self, interactions: List[Dict[str, Any]], current_level: str
    ) -> List[Dict[str, Any]]:
        """Get content complexity recommendations."""
        recommendations = []
        
        # Analyze engagement with different complexity levels
        complexity_engagement = {}
        for interaction in interactions[-15:]:
            complexity = interaction.get("context", {}).get("complexity_level", "medium")
            engagement = interaction.get("context", {}).get("engagement_level", 0)
            if engagement:
                complexity_engagement[complexity] = complexity_engagement.get(complexity, [])
                complexity_engagement[complexity].append(engagement)
        
        # Find best performing complexity
        best_complexity = None
        best_score = 0
        for complexity, scores in complexity_engagement.items():
            avg_score = sum(scores) / len(scores)
            if avg_score > best_score:
                best_score = avg_score
                best_complexity = complexity
        
        if best_complexity and best_complexity != current_level and best_score > 0.6:
            recommendations.append({
                "type": "complexity",
                "suggestion": f"Try {best_complexity} complexity responses",
                "relevance_score": best_score,
                "reason": f"You showed higher engagement with {best_complexity} content"
            })
        
        return recommendations
    
    async def _get_spiritual_journey_recommendations(
        self, profile: UserPreferences, interactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get spiritual journey recommendations."""
        recommendations = []
        
        # Based on spiritual interests from preferred personalities
        interests = ["meditation", "dharma", "wisdom"]  # Default spiritual interests
        
        # Map preferred personalities to spiritual interests
        personality_interests = {
            "krishna": ["dharma", "wisdom", "meditation"],
            "rama": ["dharma", "righteousness", "leadership"],
            "hanuman": ["devotion", "strength", "service"],
            "saraswati": ["knowledge", "wisdom", "learning"]
        }
        
        # Get interests from user's preferred personalities
        user_interests = []
        for personality in profile.preferred_personalities:
            user_interests.extend(personality_interests.get(personality, []))
        
        # Use unique interests
        interests = list(set(user_interests)) if user_interests else interests
        
        spiritual_paths = {
            "meditation": "Explore deeper meditation practices with Krishna's guidance",
            "dharma": "Dive into dharmic principles with Rama's wisdom",
            "devotion": "Strengthen devotional practices with Hanuman's inspiration",
            "knowledge": "Pursue spiritual knowledge with Saraswati's blessings"
        }
        
        for interest in interests:
            if interest.lower() in spiritual_paths:
                recommendations.append({
                    "type": "spiritual_journey",
                    "suggestion": spiritual_paths[interest.lower()],
                    "relevance_score": 0.8,
                    "reason": f"Based on your interest in {interest}"
                })
        
        return recommendations[:1]  # Limit to top 1
    
    async def _get_interaction_style_recommendations(
        self, profile: UserPreferences, interactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get interaction style recommendations."""
        recommendations = []
        
        # Analyze current interaction style effectiveness
        style_performance = {}
        for interaction in interactions[-10:]:
            style = interaction.get("context", {}).get("interaction_style", "balanced")
            satisfaction = interaction.get("satisfaction_score", 0)
            if satisfaction:
                style_performance[style] = style_performance.get(style, [])
                style_performance[style].append(satisfaction)
        
        # Find best performing style
        current_style = profile.conversation_style
        for style, scores in style_performance.items():
            avg_score = sum(scores) / len(scores)
            if style != current_style and avg_score > 0.75:
                recommendations.append({
                    "type": "interaction_style",
                    "suggestion": f"Try {style} interaction style",
                    "relevance_score": avg_score,
                    "reason": f"You responded well to {style} interactions"
                })
                break
        
        return recommendations
    
    def _get_default_ui_settings(self) -> Dict[str, Any]:
        """Get default UI settings for new users."""
        return {
            "theme": "auto",
            "layout_density": "comfortable",
            "navigation_style": "standard",
            "content_presentation": "balanced",
            "interaction_hints": True,
            "personalization_level": "basic"
        }
    
    async def _determine_theme_preference(self, interactions: List[Dict]) -> str:
        """Determine user's theme preference from interactions."""
        # Simple heuristic based on interaction times
        morning_interactions = sum(1 for i in interactions if "morning" in i.get("context", {}).get("time_of_day", ""))
        evening_interactions = sum(1 for i in interactions if "evening" in i.get("context", {}).get("time_of_day", ""))
        
        if evening_interactions > morning_interactions * 1.5:
            return "dark"
        elif morning_interactions > evening_interactions * 1.5:
            return "light"
        else:
            return "auto"
    
    async def _determine_layout_density(self, interactions: List[Dict]) -> str:
        """Determine preferred layout density."""
        # Analyze interaction speed and engagement
        quick_interactions = sum(1 for i in interactions if i.get("context", {}).get("response_time", 0) < 5)
        total_interactions = len(interactions)
        
        if quick_interactions / total_interactions > 0.7:
            return "compact"  # User prefers quick interactions
        else:
            return "comfortable"
    
    async def _determine_navigation_style(self, interactions: List[Dict]) -> str:
        """Determine preferred navigation style."""
        return "standard"  # For MVP, keep it simple
    
    async def _determine_content_presentation(self, interactions: List[Dict]) -> str:
        """Determine preferred content presentation style."""
        return "balanced"  # For MVP
    
    async def _determine_interaction_hints(self, interactions: List[Dict]) -> bool:
        """Determine if user needs interaction hints."""
        # New users or those with errors might need hints
        error_interactions = sum(1 for i in interactions if i.get("context", {}).get("had_error", False))
        return len(interactions) < 10 or error_interactions > 2
    
    async def _analyze_personality_performance(self, interactions: List[Dict]) -> Dict[str, float]:
        """Analyze how well different personalities are performing."""
        performance = {}
        for interaction in interactions:
            personality = interaction.get("personality_id")
            satisfaction = interaction.get("satisfaction_score", 0)
            if personality and satisfaction:
                performance[personality] = performance.get(personality, [])
                performance[personality].append(satisfaction)
        
        # Calculate averages
        avg_performance = {}
        for personality, scores in performance.items():
            avg_performance[personality] = sum(scores) / len(scores)
        
        return avg_performance
    
    async def _calculate_personality_confidence(
        self, personality: str, context: str, interactions: List[Dict]
    ) -> float:
        """Calculate confidence score for personality suggestion."""
        # Base confidence on past performance and context match
        base_confidence = 0.5
        
        # Check past performance with this personality
        personality_scores = [
            i.get("satisfaction_score", 0) for i in interactions 
            if i.get("personality_id") == personality
        ]
        
        if personality_scores:
            avg_score = sum(personality_scores) / len(personality_scores)
            base_confidence = avg_score
        
        # Context bonus
        context_bonus = 0.1 if context in ["stress", "learning", "decision_making"] else 0
        
        return min(base_confidence + context_bonus, 1.0)
    
    async def _get_personality_benefits(self, personality: str, context: str) -> List[str]:
        """Get expected benefits of switching to a personality."""
        benefits_map = {
            "krishna": [
                "Wise guidance and balanced perspective",
                "Help with complex decisions",
                "Spiritual insights and life philosophy"
            ],
            "hanuman": [
                "Motivation and strength",
                "Overcoming obstacles",
                "Building courage and determination"
            ],
            "rama": [
                "Moral guidance and righteousness",
                "Leadership principles",
                "Balanced decision making"
            ]
        }
        
        return benefits_map.get(personality, ["Enhanced spiritual guidance"])
    
    async def _calculate_adaptation_trends(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Calculate adaptation trends over time."""
        if len(interactions) < 10:
            return {"trend": "insufficient_data"}
        
        # Simple trend analysis
        early_satisfaction = [
            i.get("satisfaction_score", 0) for i in interactions[:len(interactions)//2]
            if i.get("satisfaction_score")
        ]
        
        late_satisfaction = [
            i.get("satisfaction_score", 0) for i in interactions[len(interactions)//2:]
            if i.get("satisfaction_score")
        ]
        
        if early_satisfaction and late_satisfaction:
            early_avg = sum(early_satisfaction) / len(early_satisfaction)
            late_avg = sum(late_satisfaction) / len(late_satisfaction)
            
            if late_avg > early_avg + 0.1:
                return {"trend": "improving", "improvement": round(late_avg - early_avg, 2)}
            elif early_avg > late_avg + 0.1:
                return {"trend": "declining", "decline": round(early_avg - late_avg, 2)}
            else:
                return {"trend": "stable"}
        
        return {"trend": "unknown"}
    
    async def _analyze_engagement_patterns(self, interactions: List[Dict]) -> Dict[str, Any]:
        """Analyze user engagement patterns."""
        if not interactions:
            return {}
        
        # Time-based patterns
        time_distribution = {}
        engagement_by_time = {}
        
        for interaction in interactions:
            time_of_day = interaction.get("context", {}).get("time_of_day", "unknown")
            engagement = interaction.get("context", {}).get("engagement_level", 0)
            
            time_distribution[time_of_day] = time_distribution.get(time_of_day, 0) + 1
            
            if engagement:
                engagement_by_time[time_of_day] = engagement_by_time.get(time_of_day, [])
                engagement_by_time[time_of_day].append(engagement)
        
        # Find peak engagement time
        peak_time = None
        peak_engagement = 0
        
        for time, engagements in engagement_by_time.items():
            avg_engagement = sum(engagements) / len(engagements)
            if avg_engagement > peak_engagement:
                peak_engagement = avg_engagement
                peak_time = time
        
        return {
            "most_active_time": max(time_distribution.items(), key=lambda x: x[1])[0] if time_distribution else None,
            "peak_engagement_time": peak_time,
            "average_engagement": peak_engagement
        }
    
    async def _analyze_response_length_preference(self, interactions: List[Dict]) -> str:
        """Analyze user's preferred response length."""
        length_satisfaction = {"short": [], "medium": [], "long": []}
        
        for interaction in interactions:
            length = interaction.get("context", {}).get("response_length", "medium")
            satisfaction = interaction.get("satisfaction_score")
            if satisfaction and length in length_satisfaction:
                length_satisfaction[length].append(satisfaction)
        
        # Find best performing length
        best_length = "medium"
        best_score = 0
        
        for length, scores in length_satisfaction.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                if avg_score > best_score:
                    best_score = avg_score
                    best_length = length
        
        return best_length
    
    async def _analyze_complexity_preference(self, interactions: List[Dict]) -> str:
        """Analyze user's preferred content complexity."""
        complexity_satisfaction = {"simple": [], "balanced": [], "complex": []}
        
        for interaction in interactions:
            complexity = interaction.get("context", {}).get("complexity_level", "balanced")
            satisfaction = interaction.get("satisfaction_score")
            if satisfaction and complexity in complexity_satisfaction:
                complexity_satisfaction[complexity].append(satisfaction)
        
        # Find best performing complexity
        best_complexity = "balanced"
        best_score = 0
        
        for complexity, scores in complexity_satisfaction.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                if avg_score > best_score:
                    best_score = avg_score
                    best_complexity = complexity
        
        return best_complexity

# Singleton instance
progressive_personalization_service = ProgressivePersonalizationService()

# Test function
async def test_progressive_personalization_service():
    """Test the progressive personalization service functionality."""
    print("🧪 Testing Progressive Personalization Service...")
    
    service = progressive_personalization_service
    test_user_id = "test_user_456"
    
    try:
        # Initialize user personalization
        profile = await service.initialize_user_personalization(
            user_id=test_user_id,
            initial_preferences={
                "interests": ["meditation", "dharma"],
                "communication": {"style": "detailed", "tone": "formal"}
            }
        )
        print(f"✅ Initialized personalization profile: {profile.user_id}")
        
        # Track some interactions
        await service.track_user_interaction(
            user_id=test_user_id,
            interaction_type="question_answer",
            context={"engagement_level": 0.8, "response_time": 5, "complexity_level": "balanced"},
            personality_id="krishna",
            satisfaction_score=0.9
        )
        print("✅ Tracked user interaction")
        
        # Get recommendations
        recommendations = await service.get_personalized_recommendations(
            user_id=test_user_id,
            context="learning",
            limit=3
        )
        print(f"✅ Generated {len(recommendations)} personalized recommendations")
        
        # Get adaptive UI settings
        ui_settings = await service.get_adaptive_ui_settings(test_user_id)
        print(f"✅ Generated adaptive UI settings: {ui_settings.get('theme', 'auto')}")
        
        # Get personalization insights
        insights = await service.get_personalization_insights(test_user_id)
        print(f"✅ Generated insights: {insights.get('total_interactions', 0)} interactions")
        
        print("🎉 Progressive Personalization Service test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_progressive_personalization_service())
