"""
Vimarsh Feedback Collection Module
Comprehensive user feedback collection, analysis, and continuous improvement system
"""

from .vimarsh_feedback_collector import (
    VimarshFeedbackCollector,
    FeedbackType,
    FeedbackSentiment,
    FeedbackPriority,
    UserFeedback,
    FeedbackAnalytics,
    ContinuousImprovementMetrics,
    collect_user_feedback,
    generate_weekly_feedback_report
)

__version__ = "1.0.0"
__author__ = "Vimarsh Development Team"

__all__ = [
    "VimarshFeedbackCollector",
    "FeedbackType",
    "FeedbackSentiment", 
    "FeedbackPriority",
    "UserFeedback",
    "FeedbackAnalytics",
    "ContinuousImprovementMetrics",
    "collect_user_feedback",
    "generate_weekly_feedback_report"
]
