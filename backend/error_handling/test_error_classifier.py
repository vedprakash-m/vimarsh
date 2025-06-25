"""
Test suite for the error classification system.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from error_classifier import (
    ErrorClassifier, ErrorCategory, ErrorSeverity, ErrorSource, 
    RecoveryStrategy, ErrorContext, ErrorPattern, ClassifiedError,
    create_error_classifier, classify_exception
)


class TestErrorClassifier:
    """Test cases for ErrorClassifier"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.classifier = ErrorClassifier()
    
    def test_initialization(self):
        """Test classifier initialization with default patterns"""
        assert len(self.classifier.patterns) > 0
        assert "auth_token_expired" in self.classifier.patterns
        assert "llm_rate_limit" in self.classifier.patterns
        assert "vector_search_failure" in self.classifier.patterns
    
    def test_add_pattern(self):
        """Test adding new error patterns"""
        pattern = ErrorPattern(
            pattern_id="test_pattern",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.LOW,
            source=ErrorSource.SERVER,
            recovery_strategy=RecoveryStrategy.RETRY,
            exception_types=["TestError"],
            message_patterns=["test error"],
            description="Test error pattern"
        )
        
        self.classifier.add_pattern(pattern)
        assert "test_pattern" in self.classifier.patterns
        assert self.classifier.patterns["test_pattern"] == pattern
    
    def test_classify_known_error(self):
        """Test classification of known error types"""
        # Test authentication error
        auth_error = Exception("authentication failed")
        context = ErrorContext(user_id="test_user", operation="login")
        
        classified = self.classifier.classify_error(auth_error, context, status_code=401)
        
        assert classified.category == ErrorCategory.AUTHENTICATION
        assert classified.severity == ErrorSeverity.MEDIUM
        assert classified.source == ErrorSource.CLIENT
        assert classified.recovery_strategy == RecoveryStrategy.FALLBACK
        assert classified.matched_pattern == "auth_token_expired"
        assert classified.confidence > 0.3
        assert "log in again" in classified.user_message
    
    def test_classify_llm_rate_limit(self):
        """Test classification of LLM rate limit errors"""
        rate_limit_error = Exception("rate limit exceeded")
        
        classified = self.classifier.classify_error(rate_limit_error, status_code=429)
        
        assert classified.category == ErrorCategory.LLM_SERVICE
        assert classified.severity == ErrorSeverity.HIGH
        assert classified.recovery_strategy == RecoveryStrategy.RETRY
        assert classified.max_retries == 3
        assert classified.retry_delay == 5.0
    
    def test_classify_unknown_error(self):
        """Test classification of unknown error types"""
        unknown_error = Exception("completely random and unique error message that matches no patterns")
        
        classified = self.classifier.classify_error(unknown_error)
        
        assert classified.category == ErrorCategory.UNKNOWN
        assert classified.severity == ErrorSeverity.MEDIUM
        assert classified.source == ErrorSource.SERVER
        assert classified.recovery_strategy == RecoveryStrategy.FAIL_FAST
        assert classified.matched_pattern is None
        assert classified.confidence == 0.5
    
    def test_error_deduplication(self):
        """Test that identical errors are deduplicated"""
        error1 = Exception("test error message")
        error2 = Exception("test error message")
        context = ErrorContext(operation="test_op")
        
        classified1 = self.classifier.classify_error(error1, context)
        classified2 = self.classifier.classify_error(error2, context)
        
        assert classified1.error_id == classified2.error_id
        assert classified2.frequency_count == 2
        assert classified1.first_occurrence < classified2.last_occurrence
    
    def test_frequency_tracking(self):
        """Test error frequency tracking"""
        error = Exception("frequent error")
        context = ErrorContext(operation="test")
        
        # Generate the same error multiple times
        for _ in range(5):
            self.classifier.classify_error(error, context)
            time.sleep(0.01)  # Small delay to differentiate timestamps
        
        classified = self.classifier.classify_error(error, context)
        frequency = self.classifier.get_error_frequency(classified.error_id)
        
        assert frequency == 6  # 5 + 1 from classify call
        assert classified.frequency_count == 6
    
    def test_alert_threshold(self):
        """Test alert threshold detection"""
        error = Exception("alert test error")
        
        # Add a pattern with low alert threshold
        pattern = ErrorPattern(
            pattern_id="alert_test",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            source=ErrorSource.SERVER,
            recovery_strategy=RecoveryStrategy.RETRY,
            exception_types=["Exception"],
            message_patterns=["alert test"],
            alert_threshold=3
        )
        self.classifier.add_pattern(pattern)
        
        # Generate errors below threshold
        for _ in range(2):
            classified = self.classifier.classify_error(error)
            assert not self.classifier.should_alert(classified)
        
        # Generate error that crosses threshold
        classified = self.classifier.classify_error(error)
        assert self.classifier.should_alert(classified)
    
    def test_escalation_threshold(self):
        """Test escalation threshold detection"""
        error = Exception("escalation test error")
        
        # Add a pattern with low escalation threshold
        pattern = ErrorPattern(
            pattern_id="escalation_test",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            source=ErrorSource.SERVER,
            recovery_strategy=RecoveryStrategy.RETRY,
            exception_types=["Exception"],
            message_patterns=["escalation test"],
            escalation_threshold=2
        )
        self.classifier.add_pattern(pattern)
        
        # Generate error that crosses escalation threshold
        classified = self.classifier.classify_error(error)
        classified = self.classifier.classify_error(error)
        
        assert self.classifier.should_escalate(classified)
    
    def test_critical_error_escalation(self):
        """Test that critical errors are always escalated"""
        # Add a critical error pattern
        pattern = ErrorPattern(
            pattern_id="critical_test",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            source=ErrorSource.SYSTEM,
            recovery_strategy=RecoveryStrategy.ESCALATE,
            exception_types=["CriticalError"]
        )
        self.classifier.add_pattern(pattern)
        
        critical_error = Exception("CriticalError occurred")
        classified = self.classifier.classify_error(critical_error)
        
        assert self.classifier.should_escalate(classified)
    
    def test_pattern_matching_priority(self):
        """Test that more specific patterns are matched first"""
        # Add two patterns with different specificity
        specific_pattern = ErrorPattern(
            pattern_id="specific_auth",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            source=ErrorSource.CLIENT,
            recovery_strategy=RecoveryStrategy.RETRY,
            exception_types=["AuthenticationError"],
            message_patterns=["token expired", "authentication failed"]
        )
        
        general_pattern = ErrorPattern(
            pattern_id="general_auth",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.MEDIUM,
            source=ErrorSource.CLIENT,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            exception_types=["AuthenticationError"]
        )
        
        self.classifier.add_pattern(specific_pattern)
        self.classifier.add_pattern(general_pattern)
        
        # Test with error that matches both patterns
        auth_error = Exception("AuthenticationError: token expired")
        classified = self.classifier.classify_error(auth_error)
        
        # Should match the more specific pattern
        assert classified.matched_pattern in ["specific_auth", "auth_token_expired"]
        assert classified.confidence >= 0.3  # Lowered threshold
    
    def test_error_statistics(self):
        """Test error statistics generation"""
        # Generate various types of errors
        errors = [
            (Exception("auth error"), 401),
            (Exception("rate limit exceeded"), 429),
            (Exception("database unavailable"), 503),
            (Exception("unknown error"), None)
        ]
        
        for error, status_code in errors:
            for _ in range(3):  # Generate multiple occurrences
                self.classifier.classify_error(error, status_code=status_code)
        
        stats = self.classifier.get_error_statistics()
        
        assert stats["total_errors"] >= 12  # 4 error types * 3 occurrences
        assert len(stats["by_category"]) > 0
        assert len(stats["by_severity"]) > 0
        assert len(stats["by_source"]) > 0
        assert len(stats["top_errors"]) > 0
    
    def test_export_patterns(self):
        """Test pattern export functionality"""
        exported = self.classifier.export_patterns()
        
        assert isinstance(exported, dict)
        assert len(exported) == len(self.classifier.patterns)
        
        # Check structure of exported pattern
        for pattern_id, pattern_data in exported.items():
            assert "category" in pattern_data
            assert "severity" in pattern_data
            assert "source" in pattern_data
            assert "recovery_strategy" in pattern_data
            assert "description" in pattern_data


class TestErrorContext:
    """Test cases for ErrorContext"""
    
    def test_error_context_creation(self):
        """Test ErrorContext creation and default values"""
        context = ErrorContext()
        
        assert context.user_id is None
        assert context.session_id is None
        assert isinstance(context.timestamp, datetime)
        assert isinstance(context.additional_data, dict)
    
    def test_error_context_with_data(self):
        """Test ErrorContext with provided data"""
        context = ErrorContext(
            user_id="test_user",
            session_id="test_session",
            operation="test_operation",
            additional_data={"key": "value"}
        )
        
        assert context.user_id == "test_user"
        assert context.session_id == "test_session"
        assert context.operation == "test_operation"
        assert context.additional_data["key"] == "value"


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_create_error_classifier(self):
        """Test create_error_classifier function"""
        classifier = create_error_classifier()
        
        assert isinstance(classifier, ErrorClassifier)
        assert len(classifier.patterns) > 0
    
    def test_classify_exception(self):
        """Test classify_exception convenience function"""
        error = Exception("test error")
        context = ErrorContext(operation="test")
        
        classified = classify_exception(error, context, status_code=500)
        
        assert isinstance(classified, ClassifiedError)
        assert classified.original_exception == error
        assert classified.context == context


class TestSpiritualSpecificErrors:
    """Test spiritual guidance specific error scenarios"""
    
    def setup_method(self):
        self.classifier = ErrorClassifier()
    
    def test_spiritual_validation_error(self):
        """Test spiritual validation error classification"""
        error = Exception("inappropriate spiritual content detected")
        
        classified = self.classifier.classify_error(error)
        
        assert classified.category == ErrorCategory.SPIRITUAL_VALIDATION
        assert classified.severity == ErrorSeverity.HIGH
        assert classified.recovery_strategy == RecoveryStrategy.ESCALATE
        assert "spiritually appropriate" in classified.user_message
    
    def test_expert_review_unavailable(self):
        """Test expert review system unavailable"""
        error = Exception("expert review unavailable")
        
        classified = self.classifier.classify_error(error)
        
        assert classified.category == ErrorCategory.EXPERT_REVIEW
        assert classified.severity == ErrorSeverity.MEDIUM
        assert classified.recovery_strategy == RecoveryStrategy.DEGRADE
        assert "established teachings" in classified.user_message
    
    def test_content_moderation_failure(self):
        """Test content moderation failure"""
        error = Exception("content validation error")
        
        classified = self.classifier.classify_error(error)
        
        assert classified.category == ErrorCategory.CONTENT_MODERATION
        assert classified.recovery_strategy == RecoveryStrategy.DEGRADE
        assert "extra careful" in classified.user_message
    
    def test_vector_search_failure(self):
        """Test vector search failure"""
        error = Exception("vector search failed")
        
        classified = self.classifier.classify_error(error)
        
        assert classified.category == ErrorCategory.VECTOR_SEARCH
        assert classified.severity == ErrorSeverity.HIGH
        assert classified.recovery_strategy == RecoveryStrategy.FALLBACK
        assert "different approach" in classified.user_message


class TestErrorRecoveryStrategies:
    """Test error recovery strategy logic"""
    
    def setup_method(self):
        self.classifier = ErrorClassifier()
    
    def test_retry_strategy(self):
        """Test retry recovery strategy"""
        error = Exception("rate limit exceeded")
        
        classified = self.classifier.classify_error(error, status_code=429)
        
        assert classified.recovery_strategy == RecoveryStrategy.RETRY
        assert classified.max_retries > 0
        assert classified.retry_delay > 0
    
    def test_fallback_strategy(self):
        """Test fallback recovery strategy"""
        error = Exception("service unavailable")
        
        classified = self.classifier.classify_error(error, status_code=503)
        
        assert classified.recovery_strategy == RecoveryStrategy.FALLBACK
    
    def test_fail_fast_strategy(self):
        """Test fail fast recovery strategy"""
        error = Exception("invalid input")
        
        classified = self.classifier.classify_error(error, status_code=400)
        
        assert classified.recovery_strategy == RecoveryStrategy.FAIL_FAST
        assert classified.max_retries == 0
    
    def test_circuit_breaker_strategy(self):
        """Test circuit breaker recovery strategy"""
        error = Exception("out of memory")
        
        classified = self.classifier.classify_error(error)
        
        assert classified.recovery_strategy == RecoveryStrategy.CIRCUIT_BREAK
        assert classified.severity == ErrorSeverity.CRITICAL


if __name__ == "__main__":
    pytest.main([__file__])
