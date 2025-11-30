"""
Azure Speech Service for Vimarsh Personality TTS

This module provides Azure Neural Voice integration with personality-specific
voice configurations and SSML styling for authentic character representation.
"""

import logging
import os
from typing import Optional, Callable
import azure.cognitiveservices.speech as speechsdk

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
    
    Supports:
    - Personality-specific Azure Neural Voices
    - SSML styling for authentic character representation
    - Audio output in various formats (MP3, WAV, OGG)
    - Streaming support for long-form content
    """
    
    # Audio format mappings
    AUDIO_FORMATS = {
        "mp3": speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3,
        "mp3-hd": speechsdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3,
        "wav": speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm,
        "ogg": speechsdk.SpeechSynthesisOutputFormat.Ogg16Khz16BitMonoOpus,
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
            logger.info(f"🎙️ Azure Speech Service initialized (region: {self.speech_region})")
    
    @property
    def is_available(self) -> bool:
        """Check if the service is properly configured and available."""
        return self._initialized
    
    def _create_speech_config(
        self, 
        voice_config: VoiceConfig,
        audio_format: str = "mp3"
    ) -> speechsdk.SpeechConfig:
        """
        Create speech configuration with voice settings.
        
        Args:
            voice_config: Voice configuration for the personality
            audio_format: Output audio format (mp3, mp3-hd, wav, ogg)
            
        Returns:
            Configured SpeechConfig instance
        """
        speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region
        )
        
        # Set the voice
        speech_config.speech_synthesis_voice_name = voice_config.voice_name
        
        # Set audio format
        format_enum = self.AUDIO_FORMATS.get(audio_format, self.AUDIO_FORMATS["mp3"])
        speech_config.set_speech_synthesis_output_format(format_enum)
        
        return speech_config
    
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
            # Create speech config
            speech_config = self._create_speech_config(voice_config, audio_format)
            
            # Use in-memory audio output
            audio_config = None  # None = in-memory output
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            
            # Synthesize with SSML or plain text
            if use_ssml:
                ssml = build_ssml(text, voice_config)
                result = synthesizer.speak_ssml_async(ssml).get()
            else:
                result = synthesizer.speak_text_async(text).get()
            
            # Check result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_data = result.audio_data
                logger.info(
                    f"✅ Speech synthesis completed: {len(audio_data)} bytes "
                    f"for {personality}"
                )
                return audio_data
            
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                logger.error(
                    f"❌ Speech synthesis canceled: {cancellation.reason}. "
                    f"Error: {cancellation.error_details}"
                )
                return None
            
            else:
                logger.error(f"❌ Unexpected result: {result.reason}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Speech synthesis error: {str(e)}")
            raise
    
    def synthesize_to_stream(
        self,
        text: str,
        personality: str = "krishna",
        audio_format: str = "mp3",
        use_ssml: bool = True,
        chunk_callback: Optional[Callable] = None
    ) -> Optional[bytes]:
        """
        Synthesize speech with streaming support for real-time playback.
        
        This method supports chunk-by-chunk audio delivery for lower latency.
        
        Args:
            text: The text to synthesize
            personality: The personality ID
            audio_format: Output format (mp3, mp3-hd, wav, ogg)
            use_ssml: Whether to use SSML for enhanced styling
            chunk_callback: Optional callback for streaming chunks
            
        Returns:
            Complete audio bytes if successful, None if failed
        """
        if not self.is_available:
            raise ValueError("Azure Speech Service is not configured. Set AZURE_SPEECH_KEY.")
        
        voice_config = get_voice_config(personality)
        speech_config = self._create_speech_config(voice_config, audio_format)
        
        # Create pull audio output stream for streaming
        stream = speechsdk.audio.PullAudioOutputStream()
        audio_config = speechsdk.audio.AudioOutputConfig(stream=stream)
        
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        
        audio_chunks = []
        
        def handle_audio_data(evt):
            """Handle streaming audio data events."""
            if evt.audio_data:
                audio_chunks.append(evt.audio_data)
                if chunk_callback:
                    chunk_callback(evt.audio_data)
        
        # Connect to synthesizing event for streaming
        synthesizer.synthesizing.connect(handle_audio_data)
        
        try:
            if use_ssml:
                ssml = build_ssml(text, voice_config)
                result = synthesizer.speak_ssml_async(ssml).get()
            else:
                result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Return complete audio data
                return result.audio_data
            else:
                cancellation = result.cancellation_details
                logger.error(f"❌ Streaming synthesis failed: {cancellation.error_details}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Streaming synthesis error: {str(e)}")
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
            speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key,
                region=self.speech_region
            )
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=None
            )
            
            result = synthesizer.get_voices_async(locale or "").get()
            
            if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                voices = []
                for voice in result.voices:
                    voices.append({
                        "name": voice.name,
                        "short_name": voice.short_name,
                        "locale": voice.locale,
                        "gender": voice.gender.name,
                        "voice_type": voice.voice_type.name,
                        "style_list": voice.style_list if hasattr(voice, 'style_list') else []
                    })
                return voices
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
