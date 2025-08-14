#!/usr/bin/env python3
"""
Data backup script for migration preparation
Exports all current data before migration starts
"""

import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from root .env
load_dotenv('../../.env')

try:
    from azure.cosmos import CosmosClient
    
    def export_container_data(container_name, output_dir):
        """Export all data from a container to JSON file"""
        print(f"📦 Exporting {container_name}...")
        
        # Get connection string
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        client = CosmosClient.from_connection_string(connection_string)
        
        # Get database and container
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        
        # Query all documents
        query = "SELECT * FROM c"
        documents = []
        
        for doc in container.query_items(query=query, enable_cross_partition_query=True):
            # Remove Cosmos DB system fields for cleaner export
            clean_doc = {k: v for k, v in doc.items() if not k.startswith('_')}
            documents.append(clean_doc)
        
        # Save to file
        output_file = os.path.join(output_dir, f"{container_name}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Exported {len(documents)} documents from {container_name} to {output_file}")
        return len(documents)
    
    def main():
        """Main backup function"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"/tmp/vimarsh-migration-backup/{timestamp}"
        
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        print(f"🗂️ Creating backup in: {backup_dir}")
        
        # Export all current containers
        containers_to_backup = ['personality-vectors', 'users', 'user_activity']
        total_documents = 0
        
        for container_name in containers_to_backup:
            try:
                count = export_container_data(container_name, backup_dir)
                total_documents += count
            except Exception as e:
                print(f"❌ Error exporting {container_name}: {e}")
        
        # Create backup manifest
        manifest = {
            "backup_timestamp": timestamp,
            "backup_directory": backup_dir,
            "containers_backed_up": containers_to_backup,
            "total_documents": total_documents,
            "database_name": os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality'),
            "backup_purpose": "Pre-migration data preservation"
        }
        
        manifest_file = os.path.join(backup_dir, "backup_manifest.json")
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n🎉 BACKUP COMPLETED")
        print(f"📊 Total documents backed up: {total_documents}")
        print(f"📁 Backup location: {backup_dir}")
        print(f"📋 Manifest: {manifest_file}")
        print(f"\n⚠️ CRITICAL: Keep this backup safe until migration is fully validated!")
        
        return backup_dir

    if __name__ == "__main__":
        main()

except ImportError:
    print("❌ Error: azure-cosmos package not installed")
    print("Run: pip install azure-cosmos")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
