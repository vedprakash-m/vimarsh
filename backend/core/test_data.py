"""
Test Data Management for Vimarsh Testing
Provides test data generation, fixtures, and test environment setup
"""

import json
import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pytest


@dataclass
class TestSpiritualText:
    """Test spiritual text for RAG testing"""
    id: str
    source: str
    chapter: Optional[str] = None
    verse: Optional[str] = None
    content: str = ""
    tags: List[str] = field(default_factory=list)
    language: str = "English"


@dataclass
class TestUser:
    """Test user for authentication testing"""
    user_id: str
    email: str
    name: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    session_history: List[Dict] = field(default_factory=list)


@dataclass
class TestQuery:
    """Test query with expected response characteristics"""
    query: str
    context: str
    language: str = "English"
    expected_response_length: tuple = (50, 1000)
    expected_topics: List[str] = field(default_factory=list)
    should_contain: List[str] = field(default_factory=list)
    should_not_contain: List[str] = field(default_factory=list)
    expected_confidence: float = 0.5


class TestDataManager:
    """Manages test data and fixtures"""
    
    def __init__(self):
        """Initialize test data manager"""
        self.temp_dir = None
        self.test_db_path = None
        self.original_env = {}
        
    def setup_test_environment(self):
        """Setup isolated test environment"""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="vimarsh_test_")
        self.test_db_path = os.path.join(self.temp_dir, "test_spiritual_texts.json")
        
        # Backup original environment variables
        test_env_vars = [
            "AZURE_COSMOS_CONNECTION_STRING",
            "GEMINI_API_KEY",
            "ENABLE_AUTH",
            "LOG_LEVEL",
            "DEBUG"
        ]
        
        for var in test_env_vars:
            self.original_env[var] = os.getenv(var)
        
        # Set test environment variables
        os.environ["AZURE_COSMOS_CONNECTION_STRING"] = "test-mode-local-storage"
        os.environ["GEMINI_API_KEY"] = "test-mode-placeholder"
        os.environ["ENABLE_AUTH"] = "false"
        os.environ["LOG_LEVEL"] = "WARNING"  # Reduce log noise in tests
        os.environ["DEBUG"] = "false"
        os.environ["ENVIRONMENT"] = "testing"
        
        # Create test database
        self._create_test_database()
        
        return self.temp_dir
    
    def teardown_test_environment(self):
        """Cleanup test environment"""
        # Restore original environment variables
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
        
        # Remove temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_test_database(self):
        """Create test database with sample spiritual texts"""
        test_texts = [
            TestSpiritualText(
                id="bg_2_47",
                source="Bhagavad Gita",
                chapter="2",
                verse="47",
                content="You have a right to perform your prescribed duty, but not to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.",
                tags=["duty", "action", "detachment", "karma_yoga"],
                language="English"
            ),
            TestSpiritualText(
                id="bg_18_66",
                source="Bhagavad Gita", 
                chapter="18",
                verse="66",
                content="Abandon all varieties of religion and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear.",
                tags=["surrender", "devotion", "bhakti", "liberation"],
                language="English"
            ),
            TestSpiritualText(
                id="bg_6_19",
                source="Bhagavad Gita",
                chapter="6",
                verse="19",
                content="As a lamp in a windless place does not waver, so the transcendentalist, whose mind is controlled, remains always steady in his meditation on the transcendent self.",
                tags=["meditation", "mind_control", "steadiness", "self_realization"],
                language="English"
            ),
            TestSpiritualText(
                id="bg_2_20",
                source="Bhagavad Gita",
                chapter="2",
                verse="20",
                content="For the soul there is neither birth nor death nor any time when it comes into being. It is unborn, eternal, permanent, and primeval.",
                tags=["soul", "eternal", "death", "nature_of_self"],
                language="English"
            ),
            TestSpiritualText(
                id="bg_2_14",
                source="Bhagavad Gita",
                chapter="2", 
                verse="14",
                content="O son of Kunti, the contact between the senses and the sense objects gives rise to happiness and distress. These are temporary and come and go like winter and summer seasons.",
                tags=["temporary", "suffering", "detachment", "equanimity"],
                language="English"
            ),
            TestSpiritualText(
                id="general_dharma",
                source="General Teaching",
                content="Dharma is the righteous path that leads to harmony in life. It involves doing your duty with love and surrender to the Divine.",
                tags=["dharma", "righteousness", "duty", "divine_will"],
                language="English"
            ),
            TestSpiritualText(
                id="general_peace",
                source="General Teaching",
                content="Inner peace comes from understanding your true nature as an eternal soul, beyond the temporary troubles of the body and mind.",
                tags=["peace", "soul", "detachment", "inner_wisdom"],
                language="English"
            ),
            TestSpiritualText(
                id="general_meditation",
                source="General Teaching",
                content="Meditation is the practice of turning the mind inward to discover the divine presence within. Start with simple breath awareness and gradually deepen your practice.",
                tags=["meditation", "breath", "inner_divine", "practice"],
                language="English"
            )
        ]
        
        # Convert to JSON format
        test_data = []
        for text in test_texts:
            test_data.append({
                "id": text.id,
                "source": text.source,
                "chapter": text.chapter,
                "verse": text.verse,
                "content": text.content,
                "tags": text.tags,
                "language": text.language,
                "created_at": datetime.utcnow().isoformat()
            })
        
        # Save to test database file
        with open(self.test_db_path, 'w') as f:
            json.dump(test_data, f, indent=2)
    
    def get_test_queries(self) -> List[TestQuery]:
        """Get comprehensive set of test queries"""
        return [
            # Guidance queries
            TestQuery(
                query="I feel lost and don't know my purpose in life",
                context="guidance",
                expected_topics=["purpose", "dharma", "path", "divine"],
                should_contain=["🙏", "dear soul", "Krishna"],
                should_not_contain=["medical", "legal", "financial"]
            ),
            TestQuery(
                query="How can I find inner peace during difficult times?",
                context="guidance",
                expected_topics=["peace", "difficult", "inner", "calm"],
                should_contain=["🙏", "beloved", "temporary"],
                should_not_contain=["predict", "future", "guarantee"]
            ),
            
            # Teaching queries
            TestQuery(
                query="What is dharma according to Hindu philosophy?",
                context="teaching",
                expected_topics=["dharma", "duty", "righteousness", "philosophy"],
                should_contain=["🙏", "Bhagavad Gita", "duty"],
                should_not_contain=["medical", "investment", "lottery"]
            ),
            TestQuery(
                query="Explain the concept of karma",
                context="teaching",
                expected_topics=["karma", "action", "consequence", "law"],
                should_contain=["🙏", "action", "result"],
                should_not_contain=["punishment", "revenge"]
            ),
            
            # Meditation queries
            TestQuery(
                query="How should I start a meditation practice?",
                context="meditation",
                expected_topics=["meditation", "practice", "breath", "start"],
                should_contain=["🙏", "breath", "practice", "daily"],
                should_not_contain=["instant", "miracle", "guarantee"]
            ),
            
            # Philosophy queries
            TestQuery(
                query="What is the nature of the soul according to Vedanta?",
                context="philosophy",
                expected_topics=["soul", "vedanta", "eternal", "nature"],
                should_contain=["🙏", "eternal", "soul", "consciousness"],
                should_not_contain=["scientific", "proof", "evidence"]
            ),
            
            # Devotional queries
            TestQuery(
                query="How can I develop love and devotion for Krishna?",
                context="devotional",
                expected_topics=["devotion", "love", "krishna", "bhakti"],
                should_contain=["🙏", "Krishna", "love", "devotion"],
                should_not_contain=["ritual", "money", "material"]
            ),
            
            # Edge cases
            TestQuery(
                query="Can you predict my future?",
                context="guidance",
                expected_topics=["spiritual", "guidance", "present"],
                should_contain=["🙏", "spiritual", "present moment"],
                should_not_contain=["predict", "future", "will happen"],
                expected_confidence=0.3  # Lower confidence for redirected queries
            ),
            TestQuery(
                query="What lottery numbers should I pick?",
                context="guidance", 
                expected_topics=["spiritual", "material", "attachment"],
                should_contain=["🙏", "spiritual", "detachment"],
                should_not_contain=["numbers", "lottery", "pick", "win"],
                expected_confidence=0.3  # Lower confidence for redirected queries
            )
        ]
    
    def get_test_users(self) -> List[TestUser]:
        """Get test users for authentication testing"""
        return [
            TestUser(
                user_id="test_user_1",
                email="test1@vedprakash.net",
                name="Test User One",
                preferences={
                    "language": "English",
                    "context_preference": "guidance",
                    "response_length": "medium"
                }
            ),
            TestUser(
                user_id="test_user_2", 
                email="test2@vedprakash.net",
                name="Test User Two",
                preferences={
                    "language": "Hindi",
                    "context_preference": "teaching",
                    "response_length": "brief"
                }
            )
        ]
    
    def create_mock_response_data(self, query: str, context: str) -> Dict[str, Any]:
        """Create mock response data for testing"""
        return {
            "response": f"🙏 Dear soul, thank you for your question about {query[:20]}... This is a test response for {context} context.",
            "confidence": 0.8,
            "citations": ["Test Citation 1", "Test Citation 2"],
            "language": "English",
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "model": "test-model",
                "response_time": 1.5,
                "token_count": 150,
                "safety_check": True
            }
        }
    
    def validate_response_format(self, response_data: Dict[str, Any]) -> List[str]:
        """Validate response format and return list of issues"""
        issues = []
        
        # Required fields
        required_fields = ["response", "confidence"]
        for field in required_fields:
            if field not in response_data:
                issues.append(f"Missing required field: {field}")
        
        # Response format checks
        if "response" in response_data:
            response_text = response_data["response"]
            
            if not response_text.startswith("🙏"):
                issues.append("Response should start with reverent greeting (🙏)")
            
            if len(response_text) < 20:
                issues.append("Response too short (< 20 characters)")
            
            if len(response_text) > 2000:
                issues.append("Response too long (> 2000 characters)")
            
            # Check for spiritual tone
            spiritual_indicators = ["dear soul", "beloved devotee", "dear seeker", "beloved child"]
            if not any(indicator in response_text.lower() for indicator in spiritual_indicators):
                issues.append("Response should use reverent addressing")
        
        # Confidence check
        if "confidence" in response_data:
            confidence = response_data["confidence"]
            if not (0.0 <= confidence <= 1.0):
                issues.append(f"Confidence should be between 0.0 and 1.0, got {confidence}")
        
        return issues


# Global test data manager instance
test_data_manager = TestDataManager()


# Pytest fixtures
@pytest.fixture(scope="session")
def test_environment():
    """Setup test environment for entire test session"""
    temp_dir = test_data_manager.setup_test_environment()
    yield temp_dir
    test_data_manager.teardown_test_environment()


@pytest.fixture
def test_queries():
    """Provide test queries"""
    return test_data_manager.get_test_queries()


@pytest.fixture
def test_users():
    """Provide test users"""
    return test_data_manager.get_test_users()


@pytest.fixture
def mock_response():
    """Provide mock response generator"""
    def _create_mock_response(query: str, context: str = "guidance"):
        return test_data_manager.create_mock_response_data(query, context)
    return _create_mock_response


@pytest.fixture
def response_validator():
    """Provide response validator"""
    return test_data_manager.validate_response_format


# Test helper functions
def assert_valid_spiritual_response(response_data: Dict[str, Any], query: TestQuery = None):
    """Assert that response is valid spiritual guidance"""
    issues = test_data_manager.validate_response_format(response_data)
    assert not issues, f"Response validation failed: {'; '.join(issues)}"
    
    if query:
        # Check expected content
        response_text = response_data["response"].lower()
        
        for should_contain in query.should_contain:
            assert should_contain.lower() in response_text, f"Response should contain '{should_contain}'"
        
        for should_not_contain in query.should_not_contain:
            assert should_not_contain.lower() not in response_text, f"Response should not contain '{should_not_contain}'"
        
        # Check response length
        response_length = len(response_data["response"])
        min_length, max_length = query.expected_response_length
        assert min_length <= response_length <= max_length, f"Response length {response_length} not in range {min_length}-{max_length}"
        
        # Check confidence
        confidence = response_data.get("confidence", 0)
        assert confidence >= query.expected_confidence, f"Confidence {confidence} below expected {query.expected_confidence}"


def create_test_request_data(query: str, context: str = "guidance", **kwargs) -> Dict[str, Any]:
    """Create test request data"""
    base_data = {
        "query": query,
        "context": context,
        "language": "English"
    }
    base_data.update(kwargs)
    return base_data


if __name__ == "__main__":
    # Test the test data manager
    manager = TestDataManager()
    temp_dir = manager.setup_test_environment()
    
    print(f"✅ Test environment created at: {temp_dir}")
    print(f"✅ Test queries available: {len(manager.get_test_queries())}")
    print(f"✅ Test users available: {len(manager.get_test_users())}")
    
    # Test validation
    mock_response = manager.create_mock_response_data("Test query", "guidance")
    issues = manager.validate_response_format(mock_response)
    print(f"✅ Mock response validation: {len(issues)} issues")
    
    manager.teardown_test_environment()
    print("✅ Test environment cleaned up")
