"""
Test suite for deployment script validation and execution flow.

This module tests the deployment automation scripts to ensure they work
correctly across different environments and handle edge cases properly.
"""

import os
import pytest
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestDeploymentScript:
    """Test class for deployment script validation."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent.parent
        self.deploy_script = self.root_dir / "scripts" / "deploy.sh"
        
    def test_script_syntax_validation(self):
        """Test that deployment script has valid bash syntax."""
        if not self.deploy_script.exists():
            pytest.skip("Deploy script not found")
            
        # Use bash -n to check syntax without executing
        try:
            result = subprocess.run(
                ["bash", "-n", str(self.deploy_script)],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0, f"Script syntax error: {result.stderr}"
        except subprocess.TimeoutExpired:
            pytest.fail("Script syntax check timed out")
        except FileNotFoundError:
            pytest.skip("Bash not available for syntax checking")
    
    def test_script_permissions(self):
        """Test that script has correct permissions."""
        if not self.deploy_script.exists():
            pytest.skip("Deploy script not found")
            
        # Check if script is executable
        if os.name != 'nt':  # Not Windows
            assert os.access(self.deploy_script, os.X_OK), "Script must be executable"
    
    def test_script_required_commands(self):
        """Test that script contains required command validations."""
        if not self.deploy_script.exists():
            pytest.skip("Deploy script not found")
            
        content = self.deploy_script.read_text()
        
        # Check for required command validations
        required_commands = ["az", "bicep"]
        for cmd in required_commands:
            assert f"command -v {cmd}" in content or f"which {cmd}" in content, \
                f"Script should validate {cmd} command availability"
    
    def test_environment_parameter_validation(self):
        """Test that script validates environment parameters correctly."""
        if not self.deploy_script.exists():
            pytest.skip("Deploy script not found")
            
        content = self.deploy_script.read_text()
        
        # Check for environment validation
        assert "ENVIRONMENT" in content, "Script should validate ENVIRONMENT parameter"
        
        # Check for valid environment values
        valid_envs = ["dev", "staging", "prod"]
        env_validation_found = any(env in content for env in valid_envs)
        assert env_validation_found, "Script should validate environment values"
    
    def test_error_handling(self):
        """Test that script has proper error handling."""
        if not self.deploy_script.exists():
            pytest.skip("Deploy script not found")
            
        content = self.deploy_script.read_text()
        
        # Check for error handling
        assert "set -e" in content, "Script should exit on errors"
        
        # Check for cleanup functions
        error_handling_indicators = ["trap", "cleanup", "exit"]
        assert any(indicator in content for indicator in error_handling_indicators), \
            "Script should have error handling mechanisms"
    
    def test_azure_login_check(self):
        """Test that script checks Azure authentication."""
        if not self.deploy_script.exists():
            pytest.skip("Deploy script not found")
            
        content = self.deploy_script.read_text()
        
        # Check for Azure login validation
        azure_auth_checks = ["az account show", "az login", "az account list"]
        assert any(check in content for check in azure_auth_checks), \
            "Script should validate Azure authentication"
    
    def test_resource_group_creation(self):
        """Test that script handles resource group creation."""
        if not self.deploy_script.exists():
            pytest.skip("Deploy script not found")
            
        content = self.deploy_script.read_text()
        
        # Check for resource group operations
        assert "az group" in content, "Script should handle resource group operations"
        assert "create" in content, "Script should create resource group if needed"
    
    def test_bicep_deployment_logic(self):
        """Test that script uses Bicep for infrastructure deployment."""
        if not self.deploy_script.exists():
            pytest.skip("Deploy script not found")
            
        content = self.deploy_script.read_text()
        
        # Check for Bicep deployment commands
        bicep_commands = ["az deployment", "bicep"]
        assert any(cmd in content for cmd in bicep_commands), \
            "Script should use Bicep for deployment"
        
        # Check for parameter file usage
        assert "parameters" in content, "Script should use parameter files"
    
    def test_output_and_logging(self):
        """Test that script provides appropriate output and logging."""
        if not self.deploy_script.exists():
            pytest.skip("Deploy script not found")
            
        content = self.deploy_script.read_text()
        
        # Check for output commands
        output_commands = ["echo", "printf"]
        assert any(cmd in content for cmd in output_commands), \
            "Script should provide user feedback"
        
        # Check for progress indicators
        progress_indicators = ["Deploying", "Creating", "Configuring"]
        assert any(indicator in content for indicator in progress_indicators), \
            "Script should show deployment progress"


class TestDeploymentValidation:
    """Test deployment validation and post-deployment checks."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent.parent
    
    def test_post_deployment_validation_functions(self):
        """Test that deployment includes validation functions."""
        deploy_script = self.root_dir / "scripts" / "deploy.sh"
        
        if not deploy_script.exists():
            pytest.skip("Deploy script not found")
            
        content = deploy_script.read_text()
        
        # Check for validation functions
        validation_functions = ["validate", "test", "health", "check"]
        assert any(func in content for func in validation_functions), \
            "Script should include post-deployment validation"
    
    def test_configuration_validation(self):
        """Test deployment configuration validation."""
        # Test parameter file validation
        param_files = [
            self.root_dir / "infrastructure" / "parameters" / "dev.parameters.json",
            self.root_dir / "infrastructure" / "parameters" / "prod.parameters.json"
        ]
        
        for param_file in param_files:
            if param_file.exists():
                import json
                try:
                    with open(param_file, 'r') as f:
                        data = json.load(f)
                    
                    # Validate required sections
                    assert "parameters" in data, f"Parameter file {param_file.name} must have parameters"
                    
                    # Validate parameter structure
                    for param_name, param_data in data["parameters"].items():
                        # Allow either direct value or KeyVault reference
                        has_value = "value" in param_data
                        has_reference = "reference" in param_data
                        assert has_value or has_reference, f"Parameter {param_name} must have either 'value' or 'reference'"
                        
                except json.JSONDecodeError:
                    pytest.fail(f"Parameter file {param_file.name} contains invalid JSON")
    
    def test_environment_specific_configurations(self):
        """Test that different environments have appropriate configurations."""
        param_dir = self.root_dir / "infrastructure" / "parameters"
        
        if not param_dir.exists():
            pytest.skip("Parameters directory not found")
        
        env_files = ["dev.parameters.json", "prod.parameters.json"]
        
        for env_file in env_files:
            param_file = param_dir / env_file
            if param_file.exists():
                import json
                with open(param_file, 'r') as f:
                    data = json.load(f)
                
                env_name = env_file.split('.')[0]
                
                # Check environment-specific settings
                if "environment" in data.get("parameters", {}):
                    env_value = data["parameters"]["environment"]["value"]
                    assert env_value == env_name, \
                        f"Environment parameter should match file name: {env_name}"


class TestDocumentationValidation:
    """Test that deployment documentation is comprehensive and accurate."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent.parent
    
    def test_deployment_guide_exists(self):
        """Test that deployment guide documentation exists."""
        deployment_docs = [
            self.root_dir / "docs" / "deployment" / "README.md",
            self.root_dir / "README.md"
        ]
        
        doc_found = any(doc.exists() for doc in deployment_docs)
        assert doc_found, "Deployment documentation must exist"
    
    def test_deployment_guide_completeness(self):
        """Test that deployment guide covers all necessary topics."""
        deployment_guide = self.root_dir / "docs" / "deployment" / "README.md"
        
        if not deployment_guide.exists():
            pytest.skip("Deployment guide not found")
        
        content = deployment_guide.read_text()
        
        # Check for required sections
        required_sections = [
            "Prerequisites",
            "Azure CLI",
            "Resource Group",
            "Environment Variables",
            "Deployment Steps"
        ]
        
        for section in required_sections:
            assert section in content, f"Deployment guide should include {section} section"
    
    def test_api_documentation_exists(self):
        """Test that API documentation exists and is comprehensive."""
        api_docs = [
            self.root_dir / "docs" / "api" / "README.md",
            self.root_dir / "docs" / "api-documentation.md"
        ]
        
        doc_found = any(doc.exists() for doc in api_docs)
        assert doc_found, "API documentation must exist"
    
    def test_troubleshooting_guide_exists(self):
        """Test that troubleshooting guide exists."""
        troubleshooting_guide = self.root_dir / "docs" / "deployment" / "troubleshooting.md"
        
        if troubleshooting_guide.exists():
            content = troubleshooting_guide.read_text()
            
            # Check for common issues coverage
            common_issues = [
                "authentication",
                "permissions", 
                "resource",
                "timeout",
                "configuration"
            ]
            
            for issue in common_issues:
                assert issue.lower() in content.lower(), \
                    f"Troubleshooting guide should cover {issue} issues"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
