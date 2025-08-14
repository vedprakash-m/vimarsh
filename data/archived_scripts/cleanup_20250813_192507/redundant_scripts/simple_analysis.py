#!/usr/bin/env python3
"""Simple analysis of current data for migration planning"""

import os
import sys
from dotenv import load_dotenv
from collections import defaultdict

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
    
    print("📊 DETAILED DATABASE ANALYSIS FOR MIGRATION PLANNING")
    print("=" * 80)
    
    # Simple count queries and sampling
    containers_info = {
        'personality-vectors': {
            'partition_key': '/personality',
            'sample_query': 'SELECT TOP 5 c.id, c.personality, c.source, c.has_embedding, c.content_type FROM c'
        },
        'users': {
            'partition_key': '/partition_key',
            'sample_query': 'SELECT TOP 3 c.id, c.auth_id, c.email, c.document_type, c.account_status FROM c'
        },
        'user_activity': {
            'partition_key': '/partition_key',  
            'sample_query': 'SELECT TOP 5 c.id, c.user_id, c.document_type, c.timestamp FROM c'
        }
    }
    
    analysis_results = {}
    
    for container_name, info in containers_info.items():
        print(f"\n📦 {container_name.upper()} CONTAINER")
        print("-" * 50)
        
        try:
            container = database.get_container_client(container_name)
            
            # Get total count
            count_query = "SELECT VALUE COUNT(1) FROM c"
            total_count = list(container.query_items(
                query=count_query, 
                enable_cross_partition_query=True
            ))[0]
            
            print(f"Total documents: {total_count:,}")
            print(f"Partition key: {info['partition_key']}")
            
            # Get sample documents
            sample_docs = list(container.query_items(
                query=info['sample_query'],
                enable_cross_partition_query=True
            ))
            
            print(f"\nSample documents ({len(sample_docs)} shown):")
            for i, doc in enumerate(sample_docs, 1):
                print(f"  Document {i}:")
                for key, value in doc.items():
                    if not key.startswith('_'):
                        if isinstance(value, str) and len(value) > 40:
                            print(f"    {key}: '{value[:40]}...'")
                        elif isinstance(value, list):
                            print(f"    {key}: [list with {len(value)} items]")
                        elif isinstance(value, dict):
                            print(f"    {key}: {{dict with {len(value)} keys}}")
                        else:
                            print(f"    {key}: {value}")
                print()
            
            analysis_results[container_name] = {
                'total_documents': total_count,
                'partition_key': info['partition_key'],
                'sample_documents': sample_docs
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {container_name}: {e}")
            analysis_results[container_name] = {
                'error': str(e)
            }
    
    # Specific analysis for personality-vectors
    print(f"\n🔍 DETAILED PERSONALITY-VECTORS ANALYSIS")
    print("-" * 50)
    
    if 'personality-vectors' in analysis_results and 'error' not in analysis_results['personality-vectors']:
        vectors_container = database.get_container_client('personality-vectors')
        
        # Count personalities manually
        personality_counts = defaultdict(int)
        embedding_status = {'with_embeddings': 0, 'without_embeddings': 0}
        content_types = defaultdict(int)
        
        print("Analyzing personality distribution...")
        
        # Sample-based analysis (get 100 documents to analyze patterns)
        sample_query = "SELECT TOP 100 c.personality, c.has_embedding, c.content_type FROM c"
        sample_docs = list(vectors_container.query_items(
            query=sample_query,
            enable_cross_partition_query=True
        ))
        
        for doc in sample_docs:
            personality = doc.get('personality', 'Unknown')
            personality_counts[personality] += 1
            
            has_embedding = doc.get('has_embedding', False)
            if has_embedding:
                embedding_status['with_embeddings'] += 1
            else:
                embedding_status['without_embeddings'] += 1
            
            content_type = doc.get('content_type', 'unknown')
            content_types[content_type] += 1
        
        print(f"\nPersonality distribution (sample of {len(sample_docs)}):")
        for personality, count in sorted(personality_counts.items()):
            print(f"  {personality}: {count}")
        
        print(f"\nEmbedding status (sample):")
        print(f"  With embeddings: {embedding_status['with_embeddings']}")
        print(f"  Without embeddings: {embedding_status['without_embeddings']}")
        
        print(f"\nContent types (sample):")
        for content_type, count in sorted(content_types.items()):
            print(f"  {content_type}: {count}")
    
    # Migration assessment
    print(f"\n\n🎯 MIGRATION ASSESSMENT")
    print("=" * 50)
    
    print("Current State:")
    for container_name, info in analysis_results.items():
        if 'error' not in info:
            print(f"  ✅ {container_name}: {info['total_documents']:,} documents")
        else:
            print(f"  ❌ {container_name}: Error - {info['error']}")
    
    print(f"\nCritical Data to Preserve:")
    if 'personality-vectors' in analysis_results:
        vectors_count = analysis_results['personality-vectors'].get('total_documents', 0)
        print(f"  🔥 CRITICAL: {vectors_count:,} personality vector documents with embeddings")
    
    if 'users' in analysis_results:
        users_count = analysis_results['users'].get('total_documents', 0)
        print(f"  👥 Important: {users_count} user profiles")
    
    if 'user_activity' in analysis_results:
        activity_count = analysis_results['user_activity'].get('total_documents', 0)
        print(f"  📊 Important: {activity_count} user activity records")
    
    print(f"\nMigration Requirements:")
    print(f"  1. personality-vectors → personality_vectors (change partition key)")
    print(f"  2. Extract personality configs to new personalities container")
    print(f"  3. Split user_activity → user_sessions + user_interactions")
    print(f"  4. Create 8 new analytics containers")
    print(f"  5. Update backend/frontend code to use new schema")
    
    print(f"\n⚠️ RISK ASSESSMENT:")
    print(f"  🔴 HIGH RISK: personality-vectors has embeddings that are expensive to regenerate")
    print(f"  🟡 MEDIUM RISK: User data and activity history must be preserved")
    print(f"  🟢 LOW RISK: New analytics containers start empty")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
