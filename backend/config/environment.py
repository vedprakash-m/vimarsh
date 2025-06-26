"""
Environment Configuration Manager for Backend
This module provides type-safe access to environment variables with validation.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class AuthConfig:
    tenant_id: str
    client_id: str
    issuer: str
    jwks_uri: str

@dataclass
class AzureConfig:
    subscription_id: str
    resource_group: str
    location: str

@dataclass
class DatabaseConfig:
    connection_string: str
    database_name: str
    container_name: str

@dataclass
class CostManagementConfig:
    monthly_budget_usd: int
    cost_alert_threshold: float
    token_rate_limit_per_user: int

@dataclass
class CacheConfig:
    ttl_seconds: int
    max_size: int

@dataclass
class SecurityConfig:
    enable_cors: bool
    allowed_origins: list
    enable_rate_limiting: bool
    rate_limit_per_minute: int

@dataclass
class FeatureFlags:
    voice_interface: bool
    expert_review: bool
    analytics: bool
    pwa_features: bool

@dataclass
class DebugConfig:
    debug_logging: bool
    show_detailed_errors: bool
    mock_llm_responses: bool
    use_local_vector_storage: bool

class EnvironmentConfigManager:
    """Manages environment-specific configuration with validation."""
    
    def __init__(self):
        self.environment = self._get_environment()
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self._setup_logging()
        self._config = self._load_configuration()
        self._validate_configuration()
        
    def _get_environment(self) -> Environment:
        """Get current environment from environment variables."""
        env_str = os.getenv("ENVIRONMENT", "development").lower()
        try:
            return Environment(env_str)
        except ValueError:
            logging.warning(f"Invalid environment '{env_str}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _setup_logging(self):
        """Configure logging based on environment."""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        if self.environment == Environment.DEVELOPMENT:
            logging.basicConfig(level=logging.DEBUG, format=log_format)
        else:
            logging.basicConfig(level=getattr(logging, self.log_level), format=log_format)
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load all configuration from environment variables."""
        return {
            "auth": AuthConfig(
                tenant_id=os.getenv("AZURE_AD_TENANT_ID", ""),
                client_id=os.getenv("AZURE_AD_CLIENT_ID", ""),
                issuer=os.getenv("JWT_ISSUER", ""),
                jwks_uri=os.getenv("JWT_JWKS_URI", "")
            ),
            "azure": AzureConfig(
                subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID", ""),
                resource_group=os.getenv("AZURE_RESOURCE_GROUP", "vimarsh-rg"),
                location=os.getenv("AZURE_LOCATION", "eastus")
            ),
            "database": DatabaseConfig(
                connection_string=os.getenv("COSMOS_CONNECTION_STRING", ""),
                database_name=os.getenv("COSMOS_DATABASE_NAME", "SpiritualGuidance"),
                container_name=os.getenv("COSMOS_CONTAINER_NAME", "Documents")
            ),
            "cost_management": CostManagementConfig(
                monthly_budget_usd=int(os.getenv("MONTHLY_BUDGET_USD", "50")),
                cost_alert_threshold=float(os.getenv("COST_ALERT_THRESHOLD", "0.8")),
                token_rate_limit_per_user=int(os.getenv("TOKEN_RATE_LIMIT_PER_USER", "1000"))
            ),
            "cache": CacheConfig(
                ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600")),
                max_size=int(os.getenv("CACHE_MAX_SIZE", "1000"))
            ),
            "security": SecurityConfig(
                enable_cors=os.getenv("ENABLE_CORS", "true").lower() == "true",
                allowed_origins=os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [],
                enable_rate_limiting=os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true",
                rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
            ),
            "features": FeatureFlags(
                voice_interface=os.getenv("ENABLE_VOICE_INTERFACE", "true").lower() == "true",
                expert_review=os.getenv("ENABLE_EXPERT_REVIEW", "true").lower() == "true",
                analytics=os.getenv("ENABLE_ANALYTICS", "true").lower() == "true",
                pwa_features=os.getenv("ENABLE_PWA_FEATURES", "true").lower() == "true"
            ),
            "debug": DebugConfig(
                debug_logging=os.getenv("ENABLE_DEBUG_LOGGING", "false").lower() == "true",
                show_detailed_errors=os.getenv("SHOW_DETAILED_ERRORS", "false").lower() == "true",
                mock_llm_responses=os.getenv("MOCK_LLM_RESPONSES", "false").lower() == "true",
                use_local_vector_storage=os.getenv("USE_LOCAL_VECTOR_STORAGE", "false").lower() == "true"
            ),
            # Additional application settings
            "app": {
                "max_query_length": int(os.getenv("MAX_QUERY_LENGTH", "1000")),
                "response_timeout_seconds": int(os.getenv("RESPONSE_TIMEOUT_SECONDS", "30")),
                "expert_review_email": os.getenv("EXPERT_REVIEW_EMAIL", ""),
                "default_language": os.getenv("DEFAULT_LANGUAGE", "en"),
                "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
                "app_insights_connection_string": os.getenv("APPINSIGHTS_CONNECTION_STRING", "")
            }
        }
    
    def _validate_configuration(self):
        """Validate configuration based on environment."""
        logger = logging.getLogger(__name__)
        
        # Always required
        required_keys = [
            ("app", "max_query_length"),
            ("cost_management", "monthly_budget_usd"),
            ("azure", "resource_group")
        ]
        
        # Production requirements
        if self.environment == Environment.PRODUCTION:
            required_keys.extend([
                ("auth", "tenant_id"),
                ("auth", "client_id"),
                ("database", "connection_string"),
                ("app", "gemini_api_key")
            ])
        
        # Validate required configuration
        missing_config = []
        for category, key in required_keys:
            value = getattr(self._config[category], key) if hasattr(self._config[category], key) else self._config[category].get(key)
            if not value:
                missing_config.append(f"{category}.{key}")
        
        if missing_config:
            error_msg = f"Missing required configuration: {', '.join(missing_config)}"
            logger.error(error_msg)
            if self.environment == Environment.PRODUCTION:
                raise ValueError(error_msg)
            else:
                logger.warning("Development environment - some production configs may be missing")
        
        # Validate budget settings
        budget = self._config["cost_management"].monthly_budget_usd
        if budget > 200:
            logger.warning(f"Monthly budget ${budget} exceeds recommended beta testing limit")
        
        # Validate URLs
        if self._config["auth"].issuer and not self._config["auth"].issuer.startswith("https://"):
            logger.warning("JWT issuer should use HTTPS")
        
        logger.info(f"✅ Configuration validated for environment: {self.environment.value}")
    
    # Public getters
    def get_environment(self) -> Environment:
        return self.environment
    
    def get_auth_config(self) -> AuthConfig:
        return self._config["auth"]
    
    def get_azure_config(self) -> AzureConfig:
        return self._config["azure"]
    
    def get_database_config(self) -> DatabaseConfig:
        return self._config["database"]
    
    def get_cost_management_config(self) -> CostManagementConfig:
        return self._config["cost_management"]
    
    def get_cache_config(self) -> CacheConfig:
        return self._config["cache"]
    
    def get_security_config(self) -> SecurityConfig:
        return self._config["security"]
    
    def get_feature_flags(self) -> FeatureFlags:
        return self._config["features"]
    
    def get_debug_config(self) -> DebugConfig:
        return self._config["debug"]
    
    def get_app_setting(self, key: str, default: Any = None) -> Any:
        return self._config["app"].get(key, default)
    
    # Utility methods
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT
    
    def is_staging(self) -> bool:
        return self.environment == Environment.STAGING
    
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION
    
    def is_feature_enabled(self, feature: str) -> bool:
        return getattr(self._config["features"], feature, False)
    
    def get_log_level(self) -> str:
        if self._config["debug"].debug_logging:
            return "DEBUG"
        return "DEBUG" if self.is_development() else "INFO"
    
    def get_cors_origins(self) -> list:
        """Get CORS allowed origins based on environment."""
        if self.is_development():
            return ["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"]
        elif self.is_staging():
            return ["https://vimarsh-staging-web.azurestaticapps.net"]
        else:  # production
            return ["https://vimarsh-web.azurestaticapps.net", "https://vimarsh.ved.ai"]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary for debugging."""
        return {
            "environment": self.environment.value,
            "auth_configured": bool(self._config["auth"].tenant_id and self._config["auth"].client_id),
            "database_configured": bool(self._config["database"].connection_string),
            "features_enabled": [
                feature for feature, enabled in self._config["features"].__dict__.items() if enabled
            ],
            "debug_mode": self._config["debug"].debug_logging,
            "monthly_budget": self._config["cost_management"].monthly_budget_usd,
            "resource_group": self._config["azure"].resource_group
        }

# Create singleton instance
config_manager = EnvironmentConfigManager()

# Export commonly used configurations
AUTH_CONFIG = config_manager.get_auth_config()
AZURE_CONFIG = config_manager.get_azure_config()
DATABASE_CONFIG = config_manager.get_database_config()
COST_CONFIG = config_manager.get_cost_management_config()
CACHE_CONFIG = config_manager.get_cache_config()
SECURITY_CONFIG = config_manager.get_security_config()
FEATURES = config_manager.get_feature_flags()
DEBUG_CONFIG = config_manager.get_debug_config()

# Export utility functions
def get_app_setting(key: str, default: Any = None) -> Any:
    return config_manager.get_app_setting(key, default)

def is_feature_enabled(feature: str) -> bool:
    return config_manager.is_feature_enabled(feature)

def get_environment() -> Environment:
    return config_manager.get_environment()

def is_development() -> bool:
    return config_manager.is_development()

def is_production() -> bool:
    return config_manager.is_production()

def is_staging() -> bool:
    return config_manager.is_staging()

# Development utilities
if config_manager.is_development() and config_manager.get_debug_config().debug_logging:
    logger = logging.getLogger(__name__)
    logger.debug("🔧 Environment Configuration: %s", config_manager.get_summary())
