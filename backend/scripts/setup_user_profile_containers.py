"""
Initialize User Profile Containers in Existing Cosmos DB
Adds the 2-container user profile system to your existing vimarsh-db setup.
"""

import os
import logging
from typing import Dict, Any

# Azure Cosmos DB imports
try:
    from azure.cosmos import CosmosClient, PartitionKey, exceptions
    from azure.identity import DefaultAzureCredential
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False
    print("❌ Azure Cosmos DB SDK not available. Install with: pip install azure-cosmos azure-identity")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserProfileContainerSetup:
    """Setup user profile containers in existing Cosmos DB"""
    
    def __init__(self):
        """Initialize with existing Cosmos DB configuration"""
        # Use your existing environment variables
        self.cosmos_connection_string = (
            os.getenv("AZURE_COSMOS_CONNECTION_STRING") or 
            os.getenv("COSMOS_CONNECTION_STRING")
        )
        self.database_name = (
            os.getenv("COSMOS_DATABASE_NAME") or 
            os.getenv("COSMOS_DB_NAME", "vimarsh-db")
        )
        
        if not self.cosmos_connection_string:
            raise ValueError(
                "❌ Cosmos DB connection string not found!\n"
                "   For development: Set COSMOS_CONNECTION_STRING in .env\n"
                "   For production: Set AZURE_COSMOS_CONNECTION_STRING as environment var"
            )
        
        if self.cosmos_connection_string == "dev-mode-local-storage":
            print("ℹ️ Development mode detected - local storage will be used")
            print("   This setup is for production Cosmos DB only")
            exit(0)
        
        # Initialize client
        self.cosmos_client = CosmosClient.from_connection_string(self.cosmos_connection_string)
        logger.info(f"🔗 Connected to existing Cosmos DB: {self.database_name}")
    
    def setup_user_profile_containers(self) -> bool:
        """Add user profile containers to existing database"""
        
        try:
            # Get existing database (should already exist)
            database = self.cosmos_client.get_database_client(self.database_name)
            logger.info(f"📚 Using existing database: {self.database_name}")
            
            # Check existing containers
            existing_containers = []
            try:
                for container in database.list_containers():
                    existing_containers.append(container['id'])
            except:
                pass
            
            if existing_containers:
                logger.info(f"📦 Found existing containers: {', '.join(existing_containers)}")
            
            # Create Container 1: users (if not exists)
            if "users" not in existing_containers:
                logger.info("🏺 Creating 'users' container...")
                database.create_container(
                    id="users",
                    partition_key=PartitionKey(path="/partition_key"),
                )
                logger.info("✅ Container 'users' created successfully")
            else:
                logger.info("ℹ️ Container 'users' already exists")
            
            # Create Container 2: user_activity (if not exists)
            if "user_activity" not in existing_containers:
                logger.info("📊 Creating 'user_activity' container...")
                database.create_container(
                    id="user_activity", 
                    partition_key=PartitionKey(path="/partition_key"),
                )
                logger.info("✅ Container 'user_activity' created successfully")
            else:
                logger.info("ℹ️ Container 'user_activity' already exists")
            
            # Verify containers
            self._verify_containers(database)
            
            logger.info("🎉 User profile container setup completed!")
            logger.info("\n📋 Database Summary:")
            logger.info(f"   Database: {self.database_name}")
            logger.info("   User Profile Containers:")
            logger.info("   - users (User profiles with embedded recent activity & bookmarks)")
            logger.info("   - user_activity (All detailed sessions, interactions & analytics)")
            if existing_containers:
                logger.info("   Existing Containers:")
                for container in existing_containers:
                    logger.info(f"   - {container}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup user profile containers: {e}")
            return False
    
    def _verify_containers(self, database):
        """Verify containers are accessible"""
        try:
            users_container = database.get_container_client("users")
            activity_container = database.get_container_client("user_activity")
            
            # Test basic operations
            users_container.read()
            activity_container.read()
            
            logger.info("✅ Container verification successful")
            
        except Exception as e:
            logger.warning(f"⚠️ Container verification failed: {e}")
    
    def create_sample_user(self):
        """Create a sample user for testing (optional)"""
        try:
            from datetime import datetime
            import uuid
            
            logger.info("📝 Creating sample user for testing...")
            
            database = self.cosmos_client.get_database_client(self.database_name)
            users_container = database.get_container_client("users")
            
            # Sample user document matching your schema
            sample_user = {
                "id": str(uuid.uuid4()),
                "partition_key": None,  # Will be set to id
                "auth_id": "sample-microsoft-auth-id",
                "email": "sample@vimarsh.example.com",
                "name": "Sample User",
                "document_type": "user_profile",
                "given_name": "Sample",
                "family_name": "User",
                "auth_provider": "microsoft",
                "account_status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "user_preferences": {
                    "preferred_personalities": ["krishna", "buddha"]
                },
                "usage_stats": {
                    "total_sessions": 0,
                    "total_queries": 0,
                    "total_tokens": 0,
                    "total_cost_usd": 0.0,
                    "favorite_personalities": [],
                    "common_topics": [],
                    "monthly_usage": {}
                },
                "recent_activity": [],
                "bookmarks": [],
                "risk_score": 0.0,
                "abuse_flags": [],
                "is_admin": False,
                "data_retention_consent": True,
                "analytics_consent": True,
                "last_consent_update": datetime.utcnow().isoformat()
            }
            
            sample_user["partition_key"] = sample_user["id"]
            
            users_container.create_item(sample_user)
            logger.info(f"✅ Sample user created: {sample_user['email']}")
            logger.info(f"   User ID: {sample_user['id']}")
            
        except exceptions.CosmosResourceExistsError:
            logger.info("ℹ️ Sample user already exists")
        except Exception as e:
            logger.warning(f"⚠️ Could not create sample user: {e}")


def main():
    """Main setup function"""
    print("🚀 Vimarsh User Profile Container Setup")
    print("=" * 50)
    
    try:
        # Initialize setup
        setup = UserProfileContainerSetup()
        
        # Create user profile containers
        success = setup.setup_user_profile_containers()
        if not success:
            return False
        
        # Optionally create sample data
        create_sample = input("\n❓ Create sample user for testing? (y/N): ").lower().strip()
        if create_sample == 'y':
            setup.create_sample_user()
        
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Deploy your backend with the UserProfileService")
        print("2. Test the authentication flow - should now work perfectly!")
        print("3. Check new endpoints: /api/user/profile and /api/user/bookmark")
        print("4. Monitor user interactions and analytics")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False


if __name__ == "__main__":
    main()
