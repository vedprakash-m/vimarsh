"""Shim to expose ErrorClassifier utilities for legacy tests."""
import importlib, sys as _sys
_mod = importlib.import_module('backend.error_handling.error_classifier')
_sys.modules[__name__] = _mod

__all__ = getattr(_mod, '__all__', [n for n in dir(_mod) if not n.startswith('_')])

# __all__ = [
#     "ErrorClassifier",
#     "ErrorCategory",
#     "ErrorSeverity",
#     "ErrorContext",
#     "ErrorSource",
# ] 