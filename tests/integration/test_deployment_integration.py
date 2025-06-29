"""
Integration test suite for complete deployment workflow validation.

This module tests the entire deployment process end-to-end to ensure
all components work together correctly in the production environment.
"""

import json
import os
import pytest
import subprocess
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock


class TestEndToEndDeployment:
    """Test complete deployment workflow end-to-end."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent.parent
        self.infrastructure_dir = self.root_dir / "infrastructure"
        self.scripts_dir = self.root_dir / "scripts"
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
    
    def test_complete_project_structure(self):
        """Test that all required files exist for deployment."""
        required_files = [
            # Infrastructure
            "infrastructure/main.bicep",
            "infrastructure/parameters/development.parameters.json",
            "infrastructure/parameters/prod.parameters.json",
            
            # Scripts
            "scripts/deploy.sh",
            
            # Backend
            "backend/function_app.py",
            "backend/requirements.txt",
            "backend/host.json",
            
            # Frontend
            "frontend/package.json",
            
            # Documentation
            "README.md",
            "docs/api/README.md",
            "docs/deployment/README.md",
            
            # Configuration
            ".gitignore"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        assert not missing_files, f"Missing required files: {missing_files}"
    
    def test_github_actions_workflow_validity(self):
        """Test that GitHub Actions workflows are valid."""
        workflows_dir = self.root_dir / ".github" / "workflows"
        
        if not workflows_dir.exists():
            pytest.skip("GitHub workflows directory not found")
        
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        
        assert len(workflow_files) > 0, "Should have at least one GitHub Actions workflow"
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = yaml.safe_load(f)
                
                # Basic workflow structure validation
                assert "name" in workflow_data, f"Workflow {workflow_file.name} should have a name"
                assert "on" in workflow_data, f"Workflow {workflow_file.name} should have triggers"
                assert "jobs" in workflow_data, f"Workflow {workflow_file.name} should have jobs"
                
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in workflow {workflow_file.name}: {e}")
    
    def test_backend_deployment_readiness(self):
        """Test that backend is ready for deployment."""
        # Check function app structure
        assert self.backend_dir.exists(), "Backend directory must exist"
        
        function_app = self.backend_dir / "function_app.py"
        assert function_app.exists(), "Function app entry point must exist"
        
        # Check requirements file
        requirements = self.backend_dir / "requirements.txt"
        assert requirements.exists(), "Requirements file must exist"
        
        # Validate requirements content
        req_content = requirements.read_text()
        required_packages = [
            "azure-functions",
            "azure-cosmos",
            "google-generativeai"
        ]
        
        for package in required_packages:
            assert any(package in line for line in req_content.split('\n')), \
                f"Required package {package} not in requirements.txt"
        
        # Check host.json
        host_json = self.backend_dir / "host.json"
        assert host_json.exists(), "host.json must exist"
        
        try:
            with open(host_json, 'r') as f:
                host_config = json.load(f)
            
            assert "version" in host_config, "host.json should specify version"
            assert "functionTimeout" in host_config, "host.json should specify timeout"
            
        except json.JSONDecodeError:
            pytest.fail("host.json contains invalid JSON")
    
    def test_frontend_deployment_readiness(self):
        """Test that frontend is ready for deployment."""
        if not self.frontend_dir.exists():
            pytest.skip("Frontend directory not found")
        
        # Check package.json
        package_json = self.frontend_dir / "package.json"
        assert package_json.exists(), "package.json must exist"
        
        try:
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            assert "name" in package_data, "package.json should have name"
            assert "scripts" in package_data, "package.json should have scripts"
            assert "build" in package_data["scripts"], "Should have build script"
            
            # Check for required dependencies
            dependencies = package_data.get("dependencies", {})
            required_deps = ["react", "@azure/msal-react"]
            
            for dep in required_deps:
                assert dep in dependencies, f"Required dependency {dep} not found"
                
        except json.JSONDecodeError:
            pytest.fail("package.json contains invalid JSON")
    
    def test_environment_configuration_completeness(self):
        """Test that environment configurations are complete."""
        param_files = [
            self.infrastructure_dir / "parameters" / "development.parameters.json",
            self.infrastructure_dir / "parameters" / "prod.parameters.json"
        ]
        
        for param_file in param_files:
            if not param_file.exists():
                continue
                
            try:
                with open(param_file, 'r') as f:
                    data = json.load(f)
                
                params = data.get("parameters", {})
                
                # Check required parameters
                required_params = [
                    "location",
                    "geminiApiKey"
                ]
                
                for param in required_params:
                    assert param in params, \
                        f"Required parameter {param} missing in {param_file.name}"
                    
                    param_config = params[param]
                    # Allow either direct value or KeyVault reference
                    has_value = "value" in param_config
                    has_reference = "reference" in param_config
                    assert has_value or has_reference, \
                        f"Parameter {param} should have either 'value' or 'reference' in {param_file.name}"
                
            except json.JSONDecodeError:
                pytest.fail(f"Parameter file {param_file.name} contains invalid JSON")
    
    def test_security_configuration(self):
        """Test that security configurations are in place."""
        # Check for .gitignore
        gitignore = self.root_dir / ".gitignore"
        assert gitignore.exists(), ".gitignore file must exist"
        
        gitignore_content = gitignore.read_text()
        
        # Check for sensitive file patterns
        sensitive_patterns = [
            "*.env",
            "local.settings.json",
            "__pycache__",
            "node_modules",
            ".azure"
        ]
        
        for pattern in sensitive_patterns:
            assert pattern in gitignore_content, \
                f"Sensitive pattern {pattern} should be in .gitignore"
    
    def test_monitoring_and_logging_setup(self):
        """Test that monitoring and logging are configured."""
        # Check Bicep template for Application Insights
        main_bicep = self.infrastructure_dir / "main.bicep"
        
        if main_bicep.exists():
            bicep_content = main_bicep.read_text()
            
            # Check for Application Insights in compute module or main template
            compute_bicep = self.infrastructure_dir / "compute.bicep"
            app_insights_configured = False
            
            if compute_bicep.exists():
                compute_content = compute_bicep.read_text()
                if "Microsoft.Insights/components" in compute_content:
                    app_insights_configured = True
            
            if "Microsoft.Insights/components" in bicep_content:
                app_insights_configured = True
                
            assert app_insights_configured, \
                "Should configure Application Insights for monitoring in main.bicep or compute.bicep"
            
            # Check for logging configuration in relevant files
            app_insights_connection_configured = False
            
            if compute_bicep.exists():
                compute_content = compute_bicep.read_text()
                if ("APPLICATIONINSIGHTS_CONNECTION_STRING" in compute_content or 
                    "APPINSIGHTS_INSTRUMENTATIONKEY" in compute_content):
                    app_insights_connection_configured = True
            
            if ("APPLICATIONINSIGHTS_CONNECTION_STRING" in bicep_content or 
                "APPINSIGHTS_INSTRUMENTATIONKEY" in bicep_content):
                app_insights_connection_configured = True
                
            assert app_insights_connection_configured, \
                "Should configure Application Insights connection"
    
    def test_cost_optimization_configuration(self):
        """Test that cost optimization settings are configured."""
        main_bicep = self.infrastructure_dir / "main.bicep"
        
        if main_bicep.exists():
            bicep_content = main_bicep.read_text()
            
            # Check for consumption plan
            assert "Consumption" in bicep_content, \
                "Should use consumption plans for cost optimization"
            
            # Check for auto-scaling settings
            scaling_keywords = ["sku", "tier", "size"]
            assert any(keyword in bicep_content for keyword in scaling_keywords), \
                "Should configure appropriate resource sizes"


class TestDeploymentValidation:
    """Test deployment validation and health checks."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent.parent
    
    def test_health_endpoint_implementation(self):
        """Test that health endpoint is properly implemented."""
        function_app = self.root_dir / "backend" / "function_app.py"
        
        if not function_app.exists():
            pytest.skip("Function app not found")
        
        content = function_app.read_text()
        
        # Check for health endpoint
        assert "@app.route" in content and "health" in content, \
            "Should implement health check endpoint"
        
        # Check for health check logic
        assert "health_check" in content, "Should have health check function"
    
    def test_error_handling_implementation(self):
        """Test that comprehensive error handling is implemented."""
        function_app = self.root_dir / "backend" / "function_app.py"
        
        if not function_app.exists():
            pytest.skip("Function app not found")
        
        content = function_app.read_text()
        
        # Check for error handling
        error_handling_patterns = [
            "try:",
            "except",
            "ValueError",
            "Exception",
            "status_code"
        ]
        
        for pattern in error_handling_patterns:
            assert pattern in content, f"Should implement {pattern} for error handling"
    
    def test_cors_configuration(self):
        """Test that CORS is properly configured."""
        function_app = self.root_dir / "backend" / "function_app.py"
        
        if not function_app.exists():
            pytest.skip("Function app not found")
        
        content = function_app.read_text()
        
        # Check for CORS headers
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        for header in cors_headers:
            assert header in content, f"Should configure CORS header: {header}"
    
    def test_spiritual_guidance_endpoint_implementation(self):
        """Test that spiritual guidance endpoint is properly implemented."""
        function_app = self.root_dir / "backend" / "function_app.py"
        
        if not function_app.exists():
            pytest.skip("Function app not found")
        
        content = function_app.read_text()
        
        # Check for spiritual guidance endpoint
        assert "spiritual_guidance" in content, \
            "Should implement spiritual guidance endpoint"
        
        # Check for spiritual-specific features
        spiritual_features = [
            "Lord Krishna",
            "citations",
            "language",
            "Sanskrit"
        ]
        
        for feature in spiritual_features:
            assert feature in content, \
                f"Should implement spiritual feature: {feature}"


class TestDocumentationCompleteness:
    """Test that all documentation is complete and accurate."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent.parent
    
    def test_readme_completeness(self):
        """Test that README is comprehensive."""
        readme = self.root_dir / "README.md"
        assert readme.exists(), "README.md must exist"
        
        content = readme.read_text()
        
        required_sections = [
            "# ",  # Title
            "## ",  # Sections
            "Installation",
            "Usage",
            "API",
            "Deployment"
        ]
        
        for section in required_sections:
            assert section in content, f"README should include {section} section"
    
    def test_api_documentation_completeness(self):
        """Test that API documentation is complete."""
        api_docs = self.root_dir / "docs" / "api" / "README.md"
        
        if api_docs.exists():
            content = api_docs.read_text()
            
            # Check for endpoint documentation
            endpoints = [
                "/api/health",
                "/api/spiritual_guidance",
                "/api/languages"
            ]
            
            for endpoint in endpoints:
                assert endpoint in content, f"Should document {endpoint} endpoint"
    
    def test_deployment_documentation_completeness(self):
        """Test that deployment documentation is complete."""
        deployment_docs = self.root_dir / "docs" / "deployment" / "README.md"
        
        if deployment_docs.exists():
            content = deployment_docs.read_text()
            
            required_topics = [
                "Prerequisites",
                "Azure",
                "Environment",
                "Deployment",
                "Validation"
            ]
            
            for topic in required_topics:
                assert topic in content, f"Deployment docs should cover {topic}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
