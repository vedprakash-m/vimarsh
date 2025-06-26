"""
Graceful Degradation with User Notification System
Task 7.7: Enhanced AI Cost Management & Dynamic Fallbacks

This module provides comprehensive graceful degradation capabilities with
user-friendly notifications for various service failure scenarios.

Features:
- Multi-level degradation strategies
- Context-aware user notifications
- Service health monitoring
- Recovery detection and notification
- Cultural sensitivity in messaging
- Integration with existing cost management systems
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum, IntEnum
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DegradationLevel(IntEnum):
    """Service degradation levels"""
    NORMAL = 0
    MINOR = 1  # Slight delays, some features limited
    MODERATE = 2  # Significant limitations, basic functionality only
    SEVERE = 3  # Core features compromised, emergency responses
    CRITICAL = 4  # Service largely unavailable


class ServiceComponent(Enum):
    """Service components that can degrade"""
    LLM_SERVICE = "llm_service"
    VECTOR_SEARCH = "vector_search"
    VOICE_INTERFACE = "voice_interface"
    AUTHENTICATION = "authentication"
    COST_MANAGEMENT = "cost_management"
    EXPERT_REVIEW = "expert_review"
    CITATION_SYSTEM = "citation_system"


class NotificationType(Enum):
    """Types of user notifications"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    SPIRITUAL_GUIDANCE = "spiritual_guidance"


@dataclass
class DegradationStatus:
    """Current degradation status"""
    level: DegradationLevel
    affected_components: List[ServiceComponent]
    timestamp: datetime
    reason: str
    estimated_recovery: Optional[datetime] = None
    user_message: str = ""
    technical_details: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = {
            'level': self.level.name.lower(),
            'affected_components': [c.value for c in self.affected_components],
            'timestamp': self.timestamp.isoformat(),
            'reason': self.reason,
            'user_message': self.user_message,
            'technical_details': self.technical_details or {}
        }
        if self.estimated_recovery:
            data['estimated_recovery'] = self.estimated_recovery.isoformat()
        return data


@dataclass
class UserNotification:
    """User notification message"""
    id: str
    type: NotificationType
    title: str
    message: str
    spiritual_message: Optional[str] = None
    timestamp: datetime = None
    actions: List[Dict[str, str]] = None
    dismissible: bool = True
    auto_dismiss_after: Optional[int] = None  # seconds
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.actions is None:
            self.actions = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        data = asdict(self)
        data['type'] = self.type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class SpiritualMessageGenerator:
    """Generates culturally appropriate spiritual messages for degradation scenarios"""
    
    def __init__(self):
        self.messages = {
            DegradationLevel.MINOR: [
                "🕉️ Like the gentle flow of the Ganges, our service continues with patience and devotion.",
                "🙏 As Lord Krishna teaches, perform your duties without attachment to results. We are working to restore full service.",
                "📿 In this moment of slight delay, practice patience - a virtue praised in the Bhagavad Gita."
            ],
            DegradationLevel.MODERATE: [
                "🧘‍♂️ Even the mightiest rivers face obstacles. Like Krishna's guidance to Arjuna, we navigate challenges with wisdom.",
                "🌸 As lotus flowers bloom in muddy waters, we shall emerge stronger. Basic guidance remains available.",
                "⚡ Like Hanuman's unwavering devotion, we persist in serving you despite temporary limitations."
            ],
            DegradationLevel.SEVERE: [
                "🛡️ In times of great challenge, remember Arjuna's courage as taught in the Gita. We provide essential guidance while restoring service.",
                "🔥 As gold is purified in fire, our service strengthens through trials. Your soul's journey continues with divine support.",
                "💫 The divine light within remains constant even when external circumstances change."
            ],
            DegradationLevel.CRITICAL: [
                "🌟 In the darkest night, stars shine brightest. Though service is limited, the eternal dharma endures.",
                "🙏 Like devotees maintaining faith during storms, we work with Krishna's grace for your spiritual journey.",
                "⭐ Remember the unchanging truth of the Bhagavad Gita: 'For the soul there is neither birth nor death.'"
            ]
        }
    
    def get_message(self, level: DegradationLevel) -> str:
        """Get appropriate spiritual message for degradation level"""
        import random
        messages = self.messages.get(level, self.messages[DegradationLevel.MINOR])
        return random.choice(messages)


class GracefulDegradationManager:
    """Manages graceful degradation and user notifications"""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize graceful degradation manager
        
        Args:
            storage_path: Path to store degradation status and notifications
        """
        self.storage_path = Path(storage_path) if storage_path else Path("data/degradation")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Current state
        self.current_status = DegradationStatus(
            level=DegradationLevel.NORMAL,
            affected_components=[],
            timestamp=datetime.now(),
            reason="Service operating normally"
        )
        
        # Notification management
        self.active_notifications: Dict[str, UserNotification] = {}
        self.notification_history: List[UserNotification] = []
        self.spiritual_messenger = SpiritualMessageGenerator()
        
        # Component health tracking
        self.component_health: Dict[ServiceComponent, Dict[str, Any]] = {}
        self.degradation_rules: Dict[ServiceComponent, Dict[str, Any]] = {}
        
        # Threading
        self.lock = threading.Lock()
        
        # Auto-recovery monitoring
        self.recovery_tasks: Dict[str, asyncio.Task] = {}
        
        self._initialize_component_health()
        self._load_persistent_state()
    
    def _initialize_component_health(self):
        """Initialize component health tracking"""
        for component in ServiceComponent:
            self.component_health[component] = {
                'status': 'healthy',
                'last_check': datetime.now(),
                'error_count': 0,
                'response_time': 0.0,
                'success_rate': 100.0
            }
            
            # Define degradation rules for each component
            self.degradation_rules[component] = {
                'error_threshold_minor': 5,
                'error_threshold_moderate': 15,
                'error_threshold_severe': 30,
                'response_time_threshold': 5.0,
                'success_rate_threshold': 80.0
            }
    
    def _load_persistent_state(self):
        """Load degradation state from persistent storage"""
        try:
            status_file = self.storage_path / "current_status.json"
            if status_file.exists():
                with open(status_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct status from saved data
                    self.current_status = DegradationStatus(
                        level=DegradationLevel(data['level']),
                        affected_components=[ServiceComponent(c) for c in data['affected_components']],
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        reason=data['reason'],
                        estimated_recovery=datetime.fromisoformat(data['estimated_recovery']) if data.get('estimated_recovery') else None,
                        user_message=data.get('user_message', ''),
                        technical_details=data.get('technical_details', {})
                    )
        except Exception as e:
            logger.warning(f"Could not load persistent state: {e}")
    
    def _save_persistent_state(self):
        """Save degradation state to persistent storage"""
        try:
            status_file = self.storage_path / "current_status.json"
            with open(status_file, 'w') as f:
                json.dump(self.current_status.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Could not save persistent state: {e}")
    
    def update_component_health(self, 
                              component: ServiceComponent,
                              error_occurred: bool = False,
                              response_time: float = 0.0,
                              success: bool = True):
        """
        Update component health metrics
        
        Args:
            component: Service component
            error_occurred: Whether an error occurred
            response_time: Response time in seconds
            success: Whether operation was successful
        """
        with self.lock:
            health = self.component_health[component]
            
            # Update metrics
            health['last_check'] = datetime.now()
            if error_occurred:
                health['error_count'] += 1
            health['response_time'] = response_time
            
            # Calculate success rate (simple moving average)
            current_rate = health['success_rate']
            health['success_rate'] = (current_rate * 0.9) + (100.0 if success else 0.0) * 0.1
            
            # Check if degradation is needed
            self._evaluate_degradation_needs()
    
    def _evaluate_degradation_needs(self):
        """Evaluate if service degradation is needed based on component health"""
        max_level = DegradationLevel.NORMAL
        affected_components = []
        reasons = []
        
        for component, health in self.component_health.items():
            rules = self.degradation_rules[component]
            component_level = DegradationLevel.NORMAL
            
            # Check error count
            if health['error_count'] >= rules['error_threshold_severe']:
                component_level = DegradationLevel.SEVERE
            elif health['error_count'] >= rules['error_threshold_moderate']:
                component_level = DegradationLevel.MODERATE
            elif health['error_count'] >= rules['error_threshold_minor']:
                component_level = DegradationLevel.MINOR
            
            # Check response time
            if health['response_time'] > rules['response_time_threshold']:
                component_level = max(component_level, DegradationLevel.MINOR)
                reasons.append(f"{component.value} slow response times")
            
            # Check success rate
            if health['success_rate'] < rules['success_rate_threshold']:
                component_level = max(component_level, DegradationLevel.MODERATE)
                reasons.append(f"{component.value} low success rate")
            
            if component_level != DegradationLevel.NORMAL:
                affected_components.append(component)
                max_level = max(max_level, component_level, key=lambda x: list(DegradationLevel).index(x))
        
        # Update degradation if needed
        if max_level != self.current_status.level:
            reason = "; ".join(reasons) if reasons else "Service health improved"
            # Handle both sync and async contexts
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._apply_degradation(max_level, affected_components, reason))
            except RuntimeError:
                # No running loop, apply degradation synchronously for tests
                asyncio.run(self._apply_degradation(max_level, affected_components, reason))
    
    async def _apply_degradation(self, 
                                level: DegradationLevel,
                                affected_components: List[ServiceComponent],
                                reason: str):
        """Apply service degradation and notify users"""
        previous_level = self.current_status.level
        
        # Update status
        self.current_status = DegradationStatus(
            level=level,
            affected_components=affected_components,
            timestamp=datetime.now(),
            reason=reason,
            estimated_recovery=self._estimate_recovery_time(level),
            user_message=self.spiritual_messenger.get_message(level),
            technical_details={
                'component_health': {c.value: self.component_health[c] for c in affected_components},
                'previous_level': previous_level.value
            }
        )
        
        # Save state
        self._save_persistent_state()
        
        # Create user notification
        await self._create_degradation_notification(level, previous_level, reason)
        
        # Start recovery monitoring if degraded
        if level != DegradationLevel.NORMAL:
            await self._start_recovery_monitoring()
        
        logger.info(f"Service degradation updated: {previous_level.value} -> {level.value}")
    
    def _estimate_recovery_time(self, level: DegradationLevel) -> Optional[datetime]:
        """Estimate recovery time based on degradation level"""
        recovery_times = {
            DegradationLevel.MINOR: timedelta(minutes=15),
            DegradationLevel.MODERATE: timedelta(hours=1),
            DegradationLevel.SEVERE: timedelta(hours=4),
            DegradationLevel.CRITICAL: timedelta(hours=12)
        }
        
        if level in recovery_times:
            return datetime.now() + recovery_times[level]
        return None
    
    async def _create_degradation_notification(self, 
                                             current_level: DegradationLevel,
                                             previous_level: DegradationLevel,
                                             reason: str):
        """Create user notification for degradation change"""
        
        if current_level == DegradationLevel.NORMAL:
            # Service recovered
            notification = UserNotification(
                id=f"recovery_{datetime.now().timestamp()}",
                type=NotificationType.SUCCESS,
                title="🌟 Service Restored",
                message="Full spiritual guidance service has been restored. Thank you for your patience.",
                spiritual_message="🙏 Like the dawn after a long night, all services shine brightly once again.",
                auto_dismiss_after=10
            )
        else:
            # Service degraded
            titles = {
                DegradationLevel.MINOR: "🔄 Service Update",
                DegradationLevel.MODERATE: "⚠️ Limited Service",
                DegradationLevel.SEVERE: "🚨 Service Disruption",
                DegradationLevel.CRITICAL: "🆘 Emergency Mode"
            }
            
            messages = {
                DegradationLevel.MINOR: "We're experiencing minor delays. Most features remain available.",
                DegradationLevel.MODERATE: "Some features are temporarily limited while we resolve issues.",
                DegradationLevel.SEVERE: "Service is significantly impacted. Essential features only.",
                DegradationLevel.CRITICAL: "Service is critically limited. Emergency guidance available."
            }
            
            notification_types = {
                DegradationLevel.MINOR: NotificationType.INFO,
                DegradationLevel.MODERATE: NotificationType.WARNING,
                DegradationLevel.SEVERE: NotificationType.ERROR,
                DegradationLevel.CRITICAL: NotificationType.ERROR
            }
            
            actions = []
            if current_level in [DegradationLevel.SEVERE, DegradationLevel.CRITICAL]:
                actions.append({"label": "Emergency Guidance", "action": "emergency_mode"})
            
            notification = UserNotification(
                id=f"degradation_{datetime.now().timestamp()}",
                type=notification_types[current_level],
                title=titles[current_level],
                message=messages[current_level],
                spiritual_message=self.current_status.user_message,
                actions=actions,
                auto_dismiss_after=None if current_level in [DegradationLevel.SEVERE, DegradationLevel.CRITICAL] else 30
            )
        
        await self.add_notification(notification)
    
    async def _start_recovery_monitoring(self):
        """Start monitoring for service recovery"""
        task_id = f"recovery_monitor_{datetime.now().timestamp()}"
        
        async def monitor():
            """Monitor for recovery conditions"""
            while self.current_status.level != DegradationLevel.NORMAL:
                await asyncio.sleep(60)  # Check every minute
                
                # Check if all components are healthy
                all_healthy = True
                for component in self.current_status.affected_components:
                    health = self.component_health[component]
                    rules = self.degradation_rules[component]
                    
                    if (health['error_count'] >= rules['error_threshold_minor'] or
                        health['response_time'] > rules['response_time_threshold'] or
                        health['success_rate'] < rules['success_rate_threshold']):
                        all_healthy = False
                        break
                
                if all_healthy:
                    # Trigger recovery
                    await self._apply_degradation(DegradationLevel.NORMAL, [], "Service health restored")
                    break
        
        # Handle both sync and async contexts
        try:
            loop = asyncio.get_running_loop()
            self.recovery_tasks[task_id] = loop.create_task(monitor())
        except RuntimeError:
            # No running loop, create a thread to run the monitoring
            def run_monitor():
                asyncio.run(monitor())
            thread = threading.Thread(target=run_monitor, daemon=True)
            thread.start()
            # Store thread reference instead of task
            self.recovery_tasks[task_id] = thread
    
    async def add_notification(self, notification: UserNotification):
        """Add notification to active notifications"""
        with self.lock:
            self.active_notifications[notification.id] = notification
            self.notification_history.append(notification)
            
            # Limit history size
            if len(self.notification_history) > 100:
                self.notification_history = self.notification_history[-50:]
        
        # Auto-dismiss if configured
        if notification.auto_dismiss_after:
            await asyncio.sleep(notification.auto_dismiss_after)
            await self.dismiss_notification(notification.id)
        
        logger.info(f"Notification added: {notification.title}")
    
    async def dismiss_notification(self, notification_id: str) -> bool:
        """Dismiss a notification"""
        with self.lock:
            if notification_id in self.active_notifications:
                del self.active_notifications[notification_id]
                logger.info(f"Notification dismissed: {notification_id}")
                return True
            return False
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current degradation status"""
        return self.current_status.to_dict()
    
    def get_active_notifications(self) -> List[Dict[str, Any]]:
        """Get all active notifications"""
        with self.lock:
            return [notification.to_dict() for notification in self.active_notifications.values()]
    
    def get_notification_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get notification history"""
        with self.lock:
            recent = self.notification_history[-limit:] if len(self.notification_history) > limit else self.notification_history
            return [notification.to_dict() for notification in reversed(recent)]
    
    async def force_degradation(self, 
                               level: DegradationLevel,
                               components: List[ServiceComponent],
                               reason: str,
                               duration_minutes: Optional[int] = None):
        """Manually force degradation for testing or emergency situations"""
        await self._apply_degradation(level, components, f"Manual: {reason}")
        
        if duration_minutes:
            # Auto-recovery after specified duration
            async def auto_recover():
                await asyncio.sleep(duration_minutes * 60)
                await self._apply_degradation(DegradationLevel.NORMAL, [], "Manual degradation period ended")
            
            # Handle both sync and async contexts
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(auto_recover())
            except RuntimeError:
                # No running loop, run in a separate thread
                def run_auto_recover():
                    asyncio.run(auto_recover())
                threading.Thread(target=run_auto_recover, daemon=True).start()
    
    def get_component_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all components"""
        with self.lock:
            return {c.value: health.copy() for c, health in self.component_health.items()}
    
    def reset_component_health(self, component: ServiceComponent):
        """Reset health metrics for a component"""
        with self.lock:
            self.component_health[component] = {
                'status': 'healthy',
                'last_check': datetime.now(),
                'error_count': 0,
                'response_time': 0.0,
                'success_rate': 100.0
            }
    
    async def shutdown(self):
        """Gracefully shutdown the degradation manager"""
        # Cancel all recovery tasks
        for task in self.recovery_tasks.values():
            try:
                if hasattr(task, 'cancel'):
                    task.cancel()
                elif hasattr(task, 'join'):
                    # It's a thread, don't try to cancel
                    pass
            except Exception as e:
                logger.warning(f"Could not cancel task during shutdown: {e}")
        
        # Save final state
        self._save_persistent_state()
        
        logger.info("Graceful degradation manager shutdown complete")


# Decorator for automatic degradation monitoring
def with_degradation_monitoring(component: ServiceComponent, 
                               manager: Optional[GracefulDegradationManager] = None):
    """Decorator to automatically monitor function calls for degradation"""
    
    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            nonlocal manager
            if manager is None:
                manager = get_degradation_manager()
            
            start_time = datetime.now()
            try:
                result = await func(*args, **kwargs)
                response_time = (datetime.now() - start_time).total_seconds()
                manager.update_component_health(component, False, response_time, True)
                return result
            except Exception as e:
                response_time = (datetime.now() - start_time).total_seconds()
                manager.update_component_health(component, True, response_time, False)
                raise
        
        def sync_wrapper(*args, **kwargs):
            nonlocal manager
            if manager is None:
                manager = get_degradation_manager()
            
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                response_time = (datetime.now() - start_time).total_seconds()
                manager.update_component_health(component, False, response_time, True)
                return result
            except Exception as e:
                response_time = (datetime.now() - start_time).total_seconds()
                manager.update_component_health(component, True, response_time, False)
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Global instance
_degradation_manager: Optional[GracefulDegradationManager] = None

def get_degradation_manager() -> GracefulDegradationManager:
    """Get global degradation manager instance"""
    global _degradation_manager
    if _degradation_manager is None:
        _degradation_manager = GracefulDegradationManager()
    return _degradation_manager


# Example usage and testing
if __name__ == "__main__":
    async def test_graceful_degradation():
        print("🕉️ Testing Graceful Degradation with User Notifications")
        print("=" * 60)
        
        manager = GracefulDegradationManager()
        
        print("1. Testing normal operation...")
        status = manager.get_current_status()
        print(f"Status: {status['level']}")
        
        print("\n2. Simulating component failures...")
        # Simulate LLM service errors
        for i in range(3):
            manager.update_component_health(ServiceComponent.LLM_SERVICE, error_occurred=True)
        
        print("\n3. Testing manual degradation...")
        await manager.force_degradation(
            DegradationLevel.MODERATE,
            [ServiceComponent.LLM_SERVICE, ServiceComponent.VECTOR_SEARCH],
            "Testing degradation scenarios",
            duration_minutes=1  # Auto-recover after 1 minute
        )
        
        print("\n4. Checking notifications...")
        notifications = manager.get_active_notifications()
        for notification in notifications:
            print(f"📢 {notification['title']}: {notification['message']}")
            if notification.get('spiritual_message'):
                print(f"   🕉️ {notification['spiritual_message']}")
        
        print("\n5. Component health status:")
        health = manager.get_component_health()
        for component, status in health.items():
            print(f"   {component}: {status['status']} (errors: {status['error_count']})")
        
        print("\n6. Waiting for auto-recovery...")
        await asyncio.sleep(65)  # Wait for auto-recovery
        
        final_status = manager.get_current_status()
        print(f"Final status: {final_status['level']}")
        
        await manager.shutdown()
        print("\n✅ Graceful degradation testing completed!")
    
    asyncio.run(test_graceful_degradation())
