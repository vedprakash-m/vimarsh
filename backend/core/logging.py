"""
Structured Logging System for Vimarsh
Provides Azure Application Insights integration with spiritual context awareness
"""

import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Azure Application Insights integration
try:
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    from opencensus.ext.azure.trace_exporter import AzureExporter
    from opencensus.trace.tracer import Tracer
    from opencensus.trace.samplers import ProbabilitySampler
    AZURE_INSIGHTS_AVAILABLE = True
except ImportError:
    AZURE_INSIGHTS_AVAILABLE = False

# Import centralized configuration
try:
    from backend.core.config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


class LogLevel(Enum):
    """Log levels for structured logging"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EventType(Enum):
    """Types of events for spiritual guidance system"""
    SPIRITUAL_GUIDANCE = "spiritual_guidance"
    AUTHENTICATION = "authentication"
    DATABASE_OPERATION = "database_operation"
    LLM_REQUEST = "llm_request"
    SAFETY_VALIDATION = "safety_validation"
    CONFIGURATION = "configuration"
    HEALTH_CHECK = "health_check"
    ERROR = "error"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class LogContext:
    """Context information for structured logging"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    operation_id: Optional[str] = None
    spiritual_context: Optional[str] = None
    endpoint: Optional[str] = None
    model_name: Optional[str] = None
    environment: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    token_count: Optional[int] = None
    response_size: Optional[int] = None
    
    def finish(self):
        """Mark operation as finished and calculate duration"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "duration_ms": self.duration_ms,
            "token_count": self.token_count,
            "response_size": self.response_size
        }


class StructuredLogger:
    """Structured logger with Azure Application Insights integration"""
    
    def __init__(self, name: str, connection_string: Optional[str] = None):
        """Initialize structured logger"""
        self.name = name
        self.logger = logging.getLogger(name)
        self.connection_string = connection_string
        self.tracer = None
        
        # Load configuration
        if CONFIG_AVAILABLE:
            config = get_config()
            self.connection_string = self.connection_string or config.monitoring.app_insights_connection_string
            self.log_level = config.monitoring.log_level.value
            self.debug_enabled = config.monitoring.debug
            self.environment = config.environment.value
        else:
            self.connection_string = self.connection_string or os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
            self.log_level = os.getenv("LOG_LEVEL", "INFO")
            self.debug_enabled = os.getenv("DEBUG", "false").lower() == "true"
            self.environment = os.getenv("ENVIRONMENT", "development")
        
        self._setup_logging()
        self._setup_azure_insights()
    
    def _setup_logging(self):
        """Setup basic logging configuration"""
        # Set log level
        level = getattr(logging, self.log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Create console handler if not already exists
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
    
    def _setup_azure_insights(self):
        """Setup Azure Application Insights integration"""
        if not AZURE_INSIGHTS_AVAILABLE:
            self.logger.warning("Azure Application Insights not available - using console logging only")
            return
        
        if not self.connection_string:
            self.logger.warning("Application Insights connection string not configured")
            return
        
        try:
            # Setup Azure Log Handler
            azure_handler = AzureLogHandler(connection_string=self.connection_string)
            azure_handler.setLevel(getattr(logging, self.log_level.upper(), logging.INFO))
            self.logger.addHandler(azure_handler)
            
            # Setup Azure Tracer
            azure_exporter = AzureExporter(connection_string=self.connection_string)
            self.tracer = Tracer(exporter=azure_exporter, sampler=ProbabilitySampler(1.0))
            
            self.logger.info("✅ Azure Application Insights configured successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to configure Azure Application Insights: {e}")
    
    def log_event(self, 
                  event_type: EventType,
                  message: str,
                  level: LogLevel = LogLevel.INFO,
                  context: Optional[LogContext] = None,
                  metrics: Optional[PerformanceMetrics] = None,
                  extra_data: Optional[Dict[str, Any]] = None):
        """Log a structured event"""
        
        # Build log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "message": message,
            "level": level.value,
            "environment": self.environment,
            "logger_name": self.name
        }
        
        # Add context if provided
        if context:
            log_entry["context"] = context.to_dict()
        
        # Add metrics if provided
        if metrics:
            log_entry["metrics"] = metrics.to_dict()
        
        # Add extra data if provided
        if extra_data:
            log_entry["extra_data"] = extra_data
        
        # Log to appropriate level
        log_level = getattr(logging, level.value)
        self.logger.log(log_level, json.dumps(log_entry))
    
    def log_spiritual_guidance(self,
                             query: str,
                             response: str,
                             context: LogContext,
                             metrics: PerformanceMetrics,
                             safety_passed: bool = True,
                             citations: Optional[list] = None):
        """Log spiritual guidance request"""
        extra_data = {
            "query_length": len(query),
            "response_length": len(response),
            "safety_passed": safety_passed,
            "citations_count": len(citations) if citations else 0
        }
        
        self.log_event(
            EventType.SPIRITUAL_GUIDANCE,
            f"Spiritual guidance provided - {context.spiritual_context or 'general'}",
            LogLevel.INFO,
            context,
            metrics,
            extra_data
        )
    
    def log_authentication_event(self,
                                event: str,
                                user_id: Optional[str] = None,
                                success: bool = True,
                                error_message: Optional[str] = None):
        """Log authentication event"""
        context = LogContext(user_id=user_id)
        level = LogLevel.INFO if success else LogLevel.WARNING
        
        extra_data = {
            "success": success,
            "error_message": error_message
        }
        
        self.log_event(
            EventType.AUTHENTICATION,
            f"Authentication {event}",
            level,
            context,
            extra_data=extra_data
        )
    
    def log_database_operation(self,
                             operation: str,
                             table_name: str,
                             success: bool = True,
                             metrics: Optional[PerformanceMetrics] = None,
                             error_message: Optional[str] = None):
        """Log database operation"""
        level = LogLevel.INFO if success else LogLevel.ERROR
        
        extra_data = {
            "operation": operation,
            "table_name": table_name,
            "success": success,
            "error_message": error_message
        }
        
        self.log_event(
            EventType.DATABASE_OPERATION,
            f"Database {operation} on {table_name}",
            level,
            metrics=metrics,
            extra_data=extra_data
        )
    
    def log_llm_request(self,
                       model_name: str,
                       token_count: int,
                       success: bool = True,
                       metrics: Optional[PerformanceMetrics] = None,
                       error_message: Optional[str] = None):
        """Log LLM API request"""
        level = LogLevel.INFO if success else LogLevel.ERROR
        
        extra_data = {
            "model_name": model_name,
            "token_count": token_count,
            "success": success,
            "error_message": error_message
        }
        
        self.log_event(
            EventType.LLM_REQUEST,
            f"LLM request to {model_name}",
            level,
            metrics=metrics,
            extra_data=extra_data
        )
    
    def log_safety_validation(self,
                            content: str,
                            safety_passed: bool,
                            safety_score: float,
                            warnings: list):
        """Log safety validation event"""
        level = LogLevel.INFO if safety_passed else LogLevel.WARNING
        
        extra_data = {
            "content_length": len(content),
            "safety_passed": safety_passed,
            "safety_score": safety_score,
            "warnings_count": len(warnings),
            "warnings": warnings
        }
        
        self.log_event(
            EventType.SAFETY_VALIDATION,
            f"Safety validation - {'PASSED' if safety_passed else 'FAILED'}",
            level,
            extra_data=extra_data
        )
    
    def log_error(self,
                  error_message: str,
                  exception: Optional[Exception] = None,
                  context: Optional[LogContext] = None,
                  stack_trace: Optional[str] = None):
        """Log error event"""
        extra_data = {
            "exception_type": type(exception).__name__ if exception else None,
            "exception_message": str(exception) if exception else None,
            "stack_trace": stack_trace
        }
        
        self.log_event(
            EventType.ERROR,
            error_message,
            LogLevel.ERROR,
            context,
            extra_data=extra_data
        )
    
    def log_performance_metric(self,
                             operation: str,
                             metrics: PerformanceMetrics,
                             context: Optional[LogContext] = None):
        """Log performance metric"""
        self.log_event(
            EventType.PERFORMANCE,
            f"Performance metric for {operation}",
            LogLevel.INFO,
            context,
            metrics
        )
    
    def start_operation(self, operation_name: str, context: Optional[LogContext] = None) -> str:
        """Start tracking an operation"""
        operation_id = str(uuid.uuid4())
        
        if context:
            context.operation_id = operation_id
        
        self.log_event(
            EventType.PERFORMANCE,
            f"Operation started: {operation_name}",
            LogLevel.DEBUG,
            context,
            extra_data={"operation_id": operation_id}
        )
        
        return operation_id
    
    def finish_operation(self, 
                        operation_id: str,
                        operation_name: str,
                        metrics: PerformanceMetrics,
                        success: bool = True,
                        error_message: Optional[str] = None):
        """Finish tracking an operation"""
        metrics.finish()
        
        level = LogLevel.INFO if success else LogLevel.ERROR
        
        extra_data = {
            "operation_id": operation_id,
            "success": success,
            "error_message": error_message
        }
        
        self.log_event(
            EventType.PERFORMANCE,
            f"Operation finished: {operation_name}",
            level,
            metrics=metrics,
            extra_data=extra_data
        )


# Global logger instances
_loggers = {}


def get_logger(name: str) -> StructuredLogger:
    """Get or create a structured logger instance"""
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name)
    return _loggers[name]


# Common logger instances
spiritual_logger = get_logger("vimarsh.spiritual_guidance")
auth_logger = get_logger("vimarsh.authentication")
db_logger = get_logger("vimarsh.database")
api_logger = get_logger("vimarsh.api")
health_logger = get_logger("vimarsh.health")
security_logger = get_logger("vimarsh.security")
