"""
Budget Validation and Enforcement System
Manages spending limits and automated cost controls
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os

from .token_tracker import token_tracker, TokenUsage

logger = logging.getLogger(__name__)


class BudgetLevel(Enum):
    """Budget alert levels"""
    INFO = "info"          # 50% of budget
    WARNING = "warning"    # 75% of budget
    CRITICAL = "critical"  # 90% of budget
    EMERGENCY = "emergency" # 100% of budget


@dataclass
class BudgetLimit:
    """Budget limit configuration"""
    user_id: str
    user_email: str
    monthly_limit_usd: float
    daily_limit_usd: float
    per_request_limit_usd: float
    enabled: bool = True
    emergency_override: bool = False
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class BudgetAlert:
    """Budget alert record"""
    user_id: str
    user_email: str
    level: BudgetLevel
    current_usage: float
    limit: float
    percentage: float
    timestamp: datetime
    message: str
    action_taken: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        data = asdict(self)
        data['level'] = self.level.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class BudgetValidator:
    """Validates and enforces budget limits"""
    
    def __init__(self):
        self.budget_limits: Dict[str, BudgetLimit] = {}
        self.budget_alerts: List[BudgetAlert] = []
        self.blocked_users: set = set()
        
        # Default budget limits
        self.default_limits = {
            'monthly_limit_usd': float(os.getenv('DEFAULT_MONTHLY_BUDGET', '50.0')),
            'daily_limit_usd': float(os.getenv('DEFAULT_DAILY_BUDGET', '5.0')),
            'per_request_limit_usd': float(os.getenv('DEFAULT_REQUEST_BUDGET', '0.50'))
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            BudgetLevel.INFO: 0.5,
            BudgetLevel.WARNING: 0.75,
            BudgetLevel.CRITICAL: 0.9,
            BudgetLevel.EMERGENCY: 1.0
        }
    
    def set_user_budget(self, user_id: str, user_email: str, 
                       monthly_limit: float, daily_limit: float = None, 
                       per_request_limit: float = None) -> BudgetLimit:
        """Set budget limits for a user"""
        
        if daily_limit is None:
            daily_limit = monthly_limit / 30
        
        if per_request_limit is None:
            per_request_limit = min(daily_limit / 10, 1.0)
        
        budget_limit = BudgetLimit(
            user_id=user_id,
            user_email=user_email,
            monthly_limit_usd=monthly_limit,
            daily_limit_usd=daily_limit,
            per_request_limit_usd=per_request_limit
        )
        
        self.budget_limits[user_id] = budget_limit
        
        logger.info(f"💰 Budget set for {user_email}: ${monthly_limit}/month, ${daily_limit}/day")
        
        return budget_limit
    
    def get_user_budget(self, user_id: str) -> Optional[BudgetLimit]:
        """Get budget limits for a user"""
        return self.budget_limits.get(user_id)
    
    def get_or_create_user_budget(self, user_id: str, user_email: str) -> BudgetLimit:
        """Get existing budget or create default budget for user"""
        if user_id in self.budget_limits:
            return self.budget_limits[user_id]
        
        return self.set_user_budget(
            user_id=user_id,
            user_email=user_email,
            monthly_limit=self.default_limits['monthly_limit_usd'],
            daily_limit=self.default_limits['daily_limit_usd'],
            per_request_limit=self.default_limits['per_request_limit_usd']
        )
    
    def validate_request_budget(self, user_id: str, user_email: str, 
                               estimated_cost: float) -> Tuple[bool, Optional[str]]:
        """Validate if a request is within budget limits"""
        
        # Check if user is blocked
        if user_id in self.blocked_users:
            return False, "User is temporarily blocked due to budget violations"
        
        # Get or create budget
        budget = self.get_or_create_user_budget(user_id, user_email)
        
        if not budget.enabled:
            return True, None
        
        # Check per-request limit
        if estimated_cost > budget.per_request_limit_usd:
            return False, f"Request cost ${estimated_cost:.4f} exceeds per-request limit ${budget.per_request_limit_usd:.4f}"
        
        # Get current usage
        user_stats = token_tracker.get_user_usage(user_id)
        if not user_stats:
            return True, None
        
        # Check monthly limit
        monthly_usage = user_stats.current_month_cost_usd
        if monthly_usage + estimated_cost > budget.monthly_limit_usd:
            if not budget.emergency_override:
                return False, f"Monthly budget exceeded: ${monthly_usage + estimated_cost:.4f} > ${budget.monthly_limit_usd:.4f}"
        
        # Check daily limit
        daily_usage = self._get_daily_usage(user_id)
        if daily_usage + estimated_cost > budget.daily_limit_usd:
            if not budget.emergency_override:
                return False, f"Daily budget exceeded: ${daily_usage + estimated_cost:.4f} > ${budget.daily_limit_usd:.4f}"
        
        return True, None
    
    def _get_daily_usage(self, user_id: str) -> float:
        """Get today's usage for a user"""
        today = datetime.utcnow().date()
        daily_cost = 0.0
        
        for record in token_tracker.usage_records:
            if (record.user_id == user_id and 
                record.timestamp.date() == today):
                daily_cost += record.cost_usd
        
        return daily_cost
    
    def check_budget_alerts(self, user_id: str) -> List[BudgetAlert]:
        """Check for budget alerts for a user"""
        budget = self.get_user_budget(user_id)
        user_stats = token_tracker.get_user_usage(user_id)
        
        if not budget or not user_stats:
            return []
        
        alerts = []
        
        # Check monthly budget
        monthly_percentage = user_stats.current_month_cost_usd / budget.monthly_limit_usd
        monthly_alert = self._create_alert_if_needed(
            user_id, user_stats.user_email, monthly_percentage,
            user_stats.current_month_cost_usd, budget.monthly_limit_usd, "monthly"
        )
        if monthly_alert:
            alerts.append(monthly_alert)
        
        # Check daily budget
        daily_usage = self._get_daily_usage(user_id)
        daily_percentage = daily_usage / budget.daily_limit_usd
        daily_alert = self._create_alert_if_needed(
            user_id, user_stats.user_email, daily_percentage,
            daily_usage, budget.daily_limit_usd, "daily"
        )
        if daily_alert:
            alerts.append(daily_alert)
        
        return alerts
    
    def _create_alert_if_needed(self, user_id: str, user_email: str, 
                               percentage: float, current_usage: float, 
                               limit: float, period: str) -> Optional[BudgetAlert]:
        """Create an alert if thresholds are exceeded"""
        
        level = None
        for alert_level, threshold in self.alert_thresholds.items():
            if percentage >= threshold:
                level = alert_level
        
        if not level:
            return None
        
        # Determine action based on level
        action_taken = "none"
        if level == BudgetLevel.EMERGENCY:
            action_taken = "user_blocked"
            self.blocked_users.add(user_id)
        elif level == BudgetLevel.CRITICAL:
            action_taken = "fallback_mode_enabled"
        elif level == BudgetLevel.WARNING:
            action_taken = "notification_sent"
        
        # Create spiritual message
        message = self._create_spiritual_message(level, percentage, period)
        
        alert = BudgetAlert(
            user_id=user_id,
            user_email=user_email,
            level=level,
            current_usage=current_usage,
            limit=limit,
            percentage=percentage,
            timestamp=datetime.utcnow(),
            message=message,
            action_taken=action_taken
        )
        
        self.budget_alerts.append(alert)
        
        logger.warning(f"🚨 Budget alert for {user_email}: {level.value} - {percentage:.1%} of {period} budget")
        
        return alert
    
    def _create_spiritual_message(self, level: BudgetLevel, percentage: float, period: str) -> str:
        """Create Krishna-inspired budget messages"""
        
        if level == BudgetLevel.INFO:
            return (f"🕉️ Beloved devotee, you have used {percentage:.1%} of your {period} spiritual guidance budget. "
                   f"Like the steady flow of the Ganges, mindful usage brings lasting wisdom.")
        
        elif level == BudgetLevel.WARNING:
            return (f"⚡ Dear seeker, you have used {percentage:.1%} of your {period} budget. "
                   f"As I taught Arjuna about balance, consider moderating your requests to maintain harmony.")
        
        elif level == BudgetLevel.CRITICAL:
            return (f"🔥 Devoted soul, you have used {percentage:.1%} of your {period} budget. "
                   f"Like the careful archer who conserves arrows, wisdom lies in mindful consumption. "
                   f"Fallback responses will now be prioritized to preserve your remaining budget.")
        
        elif level == BudgetLevel.EMERGENCY:
            return (f"🛑 Precious devotee, your {period} budget has been exhausted. "
                   f"As even the sun must set to rise again, take this time for reflection. "
                   f"Your access is temporarily paused for spiritual and financial balance.")
        
        return "Budget threshold reached"
    
    def override_budget(self, user_id: str, admin_email: str, reason: str) -> bool:
        """Override budget limits (admin only)"""
        budget = self.get_user_budget(user_id)
        if not budget:
            return False
        
        budget.emergency_override = True
        budget.updated_at = datetime.utcnow()
        
        # Remove from blocked users
        self.blocked_users.discard(user_id)
        
        logger.info(f"🔓 Budget override for {budget.user_email} by admin {admin_email}: {reason}")
        
        return True
    
    def unblock_user(self, user_id: str, admin_email: str) -> bool:
        """Unblock a user (admin only)"""
        if user_id not in self.blocked_users:
            return False
        
        self.blocked_users.remove(user_id)
        
        budget = self.get_user_budget(user_id)
        user_email = budget.user_email if budget else user_id
        
        logger.info(f"🔓 User {user_email} unblocked by admin {admin_email}")
        
        return True
    
    def get_budget_summary(self) -> Dict[str, Any]:
        """Get system-wide budget summary"""
        total_budgets = len(self.budget_limits)
        total_alerts = len(self.budget_alerts)
        blocked_count = len(self.blocked_users)
        
        # Alert breakdown
        alert_breakdown = {}
        for alert in self.budget_alerts:
            level = alert.level.value
            alert_breakdown[level] = alert_breakdown.get(level, 0) + 1
        
        # Recent alerts (last 24 hours)
        recent_alerts = [
            alert for alert in self.budget_alerts
            if alert.timestamp > datetime.utcnow() - timedelta(hours=24)
        ]
        
        return {
            'total_budgets': total_budgets,
            'total_alerts': total_alerts,
            'blocked_users': blocked_count,
            'recent_alerts': len(recent_alerts),
            'alert_breakdown': alert_breakdown,
            'default_limits': self.default_limits
        }
    
    def get_user_budget_status(self, user_id: str) -> Dict[str, Any]:
        """Get detailed budget status for a user"""
        budget = self.get_user_budget(user_id)
        user_stats = token_tracker.get_user_usage(user_id)
        
        if not budget or not user_stats:
            return {'status': 'no_data'}
        
        daily_usage = self._get_daily_usage(user_id)
        monthly_usage = user_stats.current_month_cost_usd
        
        return {
            'budget_limits': budget.to_dict(),
            'current_usage': {
                'monthly': monthly_usage,
                'daily': daily_usage,
                'total': user_stats.total_cost_usd
            },
            'usage_percentages': {
                'monthly': (monthly_usage / budget.monthly_limit_usd) * 100,
                'daily': (daily_usage / budget.daily_limit_usd) * 100
            },
            'is_blocked': user_id in self.blocked_users,
            'emergency_override': budget.emergency_override,
            'remaining_budget': {
                'monthly': budget.monthly_limit_usd - monthly_usage,
                'daily': budget.daily_limit_usd - daily_usage
            }
        }


# Global budget validator
budget_validator = BudgetValidator()
