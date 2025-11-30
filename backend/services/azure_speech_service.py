"""
Azure Speech Service for Vimarsh Personality TTS

This module provides Azure Neural Voice integration with personality-specific
voice configurations and SSML styling for authentic character representation.

Uses REST API instead of SDK to ensure compatibility with Azure Functions.
"""

import logging
import os
from typing import Optional
import httpx

from config.voice_config import get_voice_config, VoiceConfig

logger = logging.getLogger(__name__)


def build_ssml(text: str, voice_config: VoiceConfig) -> str:
    """
    Build SSML (Speech Synthesis Markup Language) for personality-specific TTS.
    
    Creates styled speech with:
    - Personality-specific voice
    - Speaking style (empathetic, calm, cheerful, etc.)
    - Rate and pitch adjustments
    
    Args:
        text: The text to synthesize
        voice_config: Voice configuration for the personality
        
    Returns:
        SSML string ready for Azure Speech Service
    """
    # Escape XML special characters in text
    escaped_text = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\"", "&quot;")
        .replace("'", "&apos;")
    )
    
    ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
    xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{voice_config.locale}">
    <voice name="{voice_config.voice_name}">
        <mstts:express-as style="{voice_config.style}">
            <prosody rate="{voice_config.rate}" pitch="{voice_config.pitch}">
                {escaped_text}
            </prosody>
        </mstts:express-as>
    </voice>
</speak>'''
    
    return ssml


class AzureSpeechService:
    """
    Azure Speech Service client for personality-based text-to-speech synthesis.
    
    Uses REST API for Azure Functions compatibility (SDK has native lib issues).
    
    Supports:
    - Personality-specific Azure Neural Voices
    - SSML styling for authentic character representation
    - Audio output in MP3/WAV/OGG formats
    """
    
    # Audio format mappings for REST API
    AUDIO_FORMATS = {
        "mp3": "audio-16khz-32kbitrate-mono-mp3",
        "mp3-hd": "audio-24khz-48kbitrate-mono-mp3",
        "wav": "riff-16khz-16bit-mono-pcm",
        "ogg": "ogg-16khz-16bit-mono-opus",
    }
    
    CONTENT_TYPES = {
        "mp3": "audio/mpeg",
        "mp3-hd": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
    }
    
    def __init__(self):
        """Initialize Azure Speech Service with credentials from environment."""
        self.speech_key = os.environ.get("AZURE_SPEECH_KEY")
        self.speech_region = os.environ.get("AZURE_SPEECH_REGION", "eastus")
        
        if not self.speech_key:
            logger.warning("AZURE_SPEECH_KEY not configured - TTS will be unavailable")
            self._initialized = False
        else:
            self._initialized = True
            self._token_url = f"https://{self.speech_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
            self._tts_url = f"https://{self.speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"
            logger.info(f"🎙️ Azure Speech Service initialized (region: {self.speech_region})")
    
    @property
    def is_available(self) -> bool:
        """Check if the service is properly configured and available."""
        return self._initialized
    
    def _get_access_token(self) -> Optional[str]:
        """
        Get access token for Azure Speech Service.
        
        Returns:
            Access token string or None if failed
        """
        try:
            response = httpx.post(
                self._token_url,
                headers={
                    "Ocp-Apim-Subscription-Key": self.speech_key,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"❌ Failed to get access token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Token request error: {str(e)}")
            return None
    
    def synthesize_speech(
        self,
        text: str,
        personality: str = "krishna",
        audio_format: str = "mp3",
        use_ssml: bool = True
    ) -> Optional[bytes]:
        """
        Synthesize speech for a given text using personality-specific voice.
        
        Args:
            text: The text to synthesize
            personality: The personality ID (e.g., "krishna", "buddha")
            audio_format: Output format (mp3, mp3-hd, wav, ogg)
            use_ssml: Whether to use SSML for enhanced styling
            
        Returns:
            Audio bytes if successful, None if failed
            
        Raises:
            ValueError: If service is not configured
        """
        if not self.is_available:
            raise ValueError("Azure Speech Service is not configured. Set AZURE_SPEECH_KEY.")
        
        # Get voice configuration for personality
        voice_config = get_voice_config(personality)
        
        logger.info(
            f"🎙️ Synthesizing speech for {personality} "
            f"(voice: {voice_config.voice_name}, style: {voice_config.style})"
        )
        
        try:
            # Get access token
            access_token = self._get_access_token()
            if not access_token:
                logger.error("❌ Failed to get access token")
                return None
            
            # Build SSML body
            body = build_ssml(text, voice_config)
            
            # Get output format
            output_format = self.AUDIO_FORMATS.get(audio_format, self.AUDIO_FORMATS["mp3"])
            
            # Make TTS request
            response = httpx.post(
                self._tts_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/ssml+xml",
                    "X-Microsoft-OutputFormat": output_format,
                    "User-Agent": "VimarshApp/1.0",
                },
                content=body.encode("utf-8"),
                timeout=30.0
            )
            
            if response.status_code == 200:
                audio_data = response.content
                logger.info(
                    f"✅ Speech synthesis completed: {len(audio_data)} bytes "
                    f"for {personality}"
                )
                return audio_data
            else:
                logger.error(
                    f"❌ Speech synthesis failed: {response.status_code} - {response.text}"
                )
                return None
                
        except Exception as e:
            logger.error(f"❌ Speech synthesis error: {str(e)}")
            raise
    
    def get_available_voices(self, locale: Optional[str] = None) -> list:
        """
        Get list of available Azure Neural Voices.
        
        Args:
            locale: Optional locale filter (e.g., "en-US", "en-IN")
            
        Returns:
            List of available voice information dicts
        """
        if not self.is_available:
            return []
        
        try:
            access_token = self._get_access_token()
            if not access_token:
                return []
            
            voices_url = f"https://{self.speech_region}.tts.speech.microsoft.com/cognitiveservices/voices/list"
            
            response = httpx.get(
                voices_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                voices = response.json()
                if locale:
                    voices = [v for v in voices if v.get("Locale", "").startswith(locale)]
                return [
                    {
                        "name": v.get("Name"),
                        "short_name": v.get("ShortName"),
                        "locale": v.get("Locale"),
                        "gender": v.get("Gender"),
                        "voice_type": v.get("VoiceType"),
                        "style_list": v.get("StyleList", [])
                    }
                    for v in voices
                ]
            return []
            
        except Exception as e:
            logger.error(f"❌ Failed to get voices: {str(e)}")
            return []
    
    def estimate_cost(self, text: str) -> dict:
        """
        Estimate the cost for synthesizing given text.
        
        Azure Speech Service pricing (Neural): ~$15 per 1M characters
        
        Args:
            text: The text to estimate cost for
            
        Returns:
            Dict with character count and estimated cost
        """
        char_count = len(text)
        # Neural voice pricing: $15 per 1M characters
        cost_per_char = 15.0 / 1_000_000
        estimated_cost = char_count * cost_per_char
        
        return {
            "character_count": char_count,
            "estimated_cost_usd": round(estimated_cost, 6),
            "pricing_tier": "neural",
            "free_tier_chars_remaining": max(0, 500_000 - char_count)  # 500K free/month
        }


# Module-level singleton for convenience
_service_instance: Optional[AzureSpeechService] = None


def get_speech_service() -> AzureSpeechService:
    """Get or create the Azure Speech Service singleton instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = AzureSpeechService()
    return _service_instance


def synthesize_personality_speech(
    text: str,
    personality: str = "krishna",
    audio_format: str = "mp3"
) -> Optional[bytes]:
    """
    Convenience function to synthesize speech for a personality.
    
    Args:
        text: Text to synthesize
        personality: Personality ID (e.g., "krishna", "buddha")
        audio_format: Output format (mp3, wav, ogg)
        
    Returns:
        Audio bytes if successful, None if failed
    """
    service = get_speech_service()
    return service.synthesize_speech(text, personality, audio_format)
