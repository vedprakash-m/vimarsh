"""
Unified Configuration System for Vimarsh Backend
Provides centralized configuration management with validation and environment awareness
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    

class ConfigSection(Enum):
    """Configuration sections"""
    AZURE = "azure"
    LLM = "llm"
    AUTH = "auth"
    DATABASE = "database"
    MONITORING = "monitoring"
    SECURITY = "security"
    ADMIN = "admin"
    COST = "cost"


@dataclass
class ConfigValidationRule:
    """Validation rule for configuration values"""
    required: bool = False
    data_type: type = str
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[str]] = None
    pattern: Optional[str] = None
    
    
@dataclass
class ConfigItem:
    """Configuration item with validation"""
    key: str
    value: Any
    section: ConfigSection
    description: str
    validation: ConfigValidationRule = field(default_factory=ConfigValidationRule)
    environment_specific: bool = False


class UnifiedConfig:
    """Unified configuration management system"""
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self.config_data: Dict[str, Any] = {}
        self.validation_rules: Dict[str, ConfigValidationRule] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Load configuration
        self._load_configuration()
        self._setup_validation_rules()
        
    def _load_configuration(self):
        """Load configuration from environment variables and files"""
        # Load from Azure Functions configuration
        config_file = self._get_config_file_path()
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    if 'Values' in file_config:
                        self.config_data.update(file_config['Values'])
            except Exception as e:
                logger.warning(f"Could not load configuration file {config_file}: {e}")
        
        # Override with environment variables
        for key, value in os.environ.items():
            self.config_data[key] = value
            
    def _get_config_file_path(self) -> Path:
        """Get the appropriate config file path for the environment"""
        if self.environment == Environment.PRODUCTION:
            return Path("local.settings.production.json")
        elif self.environment == Environment.STAGING:
            return Path("local.settings.staging.json")
        else:
            return Path("local.settings.json")
    
    def _setup_validation_rules(self):
        """Setup validation rules for configuration items"""
        self.validation_rules = {
            # Azure Configuration
            "AZURE_CLIENT_ID": ConfigValidationRule(required=False, data_type=str),
            "AZURE_TENANT_ID": ConfigValidationRule(required=False, data_type=str),
            "AZURE_CLIENT_SECRET": ConfigValidationRule(required=False, data_type=str),
            "COSMOSDB_CONNECTION_STRING": ConfigValidationRule(required=False, data_type=str),
            "APPLICATIONINSIGHTS_CONNECTION_STRING": ConfigValidationRule(required=False, data_type=str),
            
            # LLM Configuration
            "GEMINI_API_KEY": ConfigValidationRule(required=False, data_type=str),
            "LLM_MODEL": ConfigValidationRule(
                required=True, 
                data_type=str, 
                allowed_values=["gemini-2.5-flash", "gemini-pro", "gpt-4"]
            ),
            "LLM_TEMPERATURE": ConfigValidationRule(
                required=True, 
                data_type=float, 
                min_value=0.0, 
                max_value=2.0
            ),
            "MAX_TOKENS": ConfigValidationRule(
                required=True, 
                data_type=int, 
                min_value=100, 
                max_value=8192
            ),
            
            # Authentication Configuration  
            "ENABLE_AUTH": ConfigValidationRule(
                required=True, 
                data_type=str, 
                allowed_values=["true", "false"]
            ),
            "AUTH_MODE": ConfigValidationRule(
                required=True, 
                data_type=str, 
                allowed_values=["development", "production"]
            ),
            "ADMIN_EMAILS": ConfigValidationRule(required=False, data_type=str),
            "SUPER_ADMIN_EMAILS": ConfigValidationRule(required=False, data_type=str),
            
            # Database Configuration
            "ENABLE_COSMOS_DB": ConfigValidationRule(
                required=True, 
                data_type=str, 
                allowed_values=["true", "false"]
            ),
            
            # Admin Features
            "ADMIN_FEATURES_ENABLED": ConfigValidationRule(
                required=True, 
                data_type=str, 
                allowed_values=["true", "false"]
            ),
            "COST_TRACKING_ENABLED": ConfigValidationRule(
                required=True, 
                data_type=str, 
                allowed_values=["true", "false"]
            ),
            "DEFAULT_MONTHLY_BUDGET": ConfigValidationRule(
                required=True, 
                data_type=float, 
                min_value=1.0, 
                max_value=10000.0
            ),
            
            # Security Configuration
            "RATE_LIMIT_REQUESTS_PER_MINUTE": ConfigValidationRule(
                required=True, 
                data_type=int, 
                min_value=1, 
                max_value=1000
            ),
            "SECURITY_LOG_LEVEL": ConfigValidationRule(
                required=True, 
                data_type=str, 
                allowed_values=["DEBUG", "INFO", "WARNING", "ERROR"]
            ),
        }
    
    def get(self, key: str, default: Any = None, section: Optional[ConfigSection] = None) -> Any:
        """Get configuration value with type conversion"""
        value = self.config_data.get(key, default)
        
        # Apply type conversion based on validation rules
        if key in self.validation_rules:
            rule = self.validation_rules[key]
            if value is not None and rule.data_type != str:
                try:
                    if rule.data_type == bool:
                        value = str(value).lower() in ('true', '1', 'yes', 'on')
                    elif rule.data_type == int:
                        value = int(value)
                    elif rule.data_type == float:
                        value = float(value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not convert {key}={value} to {rule.data_type}: {e}")
                    return default
        
        return value
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = self.get(key, str(default))
        return str(value).lower() in ('true', '1', 'yes', 'on')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        try:
            return int(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float configuration value"""
        try:
            return float(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def validate(self) -> bool:
        """Validate all configuration values"""
        self.errors.clear()
        self.warnings.clear()
        
        for key, rule in self.validation_rules.items():
            value = self.config_data.get(key)
            
            # Check required values
            if rule.required and (value is None or value == ""):
                self.errors.append(f"Required configuration '{key}' is missing")
                continue
            
            if value is None:
                continue
            
            # Check data type
            if rule.data_type != str:
                try:
                    if rule.data_type == bool:
                        converted_value = str(value).lower() in ('true', '1', 'yes', 'on')
                    elif rule.data_type == int:
                        converted_value = int(value)
                    elif rule.data_type == float:
                        converted_value = float(value)
                    else:
                        converted_value = value
                except (ValueError, TypeError):
                    self.errors.append(f"Configuration '{key}' has invalid type. Expected {rule.data_type.__name__}")
                    continue
            else:
                converted_value = str(value)
            
            # Check allowed values
            if rule.allowed_values and str(converted_value) not in rule.allowed_values:
                self.errors.append(f"Configuration '{key}' has invalid value '{converted_value}'. Allowed: {rule.allowed_values}")
            
            # Check numeric ranges
            if rule.data_type in (int, float) and isinstance(converted_value, (int, float)):
                if rule.min_value is not None and converted_value < rule.min_value:
                    self.errors.append(f"Configuration '{key}' value {converted_value} is below minimum {rule.min_value}")
                if rule.max_value is not None and converted_value > rule.max_value:
                    self.errors.append(f"Configuration '{key}' value {converted_value} is above maximum {rule.max_value}")
        
        return len(self.errors) == 0
    
    def get_section_config(self, section: ConfigSection) -> Dict[str, Any]:
        """Get all configuration for a specific section"""
        section_config = {}
        
        # Define section mappings
        section_mappings = {
            ConfigSection.AZURE: ["AZURE_", "COSMOSDB_", "APPLICATIONINSIGHTS_"],
            ConfigSection.LLM: ["GEMINI_", "LLM_", "MAX_TOKENS", "SAFETY_"],
            ConfigSection.AUTH: ["ENABLE_AUTH", "AUTH_", "ADMIN_EMAILS", "SUPER_ADMIN_EMAILS"],
            ConfigSection.DATABASE: ["ENABLE_COSMOS_DB", "COSMOSDB_"],
            ConfigSection.MONITORING: ["APPLICATIONINSIGHTS_", "LOG_LEVEL"],
            ConfigSection.SECURITY: ["RATE_LIMIT_", "SECURITY_"],
            ConfigSection.ADMIN: ["ADMIN_", "COST_"],
            ConfigSection.COST: ["COST_", "BUDGET_", "DEFAULT_"]
        }
        
        prefixes = section_mappings.get(section, [])
        for key, value in self.config_data.items():
            if any(key.startswith(prefix) for prefix in prefixes):
                section_config[key] = value
        
        return section_config
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.get_bool(f"{feature.upper()}_ENABLED", False)
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information"""
        return {
            "environment": self.environment.value,
            "debug_mode": self.get_bool("DEBUG", False),
            "auth_enabled": self.get_bool("ENABLE_AUTH", False),
            "cosmos_enabled": self.get_bool("ENABLE_COSMOS_DB", False),
            "admin_features_enabled": self.get_bool("ADMIN_FEATURES_ENABLED", False),
            "cost_tracking_enabled": self.get_bool("COST_TRACKING_ENABLED", False),
        }
    
    def log_configuration_status(self):
        """Log configuration status for debugging"""
        logger.info(f"🔧 Configuration loaded for environment: {self.environment.value}")
        
        env_info = self.get_environment_info()
        for key, value in env_info.items():
            logger.info(f"  {key}: {value}")
        
        if self.validate():
            logger.info("✅ Configuration validation passed")
        else:
            logger.error("❌ Configuration validation failed:")
            for error in self.errors:
                logger.error(f"  - {error}")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")


# Global configuration instance
def get_config() -> UnifiedConfig:
    """Get the global configuration instance"""
    if not hasattr(get_config, '_instance'):
        # Determine environment from environment variable
        env_name = os.getenv('ENVIRONMENT', 'development').lower()
        try:
            environment = Environment(env_name)
        except ValueError:
            environment = Environment.DEVELOPMENT
            
        get_config._instance = UnifiedConfig(environment)
        get_config._instance.log_configuration_status()
    
    return get_config._instance


# Convenience functions
def get_azure_config() -> Dict[str, Any]:
    """Get Azure-specific configuration"""
    return get_config().get_section_config(ConfigSection.AZURE)


def get_llm_config() -> Dict[str, Any]:
    """Get LLM-specific configuration"""
    return get_config().get_section_config(ConfigSection.LLM)


def get_auth_config() -> Dict[str, Any]:
    """Get authentication-specific configuration"""
    return get_config().get_section_config(ConfigSection.AUTH)


def is_development_mode() -> bool:
    """Check if running in development mode"""
    return get_config().environment == Environment.DEVELOPMENT


def is_production_mode() -> bool:
    """Check if running in production mode"""
    return get_config().environment == Environment.PRODUCTION
