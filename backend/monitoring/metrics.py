"""
Metrics collection and analysis for Vimarsh AI Agent

Provides comprehensive metrics collection, aggregation, and analysis
for spiritual guidance operations.
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Re-export from app_insights for compatibility
from .app_insights import SpiritualMetrics, MetricsCollector

__all__ = ['SpiritualMetrics', 'MetricsCollector']
