"""
Unit Tests for Speech Processing Components

This module contains comprehensive tests for the speech processing functionality
in the Vimarsh AI Agent voice interface.
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from .speech_processor import (
    SpeechProcessor,
    VoiceConfig,
    RecognitionResult,
    VoiceLanguage,
    SpeechQuality,
    RecognitionStatus,
    create_spiritual_speech_processor
)


class TestVoiceConfig:
    """Test VoiceConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = VoiceConfig()
        
        assert config.language == VoiceLanguage.ENGLISH
        assert config.quality == SpeechQuality.HIGH
        assert config.continuous is True
        assert config.interim_results is True
        assert config.max_alternatives == 3
        assert config.sanskrit_support is True
        assert config.spiritual_vocabulary_boost is True
        assert config.timeout_seconds == 30.0
        assert config.confidence_threshold == 0.7
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = VoiceConfig(
            language=VoiceLanguage.HINDI,
            quality=SpeechQuality.PREMIUM,
            continuous=False,
            sanskrit_support=False,
            confidence_threshold=0.8
        )
        
        assert config.language == VoiceLanguage.HINDI
        assert config.quality == SpeechQuality.PREMIUM
        assert config.continuous is False
        assert config.sanskrit_support is False
        assert config.confidence_threshold == 0.8


class TestRecognitionResult:
    """Test RecognitionResult class"""
    
    def test_basic_result(self):
        """Test basic recognition result"""
        result = RecognitionResult(
            transcript="Test transcript",
            confidence=0.85,
            language=VoiceLanguage.ENGLISH
        )
        
        assert result.transcript == "Test transcript"
        assert result.confidence == 0.85
        assert result.language == VoiceLanguage.ENGLISH
        assert result.status == RecognitionStatus.COMPLETED
        assert isinstance(result.timestamp, datetime)
    
    def test_spiritual_content_result(self):
        """Test result with spiritual content"""
        result = RecognitionResult(
            transcript="What is dharma according to Krishna?",
            confidence=0.9,
            language=VoiceLanguage.ENGLISH,
            contains_sanskrit=True,
            spiritual_terms=["dharma"],
            deity_references=["krishna"]
        )
        
        assert result.contains_sanskrit is True
        assert "dharma" in result.spiritual_terms
        assert "krishna" in result.deity_references


class TestSpeechProcessor:
    """Test SpeechProcessor class"""
    
    @pytest.fixture
    def processor(self):
        """Create speech processor for testing"""
        return SpeechProcessor()
    
    @pytest.fixture
    def custom_processor(self):
        """Create speech processor with custom config"""
        config = VoiceConfig(
            language=VoiceLanguage.HINDI,
            quality=SpeechQuality.PREMIUM,
            confidence_threshold=0.8
        )
        return SpeechProcessor(config)
    
    def test_initialization(self, processor):
        """Test speech processor initialization"""
        assert processor.config.language == VoiceLanguage.ENGLISH
        assert processor.is_listening is False
        assert processor.current_session_id is None
        assert len(processor.recognition_history) == 0
        assert isinstance(processor.sanskrit_terms, dict)
        assert isinstance(processor.deity_names, dict)
        assert isinstance(processor.mantras, list)
    
    def test_sanskrit_vocabulary_loading(self, processor):
        """Test Sanskrit vocabulary loading"""
        assert 'dharma' in processor.sanskrit_terms
        assert 'karma' in processor.sanskrit_terms
        assert 'yoga' in processor.sanskrit_terms
        assert 'moksha' in processor.sanskrit_terms
        
        # Test variations
        assert 'dharma' in processor.sanskrit_terms['dharma']
        assert 'dhamma' in processor.sanskrit_terms['dharma']
    
    def test_deity_names_loading(self, processor):
        """Test deity names loading"""
        assert 'krishna' in processor.deity_names
        assert 'rama' in processor.deity_names
        assert 'shiva' in processor.deity_names
        
        # Test variations
        assert 'govinda' in processor.deity_names['krishna']
        assert 'shankar' in processor.deity_names['shiva']
    
    def test_mantras_loading(self, processor):
        """Test mantras loading"""
        assert 'om' in processor.mantras
        assert 'om namah shivaya' in processor.mantras
        assert 'hare krishna' in processor.mantras
    
    @pytest.mark.asyncio
    async def test_start_recognition(self, processor):
        """Test starting recognition"""
        session_id = await processor.start_recognition()
        
        assert processor.is_listening is True
        assert processor.current_session_id == session_id
        assert session_id.startswith("session_")
    
    @pytest.mark.asyncio
    async def test_start_recognition_custom_session(self, processor):
        """Test starting recognition with custom session ID"""
        custom_id = "test_session_123"
        session_id = await processor.start_recognition(custom_id)
        
        assert processor.is_listening is True
        assert processor.current_session_id == custom_id
        assert session_id == custom_id
    
    @pytest.mark.asyncio
    async def test_start_recognition_already_listening(self, processor):
        """Test starting recognition when already listening"""
        await processor.start_recognition()
        
        with pytest.raises(RuntimeError):
            await processor.start_recognition()
    
    @pytest.mark.asyncio
    async def test_stop_recognition(self, processor):
        """Test stopping recognition"""
        session_id = await processor.start_recognition()
        result = await processor.stop_recognition()
        
        assert processor.is_listening is False
        assert processor.current_session_id is None
    
    @pytest.mark.asyncio
    async def test_stop_recognition_not_listening(self, processor):
        """Test stopping recognition when not listening"""
        result = await processor.stop_recognition()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_process_audio_data(self, processor):
        """Test processing audio data"""
        audio_data = b'\x00' * 1000  # Dummy audio data
        sample_rate = 16000
        
        result = await processor.process_audio_data(audio_data, sample_rate)
        
        assert isinstance(result, RecognitionResult)
        assert len(result.transcript) > 0
        assert 0.0 <= result.confidence <= 1.0
        assert result.status == RecognitionStatus.COMPLETED
        assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_spiritual_content_enhancement(self, processor):
        """Test spiritual content enhancement"""
        # Create a result with spiritual content
        result = RecognitionResult(
            transcript="What is dharma according to Krishna in the Bhagavad Gita?",
            confidence=0.8,
            language=VoiceLanguage.ENGLISH
        )
        
        await processor._enhance_spiritual_recognition(result)
        
        assert result.contains_sanskrit is True
        assert 'dharma' in result.spiritual_terms
        assert 'krishna' in result.deity_references
        assert 'bhagavad gita' in result.spiritual_terms
        assert result.confidence > 0.8  # Should be boosted
    
    @pytest.mark.asyncio
    async def test_mantra_detection(self, processor):
        """Test mantra detection"""
        result = RecognitionResult(
            transcript="Please guide me in chanting Om Namah Shivaya",
            confidence=0.8,
            language=VoiceLanguage.ENGLISH
        )
        
        await processor._enhance_spiritual_recognition(result)
        
        assert 'om namah shivaya' in result.detected_mantras
        assert 'shiva' in result.deity_references
    
    def test_recognition_stats_update(self, processor):
        """Test recognition statistics update"""
        # Create successful result
        result = RecognitionResult(
            transcript="Test transcript",
            confidence=0.9,
            language=VoiceLanguage.ENGLISH
        )
        
        processor._update_recognition_stats(result, 100.0)
        
        stats = processor.get_recognition_stats()
        assert stats['total_requests'] == 1
        assert stats['successful_recognitions'] == 1
        assert stats['failed_recognitions'] == 0
        assert stats['success_rate'] == 1.0
        assert stats['average_confidence'] == 0.9
        assert stats['average_processing_time'] == 100.0
    
    def test_recognition_stats_failure(self, processor):
        """Test recognition statistics for failures"""
        # Create failed result
        result = RecognitionResult(
            transcript="",
            confidence=0.3,  # Below threshold
            language=VoiceLanguage.ENGLISH,
            status=RecognitionStatus.ERROR
        )
        
        processor._update_recognition_stats(result, 50.0)
        
        stats = processor.get_recognition_stats()
        assert stats['total_requests'] == 1
        assert stats['successful_recognitions'] == 0
        assert stats['failed_recognitions'] == 1
        assert stats['failure_rate'] == 1.0
    
    def test_get_recognition_history(self, processor):
        """Test getting recognition history"""
        # Add some results to history
        for i in range(5):
            result = RecognitionResult(
                transcript=f"Test {i}",
                confidence=0.8,
                language=VoiceLanguage.ENGLISH
            )
            processor.recognition_history.append(result)
        
        # Test limited history
        history = processor.get_recognition_history(3)
        assert len(history) == 3
        assert history[0].transcript == "Test 2"
        assert history[2].transcript == "Test 4"
        
        # Test full history
        full_history = processor.get_recognition_history()
        assert len(full_history) == 5
    
    def test_update_config(self, processor):
        """Test updating configuration"""
        new_config = VoiceConfig(
            language=VoiceLanguage.HINDI,
            quality=SpeechQuality.PREMIUM,
            confidence_threshold=0.9
        )
        
        processor.update_config(new_config)
        
        assert processor.config.language == VoiceLanguage.HINDI
        assert processor.config.quality == SpeechQuality.PREMIUM
        assert processor.config.confidence_threshold == 0.9
    
    def test_reset_stats(self, processor):
        """Test resetting statistics"""
        # Add some stats
        processor.recognition_stats['total_requests'] = 10
        processor.recognition_stats['successful_recognitions'] = 8
        
        processor.reset_stats()
        
        stats = processor.get_recognition_stats()
        assert stats['total_requests'] == 0
        assert stats['successful_recognitions'] == 0
        assert stats['success_rate'] == 0.0
    
    @pytest.mark.asyncio
    async def test_optimize_for_spiritual_content(self, processor):
        """Test optimization for spiritual content"""
        # Add spiritual content to history
        for i in range(10):
            result = RecognitionResult(
                transcript=f"What is dharma according to Krishna? {i}",
                confidence=0.8,
                language=VoiceLanguage.ENGLISH,
                contains_sanskrit=True,
                spiritual_terms=['dharma'],
                deity_references=['krishna']
            )
            processor.recognition_history.append(result)
        
        optimization = await processor.optimize_for_spiritual_content()
        
        assert optimization['spiritual_content_ratio'] == 1.0
        assert optimization['sanskrit_content_ratio'] == 1.0
        assert optimization['average_confidence'] == 0.8
        assert len(optimization['recommendations']) > 0


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_create_spiritual_speech_processor(self):
        """Test creating spiritual speech processor"""
        processor = create_spiritual_speech_processor(
            language=VoiceLanguage.HINDI,
            quality=SpeechQuality.PREMIUM
        )
        
        assert isinstance(processor, SpeechProcessor)
        assert processor.config.language == VoiceLanguage.HINDI
        assert processor.config.quality == SpeechQuality.PREMIUM
        assert processor.config.sanskrit_support is True
        assert processor.config.spiritual_vocabulary_boost is True
        assert processor.config.deity_name_recognition is True
        assert processor.config.confidence_threshold == 0.6  # Lower for spiritual content


# Integration tests
class TestSpeechProcessorIntegration:
    """Integration tests for speech processor"""
    
    @pytest.mark.asyncio
    async def test_full_recognition_workflow(self):
        """Test complete recognition workflow"""
        processor = create_spiritual_speech_processor()
        
        # Start recognition
        session_id = await processor.start_recognition()
        assert processor.is_listening is True
        
        # Process audio
        audio_data = b'\x00' * 2000
        result = await processor.process_audio_data(audio_data)
        
        assert isinstance(result, RecognitionResult)
        assert len(result.transcript) > 0
        
        # Stop recognition
        final_result = await processor.stop_recognition()
        assert processor.is_listening is False
        
        # Check stats
        stats = processor.get_recognition_stats()
        assert stats['total_requests'] >= 1
    
    @pytest.mark.asyncio 
    async def test_error_handling_workflow(self):
        """Test error handling in recognition workflow"""
        processor = SpeechProcessor()
        
        # Mock an error during processing
        with patch.object(processor, '_simulate_recognition', side_effect=Exception("Test error")):
            result = await processor.process_audio_data(b'\x00' * 1000)
            
            assert result.status == RecognitionStatus.ERROR
            assert result.error_message == "Test error"
            assert result.confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_continuous_recognition(self):
        """Test continuous recognition with multiple audio chunks"""
        processor = create_spiritual_speech_processor()
        
        await processor.start_recognition()
        
        # Process multiple audio chunks
        results = []
        for i in range(3):
            audio_data = b'\x00' * (1000 + i * 500)
            result = await processor.process_audio_data(audio_data)
            results.append(result)
        
        await processor.stop_recognition()
        
        assert len(results) == 3
        assert all(isinstance(r, RecognitionResult) for r in results)
        assert len(processor.recognition_history) >= 3
        
        # Check that stats accumulated
        stats = processor.get_recognition_stats()
        assert stats['total_requests'] >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
