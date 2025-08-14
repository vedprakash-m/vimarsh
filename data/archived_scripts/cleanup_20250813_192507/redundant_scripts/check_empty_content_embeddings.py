#!/usr/bin/env python3
"""
Check for entries with embeddings but empty content
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_empty_content_with_embeddings():
    """Check for entries that have embeddings but empty or minimal content"""
    try:
        from azure.cosmos import CosmosClient
        
        # Use connection string approach (more reliable)
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ AZURE_COSMOS_CONNECTION_STRING not found")
            return
        
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client('vimarsh-multi-personality')
        container = database.get_container_client('personality_vectors')
        
        print("🔍 Checking for entries with embeddings but empty/minimal content...")
        print("=" * 70)
        
        # Query for entries with embeddings but problematic content
        problematic_query = """
        SELECT c.id, c.personality, c.content, c.has_embedding, c.title, c.source, c.keywords
        FROM c 
        WHERE c.has_embedding = true 
        AND (IS_NULL(c.content) OR c.content = "" OR LENGTH(c.content) < 20)
        """
        
        problematic_entries = list(container.query_items(
            query=problematic_query,
            enable_cross_partition_query=True
        ))
        
        print(f"📊 Found {len(problematic_entries)} entries with embeddings but problematic content")
        
        if len(problematic_entries) == 0:
            print("✅ All entries with embeddings have substantial content!")
            
            # Let's also check the reverse - entries with good content but no embeddings
            missing_embeddings_query = """
            SELECT c.personality, COUNT(1) as count
            FROM c 
            WHERE (c.has_embedding = false OR IS_NULL(c.has_embedding) OR NOT IS_DEFINED(c.has_embedding))
            AND IS_DEFINED(c.content) AND LENGTH(c.content) > 20
            GROUP BY c.personality
            """
            
            missing_embeddings = list(container.query_items(
                query=missing_embeddings_query,
                enable_cross_partition_query=True
            ))
            
            if missing_embeddings:
                print("\n📈 Entries with good content but missing embeddings:")
                total_missing = 0
                for item in missing_embeddings:
                    count = item['count']
                    total_missing += count
                    print(f"  {item['personality']}: {count} entries")
                print(f"  TOTAL: {total_missing} entries need embeddings")
            else:
                print("✅ All entries with good content have embeddings!")
            
            return
        
        # Analyze problematic entries by personality
        by_personality = {}
        for entry in problematic_entries:
            personality = entry.get('personality', 'Unknown')
            if personality not in by_personality:
                by_personality[personality] = []
            by_personality[personality].append(entry)
        
        print("\n🎭 Problematic entries by personality:")
        for personality, entries in by_personality.items():
            print(f"\n  {personality}: {len(entries)} entries")
            
            # Show examples
            for i, entry in enumerate(entries[:3], 1):
                content = entry.get('content', '')
                if content is None:
                    content_preview = "NULL"
                elif content == "":
                    content_preview = "EMPTY STRING"
                else:
                    content_preview = f'"{content[:50]}..."'
                
                print(f"    {i}. ID: {entry.get('id', 'N/A')[:25]}...")
                print(f"       Content: {content_preview}")
                print(f"       Title: {entry.get('title', 'N/A')}")
                print(f"       Source: {entry.get('source', 'N/A')}")
        
        print(f"\n⚠️  IMPACT ASSESSMENT:")
        print(f"  • {len(problematic_entries)} entries have embeddings but poor content")
        print(f"  • This could lead to poor user experience when these entries are retrieved")
        print(f"  • Users might get responses that reference empty or minimal content")
        print(f"  • These entries should be either:")
        print(f"    1. Fixed with proper content, or")
        print(f"    2. Removed from the database")
        
        # Check if any of these entries were recently added
        recent_entries = [e for e in problematic_entries if e.get('integration_date') == '2025-08-12']
        if recent_entries:
            print(f"\n🚨 WARNING: {len(recent_entries)} problematic entries were added recently (2025-08-12)")
            print("  This suggests an issue with the recent content processing pipeline")
        
        return problematic_entries
        
    except Exception as e:
        logger.error(f"Error checking entries: {str(e)}")
        raise

if __name__ == "__main__":
    check_empty_content_with_embeddings()
