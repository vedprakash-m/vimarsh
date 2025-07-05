"""Shim for backend.error_handling.circuit_breaker."""
import importlib, sys as _sys
_mod = importlib.import_module('backend.error_handling.circuit_breaker')
_sys.modules[__name__] = _mod
__all__ = getattr(_mod, '__all__', [n for n in dir(_mod) if not n.startswith('_')]) 