"""
Voice Interface Module for Vimarsh AI Agent

This module provides voice processing capabilities optimized for spiritual guidance,
including speech recognition with Sanskrit support and text-to-speech optimization
for sacred content delivery.
"""

from .speech_processor import SpeechProcessor, VoiceConfig, RecognitionResult
from .web_speech_integration import WebSpeechIntegration, SpeechRecognitionError

__all__ = [
    'SpeechProcessor',
    'VoiceConfig', 
    'RecognitionResult',
    'WebSpeechIntegration',
    'SpeechRecognitionError'
]

__version__ = "1.0.0"
