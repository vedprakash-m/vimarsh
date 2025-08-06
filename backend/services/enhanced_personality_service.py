"""
Personality Service for New Database Architecture
Manages personality configurations from the new 'personalities' container
"""

import os
import logging
from typing import List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PersonalityConfig:
    """Enhanced personality configuration"""
    id: str
    personality_id: str
    display_name: str
    domain: str
    description: str
    system_prompt: str
    cultural_context: str
    foundational_texts: List[str]
    core_teachings: List[str]
    personality_traits: List[str]
    associated_sources: List[str]
    is_active: bool
    created_at: str
    updated_at: str

class PersonalityService:
    """Service for managing personality configurations from new database architecture"""
    
    def __init__(self):
        self.cosmos_db_name = "vimarsh-multi-personality"
        self.container_name = "personalities"  # New container
        self.cosmos_client = None
        self.database = None
        self.container = None
        
        self._initialize_cosmos_db()
    
    def _initialize_cosmos_db(self):
        """Initialize Cosmos DB connection"""
        try:
            # Check if we have Cosmos DB configuration
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if not connection_string or connection_string == 'dev-mode-local-storage':
                logger.info("📝 Using local development mode for personality service")
                return
            
            from azure.cosmos import CosmosClient
            
            # Initialize Cosmos DB client with proper typing
            self.cosmos_client = CosmosClient.from_connection_string(connection_string)
            self.database = self.cosmos_client.get_database_client(self.cosmos_db_name)
            self.container = self.database.get_container_client(self.container_name)
            
            logger.info(f"✅ Connected to personalities container: {self.container_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB for personalities: {e}")
            self.cosmos_client = None
    
    async def get_personality(self, personality_id: str) -> Optional[PersonalityConfig]:
        """Get a specific personality configuration"""
        try:
            if not self.container:
                logger.warning("📝 Cosmos DB not available, using fallback data")
                return self._get_fallback_personality(personality_id)
            
            # Query for the specific personality
            query = "SELECT * FROM c WHERE c.personality_id = @personality_id"
            parameters = [{"name": "@personality_id", "value": personality_id}]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=False
            ))
            
            if items:
                item = items[0]
                return PersonalityConfig(
                    id=item['id'],
                    personality_id=item['personality_id'],
                    display_name=item['display_name'],
                    domain=item['domain'],
                    description=item['description'],
                    system_prompt=item['system_prompt'],
                    cultural_context=item['cultural_context'],
                    foundational_texts=item.get('foundational_texts', []),
                    core_teachings=item.get('core_teachings', []),
                    personality_traits=item.get('personality_traits', []),
                    associated_sources=item.get('associated_sources', []),
                    is_active=item.get('is_active', True),
                    created_at=item.get('created_at', ''),
                    updated_at=item.get('updated_at', '')
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get personality {personality_id}: {e}")
            return self._get_fallback_personality(personality_id)
    
    async def get_all_personalities(self) -> List[PersonalityConfig]:
        """Get all personality configurations"""
        try:
            if not self.container:
                logger.warning("📝 Cosmos DB not available, using fallback data")
                return self._get_fallback_personalities()
            
            # Query all personalities
            query = "SELECT * FROM c ORDER BY c.display_name"
            
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            personalities: List[PersonalityConfig] = []
            for item in items:
                personalities.append(PersonalityConfig(
                    id=item['id'],
                    personality_id=item['personality_id'],
                    display_name=item['display_name'],
                    domain=item['domain'],
                    description=item['description'],
                    system_prompt=item['system_prompt'],
                    cultural_context=item['cultural_context'],
                    foundational_texts=item.get('foundational_texts', []),
                    core_teachings=item.get('core_teachings', []),
                    personality_traits=item.get('personality_traits', []),
                    associated_sources=item.get('associated_sources', []),
                    is_active=item.get('is_active', True),
                    created_at=item.get('created_at', ''),
                    updated_at=item.get('updated_at', '')
                ))
            
            logger.info(f"✅ Retrieved {len(personalities)} personalities")
            return personalities
            
        except Exception as e:
            logger.error(f"❌ Failed to get all personalities: {e}")
            return self._get_fallback_personalities()
    
    async def get_active_personalities(self) -> List[PersonalityConfig]:
        """Get only active personality configurations"""
        try:
            all_personalities = await self.get_all_personalities()
            return [p for p in all_personalities if p.is_active]
            
        except Exception as e:
            logger.error(f"❌ Failed to get active personalities: {e}")
            return []
    
    async def search_personalities(self, query: Optional[str] = None, domain: Optional[str] = None) -> List[PersonalityConfig]:
        """Search personalities with optional filters"""
        try:
            if not self.container:
                return self._get_fallback_personalities()
            
            # Build query with filters
            sql_query = "SELECT * FROM c WHERE 1=1"
            parameters = []
            
            if query:
                sql_query += " AND (CONTAINS(c.personality_id, @query) OR CONTAINS(c.display_name, @query) OR CONTAINS(c.description, @query))"
                parameters.append({"name": "@query", "value": query})
            
            if domain:
                sql_query += " AND c.domain = @domain"
                parameters.append({"name": "@domain", "value": domain})
            
            sql_query += " ORDER BY c.display_name"
            
            items = list(self.container.query_items(
                query=sql_query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            personalities: List[PersonalityConfig] = []
            for item in items:
                personalities.append(PersonalityConfig(
                    id=item['id'],
                    personality_id=item['personality_id'],
                    display_name=item['display_name'],
                    domain=item['domain'],
                    description=item['description'],
                    system_prompt=item['system_prompt'],
                    cultural_context=item['cultural_context'],
                    foundational_texts=item.get('foundational_texts', []),
                    core_teachings=item.get('core_teachings', []),
                    personality_traits=item.get('personality_traits', []),
                    associated_sources=item.get('associated_sources', []),
                    is_active=item.get('is_active', True),
                    created_at=item.get('created_at', ''),
                    updated_at=item.get('updated_at', '')
                ))
            
            return personalities
            
        except Exception as e:
            logger.error(f"❌ Failed to search personalities: {e}")
            return []
    
    def _get_fallback_personality(self, personality_id: str) -> Optional[PersonalityConfig]:
        """Fallback personality data for development"""
        fallback_personalities = {
            "krishna": PersonalityConfig(
                id="personality_krishna",
                personality_id="krishna",
                display_name="Lord Krishna",
                domain="spiritual",
                description="Divine guide from Hindu traditions, emphasizing dharma, karma yoga, and devotion",
                system_prompt="I am Krishna, the divine charioteer from the Bhagavad Gita. I guide souls toward their highest dharma through wisdom, compassion, and divine love.",
                cultural_context="hindu",
                foundational_texts=["bhagavad_gita", "srimad_bhagavatam", "mahabharata"],
                core_teachings=["dharma", "karma_yoga", "bhakti", "detachment", "divine_love"],
                personality_traits=["wise", "compassionate", "playful", "divine", "protective"],
                associated_sources=["Bhagavad Gita"],
                is_active=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            "buddha": PersonalityConfig(
                id="personality_buddha",
                personality_id="Buddha",
                display_name="Buddha",
                domain="spiritual",
                description="Enlightened teacher emphasizing mindfulness, compassion, and liberation from suffering",
                system_prompt="I am Buddha, the awakened one. I teach the path to liberation from suffering through mindfulness, compassion, and understanding the nature of reality.",
                cultural_context="buddhist",
                foundational_texts=["dhammapada", "lotus_sutra"],
                core_teachings=["four_noble_truths", "eightfold_path", "mindfulness", "compassion"],
                personality_traits=["peaceful", "wise", "compassionate", "mindful"],
                associated_sources=["Buddhist Teachings"],
                is_active=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        }
        
        return fallback_personalities.get(personality_id.lower())
    
    def _get_fallback_personalities(self) -> List[PersonalityConfig]:
        """Fallback personality list for development"""
        personalities: List[PersonalityConfig] = []
        krishna = self._get_fallback_personality("krishna")
        buddha = self._get_fallback_personality("buddha")
        
        if krishna:
            personalities.append(krishna)
        if buddha:
            personalities.append(buddha)
            
        return personalities

# Global personality service instance
personality_service = PersonalityService()
