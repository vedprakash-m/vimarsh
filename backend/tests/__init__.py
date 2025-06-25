"""
Comprehensive test suite for Vimarsh backend components.

This package contains unit tests, integration tests, and validation tests
for all backend components of the Vimarsh spiritual guidance platform.

Test Structure:
- unit/: Unit tests for individual components
- integration/: Integration tests for component interactions
- fixtures/: Test data and mock objects
- helpers/: Test utilities and common functions

Quality Standards:
- All tests must maintain spiritual content reverence
- Error handling must be comprehensive
- Sanskrit terminology handling must be tested
- Cultural sensitivity must be validated
- Performance requirements must be met
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Test configuration constants
TEST_DATA_DIR = backend_dir / "tests" / "fixtures"
MOCK_SPIRITUAL_TEXTS_DIR = TEST_DATA_DIR / "spiritual_texts"

# Ensure test directories exist
TEST_DATA_DIR.mkdir(exist_ok=True)
MOCK_SPIRITUAL_TEXTS_DIR.mkdir(exist_ok=True)
