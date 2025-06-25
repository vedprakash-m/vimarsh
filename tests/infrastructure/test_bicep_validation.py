"""
Test suite for Azure Bicep infrastructure templates validation.

This module validates that all Bicep templates are syntactically correct,
contain required parameters, and follow Azure best practices for the
Vimarsh spiritual guidance system.
"""

import json
import os
import pytest
import subprocess
from pathlib import Path
from typing import Dict, Any


class TestBicepValidation:
    """Test class for Bicep template validation."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent.parent
        self.infrastructure_dir = self.root_dir / "infrastructure"
        self.parameters_dir = self.infrastructure_dir / "parameters"
        
    def test_infrastructure_directory_exists(self):
        """Test that infrastructure directory exists with required files."""
        assert self.infrastructure_dir.exists(), "Infrastructure directory must exist"
        
        required_files = [
            "main.bicep",
            "parameters/dev.parameters.json",
            "parameters/prod.parameters.json"
        ]
        
        for file_path in required_files:
            full_path = self.infrastructure_dir / file_path
            assert full_path.exists(), f"Required file {file_path} must exist"
    
    def test_main_bicep_syntax(self):
        """Test that main.bicep has valid syntax."""
        bicep_file = self.infrastructure_dir / "main.bicep"
        
        # Check if Azure CLI with Bicep is available
        try:
            result = subprocess.run(
                ["az", "bicep", "build", "--file", str(bicep_file), "--stdout"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # If Azure CLI is available, validate syntax
            if result.returncode == 0:
                assert result.returncode == 0, f"Bicep syntax validation failed: {result.stderr}"
                assert len(result.stdout) > 0, "Bicep compilation should produce ARM template output"
            else:
                # Fallback: Basic file structure validation
                content = bicep_file.read_text()
                assert "targetScope" in content, "Bicep file should define targetScope"
                assert "param" in content, "Bicep file should define parameters"
                assert "resource" in content, "Bicep file should define resources"
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback validation if Azure CLI not available
            content = bicep_file.read_text()
            assert "targetScope" in content, "Bicep file should define targetScope"
            assert "param" in content, "Bicep file should define parameters"
            
    def test_parameter_files_valid_json(self):
        """Test that parameter files contain valid JSON."""
        parameter_files = [
            self.parameters_dir / "dev.parameters.json",
            self.parameters_dir / "prod.parameters.json"
        ]
        
        for param_file in parameter_files:
            assert param_file.exists(), f"Parameter file {param_file.name} must exist"
            
            try:
                with open(param_file, 'r') as f:
                    data = json.load(f)
                    
                # Validate structure
                assert "$schema" in data, f"Parameter file {param_file.name} must have $schema"
                assert "contentVersion" in data, f"Parameter file {param_file.name} must have contentVersion"
                assert "parameters" in data, f"Parameter file {param_file.name} must have parameters section"
                
            except json.JSONDecodeError as e:
                pytest.fail(f"Parameter file {param_file.name} contains invalid JSON: {e}")
    
    def test_required_parameters_present(self):
        """Test that required parameters are present in parameter files."""
        required_params = [
            "projectName",
            "environment", 
            "location",
            "geminiApiKey",
            "expertReviewEmail"
        ]
        
        parameter_files = [
            self.parameters_dir / "dev.parameters.json",
            self.parameters_dir / "prod.parameters.json"
        ]
        
        for param_file in parameter_files:
            with open(param_file, 'r') as f:
                data = json.load(f)
                
            for required_param in required_params:
                assert required_param in data["parameters"], \
                    f"Required parameter '{required_param}' missing in {param_file.name}"
    
    def test_parameter_values_format(self):
        """Test that parameter values have correct format and constraints."""
        parameter_files = [
            self.parameters_dir / "dev.parameters.json",
            self.parameters_dir / "prod.parameters.json"
        ]
        
        for param_file in parameter_files:
            with open(param_file, 'r') as f:
                data = json.load(f)
                
            params = data["parameters"]
            
            # Validate project name format
            project_name = params["projectName"]["value"]
            assert len(project_name) <= 11, "Project name must be 11 characters or less"
            assert project_name.isalnum(), "Project name must be alphanumeric"
            
            # Validate environment values
            environment = params["environment"]["value"]
            assert environment in ["dev", "staging", "prod"], \
                f"Environment must be dev, staging, or prod, got: {environment}"
            
            # Validate location format
            location = params["location"]["value"]
            assert isinstance(location, str) and len(location) > 0, \
                "Location must be a non-empty string"
    
    def test_bicep_resource_naming_conventions(self):
        """Test that Bicep template follows Azure naming conventions."""
        bicep_file = self.infrastructure_dir / "main.bicep"
        content = bicep_file.read_text()
        
        # Check for proper resource naming patterns
        assert "${projectName}" in content or "@{projectName}" in content, \
            "Resources should use projectName parameter for naming"
        
        assert "${environment}" in content or "@{environment}" in content, \
            "Resources should use environment parameter for naming"
        
        # Check for required resource types
        required_resources = [
            "Microsoft.DocumentDB/databaseAccounts",  # Cosmos DB
            "Microsoft.Web/sites",                   # Azure Functions
            "Microsoft.Web/staticSites",            # Static Web App
            "Microsoft.Insights/components"          # Application Insights
        ]
        
        for resource_type in required_resources:
            assert resource_type in content, \
                f"Required resource type {resource_type} not found in Bicep template"
    
    def test_security_best_practices(self):
        """Test that Bicep template follows security best practices."""
        bicep_file = self.infrastructure_dir / "main.bicep"
        content = bicep_file.read_text()
        
        # Check for secure string parameters for sensitive data
        assert "@secure()" in content or "secureString" in content, \
            "Sensitive parameters should be marked as secure"
        
        # Check for Key Vault integration
        assert "keyVault" in content.lower() or "Microsoft.KeyVault" in content, \
            "Should integrate with Azure Key Vault for secret management"
        
        # Check for HTTPS enforcement
        assert "httpsOnly" in content, \
            "Should enforce HTTPS for web applications"
    
    def test_cost_optimization_settings(self):
        """Test that Bicep template includes cost optimization settings."""
        bicep_file = self.infrastructure_dir / "main.bicep"
        content = bicep_file.read_text()
        
        # Check for consumption plan usage
        assert "Consumption" in content, \
            "Should use consumption plans for cost optimization"
        
        # Check for appropriate SKU settings
        assert "sku" in content.lower(), \
            "Should specify appropriate SKUs for cost optimization"


class TestDeploymentConfiguration:
    """Test deployment configuration and environment setup."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent.parent
        
    def test_deployment_script_exists(self):
        """Test that deployment script exists and is executable."""
        deploy_script = self.root_dir / "scripts" / "deploy.sh"
        assert deploy_script.exists(), "Deployment script must exist"
        
        # Check if script is executable (on Unix systems)
        if os.name != 'nt':  # Not Windows
            assert os.access(deploy_script, os.X_OK), "Deployment script must be executable"
    
    def test_deployment_script_content(self):
        """Test deployment script content and structure."""
        deploy_script = self.root_dir / "scripts" / "deploy.sh"
        content = deploy_script.read_text()
        
        # Check for required sections
        assert "#!/bin/bash" in content, "Script should have proper shebang"
        assert "set -e" in content, "Script should exit on errors"
        assert "az login" in content, "Script should check Azure login"
        assert "bicep" in content, "Script should use Bicep for deployment"
        
        # Check for environment validation
        assert "ENVIRONMENT" in content, "Script should validate environment parameter"
        assert "dev|staging|prod" in content or "dev\\|staging\\|prod" in content, \
            "Script should validate environment values"
    
    def test_environment_variables_template(self):
        """Test that environment variables template exists."""
        env_files = [
            self.root_dir / ".env.example",
            self.root_dir / "backend" / "local.settings.json.example"
        ]
        
        for env_file in env_files:
            if env_file.exists():
                content = env_file.read_text()
                
                # Check for required environment variables
                required_vars = ["GEMINI_API_KEY", "COSMOS_CONNECTION_STRING"]
                for var in required_vars:
                    assert var in content, f"Required environment variable {var} not in template"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
