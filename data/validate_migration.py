#!/usr/bin/env python3
"""
Migration validation script
Verifies data integrity after migration
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from root .env
load_dotenv('../../.env')

try:
    from azure.cosmos import CosmosClient
    
    def get_container_count(database, container_name):
        """Get document count for a container"""
        try:
            container = database.get_container_client(container_name)
            query = "SELECT VALUE COUNT(1) FROM c"
            result = list(container.query_items(query=query, enable_cross_partition_query=True))
            return result[0] if result else 0
        except Exception as e:
            print(f"❌ Error counting {container_name}: {e}")
            return -1
    
    def validate_embeddings_preserved(database):
        """Validate that embeddings are preserved in personality_vectors"""
        try:
            container = database.get_container_client('personality_vectors')
            
            # Check for embeddings
            query = """
            SELECT TOP 10 c.id, c.embedding 
            FROM c 
            WHERE IS_DEFINED(c.embedding) AND c.embedding != null
            """
            
            results = list(container.query_items(query=query, enable_cross_partition_query=True))
            
            if not results:
                print("❌ No embeddings found in personality_vectors!")
                return False
            
            # Validate embedding format
            for doc in results:
                embedding = doc.get('embedding')
                if not embedding or not isinstance(embedding, list) or len(embedding) == 0:
                    print(f"❌ Invalid embedding for document {doc['id']}")
                    return False
            
            print(f"✅ Embeddings validated - {len(results)} sample documents have valid embeddings")
            return True
            
        except Exception as e:
            print(f"❌ Error validating embeddings: {e}")
            return False
    
    def validate_partition_keys(database):
        """Validate that new partition key structure is working"""
        try:
            container = database.get_container_client('personality_vectors')
            
            # Check for hierarchical partition keys
            query = """
            SELECT TOP 5 c.partition_key, c.personality_id, c.source
            FROM c 
            WHERE IS_DEFINED(c.partition_key)
            """
            
            results = list(container.query_items(query=query, enable_cross_partition_query=True))
            
            if not results:
                print("❌ No documents with partition_key found!")
                return False
            
            # Validate partition key format (should be personality_id::source)
            for doc in results:
                partition_key = doc.get('partition_key', '')
                if '::' not in partition_key:
                    print(f"❌ Invalid partition key format: {partition_key}")
                    return False
            
            print(f"✅ Partition keys validated - {len(results)} sample documents have correct format")
            return True
            
        except Exception as e:
            print(f"❌ Error validating partition keys: {e}")
            return False
    
    def validate_personality_configs(database):
        """Validate personality configurations container"""
        try:
            container = database.get_container_client('personalities')
            count = get_container_count(database, 'personalities')
            
            if count == 0:
                print("⚠️ personalities container is empty")
                return False
            
            # Get sample personality config
            query = "SELECT TOP 1 * FROM c"
            results = list(container.query_items(query=query, enable_cross_partition_query=True))
            
            if results:
                config = results[0]
                required_fields = ['personality_id', 'display_name', 'domain', 'is_active']
                for field in required_fields:
                    if field not in config:
                        print(f"❌ Missing required field in personality config: {field}")
                        return False
                
                print(f"✅ Personality configs validated - {count} configurations found")
                return True
            else:
                print("❌ No personality configurations found")
                return False
                
        except Exception as e:
            print(f"❌ Error validating personality configs: {e}")
            return False
    
    def main():
        """Main validation function"""
        print("🔍 MIGRATION VALIDATION")
        print("=" * 50)
        
        # Connect to database
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ AZURE_COSMOS_CONNECTION_STRING not found")
            return False
        
        client = CosmosClient.from_connection_string(connection_string)
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        database = client.get_database_client(database_name)
        
        # Expected document counts (from current analysis)
        expected_counts = {
            'personality_vectors': 6514,  # Must match original personality-vectors
            'users': 18,                  # Should remain same or enhanced
            'personalities': 13           # Should have unique personality configs
        }
        
        # Document count validation
        print("\n📊 DOCUMENT COUNT VALIDATION")
        print("-" * 40)
        
        count_validation_passed = True
        for container_name, expected_count in expected_counts.items():
            actual_count = get_container_count(database, container_name)
            
            if actual_count == -1:
                print(f"❌ {container_name}: Unable to count documents")
                count_validation_passed = False
            elif container_name == 'personality_vectors' and actual_count != expected_count:
                print(f"❌ {container_name}: Expected {expected_count}, got {actual_count}")
                count_validation_passed = False
            elif container_name == 'users' and actual_count < expected_count:
                print(f"❌ {container_name}: Expected at least {expected_count}, got {actual_count}")
                count_validation_passed = False
            elif container_name == 'personalities' and actual_count == 0:
                print(f"❌ {container_name}: Expected personality configs, got {actual_count}")
                count_validation_passed = False
            else:
                print(f"✅ {container_name}: {actual_count} documents")
        
        # Data integrity validation
        print("\n🔍 DATA INTEGRITY VALIDATION")
        print("-" * 40)
        
        embeddings_valid = validate_embeddings_preserved(database)
        partition_keys_valid = validate_partition_keys(database)
        personalities_valid = validate_personality_configs(database)
        
        # Container existence validation
        print("\n📦 CONTAINER EXISTENCE VALIDATION")
        print("-" * 40)
        
        required_containers = [
            'users', 'user_sessions', 'user_interactions',
            'personalities', 'personality_vectors',
            'user_analytics', 'content_analytics', 'daily_metrics',
            'abuse_incidents', 'engagement_summary', 'content_popularity',
            'incidents_by_content'
        ]
        
        containers_exist = True
        for container_name in required_containers:
            try:
                container = database.get_container_client(container_name)
                container.read()  # Verify it exists
                print(f"✅ {container_name}: exists")
            except Exception:
                print(f"❌ {container_name}: missing")
                containers_exist = False
        
        # Overall validation result
        print("\n🎯 VALIDATION SUMMARY")
        print("=" * 30)
        
        all_validations = [
            ("Document Counts", count_validation_passed),
            ("Embeddings Preserved", embeddings_valid),
            ("Partition Keys Valid", partition_keys_valid),
            ("Personality Configs", personalities_valid),
            ("All Containers Exist", containers_exist)
        ]
        
        passed_count = sum(1 for _, passed in all_validations if passed)
        total_count = len(all_validations)
        
        for validation_name, passed in all_validations:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{validation_name}: {status}")
        
        overall_success = passed_count == total_count
        
        print(f"\nOverall Result: {passed_count}/{total_count} validations passed")
        
        if overall_success:
            print("🎉 MIGRATION VALIDATION SUCCESSFUL!")
            print("All critical data has been preserved and new containers are ready.")
        else:
            print("⚠️ MIGRATION VALIDATION FAILED!")
            print("Please review failed validations before proceeding.")
        
        return overall_success

    if __name__ == "__main__":
        success = main()
        if not success:
            sys.exit(1)

except ImportError:
    print("❌ Error: azure-cosmos package not installed")
    print("Run: pip install azure-cosmos")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
