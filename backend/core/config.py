"""
Centralized Configuration Management for Vimarsh
Handles environment-specific configuration with validation and defaults
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Supported environments"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(Enum):
    """Supported log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class AzureConfig:
    """Azure services configuration"""
    subscription_id: str = ""
    resource_group: str = ""
    location: str = "eastus"
    tenant_id: str = ""
    client_id: str = ""
    cosmos_connection_string: str = ""
    cosmos_database_name: str = "vimarsh"
    cosmos_container_name: str = "spiritual_texts"
    key_vault_name: str = ""
    storage_connection_string: str = ""
    
    def validate(self) -> bool:
        """Validate Azure configuration"""
        if not self.cosmos_connection_string or self.cosmos_connection_string == "dev-mode-local-storage":
            logger.warning("Azure Cosmos DB not configured - using local storage")
            return False
        return True


@dataclass
class LLMConfig:
    """LLM service configuration"""
    model: str = "gemini-2.5-flash"
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    safety_settings: str = "BLOCK_MEDIUM_AND_ABOVE"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_dimension: int = 384
    similarity_threshold: float = 0.7
    max_retrieved_chunks: int = 10
    
    def validate(self) -> bool:
        """Validate LLM configuration"""
        if not self.api_key or self.api_key == "dev-mode-placeholder":
            logger.warning("LLM API key not configured - using fallback responses")
            return False
        if not (0.0 <= self.temperature <= 2.0):
            logger.error(f"Invalid temperature: {self.temperature}")
            return False
        if not (1 <= self.max_tokens <= 8192):
            logger.error(f"Invalid max_tokens: {self.max_tokens}")
            return False
        return True


@dataclass
class AuthConfig:
    """Authentication configuration"""
    enabled: bool = False
    tenant_id: str = ""
    client_id: str = ""
    authority: str = ""
    redirect_uri: str = ""
    jwks_uri: str = ""
    
    def validate(self) -> bool:
        """Validate authentication configuration"""
        if not self.enabled:
            logger.warning("Authentication disabled - using development mode")
            return True
        
        if not all([self.tenant_id, self.client_id, self.authority]):
            logger.error("Authentication enabled but missing required configuration")
            return False
        return True


@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""
    log_level: LogLevel = LogLevel.INFO
    debug: bool = False
    app_insights_connection_string: str = ""
    enable_metrics: bool = True
    enable_health_checks: bool = True
    
    def validate(self) -> bool:
        """Validate monitoring configuration"""
        if not self.app_insights_connection_string:
            logger.warning("Application Insights not configured - using console logging")
        return True


@dataclass
class SecurityConfig:
    """Security settings"""
    cors_origins: list = field(default_factory=lambda: ["http://localhost:3000"])
    cors_credentials: bool = True
    https_only: bool = False
    content_security_policy: str = ""
    
    def validate(self) -> bool:
        """Validate security configuration"""
        if not self.cors_origins:
            logger.warning("No CORS origins configured")
            return False
        return True


@dataclass
class ApplicationConfig:
    """Application-specific configuration"""
    default_language: str = "English"
    supported_languages: list = field(default_factory=lambda: ["English", "Hindi"])
    expert_review_enabled: bool = True
    expert_notification_email: str = ""
    max_conversation_history: int = 50
    
    def validate(self) -> bool:
        """Validate application configuration"""
        if self.default_language not in self.supported_languages:
            logger.error(f"Default language {self.default_language} not in supported languages")
            return False
        return True


class ConfigManager:
    """Centralized configuration manager"""
    
    def __init__(self, environment: Optional[Environment] = None):
        """Initialize configuration manager"""
        self.environment = environment or self._detect_environment()
        self.config_loaded = False
        
        # Initialize configuration sections
        self.azure = AzureConfig()
        self.llm = LLMConfig()
        self.auth = AuthConfig()
        self.monitoring = MonitoringConfig()
        self.security = SecurityConfig()
        self.application = ApplicationConfig()
        
        # Load configuration
        self._load_configuration()
    
    def _detect_environment(self) -> Environment:
        """Detect current environment"""
        env_name = os.getenv("ENVIRONMENT", "development").lower()
        try:
            return Environment(env_name)
        except ValueError:
            logger.warning(f"Unknown environment '{env_name}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _load_configuration(self):
        """Load configuration from various sources"""
        try:
            # Load from environment variables (highest priority)
            self._load_from_environment()
            
            # Load from local.settings.json for Azure Functions
            self._load_from_local_settings()
            
            # Load from environment-specific config files
            self._load_from_env_files()
            
            # Validate all configurations
            self._validate_configuration()
            
            self.config_loaded = True
            logger.info(f"Configuration loaded successfully for {self.environment.value} environment")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Azure configuration
        self.azure.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID", self.azure.subscription_id)
        self.azure.resource_group = os.getenv("AZURE_RESOURCE_GROUP", self.azure.resource_group)
        self.azure.location = os.getenv("AZURE_LOCATION", self.azure.location)
        self.azure.tenant_id = os.getenv("AZURE_TENANT_ID", self.azure.tenant_id)
        self.azure.client_id = os.getenv("AZURE_CLIENT_ID", self.azure.client_id)
        self.azure.cosmos_connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING", self.azure.cosmos_connection_string)
        self.azure.cosmos_database_name = os.getenv("AZURE_COSMOS_DATABASE_NAME", self.azure.cosmos_database_name)
        self.azure.cosmos_container_name = os.getenv("AZURE_COSMOS_CONTAINER_NAME", self.azure.cosmos_container_name)
        self.azure.storage_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING", self.azure.storage_connection_string)
        
        # LLM configuration
        self.llm.api_key = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_AI_API_KEY", self.llm.api_key))
        self.llm.model = os.getenv("LLM_MODEL", self.llm.model)
        self.llm.temperature = float(os.getenv("LLM_TEMPERATURE", str(self.llm.temperature)))
        self.llm.max_tokens = int(os.getenv("MAX_TOKENS", str(self.llm.max_tokens)))
        self.llm.safety_settings = os.getenv("SAFETY_SETTINGS", self.llm.safety_settings)
        
        # Authentication configuration
        self.auth.enabled = os.getenv("ENABLE_AUTH", "false").lower() == "true"
        self.auth.tenant_id = os.getenv("ENTRA_TENANT_ID", self.auth.tenant_id)
        self.auth.client_id = os.getenv("ENTRA_CLIENT_ID", self.auth.client_id)
        self.auth.authority = os.getenv("AZURE_AUTHORITY", self.auth.authority)
        self.auth.redirect_uri = os.getenv("AZURE_REDIRECT_URI", self.auth.redirect_uri)
        
        # Monitoring configuration
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        try:
            self.monitoring.log_level = LogLevel(log_level_str)
        except ValueError:
            logger.warning(f"Invalid log level '{log_level_str}', using INFO")
            self.monitoring.log_level = LogLevel.INFO
        
        self.monitoring.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.monitoring.app_insights_connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", self.monitoring.app_insights_connection_string)
        
        # Security configuration
        cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
        if cors_origins and cors_origins[0]:
            self.security.cors_origins = [origin.strip() for origin in cors_origins]
        
        # Application configuration
        self.application.default_language = os.getenv("DEFAULT_LANGUAGE", self.application.default_language)
        supported_langs = os.getenv("SUPPORTED_LANGUAGES", "").split(",")
        if supported_langs and supported_langs[0]:
            self.application.supported_languages = [lang.strip() for lang in supported_langs]
        
        self.application.expert_review_enabled = os.getenv("EXPERT_REVIEW_ENABLED", "true").lower() == "true"
        self.application.expert_notification_email = os.getenv("EXPERT_NOTIFICATION_EMAIL", self.application.expert_notification_email)
    
    def _load_from_local_settings(self):
        """Load configuration from local.settings.json (Azure Functions)"""
        try:
            local_settings_path = Path(__file__).parent / "local.settings.json"
            if local_settings_path.exists():
                with open(local_settings_path, 'r') as f:
                    local_settings = json.load(f)
                    values = local_settings.get("Values", {})
                    
                    # Override environment variables with local settings
                    for key, value in values.items():
                        if key not in os.environ:
                            os.environ[key] = value
                    
                    logger.debug("Loaded configuration from local.settings.json")
        except Exception as e:
            logger.warning(f"Could not load local.settings.json: {e}")
    
    def _load_from_env_files(self):
        """Load configuration from environment-specific files"""
        try:
            env_file_path = Path(__file__).parent.parent / "config" / "environments" / f".env.{self.environment.value}"
            if env_file_path.exists():
                with open(env_file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if key not in os.environ:
                                os.environ[key] = value
                
                logger.debug(f"Loaded configuration from {env_file_path}")
        except Exception as e:
            logger.warning(f"Could not load environment file: {e}")
    
    def _validate_configuration(self):
        """Validate all configuration sections"""
        validation_results = {
            "azure": self.azure.validate(),
            "llm": self.llm.validate(),
            "auth": self.auth.validate(),
            "monitoring": self.monitoring.validate(),
            "security": self.security.validate(),
            "application": self.application.validate()
        }
        
        failed_validations = [section for section, valid in validation_results.items() if not valid]
        if failed_validations:
            logger.warning(f"Configuration validation failed for: {', '.join(failed_validations)}")
        
        # Log configuration summary
        self._log_configuration_summary()
    
    def _log_configuration_summary(self):
        """Log configuration summary"""
        logger.info("=== Configuration Summary ===")
        logger.info(f"Environment: {self.environment.value}")
        logger.info(f"Log Level: {self.monitoring.log_level.value}")
        logger.info(f"Debug Mode: {self.monitoring.debug}")
        logger.info(f"Authentication: {'Enabled' if self.auth.enabled else 'Disabled'}")
        logger.info(f"LLM Model: {self.llm.model}")
        logger.info(f"LLM API: {'Configured' if self.llm.validate() else 'Using Fallback'}")
        logger.info(f"Azure Cosmos: {'Configured' if self.azure.validate() else 'Using Local Storage'}")
        logger.info(f"CORS Origins: {', '.join(self.security.cors_origins)}")
        logger.info("=============================")
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get all environment variables as a dictionary"""
        return {
            # Azure
            "AZURE_SUBSCRIPTION_ID": self.azure.subscription_id,
            "AZURE_RESOURCE_GROUP": self.azure.resource_group,
            "AZURE_LOCATION": self.azure.location,
            "AZURE_TENANT_ID": self.azure.tenant_id,
            "AZURE_CLIENT_ID": self.azure.client_id,
            "AZURE_COSMOS_CONNECTION_STRING": self.azure.cosmos_connection_string,
            "AZURE_COSMOS_DATABASE_NAME": self.azure.cosmos_database_name,
            "AZURE_COSMOS_CONTAINER_NAME": self.azure.cosmos_container_name,
            "AZURE_STORAGE_CONNECTION_STRING": self.azure.storage_connection_string,
            
            # LLM
            "GEMINI_API_KEY": self.llm.api_key,
            "LLM_MODEL": self.llm.model,
            "LLM_TEMPERATURE": str(self.llm.temperature),
            "MAX_TOKENS": str(self.llm.max_tokens),
            "SAFETY_SETTINGS": self.llm.safety_settings,
            
            # Authentication
            "ENABLE_AUTH": str(self.auth.enabled).lower(),
            "ENTRA_TENANT_ID": self.auth.tenant_id,
            "ENTRA_CLIENT_ID": self.auth.client_id,
            "AZURE_AUTHORITY": self.auth.authority,
            "AZURE_REDIRECT_URI": self.auth.redirect_uri,
            
            # Monitoring
            "LOG_LEVEL": self.monitoring.log_level.value,
            "DEBUG": str(self.monitoring.debug).lower(),
            "APPLICATIONINSIGHTS_CONNECTION_STRING": self.monitoring.app_insights_connection_string,
            
            # Security
            "CORS_ORIGINS": ",".join(self.security.cors_origins),
            
            # Application
            "DEFAULT_LANGUAGE": self.application.default_language,
            "SUPPORTED_LANGUAGES": ",".join(self.application.supported_languages),
            "EXPERT_REVIEW_ENABLED": str(self.application.expert_review_enabled).lower(),
            "EXPERT_NOTIFICATION_EMAIL": self.application.expert_notification_email,
        }
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.environment == Environment.TESTING


# Global configuration instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    return config


def reload_config():
    """Reload configuration from all sources"""
    global config
    config = ConfigManager()
    return config
