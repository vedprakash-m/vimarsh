"""
Cost Management Module for Vimarsh AI Agent
Enhanced AI Cost Management & Dynamic Fallbacks (Section 7)
"""

from .vimarsh_cost_monitor import VimarshCostMonitor as CostMonitor
from .request_batcher import RequestBatcher  
from .intelligent_cache import QueryDeduplication
from .model_switcher import CostOptimizer

# Create module-level instances for backward compatibility
cost_monitor = CostMonitor()
request_batching = RequestBatcher()
query_deduplication = QueryDeduplication()
cost_optimizer = CostOptimizer()

__version__ = "1.0.0"

__all__ = [
    'CostMonitor',
    'RequestBatcher', 
    'QueryDeduplication',
    'CostOptimizer',
    'cost_monitor',
    'request_batching',
    'query_deduplication', 
    'cost_optimizer'
]
