"""
User Profile Service - Cosmos DB implementation for user persistence and analytics.
Implements the 2-container optimized design for efficient user management.
"""

import json
import os
import logging
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

# Azure Cosmos DB imports
try:
    from azure.cosmos import CosmosClient, exceptions
    from azure.identity import DefaultAzureCredential
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False
    logging.warning("Azure Cosmos DB SDK not available - using local storage")

# Import authentication models
from auth.models import AuthenticatedUser

logger = logging.getLogger(__name__)


@dataclass
class UserDocument:
    """Consolidated user profile with embedded aggregated data - Container 1"""
    # Cosmos DB required fields
    id: str                           # User ID (UUID)
    partition_key: str               # Same as id for single-user queries
    
    # Authentication & Identity (required fields first)  
    auth_id: str                     # Microsoft Entra ID (oid field) - UNIQUE
    email: str                       # Primary email address - UNIQUE
    name: str                        # Display name from Entra ID
    
    # Optional fields with defaults
    document_type: str = "user_profile"
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    auth_provider: str = "microsoft"
    tenant_id: Optional[str] = None
    
    # Profile Information
    profile_picture_url: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    preferred_language: str = "en"
    timezone: Optional[str] = None
    
    # User Preferences (Generic & Flexible)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Account Status & Metadata
    account_status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    # Aggregated Usage Statistics (Live Updated)
    usage_stats: Dict[str, Any] = field(default_factory=lambda: {
        "total_sessions": 0,
        "total_queries": 0,
        "total_tokens": 0,
        "total_cost_usd": 0.0,
        "avg_session_duration": 0,
        "favorite_personalities": [],
        "common_topics": [],
        "monthly_usage": {}
    })
    
    # Recent Activity (Last 10 interactions for quick access)
    recent_activity: List[Dict[str, Any]] = field(default_factory=list)
    
    # User Bookmarks (Embedded for quick access)
    bookmarks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Risk & Admin
    risk_score: float = 0.0
    abuse_flags: List[str] = field(default_factory=list)
    is_admin: bool = False
    admin_notes: Optional[str] = None
    
    # Privacy & Compliance
    data_retention_consent: bool = True
    analytics_consent: bool = True
    last_consent_update: Optional[datetime] = None

    def __post_init__(self):
        """Ensure partition_key matches id and timestamps are set"""
        if not self.partition_key:
            self.partition_key = self.id
        if self.last_consent_update is None:
            self.last_consent_update = datetime.utcnow()


@dataclass
class UserActivityDocument:
    """All user activity - sessions, interactions, detailed analytics - Container 2"""
    # Cosmos DB required fields
    id: str                          # Activity ID (UUID)
    partition_key: str              # user_id for efficient querying
    user_id: str                    # Reference to user
    document_type: str              # "session", "interaction", "analytics_snapshot"
    
    # Common fields with defaults
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Session Document (when document_type = "session")
    session_data: Optional[Dict[str, Any]] = None
    
    # Interaction Document (when document_type = "interaction")
    interaction_data: Optional[Dict[str, Any]] = None
    
    # Analytics Snapshot (when document_type = "analytics_snapshot")
    analytics_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Ensure partition_key is set to user_id"""
        if not self.partition_key:
            self.partition_key = self.user_id


class DocumentType(Enum):
    """Document types for activity container"""
    SESSION = "session"
    INTERACTION = "interaction"
    ANALYTICS_SNAPSHOT = "analytics_snapshot"


class UserProfileService:
    """
    User Profile Service implementing 2-container Cosmos DB design.
    
    Container 1: users - User profiles with embedded recent activity and bookmarks
    Container 2: user_activity - All detailed activity history and analytics
    """
    
    def __init__(self):
        """Initialize service with Cosmos DB connection or local fallback"""
        self.cosmos_client = None
        self.database = None
        self.users_container = None
        self.activity_container = None
        self.local_storage_path = "data/vimarsh-db"
        
        # Initialize connection
        self._initialize_connection()
        
        logger.info(f"🔗 UserProfileService initialized - Cosmos: {self.cosmos_client is not None}")
    
    def _initialize_connection(self):
        """Initialize Cosmos DB connection or fallback to local storage"""
        if not COSMOS_AVAILABLE:
            logger.warning("📁 Using local JSON storage (Cosmos DB SDK not available)")
            self._ensure_local_directories()
            return
        
        try:
            # Try to get Cosmos DB configuration - support both formats
            cosmos_endpoint = os.getenv("COSMOS_DB_ENDPOINT")
            cosmos_key = os.getenv("COSMOS_DB_KEY")
            cosmos_connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING") or os.getenv("COSMOS_CONNECTION_STRING")
            database_name = os.getenv("AZURE_COSMOS_DATABASE_NAME") or os.getenv("COSMOS_DB_NAME") or os.getenv("COSMOS_DATABASE_NAME", "vimarsh-multi-personality")
            
            if not cosmos_endpoint and not cosmos_connection_string:
                logger.warning("📁 No Cosmos DB configuration found - using local storage")
                logger.info("   Expected: AZURE_COSMOS_CONNECTION_STRING or COSMOS_DB_ENDPOINT")
                self._ensure_local_directories()
                return
            
            # Initialize Cosmos client
            if cosmos_connection_string:
                # Use connection string (production format)
                self.cosmos_client = CosmosClient.from_connection_string(cosmos_connection_string)
                logger.info("🔑 Connected to Cosmos DB with connection string")
            elif cosmos_key:
                # Use endpoint + key format
                self.cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
                logger.info("🔑 Connected to Cosmos DB with endpoint + key")
            else:
                # Use managed identity for Azure-hosted environments
                credential = DefaultAzureCredential()
                self.cosmos_client = CosmosClient(cosmos_endpoint, credential)
                logger.info("🔐 Connected to Cosmos DB with managed identity")
            
            # Get database and containers - Updated for new 11-container architecture
            self.database = self.cosmos_client.get_database_client(database_name)
            self.users_container = self.database.get_container_client("user_profiles")  # Updated container name
            self.activity_container = self.database.get_container_client("user_activity")  # Updated container name
            
            logger.info("✅ Cosmos DB containers connected successfully")
            logger.info(f"   Database: {database_name}")
            logger.info("   Containers: user_profiles, user_activity")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
            logger.info("📁 Falling back to local JSON storage")
            self.cosmos_client = None
            self._ensure_local_directories()
    
    def _ensure_local_directories(self):
        """Create local storage directories"""
        os.makedirs(f"{self.local_storage_path}/users", exist_ok=True)
        os.makedirs(f"{self.local_storage_path}/user_activity", exist_ok=True)
    
    async def get_or_create_user_profile(self, auth_user: AuthenticatedUser) -> UserDocument:
        """
        Get existing user profile or create new one from authenticated user.
        
        Args:
            auth_user: Authenticated user from auth service
            
        Returns:
            UserDocument: Complete user profile
        """
        try:
            # Try to find existing user by auth_id first, then by email
            existing_user = await self._find_user_by_auth_id(auth_user.id)
            
            if existing_user:
                # Update last login and return existing user
                existing_user.last_login = datetime.utcnow()
                existing_user.last_activity = datetime.utcnow()
                
                # Update any changed profile information from auth provider
                existing_user.name = auth_user.name
                existing_user.email = auth_user.email
                existing_user.given_name = auth_user.given_name
                existing_user.family_name = auth_user.family_name
                existing_user.job_title = auth_user.job_title
                existing_user.company_name = auth_user.company_name
                existing_user.tenant_id = auth_user.tenant_id
                
                await self._save_user_document(existing_user)
                logger.info(f"👤 Updated existing user profile: {existing_user.email}")
                return existing_user
            
            # Create new user profile
            new_user = self._create_user_from_auth(auth_user)
            await self._save_user_document(new_user)
            
            # Create initial session activity
            await self._record_session_start(new_user.id)
            
            logger.info(f"🆕 Created new user profile: {new_user.email}")
            return new_user
            
        except Exception as e:
            logger.error(f"❌ Error in get_or_create_user_profile: {e}")
            raise
    
    def _create_user_from_auth(self, auth_user: AuthenticatedUser) -> UserDocument:
        """Create UserDocument from AuthenticatedUser"""
        user_id = str(uuid.uuid4())
        
        # Extract spiritual preferences from auth_user if available
        spiritual_prefs = {}
        if hasattr(auth_user, 'preferred_personalities'):
            spiritual_prefs['preferred_personalities'] = auth_user.preferred_personalities
        if hasattr(auth_user, 'profile'):
            spiritual_prefs.update(auth_user.profile)
        
        return UserDocument(
            id=user_id,
            partition_key=user_id,
            auth_id=auth_user.id,
            email=auth_user.email,
            name=auth_user.name,
            given_name=auth_user.given_name,
            family_name=auth_user.family_name,
            job_title=auth_user.job_title,
            company_name=auth_user.company_name,
            tenant_id=auth_user.tenant_id,
            user_preferences=spiritual_prefs,
            is_admin=(auth_user.role.name == "ADMIN" if hasattr(auth_user.role, 'name') else False)
        )
    
    async def _find_user_by_auth_id(self, auth_id: str) -> Optional[UserDocument]:
        """Find user by Microsoft Entra ID"""
        if self.cosmos_client:
            return await self._find_user_cosmos(auth_id)
        else:
            return await self._find_user_local(auth_id)
    
    async def _find_user_cosmos(self, auth_id: str) -> Optional[UserDocument]:
        """Find user in Cosmos DB by auth_id"""
        try:
            query = "SELECT * FROM user_profiles u WHERE u.auth_id = @auth_id"
            parameters = [{"name": "@auth_id", "value": auth_id}]
            
            items = list(self.users_container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            if items:
                user_data = items[0]
                # Convert datetime strings back to datetime objects
                if isinstance(user_data.get('created_at'), str):
                    user_data['created_at'] = datetime.fromisoformat(user_data['created_at'].replace('Z', '+00:00'))
                if isinstance(user_data.get('last_login'), str):
                    user_data['last_login'] = datetime.fromisoformat(user_data['last_login'].replace('Z', '+00:00'))
                if isinstance(user_data.get('last_activity'), str):
                    user_data['last_activity'] = datetime.fromisoformat(user_data['last_activity'].replace('Z', '+00:00'))
                if user_data.get('last_consent_update') and isinstance(user_data['last_consent_update'], str):
                    user_data['last_consent_update'] = datetime.fromisoformat(user_data['last_consent_update'].replace('Z', '+00:00'))
                
                return UserDocument(**user_data)
            
            return None
            
        except exceptions.CosmosResourceNotFoundError:
            return None
        except Exception as e:
            logger.error(f"❌ Error finding user in Cosmos DB: {e}")
            return None
    
    async def _find_user_local(self, auth_id: str) -> Optional[UserDocument]:
        """Find user in local JSON storage by auth_id"""
        try:
            users_dir = f"{self.local_storage_path}/users"
            for filename in os.listdir(users_dir):
                if filename.endswith('.json'):
                    with open(f"{users_dir}/{filename}", 'r') as f:
                        user_data = json.load(f)
                        if user_data.get('auth_id') == auth_id:
                            # Convert datetime strings back to datetime objects
                            if isinstance(user_data.get('created_at'), str):
                                user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
                            if isinstance(user_data.get('last_login'), str):
                                user_data['last_login'] = datetime.fromisoformat(user_data['last_login'])
                            if isinstance(user_data.get('last_activity'), str):
                                user_data['last_activity'] = datetime.fromisoformat(user_data['last_activity'])
                            if user_data.get('last_consent_update') and isinstance(user_data['last_consent_update'], str):
                                user_data['last_consent_update'] = datetime.fromisoformat(user_data['last_consent_update'])
                            
                            return UserDocument(**user_data)
            return None
        except Exception as e:
            logger.error(f"❌ Error finding user in local storage: {e}")
            return None
    
    async def _save_user_document(self, user_doc: UserDocument):
        """Save user document to storage"""
        if self.cosmos_client:
            await self._save_user_cosmos(user_doc)
        else:
            await self._save_user_local(user_doc)
    
    async def _save_user_cosmos(self, user_doc: UserDocument):
        """Save user document to Cosmos DB"""
        try:
            # Convert to dict and handle datetime serialization
            user_dict = asdict(user_doc)
            
            # Convert datetime objects to ISO strings
            for field in ['created_at', 'last_login', 'last_activity', 'last_consent_update']:
                if user_dict.get(field) and isinstance(user_dict[field], datetime):
                    user_dict[field] = user_dict[field].isoformat()
            
            self.users_container.upsert_item(user_dict)
            logger.info(f"💾 Saved user to Cosmos DB: {user_doc.email}")
            
        except Exception as e:
            logger.error(f"❌ Error saving user to Cosmos DB: {e}")
            raise
    
    async def _save_user_local(self, user_doc: UserDocument):
        """Save user document to local JSON storage"""
        try:
            # Convert to dict and handle datetime serialization
            user_dict = asdict(user_doc)
            
            # Convert datetime objects to ISO strings
            for field in ['created_at', 'last_login', 'last_activity', 'last_consent_update']:
                if user_dict.get(field) and isinstance(user_dict[field], datetime):
                    user_dict[field] = user_dict[field].isoformat()
            
            filepath = f"{self.local_storage_path}/users/{user_doc.id}.json"
            with open(filepath, 'w') as f:
                json.dump(user_dict, f, indent=2, default=str)
            
            logger.info(f"💾 Saved user to local storage: {user_doc.email}")
            
        except Exception as e:
            logger.error(f"❌ Error saving user to local storage: {e}")
            raise
    
    async def record_interaction(self, user_id: str, session_id: str, interaction_data: Dict[str, Any]):
        """
        Record a user interaction and update aggregated statistics.
        
        Args:
            user_id: User ID
            session_id: Session ID
            interaction_data: Interaction details
        """
        try:
            # Create interaction activity document
            interaction_doc = UserActivityDocument(
                id=str(uuid.uuid4()),
                partition_key=user_id,
                document_type=DocumentType.INTERACTION.value,
                user_id=user_id,
                interaction_data={
                    "session_id": session_id,
                    "sequence": interaction_data.get("sequence", 1),
                    "user_query": interaction_data.get("query", ""),
                    "personality_used": interaction_data.get("personality", "krishna"),
                    "response_text": interaction_data.get("response", ""),
                    "response_time_ms": interaction_data.get("response_time_ms", 0),
                    "model_used": interaction_data.get("model", "gemini-flash"),
                    "input_tokens": interaction_data.get("input_tokens", 0),
                    "output_tokens": interaction_data.get("output_tokens", 0),
                    "cost_usd": interaction_data.get("cost_usd", 0.0),
                    "user_rating": interaction_data.get("rating"),
                    "was_bookmarked": interaction_data.get("bookmarked", False),
                    "content_themes": interaction_data.get("themes", [])
                }
            )
            
            # Save interaction to activity container
            await self._save_activity_document(interaction_doc)
            
            # Update user's aggregated stats and recent activity
            await self._update_user_stats(user_id, interaction_data)
            
            logger.info(f"📝 Recorded interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error recording interaction: {e}")
            raise
    
    async def _record_session_start(self, user_id: str) -> str:
        """Record session start and return session ID"""
        session_id = str(uuid.uuid4())
        
        try:
            session_doc = UserActivityDocument(
                id=str(uuid.uuid4()),
                partition_key=user_id,
                document_type=DocumentType.SESSION.value,
                user_id=user_id,
                session_data={
                    "session_id": session_id,
                    "start_time": datetime.utcnow().isoformat(),
                    "status": "active"
                }
            )
            
            await self._save_activity_document(session_doc)
            logger.info(f"🎯 Started session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Error starting session: {e}")
            return session_id  # Return session_id even if recording fails
    
    async def _save_activity_document(self, activity_doc: UserActivityDocument):
        """Save activity document to storage"""
        if self.cosmos_client:
            await self._save_activity_cosmos(activity_doc)
        else:
            await self._save_activity_local(activity_doc)
    
    async def _save_activity_cosmos(self, activity_doc: UserActivityDocument):
        """Save activity document to Cosmos DB"""
        try:
            activity_dict = asdict(activity_doc)
            
            # Convert datetime to ISO string
            if isinstance(activity_dict.get('timestamp'), datetime):
                activity_dict['timestamp'] = activity_dict['timestamp'].isoformat()
            
            self.activity_container.upsert_item(activity_dict)
            
        except Exception as e:
            logger.error(f"❌ Error saving activity to Cosmos DB: {e}")
            raise
    
    async def _save_activity_local(self, activity_doc: UserActivityDocument):
        """Save activity document to local JSON storage"""
        try:
            activity_dict = asdict(activity_doc)
            
            # Convert datetime to ISO string
            if isinstance(activity_dict.get('timestamp'), datetime):
                activity_dict['timestamp'] = activity_dict['timestamp'].isoformat()
            
            filepath = f"{self.local_storage_path}/user_activity/{activity_doc.id}.json"
            with open(filepath, 'w') as f:
                json.dump(activity_dict, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"❌ Error saving activity to local storage: {e}")
            raise
    
    async def _update_user_stats(self, user_id: str, interaction_data: Dict[str, Any]):
        """Update user's aggregated statistics and recent activity"""
        try:
            # Get current user document
            user_doc = await self._get_user_by_id(user_id)
            if not user_doc:
                logger.warning(f"⚠️ User {user_id} not found for stats update")
                return
            
            # Update usage statistics
            stats = user_doc.usage_stats
            stats["total_queries"] = stats.get("total_queries", 0) + 1
            stats["total_tokens"] = stats.get("total_tokens", 0) + interaction_data.get("input_tokens", 0) + interaction_data.get("output_tokens", 0)
            stats["total_cost_usd"] = stats.get("total_cost_usd", 0.0) + interaction_data.get("cost_usd", 0.0)
            
            # Update personality usage
            personality = interaction_data.get("personality", "krishna")
            fav_personalities = stats.get("favorite_personalities", [])
            if personality not in fav_personalities:
                fav_personalities.append(personality)
                stats["favorite_personalities"] = fav_personalities
            
            # Update recent activity (keep last 10)
            recent_item = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": interaction_data.get("query", "")[:100],  # Truncate long queries
                "personality": personality,
                "rating": interaction_data.get("rating"),
                "bookmarked": interaction_data.get("bookmarked", False)
            }
            
            user_doc.recent_activity.insert(0, recent_item)
            user_doc.recent_activity = user_doc.recent_activity[:10]  # Keep only last 10
            
            # Update last activity timestamp
            user_doc.last_activity = datetime.utcnow()
            user_doc.usage_stats = stats
            
            # Save updated user document
            await self._save_user_document(user_doc)
            
        except Exception as e:
            logger.error(f"❌ Error updating user stats: {e}")
    
    async def _get_user_by_id(self, user_id: str) -> Optional[UserDocument]:
        """Get user by internal user ID"""
        if self.cosmos_client:
            try:
                user_data = self.users_container.read_item(item=user_id, partition_key=user_id)
                
                # Convert datetime strings back to datetime objects
                if isinstance(user_data.get('created_at'), str):
                    user_data['created_at'] = datetime.fromisoformat(user_data['created_at'].replace('Z', '+00:00'))
                if isinstance(user_data.get('last_login'), str):
                    user_data['last_login'] = datetime.fromisoformat(user_data['last_login'].replace('Z', '+00:00'))
                if isinstance(user_data.get('last_activity'), str):
                    user_data['last_activity'] = datetime.fromisoformat(user_data['last_activity'].replace('Z', '+00:00'))
                if user_data.get('last_consent_update') and isinstance(user_data['last_consent_update'], str):
                    user_data['last_consent_update'] = datetime.fromisoformat(user_data['last_consent_update'].replace('Z', '+00:00'))
                
                return UserDocument(**user_data)
                
            except exceptions.CosmosResourceNotFoundError:
                return None
        else:
            # Local storage
            try:
                filepath = f"{self.local_storage_path}/users/{user_id}.json"
                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        user_data = json.load(f)
                        
                    # Convert datetime strings back to datetime objects
                    for field in ['created_at', 'last_login', 'last_activity', 'last_consent_update']:
                        if user_data.get(field) and isinstance(user_data[field], str):
                            user_data[field] = datetime.fromisoformat(user_data[field])
                    
                    return UserDocument(**user_data)
                return None
            except Exception as e:
                logger.error(f"❌ Error getting user from local storage: {e}")
                return None
    
    async def add_bookmark(self, user_id: str, bookmark_data: Dict[str, Any]) -> bool:
        """Add bookmark to user's profile"""
        try:
            user_doc = await self._get_user_by_id(user_id)
            if not user_doc:
                return False
            
            bookmark = {
                "bookmark_id": str(uuid.uuid4()),
                "title": bookmark_data.get("title", "Spiritual Guidance"),
                "query": bookmark_data.get("query", ""),
                "response": bookmark_data.get("response", "")[:500],  # Truncate long responses
                "personality": bookmark_data.get("personality", "krishna"),
                "bookmarked_at": datetime.utcnow().isoformat(),
                "tags": bookmark_data.get("tags", []),
                "notes": bookmark_data.get("notes", "")
            }
            
            user_doc.bookmarks.append(bookmark)
            await self._save_user_document(user_doc)
            
            logger.info(f"🔖 Added bookmark for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding bookmark: {e}")
            return False
    
    async def get_user_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user analytics for the specified period"""
        try:
            user_doc = await self._get_user_by_id(user_id)
            if not user_doc:
                return {}
            
            # Return basic analytics from user document
            return {
                "user_id": user_id,
                "email": user_doc.email,
                "account_created": user_doc.created_at.isoformat() if user_doc.created_at else None,
                "last_activity": user_doc.last_activity.isoformat() if user_doc.last_activity else None,
                "usage_stats": user_doc.usage_stats,
                "recent_activity": user_doc.recent_activity,
                "bookmarks_count": len(user_doc.bookmarks),
                "account_status": user_doc.account_status
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user analytics: {e}")
            return {}


# Global service instance
user_profile_service = UserProfileService()
