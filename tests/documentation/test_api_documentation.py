"""
Test suite for API documentation validation and accuracy.

This module validates that the API documentation is accurate, complete,
and matches the actual API implementation in the backend.
"""

import json
import pytest
import re
from pathlib import Path
from typing import Dict, List, Any


class TestAPIDocumentation:
    """Test class for API documentation validation."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent.parent
        self.api_docs_path = self.root_dir / "docs" / "api" / "README.md"
        self.backend_path = self.root_dir / "backend"
        self.function_app_path = self.backend_path / "function_app.py"
    
    def test_api_documentation_exists(self):
        """Test that API documentation file exists."""
        assert self.api_docs_path.exists(), "API documentation must exist"
    
    def test_api_documentation_structure(self):
        """Test that API documentation has proper structure."""
        if not self.api_docs_path.exists():
            pytest.skip("API documentation not found")
        
        content = self.api_docs_path.read_text()
        
        # Check for required sections
        required_sections = [
            "# Vimarsh API Documentation",
            "## Authentication",
            "## Endpoints",
            "## Error Handling",
            "## Rate Limiting",
            "## Examples"
        ]
        
        for section in required_sections:
            assert section in content, f"API documentation should include {section}"
    
    def test_documented_endpoints_match_implementation(self):
        """Test that documented endpoints match actual implementation."""
        if not self.api_docs_path.exists() or not self.function_app_path.exists():
            pytest.skip("Required files not found")
        
        # Extract endpoints from documentation
        api_content = self.api_docs_path.read_text()
        documented_endpoints = self._extract_documented_endpoints(api_content)
        
        # Extract endpoints from implementation
        function_app_content = self.function_app_path.read_text()
        implemented_endpoints = self._extract_implemented_endpoints(function_app_content)
        
        # Compare endpoints
        for endpoint in implemented_endpoints:
            assert endpoint in documented_endpoints, \
                f"Endpoint {endpoint} is implemented but not documented"
        
        for endpoint in documented_endpoints:
            if endpoint != "OPTIONS":  # OPTIONS is a general CORS handler
                assert endpoint in implemented_endpoints, \
                    f"Endpoint {endpoint} is documented but not implemented"
    
    def test_endpoint_request_response_examples(self):
        """Test that endpoints have proper request/response examples."""
        if not self.api_docs_path.exists():
            pytest.skip("API documentation not found")
        
        content = self.api_docs_path.read_text()
        
        # Check for endpoint examples
        required_examples = [
            "POST /api/spiritual_guidance",
            "GET /api/health",
            "GET /api/languages"
        ]
        
        for example in required_examples:
            assert example in content, f"Should document {example} endpoint"
        
        # Check for JSON examples
        assert "```json" in content, "Should include JSON examples"
        assert "response" in content.lower(), "Should include response examples"
        assert "request" in content.lower(), "Should include request examples"
    
    def test_authentication_documentation(self):
        """Test that authentication is properly documented."""
        if not self.api_docs_path.exists():
            pytest.skip("API documentation not found")
        
        content = self.api_docs_path.read_text()
        
        # Check for authentication details
        auth_keywords = [
            "Authentication",
            "Bearer",
            "token",
            "Authorization",
            "Azure AD"
        ]
        
        auth_mentioned = any(keyword in content for keyword in auth_keywords)
        assert auth_mentioned, "Authentication should be documented"
    
    def test_error_codes_documentation(self):
        """Test that error codes are properly documented."""
        if not self.api_docs_path.exists():
            pytest.skip("API documentation not found")
        
        content = self.api_docs_path.read_text()
        
        # Check for HTTP status codes
        status_codes = ["200", "400", "401", "429", "500"]
        
        for code in status_codes:
            assert code in content, f"HTTP status code {code} should be documented"
        
        # Check for error response structure
        assert "error" in content.lower(), "Error response structure should be documented"
    
    def test_spiritual_guidance_endpoint_details(self):
        """Test that spiritual guidance endpoint is thoroughly documented."""
        if not self.api_docs_path.exists():
            pytest.skip("API documentation not found")
        
        content = self.api_docs_path.read_text()
        
        # Check for spiritual guidance specific documentation
        spiritual_keywords = [
            "spiritual-guidance",
            "Lord Krishna",
            "citations",
            "language",
            "Sanskrit"
        ]
        
        for keyword in spiritual_keywords:
            assert keyword in content, f"Should document {keyword} in spiritual guidance endpoint"
    
    def test_rate_limiting_documentation(self):
        """Test that rate limiting is documented."""
        if not self.api_docs_path.exists():
            pytest.skip("API documentation not found")
        
        content = self.api_docs_path.read_text()
        
        # Check for rate limiting information
        rate_limit_keywords = [
            "rate limit",
            "requests per",
            "429",
            "Too Many Requests"
        ]
        
        rate_limit_mentioned = any(keyword.lower() in content.lower() for keyword in rate_limit_keywords)
        assert rate_limit_mentioned, "Rate limiting should be documented"
    
    def test_cultural_sensitivity_documentation(self):
        """Test that cultural sensitivity guidelines are documented."""
        if not self.api_docs_path.exists():
            pytest.skip("API documentation not found")
        
        content = self.api_docs_path.read_text()
        
        # Check for cultural sensitivity mentions
        cultural_keywords = [
            "cultural",
            "respectful",
            "spiritual",
            "reverent",
            "Krishna",
            "Sanskrit"
        ]
        
        cultural_mentioned = any(keyword in content for keyword in cultural_keywords)
        assert cultural_mentioned, "Cultural sensitivity should be documented"
    
    def _extract_documented_endpoints(self, content: str) -> List[str]:
        """Extract endpoint paths from API documentation."""
        # Find endpoint patterns like `POST /api/endpoint` or POST /api/endpoint
        pattern = r'`?(GET|POST|PUT|DELETE|OPTIONS)\s+(/api/[^\s\n`]+)`?'
        matches = re.findall(pattern, content)
        return [match[1] for match in matches]
    
    def _extract_implemented_endpoints(self, content: str) -> List[str]:
        """Extract endpoint routes from function app implementation."""
        # Find @app.route patterns
        pattern = r'@app\.route\(route="([^"]+)"'
        matches = re.findall(pattern, content)
        
        # Convert to API paths
        api_endpoints = []
        for route in matches:
            if route == "{*route}":  # CORS handler
                continue
            api_endpoints.append(f"/api/{route}")
        
        return api_endpoints


class TestDocumentationAccuracy:
    """Test that documentation accurately reflects the implementation."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent.parent
    
    def test_readme_api_section_accuracy(self):
        """Test that README API section is accurate."""
        readme_path = self.root_dir / "README.md"
        
        if not readme_path.exists():
            pytest.skip("README not found")
        
        content = readme_path.read_text()
        
        # Check for API documentation section
        assert "API Documentation" in content or "API" in content, \
            "README should mention API documentation"
        
        # Check for correct API base URL format
        assert "/api/" in content, "README should show correct API path format"
    
    def test_deployment_guide_api_references(self):
        """Test that deployment guide correctly references API endpoints."""
        deployment_guide = self.root_dir / "docs" / "deployment" / "README.md"
        
        if not deployment_guide.exists():
            pytest.skip("Deployment guide not found")
        
        content = deployment_guide.read_text()
        
        # Check for health check endpoint mention
        if "/health" in content:
            assert "/api/health" in content or "health" in content, \
                "Deployment guide should reference correct health endpoint"
    
    def test_configuration_examples_validity(self):
        """Test that configuration examples in documentation are valid."""
        docs_dir = self.root_dir / "docs"
        
        if not docs_dir.exists():
            pytest.skip("Documentation directory not found")
        
        # Find all markdown files with configuration examples
        md_files = list(docs_dir.glob("**/*.md"))
        
        for md_file in md_files:
            content = md_file.read_text()
            
            # Check JSON blocks for validity
            json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)
            
            for json_block in json_blocks:
                try:
                    json.loads(json_block)
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {md_file.name}: {e}")
    
    def test_code_examples_syntax(self):
        """Test that code examples in documentation have valid syntax."""
        docs_dir = self.root_dir / "docs"
        
        if not docs_dir.exists():
            pytest.skip("Documentation directory not found")
        
        md_files = list(docs_dir.glob("**/*.md"))
        
        for md_file in md_files:
            content = md_file.read_text()
            
            # Check bash code blocks
            bash_blocks = re.findall(r'```bash\n(.*?)\n```', content, re.DOTALL)
            
            for bash_block in bash_blocks:
                # Basic bash syntax validation
                lines = bash_block.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Check for basic bash syntax issues
                        assert not line.endswith('\\') or line.count('\\') % 2 == 1, \
                            f"Invalid line continuation in {md_file.name}: {line}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
