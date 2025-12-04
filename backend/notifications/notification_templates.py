"""
Notification Templates
Defines notification types, templates, and content structures
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


class NotificationType(Enum):
    """Types of notifications the system can send"""
    DAILY_WISDOM = "daily_wisdom"
    STREAK_REMINDER = "streak_reminder"
    STREAK_AT_RISK = "streak_at_risk"
    STREAK_BROKEN = "streak_broken"
    STREAK_MILESTONE = "streak_milestone"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    NEW_PERSONALITY = "new_personality"
    WEEKLY_SUMMARY = "weekly_summary"
    WELCOME_BACK = "welcome_back"
    ENGAGEMENT_NUDGE = "engagement_nudge"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationTemplate:
    """Template structure for notifications"""
    type: NotificationType
    title_template: str
    body_template: str
    icon: str
    badge: str
    tag: str
    priority: NotificationPriority
    require_interaction: bool = False
    actions: Optional[List[Dict[str, str]]] = None
    data: Optional[Dict[str, Any]] = None
    
    def render(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Render the template with the given context"""
        title = self.title_template.format(**context)
        body = self.body_template.format(**context)
        
        notification = {
            "title": title,
            "body": body,
            "icon": self.icon,
            "badge": self.badge,
            "tag": self.tag,
            "requireInteraction": self.require_interaction,
            "data": {
                "type": self.type.value,
                "url": context.get("url", "/guidance"),
                **(self.data or {}),
                **context
            }
        }
        
        if self.actions:
            notification["actions"] = self.actions
            
        return notification


# =============================================================================
# NOTIFICATION TEMPLATES
# =============================================================================

NOTIFICATION_TEMPLATES: Dict[NotificationType, NotificationTemplate] = {
    
    # Daily Wisdom Notification
    NotificationType.DAILY_WISDOM: NotificationTemplate(
        type=NotificationType.DAILY_WISDOM,
        title_template="🕉️ Daily Wisdom from {personality_name}",
        body_template='"{wisdom_quote}"',
        icon="/icons/wisdom-192.png",
        badge="/icons/badge-72.png",
        tag="daily-wisdom",
        priority=NotificationPriority.NORMAL,
        require_interaction=False,
        actions=[
            {"action": "open", "title": "Explore More"},
            {"action": "dismiss", "title": "Later"}
        ]
    ),
    
    # Streak Reminder (sent at user's preferred time)
    NotificationType.STREAK_REMINDER: NotificationTemplate(
        type=NotificationType.STREAK_REMINDER,
        title_template="🔥 Keep Your {streak_count}-Day Streak Alive!",
        body_template="A moment of wisdom awaits. {personality_name} has something to share.",
        icon="/icons/streak-192.png",
        badge="/icons/badge-72.png",
        tag="streak-reminder",
        priority=NotificationPriority.NORMAL,
        require_interaction=False,
        actions=[
            {"action": "open", "title": "Continue Streak"},
            {"action": "dismiss", "title": "Remind Later"}
        ]
    ),
    
    # Streak At Risk (sent when user hasn't engaged today and time is running out)
    NotificationType.STREAK_AT_RISK: NotificationTemplate(
        type=NotificationType.STREAK_AT_RISK,
        title_template="⚠️ Your {streak_count}-Day Streak is at Risk!",
        body_template="Only {hours_left} hours left! Don't lose your progress.",
        icon="/icons/warning-192.png",
        badge="/icons/badge-72.png",
        tag="streak-risk",
        priority=NotificationPriority.HIGH,
        require_interaction=True,
        actions=[
            {"action": "open", "title": "Save My Streak"},
            {"action": "freeze", "title": "Use Freeze"}
        ]
    ),
    
    # Streak Broken
    NotificationType.STREAK_BROKEN: NotificationTemplate(
        type=NotificationType.STREAK_BROKEN,
        title_template="💔 Your Streak Has Ended",
        body_template="Your {previous_streak}-day streak ended, but every journey has new beginnings. Start fresh today!",
        icon="/icons/streak-broken-192.png",
        badge="/icons/badge-72.png",
        tag="streak-broken",
        priority=NotificationPriority.NORMAL,
        require_interaction=False,
        actions=[
            {"action": "open", "title": "Start New Streak"}
        ]
    ),
    
    # Streak Milestone
    NotificationType.STREAK_MILESTONE: NotificationTemplate(
        type=NotificationType.STREAK_MILESTONE,
        title_template="🎉 {streak_count}-Day Streak Milestone!",
        body_template="Incredible dedication! You've earned {points} points and unlocked special wisdom.",
        icon="/icons/milestone-192.png",
        badge="/icons/badge-72.png",
        tag="streak-milestone",
        priority=NotificationPriority.HIGH,
        require_interaction=False,
        actions=[
            {"action": "open", "title": "View Achievement"},
            {"action": "share", "title": "Share"}
        ]
    ),
    
    # Achievement Unlocked
    NotificationType.ACHIEVEMENT_UNLOCKED: NotificationTemplate(
        type=NotificationType.ACHIEVEMENT_UNLOCKED,
        title_template="🏆 Achievement Unlocked!",
        body_template='"{achievement_name}" - {achievement_description}',
        icon="/icons/achievement-192.png",
        badge="/icons/badge-72.png",
        tag="achievement",
        priority=NotificationPriority.NORMAL,
        require_interaction=False,
        actions=[
            {"action": "open", "title": "View Achievement"},
            {"action": "share", "title": "Share"}
        ]
    ),
    
    # New Personality Available
    NotificationType.NEW_PERSONALITY: NotificationTemplate(
        type=NotificationType.NEW_PERSONALITY,
        title_template="✨ New Wisdom Guide Available",
        body_template="{personality_name} has joined Vimarsh. Discover {domain} wisdom!",
        icon="/icons/new-personality-192.png",
        badge="/icons/badge-72.png",
        tag="new-personality",
        priority=NotificationPriority.LOW,
        require_interaction=False,
        actions=[
            {"action": "open", "title": "Meet {personality_name}"}
        ]
    ),
    
    # Weekly Summary
    NotificationType.WEEKLY_SUMMARY: NotificationTemplate(
        type=NotificationType.WEEKLY_SUMMARY,
        title_template="📊 Your Weekly Wisdom Journey",
        body_template="{conversations} conversations, {domains_explored} domains, {streak_days} streak days. Keep growing!",
        icon="/icons/summary-192.png",
        badge="/icons/badge-72.png",
        tag="weekly-summary",
        priority=NotificationPriority.LOW,
        require_interaction=False,
        actions=[
            {"action": "open", "title": "View Full Report"}
        ]
    ),
    
    # Welcome Back (for users who haven't engaged in 3+ days)
    NotificationType.WELCOME_BACK: NotificationTemplate(
        type=NotificationType.WELCOME_BACK,
        title_template="🙏 We've Missed You",
        body_template="{personality_name} has new wisdom to share. Your journey awaits.",
        icon="/icons/welcome-192.png",
        badge="/icons/badge-72.png",
        tag="welcome-back",
        priority=NotificationPriority.NORMAL,
        require_interaction=False,
        actions=[
            {"action": "open", "title": "Resume Journey"}
        ]
    ),
    
    # Engagement Nudge (gentle reminder for light users)
    NotificationType.ENGAGEMENT_NUDGE: NotificationTemplate(
        type=NotificationType.ENGAGEMENT_NUDGE,
        title_template="💭 A Moment of Reflection",
        body_template="Take a mindful pause. {personality_name} awaits with timeless wisdom.",
        icon="/icons/nudge-192.png",
        badge="/icons/badge-72.png",
        tag="engagement-nudge",
        priority=NotificationPriority.LOW,
        require_interaction=False,
        actions=[
            {"action": "open", "title": "Begin"}
        ]
    ),
}


def get_template(notification_type: NotificationType) -> NotificationTemplate:
    """Get a notification template by type"""
    return NOTIFICATION_TEMPLATES.get(notification_type)


def render_notification(
    notification_type: NotificationType, 
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Render a notification with the given context"""
    template = get_template(notification_type)
    if not template:
        raise ValueError(f"Unknown notification type: {notification_type}")
    return template.render(context)


# =============================================================================
# WISDOM QUOTES FOR DAILY NOTIFICATIONS
# =============================================================================

WISDOM_QUOTES: Dict[str, List[str]] = {
    "krishna": [
        "You have the right to work, but never to the fruit of work.",
        "Change is the law of the universe. What you consider as death is actually a new beginning.",
        "The mind is restless and difficult to control, but it can be trained by practice.",
        "Whatever happened, happened for good. Whatever is happening, is happening for good.",
        "Set thy heart upon thy work, but never on its reward.",
    ],
    "buddha": [
        "Peace comes from within. Do not seek it without.",
        "The mind is everything. What you think you become.",
        "Three things cannot be long hidden: the sun, the moon, and the truth.",
        "In the end, only three things matter: how much you loved, how gently you lived, and how gracefully you let go.",
        "Holding on to anger is like grasping a hot coal with the intent of throwing it at someone else.",
    ],
    "einstein": [
        "Imagination is more important than knowledge. Knowledge is limited, imagination encircles the world.",
        "Life is like riding a bicycle. To keep your balance, you must keep moving.",
        "Try not to become a man of success, but rather try to become a man of value.",
        "The important thing is not to stop questioning. Curiosity has its own reason for existing.",
        "In the middle of difficulty lies opportunity.",
    ],
    "gandhi": [
        "Be the change you wish to see in the world.",
        "Strength does not come from physical capacity. It comes from an indomitable will.",
        "The best way to find yourself is to lose yourself in the service of others.",
        "An eye for an eye only ends up making the whole world blind.",
        "Live as if you were to die tomorrow. Learn as if you were to live forever.",
    ],
    "marcus_aurelius": [
        "The happiness of your life depends upon the quality of your thoughts.",
        "Very little is needed to make a happy life; it is all within yourself, in your way of thinking.",
        "Waste no more time arguing about what a good man should be. Be one.",
        "The soul becomes dyed with the color of its thoughts.",
        "Accept the things to which fate binds you, and love the people with whom fate brings you together.",
    ],
    "lincoln": [
        "In the end, it's not the years in your life that count. It's the life in your years.",
        "Whatever you are, be a good one.",
        "The best way to predict your future is to create it.",
        "I am not bound to succeed, but I am bound to live by the light that I have.",
        "Character is like a tree and reputation like a shadow. The shadow is what we think of it; the tree is the real thing.",
    ],
    "shakespeare": [
        "To thine own self be true.",
        "All the world's a stage, and all the men and women merely players.",
        "The course of true love never did run smooth.",
        "There is nothing either good or bad, but thinking makes it so.",
        "We know what we are, but know not what we may be.",
    ],
    "confucius": [
        "It does not matter how slowly you go as long as you do not stop.",
        "Our greatest glory is not in never falling, but in rising every time we fall.",
        "Real knowledge is to know the extent of one's ignorance.",
        "Choose a job you love, and you will never have to work a day in your life.",
        "Before you embark on a journey of revenge, dig two graves.",
    ],
}


def get_random_quote(personality_id: str) -> Optional[str]:
    """Get a random wisdom quote for a personality"""
    import random
    quotes = WISDOM_QUOTES.get(personality_id, [])
    if quotes:
        return random.choice(quotes)
    return None
