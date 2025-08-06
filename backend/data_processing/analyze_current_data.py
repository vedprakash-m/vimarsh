#!/usr/bin/env python3
"""Analyze current data structure for migration planning"""

import os
import sys
import json
from dotenv import load_dotenv
from datetime import datetime

# Add the parent directory to sys.path to import from backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from root .env
load_dotenv('../../.env')

try:
    from azure.cosmos import CosmosClient
    
    # Get connection string
    connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
    client = CosmosClient.from_connection_string(connection_string)
    
    # Get database
    database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
    database = client.get_database_client(database_name)
    
    print("📊 CURRENT DATABASE ANALYSIS FOR MIGRATION PLANNING")
    print("=" * 80)
    
    # Analyze personality-vectors container
    print("\n1️⃣ PERSONALITY-VECTORS CONTAINER ANALYSIS")
    print("-" * 50)
    
    vectors_container = database.get_container_client('personality-vectors')
    
    # Get personality distribution
    personality_query = """
    SELECT c.personality, COUNT(1) as count
    FROM c 
    GROUP BY c.personality
    """
    
    personality_stats = list(vectors_container.query_items(
        query=personality_query, 
        enable_cross_partition_query=True
    ))
    
    print("Current personality distribution:")
    total_vectors = 0
    for stat in personality_stats:
        count = stat['count']
        total_vectors += count
        print(f"  {stat['personality']}: {count:,} documents")
    
    print(f"Total vector documents: {total_vectors:,}")
    
    # Check embedding status
    embedding_query = """
    SELECT 
        COUNT(1) as total,
        SUM(CASE WHEN c.has_embedding = true THEN 1 ELSE 0 END) as with_embeddings,
        SUM(CASE WHEN c.has_embedding = false OR NOT IS_DEFINED(c.has_embedding) THEN 1 ELSE 0 END) as without_embeddings
    FROM c
    """
    
    embedding_stats = list(vectors_container.query_items(
        query=embedding_query, 
        enable_cross_partition_query=True
    ))[0]
    
    print(f"\nEmbedding status:")
    print(f"  With embeddings: {embedding_stats['with_embeddings']:,}")
    print(f"  Without embeddings: {embedding_stats['without_embeddings']:,}")
    
    # Get sample document for schema analysis
    sample_query = "SELECT TOP 1 * FROM c WHERE c.personality = 'krishna'"
    sample_docs = list(vectors_container.query_items(query=sample_query))
    
    if sample_docs:
        sample = sample_docs[0]
        print(f"\nSample document schema:")
        for key, value in sample.items():
            if not key.startswith('_'):
                value_type = type(value).__name__
                if isinstance(value, list) and value:
                    if key == 'embedding':
                        print(f"  {key}: {value_type} (length: {len(value)})")
                    else:
                        print(f"  {key}: {value_type} (sample: {value[0] if len(str(value[0])) < 50 else str(value[0])[:50] + '...'})")
                elif isinstance(value, str) and len(value) > 50:
                    print(f"  {key}: {value_type} ('{value[:50]}...')")
                else:
                    print(f"  {key}: {value_type} ({value})")
    
    # Analyze users container
    print("\n\n2️⃣ USERS CONTAINER ANALYSIS")
    print("-" * 50)
    
    users_container = database.get_container_client('users')
    
    users_count_query = "SELECT VALUE COUNT(1) FROM c"
    users_count = list(users_container.query_items(query=users_count_query, enable_cross_partition_query=True))[0]
    print(f"Total users: {users_count}")
    
    # Get sample user for schema analysis
    sample_user_query = "SELECT TOP 1 * FROM c"
    sample_users = list(users_container.query_items(query=sample_user_query, enable_cross_partition_query=True))
    
    if sample_users:
        user = sample_users[0]
        print(f"\nUser document schema:")
        for key, value in user.items():
            if not key.startswith('_'):
                value_type = type(value).__name__
                if isinstance(value, dict):
                    print(f"  {key}: {value_type} (keys: {list(value.keys())[:5]})")
                elif isinstance(value, list):
                    print(f"  {key}: {value_type} (length: {len(value)})")
                elif isinstance(value, str) and len(value) > 50:
                    print(f"  {key}: {value_type} ('{value[:50]}...')")
                else:
                    print(f"  {key}: {value_type} ({value})")
    
    # Analyze user_activity container
    print("\n\n3️⃣ USER_ACTIVITY CONTAINER ANALYSIS")
    print("-" * 50)
    
    activity_container = database.get_container_client('user_activity')
    
    activity_count_query = "SELECT VALUE COUNT(1) FROM c"
    activity_count = list(activity_container.query_items(query=activity_count_query, enable_cross_partition_query=True))[0]
    print(f"Total user activity documents: {activity_count}")
    
    # Get document types distribution
    doc_types_query = """
    SELECT c.document_type, COUNT(1) as count
    FROM c 
    GROUP BY c.document_type
    """
    
    doc_types = list(activity_container.query_items(
        query=doc_types_query, 
        enable_cross_partition_query=True
    ))
    
    print(f"\nDocument type distribution:")
    for doc_type in doc_types:
        print(f"  {doc_type['document_type']}: {doc_type['count']}")
    
    # Get sample activity document
    sample_activity_query = "SELECT TOP 1 * FROM c"
    sample_activities = list(activity_container.query_items(query=sample_activity_query, enable_cross_partition_query=True))
    
    if sample_activities:
        activity = sample_activities[0]
        print(f"\nActivity document schema:")
        for key, value in activity.items():
            if not key.startswith('_'):
                value_type = type(value).__name__
                if isinstance(value, dict):
                    print(f"  {key}: {value_type} (keys: {list(value.keys())[:5]})")
                elif isinstance(value, list):
                    print(f"  {key}: {value_type} (length: {len(value)})")
                elif isinstance(value, str) and len(value) > 50:
                    print(f"  {key}: {value_type} ('{value[:50]}...')")
                else:
                    print(f"  {key}: {value_type} ({value})")
    
    print("\n\n4️⃣ MIGRATION ASSESSMENT")
    print("-" * 50)
    print("✅ Data to preserve:")
    print(f"   - {total_vectors:,} personality vector documents with embeddings")
    print(f"   - {users_count} user profiles with preferences and stats")
    print(f"   - {activity_count} user activity records")
    
    print("\n⚠️ Critical considerations:")
    print("   - personality-vectors container has 6,514 documents - MUST preserve all")
    print("   - Current partition key is '/personality' - will change to hierarchical")
    print("   - All embeddings must be preserved - re-generation would be expensive")
    print("   - User data and activity history must be preserved")
    
    print("\n🔄 Required transformations:")
    print("   - personality-vectors → personality_vectors (new partition key)")
    print("   - Extract personality configs from vectors into new personalities container")
    print("   - Split user_activity into user_sessions and user_interactions")
    print("   - Create new analytics containers with aggregated data")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
