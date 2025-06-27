"""
Comprehensive unit tests for voice interface components.

Tests speech processing, Sanskrit optimization, TTS functionality,
multilingual support, and voice error recovery systems.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import tempfile
import os
import time

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from voice.speech_processor import SpeechProcessor
from voice.sanskrit_optimizer import SanskritRecognitionOptimizer
from voice.tts_optimizer import SpiritualTTSOptimizer
from voice.multilingual import MultilingualVoiceManager
from voice.voice_recovery import SpiritualVoiceRecovery
from voice.tts_optimizer import SpiritualTTSOptimizer
from voice.multilingual import MultilingualVoiceManager
from voice.voice_recovery import SpiritualVoiceRecovery
from voice.quality_monitor import VoiceQualityMonitor
from tests.fixtures import (
    VOICE_TEST_DATA, PERFORMANCE_BENCHMARKS, ERROR_TEST_SCENARIOS,
    SAMPLE_KRISHNA_RESPONSES
)


class TestSpeechProcessor:
    """Test suite for SpeechProcessor class."""
    
    @pytest.fixture
    def speech_processor(self):
        """Create SpeechProcessor instance for testing."""
        return SpeechProcessor()
    
    def test_speech_processor_initialization(self, speech_processor):
        """Test speech processor initialization."""
        assert speech_processor is not None
        assert hasattr(speech_processor, 'supported_languages')
        assert hasattr(speech_processor, 'quality_settings')
        assert 'en-US' in speech_processor.supported_languages
        assert 'hi-IN' in speech_processor.supported_languages
    
    @pytest.mark.asyncio
    async def test_process_audio_basic(self, speech_processor):
        """Test basic audio processing functionality."""
        # Mock audio data
        mock_audio_data = b"mock_audio_bytes"
        
        with patch.object(speech_processor, '_recognize_speech') as mock_recognize:
            mock_recognize.return_value = {
                "text": "What is dharma according to Krishna?",
                "confidence": 0.95,
                "language": "en-US"
            }
            
            result = await speech_processor.process_audio(mock_audio_data)
            
            assert result is not None
            assert "text" in result
            assert "confidence" in result
            assert result["confidence"] > 0.8
            assert "dharma" in result["text"].lower()
    
    @pytest.mark.asyncio
    async def test_multilingual_speech_recognition(self, speech_processor):
        """Test speech recognition in multiple languages."""
        test_cases = [
            {
                "audio": b"english_audio",
                "expected_text": "What is my duty in life?",
                "language": "en-US"
            },
            {
                "audio": b"hindi_audio", 
                "expected_text": "मेरा जीवन में क्या कर्तव्य है?",
                "language": "hi-IN"
            }
        ]
        
        for case in test_cases:
            with patch.object(speech_processor, '_recognize_speech') as mock_recognize:
                mock_recognize.return_value = {
                    "text": case["expected_text"],
                    "confidence": 0.9,
                    "language": case["language"]
                }
                
                result = await speech_processor.process_audio(
                    case["audio"], 
                    language=case["language"]
                )
                
                assert result["text"] == case["expected_text"]
                assert result["language"] == case["language"]
    
    @pytest.mark.asyncio
    async def test_noise_reduction(self, speech_processor):
        """Test noise reduction in audio processing."""
        noisy_audio = b"noisy_mock_audio"
        
        with patch.object(speech_processor, '_reduce_noise') as mock_denoise:
            mock_denoise.return_value = b"clean_audio"
            
            with patch.object(speech_processor, '_recognize_speech') as mock_recognize:
                mock_recognize.return_value = {
                    "text": "Clear spiritual question",
                    "confidence": 0.95,
                    "language": "en-US"
                }
                
                result = await speech_processor.process_audio(
                    noisy_audio, 
                    noise_reduction=True
                )
                
                # Should improve recognition confidence
                assert result["confidence"] > 0.9
                mock_denoise.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_audio(self, speech_processor):
        """Test handling of invalid or corrupted audio."""
        invalid_audio_cases = [
            b"",  # Empty audio
            b"invalid_format",  # Invalid format
            None,  # None value
        ]
        
        for invalid_audio in invalid_audio_cases:
            result = await speech_processor.process_audio(invalid_audio)
            
            assert result is not None
            assert "error" in result or result.get("confidence", 0) == 0
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, speech_processor):
        """Test that speech processing meets performance requirements."""
        mock_audio = b"test_audio_data"
        
        with patch.object(speech_processor, '_recognize_speech') as mock_recognize:
            mock_recognize.return_value = {
                "text": "Quick test",
                "confidence": 0.9,
                "language": "en-US"
            }
            
            start_time = time.time()
            result = await speech_processor.process_audio(mock_audio)
            elapsed_time = time.time() - start_time
            
            # Should process audio quickly for real-time interaction
            assert elapsed_time < 2.0  # Within 2 seconds
            assert result is not None


class TestSanskritOptimizer:
    """Test suite for SanskritOptimizer class."""
    
    @pytest.fixture
    def sanskrit_optimizer(self):
        """Create SanskritOptimizer instance for testing."""
        return SanskritOptimizer()
    
    def test_sanskrit_optimizer_initialization(self, sanskrit_optimizer):
        """Test Sanskrit optimizer initialization."""
        assert sanskrit_optimizer is not None
        assert hasattr(sanskrit_optimizer, 'sanskrit_phonemes')
        assert hasattr(sanskrit_optimizer, 'pronunciation_rules')
    
    def test_sanskrit_term_detection(self, sanskrit_optimizer):
        """Test detection of Sanskrit terms in text."""
        texts_with_sanskrit = [
            "The concept of dharma is central to Krishna's teachings.",
            "Karma yoga involves selfless action without attachment.",
            "The Bhagavad Gita teaches about moksha and liberation.",
            "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन - this verse teaches duty."
        ]
        
        for text in texts_with_sanskrit:
            detected_terms = sanskrit_optimizer.detect_sanskrit_terms(text)
            assert len(detected_terms) > 0
            
            # Should detect common Sanskrit spiritual terms
            expected_terms = ['dharma', 'karma', 'moksha', 'bhagavad', 'gita']
            found_expected = any(term in detected_terms for term in expected_terms)
            assert found_expected
    
    def test_pronunciation_guide_generation(self, sanskrit_optimizer):
        """Test generation of pronunciation guides for Sanskrit terms."""
        sanskrit_terms = ["dharma", "karma", "moksha", "bhagavad", "krishna"]
        
        for term in sanskrit_terms:
            pronunciation = sanskrit_optimizer.get_pronunciation_guide(term)
            
            assert pronunciation is not None
            assert "ipa" in pronunciation or "phonetic" in pronunciation
            assert "difficulty" in pronunciation
            
            # Verify known pronunciations
            if term == "dharma":
                assert "dhar" in pronunciation["phonetic"].lower()
            elif term == "karma":
                assert "kar" in pronunciation["phonetic"].lower()
    
    def test_text_optimization_for_tts(self, sanskrit_optimizer):
        """Test text optimization for TTS pronunciation."""
        original_text = "Krishna teaches about dharma and karma in the Bhagavad Gita."
        
        optimized = sanskrit_optimizer.optimize_for_tts(original_text)
        
        assert optimized is not None
        assert len(optimized) > 0
        
        # Should include pronunciation hints or phonetic spellings
        assert "krishna" in optimized.lower() or "krish-na" in optimized.lower()
        assert "dharma" in optimized.lower() or "dhar-ma" in optimized.lower()
    
    def test_multilingual_sanskrit_handling(self, sanskrit_optimizer):
        """Test handling of Sanskrit in different language contexts."""
        # English context
        english_text = "The dharma of a warrior is to fight righteously."
        optimized_en = sanskrit_optimizer.optimize_for_tts(english_text, target_language="en")
        
        # Hindi context  
        hindi_text = "धर्म और कर्म के बारे में कृष्ण की शिक्षा।"
        optimized_hi = sanskrit_optimizer.optimize_for_tts(hindi_text, target_language="hi")
        
        assert optimized_en != optimized_hi
        assert len(optimized_en) > 0
        assert len(optimized_hi) > 0
    
    def test_accent_and_stress_patterns(self, sanskrit_optimizer):
        """Test proper accent and stress pattern suggestions."""
        complex_terms = ["mahabharata", "srimad bhagavatam", "karmanye vadhikaraste"]
        
        for term in complex_terms:
            stress_pattern = sanskrit_optimizer.get_stress_pattern(term)
            
            assert stress_pattern is not None
            assert "syllables" in stress_pattern
            assert "primary_stress" in stress_pattern
            assert len(stress_pattern["syllables"]) > 1


class TestTTSOptimizer:
    """Test suite for TTSOptimizer class."""
    
    @pytest.fixture
    def tts_optimizer(self):
        """Create TTSOptimizer instance for testing."""
        return TTSOptimizer()
    
    def test_tts_optimizer_initialization(self, tts_optimizer):
        """Test TTS optimizer initialization."""
        assert tts_optimizer is not None
        assert hasattr(tts_optimizer, 'voice_profiles')
        assert hasattr(tts_optimizer, 'spiritual_voice_settings')
    
    @pytest.mark.asyncio
    async def test_generate_spiritual_audio(self, tts_optimizer):
        """Test generation of spiritual audio content."""
        spiritual_text = "O beloved soul, let the divine wisdom of dharma guide your path towards eternal peace and liberation."
        
        with patch.object(tts_optimizer, '_call_tts_api') as mock_tts:
            mock_tts.return_value = {
                "audio_data": b"mock_audio_bytes",
                "duration": 5.2,
                "quality": "high"
            }
            
            result = await tts_optimizer.generate_audio(
                text=spiritual_text,
                voice_profile="divine_male",
                language="en"
            )
            
            assert result is not None
            assert "audio_data" in result
            assert "duration" in result
            assert result["duration"] > 0
    
    @pytest.mark.asyncio
    async def test_voice_profile_selection(self, tts_optimizer):
        """Test selection of appropriate voice profiles."""
        content_types = [
            {
                "text": "Divine guidance from Lord Krishna",
                "expected_profile": "divine_male",
                "tone": "authoritative_compassionate"
            },
            {
                "text": "Gentle wisdom for inner peace",
                "expected_profile": "gentle_wise",
                "tone": "soft_guidance"
            },
            {
                "text": "Sanskrit verse recitation",
                "expected_profile": "sanskrit_chant",
                "tone": "sacred_recitation"
            }
        ]
        
        for content in content_types:
            profile = tts_optimizer.select_voice_profile(
                content["text"], 
                tone=content["tone"]
            )
            
            assert profile is not None
            assert profile in tts_optimizer.voice_profiles
            # Profile should be appropriate for spiritual content
            assert "divine" in profile or "wise" in profile or "sacred" in profile
    
    @pytest.mark.asyncio 
    async def test_multilingual_tts(self, tts_optimizer):
        """Test TTS generation in multiple languages."""
        test_cases = [
            {
                "text": "Divine wisdom guides your path",
                "language": "en",
                "expected_voice": "en-US-Neural"
            },
            {
                "text": "दिव्य ज्ञान आपके मार्ग का मार्गदर्शन करता है",
                "language": "hi", 
                "expected_voice": "hi-IN-Neural"
            }
        ]
        
        for case in test_cases:
            with patch.object(tts_optimizer, '_call_tts_api') as mock_tts:
                mock_tts.return_value = {
                    "audio_data": b"audio_bytes",
                    "language": case["language"]
                }
                
                result = await tts_optimizer.generate_audio(
                    text=case["text"],
                    language=case["language"]
                )
                
                assert result["language"] == case["language"]
                mock_tts.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_audio_quality_optimization(self, tts_optimizer):
        """Test audio quality optimization features."""
        spiritual_text = "Let peace and wisdom fill your heart with divine light."
        
        quality_levels = ["standard", "high", "premium"]
        
        for quality in quality_levels:
            with patch.object(tts_optimizer, '_call_tts_api') as mock_tts:
                mock_tts.return_value = {
                    "audio_data": b"quality_audio",
                    "quality": quality,
                    "bitrate": "128kbps" if quality == "standard" else "256kbps"
                }
                
                result = await tts_optimizer.generate_audio(
                    text=spiritual_text,
                    quality=quality
                )
                
                assert result["quality"] == quality
                if quality == "premium":
                    assert "256kbps" in result["bitrate"]
    
    @pytest.mark.asyncio
    async def test_error_handling_tts_failure(self, tts_optimizer):
        """Test handling of TTS API failures."""
        text = "Test spiritual guidance"
        
        with patch.object(tts_optimizer, '_call_tts_api') as mock_tts:
            mock_tts.side_effect = Exception("TTS API Error")
            
            result = await tts_optimizer.generate_audio(text)
            
            # Should handle error gracefully
            assert result is not None
            assert "error" in result or "fallback" in result


class TestMultilingualVoiceManager:
    """Test suite for MultilingualVoiceManager class."""
    
    @pytest.fixture
    def multilingual_handler(self):
        """Create MultilingualVoiceManager instance for testing."""
        return MultilingualVoiceManager()
    
    def test_multilingual_handler_initialization(self, multilingual_handler):
        """Test multilingual handler initialization."""
        assert multilingual_handler is not None
        assert hasattr(multilingual_handler, 'supported_languages')
        assert 'en' in multilingual_handler.supported_languages
        assert 'hi' in multilingual_handler.supported_languages
    
    def test_language_detection(self, multilingual_handler):
        """Test automatic language detection from text."""
        test_cases = [
            {
                "text": "What is dharma according to Krishna?",
                "expected_language": "en"
            },
            {
                "text": "कृष्ण के अनुसार धर्म क्या है?",
                "expected_language": "hi"
            },
            {
                "text": "Mixed text with धर्म and English words",
                "expected_language": "mixed"
            }
        ]
        
        for case in test_cases:
            detected = multilingual_handler.detect_language(case["text"])
            
            assert detected is not None
            if case["expected_language"] != "mixed":
                assert detected["primary_language"] == case["expected_language"]
            else:
                assert len(detected["languages"]) > 1
    
    @pytest.mark.asyncio
    async def test_cross_lingual_voice_processing(self, multilingual_handler):
        """Test voice processing across different languages."""
        # English to Hindi translation scenario
        english_query = "What is my duty in life?"
        
        with patch.object(multilingual_handler, '_process_cross_lingual') as mock_process:
            mock_process.return_value = {
                "original_text": english_query,
                "target_language": "hi",
                "translated_text": "जीवन में मेरा कर्तव्य क्या है?",
                "audio_data": b"hindi_audio"
            }
            
            result = await multilingual_handler.process_cross_lingual(
                english_query, 
                source_lang="en", 
                target_lang="hi"
            )
            
            assert result["target_language"] == "hi"
            assert result["translated_text"] is not None
            assert result["audio_data"] is not None
    
    def test_voice_parameter_adaptation(self, multilingual_handler):
        """Test adaptation of voice parameters for different languages."""
        languages = ["en", "hi"]
        
        for lang in languages:
            params = multilingual_handler.get_voice_parameters(lang)
            
            assert params is not None
            assert "voice_name" in params
            assert "speech_rate" in params
            assert "pitch" in params
            
            # Hindi should have different parameters than English
            if lang == "hi":
                assert "hi-IN" in params["voice_name"] or "hindi" in params["voice_name"].lower()
    
    @pytest.mark.asyncio
    async def test_code_switching_handling(self, multilingual_handler):
        """Test handling of code-switching (mixed language) content."""
        mixed_content = "Krishna teaches about dharma और कर्म in the Bhagavad Gita।"
        
        with patch.object(multilingual_handler, '_handle_code_switching') as mock_handle:
            mock_handle.return_value = {
                "segments": [
                    {"text": "Krishna teaches about dharma", "language": "en"},
                    {"text": "और कर्म", "language": "hi"},
                    {"text": "in the Bhagavad Gita", "language": "en"}
                ],
                "audio_data": b"mixed_audio"
            }
            
            result = await multilingual_handler.handle_mixed_language(mixed_content)
            
            assert result is not None
            assert "segments" in result
            assert len(result["segments"]) > 1
            assert result["audio_data"] is not None


class TestVoiceErrorRecovery:
    """Test suite for VoiceErrorRecovery class."""
    
    @pytest.fixture
    def voice_recovery(self):
        """Create VoiceErrorRecovery instance for testing."""
        return SpiritualVoiceRecovery()
    
    def test_voice_recovery_initialization(self, voice_recovery):
        """Test voice recovery system initialization."""
        assert voice_recovery is not None
        assert hasattr(voice_recovery, 'recovery_strategies')
        assert hasattr(voice_recovery, 'fallback_options')
    
    @pytest.mark.asyncio
    async def test_audio_quality_recovery(self, voice_recovery):
        """Test recovery from poor audio quality."""
        poor_audio_data = b"noisy_unclear_audio"
        
        with patch.object(voice_recovery, '_assess_audio_quality') as mock_assess:
            mock_assess.return_value = {"quality_score": 0.3, "issues": ["noise", "low_volume"]}
            
            with patch.object(voice_recovery, '_enhance_audio') as mock_enhance:
                mock_enhance.return_value = {
                    "enhanced_audio": b"enhanced_audio",
                    "improvement_score": 0.4
                }
                
                result = await voice_recovery.recover_from_poor_audio(poor_audio_data)
                
                assert result is not None
                assert "enhanced_audio" in result
                assert result["improvement_score"] > 0
    
    @pytest.mark.asyncio
    async def test_speech_recognition_failure_recovery(self, voice_recovery):
        """Test recovery from speech recognition failures."""
        # Simulate recognition failure
        failed_audio = b"unclear_audio"
        
        recovery_options = await voice_recovery.handle_recognition_failure(
            failed_audio,
            confidence_threshold=0.8
        )
        
        assert recovery_options is not None
        assert "fallback_options" in recovery_options
        assert len(recovery_options["fallback_options"]) > 0
        
        # Should suggest alternatives like text input
        fallback_types = [opt["type"] for opt in recovery_options["fallback_options"]]
        assert "text_input" in fallback_types or "retry_audio" in fallback_types
    
    @pytest.mark.asyncio
    async def test_tts_failure_recovery(self, voice_recovery):
        """Test recovery from TTS generation failures."""
        spiritual_text = "Divine guidance about dharma and karma."
        
        with patch.object(voice_recovery, '_attempt_alternative_tts') as mock_alt_tts:
            mock_alt_tts.return_value = {
                "audio_data": b"fallback_audio",
                "provider": "fallback_tts",
                "quality": "basic"
            }
            
            result = await voice_recovery.recover_from_tts_failure(spiritual_text)
            
            assert result is not None
            assert "audio_data" in result
            assert result["provider"] == "fallback_tts"
    
    @pytest.mark.asyncio
    async def test_network_failure_recovery(self, voice_recovery):
        """Test recovery from network connectivity issues."""
        text_for_tts = "Spiritual wisdom about finding peace."
        
        # Simulate network failure
        with patch.object(voice_recovery, '_check_network_connectivity') as mock_network:
            mock_network.return_value = False
            
            result = await voice_recovery.handle_network_failure(text_for_tts)
            
            assert result is not None
            assert "offline_mode" in result or "cached_response" in result
            # Should provide text-only fallback when no network
            assert "text_fallback" in result
    
    def test_error_classification(self, voice_recovery):
        """Test classification of different error types."""
        error_scenarios = [
            {
                "error": "Network timeout during TTS",
                "expected_type": "network_error"
            },
            {
                "error": "Audio quality too poor for recognition",
                "expected_type": "audio_quality_error"
            },
            {
                "error": "Unsupported language detected",
                "expected_type": "language_error"
            }
        ]
        
        for scenario in error_scenarios:
            error_type = voice_recovery.classify_error(scenario["error"])
            
            assert error_type is not None
            assert scenario["expected_type"] in error_type.lower()


class TestVoiceQualityMonitor:
    """Test suite for VoiceQualityMonitor class."""
    
    @pytest.fixture
    def quality_monitor(self):
        """Create VoiceQualityMonitor instance for testing."""
        return VoiceQualityMonitor()
    
    def test_quality_monitor_initialization(self, quality_monitor):
        """Test quality monitor initialization."""
        assert quality_monitor is not None
        assert hasattr(quality_monitor, 'quality_metrics')
        assert hasattr(quality_monitor, 'thresholds')
    
    def test_audio_quality_assessment(self, quality_monitor):
        """Test assessment of audio quality."""
        # Mock different quality audio samples
        quality_samples = [
            {"data": b"high_quality_audio", "expected_score": 0.9},
            {"data": b"medium_quality_audio", "expected_score": 0.6},
            {"data": b"poor_quality_audio", "expected_score": 0.3}
        ]
        
        for sample in quality_samples:
            with patch.object(quality_monitor, '_analyze_audio_features') as mock_analyze:
                mock_analyze.return_value = {
                    "clarity": sample["expected_score"],
                    "noise_level": 1.0 - sample["expected_score"],
                    "volume_consistency": sample["expected_score"]
                }
                
                quality_score = quality_monitor.assess_audio_quality(sample["data"])
                
                assert quality_score is not None
                assert 0.0 <= quality_score <= 1.0
                # Score should roughly match expected quality
                assert abs(quality_score - sample["expected_score"]) < 0.2
    
    def test_speech_clarity_measurement(self, quality_monitor):
        """Test measurement of speech clarity."""
        test_audio = b"test_speech_audio"
        
        with patch.object(quality_monitor, '_measure_speech_clarity') as mock_clarity:
            mock_clarity.return_value = {
                "articulation_score": 0.85,
                "pronunciation_clarity": 0.90,
                "speech_rate_appropriateness": 0.80
            }
            
            clarity_metrics = quality_monitor.measure_speech_clarity(test_audio)
            
            assert clarity_metrics is not None
            assert "articulation_score" in clarity_metrics
            assert all(0.0 <= score <= 1.0 for score in clarity_metrics.values())
    
    def test_sanskrit_pronunciation_accuracy(self, quality_monitor):
        """Test accuracy assessment of Sanskrit pronunciation."""
        sanskrit_audio_cases = [
            {
                "audio": b"dharma_pronunciation",
                "expected_text": "dharma",
                "expected_accuracy": 0.85
            },
            {
                "audio": b"karma_pronunciation", 
                "expected_text": "karma",
                "expected_accuracy": 0.90
            }
        ]
        
        for case in sanskrit_audio_cases:
            with patch.object(quality_monitor, '_assess_sanskrit_pronunciation') as mock_assess:
                mock_assess.return_value = {
                    "pronunciation_accuracy": case["expected_accuracy"],
                    "phoneme_correctness": case["expected_accuracy"],
                    "stress_pattern_accuracy": case["expected_accuracy"] - 0.05
                }
                
                accuracy = quality_monitor.assess_sanskrit_pronunciation(
                    case["audio"], 
                    expected_text=case["expected_text"]
                )
                
                assert accuracy is not None
                assert accuracy["pronunciation_accuracy"] >= 0.8  # High standard for Sanskrit
    
    def test_real_time_quality_monitoring(self, quality_monitor):
        """Test real-time quality monitoring capabilities."""
        # Simulate real-time audio stream
        audio_chunks = [b"chunk1", b"chunk2", b"chunk3", b"chunk4"]
        
        quality_scores = []
        for chunk in audio_chunks:
            with patch.object(quality_monitor, '_analyze_chunk_quality') as mock_chunk:
                mock_chunk.return_value = {"quality": 0.8, "issues": []}
                
                score = quality_monitor.monitor_real_time_quality(chunk)
                quality_scores.append(score)
        
        # Should maintain consistent monitoring
        assert len(quality_scores) == len(audio_chunks)
        assert all(score is not None for score in quality_scores)
    
    def test_quality_improvement_suggestions(self, quality_monitor):
        """Test generation of quality improvement suggestions."""
        poor_quality_metrics = {
            "clarity": 0.4,
            "noise_level": 0.7,
            "volume_consistency": 0.3,
            "pronunciation_accuracy": 0.5
        }
        
        suggestions = quality_monitor.generate_improvement_suggestions(poor_quality_metrics)
        
        assert suggestions is not None
        assert len(suggestions) > 0
        
        # Should include specific suggestions for identified issues
        suggestion_text = " ".join(suggestions).lower()
        assert "noise" in suggestion_text or "volume" in suggestion_text or "pronunciation" in suggestion_text


class TestVoiceIntegrationFlow:
    """Integration tests for complete voice processing workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_voice_workflow(self):
        """Test complete voice processing workflow integration."""
        # Create component instances
        speech_processor = SpeechProcessor()
        sanskrit_optimizer = SanskritOptimizer()
        tts_optimizer = TTSOptimizer()
        quality_monitor = VoiceQualityMonitor()
        
        # Mock the complete workflow
        input_audio = b"mock_spiritual_question_audio"
        
        with patch.multiple(
            speech_processor,
            _recognize_speech=Mock(return_value={
                "text": "What is dharma according to Krishna?",
                "confidence": 0.92,
                "language": "en-US"
            })
        ):
            # Step 1: Speech recognition
            recognition_result = await speech_processor.process_audio(input_audio)
            assert recognition_result["text"] is not None
            
            # Step 2: Sanskrit optimization
            spiritual_response = "O beloved soul, dharma is the eternal law that sustains all creation."
            optimized_text = sanskrit_optimizer.optimize_for_tts(spiritual_response)
            assert optimized_text is not None
            
            # Step 3: TTS generation
            with patch.object(tts_optimizer, '_call_tts_api') as mock_tts:
                mock_tts.return_value = {
                    "audio_data": b"spiritual_response_audio",
                    "duration": 4.5,
                    "quality": "high"
                }
                
                tts_result = await tts_optimizer.generate_audio(
                    optimized_text,
                    voice_profile="divine_male"
                )
                assert tts_result["audio_data"] is not None
            
            # Step 4: Quality monitoring
            with patch.object(quality_monitor, '_analyze_audio_features') as mock_analyze:
                mock_analyze.return_value = {
                    "clarity": 0.9,
                    "spiritual_appropriateness": 0.95
                }
                
                quality_score = quality_monitor.assess_audio_quality(tts_result["audio_data"])
                assert quality_score > 0.8  # High quality threshold
    
    @pytest.mark.asyncio
    async def test_voice_error_recovery_integration(self):
        """Test integrated error recovery across voice components."""
        speech_processor = SpeechProcessor()
        voice_recovery = SpiritualVoiceRecovery()
        
        # Simulate cascading errors and recovery
        poor_audio = b"very_poor_quality_audio"
        
        # First attempt fails
        with patch.object(speech_processor, '_recognize_speech') as mock_recognize:
            mock_recognize.side_effect = Exception("Recognition failed")
            
            # Should trigger recovery mechanisms
            recovery_result = await voice_recovery.handle_recognition_failure(poor_audio)
            
            assert recovery_result is not None
            assert "fallback_options" in recovery_result
            
            # Should offer alternative interaction methods
            fallback_options = recovery_result["fallback_options"]
            assert any(opt["type"] == "text_input" for opt in fallback_options)
    
    @pytest.mark.asyncio
    async def test_performance_requirements_integration(self):
        """Test that integrated voice workflow meets performance requirements."""
        # Test complete voice round-trip performance
        components = {
            "speech_processor": SpeechProcessor(),
            "tts_optimizer": TTSOptimizer(),
            "quality_monitor": VoiceQualityMonitor()
        }
        
        input_audio = b"test_question_audio"
        response_text = "Divine guidance response"
        
        # Mock all components for performance testing
        with patch.multiple(
            components["speech_processor"],
            process_audio=AsyncMock(return_value={
                "text": "What is my purpose?",
                "confidence": 0.9
            })
        ):
            with patch.object(components["tts_optimizer"], 'generate_audio') as mock_tts:
                mock_tts.return_value = {"audio_data": b"response_audio"}
                
                start_time = time.time()
                
                # Complete voice processing cycle
                recognition_result = await components["speech_processor"].process_audio(input_audio)
                tts_result = await components["tts_optimizer"].generate_audio(response_text)
                
                elapsed_time = time.time() - start_time
                
                # Should meet voice response time target
                target_time = PERFORMANCE_BENCHMARKS["response_time_targets"]["voice_query"]
                assert elapsed_time < target_time
                
                assert recognition_result is not None
                assert tts_result is not None
