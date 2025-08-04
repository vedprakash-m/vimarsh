#!/usr/bin/env python3
"""
Download Personality Data from Production Cosmos DB

This script connects to the production Cosmos DB and downloads all personality
content to local JSON files for development use.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Any

# Load environment variables
root_env_path = Path(__file__).parent.parent.parent / '.env'
if root_env_path.exists():
    load_dotenv(root_env_path)

try:
    from azure.cosmos import CosmosClient
    print("✅ Azure Cosmos SDK imported successfully")
except ImportError:
    print("❌ Azure Cosmos SDK not found. Install with: pip install azure-cosmos")
    sys.exit(1)


class PersonalityDataDownloader:
    """Download personality data from Cosmos DB to local JSON files"""
    
    def __init__(self):
        # You'll need to provide the production connection string
        self.connection_string = input("Enter production Cosmos DB connection string: ").strip()
        if not self.connection_string:
            print("❌ Connection string required")
            sys.exit(1)
            
        self.database_name = "vimarsh-multi-personality"
        self.container_name = "personality-vectors"
        self.output_dir = Path(__file__).parent.parent / "data" / "sources"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Output directory: {self.output_dir}")
    
    def connect_to_cosmos(self):
        """Connect to Cosmos DB"""
        try:
            self.client = CosmosClient.from_connection_string(self.connection_string)
            self.database = self.client.get_database_client(self.database_name)
            self.container = self.database.get_container_client(self.container_name)
            print("✅ Connected to Cosmos DB successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Cosmos DB: {e}")
            return False
    
    def get_all_personalities(self) -> List[str]:
        """Get list of all personalities in the database"""
        try:
            query = "SELECT DISTINCT c.personality FROM c"
            items = list(self.container.query_items(
                query=query, 
                enable_cross_partition_query=True
            ))
            personalities = [item['personality'] for item in items if item.get('personality')]
            print(f"📊 Found personalities: {personalities}")
            return personalities
        except Exception as e:
            print(f"❌ Error getting personalities: {e}")
            return []
    
    def download_personality_data(self, personality: str) -> List[Dict[str, Any]]:
        """Download all data for a specific personality"""
        try:
            query = f"SELECT * FROM c WHERE c.personality = '{personality}'"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            print(f"📥 Downloaded {len(items)} items for {personality}")
            return items
        except Exception as e:
            print(f"❌ Error downloading {personality} data: {e}")
            return []
    
    def save_personality_to_file(self, personality: str, data: List[Dict[str, Any]]):
        """Save personality data to JSON file"""
        try:
            # Convert to the format expected by the RAG service
            formatted_data = []
            for item in data:
                formatted_item = {
                    'text': item.get('content', ''),
                    'source': item.get('source', ''),
                    'title': item.get('title', ''),
                    'metadata': item.get('metadata', {}),
                    'personality': personality
                }
                # Add any additional fields that might be useful
                if 'verse_number' in item:
                    formatted_item['verse_number'] = item['verse_number']
                if 'chapter' in item:
                    formatted_item['chapter'] = item['chapter']
                    
                formatted_data.append(formatted_item)
            
            # Save to file
            filename = f"{personality.lower().replace(' ', '_')}_teachings.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(formatted_data)} items to {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving {personality} data: {e}")
            return False
    
    def download_all_personalities(self):
        """Download all personality data"""
        if not self.connect_to_cosmos():
            return False
        
        personalities = self.get_all_personalities()
        if not personalities:
            print("❌ No personalities found")
            return False
        
        success_count = 0
        for personality in personalities:
            print(f"\n🔄 Processing {personality}...")
            data = self.download_personality_data(personality)
            if data and self.save_personality_to_file(personality, data):
                success_count += 1
        
        print(f"\n🎉 Successfully downloaded {success_count}/{len(personalities)} personalities")
        print(f"📁 Files saved to: {self.output_dir}")
        
        # List created files
        print("\n📄 Created files:")
        for file in self.output_dir.glob("*_teachings.json"):
            size = file.stat().st_size / 1024  # KB
            print(f"  - {file.name} ({size:.1f} KB)")
        
        return success_count == len(personalities)


def main():
    print("🚀 Vimarsh Personality Data Downloader")
    print("=" * 50)
    print("This script will download all personality data from production Cosmos DB")
    print("and save it as local JSON files for development use.\\n")
    
    # Confirm action
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return
    
    downloader = PersonalityDataDownloader()
    success = downloader.download_all_personalities()
    
    if success:
        print("\\n✅ All done! You can now restart your backend with full personality data.")
    else:
        print("\\n❌ Some downloads failed. Check the errors above.")


if __name__ == "__main__":
    main()
