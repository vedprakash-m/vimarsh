"""
Comprehensive Error Classification System for Vimarsh AI Agent

This module provides a sophisticated error classification system that categorizes,
analyzes, and provides appropriate handling strategies for different types of
errors that can occur in the spiritual guidance AI system.
"""

import logging
import traceback
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"      # System-breaking, requires immediate attention
    HIGH = "high"             # Major functionality impacted
    MEDIUM = "medium"         # Some functionality affected
    LOW = "low"              # Minor issues, graceful degradation
    INFO = "info"            # Informational, no action needed


class ErrorCategory(Enum):
    """Error categories for classification"""
    # System errors
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    
    # Application errors
    INPUT_VALIDATION = "input_validation"
    BUSINESS_LOGIC = "business_logic"
    DATA_PROCESSING = "data_processing"
    CONFIGURATION = "configuration"
    
    # AI/ML specific errors
    LLM_SERVICE = "llm_service"
    RAG_PIPELINE = "rag_pipeline"
    VECTOR_SEARCH = "vector_search"
    CONTENT_MODERATION = "content_moderation"
    
    # Spiritual guidance specific
    SPIRITUAL_VALIDATION = "spiritual_validation"
    EXPERT_REVIEW = "expert_review"
    CITATION_EXTRACTION = "citation_extraction"
    PERSONA_CONSISTENCY = "persona_consistency"
    
    # User experience errors
    RATE_LIMITING = "rate_limiting"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    
    # System errors
    SYSTEM = "system"
    
    # Unknown/uncategorized
    UNKNOWN = "unknown"


class ErrorSource(Enum):
    """Source of the error"""
    CLIENT = "client"           # User/frontend error
    SERVER = "server"           # Backend/server error
    EXTERNAL = "external"       # External service error
    SYSTEM = "system"          # System/infrastructure error


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types"""
    RETRY = "retry"                      # Retry the operation
    FALLBACK = "fallback"               # Use fallback mechanism
    DEGRADE = "degrade"                 # Graceful degradation
    ESCALATE = "escalate"               # Escalate to human/expert
    FAIL_FAST = "fail_fast"             # Fail immediately
    IGNORE = "ignore"                   # Log but continue
    CIRCUIT_BREAK = "circuit_break"     # Open circuit breaker


@dataclass
class ErrorContext:
    """Context information for error classification"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    operation: Optional[str] = None
    endpoint: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorPattern:
    """Pattern for matching and classifying errors"""
    pattern_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    source: ErrorSource
    recovery_strategy: RecoveryStrategy
    
    # Matching criteria
    exception_types: List[str] = field(default_factory=list)
    message_patterns: List[str] = field(default_factory=list)
    status_codes: List[int] = field(default_factory=list)
    
    # Classification rules
    description: str = ""
    user_message: str = ""
    technical_message: str = ""
    
    # Recovery parameters
    max_retries: int = 0
    retry_delay: float = 1.0
    timeout: float = 30.0
    
    # Monitoring
    alert_threshold: int = 5  # Alert after this many occurrences
    escalation_threshold: int = 10


@dataclass
class ClassifiedError:
    """A classified error with all relevant information"""
    error_id: str
    original_exception: Exception
    category: ErrorCategory
    severity: ErrorSeverity
    source: ErrorSource
    recovery_strategy: RecoveryStrategy
    
    # Messages
    user_message: str
    technical_message: str
    
    # Context
    context: ErrorContext
    
    # Recovery information
    max_retries: int = 0
    retry_delay: float = 1.0
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Pattern matching
    matched_pattern: Optional[str] = None
    confidence: float = 1.0
    
    # Additional metadata
    stack_trace: str = ""
    frequency_count: int = 1
    first_occurrence: datetime = field(default_factory=datetime.now)
    last_occurrence: datetime = field(default_factory=datetime.now)


class ErrorClassifier:
    """Main error classification system"""
    
    def __init__(self):
        self.patterns: Dict[str, ErrorPattern] = {}
        self.error_history: Dict[str, ClassifiedError] = {}
        self.frequency_tracker: Dict[str, List[datetime]] = {}
        self._initialize_default_patterns()
    
    def _initialize_default_patterns(self):
        """Initialize default error patterns"""
        
        # Authentication errors
        self.add_pattern(ErrorPattern(
            pattern_id="auth_token_expired",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.MEDIUM,
            source=ErrorSource.CLIENT,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            exception_types=["TokenExpiredError", "AuthenticationError"],
            message_patterns=["token expired", "authentication failed"],
            status_codes=[401],
            description="Authentication token has expired",
            user_message="Your session has expired. Please log in again.",
            technical_message="Authentication token expired, user needs to re-authenticate",
            max_retries=1
        ))
        
        # LLM service errors
        self.add_pattern(ErrorPattern(
            pattern_id="llm_rate_limit",
            category=ErrorCategory.LLM_SERVICE,
            severity=ErrorSeverity.HIGH,
            source=ErrorSource.EXTERNAL,
            recovery_strategy=RecoveryStrategy.RETRY,
            exception_types=["RateLimitError", "APIError"],
            message_patterns=["rate limit", "quota exceeded", "too many requests"],
            status_codes=[429],
            description="LLM service rate limit exceeded",
            user_message="I'm receiving many requests right now. Please try again in a moment.",
            technical_message="Gemini API rate limit exceeded",
            max_retries=3,
            retry_delay=5.0
        ))
        
        self.add_pattern(ErrorPattern(
            pattern_id="llm_service_unavailable",
            category=ErrorCategory.LLM_SERVICE,
            severity=ErrorSeverity.CRITICAL,
            source=ErrorSource.EXTERNAL,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            exception_types=["ServiceUnavailableError", "ConnectionError"],
            message_patterns=["service unavailable", "connection refused", "timeout"],
            status_codes=[503, 504],
            description="LLM service is unavailable",
            user_message="I'm experiencing technical difficulties. Please try again later.",
            technical_message="Gemini API service unavailable",
            max_retries=2,
            retry_delay=10.0
        ))
        
        # Vector search errors
        self.add_pattern(ErrorPattern(
            pattern_id="vector_search_failure",
            category=ErrorCategory.VECTOR_SEARCH,
            severity=ErrorSeverity.HIGH,
            source=ErrorSource.SERVER,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            exception_types=["VectorSearchError", "IndexError"],
            message_patterns=["vector search failed", "index not found", "embedding error"],
            description="Vector search operation failed",
            user_message="I'm having trouble finding relevant spiritual texts. Let me try a different approach.",
            technical_message="Vector search operation failed, falling back to keyword search",
            max_retries=2
        ))
        
        # Database errors
        self.add_pattern(ErrorPattern(
            pattern_id="database_connection",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.CRITICAL,
            source=ErrorSource.SYSTEM,
            recovery_strategy=RecoveryStrategy.RETRY,
            exception_types=["ConnectionError", "DatabaseError", "OperationalError"],
            message_patterns=["connection refused", "database unavailable", "timeout"],
            description="Database connection failure",
            user_message="I'm experiencing connection issues. Please try again in a moment.",
            technical_message="Database connection failed",
            max_retries=3,
            retry_delay=2.0
        ))
        
        # Content moderation errors
        self.add_pattern(ErrorPattern(
            pattern_id="content_moderation_failure",
            category=ErrorCategory.CONTENT_MODERATION,
            severity=ErrorSeverity.MEDIUM,
            source=ErrorSource.SERVER,
            recovery_strategy=RecoveryStrategy.DEGRADE,
            exception_types=["ModerationError", "ValidationError"],
            message_patterns=["moderation failed", "content validation error"],
            description="Content moderation system failure",
            user_message="I'll provide guidance while being extra careful about the content.",
            technical_message="Content moderation failed, continuing with basic validation",
            max_retries=1
        ))
        
        # Input validation errors
        self.add_pattern(ErrorPattern(
            pattern_id="invalid_input",
            category=ErrorCategory.INPUT_VALIDATION,
            severity=ErrorSeverity.LOW,
            source=ErrorSource.CLIENT,
            recovery_strategy=RecoveryStrategy.FAIL_FAST,
            exception_types=["ValidationError", "ValueError"],
            message_patterns=["invalid input", "validation failed", "required field"],
            status_codes=[400],
            description="Invalid user input",
            user_message="Please check your input and try again.",
            technical_message="Input validation failed",
            max_retries=0
        ))
        
        # Spiritual validation errors
        self.add_pattern(ErrorPattern(
            pattern_id="spiritual_validation_failure",
            category=ErrorCategory.SPIRITUAL_VALIDATION,
            severity=ErrorSeverity.HIGH,
            source=ErrorSource.SERVER,
            recovery_strategy=RecoveryStrategy.ESCALATE,
            exception_types=["SpiritualValidationError"],
            message_patterns=["spiritual validation failed", "inappropriate spiritual content"],
            description="Spiritual content validation failed",
            user_message="Let me reconsider my response to ensure it's spiritually appropriate.",
            technical_message="Spiritual validation failed, escalating for expert review",
            max_retries=1
        ))
        
        # Expert review system errors
        self.add_pattern(ErrorPattern(
            pattern_id="expert_review_unavailable",
            category=ErrorCategory.EXPERT_REVIEW,
            severity=ErrorSeverity.MEDIUM,
            source=ErrorSource.EXTERNAL,
            recovery_strategy=RecoveryStrategy.DEGRADE,
            exception_types=["ExpertReviewError", "ReviewUnavailableError"],
            message_patterns=["expert review unavailable", "no experts available"],
            description="Expert review system unavailable",
            user_message="I'll provide guidance based on established teachings while our experts are unavailable.",
            technical_message="Expert review system unavailable, proceeding with validated content",
            max_retries=1
        ))
        
        # Network errors
        self.add_pattern(ErrorPattern(
            pattern_id="network_timeout",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            source=ErrorSource.EXTERNAL,
            recovery_strategy=RecoveryStrategy.RETRY,
            exception_types=["TimeoutError", "ConnectTimeout", "ReadTimeout"],
            message_patterns=["timeout", "connection timeout", "read timeout"],
            description="Network operation timeout",
            user_message="The connection is slow. Let me try again.",
            technical_message="Network operation timed out",
            max_retries=2,
            retry_delay=3.0
        ))
        
        # Resource exhaustion
        self.add_pattern(ErrorPattern(
            pattern_id="memory_exhaustion",
            category=ErrorCategory.RESOURCE_EXHAUSTION,
            severity=ErrorSeverity.CRITICAL,
            source=ErrorSource.SYSTEM,
            recovery_strategy=RecoveryStrategy.CIRCUIT_BREAK,
            exception_types=["MemoryError", "OutOfMemoryError"],
            message_patterns=["out of memory", "memory exhausted"],
            description="System memory exhausted",
            user_message="I'm experiencing high load. Please try again in a few minutes.",
            technical_message="System memory exhausted, circuit breaker activated",
            max_retries=0
        ))
    
    def add_pattern(self, pattern: ErrorPattern):
        """Add an error pattern to the classifier"""
        self.patterns[pattern.pattern_id] = pattern
        logger.debug(f"Added error pattern: {pattern.pattern_id}")
    
    def classify_error(self, 
                      exception: Exception, 
                      context: Optional[ErrorContext] = None,
                      status_code: Optional[int] = None) -> ClassifiedError:
        """Classify an error based on patterns"""
        
        if context is None:
            context = ErrorContext()
        
        # Generate error ID
        error_signature = self._generate_error_signature(exception, context)
        
        # Check if we've seen this error before
        if error_signature in self.error_history:
            existing_error = self.error_history[error_signature]
            existing_error.frequency_count += 1
            existing_error.last_occurrence = datetime.now()
            self._update_frequency_tracker(error_signature)
            return existing_error
        
        # Find matching pattern
        matched_pattern, confidence = self._find_matching_pattern(exception, status_code)
        
        if matched_pattern:
            pattern = self.patterns[matched_pattern]
            classified_error = ClassifiedError(
                error_id=error_signature,
                original_exception=exception,
                category=pattern.category,
                severity=pattern.severity,
                source=pattern.source,
                recovery_strategy=pattern.recovery_strategy,
                user_message=pattern.user_message,
                technical_message=pattern.technical_message,
                context=context,
                max_retries=pattern.max_retries,
                retry_delay=pattern.retry_delay,
                matched_pattern=matched_pattern,
                confidence=confidence,
                stack_trace=traceback.format_exc()
            )
        else:
            # Unknown error - create generic classification
            classified_error = ClassifiedError(
                error_id=error_signature,
                original_exception=exception,
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                source=ErrorSource.SERVER,
                recovery_strategy=RecoveryStrategy.FAIL_FAST,
                user_message="I encountered an unexpected issue. Please try again.",
                technical_message=f"Unclassified error: {str(exception)}",
                context=context,
                stack_trace=traceback.format_exc(),
                confidence=0.5
            )
        
        # Store in history
        self.error_history[error_signature] = classified_error
        self._update_frequency_tracker(error_signature)
        
        logger.info(f"Classified error: {classified_error.category.value} - {classified_error.severity.value}")
        
        return classified_error
    
    def _generate_error_signature(self, exception: Exception, context: ErrorContext) -> str:
        """Generate a unique signature for error deduplication"""
        # Create signature based on exception type, message, and operation
        signature_data = {
            "type": type(exception).__name__,
            "message": str(exception)[:200],  # Truncate long messages
            "operation": context.operation or "unknown"
        }
        
        signature_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.md5(signature_string.encode()).hexdigest()
    
    def _find_matching_pattern(self, 
                              exception: Exception, 
                              status_code: Optional[int] = None) -> Tuple[Optional[str], float]:
        """Find the best matching pattern for an error"""
        
        exception_type = type(exception).__name__
        exception_message = str(exception).lower()
        
        best_match = None
        best_confidence = 0.0
        
        for pattern_id, pattern in self.patterns.items():
            confidence = 0.0
            
            # Check exception type match (exact or partial)
            if pattern.exception_types:
                for exc_type in pattern.exception_types:
                    if exc_type.lower() in exception_type.lower() or exception_type == exc_type:
                        confidence += 0.4
                        break
            
            # Check message pattern match
            if pattern.message_patterns:
                for msg_pattern in pattern.message_patterns:
                    if msg_pattern.lower() in exception_message:
                        confidence += 0.4
                        break
            
            # Check status code match
            if pattern.status_codes and status_code:
                if status_code in pattern.status_codes:
                    confidence += 0.2
            
            # Update best match if this is better
            if confidence > best_confidence and confidence >= 0.3:  # Minimum threshold
                best_confidence = confidence
                best_match = pattern_id
        
        return best_match, best_confidence
    
    def _update_frequency_tracker(self, error_signature: str):
        """Update frequency tracking for error patterns"""
        now = datetime.now()
        
        if error_signature not in self.frequency_tracker:
            self.frequency_tracker[error_signature] = []
        
        self.frequency_tracker[error_signature].append(now)
        
        # Clean up old entries (keep last 24 hours)
        cutoff = now - timedelta(hours=24)
        self.frequency_tracker[error_signature] = [
            timestamp for timestamp in self.frequency_tracker[error_signature]
            if timestamp > cutoff
        ]
    
    def get_error_frequency(self, error_signature: str, 
                           time_window: timedelta = timedelta(hours=1)) -> int:
        """Get error frequency within a time window"""
        if error_signature not in self.frequency_tracker:
            return 0
        
        cutoff = datetime.now() - time_window
        return len([
            timestamp for timestamp in self.frequency_tracker[error_signature]
            if timestamp > cutoff
        ])
    
    def should_alert(self, classified_error: ClassifiedError) -> bool:
        """Determine if an error should trigger an alert"""
        if not classified_error.matched_pattern:
            return True  # Alert for unknown errors
        
        pattern = self.patterns[classified_error.matched_pattern]
        frequency = self.get_error_frequency(classified_error.error_id)
        
        return frequency >= pattern.alert_threshold
    
    def should_escalate(self, classified_error: ClassifiedError) -> bool:
        """Determine if an error should be escalated"""
        if classified_error.severity == ErrorSeverity.CRITICAL:
            return True
        
        if not classified_error.matched_pattern:
            return True  # Escalate unknown errors
        
        pattern = self.patterns[classified_error.matched_pattern]
        frequency = self.get_error_frequency(classified_error.error_id)
        
        return frequency >= pattern.escalation_threshold
    
    def get_error_statistics(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        cutoff = datetime.now() - time_window
        
        stats = {
            "total_errors": 0,
            "by_category": {},
            "by_severity": {},
            "by_source": {},
            "top_errors": [],
            "alert_worthy": 0,
            "escalation_worthy": 0
        }
        
        for error in self.error_history.values():
            if error.last_occurrence > cutoff:
                stats["total_errors"] += error.frequency_count
                
                # Count by category
                category = error.category.value
                stats["by_category"][category] = stats["by_category"].get(category, 0) + error.frequency_count
                
                # Count by severity
                severity = error.severity.value
                stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + error.frequency_count
                
                # Count by source
                source = error.source.value
                stats["by_source"][source] = stats["by_source"].get(source, 0) + error.frequency_count
                
                # Check if alert/escalation worthy
                if self.should_alert(error):
                    stats["alert_worthy"] += 1
                
                if self.should_escalate(error):
                    stats["escalation_worthy"] += 1
        
        # Get top errors by frequency
        top_errors = sorted(
            self.error_history.values(),
            key=lambda e: e.frequency_count,
            reverse=True
        )[:10]
        
        stats["top_errors"] = [
            {
                "error_id": error.error_id,
                "category": error.category.value,
                "frequency": error.frequency_count,
                "user_message": error.user_message
            }
            for error in top_errors
        ]
        
        return stats
    
    def export_patterns(self) -> Dict[str, Any]:
        """Export error patterns for backup/sharing"""
        exported = {}
        for pattern_id, pattern in self.patterns.items():
            exported[pattern_id] = {
                "category": pattern.category.value,
                "severity": pattern.severity.value,
                "source": pattern.source.value,
                "recovery_strategy": pattern.recovery_strategy.value,
                "exception_types": pattern.exception_types,
                "message_patterns": pattern.message_patterns,
                "status_codes": pattern.status_codes,
                "description": pattern.description,
                "user_message": pattern.user_message,
                "technical_message": pattern.technical_message,
                "max_retries": pattern.max_retries,
                "retry_delay": pattern.retry_delay,
                "alert_threshold": pattern.alert_threshold,
                "escalation_threshold": pattern.escalation_threshold
            }
        return exported


# Convenience functions
def create_error_classifier() -> ErrorClassifier:
    """Create and initialize error classifier"""
    return ErrorClassifier()


def classify_exception(exception: Exception, 
                      context: Optional[ErrorContext] = None,
                      status_code: Optional[int] = None) -> ClassifiedError:
    """Convenience function to classify an exception"""
    classifier = create_error_classifier()
    return classifier.classify_error(exception, context, status_code)


def get_recovery_strategy(error: ClassifiedError) -> RecoveryStrategy:
    """Get the recommended recovery strategy for an error"""
    return error.recovery_strategy
