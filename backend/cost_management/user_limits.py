"""
Per-User AI Usage Limits with Enforcement and Override Capabilities
Task 7.9: Enhanced AI Cost Management & Dynamic Fallbacks

This module provides comprehensive per-user usage limits, enforcement mechanisms,
and administrative override capabilities for managing AI costs in beta testing.

Features:
- Flexible per-user usage limits (tokens, cost, queries, time-based)
- Real-time enforcement with multiple escalation levels
- Administrative override capabilities for VIP users
- Usage tracking and analytics per user
- Automatic quota resets and notifications
- Integration with existing cost management systems
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum, IntEnum
from pathlib import Path
import threading
from collections import defaultdict, deque
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LimitType(Enum):
    """Types of usage limits"""
    TOKENS_PER_DAY = "tokens_per_day"
    TOKENS_PER_HOUR = "tokens_per_hour"
    COST_PER_DAY = "cost_per_day"
    COST_PER_HOUR = "cost_per_hour"
    QUERIES_PER_DAY = "queries_per_day"
    QUERIES_PER_HOUR = "queries_per_hour"
    CONCURRENT_REQUESTS = "concurrent_requests"


class EnforcementAction(Enum):
    """Actions to take when limits are exceeded"""
    ALLOW = "allow"              # Allow but log
    WARN = "warn"               # Warning to user
    THROTTLE = "throttle"       # Slow down requests
    DOWNGRADE = "downgrade"     # Use cheaper model
    QUEUE = "queue"             # Queue for later processing
    BLOCK = "block"             # Block request entirely


class UserTier(Enum):
    """User tiers for different limit levels"""
    FREE = "free"               # Basic limits
    BETA = "beta"               # Beta tester limits
    VIP = "vip"                 # Higher limits for VIP users
    ADMIN = "admin"             # Administrative access
    UNLIMITED = "unlimited"     # No limits (emergency only)


@dataclass
class UsageLimitConfig:
    """Configuration for a usage limit"""
    limit_type: LimitType
    value: float
    enforcement_action: EnforcementAction
    reset_period_hours: int = 24
    warning_threshold: float = 0.8  # Warn at 80% of limit
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['limit_type'] = self.limit_type.value
        data['enforcement_action'] = self.enforcement_action.value
        return data


@dataclass
class UserUsageProfile:
    """User usage profile and limits"""
    user_id: str
    tier: UserTier
    limits: List[UsageLimitConfig]
    current_usage: Dict[str, float]  # limit_type -> current value
    last_reset: Dict[str, datetime]  # limit_type -> last reset time
    overrides: Dict[str, Any]  # admin overrides
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['tier'] = self.tier.value
        data['limits'] = [limit.to_dict() for limit in self.limits]
        data['last_reset'] = {k: v.isoformat() for k, v in self.last_reset.items()}
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class UsageAttempt:
    """Record of a usage attempt"""
    user_id: str
    timestamp: datetime
    tokens_requested: int
    cost_requested: float
    limit_type: LimitType
    enforcement_action: EnforcementAction
    success: bool
    reason: str
    override_used: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['limit_type'] = self.limit_type.value
        data['enforcement_action'] = self.enforcement_action.value
        return data


class UserLimitManager:
    """Manages per-user usage limits and enforcement"""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize user limit manager
        
        Args:
            storage_path: Path to store user profiles and usage data
        """
        self.storage_path = Path(storage_path) if storage_path else Path("data/user_limits")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # User profiles storage
        self.user_profiles: Dict[str, UserUsageProfile] = {}
        self.usage_attempts: List[UsageAttempt] = []
        
        # Default tier configurations
        self.tier_configs = self._initialize_tier_configs()
        
        # Active sessions tracking
        self.active_sessions: Dict[str, int] = defaultdict(int)  # user_id -> concurrent requests
        
        # Threading
        self.lock = threading.Lock()
        
        # Load existing data
        self._load_user_profiles()
        self._load_usage_attempts()
    
    def _initialize_tier_configs(self) -> Dict[UserTier, List[UsageLimitConfig]]:
        """Initialize default configurations for each user tier"""
        return {
            UserTier.FREE: [
                UsageLimitConfig(LimitType.TOKENS_PER_DAY, 10000, EnforcementAction.BLOCK),
                UsageLimitConfig(LimitType.COST_PER_DAY, 1.0, EnforcementAction.BLOCK),
                UsageLimitConfig(LimitType.QUERIES_PER_HOUR, 20, EnforcementAction.THROTTLE),
                UsageLimitConfig(LimitType.CONCURRENT_REQUESTS, 2, EnforcementAction.QUEUE, reset_period_hours=0)
            ],
            UserTier.BETA: [
                UsageLimitConfig(LimitType.TOKENS_PER_DAY, 50000, EnforcementAction.WARN),
                UsageLimitConfig(LimitType.COST_PER_DAY, 5.0, EnforcementAction.DOWNGRADE),
                UsageLimitConfig(LimitType.QUERIES_PER_HOUR, 100, EnforcementAction.THROTTLE),
                UsageLimitConfig(LimitType.CONCURRENT_REQUESTS, 5, EnforcementAction.QUEUE, reset_period_hours=0)
            ],
            UserTier.VIP: [
                UsageLimitConfig(LimitType.TOKENS_PER_DAY, 200000, EnforcementAction.WARN),
                UsageLimitConfig(LimitType.COST_PER_DAY, 20.0, EnforcementAction.WARN),
                UsageLimitConfig(LimitType.QUERIES_PER_HOUR, 500, EnforcementAction.WARN),
                UsageLimitConfig(LimitType.CONCURRENT_REQUESTS, 10, EnforcementAction.ALLOW, reset_period_hours=0)
            ],
            UserTier.ADMIN: [
                UsageLimitConfig(LimitType.TOKENS_PER_DAY, 1000000, EnforcementAction.ALLOW),
                UsageLimitConfig(LimitType.COST_PER_DAY, 100.0, EnforcementAction.ALLOW),
                UsageLimitConfig(LimitType.QUERIES_PER_HOUR, 2000, EnforcementAction.ALLOW),
                UsageLimitConfig(LimitType.CONCURRENT_REQUESTS, 20, EnforcementAction.ALLOW, reset_period_hours=0)
            ],
            UserTier.UNLIMITED: []  # No limits
        }
    
    def _load_user_profiles(self):
        """Load user profiles from storage"""
        try:
            profiles_file = self.storage_path / "user_profiles.json"
            if profiles_file.exists():
                with open(profiles_file, 'r') as f:
                    data = json.load(f)
                    for user_id, profile_data in data.items():
                        self.user_profiles[user_id] = UserUsageProfile(
                            user_id=profile_data['user_id'],
                            tier=UserTier(profile_data['tier']),
                            limits=[
                                UsageLimitConfig(
                                    limit_type=LimitType(limit_data['limit_type']),
                                    value=limit_data['value'],
                                    enforcement_action=EnforcementAction(limit_data['enforcement_action']),
                                    reset_period_hours=limit_data['reset_period_hours'],
                                    warning_threshold=limit_data['warning_threshold'],
                                    enabled=limit_data['enabled']
                                )
                                for limit_data in profile_data['limits']
                            ],
                            current_usage=profile_data['current_usage'],
                            last_reset={k: datetime.fromisoformat(v) for k, v in profile_data['last_reset'].items()},
                            overrides=profile_data['overrides'],
                            created_at=datetime.fromisoformat(profile_data['created_at']),
                            updated_at=datetime.fromisoformat(profile_data['updated_at'])
                        )
                logger.info(f"Loaded {len(self.user_profiles)} user profiles")
        except Exception as e:
            logger.warning(f"Could not load user profiles: {e}")
    
    def _load_usage_attempts(self):
        """Load usage attempts history"""
        try:
            attempts_file = self.storage_path / "usage_attempts.json"
            if attempts_file.exists():
                with open(attempts_file, 'r') as f:
                    data = json.load(f)
                    self.usage_attempts = [
                        UsageAttempt(
                            user_id=attempt['user_id'],
                            timestamp=datetime.fromisoformat(attempt['timestamp']),
                            tokens_requested=attempt['tokens_requested'],
                            cost_requested=attempt['cost_requested'],
                            limit_type=LimitType(attempt['limit_type']),
                            enforcement_action=EnforcementAction(attempt['enforcement_action']),
                            success=attempt['success'],
                            reason=attempt['reason'],
                            override_used=attempt.get('override_used')
                        )
                        for attempt in data
                    ]
                    
                    # Keep only recent attempts (last 30 days)
                    cutoff_date = datetime.now() - timedelta(days=30)
                    self.usage_attempts = [
                        attempt for attempt in self.usage_attempts 
                        if attempt.timestamp >= cutoff_date
                    ]
                logger.info(f"Loaded {len(self.usage_attempts)} usage attempts")
        except Exception as e:
            logger.warning(f"Could not load usage attempts: {e}")
    
    def _save_user_profiles(self):
        """Save user profiles to storage"""
        try:
            profiles_file = self.storage_path / "user_profiles.json"
            with open(profiles_file, 'w') as f:
                json.dump({user_id: profile.to_dict() for user_id, profile in self.user_profiles.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save user profiles: {e}")
    
    def _save_usage_attempts(self):
        """Save usage attempts to storage"""
        try:
            attempts_file = self.storage_path / "usage_attempts.json"
            with open(attempts_file, 'w') as f:
                json.dump([attempt.to_dict() for attempt in self.usage_attempts], f, indent=2)
        except Exception as e:
            logger.error(f"Could not save usage attempts: {e}")
    
    def create_user_profile(self, 
                           user_id: str, 
                           tier: UserTier,
                           custom_limits: Optional[List[UsageLimitConfig]] = None) -> UserUsageProfile:
        """
        Create a new user profile with usage limits
        
        Args:
            user_id: Unique user identifier
            tier: User tier determining default limits
            custom_limits: Custom limits to override defaults
            
        Returns:
            Created user profile
        """
        with self.lock:
            if user_id in self.user_profiles:
                logger.warning(f"User profile already exists for {user_id}")
                return self.user_profiles[user_id]
            
            # Use custom limits or tier defaults
            limits = custom_limits if custom_limits else self.tier_configs.get(tier, [])
            
            # Initialize current usage and reset times
            current_usage = {}
            last_reset = {}
            for limit in limits:
                current_usage[limit.limit_type.value] = 0.0
                last_reset[limit.limit_type.value] = datetime.now()
            
            profile = UserUsageProfile(
                user_id=user_id,
                tier=tier,
                limits=limits,
                current_usage=current_usage,
                last_reset=last_reset,
                overrides={},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.user_profiles[user_id] = profile
            self._save_user_profiles()
            
            logger.info(f"Created user profile for {user_id} with tier {tier.value}")
            return profile
    
    def get_user_profile(self, user_id: str) -> Optional[UserUsageProfile]:
        """Get user profile, creating one if needed"""
        if user_id not in self.user_profiles:
            # Create default profile for new users
            return self.create_user_profile(user_id, UserTier.FREE)
        return self.user_profiles[user_id]
    
    def update_user_tier(self, user_id: str, new_tier: UserTier) -> bool:
        """
        Update user tier and associated limits
        
        Args:
            user_id: User identifier
            new_tier: New user tier
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            if user_id not in self.user_profiles:
                logger.error(f"User profile not found: {user_id}")
                return False
            
            profile = self.user_profiles[user_id]
            old_tier = profile.tier
            
            # Update tier and limits
            profile.tier = new_tier
            profile.limits = self.tier_configs.get(new_tier, [])
            profile.updated_at = datetime.now()
            
            # Reset usage counters for new limits
            for limit in profile.limits:
                if limit.limit_type.value not in profile.current_usage:
                    profile.current_usage[limit.limit_type.value] = 0.0
                    profile.last_reset[limit.limit_type.value] = datetime.now()
            
            self._save_user_profiles()
            
            logger.info(f"Updated user {user_id} tier from {old_tier.value} to {new_tier.value}")
            return True
    
    def add_admin_override(self, 
                          user_id: str, 
                          override_type: str, 
                          value: Any, 
                          duration_hours: Optional[int] = None,
                          reason: str = "") -> bool:
        """
        Add administrative override for a user
        
        Args:
            user_id: User identifier
            override_type: Type of override (e.g., 'unlimited_tokens', 'bypass_limits')
            value: Override value
            duration_hours: Duration in hours (None = permanent)
            reason: Reason for override
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            profile = self.get_user_profile(user_id)
            if not profile:
                return False
            
            expiry = datetime.now() + timedelta(hours=duration_hours) if duration_hours else None
            
            override_data = {
                'value': value,
                'expiry': expiry.isoformat() if expiry else None,
                'reason': reason,
                'created_at': datetime.now().isoformat(),
                'created_by': 'admin'  # Could be enhanced to track which admin
            }
            
            profile.overrides[override_type] = override_data
            profile.updated_at = datetime.now()
            
            self._save_user_profiles()
            
            duration_str = f"for {duration_hours} hours" if duration_hours else "permanently"
            logger.info(f"Added override '{override_type}' for user {user_id} {duration_str}: {reason}")
            return True
    
    def remove_admin_override(self, user_id: str, override_type: str) -> bool:
        """Remove administrative override"""
        with self.lock:
            profile = self.get_user_profile(user_id)
            if not profile or override_type not in profile.overrides:
                return False
            
            del profile.overrides[override_type]
            profile.updated_at = datetime.now()
            
            self._save_user_profiles()
            
            logger.info(f"Removed override '{override_type}' for user {user_id}")
            return True
    
    def _check_expired_overrides(self, profile: UserUsageProfile):
        """Remove expired overrides"""
        now = datetime.now()
        expired_overrides = []
        
        for override_type, override_data in profile.overrides.items():
            if override_data.get('expiry'):
                expiry = datetime.fromisoformat(override_data['expiry'])
                if now >= expiry:
                    expired_overrides.append(override_type)
        
        for override_type in expired_overrides:
            del profile.overrides[override_type]
            logger.info(f"Removed expired override '{override_type}' for user {profile.user_id}")
    
    def _reset_usage_if_needed(self, profile: UserUsageProfile):
        """Reset usage counters if reset period has passed"""
        now = datetime.now()
        
        for limit in profile.limits:
            limit_key = limit.limit_type.value
            last_reset = profile.last_reset.get(limit_key, now)
            
            if limit.reset_period_hours > 0:
                if now >= last_reset + timedelta(hours=limit.reset_period_hours):
                    profile.current_usage[limit_key] = 0.0
                    profile.last_reset[limit_key] = now
                    logger.debug(f"Reset usage for {profile.user_id} - {limit_key}")
    
    def check_usage_limit(self, 
                         user_id: str, 
                         tokens_requested: int = 0,
                         cost_requested: float = 0.0,
                         queries_requested: int = 1) -> Tuple[bool, EnforcementAction, str]:
        """
        Check if user can proceed with the requested usage
        
        Args:
            user_id: User identifier
            tokens_requested: Number of tokens requested
            cost_requested: Cost of the request
            queries_requested: Number of queries requested
            
        Returns:
            Tuple of (can_proceed, enforcement_action, reason)
        """
        with self.lock:
            profile = self.get_user_profile(user_id)
            if not profile:
                return False, EnforcementAction.BLOCK, "User profile not found"
            
            # Check for expired overrides
            self._check_expired_overrides(profile)
            
            # Check for unlimited override
            if 'unlimited_access' in profile.overrides:
                return True, EnforcementAction.ALLOW, "Unlimited access override"
            
            # Reset usage counters if needed
            self._reset_usage_if_needed(profile)
            
            # Check each limit
            violations = []
            most_restrictive_action = EnforcementAction.ALLOW
            
            for limit in profile.limits:
                if not limit.enabled:
                    continue
                
                limit_key = limit.limit_type.value
                current_usage = profile.current_usage.get(limit_key, 0.0)
                
                # Calculate new usage
                if limit.limit_type == LimitType.TOKENS_PER_DAY or limit.limit_type == LimitType.TOKENS_PER_HOUR:
                    new_usage = current_usage + tokens_requested
                elif limit.limit_type == LimitType.COST_PER_DAY or limit.limit_type == LimitType.COST_PER_HOUR:
                    new_usage = current_usage + cost_requested
                elif limit.limit_type == LimitType.QUERIES_PER_DAY or limit.limit_type == LimitType.QUERIES_PER_HOUR:
                    new_usage = current_usage + queries_requested
                elif limit.limit_type == LimitType.CONCURRENT_REQUESTS:
                    new_usage = self.active_sessions.get(user_id, 0) + 1
                else:
                    continue
                
                # Check if limit would be exceeded
                if new_usage > limit.value:
                    violations.append({
                        'limit_type': limit.limit_type,
                        'current': current_usage,
                        'requested': new_usage - current_usage,
                        'limit': limit.value,
                        'action': limit.enforcement_action
                    })
                    
                    # Track most restrictive action
                    if self._is_more_restrictive(limit.enforcement_action, most_restrictive_action):
                        most_restrictive_action = limit.enforcement_action
            
            # Record the attempt
            primary_limit = violations[0]['limit_type'] if violations else LimitType.QUERIES_PER_DAY
            attempt = UsageAttempt(
                user_id=user_id,
                timestamp=datetime.now(),
                tokens_requested=tokens_requested,
                cost_requested=cost_requested,
                limit_type=primary_limit,
                enforcement_action=most_restrictive_action,
                success=len(violations) == 0,
                reason=f"{len(violations)} limit violations" if violations else "Within limits"
            )
            
            self.usage_attempts.append(attempt)
            
            # Periodically save attempts
            if len(self.usage_attempts) % 50 == 0:
                self._save_usage_attempts()
            
            if violations:
                violation_details = "; ".join([
                    f"{v['limit_type'].value}: {v['current']:.2f}/{v['limit']:.2f} (+{v['requested']:.2f})"
                    for v in violations
                ])
                return False, most_restrictive_action, f"Limit exceeded: {violation_details}"
            
            return True, EnforcementAction.ALLOW, "Within all limits"
    
    def _is_more_restrictive(self, action1: EnforcementAction, action2: EnforcementAction) -> bool:
        """Check if action1 is more restrictive than action2"""
        restrictiveness = {
            EnforcementAction.ALLOW: 0,
            EnforcementAction.WARN: 1,
            EnforcementAction.THROTTLE: 2,
            EnforcementAction.DOWNGRADE: 3,
            EnforcementAction.QUEUE: 4,
            EnforcementAction.BLOCK: 5
        }
        return restrictiveness.get(action1, 0) > restrictiveness.get(action2, 0)
    
    def record_usage(self, 
                    user_id: str, 
                    tokens_used: int = 0,
                    cost_incurred: float = 0.0,
                    queries_count: int = 1):
        """
        Record actual usage for a user
        
        Args:
            user_id: User identifier
            tokens_used: Number of tokens consumed
            cost_incurred: Cost incurred
            queries_count: Number of queries processed
        """
        with self.lock:
            profile = self.get_user_profile(user_id)
            if not profile:
                return
            
            # Update usage counters
            now = datetime.now()
            
            for limit in profile.limits:
                limit_key = limit.limit_type.value
                
                if limit.limit_type in [LimitType.TOKENS_PER_DAY, LimitType.TOKENS_PER_HOUR]:
                    profile.current_usage[limit_key] = profile.current_usage.get(limit_key, 0) + tokens_used
                elif limit.limit_type in [LimitType.COST_PER_DAY, LimitType.COST_PER_HOUR]:
                    profile.current_usage[limit_key] = profile.current_usage.get(limit_key, 0) + cost_incurred
                elif limit.limit_type in [LimitType.QUERIES_PER_DAY, LimitType.QUERIES_PER_HOUR]:
                    profile.current_usage[limit_key] = profile.current_usage.get(limit_key, 0) + queries_count
            
            profile.updated_at = now
            
            # Save periodically
            if len(self.user_profiles) % 10 == 0:
                self._save_user_profiles()
    
    def start_session(self, user_id: str):
        """Start a session for concurrent request tracking"""
        with self.lock:
            self.active_sessions[user_id] = self.active_sessions.get(user_id, 0) + 1
    
    def end_session(self, user_id: str):
        """End a session for concurrent request tracking"""
        with self.lock:
            if user_id in self.active_sessions:
                self.active_sessions[user_id] = max(0, self.active_sessions[user_id] - 1)
                if self.active_sessions[user_id] == 0:
                    del self.active_sessions[user_id]
    
    def get_user_usage_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive usage statistics for a user"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return None
        
        # Reset counters if needed
        self._reset_usage_if_needed(profile)
        
        # Calculate usage percentages
        usage_stats = {}
        for limit in profile.limits:
            limit_key = limit.limit_type.value
            current = profile.current_usage.get(limit_key, 0)
            percentage = (current / limit.value * 100) if limit.value > 0 else 0
            
            usage_stats[limit_key] = {
                'current': current,
                'limit': limit.value,
                'percentage': percentage,
                'enforcement_action': limit.enforcement_action.value,
                'time_until_reset': self._time_until_reset(profile, limit)
            }
        
        # Get recent attempts
        recent_attempts = [
            attempt for attempt in self.usage_attempts
            if attempt.user_id == user_id and 
            attempt.timestamp >= datetime.now() - timedelta(hours=24)
        ]
        
        return {
            'user_id': user_id,
            'tier': profile.tier.value,
            'usage_stats': usage_stats,
            'active_overrides': list(profile.overrides.keys()),
            'recent_attempts': len(recent_attempts),
            'failed_attempts': len([a for a in recent_attempts if not a.success]),
            'concurrent_sessions': self.active_sessions.get(user_id, 0),
            'last_activity': profile.updated_at.isoformat()
        }
    
    def _time_until_reset(self, profile: UserUsageProfile, limit: UsageLimitConfig) -> Optional[str]:
        """Calculate time until limit reset"""
        if limit.reset_period_hours <= 0:
            return None
        
        limit_key = limit.limit_type.value
        last_reset = profile.last_reset.get(limit_key, datetime.now())
        next_reset = last_reset + timedelta(hours=limit.reset_period_hours)
        
        if next_reset <= datetime.now():
            return "Reset available"
        
        remaining = next_reset - datetime.now()
        hours = remaining.total_seconds() / 3600
        
        if hours < 1:
            return f"{int(remaining.total_seconds() / 60)} minutes"
        elif hours < 24:
            return f"{int(hours)} hours"
        else:
            return f"{int(hours / 24)} days"
    
    def get_admin_dashboard(self) -> Dict[str, Any]:
        """Get administrative dashboard data"""
        now = datetime.now()
        
        # User statistics
        tier_counts = defaultdict(int)
        active_users = 0
        total_overrides = 0
        
        for profile in self.user_profiles.values():
            tier_counts[profile.tier.value] += 1
            if profile.updated_at >= now - timedelta(hours=24):
                active_users += 1
            total_overrides += len(profile.overrides)
        
        # Recent usage attempts
        recent_attempts = [
            attempt for attempt in self.usage_attempts
            if attempt.timestamp >= now - timedelta(hours=24)
        ]
        
        failed_attempts = [attempt for attempt in recent_attempts if not attempt.success]
        
        # Top violators
        violator_counts = defaultdict(int)
        for attempt in failed_attempts:
            violator_counts[attempt.user_id] += 1
        
        top_violators = sorted(violator_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_users': len(self.user_profiles),
            'active_users_24h': active_users,
            'tier_distribution': dict(tier_counts),
            'total_overrides': total_overrides,
            'concurrent_sessions': sum(self.active_sessions.values()),
            'usage_attempts_24h': len(recent_attempts),
            'failed_attempts_24h': len(failed_attempts),
            'top_violators': top_violators,
            'generated_at': now.isoformat()
        }


# Global instance
_user_limit_manager: Optional[UserLimitManager] = None

def get_user_limit_manager() -> UserLimitManager:
    """Get global user limit manager instance"""
    global _user_limit_manager
    if _user_limit_manager is None:
        _user_limit_manager = UserLimitManager()
    return _user_limit_manager


# Decorator for automatic limit enforcement
def with_user_limits(require_tokens: int = 0, require_cost: float = 0.0):
    """Decorator to automatically enforce user limits"""
    
    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            # Extract user_id from kwargs or args
            user_id = kwargs.get('user_id')
            if not user_id and len(args) > 0:
                # Assume first argument might contain user_id
                if hasattr(args[0], 'get'):
                    user_id = args[0].get('user_id')
            
            if not user_id:
                logger.warning("No user_id found for limit enforcement")
                return await func(*args, **kwargs)
            
            manager = get_user_limit_manager()
            
            # Start session tracking
            manager.start_session(user_id)
            
            try:
                # Check limits
                can_proceed, action, reason = manager.check_usage_limit(
                    user_id, require_tokens, require_cost
                )
                
                if not can_proceed and action == EnforcementAction.BLOCK:
                    return {
                        'error': 'Usage limit exceeded',
                        'reason': reason,
                        'enforcement_action': action.value,
                        'spiritual_message': '🙏 Like Krishna teaches patience, please wait before making another request.'
                    }
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Record actual usage if successful
                if isinstance(result, dict) and 'cost_info' in result:
                    cost_info = result['cost_info']
                    manager.record_usage(
                        user_id,
                        tokens_used=cost_info.get('tokens_used', require_tokens),
                        cost_incurred=cost_info.get('cost', require_cost),
                        queries_count=1
                    )
                else:
                    # Use estimated usage
                    manager.record_usage(user_id, require_tokens, require_cost, 1)
                
                # Add enforcement info to result if not blocked
                if action != EnforcementAction.ALLOW:
                    if isinstance(result, dict):
                        result['enforcement_info'] = {
                            'action': action.value,
                            'reason': reason
                        }
                
                return result
                
            finally:
                manager.end_session(user_id)
        
        def sync_wrapper(*args, **kwargs):
            # Similar logic for sync functions
            user_id = kwargs.get('user_id')
            if not user_id and len(args) > 0:
                if hasattr(args[0], 'get'):
                    user_id = args[0].get('user_id')
            
            if not user_id:
                logger.warning("No user_id found for limit enforcement")
                return func(*args, **kwargs)
            
            manager = get_user_limit_manager()
            manager.start_session(user_id)
            
            try:
                can_proceed, action, reason = manager.check_usage_limit(
                    user_id, require_tokens, require_cost
                )
                
                if not can_proceed and action == EnforcementAction.BLOCK:
                    return {
                        'error': 'Usage limit exceeded',
                        'reason': reason,
                        'enforcement_action': action.value,
                        'spiritual_message': '🙏 Like Krishna teaches patience, please wait before making another request.'
                    }
                
                result = func(*args, **kwargs)
                
                # Record usage
                if isinstance(result, dict) and 'cost_info' in result:
                    cost_info = result['cost_info']
                    manager.record_usage(
                        user_id,
                        tokens_used=cost_info.get('tokens_used', require_tokens),
                        cost_incurred=cost_info.get('cost', require_cost),
                        queries_count=1
                    )
                else:
                    manager.record_usage(user_id, require_tokens, require_cost, 1)
                
                if action != EnforcementAction.ALLOW:
                    if isinstance(result, dict):
                        result['enforcement_info'] = {
                            'action': action.value,
                            'reason': reason
                        }
                
                return result
                
            finally:
                manager.end_session(user_id)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Example usage and testing
if __name__ == "__main__":
    async def test_user_limits():
        print("🕉️ Testing Per-User AI Usage Limits")
        print("=" * 60)
        
        manager = UserLimitManager()
        
        print("1. Creating user profiles...")
        
        # Create different types of users
        beta_user = manager.create_user_profile("beta_user_001", UserTier.BETA)
        vip_user = manager.create_user_profile("vip_user_001", UserTier.VIP)
        free_user = manager.create_user_profile("free_user_001", UserTier.FREE)
        
        print(f"   Created profiles for 3 users")
        
        print("\n2. Testing usage limits...")
        
        # Test free user hitting limits
        for i in range(25):  # More than 20 queries/hour limit
            can_proceed, action, reason = manager.check_usage_limit("free_user_001", queries_requested=1)
            if not can_proceed:
                print(f"   Free user blocked after {i} queries: {reason}")
                break
        
        # Test beta user with high cost
        can_proceed, action, reason = manager.check_usage_limit("beta_user_001", cost_requested=6.0)  # Above $5 daily limit
        print(f"   Beta user high cost check: {action.value} - {reason}")
        
        print("\n3. Testing admin overrides...")
        
        # Add unlimited override for VIP user
        manager.add_admin_override(
            "vip_user_001", 
            "unlimited_access", 
            True, 
            duration_hours=24,
            reason="VIP customer support"
        )
        
        # Test VIP user with override
        can_proceed, action, reason = manager.check_usage_limit("vip_user_001", cost_requested=100.0)
        print(f"   VIP user with override: {action.value} - {reason}")
        
        print("\n4. Usage statistics...")
        
        # Record some usage
        manager.record_usage("beta_user_001", tokens_used=1000, cost_incurred=0.5, queries_count=5)
        
        stats = manager.get_user_usage_stats("beta_user_001")
        if stats:
            print(f"   Beta user tier: {stats['tier']}")
            print(f"   Recent attempts: {stats['recent_attempts']}")
            print(f"   Failed attempts: {stats['failed_attempts']}")
            
            for limit_type, data in stats['usage_stats'].items():
                print(f"   {limit_type}: {data['current']:.1f}/{data['limit']} ({data['percentage']:.1f}%)")
        
        print("\n5. Admin dashboard...")
        
        dashboard = manager.get_admin_dashboard()
        print(f"   Total users: {dashboard['total_users']}")
        print(f"   Active users (24h): {dashboard['active_users_24h']}")
        print(f"   Tier distribution: {dashboard['tier_distribution']}")
        print(f"   Failed attempts (24h): {dashboard['failed_attempts_24h']}")
        
        print("\n✅ User limits testing completed!")
    
    asyncio.run(test_user_limits())
