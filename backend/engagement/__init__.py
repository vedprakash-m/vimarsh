"""
Engagement module for Vimarsh
Provides streak tracking, achievement system, and gamification features.
"""

from .engagement_service import EngagementService, get_engagement_service
from .achievement_definitions import ACHIEVEMENT_DEFINITIONS, get_achievement_by_id
from .achievement_service import AchievementService, get_achievement_service

__all__ = [
    "EngagementService",
    "get_engagement_service",
    "ACHIEVEMENT_DEFINITIONS",
    "get_achievement_by_id",
    "AchievementService",
    "get_achievement_service"
]
