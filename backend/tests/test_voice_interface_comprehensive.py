"""
Comprehensive Voice Interface Tests for Vimarsh AI Agent

This module provides comprehensive testing for voice processing, speech recognition,
text-to-speech, and Sanskrit pronunciation optimization.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any
import json
import base64

from voice.speech_processor import SpeechProcessor
from voice.sanskrit_optimizer import SanskritRecognitionOptimizer
from voice.tts_optimizer import SpiritualTTSOptimizer
from voice.audio_utils import AudioProcessor
from tests.fixtures import SAMPLE_KRISHNA_RESPONSES


class TestSpeechProcessor:
    """Test speech processing functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.processor = SpeechProcessor()
        
    def test_audio_preprocessing(self):
        """Test audio preprocessing for speech recognition."""
        # Mock audio data (base64 encoded)
        mock_audio_data = base64.b64encode(b"fake_audio_data").decode()
        
        processed = self.processor.preprocess_audio(mock_audio_data)
        
        assert processed.sample_rate > 0
        assert processed.duration > 0
        assert processed.audio_format is not None
        assert processed.is_valid is True
        
    @pytest.mark.asyncio
    async def test_speech_to_text_english(self):
        """Test English speech-to-text conversion."""
        with patch('voice.speech_processor.speech.recognize_google') as mock_recognize:
            mock_recognize.return_value = "What is the meaning of dharma?"
            
            # Mock audio file
            mock_audio = Mock()
            
            result = await self.processor.speech_to_text(mock_audio, language="en-US")
            
            assert result.text == "What is the meaning of dharma?"
            assert result.language == "en-US"
            assert result.confidence > 0.8
            
    @pytest.mark.asyncio
    async def test_speech_to_text_hindi(self):
        """Test Hindi speech-to-text conversion."""
        with patch('voice.speech_processor.speech.recognize_google') as mock_recognize:
            mock_recognize.return_value = "धर्म का क्या अर्थ है?"
            
            mock_audio = Mock()
            
            result = await self.processor.speech_to_text(mock_audio, language="hi-IN")
            
            assert result.text == "धर्म का क्या अर्थ है?"
            assert result.language == "hi-IN"
            assert result.contains_hindi is True
            
    def test_noise_reduction(self):
        """Test audio noise reduction."""
        # Mock noisy audio data
        noisy_audio = Mock()
        noisy_audio.sample_rate = 16000
        noisy_audio.duration = 5.0
        
        with patch('voice.speech_processor.nr.reduce_noise') as mock_reduce_noise:
            mock_reduce_noise.return_value = Mock()
            
            cleaned_audio = self.processor.reduce_noise(noisy_audio)
            
            assert cleaned_audio is not None
            mock_reduce_noise.assert_called_once()
            
    def test_voice_activity_detection(self):
        """Test voice activity detection in audio."""
        # Mock audio with speech segments
        audio_segments = [
            {'start': 0.0, 'end': 1.0, 'has_speech': False},  # Silence
            {'start': 1.0, 'end': 4.0, 'has_speech': True},   # Speech
            {'start': 4.0, 'end': 5.0, 'has_speech': False},  # Silence
        ]
        
        speech_segments = self.processor.detect_voice_activity(audio_segments)
        
        assert len(speech_segments) == 1
        assert speech_segments[0]['start'] == 1.0
        assert speech_segments[0]['end'] == 4.0
        
    def test_audio_quality_assessment(self):
        """Test audio quality assessment."""
        # Mock high-quality audio
        high_quality_audio = Mock()
        high_quality_audio.sample_rate = 44100
        high_quality_audio.bit_depth = 16
        high_quality_audio.signal_to_noise_ratio = 25.0
        
        quality = self.processor.assess_audio_quality(high_quality_audio)
        
        assert quality.overall_score > 0.8
        assert quality.is_suitable_for_recognition is True
        
        # Mock low-quality audio
        low_quality_audio = Mock()
        low_quality_audio.sample_rate = 8000
        low_quality_audio.bit_depth = 8
        low_quality_audio.signal_to_noise_ratio = 5.0
        
        low_quality = self.processor.assess_audio_quality(low_quality_audio)
        
        assert low_quality.overall_score < 0.6
        assert low_quality.is_suitable_for_recognition is False


class TestSanskritRecognitionOptimizer:
    """Test Sanskrit recognition optimization."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.optimizer = SanskritRecognitionOptimizer()
        
    def test_sanskrit_term_detection(self):
        """Test detection of Sanskrit terms in transcribed text."""
        text_with_sanskrit = "The concept of dharma and karma are central to yoga philosophy."
        
        detected_terms = self.optimizer.detect_sanskrit_terms(text_with_sanskrit)
        
        assert 'dharma' in detected_terms
        assert 'karma' in detected_terms
        assert 'yoga' in detected_terms
        assert 'concept' not in detected_terms  # English word
        
    def test_pronunciation_correction(self):
        """Test pronunciation-based correction of Sanskrit terms."""
        # Common mispronunciations
        corrections = [
            ("darma", "dharma"),
            ("carma", "karma"),
            ("yog", "yoga"),
            ("mosha", "moksha")
        ]
        
        for mispronounced, correct in corrections:
            corrected = self.optimizer.correct_pronunciation(mispronounced)
            assert corrected == correct
            
    def test_phonetic_mapping(self):
        """Test phonetic mapping for Sanskrit sounds."""
        # Test sound mapping
        phonetic_mappings = {
            "ध": ["dh", "d"],
            "क": ["k", "c"],
            "र": ["r", "ra"],
            "म": ["m", "ma"]
        }
        
        for devanagari, expected_sounds in phonetic_mappings.items():
            mapped_sounds = self.optimizer.get_phonetic_variants(devanagari)
            assert any(sound in mapped_sounds for sound in expected_sounds)
            
    def test_context_aware_correction(self):
        """Test context-aware Sanskrit term correction."""
        # Test in spiritual context
        spiritual_context = "Please explain the meaning of carma in Hindu philosophy."
        corrected = self.optimizer.correct_in_context(spiritual_context)
        assert "karma" in corrected
        assert "carma" not in corrected
        
        # Test in non-spiritual context (should be less aggressive)
        non_spiritual = "I work at carma company."
        non_corrected = self.optimizer.correct_in_context(non_spiritual)
        # Should be more cautious about correction in non-spiritual context
        
    def test_transliteration_support(self):
        """Test transliteration between scripts."""
        # Devanagari to Roman
        devanagari_text = "धर्म"
        romanized = self.optimizer.transliterate_to_roman(devanagari_text)
        assert romanized in ["dharma", "dharm"]
        
        # Roman to Devanagari
        roman_text = "karma"
        devanagari = self.optimizer.transliterate_to_devanagari(roman_text)
        assert "कर्म" in devanagari
        
    def test_confidence_scoring(self):
        """Test confidence scoring for Sanskrit recognition."""
        high_confidence_cases = [
            "dharma is important",
            "karma yoga practice",
            "moksha liberation"
        ]
        
        low_confidence_cases = [
            "drama is important",  # Similar sounding
            "car maintenance",     # Partial match
            "mosh pit"            # Misleading
        ]
        
        for text in high_confidence_cases:
            confidence = self.optimizer.calculate_recognition_confidence(text)
            assert confidence > 0.7
            
        for text in low_confidence_cases:
            confidence = self.optimizer.calculate_recognition_confidence(text)
            assert confidence < 0.5


class TestSpiritualTTSOptimizer:
    """Test text-to-speech optimization for spiritual content."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.tts_optimizer = SpiritualTTSOptimizer()
        
    def test_spiritual_text_preprocessing(self):
        """Test preprocessing of spiritual text for TTS."""
        spiritual_text = """O Arjuna, perform your dharma without attachment. 
        The Sanskrit verse कर्मण्येवाधिकारस्ते teaches this wisdom."""
        
        processed = self.tts_optimizer.preprocess_for_tts(spiritual_text)
        
        assert processed.pronunciation_guide is not None
        assert "dharma" in processed.sanskrit_pronunciations
        assert processed.pause_markers is not None
        assert processed.emphasis_markers is not None
        
    def test_sanskrit_pronunciation_guidance(self):
        """Test Sanskrit pronunciation guidance generation."""
        sanskrit_terms = ["dharma", "karma", "yoga", "moksha"]
        
        for term in sanskrit_terms:
            pronunciation = self.tts_optimizer.get_pronunciation_guide(term)
            assert pronunciation.phonetic_spelling is not None
            assert pronunciation.syllable_breakdown is not None
            assert pronunciation.stress_pattern is not None
            
    def test_voice_selection_optimization(self):
        """Test voice selection for different content types."""
        # Test for reverent content
        reverent_content = "Lord Krishna graciously imparts divine wisdom..."
        reverent_voice = self.tts_optimizer.select_optimal_voice(
            reverent_content, 
            language="en-US",
            context="divine_teaching"
        )
        
        assert reverent_voice.style == "calm"
        assert reverent_voice.pace == "slow"
        assert reverent_voice.tone == "reverent"
        
        # Test for explanatory content
        explanatory_content = "The concept of dharma can be understood as..."
        explanatory_voice = self.tts_optimizer.select_optimal_voice(
            explanatory_content,
            language="en-US", 
            context="explanation"
        )
        
        assert explanatory_voice.style == "clear"
        assert explanatory_voice.pace == "medium"
        
    @pytest.mark.asyncio
    async def test_multilingual_tts_generation(self):
        """Test multilingual TTS generation."""
        with patch('voice.tts_optimizer.texttospeech.TextToSpeechClient') as mock_tts:
            mock_response = Mock()
            mock_response.audio_content = b"fake_audio_data"
            mock_tts.return_value.synthesize_speech.return_value = mock_response
            
            # Test English
            english_text = "Dharma is the righteous path of action."
            english_audio = await self.tts_optimizer.generate_speech(
                english_text, 
                language="en-US"
            )
            
            assert english_audio.audio_data is not None
            assert english_audio.language == "en-US"
            
            # Test Hindi
            hindi_text = "धर्म सही कार्य का मार्ग है।"
            hindi_audio = await self.tts_optimizer.generate_speech(
                hindi_text,
                language="hi-IN"
            )
            
            assert hindi_audio.audio_data is not None
            assert hindi_audio.language == "hi-IN"
            
    def test_emotional_tone_adjustment(self):
        """Test emotional tone adjustment for spiritual content."""
        # Test peaceful content
        peaceful_content = "Find inner peace through meditation and self-reflection."
        peaceful_config = self.tts_optimizer.adjust_emotional_tone(
            peaceful_content,
            target_emotion="peaceful"
        )
        
        assert peaceful_config.speaking_rate < 1.0  # Slower pace
        assert peaceful_config.pitch < 0.0         # Lower pitch
        
        # Test inspiring content
        inspiring_content = "Rise above challenges with courage and determination!"
        inspiring_config = self.tts_optimizer.adjust_emotional_tone(
            inspiring_content,
            target_emotion="inspiring"
        )
        
        assert inspiring_config.speaking_rate > 1.0  # Faster pace
        assert inspiring_config.pitch > 0.0         # Higher pitch
        
    def test_pause_and_emphasis_optimization(self):
        """Test pause and emphasis optimization."""
        text_with_citations = """Lord Krishna teaches in Bhagavad Gita, Chapter 2, Verse 47: 
        "You have a right to perform your duties, but never to the fruits of action."
        This profound wisdom guides us toward selfless service."""
        
        optimized = self.tts_optimizer.optimize_pauses_and_emphasis(text_with_citations)
        
        # Should have pauses before citations
        assert any(marker.type == "pause" for marker in optimized.markers)
        # Should emphasize quoted text
        assert any(marker.type == "emphasis" for marker in optimized.markers)
        # Should have reverent pace for divine quotes
        assert any(marker.duration > 1.0 for marker in optimized.markers if marker.type == "pause")


class TestAudioProcessor:
    """Test audio processing utilities."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.processor = AudioProcessor()
        
    def test_audio_format_conversion(self):
        """Test audio format conversion."""
        # Mock various audio formats
        mock_formats = ['wav', 'mp3', 'ogg', 'flac']
        
        for source_format in mock_formats:
            for target_format in mock_formats:
                if source_format != target_format:
                    mock_audio = Mock()
                    mock_audio.format = source_format
                    
                    with patch('voice.audio_utils.AudioSegment.from_file') as mock_from_file:
                        with patch.object(mock_from_file.return_value, 'export') as mock_export:
                            converted = self.processor.convert_format(
                                mock_audio, 
                                target_format
                            )
                            
                            mock_export.assert_called_once()
                            
    def test_audio_compression(self):
        """Test audio compression for web delivery."""
        mock_high_quality_audio = Mock()
        mock_high_quality_audio.size_bytes = 10 * 1024 * 1024  # 10MB
        mock_high_quality_audio.bitrate = 320000  # 320 kbps
        
        compressed = self.processor.compress_for_web(mock_high_quality_audio)
        
        assert compressed.target_bitrate <= 128000  # Max 128 kbps for web
        assert compressed.optimization_applied is True
        
    def test_audio_segmentation(self):
        """Test audio segmentation for long spiritual content."""
        # Mock long audio (10 minutes)
        long_audio = Mock()
        long_audio.duration = 600.0  # 10 minutes
        
        segments = self.processor.segment_long_audio(
            long_audio, 
            max_segment_duration=120.0  # 2 minutes
        )
        
        assert len(segments) == 5  # Should create 5 segments
        assert all(segment.duration <= 120.0 for segment in segments)
        
    def test_silence_detection_and_removal(self):
        """Test silence detection and removal."""
        # Mock audio with silence
        audio_with_silence = Mock()
        audio_with_silence.silence_segments = [
            {'start': 0.0, 'end': 2.0},      # Initial silence
            {'start': 10.0, 'end': 12.0},    # Middle silence
            {'start': 25.0, 'end': 30.0}     # End silence
        ]
        
        cleaned_audio = self.processor.remove_excessive_silence(
            audio_with_silence,
            max_silence_duration=1.0
        )
        
        assert cleaned_audio.silence_removed is True
        assert cleaned_audio.original_duration > cleaned_audio.final_duration
        
    def test_audio_quality_enhancement(self):
        """Test audio quality enhancement."""
        low_quality_audio = Mock()
        low_quality_audio.sample_rate = 8000
        low_quality_audio.quality_score = 0.4
        
        enhanced = self.processor.enhance_audio_quality(low_quality_audio)
        
        assert enhanced.sample_rate >= 16000  # Upsampled
        assert enhanced.noise_reduced is True
        assert enhanced.quality_score > low_quality_audio.quality_score


class TestVoiceIntegrationWorkflows:
    """Test complete voice integration workflows."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment."""
        self.speech_processor = SpeechProcessor()
        self.sanskrit_optimizer = SanskritRecognitionOptimizer()
        self.tts_optimizer = SpiritualTTSOptimizer()
        
    @pytest.mark.asyncio
    async def test_complete_voice_to_voice_workflow(self):
        """Test complete voice-to-voice spiritual guidance workflow."""
        # Mock voice input processing
        with patch.object(self.speech_processor, 'speech_to_text') as mock_stt:
            mock_stt.return_value = Mock(
                text="What is dharma in modern life?",
                language="en-US",
                confidence=0.9
            )
            
            # Mock Sanskrit optimization
            with patch.object(self.sanskrit_optimizer, 'optimize_recognition') as mock_optimize:
                mock_optimize.return_value = "What is dharma in modern life?"
                
                # Mock TTS generation
                with patch.object(self.tts_optimizer, 'generate_speech') as mock_tts:
                    mock_audio_response = Mock()
                    mock_audio_response.audio_data = b"spiritual_response_audio"
                    mock_audio_response.duration = 45.0
                    mock_tts.return_value = mock_audio_response
                    
                    # Simulate complete workflow
                    mock_audio_input = Mock()
                    
                    # Step 1: Speech to text
                    text_result = await self.speech_processor.speech_to_text(mock_audio_input)
                    
                    # Step 2: Optimize Sanskrit recognition
                    optimized_text = self.sanskrit_optimizer.optimize_recognition(text_result.text)
                    
                    # Step 3: Generate spiritual guidance (mocked)
                    spiritual_response = SAMPLE_KRISHNA_RESPONSES["dharma_modern"]["response"]
                    
                    # Step 4: Convert response to speech
                    audio_response = await self.tts_optimizer.generate_speech(
                        spiritual_response,
                        language="en-US"
                    )
                    
                    # Verify complete workflow
                    assert text_result.text == "What is dharma in modern life?"
                    assert optimized_text == "What is dharma in modern life?"
                    assert audio_response.audio_data is not None
                    assert audio_response.duration > 0
                    
    @pytest.mark.asyncio
    async def test_multilingual_voice_workflow(self):
        """Test multilingual voice processing workflow."""
        # Test Hindi voice input
        with patch.object(self.speech_processor, 'speech_to_text') as mock_stt:
            mock_stt.return_value = Mock(
                text="आधुनिक जीवन में धर्म क्या है?",
                language="hi-IN",
                confidence=0.85
            )
            
            with patch.object(self.tts_optimizer, 'generate_speech') as mock_tts:
                mock_tts.return_value = Mock(
                    audio_data=b"hindi_response_audio",
                    language="hi-IN",
                    duration=50.0
                )
                
                # Process Hindi input
                mock_audio_input = Mock()
                text_result = await self.speech_processor.speech_to_text(
                    mock_audio_input, 
                    language="hi-IN"
                )
                
                # Generate Hindi response
                hindi_response = "धर्म जीवन का मार्गदर्शक सिद्धांत है..."
                audio_response = await self.tts_optimizer.generate_speech(
                    hindi_response,
                    language="hi-IN"
                )
                
                assert text_result.language == "hi-IN"
                assert audio_response.language == "hi-IN"
                
    def test_error_handling_in_voice_workflow(self):
        """Test error handling in voice processing workflow."""
        # Test handling of poor audio quality
        poor_audio = Mock()
        poor_audio.quality_score = 0.2
        poor_audio.is_suitable_for_recognition = False
        
        with patch.object(self.speech_processor, 'assess_audio_quality') as mock_assess:
            mock_assess.return_value = poor_audio
            
            with pytest.raises(ValueError, match="audio quality"):
                self.speech_processor.process_voice_input(poor_audio)
                
        # Test handling of unrecognized speech
        with patch.object(self.speech_processor, 'speech_to_text') as mock_stt:
            mock_stt.side_effect = Exception("Recognition failed")
            
            result = self.speech_processor.safe_speech_to_text(Mock())
            
            assert result.success is False
            assert "recognition failed" in result.error_message.lower()
