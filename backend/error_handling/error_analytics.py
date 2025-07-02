"""
Error Analytics and Pattern Learning System for Vimarsh AI Agent

This module provides comprehensive error analytics, pattern detection,
and learning capabilities to improve system reliability and user experience.
"""

import asyncio
import json
import logging
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
import statistics
import re

try:
    from .error_classifier import ErrorClassifier, ErrorCategory, ErrorSeverity, ErrorContext
except ImportError:
    from .error_classifier import ErrorClassifier, ErrorCategory, ErrorSeverity, ErrorContext


class AnalyticsMetric(Enum):
    """Types of analytics metrics to track"""
    ERROR_FREQUENCY = "error_frequency"
    ERROR_PATTERNS = "error_patterns"
    RECOVERY_SUCCESS_RATE = "recovery_success_rate"
    USER_IMPACT = "user_impact"
    SYSTEM_HEALTH = "system_health"
    PERFORMANCE_DEGRADATION = "performance_degradation"


@dataclass
class ErrorEvent:
    """Represents a single error event for analytics"""
    timestamp: datetime
    error_type: str
    category: ErrorCategory
    severity: ErrorSeverity
    component: str
    message: str
    context: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    user_impact_score: float = 0.0
    resolution_time: Optional[float] = None


@dataclass
class ErrorPattern:
    """Represents a detected error pattern"""
    pattern_id: str
    description: str
    frequency: int
    first_seen: datetime
    last_seen: datetime
    affected_components: Set[str]
    common_contexts: List[Dict[str, Any]]
    severity_distribution: Dict[ErrorSeverity, int]
    suggested_actions: List[str]
    confidence_score: float


@dataclass
class SystemHealthMetrics:
    """System health metrics derived from error analytics"""
    overall_health_score: float  # 0-100
    error_rate: float  # errors per minute
    mean_recovery_time: float
    critical_error_count: int
    user_impact_score: float
    top_error_categories: List[Tuple[ErrorCategory, int]]
    trending_issues: List[str]
    reliability_score: float


class ErrorAnalytics:
    """
    Advanced error analytics and pattern learning system
    """
    
    def __init__(self, 
                 storage_path: Optional[str] = None,
                 max_events: int = 10000,
                 pattern_detection_window: int = 24):
        """
        Initialize error analytics system
        
        Args:
            storage_path: Path to store analytics data
            max_events: Maximum number of events to keep in memory
            pattern_detection_window: Hours to look back for pattern detection
        """
        self.classifier = ErrorClassifier()
        self.storage_path = Path(storage_path) if storage_path else Path("error_analytics")
        self.storage_path.mkdir(exist_ok=True)
        
        self.max_events = max_events
        self.pattern_detection_window = pattern_detection_window
        
        # In-memory storage for recent events
        self.recent_events: List[ErrorEvent] = []
        self.detected_patterns: Dict[str, ErrorPattern] = {}
        
        # Analytics caches
        self._metrics_cache: Dict[str, Any] = {}
        self._cache_timestamp = datetime.now() - timedelta(minutes=10)  # Start invalid
        self._cache_ttl = timedelta(minutes=5)
        
        self.logger = logging.getLogger(__name__)
        
        # Load existing data
        self._load_patterns()
    
    async def record_error(self, 
                          error: Exception,
                          component: str,
                          context: Dict[str, Any],
                          user_id: Optional[str] = None,
                          session_id: Optional[str] = None) -> ErrorEvent:
        """
        Record a new error event for analytics
        
        Args:
            error: The exception that occurred
            component: Component where error occurred
            context: Additional context information
            user_id: Optional user identifier
            session_id: Optional session identifier
            
        Returns:
            ErrorEvent: The recorded error event
        """
        try:
            # Create ErrorContext object for the classifier
            error_context = ErrorContext(
                user_id=user_id,
                session_id=session_id,
                request_id=context.get('request_id'),
                operation=context.get('operation', component),
                endpoint=context.get('endpoint'),
                user_agent=context.get('user_agent'),
                ip_address=context.get('ip_address'),
                additional_data=context
            )
            
            # Classify the error
            classification = self.classifier.classify_error(error, error_context)
            
            # Calculate user impact score
            impact_score = self._calculate_user_impact(
                classification.severity, 
                classification.category,
                context
            )
            
            # Create error event
            event = ErrorEvent(
                timestamp=datetime.now(),
                error_type=type(error).__name__,
                category=classification.category,
                severity=classification.severity,
                component=component,
                message=str(error),
                context=context.copy(),
                user_id=user_id,
                session_id=session_id,
                user_impact_score=impact_score
            )
            
            # Store event
            await self._store_event(event)
            
            # Detect patterns asynchronously
            asyncio.create_task(self._detect_patterns())
            
            return event
            
        except Exception as e:
            self.logger.error(f"Failed to record error event: {e}")
            # Return a minimal event if recording fails
            return ErrorEvent(
                timestamp=datetime.now(),
                error_type=type(error).__name__,
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.LOW,
                component=component,
                message=str(error),
                context=context,
                user_id=user_id,
                session_id=session_id
            )
    
    async def record_recovery_attempt(self, 
                                    event_id: str,
                                    recovery_successful: bool,
                                    recovery_time: float,
                                    recovery_method: str):
        """
        Record recovery attempt for an error event
        
        Args:
            event_id: ID of the original error event
            recovery_successful: Whether recovery was successful
            recovery_time: Time taken for recovery (seconds)
            recovery_method: Method used for recovery
        """
        try:
            # Find the event (simplified - would use proper ID lookup in production)
            for event in self.recent_events:
                if (event.timestamp.isoformat() == event_id or 
                    f"{event.component}_{event.timestamp.timestamp()}" == event_id):
                    event.recovery_attempted = True
                    event.recovery_successful = recovery_successful
                    event.resolution_time = recovery_time
                    event.context['recovery_method'] = recovery_method
                    break
                    
        except Exception as e:
            self.logger.error(f"Failed to record recovery attempt: {e}")
    
    async def get_system_health(self) -> SystemHealthMetrics:
        """
        Get current system health metrics
        
        Returns:
            SystemHealthMetrics: Current system health
        """
        try:
            # Check cache
            if self._is_cache_valid() and 'system_health' in self._metrics_cache:
                return self._metrics_cache['system_health']
            
            now = datetime.now()
            last_hour = now - timedelta(hours=1)
            last_day = now - timedelta(days=1)
            
            # Get recent events
            recent_events = [e for e in self.recent_events if e.timestamp > last_hour]
            daily_events = [e for e in self.recent_events if e.timestamp > last_day]
            
            # Calculate metrics
            error_rate = len(recent_events) / 60.0  # errors per minute
            
            critical_errors = [e for e in recent_events 
                             if e.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]]
            critical_count = len(critical_errors)
            
            # Recovery metrics
            recovery_events = [e for e in daily_events if e.recovery_attempted]
            if recovery_events:
                successful_recoveries = [e for e in recovery_events if e.recovery_successful]
                recovery_times = [e.resolution_time for e in recovery_events 
                                if e.resolution_time is not None]
                mean_recovery_time = statistics.mean(recovery_times) if recovery_times else 0.0
            else:
                mean_recovery_time = 0.0
            
            # User impact
            user_impact = statistics.mean([e.user_impact_score for e in recent_events]) if recent_events else 0.0
            
            # Category distribution
            category_counts = Counter(e.category for e in daily_events)
            top_categories = category_counts.most_common(5)
            
            # Overall health score (0-100)
            health_score = self._calculate_health_score(
                error_rate, critical_count, user_impact, len(recent_events)
            )
            
            # Reliability score
            reliability_score = self._calculate_reliability_score(daily_events)
            
            # Trending issues
            trending = await self._identify_trending_issues()
            
            metrics = SystemHealthMetrics(
                overall_health_score=health_score,
                error_rate=error_rate,
                mean_recovery_time=mean_recovery_time,
                critical_error_count=critical_count,
                user_impact_score=user_impact,
                top_error_categories=top_categories,
                trending_issues=trending,
                reliability_score=reliability_score
            )
            
            # Cache the result
            self._metrics_cache['system_health'] = metrics
            self._cache_timestamp = now
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to calculate system health: {e}")
            # Return default metrics on failure
            return SystemHealthMetrics(
                overall_health_score=50.0,
                error_rate=0.0,
                mean_recovery_time=0.0,
                critical_error_count=0,
                user_impact_score=0.0,
                top_error_categories=[],
                trending_issues=[],
                reliability_score=50.0
            )
    
    async def get_error_patterns(self, 
                               min_frequency: int = 3,
                               min_confidence: float = 0.7) -> List[ErrorPattern]:
        """
        Get detected error patterns
        
        Args:
            min_frequency: Minimum frequency for pattern inclusion
            min_confidence: Minimum confidence score for pattern inclusion
            
        Returns:
            List[ErrorPattern]: Detected patterns matching criteria
        """
        try:
            patterns = []
            for pattern in self.detected_patterns.values():
                if (pattern.frequency >= min_frequency and 
                    pattern.confidence_score >= min_confidence):
                    patterns.append(pattern)
            
            # Sort by frequency and confidence
            patterns.sort(key=lambda p: (p.frequency, p.confidence_score), reverse=True)
            return patterns
            
        except Exception as e:
            self.logger.error(f"Failed to get error patterns: {e}")
            return []
    
    async def get_analytics_report(self, 
                                 time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report
        
        Args:
            time_range: Time range for the report (default: last 24 hours)
            
        Returns:
            Dict[str, Any]: Comprehensive analytics report
        """
        try:
            if time_range is None:
                time_range = timedelta(days=1)
            
            cutoff_time = datetime.now() - time_range
            relevant_events = [e for e in self.recent_events if e.timestamp > cutoff_time]
            
            # Basic statistics
            total_errors = len(relevant_events)
            unique_error_types = len(set(e.error_type for e in relevant_events))
            affected_components = len(set(e.component for e in relevant_events))
            
            # Severity distribution
            severity_dist = Counter(e.severity for e in relevant_events)
            
            # Category distribution
            category_dist = Counter(e.category for e in relevant_events)
            
            # Temporal patterns
            hourly_counts = defaultdict(int)
            for event in relevant_events:
                hour = event.timestamp.hour
                hourly_counts[hour] += 1
            
            # Component analysis
            component_errors = defaultdict(int)
            component_severity = defaultdict(list)
            for event in relevant_events:
                component_errors[event.component] += 1
                component_severity[event.component].append(event.severity)
            
            # Recovery analysis
            recovery_attempted = sum(1 for e in relevant_events if e.recovery_attempted)
            recovery_successful = sum(1 for e in relevant_events if e.recovery_successful)
            recovery_rate = (recovery_successful / recovery_attempted * 100) if recovery_attempted > 0 else 0
            
            # Get system health and patterns
            health_metrics = await self.get_system_health()
            patterns = await self.get_error_patterns()
            
            return {
                'report_period': {
                    'start_time': cutoff_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'duration_hours': time_range.total_seconds() / 3600
                },
                'summary': {
                    'total_errors': total_errors,
                    'unique_error_types': unique_error_types,
                    'affected_components': affected_components,
                    'recovery_rate_percent': recovery_rate
                },
                'distributions': {
                    'severity': dict(severity_dist),
                    'category': dict(category_dist),
                    'hourly_pattern': dict(hourly_counts)
                },
                'component_analysis': {
                    'error_counts': dict(component_errors),
                    'most_problematic': sorted(component_errors.items(), 
                                             key=lambda x: x[1], reverse=True)[:5]
                },
                'system_health': asdict(health_metrics),
                'detected_patterns': [asdict(p) for p in patterns[:10]],
                'recommendations': await self._generate_recommendations(relevant_events, patterns)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate analytics report: {e}")
            return {
                'error': f"Failed to generate report: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    async def _detect_patterns(self):
        """Detect error patterns in recent events"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.pattern_detection_window)
            recent_events = [e for e in self.recent_events if e.timestamp > cutoff_time]
            
            if len(recent_events) < 3:
                return
            
            # Group by error type and component
            groups = defaultdict(list)
            for event in recent_events:
                key = f"{event.error_type}_{event.component}"
                groups[key].append(event)
            
            # Analyze each group for patterns
            for group_key, events in groups.items():
                if len(events) >= 3:  # Minimum frequency for pattern
                    await self._analyze_event_group(group_key, events)
                    
        except Exception as e:
            self.logger.error(f"Failed to detect patterns: {e}")
    
    async def _analyze_event_group(self, group_key: str, events: List[ErrorEvent]):
        """Analyze a group of similar events for patterns"""
        try:
            if not events:
                return
            
            # Calculate pattern metrics
            frequency = len(events)
            first_seen = min(e.timestamp for e in events)
            last_seen = max(e.timestamp for e in events)
            
            affected_components = set(e.component for e in events)
            severity_dist = Counter(e.severity for e in events)
            
            # Analyze common contexts
            common_contexts = self._find_common_contexts(events)
            
            # Generate pattern description
            primary_error = events[0]
            description = f"Recurring {primary_error.error_type} in {primary_error.component}"
            
            # Calculate confidence score
            confidence = self._calculate_pattern_confidence(events)
            
            # Generate suggested actions
            suggestions = self._generate_pattern_suggestions(events, severity_dist)
            
            # Create or update pattern
            pattern = ErrorPattern(
                pattern_id=group_key,
                description=description,
                frequency=frequency,
                first_seen=first_seen,
                last_seen=last_seen,
                affected_components=affected_components,
                common_contexts=common_contexts,
                severity_distribution=severity_dist,
                suggested_actions=suggestions,
                confidence_score=confidence
            )
            
            self.detected_patterns[group_key] = pattern
            
            # Save pattern to storage
            await self._save_pattern(pattern)
            
        except Exception as e:
            self.logger.error(f"Failed to analyze event group {group_key}: {e}")
    
    def _find_common_contexts(self, events: List[ErrorEvent]) -> List[Dict[str, Any]]:
        """Find common context patterns in events"""
        try:
            context_keys = set()
            for event in events:
                context_keys.update(event.context.keys())
            
            common_contexts = []
            for key in context_keys:
                values = [event.context.get(key) for event in events 
                         if key in event.context]
                if len(values) >= len(events) * 0.6:  # Present in 60% of events
                    value_counts = Counter(str(v) for v in values if v is not None)
                    most_common = value_counts.most_common(1)
                    if most_common and most_common[0][1] >= 2:
                        common_contexts.append({
                            'key': key,
                            'value': most_common[0][0],
                            'frequency': most_common[0][1]
                        })
            
            return common_contexts
            
        except Exception as e:
            self.logger.error(f"Failed to find common contexts: {e}")
            return []
    
    def _calculate_pattern_confidence(self, events: List[ErrorEvent]) -> float:
        """Calculate confidence score for a pattern"""
        try:
            if not events:
                return 0.0
            
            # Factors affecting confidence
            frequency_score = min(len(events) / 10.0, 1.0)  # Max at 10 events
            
            # Time distribution (more spread = higher confidence)
            time_span = (max(e.timestamp for e in events) - 
                        min(e.timestamp for e in events)).total_seconds()
            time_score = min(time_span / (24 * 3600), 1.0)  # Max at 24 hours
            
            # Context consistency
            context_score = len(self._find_common_contexts(events)) / 5.0
            context_score = min(context_score, 1.0)
            
            # Severity consistency
            severity_types = len(set(e.severity for e in events))
            severity_score = 1.0 / severity_types if severity_types > 0 else 0.0
            
            # Weighted average
            confidence = (frequency_score * 0.4 + 
                         time_score * 0.2 + 
                         context_score * 0.3 + 
                         severity_score * 0.1)
            
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate pattern confidence: {e}")
            return 0.5
    
    def _generate_pattern_suggestions(self, 
                                    events: List[ErrorEvent],
                                    severity_dist: Counter) -> List[str]:
        """Generate suggested actions for a pattern"""
        try:
            suggestions = []
            
            # High severity patterns
            if any(s in severity_dist for s in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]):
                suggestions.append("Prioritize immediate investigation due to high severity")
                suggestions.append("Consider implementing circuit breaker for affected component")
            
            # Frequent patterns
            if len(events) >= 10:
                suggestions.append("Implement proactive monitoring for this error pattern")
                suggestions.append("Consider root cause analysis to prevent recurrence")
            
            # Component-specific suggestions
            component = events[0].component
            if 'llm' in component.lower():
                suggestions.append("Review LLM prompt engineering and fallback mechanisms")
            elif 'database' in component.lower() or 'vector' in component.lower():
                suggestions.append("Check database connection pooling and retry policies")
            elif 'auth' in component.lower():
                suggestions.append("Review authentication configuration and token handling")
            
            # Context-specific suggestions
            common_contexts = self._find_common_contexts(events)
            for context in common_contexts:
                if context['key'] == 'user_input' and context['frequency'] >= 3:
                    suggestions.append("Consider input validation improvements")
                elif context['key'] == 'rate_limit' and context['frequency'] >= 2:
                    suggestions.append("Review rate limiting configuration")
            
            return suggestions[:5]  # Limit to top 5 suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to generate pattern suggestions: {e}")
            return ["Manual investigation recommended"]
    
    def _calculate_user_impact(self, 
                             severity: ErrorSeverity,
                             category: ErrorCategory,
                             context: Dict[str, Any]) -> float:
        """Calculate user impact score (0-10)"""
        try:
            # Base score from severity
            severity_scores = {
                ErrorSeverity.CRITICAL: 9.0,
                ErrorSeverity.HIGH: 7.0,
                ErrorSeverity.MEDIUM: 4.0,
                ErrorSeverity.LOW: 2.0
            }
            base_score = severity_scores.get(severity, 3.0)
            
            # Category multipliers
            category_multipliers = {
                ErrorCategory.LLM_SERVICE: 1.2,
                ErrorCategory.AUTHENTICATION: 1.5,
                ErrorCategory.INPUT_VALIDATION: 0.8,
                ErrorCategory.NETWORK: 1.1,
                ErrorCategory.RATE_LIMITING: 0.7
            }
            multiplier = category_multipliers.get(category, 1.0)
            
            # Context adjustments
            if context.get('user_visible', False):
                multiplier *= 1.3
            if context.get('session_interrupted', False):
                multiplier *= 1.4
            if context.get('data_loss', False):
                multiplier *= 1.6
            
            impact_score = base_score * multiplier
            return min(max(impact_score, 0.0), 10.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate user impact: {e}")
            return 5.0  # Default moderate impact
    
    def _calculate_health_score(self, 
                              error_rate: float,
                              critical_count: int,
                              user_impact: float,
                              total_errors: int) -> float:
        """Calculate overall system health score (0-100)"""
        try:
            # Start with perfect health
            health = 100.0
            
            # Deduct for error rate (errors per minute)
            if error_rate > 0:
                health -= min(error_rate * 5, 30)  # Max 30 point deduction
            
            # Deduct for critical errors
            health -= min(critical_count * 10, 40)  # Max 40 point deduction
            
            # Deduct for user impact
            health -= min(user_impact * 3, 20)  # Max 20 point deduction
            
            # Deduct for total error volume
            if total_errors > 10:
                health -= min((total_errors - 10) * 0.5, 10)  # Max 10 point deduction
            
            return max(health, 0.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate health score: {e}")
            return 50.0
    
    def _calculate_reliability_score(self, events: List[ErrorEvent]) -> float:
        """Calculate system reliability score based on historical data"""
        try:
            if not events:
                return 100.0
            
            # Calculate uptime (inverse of error frequency)
            total_hours = 24  # Last 24 hours
            error_hours = len(set(e.timestamp.hour for e in events))
            uptime_score = ((total_hours - error_hours) / total_hours) * 100
            
            # Factor in recovery success rate
            recovery_events = [e for e in events if e.recovery_attempted]
            if recovery_events:
                successful_recoveries = sum(1 for e in recovery_events if e.recovery_successful)
                recovery_rate = successful_recoveries / len(recovery_events)
                recovery_score = recovery_rate * 100
            else:
                recovery_score = 100.0  # No recovery needed is good
            
            # Weighted average
            reliability = (uptime_score * 0.7 + recovery_score * 0.3)
            return min(max(reliability, 0.0), 100.0)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate reliability score: {e}")
            return 50.0
    
    async def _identify_trending_issues(self) -> List[str]:
        """Identify trending issues in the last few hours"""
        try:
            now = datetime.now()
            recent = now - timedelta(hours=2)
            older = now - timedelta(hours=6)
            
            recent_events = [e for e in self.recent_events if e.timestamp > recent]
            older_events = [e for e in self.recent_events if older < e.timestamp <= recent]
            
            # Count error types in both periods
            recent_counts = Counter(f"{e.error_type}_{e.component}" for e in recent_events)
            older_counts = Counter(f"{e.error_type}_{e.component}" for e in older_events)
            
            trending = []
            for error_key, recent_count in recent_counts.items():
                older_count = older_counts.get(error_key, 0)
                if recent_count > older_count * 2 and recent_count >= 3:
                    trending.append(error_key.replace('_', ' in '))
            
            return trending[:5]  # Top 5 trending issues
            
        except Exception as e:
            self.logger.error(f"Failed to identify trending issues: {e}")
            return []
    
    async def _generate_recommendations(self, 
                                      events: List[ErrorEvent],
                                      patterns: List[ErrorPattern]) -> List[str]:
        """Generate actionable recommendations based on analytics"""
        try:
            recommendations = []
            
            # High-level recommendations
            if len(events) > 50:
                recommendations.append("Consider implementing more aggressive rate limiting")
            
            critical_events = [e for e in events if e.severity == ErrorSeverity.CRITICAL]
            if len(critical_events) > 5:
                recommendations.append("Immediate attention required: Multiple critical errors detected")
            
            # Pattern-based recommendations
            high_confidence_patterns = [p for p in patterns if p.confidence_score > 0.8]
            if high_confidence_patterns:
                recommendations.append(f"Address {len(high_confidence_patterns)} high-confidence error patterns")
            
            # Component-specific recommendations
            component_counts = Counter(e.component for e in events)
            if component_counts:
                most_problematic = component_counts.most_common(1)[0]
                if most_problematic[1] > 10:
                    recommendations.append(f"Focus on {most_problematic[0]} component stability")
            
            # Recovery recommendations
            recovery_events = [e for e in events if e.recovery_attempted]
            if recovery_events:
                failed_recoveries = [e for e in recovery_events if not e.recovery_successful]
                if len(failed_recoveries) > len(recovery_events) * 0.3:
                    recommendations.append("Improve error recovery mechanisms")
            
            return recommendations[:5]  # Top 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return ["Manual system review recommended"]
    
    async def _store_event(self, event: ErrorEvent):
        """Store error event in memory and persistent storage"""
        try:
            # Add to in-memory storage
            self.recent_events.append(event)
            
            # Maintain size limit
            if len(self.recent_events) > self.max_events:
                self.recent_events = self.recent_events[-self.max_events:]
            
            # Store to file (simplified - would use proper database in production)
            events_file = self.storage_path / "events.jsonl"
            with open(events_file, "a") as f:
                event_dict = asdict(event)
                # Convert datetime and enums to strings for JSON serialization
                event_dict['timestamp'] = event.timestamp.isoformat()
                event_dict['category'] = event.category.value
                event_dict['severity'] = event.severity.value
                f.write(json.dumps(event_dict) + "\n")
                
        except Exception as e:
            self.logger.error(f"Failed to store event: {e}")
    
    async def _save_pattern(self, pattern: ErrorPattern):
        """Save detected pattern to persistent storage"""
        try:
            patterns_file = self.storage_path / "patterns.json"
            
            # Load existing patterns
            if patterns_file.exists():
                with open(patterns_file, "r") as f:
                    patterns_data = json.load(f)
            else:
                patterns_data = {}
            
            # Add/update pattern
            pattern_dict = asdict(pattern)
            # Convert datetime and set to serializable formats
            pattern_dict['first_seen'] = pattern.first_seen.isoformat()
            pattern_dict['last_seen'] = pattern.last_seen.isoformat()
            pattern_dict['affected_components'] = list(pattern.affected_components)
            
            # Convert severity distribution enum keys to strings
            severity_dist = {}
            for severity, count in pattern.severity_distribution.items():
                severity_dist[severity.value] = count
            pattern_dict['severity_distribution'] = severity_dist
            
            patterns_data[pattern.pattern_id] = pattern_dict
            
            # Save back to file
            with open(patterns_file, "w") as f:
                json.dump(patterns_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save pattern: {e}")
    
    def _load_patterns(self):
        """Load existing patterns from storage"""
        try:
            patterns_file = self.storage_path / "patterns.json"
            if not patterns_file.exists():
                return
            
            with open(patterns_file, "r") as f:
                patterns_data = json.load(f)
            
            for pattern_id, pattern_dict in patterns_data.items():
                # Convert back from serialized format
                pattern_dict['first_seen'] = datetime.fromisoformat(pattern_dict['first_seen'])
                pattern_dict['last_seen'] = datetime.fromisoformat(pattern_dict['last_seen'])
                pattern_dict['affected_components'] = set(pattern_dict['affected_components'])
                
                # Reconstruct severity distribution with enum keys
                severity_dist = {}
                for severity_str, count in pattern_dict['severity_distribution'].items():
                    try:
                        severity = ErrorSeverity(severity_str)
                        severity_dist[severity] = count
                    except ValueError:
                        continue
                pattern_dict['severity_distribution'] = severity_dist
                
                pattern = ErrorPattern(**pattern_dict)
                self.detected_patterns[pattern_id] = pattern
                
        except Exception as e:
            self.logger.error(f"Failed to load patterns: {e}")
    
    def _is_cache_valid(self) -> bool:
        """Check if metrics cache is still valid"""
        return datetime.now() - self._cache_timestamp < self._cache_ttl
    
    async def cleanup_old_data(self, retention_days: int = 7):
        """Clean up old analytics data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Clean in-memory events
            self.recent_events = [e for e in self.recent_events if e.timestamp > cutoff_date]
            
            # Clean patterns
            old_patterns = []
            for pattern_id, pattern in self.detected_patterns.items():
                if pattern.last_seen < cutoff_date:
                    old_patterns.append(pattern_id)
            
            for pattern_id in old_patterns:
                del self.detected_patterns[pattern_id]
            
            self.logger.info(f"Cleaned up data older than {retention_days} days")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
