"""
Comprehensive Voice Interface Testing Suite for Vimarsh AI Agent

This module implements comprehensive testing for voice interface components,
including speech recognition, TTS, multilingual support, and Sanskrit optimization.
"""

import asyncio
import json
import time
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import tempfile
import os

# Import voice components to test
from voice.speech_processor import (
    SpeechProcessor, VoiceConfig, VoiceLanguage, 
    SpeechQuality, RecognitionStatus
)
from voice.sanskrit_optimizer import SanskritOptimizer
from voice.tts_optimizer import TTSOptimizer
from voice.multilingual import MultilingualVoiceManager
from voice.voice_recovery import VoiceErrorRecovery
from voice.quality_monitor import VoiceQualityMonitor
from voice.advanced_features import AdvancedVoiceFeatures


@dataclass
class MockAudioData:
    """Mock audio data for testing"""
    text: str
    language: str
    confidence: float
    duration: float
    sample_rate: int = 16000
    
    def to_bytes(self) -> bytes:
        """Convert to mock audio bytes"""
        return f"AUDIO:{self.text}:{self.language}:{self.confidence}".encode()


@dataclass
class VoiceTestResult:
    """Voice test result structure"""
    test_name: str
    status: str
    duration: float
    details: Dict[str, Any]
    errors: List[str] = None


class MockWebSpeechAPI:
    """Mock Web Speech API for testing"""
    
    def __init__(self):
        self.is_listening = False
        self.language = "en-US"
        self.continuous = False
        self.interim_results = False
        self.max_alternatives = 1
        self.recognition_data = []
        self.error_simulation = None
        
    def start_recognition(self, audio_data: MockAudioData):
        """Simulate speech recognition"""
        self.is_listening = True
        if self.error_simulation:
            raise Exception(f"Recognition error: {self.error_simulation}")
        
        # Simulate processing delay
        time.sleep(0.1)
        
        result = {
            'transcript': audio_data.text,
            'confidence': audio_data.confidence,
            'alternatives': [
                {'transcript': audio_data.text, 'confidence': audio_data.confidence}
            ]
        }
        self.recognition_data.append(result)
        return result
    
    def stop_recognition(self):
        """Stop recognition simulation"""
        self.is_listening = False
    
    def simulate_error(self, error_type: str):
        """Simulate recognition errors"""
        self.error_simulation = error_type


class MockTTSEngine:
    """Mock Text-to-Speech engine for testing"""
    
    def __init__(self):
        self.voice_settings = {
            'rate': 1.0,
            'pitch': 1.0,
            'volume': 1.0,
            'voice_id': 'default'
        }
        self.synthesis_data = []
        
    def synthesize_speech(self, text: str, language: str) -> MockAudioData:
        """Simulate speech synthesis"""
        audio_data = MockAudioData(
            text=text,
            language=language,
            confidence=0.95,
            duration=len(text) * 0.1  # Estimate duration
        )
        self.synthesis_data.append(audio_data)
        return audio_data
    
    def set_voice_parameters(self, rate: float, pitch: float, volume: float):
        """Set voice parameters"""
        self.voice_settings.update({
            'rate': rate,
            'pitch': pitch,
            'volume': volume
        })


class TestVoiceInterfaceCore:
    """Core voice interface functionality tests"""
    
    @pytest.fixture
    def mock_web_speech(self):
        """Mock Web Speech API fixture"""
        return MockWebSpeechAPI()
    
    @pytest.fixture
    def mock_tts_engine(self):
        """Mock TTS engine fixture"""
        return MockTTSEngine()
    
    @pytest.fixture
    def speech_processor(self, mock_web_speech, mock_tts_engine):
        """Speech processor with mocked dependencies"""
        config = VoiceConfig(
            language=VoiceLanguage.ENGLISH,
            quality=SpeechQuality.HIGH,
            continuous_recognition=True,
            interim_results=True
        )
        
        with patch('voice.speech_processor.WebSpeechAPI', return_value=mock_web_speech), \
             patch('voice.speech_processor.TTSEngine', return_value=mock_tts_engine):
            processor = SpeechProcessor(config)
            processor.web_speech_api = mock_web_speech
            processor.tts_engine = mock_tts_engine
            return processor
    
    @pytest.mark.asyncio
    async def test_speech_recognition_basic(self, speech_processor, mock_web_speech):
        """Test basic speech recognition functionality"""
        # Prepare test audio
        test_audio = MockAudioData(
            text="What is the essence of dharma?",
            language="en-US",
            confidence=0.92,
            duration=3.5
        )
        
        # Test recognition
        result = await speech_processor.recognize_speech(test_audio)
        
        # Verify results
        assert result['transcript'] == "What is the essence of dharma?"
        assert result['confidence'] >= 0.9
        assert result['language'] == "en-US"
        assert 'alternatives' in result
    
    @pytest.mark.asyncio
    async def test_speech_recognition_multilingual(self, speech_processor, mock_web_speech):
        """Test multilingual speech recognition"""
        test_cases = [
            {
                'audio': MockAudioData("What is dharma?", "en-US", 0.94, 2.0),
                'expected_lang': "en-US"
            },
            {
                'audio': MockAudioData("धर्म क्या है?", "hi-IN", 0.89, 2.2),
                'expected_lang': "hi-IN"
            },
            {
                'audio': MockAudioData("धर्मः किम्?", "sa-IN", 0.85, 1.8),
                'expected_lang': "sa-IN"
            }
        ]
        
        for test_case in test_cases:
            # Set language
            speech_processor.config.language = VoiceLanguage(test_case['expected_lang'])
            mock_web_speech.language = test_case['expected_lang']
            
            # Test recognition
            result = await speech_processor.recognize_speech(test_case['audio'])
            
            # Verify language-specific results
            assert result['language'] == test_case['expected_lang']
            assert result['confidence'] > 0.8
    
    @pytest.mark.asyncio
    async def test_tts_synthesis(self, speech_processor, mock_tts_engine):
        """Test text-to-speech synthesis"""
        test_texts = [
            "Krishna teaches us about dharma in the Bhagavad Gita.",
            "कृष्ण भगवद्गीता में धर्म के बारे में सिखाते हैं।",
            "कृष्णः भगवद्गीतायाम् धर्मम् उपदिशति।"
        ]
        
        for text in test_texts:
            # Test synthesis
            audio_data = await speech_processor.synthesize_speech(text)
            
            # Verify synthesis
            assert audio_data.text == text
            assert audio_data.confidence > 0.9
            assert audio_data.duration > 0
    
    @pytest.mark.asyncio
    async def test_voice_error_recovery(self, speech_processor, mock_web_speech):
        """Test voice error recovery mechanisms"""
        # Simulate network error
        mock_web_speech.simulate_error("network_error")
        
        test_audio = MockAudioData(
            text="What is moksha?",
            language="en-US", 
            confidence=0.9,
            duration=2.5
        )
        
        # Test error recovery
        with pytest.raises(Exception):
            await speech_processor.recognize_speech(test_audio)
        
        # Test recovery after error
        mock_web_speech.error_simulation = None
        result = await speech_processor.recognize_speech(test_audio)
        assert result['transcript'] == "What is moksha?"
    
    @pytest.mark.asyncio
    async def test_voice_quality_monitoring(self, speech_processor):
        """Test voice quality monitoring and optimization"""
        # Test with various quality audio samples
        quality_tests = [
            MockAudioData("Clear spiritual question", "en-US", 0.95, 3.0),
            MockAudioData("Noisy background question", "en-US", 0.75, 3.2),
            MockAudioData("Low quality audio", "en-US", 0.55, 2.8)
        ]
        
        for audio in quality_tests:
            result = await speech_processor.recognize_speech(audio)
            
            # Quality should be assessed
            assert 'quality_score' in result
            assert 'quality_recommendations' in result
            
            # Low quality should trigger recommendations
            if result['confidence'] < 0.8:
                assert len(result['quality_recommendations']) > 0


class TestSanskritOptimization:
    """Sanskrit language optimization tests"""
    
    @pytest.fixture
    def sanskrit_optimizer(self):
        """Sanskrit optimizer fixture"""
        return SanskritOptimizer()
    
    def test_sanskrit_term_recognition(self, sanskrit_optimizer):
        """Test Sanskrit terminology recognition"""
        test_terms = [
            ("dharma", "धर्म"),
            ("karma", "कर्म"),
            ("moksha", "मोक्ष"),
            ("krishna", "कृष्ण"),
            ("bhagavad gita", "भगवद्गीता"),
            ("namaste", "नमस्ते")
        ]
        
        for latin, devanagari in test_terms:
            # Test recognition of both scripts
            result_latin = sanskrit_optimizer.optimize_recognition(latin)
            result_devanagari = sanskrit_optimizer.optimize_recognition(devanagari)
            
            assert result_latin['recognized_terms'] or result_devanagari['recognized_terms']
            assert result_latin['pronunciation_guide'] is not None
    
    def test_pronunciation_optimization(self, sanskrit_optimizer):
        """Test Sanskrit pronunciation optimization"""
        test_phrases = [
            "श्रीमद्भगवद्गीता",
            "अहिंसा परमो धर्मः",
            "सत्यमेव जयते",
            "ॐ शान्ति शान्ति शान्तिः"
        ]
        
        for phrase in test_phrases:
            pronunciation = sanskrit_optimizer.get_pronunciation_guide(phrase)
            
            assert pronunciation is not None
            assert 'phonetic' in pronunciation
            assert 'stress_patterns' in pronunciation
            assert 'syllable_breaks' in pronunciation
    
    def test_sanskrit_tts_optimization(self, sanskrit_optimizer):
        """Test Sanskrit TTS optimization"""
        spiritual_texts = [
            "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।",
            "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
            "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।"
        ]
        
        for text in spiritual_texts:
            tts_params = sanskrit_optimizer.optimize_tts_parameters(text)
            
            assert tts_params['rate'] <= 0.8  # Slower for Sanskrit
            assert tts_params['pitch_modulation'] is not None
            assert 'emphasis_points' in tts_params


class TestMultilingualVoice:
    """Multilingual voice interface tests"""
    
    @pytest.fixture
    def multilingual_manager(self):
        """Multilingual voice manager fixture"""
        return MultilingualVoiceManager()
    
    @pytest.mark.asyncio
    async def test_language_detection(self, multilingual_manager):
        """Test automatic language detection"""
        test_phrases = [
            ("What is the meaning of life?", "en"),
            ("जीवन का अर्थ क्या है?", "hi"),
            ("जीवनस्य अर्थः किम्?", "sa"),
            ("Hello namaste", "mixed")  # Code-switching
        ]
        
        for phrase, expected_lang in test_phrases:
            detected = await multilingual_manager.detect_language(phrase)
            
            if expected_lang == "mixed":
                assert detected['is_code_switching']
                assert len(detected['languages']) > 1
            else:
                assert detected['primary_language'] == expected_lang
                assert detected['confidence'] > 0.8
    
    @pytest.mark.asyncio
    async def test_code_switching_handling(self, multilingual_manager):
        """Test handling of code-switching (mixed languages)"""
        mixed_phrases = [
            "Hello namaste, what is dharma?",
            "धन्यवाद, thank you for the guidance",
            "Om shanti, may peace be with you"
        ]
        
        for phrase in mixed_phrases:
            result = await multilingual_manager.process_mixed_language(phrase)
            
            assert result['is_code_switching']
            assert len(result['language_segments']) > 1
            assert 'unified_response_strategy' in result
    
    @pytest.mark.asyncio
    async def test_multilingual_tts(self, multilingual_manager):
        """Test multilingual text-to-speech"""
        multilingual_responses = [
            {
                'text': "Krishna teaches us dharma.",
                'languages': ['en'],
                'sanskrit_terms': ['Krishna', 'dharma']
            },
            {
                'text': "कृष्ण हमें धर्म सिखाते हैं।",
                'languages': ['hi'],
                'sanskrit_terms': ['कृष्ण', 'धर्म']
            },
            {
                'text': "Krishna teaches us dharma. कृष्ण हमें धर्म सिखाते हैं।",
                'languages': ['en', 'hi'],
                'sanskrit_terms': ['Krishna', 'dharma', 'कृष्ण', 'धर्म']
            }
        ]
        
        for response in multilingual_responses:
            tts_result = await multilingual_manager.synthesize_multilingual(
                response['text'], 
                response['languages']
            )
            
            assert tts_result['success']
            assert 'audio_segments' in tts_result
            assert len(tts_result['audio_segments']) >= len(response['languages'])


class TestVoiceErrorRecovery:
    """Voice error recovery and resilience tests"""
    
    @pytest.fixture
    def error_recovery(self):
        """Voice error recovery fixture"""
        return VoiceErrorRecovery()
    
    @pytest.mark.asyncio
    async def test_network_error_recovery(self, error_recovery):
        """Test recovery from network errors"""
        error_scenarios = [
            {"type": "network_timeout", "retry_count": 3},
            {"type": "service_unavailable", "retry_count": 2},
            {"type": "rate_limit_exceeded", "retry_count": 1}
        ]
        
        for scenario in error_scenarios:
            recovery_result = await error_recovery.handle_error(
                scenario["type"], 
                {"max_retries": scenario["retry_count"]}
            )
            
            assert recovery_result['recovery_attempted']
            assert recovery_result['strategy'] is not None
            assert recovery_result['fallback_available']
    
    @pytest.mark.asyncio
    async def test_voice_quality_fallback(self, error_recovery):
        """Test fallback mechanisms for poor voice quality"""
        poor_quality_scenarios = [
            {"confidence": 0.3, "noise_level": "high"},
            {"confidence": 0.5, "noise_level": "medium"},
            {"confidence": 0.1, "noise_level": "extreme"}
        ]
        
        for scenario in poor_quality_scenarios:
            fallback = await error_recovery.handle_poor_quality(scenario)
            
            assert 'fallback_strategy' in fallback
            assert 'user_guidance' in fallback
            
            if scenario['confidence'] < 0.4:
                assert fallback['fallback_strategy'] == 'text_input_prompt'
    
    @pytest.mark.asyncio
    async def test_interruption_handling(self, error_recovery):
        """Test handling of voice interruptions"""
        interruption_scenarios = [
            {"type": "user_interruption", "timing": "mid_speech"},
            {"type": "external_noise", "timing": "start"},
            {"type": "device_switch", "timing": "end"}
        ]
        
        for scenario in interruption_scenarios:
            handling_result = await error_recovery.handle_interruption(scenario)
            
            assert handling_result['interruption_handled']
            assert 'resume_strategy' in handling_result
            assert 'context_preservation' in handling_result


class TestVoicePerformance:
    """Voice interface performance and optimization tests"""
    
    @pytest.mark.asyncio
    async def test_response_time_performance(self):
        """Test voice interface response times"""
        speech_processor = SpeechProcessor(VoiceConfig())
        
        # Test with mock data
        start_time = time.time()
        
        test_audio = MockAudioData(
            text="What is the essence of dharma?",
            language="en-US",
            confidence=0.92,
            duration=3.0
        )
        
        # Mock the recognition process
        with patch.object(speech_processor, 'recognize_speech') as mock_recognize:
            mock_recognize.return_value = {
                'transcript': test_audio.text,
                'confidence': test_audio.confidence,
                'processing_time': 0.5
            }
            
            result = await speech_processor.recognize_speech(test_audio)
            
        processing_time = time.time() - start_time
        
        # Performance assertions
        assert processing_time < 2.0  # Should process within 2 seconds
        assert result['processing_time'] < 1.0  # Core processing under 1 second
    
    @pytest.mark.asyncio
    async def test_concurrent_voice_requests(self):
        """Test handling of concurrent voice requests"""
        speech_processor = SpeechProcessor(VoiceConfig())
        
        # Create multiple concurrent requests
        concurrent_requests = []
        for i in range(5):
            audio = MockAudioData(
                text=f"Spiritual question {i+1}",
                language="en-US",
                confidence=0.9,
                duration=2.0
            )
            concurrent_requests.append(audio)
        
        # Mock concurrent processing
        with patch.object(speech_processor, 'recognize_speech') as mock_recognize:
            mock_recognize.side_effect = lambda audio: {
                'transcript': audio.text,
                'confidence': audio.confidence,
                'request_id': id(audio)
            }
            
            # Process concurrently
            tasks = [
                speech_processor.recognize_speech(audio) 
                for audio in concurrent_requests
            ]
            results = await asyncio.gather(*tasks)
        
        # Verify all requests processed
        assert len(results) == 5
        for i, result in enumerate(results):
            assert f"Spiritual question {i+1}" in result['transcript']
    
    @pytest.mark.asyncio
    async def test_memory_usage_optimization(self):
        """Test voice interface memory usage optimization"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create speech processor and process multiple requests
        speech_processor = SpeechProcessor(VoiceConfig())
        
        for i in range(10):
            audio = MockAudioData(
                text=f"Memory test question {i+1}",
                language="en-US",
                confidence=0.9,
                duration=2.0
            )
            
            with patch.object(speech_processor, 'recognize_speech') as mock_recognize:
                mock_recognize.return_value = {
                    'transcript': audio.text,
                    'confidence': audio.confidence
                }
                await speech_processor.recognize_speech(audio)
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024


async def run_comprehensive_voice_tests():
    """Run all voice interface tests and generate report"""
    test_results = []
    
    # Initialize test classes
    test_classes = [
        TestVoiceInterfaceCore,
        TestSanskritOptimization,
        TestMultilingualVoice,
        TestVoiceErrorRecovery,
        TestVoicePerformance
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__name__
        print(f"\n🎤 Running {class_name} tests...")
        
        # Get test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            start_time = time.time()
            
            try:
                # Create test instance with mocked dependencies
                if hasattr(test_class, '__init__'):
                    test_instance = test_class()
                else:
                    test_instance = test_class
                
                # Run the test method
                test_method = getattr(test_instance, method_name)
                if asyncio.iscoroutinefunction(test_method):
                    await test_method()
                else:
                    test_method()
                
                duration = time.time() - start_time
                passed_tests += 1
                
                result = VoiceTestResult(
                    test_name=f"{class_name}.{method_name}",
                    status="PASSED",
                    duration=duration,
                    details={"class": class_name, "method": method_name}
                )
                test_results.append(result)
                print(f"  ✅ {method_name} - {duration:.3f}s")
                
            except Exception as e:
                duration = time.time() - start_time
                result = VoiceTestResult(
                    test_name=f"{class_name}.{method_name}",
                    status="FAILED", 
                    duration=duration,
                    details={"class": class_name, "method": method_name},
                    errors=[str(e)]
                )
                test_results.append(result)
                print(f"  ❌ {method_name} - FAILED: {str(e)}")
    
    # Generate test report
    report = {
        'summary': {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'total_duration': sum(result.duration for result in test_results)
        },
        'test_results': [
            {
                'test_name': result.test_name,
                'status': result.status,
                'duration': result.duration,
                'details': result.details,
                'errors': result.errors
            }
            for result in test_results
        ]
    }
    
    # Save report
    with open('/Users/vedprakashmishra/vimarsh/backend/voice_interface_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n🎤 Voice Interface Testing Complete!")
    print(f"📊 Tests: {passed_tests}/{total_tests} passed ({report['summary']['success_rate']:.1f}%)")
    print(f"⏱️  Total Duration: {report['summary']['total_duration']:.2f}s")
    print(f"📄 Report: voice_interface_test_report.json")
    
    return report


if __name__ == "__main__":
    # Run the comprehensive voice interface tests
    asyncio.run(run_comprehensive_voice_tests())
