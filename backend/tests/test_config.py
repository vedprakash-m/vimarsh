"""
Test configuration and utilities for Vimarsh backend testing.

Provides common test utilities, configuration settings, and helper functions
for comprehensive testing of all backend components.
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock, patch
import logging

# Test configuration
TEST_CONFIG = {
    "log_level": "INFO",
    "test_timeout": 30,  # seconds
    "performance_test_iterations": 3,
    "mock_api_responses": True,
    "enable_integration_tests": False,  # Set to True for integration testing
    "test_data_cleanup": True
}

# Configure logging for tests
logging.basicConfig(
    level=getattr(logging, TEST_CONFIG["log_level"]),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test directories
TEST_ROOT = Path(__file__).parent
BACKEND_ROOT = TEST_ROOT.parent
PROJECT_ROOT = BACKEND_ROOT.parent

# Test data paths
TEST_DATA_DIR = TEST_ROOT / "fixtures"
TEMP_TEST_DIR = Path(tempfile.gettempdir()) / "vimarsh_tests"

# Ensure test directories exist
TEST_DATA_DIR.mkdir(exist_ok=True)
TEMP_TEST_DIR.mkdir(exist_ok=True)


class TestHelper:
    """Helper class for common test operations."""
    
    @staticmethod
    def create_temp_spiritual_text(content: str, filename: str = "test_text.txt") -> Path:
        """Create temporary spiritual text file for testing."""
        temp_file = TEMP_TEST_DIR / filename
        temp_file.write_text(content, encoding='utf-8')
        return temp_file
    
    @staticmethod
    def cleanup_temp_files():
        """Clean up temporary test files."""
        if TEST_CONFIG["test_data_cleanup"] and TEMP_TEST_DIR.exists():
            shutil.rmtree(TEMP_TEST_DIR)
            TEMP_TEST_DIR.mkdir(exist_ok=True)
    
    @staticmethod
    def mock_spiritual_response(query: str, language: str = "English") -> dict:
        """Generate mock spiritual response for testing."""
        responses = {
            "dharma": "O beloved soul, dharma is the eternal law that sustains all creation.",
            "karma": "Your actions create your destiny. Act with pure intention.",
            "duty": "Perform your prescribed duty without attachment to results.",
            "peace": "Inner peace comes from surrendering the fruits of action to the Divine."
        }
        
        # Find relevant response based on query keywords
        response_text = "Divine guidance for your spiritual journey."
        for keyword, text in responses.items():
            if keyword in query.lower():
                response_text = text
                break
        
        return {
            "response": response_text,
            "citations": ["Bhagavad Gita 2.47"],
            "language": language,
            "confidence": 0.95,
            "authenticity_score": 0.92
        }
    
    @staticmethod
    def mock_vector_search_results(query: str, top_k: int = 5) -> list:
        """Generate mock vector search results."""
        base_results = [
            {
                "text": "You have a right to perform your prescribed duty, but not to the fruits of action.",
                "source": "Bhagavad Gita 2.47",
                "score": 0.95
            },
            {
                "text": "Be steadfast in yoga, O Arjuna. Perform your duty and abandon all attachment.",
                "source": "Bhagavad Gita 2.48", 
                "score": 0.89
            },
            {
                "text": "The ultimate dharma is ahimsa, truth, and compassion towards all living beings.",
                "source": "Mahabharata, Vana Parva 313",
                "score": 0.85
            },
            {
                "text": "Work done as sacrifice for Vishnu has to be performed.",
                "source": "Bhagavad Gita 3.9",
                "score": 0.82
            },
            {
                "text": "The wise see with equal vision a learned brahmana, a cow, an elephant, a dog and a dog-eater.",
                "source": "Bhagavad Gita 5.18",
                "score": 0.78
            }
        ]
        
        # Filter and rank based on query relevance
        query_lower = query.lower()
        relevant_results = []
        
        for result in base_results:
            relevance_bonus = 0
            if "duty" in query_lower and "duty" in result["text"].lower():
                relevance_bonus = 0.1
            elif "dharma" in query_lower and "dharma" in result["text"].lower():
                relevance_bonus = 0.1
            elif "karma" in query_lower and ("karma" in result["text"].lower() or "action" in result["text"].lower()):
                relevance_bonus = 0.1
            
            result["score"] = min(result["score"] + relevance_bonus, 1.0)
            relevant_results.append(result)
        
        # Sort by score and return top_k
        relevant_results.sort(key=lambda x: x["score"], reverse=True)
        return relevant_results[:top_k]
    
    @staticmethod
    def assert_spiritual_authenticity(response: dict):
        """Assert that response maintains spiritual authenticity."""
        assert "response" in response
        response_text = response["response"].lower()
        
        # Check for appropriate spiritual tone
        appropriate_words = ["divine", "soul", "dharma", "karma", "peace", "wisdom", "sacred", "beloved"]
        has_appropriate_tone = any(word in response_text for word in appropriate_words)
        
        # Check against inappropriate language
        inappropriate_words = ["dude", "whatever", "hey", "cool", "awesome", "sucks"]
        has_inappropriate_tone = any(word in response_text for word in inappropriate_words)
        
        assert has_appropriate_tone, f"Response lacks spiritual tone: {response['response']}"
        assert not has_inappropriate_tone, f"Response contains inappropriate language: {response['response']}"
        
        # Check for citations
        assert "citations" in response
        assert isinstance(response["citations"], list)
    
    @staticmethod
    def assert_performance_requirements(elapsed_time: float, operation_type: str):
        """Assert that operation meets performance requirements."""
        from tests.fixtures import PERFORMANCE_BENCHMARKS
        
        targets = PERFORMANCE_BENCHMARKS["response_time_targets"]
        
        if operation_type in targets:
            target_time = targets[operation_type]
            assert elapsed_time < target_time, f"{operation_type} took {elapsed_time:.2f}s, target: {target_time}s"
        else:
            # Default performance assertion
            assert elapsed_time < 5.0, f"Operation took too long: {elapsed_time:.2f}s"


class AsyncTestMixin:
    """Mixin for async test utilities."""
    
    @staticmethod
    def run_async_test(coro):
        """Helper to run async tests in sync test environment."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    @staticmethod
    async def with_timeout(coro, timeout_seconds: int = TEST_CONFIG["test_timeout"]):
        """Run coroutine with timeout."""
        return await asyncio.wait_for(coro, timeout=timeout_seconds)


class MockAPIManager:
    """Manager for API mocking during tests."""
    
    def __init__(self):
        self.active_patches = []
    
    def mock_gemini_api(self, responses: dict = None):
        """Mock Gemini API responses."""
        if responses is None:
            responses = {
                "default": "Divine guidance from Lord Krishna about your spiritual journey."
            }
        
        def mock_generate_content(*args, **kwargs):
            mock_response = Mock()
            # Determine response based on prompt content
            prompt = str(args[0]) if args else str(kwargs.get('prompt', ''))
            
            for keyword, response in responses.items():
                if keyword in prompt.lower() or keyword == "default":
                    mock_response.text = response
                    break
            
            return mock_response
        
        patch_target = 'llm.gemini_client.genai.GenerativeModel'
        mock_patch = patch(patch_target)
        mock_obj = mock_patch.start()
        mock_obj.return_value.generate_content_async = AsyncMock(side_effect=mock_generate_content)
        
        self.active_patches.append(mock_patch)
        return mock_obj
    
    def mock_vector_database(self, search_results: list = None):
        """Mock vector database operations."""
        if search_results is None:
            search_results = TestHelper.mock_vector_search_results("default query")
        
        mock_search = AsyncMock(return_value=search_results)
        mock_add = AsyncMock(return_value=True)
        mock_count = AsyncMock(return_value=len(search_results))
        
        vector_db_patch = patch('rag_pipeline.vector_storage.VectorStorage')
        mock_db = vector_db_patch.start()
        mock_db.return_value.similarity_search = mock_search
        mock_db.return_value.add_documents = mock_add
        mock_db.return_value.get_document_count = mock_count
        
        self.active_patches.append(vector_db_patch)
        return mock_db
    
    def mock_voice_apis(self):
        """Mock voice-related API calls."""
        # Mock speech recognition
        speech_patch = patch('voice.speech_processor.speech_recognition')
        mock_speech = speech_patch.start()
        mock_speech.recognize_google_cloud.return_value = "What is dharma?"
        
        # Mock TTS
        tts_patch = patch('voice.tts_optimizer.texttospeech')
        mock_tts = tts_patch.start()
        mock_tts.SynthesizeSpeechResponse.return_value.audio_content = b"mock_audio"
        
        self.active_patches.extend([speech_patch, tts_patch])
        return {"speech": mock_speech, "tts": mock_tts}
    
    def cleanup(self):
        """Clean up all active patches."""
        for patch_obj in self.active_patches:
            patch_obj.stop()
        self.active_patches.clear()


# Pytest fixtures for common test needs
@pytest.fixture
def test_helper():
    """Provide TestHelper instance."""
    return TestHelper()

@pytest.fixture
def mock_api_manager():
    """Provide MockAPIManager instance."""
    manager = MockAPIManager()
    yield manager
    manager.cleanup()

@pytest.fixture
def temp_spiritual_texts():
    """Create temporary spiritual text files."""
    texts = {}
    
    # Bhagavad Gita sample
    gita_content = """
    Chapter 2: The Yoga of Knowledge
    
    Verse 47: कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
    You have a right to perform your prescribed duty, but not to the fruits of action.
    
    Verse 48: योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।
    Be steadfast in yoga, O Arjuna. Perform your duty and abandon all attachment.
    """
    texts["gita"] = TestHelper.create_temp_spiritual_text(gita_content, "bhagavad_gita.txt")
    
    # Mahabharata sample
    mb_content = """
    Udyoga Parva, Section 29:
    Dharma exists for the welfare of all beings. Hence, that by which the welfare 
    of all living beings is sustained, that is dharma.
    
    Vana Parva, Section 313:
    The ultimate dharma is ahimsa (non-violence), truth, and compassion towards all living beings.
    """
    texts["mahabharata"] = TestHelper.create_temp_spiritual_text(mb_content, "mahabharata.txt")
    
    yield texts
    
    # Cleanup
    TestHelper.cleanup_temp_files()

@pytest.fixture(scope="session", autouse=True)
def test_session_setup():
    """Setup and teardown for test session."""
    # Setup
    print("\n🕉️  Starting Vimarsh Backend Test Suite")
    print(f"Test configuration: {TEST_CONFIG}")
    
    yield
    
    # Teardown
    TestHelper.cleanup_temp_files()
    print("✨ Test suite completed. May divine wisdom guide your path.")


# Performance testing decorator
def performance_test(operation_type: str):
    """Decorator for performance testing."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            result = await func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            TestHelper.assert_performance_requirements(elapsed_time, operation_type)
            return result
        
        def sync_wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            TestHelper.assert_performance_requirements(elapsed_time, operation_type)
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Custom assertions for spiritual content
def assert_divine_persona_consistency(response: str):
    """Assert that response maintains Lord Krishna's divine persona."""
    response_lower = response.lower()
    
    # Should address user appropriately
    appropriate_addresses = ["beloved", "dear", "child", "soul", "o "]
    has_appropriate_address = any(addr in response_lower for addr in appropriate_addresses)
    
    # Should maintain authority and wisdom
    wisdom_indicators = ["teach", "guide", "show", "reveal", "wisdom", "truth"]
    has_wisdom_tone = any(indicator in response_lower for indicator in wisdom_indicators)
    
    # Should reference teachings or scriptures
    scriptural_references = ["gita", "taught", "teachings", "scripture", "verse"]
    has_scriptural_grounding = any(ref in response_lower for ref in scriptural_references)
    
    assert has_appropriate_address or has_wisdom_tone, "Response lacks divine persona characteristics"
    assert has_scriptural_grounding, "Response lacks scriptural grounding"

def assert_cultural_sensitivity(text: str):
    """Assert that text maintains cultural sensitivity."""
    text_lower = text.lower()
    
    # Check for respectful language about spiritual concepts
    spiritual_terms = ["dharma", "karma", "moksha", "bhakti", "yoga"]
    disrespectful_modifiers = ["weird", "strange", "old", "ancient nonsense", "mythology"]
    
    for term in spiritual_terms:
        if term in text_lower:
            for modifier in disrespectful_modifiers:
                assert f"{modifier} {term}" not in text_lower, f"Disrespectful reference to {term}"
                assert f"{term} {modifier}" not in text_lower, f"Disrespectful reference to {term}"
