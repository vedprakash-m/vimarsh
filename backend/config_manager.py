#!/usr/bin/env python3
"""
Configuration Management Script for Vimarsh Backend
Consolidates multiple configuration files into a single, environment-aware system
"""

import json
import os
import shutil
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConfigEnvironment:
    """Configuration for different environments"""
    name: str
    description: str
    config_file: str
    requires_secrets: bool = False


class ConfigManager:
    """Manages configuration across different environments"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.environments = {
            "development": ConfigEnvironment(
                name="development",
                description="Local development with mock services",
                config_file="local.settings.json",
                requires_secrets=False
            ),
            "staging": ConfigEnvironment(
                name="staging",
                description="Staging environment with real Azure services",
                config_file="local.settings.staging.json",
                requires_secrets=True
            ),
            "production": ConfigEnvironment(
                name="production",
                description="Production environment with Key Vault integration",
                config_file="local.settings.production.json",
                requires_secrets=True
            )
        }
        
        # Base configuration that applies to all environments
        self.base_config = {
            "IsEncrypted": False,
            "Values": {
                "AzureWebJobsStorage": "UseDevelopmentStorage=true",
                "FUNCTIONS_WORKER_RUNTIME": "python",
                "FUNCTIONS_EXTENSION_VERSION": "~4",
                
                # Core Application
                "ENVIRONMENT": "development",
                "DEBUG": "true",
                "LOG_LEVEL": "INFO",
                
                # LLM Configuration
                "LLM_MODEL": "gemini-2.5-flash",
                "LLM_TEMPERATURE": "0.7",
                "MAX_TOKENS": "4096",
                "SAFETY_SETTINGS": "BLOCK_MEDIUM_AND_ABOVE",
                
                # Admin Features
                "ADMIN_FEATURES_ENABLED": "true",
                "COST_TRACKING_ENABLED": "true",
                "BUDGET_ENFORCEMENT_ENABLED": "true",
                "DEFAULT_MONTHLY_BUDGET": "50.0",
                "DEFAULT_DAILY_BUDGET": "5.0",
                "DEFAULT_REQUEST_BUDGET": "0.50",
                
                # Authentication
                "AUTH_DEVELOPMENT_MODE": "true",
                "DEV_AUTH_SECRET": "dev-secret-change-in-production",
                
                # Database
                "AZURE_COSMOS_DATABASE_NAME": "vimarsh-multi-personality",
                "AZURE_COSMOS_CONTAINER_NAME": "personality-vectors",
                
                # Monitoring
                "MONITORING_ENABLED": "true",
                "PERFORMANCE_TRACKING_ENABLED": "true"
            }
        }
    
    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Get configuration for a specific environment"""
        if environment not in self.environments:
            raise ValueError(f"Unknown environment: {environment}")
        
        config = self.base_config.copy()
        env_config = self.environments[environment]
        
        # Apply environment-specific overrides
        if environment == "development":
            config["Values"].update({
                "ENVIRONMENT": "development",
                "DEBUG": "true",
                "AZURE_COSMOS_CONNECTION_STRING": "dev-mode-local-storage",
                "GEMINI_API_KEY": "Gemini-Key",
                "AZURE_STORAGE_CONNECTION_STRING": "",
                "GOOGLE_CLOUD_PROJECT": "",
                "AUTH_DEVELOPMENT_MODE": "true",
                "ADMIN_DEV_TOKEN": "dev-admin-token-change-in-production"
            })
        
        elif environment == "staging":
            config["Values"].update({
                "ENVIRONMENT": "staging",
                "DEBUG": "false",
                "LOG_LEVEL": "INFO",
                "AZURE_COSMOS_CONNECTION_STRING": "${AZURE_COSMOS_CONNECTION_STRING}",
                "GEMINI_API_KEY": "${GEMINI_API_KEY}",
                "AZURE_STORAGE_CONNECTION_STRING": "${AZURE_STORAGE_CONNECTION_STRING}",
                "GOOGLE_CLOUD_PROJECT": "${GOOGLE_CLOUD_PROJECT}",
                "AUTH_DEVELOPMENT_MODE": "false",
                "ENTRA_TENANT_ID": "${ENTRA_TENANT_ID}",
                "ENTRA_CLIENT_ID": "${ENTRA_CLIENT_ID}",
                "ENTRA_CLIENT_SECRET": "${ENTRA_CLIENT_SECRET}",
                "ADMIN_DEV_TOKEN": "${ADMIN_DEV_TOKEN}"
            })
        
        elif environment == "production":
            config["Values"].update({
                "ENVIRONMENT": "production",
                "DEBUG": "false",
                "LOG_LEVEL": "WARNING",
                "AZURE_COSMOS_CONNECTION_STRING": "@Microsoft.KeyVault(SecretUri=https://vimarsh-kv.vault.azure.net/secrets/cosmos-conn-str)",
                "GEMINI_API_KEY": "@Microsoft.KeyVault(SecretUri=https://vimarsh-kv.vault.azure.net/secrets/gemini-api-key)",
                "AZURE_STORAGE_CONNECTION_STRING": "@Microsoft.KeyVault(SecretUri=https://vimarsh-kv.vault.azure.net/secrets/storage-conn-str)",
                "GOOGLE_CLOUD_PROJECT": "@Microsoft.KeyVault(SecretUri=https://vimarsh-kv.vault.azure.net/secrets/gcp-project-id)",
                "AUTH_DEVELOPMENT_MODE": "false",
                "ENTRA_TENANT_ID": "@Microsoft.KeyVault(SecretUri=https://vimarsh-kv.vault.azure.net/secrets/entra-tenant-id)",
                "ENTRA_CLIENT_ID": "@Microsoft.KeyVault(SecretUri=https://vimarsh-kv.vault.azure.net/secrets/entra-client-id)",
                "ENTRA_CLIENT_SECRET": "@Microsoft.KeyVault(SecretUri=https://vimarsh-kv.vault.azure.net/secrets/entra-client-secret)",
                "ADMIN_DEV_TOKEN": "@Microsoft.KeyVault(SecretUri=https://vimarsh-kv.vault.azure.net/secrets/admin-dev-token)"
            })
        
        return config
    
    def generate_config_file(self, environment: str, output_path: Optional[str] = None) -> str:
        """Generate configuration file for specified environment"""
        config = self.get_environment_config(environment)
        env_config = self.environments[environment]
        
        if output_path is None:
            output_path = str(self.base_path / env_config.config_file)
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Generated {environment} configuration: {output_path}")
        return output_path
    
    def cleanup_old_configs(self):
        """Remove old configuration files"""
        old_files = [
            "local.settings.json.secure",
            "local.settings.json.template",
            "local.settings.json.new"
        ]
        
        for file in old_files:
            file_path = self.base_path / file
            if file_path.exists():
                print(f"🗑️  Removing old config file: {file}")
                file_path.unlink()
    
    def backup_current_config(self):
        """Backup current configuration"""
        current_config = self.base_path / "local.settings.json"
        if current_config.exists():
            backup_path = self.base_path / "local.settings.json.backup"
            shutil.copy2(current_config, backup_path)
            print(f"💾 Backed up current config to: {backup_path}")
    
    def setup_environment(self, environment: str):
        """Setup configuration for specified environment"""
        print(f"🔧 Setting up {environment} environment...")
        
        # Backup current config
        self.backup_current_config()
        
        # Generate new config
        self.generate_config_file(environment)
        
        # Generate staging and production configs as templates
        if environment == "development":
            self.generate_config_file("staging", "local.settings.staging.json")
            self.generate_config_file("production", "local.settings.production.json")
        
        # Cleanup old files
        self.cleanup_old_configs()
        
        print(f"✅ Environment {environment} setup complete!")
    
    def list_environments(self):
        """List available environments"""
        print("📋 Available environments:")
        for env_name, env_config in self.environments.items():
            print(f"  - {env_name}: {env_config.description}")


def main():
    """Main configuration management function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vimarsh Configuration Manager")
    parser.add_argument("--environment", "-e", default="development", 
                       choices=["development", "staging", "production"],
                       help="Target environment")
    parser.add_argument("--list", "-l", action="store_true", 
                       help="List available environments")
    parser.add_argument("--cleanup", "-c", action="store_true",
                       help="Cleanup old configuration files")
    
    args = parser.parse_args()
    
    manager = ConfigManager()
    
    if args.list:
        manager.list_environments()
    elif args.cleanup:
        manager.cleanup_old_configs()
    else:
        manager.setup_environment(args.environment)


if __name__ == "__main__":
    main()
