"""
Database-Driven Personality Service
Replaces hardcoded personality configurations with database-driven approach.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import asdict

# Import Azure Cosmos DB
try:
    from azure.cosmos import CosmosClient
    from azure.cosmos.exceptions import CosmosResourceNotFoundError
    cosmos_available = True
except ImportError:
    cosmos_available = False

# Import personality models
try:
    from models.personality_models import PersonalityConfig, PersonalityDomain, SafetyLevel, ResponseStyle
    models_available = True
except ImportError:
    models_available = False

logger = logging.getLogger(__name__)


class DatabasePersonalityService:
    """
    Database-driven personality management service that replaces hardcoded configurations
    """
    
    def __init__(self):
        """Initialize the database personality service"""
        self.client = None
        self.database = None
        self.container = None
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes
        self.last_cache_update = {}
        self.connection_established = False
        
        # Initialize database connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Azure Cosmos DB connection"""
        if not cosmos_available:
            logger.warning("⚠️ Azure Cosmos SDK not available")
            return
        
        try:
            # Load environment variables
            try:
                from dotenv import load_dotenv
                # Get the root directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                root_dir = os.path.dirname(os.path.dirname(current_dir))
                env_path = os.path.join(root_dir, '.env')
                load_dotenv(env_path)
                logger.info(f"📁 Loading environment from: {env_path}")
            except ImportError:
                logger.warning("⚠️ python-dotenv not available")
            
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
            
            if not connection_string:
                logger.warning("⚠️ AZURE_COSMOS_CONNECTION_STRING not found")
                return
            
            self.client = CosmosClient.from_connection_string(connection_string)
            self.database = self.client.get_database_client(database_name)
            self.container = self.database.get_container_client('personalities')
            self.connection_established = True
            
            logger.info(f"✅ Connected to Cosmos DB: {database_name}/personalities")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cosmos DB: {str(e)}")
    
    def _is_cache_valid(self, personality_id: str) -> bool:
        """Check if cached data is still valid"""
        if personality_id not in self.cache:
            return False
        
        last_update = self.last_cache_update.get(personality_id, 0)
        return (datetime.now().timestamp() - last_update) < self.cache_ttl
    
    def _update_cache(self, personality_id: str, config: Dict[str, Any]):
        """Update cache with personality configuration"""
        self.cache[personality_id] = config
        self.last_cache_update[personality_id] = datetime.now().timestamp()
    
    async def get_personality_config(self, personality_id: str) -> Optional[Dict[str, Any]]:
        """
        Get personality configuration by ID from database
        
        Args:
            personality_id: The personality identifier
            
        Returns:
            Dictionary containing personality configuration or None
        """
        # Check cache first
        if self._is_cache_valid(personality_id):
            logger.debug(f"🚀 Cache hit for personality {personality_id}")
            return self.cache[personality_id]
        
        # Try database
        if self.connection_established:
            try:
                # Query the database
                query = "SELECT * FROM c WHERE c.id = @personality_id"
                parameters = [{"name": "@personality_id", "value": personality_id}]
                
                items = list(self.container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                ))
                
                if items:
                    config = items[0]
                    self._update_cache(personality_id, config)
                    logger.debug(f"📊 Database hit for personality {personality_id}")
                    return config
                    
            except Exception as e:
                logger.warning(f"⚠️ Database query failed for {personality_id}: {str(e)}")
        
        # Fallback to hardcoded config if available
        if models_available:
            try:
                from models.personality_models import PERSONALITY_CONFIGS
                if personality_id in PERSONALITY_CONFIGS:
                    config = self._convert_config_to_dict(PERSONALITY_CONFIGS[personality_id])
                    self._update_cache(personality_id, config)
                    logger.debug(f"📋 Fallback to hardcoded config for {personality_id}")
                    return config
            except ImportError:
                pass
        
        logger.warning(f"❌ Personality {personality_id} not found")
        return None
    
    async def get_all_personalities(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all personality configurations, optionally filtered by domain
        
        Args:
            domain: Optional domain filter (spiritual, scientific, philosophical, etc.)
            
        Returns:
            List of personality configurations
        """
        # Try database first
        if self.connection_established:
            try:
                if domain and domain != "all":
                    query = "SELECT * FROM c WHERE c.domain = @domain"
                    parameters = [{"name": "@domain", "value": domain}]
                else:
                    query = "SELECT * FROM c"
                    parameters = []
                
                items = list(self.container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                ))
                
                if items:
                    logger.debug(f"📊 Retrieved {len(items)} personalities from database")
                    return items
                    
            except Exception as e:
                logger.warning(f"⚠️ Database query failed for all personalities: {str(e)}")
        
        # Fallback to hardcoded configs
        if models_available:
            try:
                from models.personality_models import PERSONALITY_CONFIGS, get_personalities_by_domain
                
                if domain and domain != "all":
                    configs = get_personalities_by_domain(domain)
                else:
                    configs = PERSONALITY_CONFIGS
                
                result = []
                for pid, config in configs.items():
                    result.append(self._convert_config_to_dict(config))
                
                logger.debug(f"📋 Fallback to {len(result)} hardcoded personalities")
                return result
                
            except ImportError:
                pass
        
        logger.warning("❌ No personalities found")
        return []
    
    async def get_personality_list(self) -> List[Dict[str, Any]]:
        """
        Get simplified personality list for API responses
        
        Returns:
            List of simplified personality info
        """
        personalities = await self.get_all_personalities()
        
        result = []
        for personality in personalities:
            result.append({
                "id": personality.get("id"),
                "name": personality.get("name"),
                "domain": personality.get("domain"),
                "description": personality.get("description"),
                "active": personality.get("status", "active") == "active"
            })
        
        return result
    
    def _convert_config_to_dict(self, config: 'PersonalityConfig') -> Dict[str, Any]:
        """Convert PersonalityConfig object to dictionary"""
        if not models_available:
            return {}
        
        try:
            result = {
                'id': config.id,
                'name': config.name,
                'display_name': config.display_name,
                'domain': config.domain.value,
                'description': config.description,
                'short_description': config.short_description,
                'safety_level': config.safety_level.value,
                'cultural_context': config.cultural_context.value,
                'max_response_length': config.max_response_length,
                'greeting_style': config.greeting_style,
                'response_style': config.response_style.value,
                'tone_indicators': config.tone_indicators,
                'expertise_areas': config.expertise_areas,
                'foundational_texts': config.foundational_texts,
                'core_teachings': config.core_teachings,
                'personality_traits': config.personality_traits,
                'response_templates': config.response_templates,
                'fallback_responses': config.fallback_responses,
                'status': config.status.value,
                'version': config.version,
                'quality_score': config.quality_score,
                'tags': config.tags,
                'vector_namespace': config.vector_namespace,
                'embedding_model': config.embedding_model,
                'search_boost': config.search_boost,
                'cache_ttl': config.cache_ttl,
                'custom_fields': config.custom_fields,
            }
            
            # Add complex nested objects
            if hasattr(config, 'content_filters'):
                result['content_filters'] = {
                    'religious_sensitivity': config.content_filters.religious_sensitivity,
                    'political_neutrality': config.content_filters.political_neutrality,
                    'avoid_medical_advice': config.content_filters.avoid_medical_advice,
                    'avoid_legal_advice': config.content_filters.avoid_legal_advice,
                    'profanity_filter': config.content_filters.profanity_filter,
                    'hate_speech_filter': config.content_filters.hate_speech_filter,
                    'violence_filter': config.content_filters.violence_filter,
                    'adult_content_filter': config.content_filters.adult_content_filter,
                }
            
            if hasattr(config, 'llm_config'):
                result['llm_config'] = {
                    'system_prompt': config.llm_config.system_prompt,
                    'max_tokens': config.llm_config.max_tokens,
                    'temperature': config.llm_config.temperature,
                    'top_p': config.llm_config.top_p,
                    'frequency_penalty': config.llm_config.frequency_penalty,
                    'presence_penalty': config.llm_config.presence_penalty,
                    'timeout_seconds': config.llm_config.timeout_seconds,
                    'max_retries': config.llm_config.max_retries,
                    'requires_citations': config.llm_config.requires_citations,
                }
            
            if hasattr(config, 'metadata'):
                result['metadata'] = {
                    'birth_year': config.metadata.birth_year,
                    'death_year': config.metadata.death_year,
                    'time_period': config.metadata.time_period,
                    'geographical_origin': config.metadata.geographical_origin,
                    'key_works': config.metadata.key_works,
                    'historical_significance': config.metadata.historical_significance,
                    'famous_quotes': config.metadata.famous_quotes,
                }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error converting config to dict: {str(e)}")
            return {}
    
    def is_database_available(self) -> bool:
        """Check if database connection is available"""
        return self.connection_established
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for debugging"""
        return {
            "cache_size": len(self.cache),
            "cached_personalities": list(self.cache.keys()),
            "database_available": self.connection_established,
            "models_available": models_available,
            "cosmos_available": cosmos_available
        }
