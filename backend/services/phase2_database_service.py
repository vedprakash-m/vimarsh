#!/usr/bin/env python3
"""
Phase 2 Database Integration Service
===================================

Production-ready database service that integrates Phase 1 and Phase 2 services
with Cosmos DB containers for conversation memory, wisdom journal, and personalization.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict
import uuid

# Import Azure Cosmos DB
try:
    from azure.cosmos import CosmosClient, PartitionKey
    from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosResourceExistsError
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False
    logging.warning("Azure Cosmos SDK not available - using local storage fallback")

# Import conversation models
try:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    from models.conversation_models import (
        ConversationSession, ConversationMessage, WisdomJournalEntry, 
        UserPreferences, ConversationStatus, MessageType, JournalEntryType,
        create_conversation_session, create_conversation_message, 
        create_wisdom_journal_entry, create_user_preferences
    )
    MODELS_AVAILABLE = True
except ImportError as e:
    logging.error(f"Conversation models not available: {e}")
    MODELS_AVAILABLE = False

logger = logging.getLogger(__name__)

class Phase2DatabaseService:
    """Enhanced database service for Phase 2 memory and personalization features"""
    
    def __init__(self):
        """Initialize the Phase 2 database service"""
        self.cosmos_client = None
        self.database = None
        self.containers = {}
        
        # Container mappings for Phase 2
        self.container_names = {
            'conversation_sessions': 'conversation-sessions',
            'conversation_messages': 'conversation-messages', 
            'wisdom_journal': 'wisdom-journal',
            'user_preferences': 'user-preferences',
            'conversation_analytics': 'conversation-analytics',
            'personalization_insights': 'personalization-insights'
        }
        
        # Local storage fallback
        self.local_storage_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'phase2-storage'
        )
        
        # Initialize connection
        self.is_cosmos_enabled = self._init_cosmos_connection()
        
        if not self.is_cosmos_enabled:
            self._init_local_storage()
            logger.warning("🔶 Using local storage fallback for Phase 2 services")
        else:
            logger.info("✅ Phase 2 database service connected to Cosmos DB")
    
    def _init_cosmos_connection(self) -> bool:
        """Initialize Cosmos DB connection"""
        if not COSMOS_AVAILABLE:
            return False
        
        try:
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if not connection_string or connection_string == 'dev-mode-local-storage':
                return False
            
            self.cosmos_client = CosmosClient.from_connection_string(connection_string)
            database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
            self.database = self.cosmos_client.get_database_client(database_name)
            
            # Initialize container clients
            for key, container_name in self.container_names.items():
                try:
                    self.containers[key] = self.database.get_container_client(container_name)
                    # Test container access
                    self.containers[key].read()
                    logger.info(f"✅ Connected to container: {container_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to connect to container {container_name}: {e}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB connection: {e}")
            return False
    
    def _init_local_storage(self):
        """Initialize local storage for development"""
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        # Create local storage files
        for container_key in self.container_names.keys():
            file_path = os.path.join(self.local_storage_path, f"{container_key}.json")
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
                logger.info(f"📁 Initialized local storage: {container_key}.json")
    
    # ============================================================================
    # CONVERSATION MEMORY METHODS
    # ============================================================================
    
    async def store_conversation_session(self, session: ConversationSession) -> bool:
        """Store a conversation session in the database"""
        try:
            session_data = session.to_dict()
            
            if self.is_cosmos_enabled:
                container = self.containers['conversation_sessions']
                container.create_item(body=session_data)
                logger.info(f"💾 Stored conversation session: {session.id}")
            else:
                # Local storage fallback
                self._store_local_item('conversation_sessions', session_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store conversation session {session.id}: {e}")
            return False
    
    async def get_conversation_session(self, session_id: str, user_id: str) -> Optional[ConversationSession]:
        """Retrieve a conversation session"""
        try:
            if self.is_cosmos_enabled:
                container = self.containers['conversation_sessions']
                partition_key = f"{user_id}|{session_id.split('_')[2] if '_' in session_id else 'unknown'}"
                
                item = container.read_item(item=session_id, partition_key=partition_key)
                return ConversationSession.from_dict(item)
            else:
                # Local storage fallback
                items = self._get_local_items('conversation_sessions')
                for item in items:
                    if item.get('id') == session_id and item.get('user_id') == user_id:
                        return ConversationSession.from_dict(item)
                return None
                
        except CosmosResourceNotFoundError:
            logger.warning(f"🔍 Conversation session not found: {session_id}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to retrieve conversation session {session_id}: {e}")
            return None
    
    async def store_conversation_message(self, message: ConversationMessage) -> bool:
        """Store a conversation message"""
        try:
            message_data = message.to_dict()
            
            if self.is_cosmos_enabled:
                container = self.containers['conversation_messages']
                container.create_item(body=message_data)
                logger.info(f"💬 Stored message: {message.id}")
            else:
                self._store_local_item('conversation_messages', message_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store message {message.id}: {e}")
            return False
    
    async def get_recent_messages(
        self, 
        user_id: str, 
        personality_id: str, 
        limit: int = 10
    ) -> List[ConversationMessage]:
        """Get recent messages for a user-personality combination"""
        try:
            if self.is_cosmos_enabled:
                container = self.containers['conversation_messages']
                partition_key = f"{user_id}|{personality_id}"
                
                query = f"""
                SELECT * FROM c 
                WHERE c.partition_key = @partition_key 
                ORDER BY c.timestamp DESC 
                OFFSET 0 LIMIT {limit}
                """
                
                items = list(container.query_items(
                    query=query,
                    parameters=[{"name": "@partition_key", "value": partition_key}]
                ))
                
                return [ConversationMessage.from_dict(item) for item in items]
            else:
                # Local storage fallback
                items = self._get_local_items('conversation_messages')
                filtered = [
                    item for item in items 
                    if (item.get('user_id') == user_id and 
                        item.get('personality_id') == personality_id)
                ]
                # Sort by timestamp and limit
                filtered.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                return [ConversationMessage.from_dict(item) for item in filtered[:limit]]
                
        except Exception as e:
            logger.error(f"❌ Failed to get recent messages for {user_id}/{personality_id}: {e}")
            return []
    
    # ============================================================================
    # WISDOM JOURNAL METHODS
    # ============================================================================
    
    async def store_wisdom_journal_entry(self, entry: WisdomJournalEntry) -> bool:
        """Store a wisdom journal entry"""
        try:
            entry_data = entry.to_dict()
            
            if self.is_cosmos_enabled:
                container = self.containers['wisdom_journal']
                container.create_item(body=entry_data)
                logger.info(f"📔 Stored journal entry: {entry.id}")
            else:
                self._store_local_item('wisdom_journal', entry_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store journal entry {entry.id}: {e}")
            return False
    
    async def get_user_journal_entries(
        self, 
        user_id: str, 
        entry_type: Optional[JournalEntryType] = None,
        limit: int = 50
    ) -> List[WisdomJournalEntry]:
        """Get journal entries for a user"""
        try:
            if self.is_cosmos_enabled:
                container = self.containers['wisdom_journal']
                
                # Build query based on filters
                query = "SELECT * FROM c WHERE c.user_id = @user_id"
                parameters = [{"name": "@user_id", "value": user_id}]
                
                if entry_type:
                    query += " AND c.entry_type = @entry_type"
                    parameters.append({"name": "@entry_type", "value": entry_type.value})
                
                query += f" ORDER BY c.created_at DESC OFFSET 0 LIMIT {limit}"
                
                items = list(container.query_items(query=query, parameters=parameters))
                return [WisdomJournalEntry.from_dict(item) for item in items]
            else:
                # Local storage fallback
                items = self._get_local_items('wisdom_journal')
                filtered = [item for item in items if item.get('user_id') == user_id]
                
                if entry_type:
                    filtered = [item for item in filtered if item.get('entry_type') == entry_type.value]
                
                # Sort and limit
                filtered.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                return [WisdomJournalEntry.from_dict(item) for item in filtered[:limit]]
                
        except Exception as e:
            logger.error(f"❌ Failed to get journal entries for {user_id}: {e}")
            return []
    
    async def search_journal_entries(
        self, 
        user_id: str, 
        search_terms: List[str],
        limit: int = 20
    ) -> List[Tuple[WisdomJournalEntry, float]]:
        """Search journal entries with basic text matching"""
        try:
            entries = await self.get_user_journal_entries(user_id, limit=100)  # Get more for searching
            
            results = []
            for entry in entries:
                # Simple text matching score
                content_lower = entry.content.lower()
                title_lower = entry.title.lower()
                
                score = 0.0
                for term in search_terms:
                    term_lower = term.lower()
                    # Weight title matches higher
                    if term_lower in title_lower:
                        score += 2.0
                    if term_lower in content_lower:
                        score += 1.0
                    # Tag matches
                    if any(term_lower in tag.lower() for tag in entry.tags):
                        score += 1.5
                
                if score > 0:
                    # Normalize score
                    normalized_score = min(score / (len(search_terms) * 2), 1.0)
                    results.append((entry, normalized_score))
            
            # Sort by score and limit
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to search journal entries for {user_id}: {e}")
            return []
    
    # ============================================================================
    # USER PREFERENCES METHODS
    # ============================================================================
    
    async def store_user_preferences(self, preferences: UserPreferences) -> bool:
        """Store user preferences"""
        try:
            prefs_data = preferences.to_dict()
            
            if self.is_cosmos_enabled:
                container = self.containers['user_preferences']
                # Use upsert to update existing preferences
                container.upsert_item(body=prefs_data)
                logger.info(f"⚙️ Stored user preferences: {preferences.user_id}")
            else:
                self._upsert_local_item('user_preferences', prefs_data, 'user_id')
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store user preferences {preferences.user_id}: {e}")
            return False
    
    async def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences"""
        try:
            if self.is_cosmos_enabled:
                container = self.containers['user_preferences']
                item = container.read_item(item=user_id, partition_key=user_id)
                return UserPreferences.from_dict(item)
            else:
                items = self._get_local_items('user_preferences')
                for item in items:
                    if item.get('user_id') == user_id:
                        return UserPreferences.from_dict(item)
                return None
                
        except CosmosResourceNotFoundError:
            # Create default preferences
            default_prefs = create_user_preferences(user_id)
            await self.store_user_preferences(default_prefs)
            return default_prefs
        except Exception as e:
            logger.error(f"❌ Failed to get user preferences {user_id}: {e}")
            return None
    
    # ============================================================================
    # ANALYTICS METHODS
    # ============================================================================
    
    async def store_conversation_analytics(self, analytics_data: Dict[str, Any]) -> bool:
        """Store conversation analytics data"""
        try:
            # Add metadata
            analytics_data['id'] = str(uuid.uuid4())
            analytics_data['created_at'] = datetime.now().isoformat()
            analytics_data['document_type'] = 'conversation_analytics'
            
            if self.is_cosmos_enabled:
                container = self.containers['conversation_analytics']
                container.create_item(body=analytics_data)
                logger.info(f"📊 Stored conversation analytics for user: {analytics_data.get('user_id')}")
            else:
                self._store_local_item('conversation_analytics', analytics_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store conversation analytics: {e}")
            return False
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _store_local_item(self, container_key: str, item_data: Dict[str, Any]):
        """Store item in local JSON file"""
        file_path = os.path.join(self.local_storage_path, f"{container_key}.json")
        
        # Read existing data
        try:
            with open(file_path, 'r') as f:
                items = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            items = []
        
        # Add new item
        items.append(item_data)
        
        # Write back
        with open(file_path, 'w') as f:
            json.dump(items, f, indent=2, default=str)
    
    def _upsert_local_item(self, container_key: str, item_data: Dict[str, Any], key_field: str):
        """Upsert item in local JSON file"""
        file_path = os.path.join(self.local_storage_path, f"{container_key}.json")
        
        # Read existing data
        try:
            with open(file_path, 'r') as f:
                items = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            items = []
        
        # Find and update existing item or add new one
        key_value = item_data.get(key_field)
        found = False
        
        for i, existing_item in enumerate(items):
            if existing_item.get(key_field) == key_value:
                items[i] = item_data
                found = True
                break
        
        if not found:
            items.append(item_data)
        
        # Write back
        with open(file_path, 'w') as f:
            json.dump(items, f, indent=2, default=str)
    
    def _get_local_items(self, container_key: str) -> List[Dict[str, Any]]:
        """Get all items from local JSON file"""
        file_path = os.path.join(self.local_storage_path, f"{container_key}.json")
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of database connections"""
        health_status = {
            'cosmos_enabled': self.is_cosmos_enabled,
            'containers': {},
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }
        
        if self.is_cosmos_enabled:
            for key, container in self.containers.items():
                try:
                    container.read()
                    health_status['containers'][key] = 'connected'
                except Exception as e:
                    health_status['containers'][key] = f'error: {str(e)}'
                    health_status['status'] = 'degraded'
        else:
            # Check local storage
            for container_key in self.container_names.keys():
                file_path = os.path.join(self.local_storage_path, f"{container_key}.json")
                if os.path.exists(file_path):
                    health_status['containers'][container_key] = 'local_storage'
                else:
                    health_status['containers'][container_key] = 'missing'
                    health_status['status'] = 'degraded'
        
        return health_status
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            'storage_type': 'cosmos_db' if self.is_cosmos_enabled else 'local_json',
            'containers': len(self.container_names),
            'timestamp': datetime.now().isoformat()
        }
        
        if not self.is_cosmos_enabled:
            # Count items in local storage
            for container_key in self.container_names.keys():
                items = self._get_local_items(container_key)
                stats[f'{container_key}_count'] = len(items)
        
        return stats

# Global instance
phase2_db_service = Phase2DatabaseService()

# Test function
async def test_phase2_database():
    """Test Phase 2 database functionality"""
    print("🧪 Testing Phase 2 Database Service")
    print("=" * 50)
    
    # Health check
    health = await phase2_db_service.health_check()
    print(f"📊 Health Status: {health['status']}")
    print(f"🔗 Cosmos Enabled: {health['cosmos_enabled']}")
    
    # Test user preferences
    test_user_id = "test_user_123"
    prefs = await phase2_db_service.get_user_preferences(test_user_id)
    print(f"⚙️ Retrieved preferences for {test_user_id}: {prefs.conversation_style if prefs else 'None'}")
    
    # Test conversation session
    test_session = create_conversation_session(test_user_id, "krishna", "Test Conversation")
    stored = await phase2_db_service.store_conversation_session(test_session)
    print(f"💾 Stored session: {stored}")
    
    # Test wisdom journal
    test_entry = create_wisdom_journal_entry(
        test_user_id, 
        JournalEntryType.INSIGHT,
        "Test Insight",
        "Today I learned about the importance of dharma in daily life.",
        personality_id="krishna"
    )
    stored_entry = await phase2_db_service.store_wisdom_journal_entry(test_entry)
    print(f"📔 Stored journal entry: {stored_entry}")
    
    # Get stats
    stats = await phase2_db_service.get_stats()
    print(f"📈 Database stats: {stats}")
    
    print("🎉 Phase 2 Database Service test completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_phase2_database())
