"""
Audio Processing Utilities for Vimarsh Voice Interface

This module provides core audio processing functionality including:
- Audio format conversion and validation
- Quality analysis and enhancement
- Real-time audio stream processing
- Audio chunk management for spiritual content
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime
import io
import wave

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    WEBM = "webm"


class AudioQuality(Enum):
    """Audio quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    STUDIO = "studio"


@dataclass
class AudioMetrics:
    """Audio quality and performance metrics"""
    sample_rate: int
    channels: int
    duration: float
    bit_depth: int
    format: str
    file_size: int
    signal_to_noise_ratio: Optional[float] = None
    dynamic_range: Optional[float] = None
    peak_level: Optional[float] = None
    rms_level: Optional[float] = None
    frequency_response: Optional[Dict[str, float]] = None


@dataclass
class AudioChunk:
    """Audio data chunk for processing"""
    data: bytes
    timestamp: datetime
    duration: float
    sample_rate: int
    channels: int
    format: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class AudioProcessor:
    """Core audio processing functionality"""
    
    def __init__(self, 
                 default_sample_rate: int = 16000,
                 default_channels: int = 1,
                 quality_level: AudioQuality = AudioQuality.HIGH):
        """
        Initialize audio processor
        
        Args:
            default_sample_rate: Default sample rate for processing
            default_channels: Default number of channels
            quality_level: Processing quality level
        """
        self.default_sample_rate = default_sample_rate
        self.default_channels = default_channels
        self.quality_level = quality_level
        
        # Processing statistics
        self.processed_chunks = 0
        self.total_duration = 0.0
        self.error_count = 0
        
        logger.info(f"AudioProcessor initialized: {default_sample_rate}Hz, {default_channels}ch, {quality_level.value}")
    
    def validate_audio_data(self, audio_data: bytes, expected_format: str = "wav") -> bool:
        """
        Validate audio data format and integrity
        
        Args:
            audio_data: Raw audio data
            expected_format: Expected audio format
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not audio_data:
                return False
            
            # Basic format validation
            if expected_format.lower() == "wav":
                # Check WAV header
                if len(audio_data) < 44:  # Minimum WAV header size
                    return False
                
                # Check RIFF signature
                if audio_data[:4] != b'RIFF':
                    return False
                
                # Check WAVE signature
                if audio_data[8:12] != b'WAVE':
                    return False
                
                return True
            
            # Add validation for other formats as needed
            return True
            
        except Exception as e:
            logger.error(f"Audio validation error: {e}")
            return False
    
    def analyze_audio_quality(self, audio_data: bytes) -> AudioMetrics:
        """
        Analyze audio quality and extract metrics
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            AudioMetrics object with quality information
        """
        try:
            # Parse WAV header for basic metrics
            metrics = self._parse_wav_header(audio_data)
            
            # Add quality analysis
            if len(audio_data) > 44:  # Has actual audio data
                audio_samples = self._extract_audio_samples(audio_data)
                if audio_samples is not None:
                    metrics.signal_to_noise_ratio = self._calculate_snr(audio_samples)
                    metrics.dynamic_range = self._calculate_dynamic_range(audio_samples)
                    metrics.peak_level = self._calculate_peak_level(audio_samples)
                    metrics.rms_level = self._calculate_rms_level(audio_samples)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Audio analysis error: {e}")
            # Return default metrics
            return AudioMetrics(
                sample_rate=self.default_sample_rate,
                channels=self.default_channels,
                duration=0.0,
                bit_depth=16,
                format="unknown",
                file_size=len(audio_data)
            )
    
    def convert_format(self, audio_data: bytes, 
                      source_format: str, 
                      target_format: str) -> bytes:
        """
        Convert audio between formats
        
        Args:
            audio_data: Source audio data
            source_format: Source format
            target_format: Target format
            
        Returns:
            Converted audio data
        """
        try:
            # For now, implement basic WAV handling
            if source_format.lower() == "wav" and target_format.lower() == "wav":
                return audio_data
            
            # Add format conversion logic as needed
            logger.warning(f"Format conversion {source_format} -> {target_format} not implemented")
            return audio_data
            
        except Exception as e:
            logger.error(f"Format conversion error: {e}")
            return audio_data
    
    def resample_audio(self, audio_data: bytes, 
                      source_rate: int, 
                      target_rate: int) -> bytes:
        """
        Resample audio to different sample rate
        
        Args:
            audio_data: Source audio data
            source_rate: Source sample rate
            target_rate: Target sample rate
            
        Returns:
            Resampled audio data
        """
        try:
            if source_rate == target_rate:
                return audio_data
            
            # Extract samples and resample
            samples = self._extract_audio_samples(audio_data)
            if samples is None:
                return audio_data
            
            # Simple resampling (in production, use proper resampling algorithms)
            ratio = target_rate / source_rate
            new_length = int(len(samples) * ratio)
            
            # Create new indices for resampling
            old_indices = np.linspace(0, len(samples) - 1, new_length)
            resampled = np.interp(old_indices, np.arange(len(samples)), samples)
            
            # Convert back to bytes
            return self._samples_to_wav_bytes(resampled.astype(np.int16), target_rate)
            
        except Exception as e:
            logger.error(f"Resampling error: {e}")
            return audio_data
    
    def create_audio_chunk(self, audio_data: bytes, metadata: Dict[str, Any] = None) -> AudioChunk:
        """
        Create audio chunk with metadata
        
        Args:
            audio_data: Raw audio data
            metadata: Additional metadata
            
        Returns:
            AudioChunk object
        """
        try:
            metrics = self.analyze_audio_quality(audio_data)
            
            chunk = AudioChunk(
                data=audio_data,
                timestamp=datetime.now(),
                duration=metrics.duration,
                sample_rate=metrics.sample_rate,
                channels=metrics.channels,
                format=metrics.format,
                metadata=metadata or {}
            )
            
            self.processed_chunks += 1
            self.total_duration += metrics.duration
            
            return chunk
            
        except Exception as e:
            logger.error(f"Chunk creation error: {e}")
            self.error_count += 1
            
            # Return basic chunk
            return AudioChunk(
                data=audio_data,
                timestamp=datetime.now(),
                duration=0.0,
                sample_rate=self.default_sample_rate,
                channels=self.default_channels,
                format="unknown",
                metadata=metadata or {}
            )
    
    def optimize_for_speech(self, audio_data: bytes) -> bytes:
        """
        Optimize audio for speech recognition and synthesis
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            Optimized audio data
        """
        try:
            # Analyze current quality
            metrics = self.analyze_audio_quality(audio_data)
            
            # Apply speech optimization
            optimized_data = audio_data
            
            # Resample to optimal rate for speech (16kHz)
            if metrics.sample_rate != 16000:
                optimized_data = self.resample_audio(optimized_data, metrics.sample_rate, 16000)
            
            # Add noise reduction, normalization, etc. as needed
            
            return optimized_data
            
        except Exception as e:
            logger.error(f"Speech optimization error: {e}")
            return audio_data
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get audio processing statistics
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            "processed_chunks": self.processed_chunks,
            "total_duration": self.total_duration,
            "error_count": self.error_count,
            "average_chunk_duration": self.total_duration / max(1, self.processed_chunks),
            "error_rate": self.error_count / max(1, self.processed_chunks),
            "quality_level": self.quality_level.value,
            "default_sample_rate": self.default_sample_rate,
            "default_channels": self.default_channels
        }
    
    def reset_stats(self):
        """Reset processing statistics"""
        self.processed_chunks = 0
        self.total_duration = 0.0
        self.error_count = 0
        logger.info("Audio processing statistics reset")
    
    def _parse_wav_header(self, audio_data: bytes) -> AudioMetrics:
        """Parse WAV file header for basic metrics"""
        try:
            if len(audio_data) < 44:
                raise ValueError("Audio data too short for WAV header")
            
            # Parse WAV header
            sample_rate = int.from_bytes(audio_data[24:28], 'little')
            channels = int.from_bytes(audio_data[22:24], 'little')
            bit_depth = int.from_bytes(audio_data[34:36], 'little')
            data_size = int.from_bytes(audio_data[40:44], 'little')
            duration = data_size / (sample_rate * channels * bit_depth // 8)
            
            return AudioMetrics(
                sample_rate=sample_rate,
                channels=channels,
                duration=duration,
                bit_depth=bit_depth,
                format="wav",
                file_size=len(audio_data)
            )
            
        except Exception as e:
            logger.error(f"WAV header parsing error: {e}")
            return AudioMetrics(
                sample_rate=self.default_sample_rate,
                channels=self.default_channels,
                duration=0.0,
                bit_depth=16,
                format="unknown",
                file_size=len(audio_data)
            )
    
    def _extract_audio_samples(self, audio_data: bytes) -> Optional[np.ndarray]:
        """Extract audio samples from WAV data"""
        try:
            if len(audio_data) < 44:
                return None
            
            # Get audio data (skip 44-byte header)
            audio_samples_bytes = audio_data[44:]
            
            # Convert to 16-bit samples
            samples = np.frombuffer(audio_samples_bytes, dtype=np.int16)
            
            return samples
            
        except Exception as e:
            logger.error(f"Sample extraction error: {e}")
            return None
    
    def _calculate_snr(self, samples: np.ndarray) -> float:
        """Calculate signal-to-noise ratio"""
        try:
            # Simple SNR calculation
            signal_power = np.mean(samples.astype(float) ** 2)
            noise_power = np.var(samples.astype(float))
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
                return float(snr)
            
            return 60.0  # High SNR if no noise detected
            
        except Exception as e:
            logger.error(f"SNR calculation error: {e}")
            return 0.0
    
    def _calculate_dynamic_range(self, samples: np.ndarray) -> float:
        """Calculate dynamic range"""
        try:
            max_val = np.max(np.abs(samples))
            min_val = np.min(np.abs(samples[samples != 0]))  # Exclude silence
            
            if min_val > 0:
                dynamic_range = 20 * np.log10(max_val / min_val)
                return float(dynamic_range)
            
            return 96.0  # 16-bit theoretical maximum
            
        except Exception as e:
            logger.error(f"Dynamic range calculation error: {e}")
            return 0.0
    
    def _calculate_peak_level(self, samples: np.ndarray) -> float:
        """Calculate peak level in dB"""
        try:
            peak = np.max(np.abs(samples))
            if peak > 0:
                peak_db = 20 * np.log10(peak / 32767.0)  # 16-bit reference
                return float(peak_db)
            
            return -96.0  # Silence
            
        except Exception as e:
            logger.error(f"Peak level calculation error: {e}")
            return -96.0
    
    def _calculate_rms_level(self, samples: np.ndarray) -> float:
        """Calculate RMS level in dB"""
        try:
            rms = np.sqrt(np.mean(samples.astype(float) ** 2))
            if rms > 0:
                rms_db = 20 * np.log10(rms / 32767.0)  # 16-bit reference
                return float(rms_db)
            
            return -96.0  # Silence
            
        except Exception as e:
            logger.error(f"RMS level calculation error: {e}")
            return -96.0
    
    def _samples_to_wav_bytes(self, samples: np.ndarray, sample_rate: int) -> bytes:
        """Convert audio samples back to WAV bytes"""
        try:
            # Create WAV file in memory
            buffer = io.BytesIO()
            
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(samples.tobytes())
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"WAV bytes conversion error: {e}")
            return b''


# Convenience functions
def create_audio_processor(quality: AudioQuality = AudioQuality.HIGH) -> AudioProcessor:
    """Create AudioProcessor with default settings"""
    return AudioProcessor(quality_level=quality)


def validate_audio_file(audio_data: bytes) -> bool:
    """Quick audio file validation"""
    processor = AudioProcessor()
    return processor.validate_audio_data(audio_data)


def analyze_audio_file(audio_data: bytes) -> AudioMetrics:
    """Quick audio file analysis"""
    processor = AudioProcessor()
    return processor.analyze_audio_quality(audio_data)
