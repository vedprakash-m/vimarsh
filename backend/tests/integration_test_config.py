"""
Integration Test Configuration and Utilities

Provides configuration, fixtures, and utilities specifically for integration testing
of RAG pipeline and LLM workflows.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock

# Test configuration constants
INTEGRATION_TEST_TIMEOUT = 30  # seconds
MAX_CONCURRENT_TESTS = 5
MOCK_EMBEDDING_DIMENSION = 384
SAMPLE_RESPONSE_MIN_LENGTH = 50


class IntegrationTestConfig:
    """Configuration class for integration tests."""
    
    # Performance thresholds
    SINGLE_QUERY_TIMEOUT = 10.0  # seconds
    CONCURRENT_QUERY_TIMEOUT = 30.0  # seconds
    AVERAGE_QUERY_TIME_LIMIT = 8.0  # seconds
    
    # Quality thresholds
    MIN_RESPONSE_LENGTH = 50  # characters
    MIN_CITATIONS_COUNT = 1
    MIN_RELEVANCE_SCORE = 0.1
    MIN_CONFIDENCE_SCORE = 0.5
    
    # Spiritual authenticity requirements
    REQUIRED_SPIRITUAL_TERMS = ["devotee", "divine", "soul", "spiritual", "sacred"]
    INAPPROPRIATE_TERMS = ["dude", "bro", "hey", "cool", "awesome", "whatever"]
    KRISHNA_PERSONA_INDICATORS = ["devotee", "beloved", "arjuna", "kurukshetra", "gita", "taught"]
    
    # Language support
    SUPPORTED_LANGUAGES = ["English", "Hindi"]
    
    # Content validation
    SPIRITUAL_THEMES = {
        "duty": ["dharma", "purpose", "duty", "path", "responsibility"],
        "peace": ["peace", "meditation", "calm", "mind", "tranquility"],
        "wisdom": ["wisdom", "guidance", "knowledge", "understanding", "insight"],
        "devotion": ["devotion", "love", "surrender", "faith", "bhakti"],
        "karma": ["karma", "action", "consequence", "deed", "effect"]
    }


class MockComponentFactory:
    """Factory for creating mock components for integration testing."""
    
    @staticmethod
    def create_mock_gemini_client() -> Mock:
        """Create a mock Gemini client with realistic behavior."""
        client = Mock()
        client.generate_response = AsyncMock()
        client.health_check = AsyncMock(return_value={"status": "healthy"})
        
        # Configure default response
        client.generate_response.return_value = {
            "response": "Dear devotee, your question touches the very essence of spiritual wisdom. As I taught Arjuna on the battlefield of Kurukshetra, life's challenges are opportunities for spiritual growth.",
            "usage": {"input_tokens": 150, "output_tokens": 75},
            "model": "gemini-pro",
            "confidence": 0.89,
            "safety_ratings": {
                "harassment": "NEGLIGIBLE",
                "hate_speech": "NEGLIGIBLE",
                "sexually_explicit": "NEGLIGIBLE",
                "dangerous_content": "NEGLIGIBLE"
            }
        }
        
        return client
    
    @staticmethod
    def create_mock_rag_pipeline() -> Dict[str, Mock]:
        """Create mock RAG pipeline components."""
        return {
            "document_loader": Mock(),
            "text_processor": Mock(),
            "vector_storage": Mock(),
            "embeddings": Mock()
        }
    
    @staticmethod
    def create_mock_spiritual_context() -> List[Dict[str, Any]]:
        """Create mock spiritual context for testing."""
        return [
            {
                "text": "You have a right to perform your prescribed duties, but never to the fruits of action.",
                "source": "Bhagavad Gita",
                "chapter": 2,
                "verse": 47,
                "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
                "relevance_score": 0.95,
                "embedding_distance": 0.05
            },
            {
                "text": "Better is one's own dharma, though imperfectly performed, than the dharma of another well performed.",
                "source": "Bhagavad Gita",
                "chapter": 3,
                "verse": 35,
                "sanskrit": "श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्",
                "relevance_score": 0.88,
                "embedding_distance": 0.12
            },
            {
                "text": "The soul is eternal, indestructible, and beyond time.",
                "source": "Bhagavad Gita",
                "chapter": 2,
                "verse": 20,
                "sanskrit": "न जायते म्रियते वा कदाचिन्",
                "relevance_score": 0.85,
                "embedding_distance": 0.15
            }
        ]


class IntegrationTestValidator:
    """Validator for integration test results."""
    
    @staticmethod
    def validate_response_structure(result: Dict[str, Any]) -> bool:
        """Validate that response has required structure."""
        required_fields = ["response", "citations", "metadata"]
        return all(field in result for field in required_fields)
    
    @staticmethod
    def validate_response_quality(result: Dict[str, Any]) -> List[str]:
        """Validate response quality and return list of issues."""
        issues = []
        
        if not result.get("response"):
            issues.append("Missing response content")
            return issues
        
        response = result["response"]
        
        # Length check
        if len(response) < IntegrationTestConfig.MIN_RESPONSE_LENGTH:
            issues.append(f"Response too short: {len(response)} chars")
        
        # Citations check
        citations = result.get("citations", [])
        if len(citations) < IntegrationTestConfig.MIN_CITATIONS_COUNT:
            issues.append(f"Insufficient citations: {len(citations)}")
        
        # Spiritual tone check
        response_lower = response.lower()
        
        # Check for inappropriate language
        inappropriate_found = [
            term for term in IntegrationTestConfig.INAPPROPRIATE_TERMS
            if term in response_lower
        ]
        if inappropriate_found:
            issues.append(f"Inappropriate terms found: {inappropriate_found}")
        
        # Check for spiritual language
        spiritual_found = [
            term for term in IntegrationTestConfig.REQUIRED_SPIRITUAL_TERMS
            if term in response_lower
        ]
        if not spiritual_found:
            issues.append("No spiritual language indicators found")
        
        return issues
    
    @staticmethod
    def validate_citations(citations: List[Dict[str, Any]]) -> List[str]:
        """Validate citation quality and return list of issues."""
        issues = []
        
        for i, citation in enumerate(citations):
            if "source" not in citation:
                issues.append(f"Citation {i}: Missing source")
            
            if "relevance_score" not in citation:
                issues.append(f"Citation {i}: Missing relevance score")
            else:
                score = citation["relevance_score"]
                if not (0 <= score <= 1):
                    issues.append(f"Citation {i}: Invalid relevance score {score}")
            
            # Check source meaningfulness
            source = citation.get("source", "")
            if len(source) < 3 or source == "Unknown Source":
                issues.append(f"Citation {i}: Invalid source '{source}'")
        
        return issues
    
    @staticmethod
    def validate_metadata(metadata: Dict[str, Any]) -> List[str]:
        """Validate metadata completeness and return list of issues."""
        issues = []
        
        required_fields = [
            "language", "processing_time_ms", "model_version", 
            "confidence_score", "spiritual_authenticity"
        ]
        
        for field in required_fields:
            if field not in metadata:
                issues.append(f"Missing metadata field: {field}")
        
        # Validate specific field values
        if "confidence_score" in metadata:
            confidence = metadata["confidence_score"]
            if not (0 <= confidence <= 1):
                issues.append(f"Invalid confidence score: {confidence}")
        
        if "processing_time_ms" in metadata:
            time_ms = metadata["processing_time_ms"]
            if not isinstance(time_ms, (int, float)) or time_ms < 0:
                issues.append(f"Invalid processing time: {time_ms}")
        
        return issues


class IntegrationTestPerformanceMonitor:
    """Monitor performance during integration tests."""
    
    def __init__(self):
        self.query_times = []
        self.response_sizes = []
        self.error_counts = {}
    
    def record_query_time(self, query_time: float):
        """Record query execution time."""
        self.query_times.append(query_time)
    
    def record_response_size(self, response_size: int):
        """Record response size."""
        self.response_sizes.append(response_size)
    
    def record_error(self, error_type: str):
        """Record error occurrence."""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.query_times:
            return {"status": "no_data"}
        
        return {
            "total_queries": len(self.query_times),
            "avg_query_time": sum(self.query_times) / len(self.query_times),
            "max_query_time": max(self.query_times),
            "min_query_time": min(self.query_times),
            "avg_response_size": sum(self.response_sizes) / len(self.response_sizes) if self.response_sizes else 0,
            "total_errors": sum(self.error_counts.values()),
            "error_breakdown": self.error_counts,
            "performance_issues": self._identify_performance_issues()
        }
    
    def _identify_performance_issues(self) -> List[str]:
        """Identify performance issues."""
        issues = []
        
        if self.query_times:
            avg_time = sum(self.query_times) / len(self.query_times)
            if avg_time > IntegrationTestConfig.AVERAGE_QUERY_TIME_LIMIT:
                issues.append(f"Average query time {avg_time:.2f}s exceeds limit")
            
            max_time = max(self.query_times)
            if max_time > IntegrationTestConfig.SINGLE_QUERY_TIMEOUT:
                issues.append(f"Maximum query time {max_time:.2f}s exceeds timeout")
        
        error_rate = sum(self.error_counts.values()) / len(self.query_times) if self.query_times else 0
        if error_rate > 0.1:  # 10% error rate threshold
            issues.append(f"High error rate: {error_rate:.1%}")
        
        return issues


# Pytest fixtures for integration testing
@pytest.fixture(scope="session")
def integration_test_config():
    """Provide integration test configuration."""
    return IntegrationTestConfig()


@pytest.fixture
def mock_components():
    """Provide mock components for integration testing."""
    return {
        "gemini_client": MockComponentFactory.create_mock_gemini_client(),
        "rag_pipeline": MockComponentFactory.create_mock_rag_pipeline(),
        "spiritual_context": MockComponentFactory.create_mock_spiritual_context()
    }


@pytest.fixture
def test_validator():
    """Provide test result validator."""
    return IntegrationTestValidator()


@pytest.fixture
def performance_monitor():
    """Provide performance monitor for tests."""
    return IntegrationTestPerformanceMonitor()


@pytest.fixture
def temp_test_environment():
    """Create temporary test environment."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield {
            "temp_dir": temp_dir,
            "data_dir": Path(temp_dir) / "data",
            "vector_dir": Path(temp_dir) / "vectors",
            "config_dir": Path(temp_dir) / "config"
        }


# Utility functions for integration tests
def create_test_spiritual_documents(data_dir: Path) -> List[Path]:
    """Create test spiritual documents in the data directory."""
    data_dir.mkdir(exist_ok=True)
    
    documents = {
        "bhagavad_gita_sample.txt": """
Chapter 2: The Yoga of Knowledge

Verse 47:
कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥

Translation: You have a right to perform your prescribed duties, 
but never to the fruits of action. Never consider yourself the cause 
of the results of your activities, and never be attached to not doing your duty.
        """,
        "upanishad_sample.txt": """
From the Isha Upanishad:

ईशावास्यमिदं सर्वं यत्किञ्च जगत्यां जगत्।
तेन त्यक्तेन भुञ्जीथा मा गृधः कस्यस्विद्धनम्॥

Translation: The universe is the creation of the Supreme Power 
meant for the benefit of all creation. Each individual life form 
must learn to enjoy its benefits by forming a part of the system.
        """
    }
    
    created_files = []
    for filename, content in documents.items():
        file_path = data_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        created_files.append(file_path)
    
    return created_files


def assert_spiritual_response_quality(result: Dict[str, Any], config: IntegrationTestConfig):
    """Assert that response meets spiritual quality standards."""
    validator = IntegrationTestValidator()
    
    # Structure validation
    assert validator.validate_response_structure(result), "Invalid response structure"
    
    # Quality validation
    quality_issues = validator.validate_response_quality(result)
    assert not quality_issues, f"Quality issues found: {quality_issues}"
    
    # Citation validation
    citation_issues = validator.validate_citations(result.get("citations", []))
    assert not citation_issues, f"Citation issues found: {citation_issues}"
    
    # Metadata validation
    metadata_issues = validator.validate_metadata(result.get("metadata", {}))
    assert not metadata_issues, f"Metadata issues found: {metadata_issues}"


def assert_performance_requirements(execution_time: float, config: IntegrationTestConfig):
    """Assert that performance meets requirements."""
    assert execution_time < config.SINGLE_QUERY_TIMEOUT, \
        f"Execution time {execution_time:.2f}s exceeds timeout {config.SINGLE_QUERY_TIMEOUT}s"


async def run_concurrent_test_queries(api, queries: List[str], config: IntegrationTestConfig) -> List[Dict[str, Any]]:
    """Run multiple queries concurrently and return results."""
    tasks = [api.process_query(query) for query in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and return successful results
    successful_results = [
        result for result in results 
        if not isinstance(result, Exception)
    ]
    
    return successful_results
