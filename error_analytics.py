"""Shim for backward compatibility - re-exports ErrorAnalytics class."""
from backend.error_handling.error_analytics import (
    ErrorAnalytics,
    ErrorEvent,
    ErrorPattern,
    SystemHealthMetrics,
    AnalyticsMetric,
)

__all__ = [
    "ErrorAnalytics",
    "ErrorEvent",
    "ErrorPattern",
    "SystemHealthMetrics",
    "AnalyticsMetric",
] 