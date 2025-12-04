"""
Content Service
Generates personalized notification content including daily wisdom and contextual messages
"""

import random
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from .notification_templates import (
    NotificationType,
    WISDOM_QUOTES,
    get_random_quote
)

logger = logging.getLogger(__name__)


# Personality display names and domains
PERSONALITY_INFO: Dict[str, Dict[str, str]] = {
    "krishna": {"name": "Lord Krishna", "domain": "spiritual"},
    "buddha": {"name": "Buddha", "domain": "spiritual"},
    "jesus": {"name": "Jesus Christ", "domain": "spiritual"},
    "rumi": {"name": "Rumi", "domain": "spiritual"},
    "vivekananda": {"name": "Swami Vivekananda", "domain": "spiritual"},
    "einstein": {"name": "Albert Einstein", "domain": "scientific"},
    "newton": {"name": "Isaac Newton", "domain": "scientific"},
    "tesla": {"name": "Nikola Tesla", "domain": "scientific"},
    "archimedes": {"name": "Archimedes", "domain": "scientific"},
    "da_vinci": {"name": "Leonardo da Vinci", "domain": "scientific"},
    "lincoln": {"name": "Abraham Lincoln", "domain": "leadership"},
    "gandhi": {"name": "Mahatma Gandhi", "domain": "leadership"},
    "mlk": {"name": "Martin Luther King Jr.", "domain": "leadership"},
    "washington": {"name": "George Washington", "domain": "leadership"},
    "franklin": {"name": "Benjamin Franklin", "domain": "leadership"},
    "chanakya": {"name": "Chanakya", "domain": "leadership"},
    "marcus_aurelius": {"name": "Marcus Aurelius", "domain": "philosophical"},
    "socrates": {"name": "Socrates", "domain": "philosophical"},
    "plato": {"name": "Plato", "domain": "philosophical"},
    "aristotle": {"name": "Aristotle", "domain": "philosophical"},
    "confucius": {"name": "Confucius", "domain": "philosophical"},
    "lao_tzu": {"name": "Lao Tzu", "domain": "philosophical"},
    "shakespeare": {"name": "William Shakespeare", "domain": "literary"},
    "tagore": {"name": "Rabindranath Tagore", "domain": "literary"},
    "freud": {"name": "Sigmund Freud", "domain": "psychology"},
}


class ContentService:
    """
    Service for generating personalized notification content
    """
    
    def __init__(self):
        """Initialize the content service"""
        self.wisdom_quotes = WISDOM_QUOTES
        self.personality_info = PERSONALITY_INFO
    
    def get_daily_wisdom_content(
        self,
        user_id: str,
        preferred_personality: Optional[str] = None,
        preferred_domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate daily wisdom notification content
        
        Args:
            user_id: User identifier
            preferred_personality: User's favorite personality (optional)
            preferred_domain: User's preferred domain (optional)
            
        Returns:
            Content dict with personality_name, wisdom_quote, and url
        """
        # Select personality based on preference or random
        personality_id = self._select_personality(
            preferred_personality, 
            preferred_domain
        )
        
        personality = self.personality_info.get(personality_id, {})
        personality_name = personality.get("name", "A Wise Guide")
        
        # Get a wisdom quote
        quote = get_random_quote(personality_id)
        if not quote:
            # Fallback quotes
            quote = self._get_fallback_quote()
        
        return {
            "personality_id": personality_id,
            "personality_name": personality_name,
            "wisdom_quote": quote,
            "domain": personality.get("domain", "spiritual"),
            "url": f"/guidance?personality={personality_id}"
        }
    
    def get_streak_reminder_content(
        self,
        user_id: str,
        current_streak: int,
        preferred_personality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate streak reminder notification content
        
        Args:
            user_id: User identifier
            current_streak: Current streak count
            preferred_personality: User's favorite personality
            
        Returns:
            Content dict for streak reminder
        """
        personality_id = preferred_personality or self._get_random_personality()
        personality = self.personality_info.get(personality_id, {})
        
        return {
            "streak_count": current_streak,
            "personality_id": personality_id,
            "personality_name": personality.get("name", "A Wise Guide"),
            "url": "/guidance"
        }
    
    def get_streak_at_risk_content(
        self,
        user_id: str,
        current_streak: int,
        hours_until_reset: int
    ) -> Dict[str, Any]:
        """
        Generate streak at risk notification content
        
        Args:
            user_id: User identifier
            current_streak: Current streak count
            hours_until_reset: Hours until streak resets
            
        Returns:
            Content dict for streak at risk notification
        """
        return {
            "streak_count": current_streak,
            "hours_left": hours_until_reset,
            "url": "/guidance"
        }
    
    def get_streak_milestone_content(
        self,
        user_id: str,
        streak_count: int,
        points_earned: int
    ) -> Dict[str, Any]:
        """
        Generate streak milestone notification content
        
        Args:
            user_id: User identifier
            streak_count: Milestone streak count
            points_earned: Points earned for milestone
            
        Returns:
            Content dict for milestone notification
        """
        return {
            "streak_count": streak_count,
            "points": points_earned,
            "url": "/progress"
        }
    
    def get_achievement_content(
        self,
        user_id: str,
        achievement_id: str,
        achievement_name: str,
        achievement_description: str,
        points: int
    ) -> Dict[str, Any]:
        """
        Generate achievement unlocked notification content
        
        Args:
            user_id: User identifier
            achievement_id: Achievement ID
            achievement_name: Display name
            achievement_description: Short description
            points: Points earned
            
        Returns:
            Content dict for achievement notification
        """
        return {
            "achievement_id": achievement_id,
            "achievement_name": achievement_name,
            "achievement_description": achievement_description,
            "points": points,
            "url": "/progress"
        }
    
    def get_weekly_summary_content(
        self,
        user_id: str,
        conversations: int,
        domains_explored: int,
        streak_days: int,
        top_personality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate weekly summary notification content
        
        Args:
            user_id: User identifier
            conversations: Number of conversations this week
            domains_explored: Number of domains explored
            streak_days: Active streak days this week
            top_personality: Most used personality
            
        Returns:
            Content dict for weekly summary
        """
        return {
            "conversations": conversations,
            "domains_explored": domains_explored,
            "streak_days": streak_days,
            "top_personality": top_personality,
            "url": "/progress"
        }
    
    def get_welcome_back_content(
        self,
        user_id: str,
        days_away: int,
        preferred_personality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate welcome back notification content
        
        Args:
            user_id: User identifier
            days_away: Days since last activity
            preferred_personality: User's favorite personality
            
        Returns:
            Content dict for welcome back notification
        """
        personality_id = preferred_personality or self._get_random_personality()
        personality = self.personality_info.get(personality_id, {})
        
        return {
            "days_away": days_away,
            "personality_id": personality_id,
            "personality_name": personality.get("name", "A Wise Guide"),
            "url": f"/guidance?personality={personality_id}"
        }
    
    def _select_personality(
        self,
        preferred_personality: Optional[str],
        preferred_domain: Optional[str]
    ) -> str:
        """Select a personality based on preferences"""
        if preferred_personality and preferred_personality in self.personality_info:
            return preferred_personality
        
        if preferred_domain:
            domain_personalities = [
                pid for pid, info in self.personality_info.items()
                if info.get("domain") == preferred_domain
            ]
            if domain_personalities:
                return random.choice(domain_personalities)
        
        return self._get_random_personality()
    
    def _get_random_personality(self) -> str:
        """Get a random personality ID"""
        # Prefer personalities with wisdom quotes
        personalities_with_quotes = list(self.wisdom_quotes.keys())
        if personalities_with_quotes:
            return random.choice(personalities_with_quotes)
        return random.choice(list(self.personality_info.keys()))
    
    def _get_fallback_quote(self) -> str:
        """Get a fallback wisdom quote"""
        fallback_quotes = [
            "The journey of a thousand miles begins with a single step.",
            "Wisdom begins in wonder.",
            "The only true wisdom is in knowing you know nothing.",
            "In the midst of chaos, there is also opportunity.",
            "What lies behind us and what lies before us are tiny matters compared to what lies within us.",
        ]
        return random.choice(fallback_quotes)
