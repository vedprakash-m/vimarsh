#!/usr/bin/env python3
"""
Migration rollback script
Restores original database structure and data from backup
"""

import os
import sys
import json
import shutil
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from root .env
load_dotenv('../../.env')

try:
    from azure.cosmos import CosmosClient, PartitionKey
    
    def find_latest_backup():
        """Find the most recent backup directory"""
        backup_base_dir = "../../data/migration_backups"
        
        if not os.path.exists(backup_base_dir):
            print("❌ No backup directory found")
            return None
        
        backup_dirs = [d for d in os.listdir(backup_base_dir) 
                      if d.startswith('backup_') and os.path.isdir(os.path.join(backup_base_dir, d))]
        
        if not backup_dirs:
            print("❌ No backup directories found")
            return None
        
        # Sort by timestamp (latest first)
        backup_dirs.sort(reverse=True)
        latest_backup = os.path.join(backup_base_dir, backup_dirs[0])
        
        print(f"📁 Found latest backup: {latest_backup}")
        return latest_backup
    
    def validate_backup(backup_dir):
        """Validate that backup contains expected data"""
        manifest_path = os.path.join(backup_dir, 'manifest.json')
        
        if not os.path.exists(manifest_path):
            print("❌ Backup manifest not found")
            return False
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        expected_containers = ['personality-vectors', 'users', 'user_activity']
        
        for container in expected_containers:
            if container not in manifest['containers']:
                print(f"❌ Container {container} not found in backup")
                return False
            
            backup_file = os.path.join(backup_dir, f"{container}.json")
            if not os.path.exists(backup_file):
                print(f"❌ Backup file for {container} not found")
                return False
        
        # Validate critical personality-vectors data
        vectors_count = manifest['containers']['personality-vectors']['document_count']
        if vectors_count < 6500:  # Should be around 6514
            print(f"❌ personality-vectors backup has only {vectors_count} documents (expected ~6514)")
            return False
        
        print(f"✅ Backup validation passed - {vectors_count} personality vectors found")
        return True
    
    def delete_new_containers(database):
        """Delete containers that were created during migration"""
        new_containers = [
            'user_sessions', 'user_interactions', 'personalities',
            'user_analytics', 'content_analytics', 'daily_metrics',
            'abuse_incidents', 'engagement_summary', 'content_popularity',
            'incidents_by_content'
        ]
        
        print("\n🗑️ Deleting new containers...")
        
        for container_name in new_containers:
            try:
                container = database.get_container_client(container_name)
                container.delete_container()
                print(f"✅ Deleted container: {container_name}")
            except Exception as e:
                if "NotFound" in str(e):
                    print(f"ℹ️ Container {container_name} does not exist")
                else:
                    print(f"❌ Error deleting {container_name}: {e}")
    
    def restore_original_containers(database, backup_dir):
        """Restore original containers from backup"""
        print("\n🔄 Restoring original containers...")
        
        # Container configurations for original structure
        original_containers = {
            'personality-vectors': {'partition_key': '/personality_id'},
            'users': {'partition_key': '/user_id'},
            'user_activity': {'partition_key': '/user_id'}
        }
        
        for container_name, config in original_containers.items():
            try:
                # Delete if exists (might be the new version)
                try:
                    existing_container = database.get_container_client(container_name.replace('-', '_'))
                    existing_container.delete_container()
                    print(f"✅ Deleted modified container: {container_name}")
                except:
                    pass
                
                # Create with original configuration
                partition_key = PartitionKey(path=config['partition_key'])
                container = database.create_container(
                    id=container_name,
                    partition_key=partition_key,
                    offer_throughput=400
                )
                print(f"✅ Created original container: {container_name}")
                
                # Restore data
                backup_file = os.path.join(backup_dir, f"{container_name}.json")
                with open(backup_file, 'r') as f:
                    documents = json.load(f)
                
                print(f"📝 Restoring {len(documents)} documents to {container_name}...")
                
                for doc in documents:
                    try:
                        container.create_item(body=doc)
                    except Exception as e:
                        print(f"⚠️ Error restoring document {doc.get('id', 'unknown')}: {e}")
                
                print(f"✅ Restored {len(documents)} documents to {container_name}")
                
            except Exception as e:
                print(f"❌ Error restoring {container_name}: {e}")
                return False
        
        return True
    
    def verify_rollback(database):
        """Verify that rollback was successful"""
        print("\n🔍 Verifying rollback...")
        
        original_containers = ['personality-vectors', 'users', 'user_activity']
        
        for container_name in original_containers:
            try:
                container = database.get_container_client(container_name)
                
                # Count documents
                query = "SELECT VALUE COUNT(1) FROM c"
                result = list(container.query_items(query=query, enable_cross_partition_query=True))
                count = result[0] if result else 0
                
                print(f"✅ {container_name}: {count} documents")
                
                # Special check for personality-vectors
                if container_name == 'personality-vectors':
                    if count < 6500:
                        print(f"❌ personality-vectors only has {count} documents (expected ~6514)")
                        return False
                    
                    # Check for embeddings
                    embedding_query = "SELECT TOP 1 c.embedding FROM c WHERE IS_DEFINED(c.embedding)"
                    embedding_results = list(container.query_items(
                        query=embedding_query, 
                        enable_cross_partition_query=True
                    ))
                    
                    if not embedding_results:
                        print("❌ No embeddings found in personality-vectors!")
                        return False
                    else:
                        print("✅ Embeddings verified in personality-vectors")
                
            except Exception as e:
                print(f"❌ Error verifying {container_name}: {e}")
                return False
        
        return True
    
    def main():
        """Main rollback function"""
        print("🔄 MIGRATION ROLLBACK")
        print("=" * 50)
        
        # Confirm rollback
        response = input("⚠️ This will DELETE all migrated data and restore original structure. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Rollback cancelled")
            return False
        
        # Find and validate backup
        backup_dir = find_latest_backup()
        if not backup_dir:
            return False
        
        if not validate_backup(backup_dir):
            return False
        
        # Connect to database
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ AZURE_COSMOS_CONNECTION_STRING not found")
            return False
        
        client = CosmosClient.from_connection_string(connection_string)
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        database = client.get_database_client(database_name)
        
        print(f"🔗 Connected to database: {database_name}")
        
        # Execute rollback
        print("\n🚀 Starting rollback process...")
        
        # Step 1: Delete new containers
        delete_new_containers(database)
        
        # Step 2: Restore original containers
        if not restore_original_containers(database, backup_dir):
            print("❌ Failed to restore original containers")
            return False
        
        # Step 3: Verify rollback
        if not verify_rollback(database):
            print("❌ Rollback verification failed")
            return False
        
        print("\n🎉 ROLLBACK COMPLETED SUCCESSFULLY!")
        print("Original database structure and data have been restored.")
        print(f"Backup used: {backup_dir}")
        
        return True

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
