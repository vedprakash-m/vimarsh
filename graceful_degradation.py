"""Shim module for legacy imports.

Delegates to backend.cost_management.graceful_degradation so existing
unit tests continue to work after package restructuring.
"""
import importlib, sys as _sys
_mod = importlib.import_module('backend.cost_management.graceful_degradation')
_sys.modules[__name__] = _mod

# Re-export public names from underlying module
__all__ = getattr(_mod, '__all__', [n for n in dir(_mod) if not n.startswith('_')]) 