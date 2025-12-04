"""
Achievement Definitions for Vimarsh
Defines all unlockable achievements with criteria, points, and metadata.
"""

from typing import Dict, Any

# Achievement tiers and point multipliers
TIER_MULTIPLIERS = {
    "bronze": 1.0,
    "silver": 2.0,
    "gold": 3.0,
    "platinum": 5.0
}

# Achievement categories
CATEGORIES = {
    "streak": "Consistency Achievements",
    "exploration": "Discovery Achievements", 
    "depth": "Engagement Achievements",
    "social": "Social Achievements",
    "milestone": "Milestone Achievements"
}

ACHIEVEMENT_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    # ============================================================
    # STREAK ACHIEVEMENTS - Rewarding daily consistency
    # ============================================================
    "streak_3_days": {
        "id": "streak_3_days",
        "name": "Spark of Consistency",
        "description": "Maintained a 3-day wisdom streak",
        "icon": "🔥",
        "points": 30,
        "category": "streak",
        "tier": "bronze",
        "criteria": {"type": "streak", "threshold": 3},
        "celebration_message": "You're building a beautiful habit! Keep the flame alive."
    },
    "streak_7_days": {
        "id": "streak_7_days",
        "name": "Week of Wisdom",
        "description": "Maintained a 7-day wisdom streak",
        "icon": "🔥🔥",
        "points": 70,
        "category": "streak",
        "tier": "silver",
        "criteria": {"type": "streak", "threshold": 7},
        "celebration_message": "A full week of wisdom! You're on your way to mastery."
    },
    "streak_14_days": {
        "id": "streak_14_days",
        "name": "Fortnight of Focus",
        "description": "Maintained a 14-day wisdom streak",
        "icon": "🌟",
        "points": 140,
        "category": "streak",
        "tier": "silver",
        "criteria": {"type": "streak", "threshold": 14},
        "celebration_message": "Two weeks of dedicated practice. The sages would be proud!"
    },
    "streak_30_days": {
        "id": "streak_30_days",
        "name": "Moon Cycle Master",
        "description": "Maintained a 30-day wisdom streak",
        "icon": "🌙",
        "points": 300,
        "category": "streak",
        "tier": "gold",
        "criteria": {"type": "streak", "threshold": 30},
        "celebration_message": "A full lunar cycle of wisdom! You've proven your dedication."
    },
    "streak_60_days": {
        "id": "streak_60_days",
        "name": "Season of Seeking",
        "description": "Maintained a 60-day wisdom streak",
        "icon": "🌸",
        "points": 500,
        "category": "streak",
        "tier": "gold",
        "criteria": {"type": "streak", "threshold": 60},
        "celebration_message": "Two months of daily wisdom. You're truly committed to growth."
    },
    "streak_100_days": {
        "id": "streak_100_days",
        "name": "Centurion of Wisdom",
        "description": "Maintained a 100-day wisdom streak",
        "icon": "👑",
        "points": 1000,
        "category": "streak",
        "tier": "platinum",
        "criteria": {"type": "streak", "threshold": 100},
        "celebration_message": "100 days! You've achieved what few dare to attempt."
    },
    "streak_365_days": {
        "id": "streak_365_days",
        "name": "Year of Enlightenment",
        "description": "Maintained a 365-day wisdom streak",
        "icon": "🏆👑",
        "points": 3650,
        "category": "streak",
        "tier": "platinum",
        "criteria": {"type": "streak", "threshold": 365},
        "celebration_message": "A full year of daily wisdom! You are truly a seeker of the highest order."
    },
    
    # ============================================================
    # EXPLORATION ACHIEVEMENTS - Discovering personalities & domains
    # ============================================================
    "first_conversation": {
        "id": "first_conversation",
        "name": "Seeker Awakened",
        "description": "Started your first wisdom conversation",
        "icon": "🌱",
        "points": 10,
        "category": "exploration",
        "tier": "bronze",
        "criteria": {"type": "conversations", "threshold": 1},
        "celebration_message": "Your journey of a thousand miles begins with this single step."
    },
    "conversations_10": {
        "id": "conversations_10",
        "name": "Curious Mind",
        "description": "Had 10 wisdom conversations",
        "icon": "💭",
        "points": 50,
        "category": "exploration",
        "tier": "bronze",
        "criteria": {"type": "conversations", "threshold": 10},
        "celebration_message": "10 conversations! Your curiosity is blossoming."
    },
    "conversations_25": {
        "id": "conversations_25",
        "name": "Dedicated Seeker",
        "description": "Had 25 wisdom conversations",
        "icon": "🔍",
        "points": 100,
        "category": "exploration",
        "tier": "silver",
        "criteria": {"type": "conversations", "threshold": 25},
        "celebration_message": "25 conversations of wisdom! You're truly dedicated."
    },
    "conversations_50": {
        "id": "conversations_50",
        "name": "Wisdom Enthusiast",
        "description": "Had 50 wisdom conversations",
        "icon": "📚",
        "points": 200,
        "category": "exploration",
        "tier": "silver",
        "criteria": {"type": "conversations", "threshold": 50},
        "celebration_message": "Half a hundred conversations! Knowledge becomes you."
    },
    "conversations_100": {
        "id": "conversations_100",
        "name": "Master Conversationalist",
        "description": "Had 100 wisdom conversations",
        "icon": "🎓",
        "points": 500,
        "category": "exploration",
        "tier": "gold",
        "criteria": {"type": "conversations", "threshold": 100},
        "celebration_message": "100 conversations! You've become a true student of wisdom."
    },
    "personalities_5": {
        "id": "personalities_5",
        "name": "Explorer",
        "description": "Conversed with 5 different personalities",
        "icon": "🧭",
        "points": 50,
        "category": "exploration",
        "tier": "bronze",
        "criteria": {"type": "personalities_met", "threshold": 5},
        "celebration_message": "5 different perspectives! You value diverse wisdom."
    },
    "personalities_10": {
        "id": "personalities_10",
        "name": "Polymath Seeker",
        "description": "Conversed with 10 different personalities",
        "icon": "🌍",
        "points": 100,
        "category": "exploration",
        "tier": "silver",
        "criteria": {"type": "personalities_met", "threshold": 10},
        "celebration_message": "10 personalities! You seek wisdom from many sources."
    },
    "personalities_15": {
        "id": "personalities_15",
        "name": "Wisdom Collector",
        "description": "Conversed with 15 different personalities",
        "icon": "📖",
        "points": 200,
        "category": "exploration",
        "tier": "silver",
        "criteria": {"type": "personalities_met", "threshold": 15},
        "celebration_message": "15 personalities! Your collection of wisdom grows."
    },
    "all_personalities": {
        "id": "all_personalities",
        "name": "Complete Collection",
        "description": "Conversed with all 25 personalities",
        "icon": "🏛️",
        "points": 500,
        "category": "exploration",
        "tier": "platinum",
        "criteria": {"type": "personalities_met", "threshold": 25},
        "celebration_message": "All 25 personalities! You've explored the full pantheon of wisdom."
    },
    "domains_3": {
        "id": "domains_3",
        "name": "Multi-Dimensional",
        "description": "Explored 3 different wisdom domains",
        "icon": "🔺",
        "points": 75,
        "category": "exploration",
        "tier": "bronze",
        "criteria": {"type": "domains_explored", "threshold": 3},
        "celebration_message": "3 domains! You seek well-rounded wisdom."
    },
    "all_domains": {
        "id": "all_domains",
        "name": "Renaissance Soul",
        "description": "Explored all 6 wisdom domains",
        "icon": "🌈",
        "points": 200,
        "category": "exploration",
        "tier": "gold",
        "criteria": {"type": "domains_explored", "threshold": 6},
        "celebration_message": "All 6 domains! You're a true renaissance seeker."
    },
    
    # ============================================================
    # DEPTH ACHIEVEMENTS - Deep engagement with the platform
    # ============================================================
    "insight_saved_1": {
        "id": "insight_saved_1",
        "name": "First Gem",
        "description": "Saved your first wisdom insight",
        "icon": "💎",
        "points": 15,
        "category": "depth",
        "tier": "bronze",
        "criteria": {"type": "insights_saved", "threshold": 1},
        "celebration_message": "Your first saved gem of wisdom! May it guide you well."
    },
    "insight_collector_10": {
        "id": "insight_collector_10",
        "name": "Insight Collector",
        "description": "Saved 10 wisdom insights to your journal",
        "icon": "📿",
        "points": 50,
        "category": "depth",
        "tier": "silver",
        "criteria": {"type": "insights_saved", "threshold": 10},
        "celebration_message": "10 saved insights! Your wisdom journal grows rich."
    },
    "insight_collector_25": {
        "id": "insight_collector_25",
        "name": "Wisdom Curator",
        "description": "Saved 25 wisdom insights",
        "icon": "📜",
        "points": 100,
        "category": "depth",
        "tier": "silver",
        "criteria": {"type": "insights_saved", "threshold": 25},
        "celebration_message": "25 insights! You're building a treasury of wisdom."
    },
    "insight_collector_50": {
        "id": "insight_collector_50",
        "name": "Master Curator",
        "description": "Saved 50 wisdom insights",
        "icon": "🗃️",
        "points": 250,
        "category": "depth",
        "tier": "gold",
        "criteria": {"type": "insights_saved", "threshold": 50},
        "celebration_message": "50 insights! Your collection is truly remarkable."
    },
    "kindred_spirit": {
        "id": "kindred_spirit",
        "name": "Kindred Spirit",
        "description": "Reached Kindred Spirit relationship level with a personality",
        "icon": "💫",
        "points": 150,
        "category": "depth",
        "tier": "gold",
        "criteria": {"type": "relationship_level", "threshold": "kindred_spirit"},
        "celebration_message": "You've formed a deep bond. This personality truly knows you."
    },
    "deep_conversation": {
        "id": "deep_conversation",
        "name": "Deep Diver",
        "description": "Had a conversation with 10+ exchanges",
        "icon": "🌊",
        "points": 30,
        "category": "depth",
        "tier": "bronze",
        "criteria": {"type": "conversation_length", "threshold": 10},
        "celebration_message": "A truly deep conversation! Real wisdom comes from going deeper."
    },
    "voice_user": {
        "id": "voice_user",
        "name": "Voice Seeker",
        "description": "Used voice to have a conversation",
        "icon": "🎙️",
        "points": 25,
        "category": "depth",
        "tier": "bronze",
        "criteria": {"type": "feature_used", "feature": "voice"},
        "celebration_message": "You've discovered the power of spoken wisdom!"
    },
    
    # ============================================================
    # SOCIAL ACHIEVEMENTS - Sharing and community
    # ============================================================
    "first_share": {
        "id": "first_share",
        "name": "Wisdom Spreader",
        "description": "Shared wisdom for the first time",
        "icon": "📤",
        "points": 20,
        "category": "social",
        "tier": "bronze",
        "criteria": {"type": "shares", "threshold": 1},
        "celebration_message": "Sharing wisdom multiplies it. Thank you for spreading the light!"
    },
    "share_10": {
        "id": "share_10",
        "name": "Knowledge Ambassador",
        "description": "Shared wisdom 10 times",
        "icon": "🌟📤",
        "points": 75,
        "category": "social",
        "tier": "silver",
        "criteria": {"type": "shares", "threshold": 10},
        "celebration_message": "10 shares! You're an ambassador of wisdom."
    },
    
    # ============================================================
    # MILESTONE ACHIEVEMENTS - Special accomplishments
    # ============================================================
    "onboarding_complete": {
        "id": "onboarding_complete",
        "name": "Journey Begun",
        "description": "Completed the onboarding journey",
        "icon": "🚀",
        "points": 25,
        "category": "milestone",
        "tier": "bronze",
        "criteria": {"type": "onboarding", "threshold": "complete"},
        "celebration_message": "Welcome to Vimarsh! Your wisdom journey officially begins."
    },
    "notification_enabled": {
        "id": "notification_enabled",
        "name": "Wisdom Reminder",
        "description": "Enabled daily wisdom notifications",
        "icon": "🔔",
        "points": 15,
        "category": "milestone",
        "tier": "bronze",
        "criteria": {"type": "feature_enabled", "feature": "notifications"},
        "celebration_message": "Daily reminders set! Wisdom will find you each day."
    },
    "night_owl": {
        "id": "night_owl",
        "name": "Night Owl",
        "description": "Had a conversation after midnight",
        "icon": "🦉",
        "points": 20,
        "category": "milestone",
        "tier": "bronze",
        "criteria": {"type": "time_based", "condition": "after_midnight"},
        "celebration_message": "Seeking wisdom in the quiet hours. The night belongs to seekers."
    },
    "early_bird": {
        "id": "early_bird",
        "name": "Early Bird",
        "description": "Had a conversation before 6 AM",
        "icon": "🐦",
        "points": 20,
        "category": "milestone",
        "tier": "bronze",
        "criteria": {"type": "time_based", "condition": "before_6am"},
        "celebration_message": "The early seeker catches the wisdom! Dawn brings clarity."
    },
    "weekend_warrior": {
        "id": "weekend_warrior",
        "name": "Weekend Warrior",
        "description": "Had conversations on 4 consecutive weekends",
        "icon": "⚔️",
        "points": 50,
        "category": "milestone",
        "tier": "silver",
        "criteria": {"type": "weekend_streak", "threshold": 4},
        "celebration_message": "Weekends are for wisdom! You make the most of your free time."
    }
}

# Milestones for progress tracking
PROGRESS_MILESTONES = {
    "conversations": [1, 10, 25, 50, 100, 250, 500, 1000],
    "streak_days": [3, 7, 14, 30, 60, 100, 200, 365],
    "personalities_met": [1, 5, 10, 15, 20, 25],
    "domains_explored": [1, 3, 6],
    "insights_saved": [1, 5, 10, 25, 50, 100],
    "shares": [1, 5, 10, 25, 50]
}

def get_achievements_for_category(category: str) -> Dict[str, Dict[str, Any]]:
    """Get all achievements for a specific category"""
    return {
        aid: achievement 
        for aid, achievement in ACHIEVEMENT_DEFINITIONS.items()
        if achievement.get("category") == category
    }

def get_achievement_by_id(achievement_id: str) -> Dict[str, Any]:
    """Get a specific achievement by ID"""
    return ACHIEVEMENT_DEFINITIONS.get(achievement_id, {})

def get_next_milestone(metric: str, current_value: int) -> int:
    """Get the next milestone for a given metric"""
    milestones = PROGRESS_MILESTONES.get(metric, [])
    for milestone in milestones:
        if current_value < milestone:
            return milestone
    return milestones[-1] if milestones else current_value

def calculate_level(total_points: int) -> tuple:
    """
    Calculate user level from total points.
    Returns (level, progress_to_next_level)
    """
    # Level thresholds (cumulative points needed)
    level_thresholds = [
        0,      # Level 1
        100,    # Level 2
        300,    # Level 3
        600,    # Level 4
        1000,   # Level 5
        1500,   # Level 6
        2200,   # Level 7
        3000,   # Level 8
        4000,   # Level 9
        5500,   # Level 10
        7500,   # Level 11+
    ]
    
    level = 1
    for i, threshold in enumerate(level_thresholds):
        if total_points >= threshold:
            level = i + 1
        else:
            break
    
    # Calculate progress to next level
    if level < len(level_thresholds):
        current_threshold = level_thresholds[level - 1]
        next_threshold = level_thresholds[level]
        points_in_level = total_points - current_threshold
        points_needed = next_threshold - current_threshold
        progress = points_in_level / points_needed if points_needed > 0 else 1.0
    else:
        progress = 1.0
    
    return level, min(progress, 1.0)
