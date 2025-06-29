"""
Test configuration and utilities for Vimarsh project
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

# Test environment setup
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("LOG_LEVEL", "DEBUG")

# Test fixtures and utilities
@pytest.fixture(scope="session")
def project_root():
    """Project root directory"""
    return PROJECT_ROOT

@pytest.fixture(scope="session") 
def test_config():
    """Test configuration settings"""
    return {
        "timeout": 30,
        "max_retries": 3,
        "test_data_dir": PROJECT_ROOT / "tests" / "test_data",
        "backend_url": "http://localhost:8000",
        "frontend_url": "http://localhost:3000"
    }

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "response": "This is a test spiritual guidance response",
        "citations": ["Bhagavad Gita 2.47"],
        "confidence": 0.85
    }

# Test categories
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"  
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on location"""
    for item in items:
        test_path = str(item.fspath)
        
        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)
        elif "/e2e/" in test_path:
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)
