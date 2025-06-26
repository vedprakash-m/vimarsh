"""
Monitoring module initialization
Application Insights integration for Vimarsh spiritual guidance monitoring
"""

from .quality_monitor import SpiritualQualityMonitor
from .performance_tracker import PerformanceTracker
from .app_insights_client import AppInsightsClient

# Import real-time cost monitoring
try:
    from ..cost_management.real_time_monitor import RealTimeCostMonitor, get_monitor
    __all__ = [
        'SpiritualQualityMonitor',
        'PerformanceTracker', 
        'AppInsightsClient',
        'RealTimeCostMonitor',
        'get_monitor'
    ]
except ImportError:
    __all__ = [
        'SpiritualQualityMonitor',
        'PerformanceTracker', 
        'AppInsightsClient'
    ]
