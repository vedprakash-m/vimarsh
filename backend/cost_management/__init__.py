"""
Cost Management Module for Vimarsh AI Agent
Enhanced AI Cost Management & Dynamic Fallbacks (Section 7)
"""

from .vimarsh_cost_monitor import VimarshCostMonitor as CostMonitor
from .request_batcher import RequestBatcher  
from .intelligent_cache import SpiritualQueryCache
from .model_switcher import ModelSwitcher

# Create module-level instances for backward compatibility
cost_monitor = CostMonitor()
request_batching = RequestBatcher()
spiritual_cache = SpiritualQueryCache()
model_switcher = ModelSwitcher()

__version__ = "1.0.0"

__all__ = [
    'CostMonitor',
    'RequestBatcher', 
    'SpiritualQueryCache',
    'ModelSwitcher',
    'cost_monitor',
    'request_batching',
    'spiritual_cache', 
    'model_switcher'
]
