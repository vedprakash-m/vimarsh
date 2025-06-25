"""
Core spiritual guidance module for Vimarsh AI Agent.

This module provides the foundational components for delivering authentic
spiritual guidance through Lord Krishna's persona, maintaining reverence
and accuracy in all responses.
"""

__version__ = "1.0.0"
__author__ = "Vimarsh Development Team"

# Module exports
from .api import SpiritualGuidanceAPI
from .persona import LordKrishnaPersona
from .validator import SpiritualResponseValidator

__all__ = [
    "SpiritualGuidanceAPI",
    "LordKrishnaPersona", 
    "SpiritualResponseValidator"
]
