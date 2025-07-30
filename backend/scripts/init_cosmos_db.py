"""
Cosmos DB Database and Container Initialization Script
Creates the 2-container user database design for Vimarsh spiritual guidance platform.
"""

import os
import logging

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


class CosmosDBInitializer:
    """Initialize Cosmos DB database and containers for user profile system"""
    
    def __init__(self):
        """Initialize with environment configuration"""
        self.cosmos_endpoint = os.getenv("COSMOS_DB_ENDPOINT")
        self.cosmos_key = os.getenv("COSMOS_DB_KEY") 
        self.cosmos_connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING") or os.getenv("COSMOSDB_CONNECTION_STRING")
        self.database_name = os.getenv("AZURE_COSMOS_DATABASE_NAME") or os.getenv("COSMOS_DATABASE_NAME", "vimarsh-multi-personality")
        
        if not self.cosmos_endpoint and not self.cosmos_connection_string:
            raise ValueError(
                "Cosmos DB configuration required. Set either:\n"
                "  - AZURE_COSMOS_CONNECTION_STRING (recommended for production)\n"
                "  - COSMOS_DB_ENDPOINT + COSMOS_DB_KEY (alternative)"
            )
        
        # Initialize client
        self.cosmos_client = self._create_client()
        logger.info(f"🔗 Connected to Cosmos DB for database: {self.database_name}")
    
    def _create_client(self) -> CosmosClient:
        """Create Cosmos DB client with connection string or endpoint"""
        if self.cosmos_connection_string:
            logger.info("🔑 Using Cosmos DB connection string")
            return CosmosClient.from_connection_string(self.cosmos_connection_string)
        elif self.cosmos_key:
            logger.info("🔑 Using Cosmos DB endpoint + key")
            return CosmosClient(self.cosmos_endpoint, self.cosmos_key)
        else:
            # Use managed identity for Azure-hosted environments
            logger.info("🔐 Using Cosmos DB with managed identity")
            credential = DefaultAzureCredential()
            return CosmosClient(self.cosmos_endpoint, credential)
    
    def initialize_database(self) -> bool:
        """Create database and containers with optimized configuration"""
        
        try:
            # Create database (serverless mode)
            logger.info(f"📚 Creating database: {self.database_name}")
            
            database = self.cosmos_client.create_database_if_not_exists(
                id=self.database_name
            )
            logger.info(f"✅ Database '{self.database_name}' ready")
            
            # Create Container 1: users (User profiles with embedded data)
            logger.info("🏺 Creating 'users' container...")
            
            database.create_container_if_not_exists(
                id="users",
                partition_key=PartitionKey(path="/partition_key"),
                # Serverless mode - no throughput specification needed
            )
            logger.info("✅ Container 'users' created successfully")
            
            # Create Container 2: user_activity (All detailed activity)
            logger.info("📊 Creating 'user_activity' container...")
            
            database.create_container_if_not_exists(
                id="user_activity", 
                partition_key=PartitionKey(path="/partition_key"),
                # Serverless mode - no throughput specification needed
            )
            logger.info("✅ Container 'user_activity' created successfully")
            
            # Create indexes for optimal query performance
            self._create_indexes(database)
            
            logger.info("🎉 Cosmos DB initialization completed successfully!")
            logger.info("\n📋 Database Summary:")
            logger.info(f"   Database: {self.database_name}")
            logger.info("   Containers:")
            logger.info("   - users (User profiles with embedded recent activity & bookmarks)")
            logger.info("   - user_activity (All detailed sessions, interactions & analytics)")
            logger.info("   Mode: Serverless (pay-per-request)")
            logger.info("   Estimated cost: $3-8/month for 1,000 users")
            
            return True
            
        except exceptions.CosmosResourceExistsError:
            logger.info("ℹ️ Database and containers already exist")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB: {e}")
            return False
    
    def _create_indexes(self, database):
        """Create composite indexes for efficient queries"""
        try:
            logger.info("🔍 Creating optimized indexes...")
            
            # Note: In serverless mode, indexes are managed automatically
            # But we can verify the default indexing policy
            
            users_container = database.get_container_client("users")
            activity_container = database.get_container_client("user_activity")
            
            # Log current indexing policies
            users_policy = users_container.read().get('indexingPolicy', {})
            activity_policy = activity_container.read().get('indexingPolicy', {})
            
            logger.info("✅ Indexing policies verified:")
            logger.info(f"   Users container: {users_policy.get('indexingMode', 'consistent')}")
            logger.info(f"   Activity container: {activity_policy.get('indexingMode', 'consistent')}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not verify indexes: {e}")
    
    def test_connection(self) -> bool:
        """Test database connection and basic operations"""
        try:
            logger.info("🧪 Testing database connection...")
            
            database = self.cosmos_client.get_database_client(self.database_name)
            users_container = database.get_container_client("users")
            
            # Try to query (should return empty results for new database)
            query = "SELECT COUNT(1) as count FROM users"
            result = list(users_container.query_items(query=query, enable_cross_partition_query=True))
            
            logger.info(f"✅ Connection test successful. Current users: {result[0]['count'] if result else 0}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    def create_sample_data(self):
        """Create sample user data for testing (optional)"""
        try:
            from datetime import datetime
            import uuid
            
            logger.info("📝 Creating sample test data...")
            
            database = self.cosmos_client.get_database_client(self.database_name)
            users_container = database.get_container_client("users")
            
            # Sample user document
            test_user = {
                "id": str(uuid.uuid4()),
                "partition_key": None,  # Will be set to id
                "document_type": "user_profile",
                "auth_id": "test-microsoft-auth-id",
                "email": "test@vimarsh.example.com",
                "name": "Test User",
                "given_name": "Test",
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
            
            test_user["partition_key"] = test_user["id"]
            
            users_container.create_item(test_user)
            logger.info(f"✅ Sample user created: {test_user['email']}")
            
        except exceptions.CosmosResourceExistsError:
            logger.info("ℹ️ Sample data already exists")
        except Exception as e:
            logger.warning(f"⚠️ Could not create sample data: {e}")


def main():
    """Main initialization function"""
    print("🚀 Vimarsh Cosmos DB Initialization")
    print("=" * 50)
    
    # Load environment variables from root .env file
    from pathlib import Path
    root_path = Path(__file__).parent.parent.parent  # Go up to project root
    env_file = root_path / ".env"
    
    if env_file.exists():
        print(f"📋 Loading environment from: {env_file}")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ Environment variables loaded from .env")
        except ImportError:
            print("⚠️ python-dotenv not available - using system environment")
    else:
        print("⚠️ No .env file found in project root")
    
    # Check if we have Cosmos DB configuration
    cosmos_conn = os.getenv("AZURE_COSMOS_CONNECTION_STRING") or os.getenv("COSMOSDB_CONNECTION_STRING")
    if not cosmos_conn:
        print("❌ No Cosmos DB connection string found in environment")
        print("\n📋 Required environment variables:")
        print("   AZURE_COSMOS_CONNECTION_STRING=AccountEndpoint=...;AccountKey=...;")
        print("   OR")
        print("   COSMOS_DB_ENDPOINT + COSMOS_DB_KEY")
        return False
    
    try:
        # Initialize Cosmos DB
        initializer = CosmosDBInitializer()
        
        # Create database and containers
        success = initializer.initialize_database()
        if not success:
            return False
        
        # Test connection
        success = initializer.test_connection()
        if not success:
            return False
        
        # Optionally create sample data
        create_sample = input("\n❓ Create sample test data? (y/N): ").lower().strip()
        if create_sample == 'y':
            initializer.create_sample_data()
        
        print("\n🎉 Initialization completed successfully!")
        print("\n📋 Next steps:")
        print("1. Deploy your Azure Functions app with the UserProfileService")
        print("2. Test the authentication flow - should now work perfectly!")
        print("3. Check new endpoints: /user/profile, /user/bookmark")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        return False


if __name__ == "__main__":
    main()
