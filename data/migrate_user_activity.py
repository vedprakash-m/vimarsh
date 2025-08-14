#!/usr/bin/env python3
"""
Migrate user_activity data to user_sessions and user_interactions
Splits the 121 activity records into separate containers
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from root .env
load_dotenv('../../.env')

try:
    from azure.cosmos import CosmosClient
    
    def migrate_user_activity():
        """Split user_activity into user_sessions and user_interactions"""
        print("🔄 MIGRATING USER ACTIVITY DATA")
        print("=" * 60)
        
        # Get connection
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            print("❌ AZURE_COSMOS_CONNECTION_STRING not found")
            return False
        
        client = CosmosClient.from_connection_string(connection_string)
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        database = client.get_database_client(database_name)
        
        # Get containers
        source_container = database.get_container_client('user_activity')
        sessions_container = database.get_container_client('user_sessions')
        interactions_container = database.get_container_client('user_interactions')
        
        session_count = 0
        interaction_count = 0
        other_count = 0
        
        print("📦 Processing user activity documents...")
        
        try:
            # Query all documents from source
            query = "SELECT * FROM c"
            
            for doc in source_container.query_items(query=query, enable_cross_partition_query=True):
                doc_type = doc.get('document_type', '').lower()
                
                try:
                    if 'session' in doc_type or doc.get('session_data'):
                        # Migrate to user_sessions
                        session_doc = transform_session_document(doc)
                        sessions_container.create_item(session_doc)
                        session_count += 1
                        
                    elif 'interaction' in doc_type or doc.get('interaction_data') or doc.get('conversation_data'):
                        # Migrate to user_interactions
                        interaction_doc = transform_interaction_document(doc)
                        interactions_container.create_item(interaction_doc)
                        interaction_count += 1
                        
                    else:
                        # Create as interaction by default (most user_activity seems to be interactions)
                        interaction_doc = transform_generic_activity_document(doc)
                        interactions_container.create_item(interaction_doc)
                        interaction_count += 1
                        
                except Exception as e:
                    print(f"❌ Error migrating document {doc.get('id', 'unknown')}: {e}")
                    other_count += 1
            
            print(f"\n🎉 USER ACTIVITY MIGRATION COMPLETED")
            print("=" * 50)
            print(f"✅ Sessions created: {session_count}")
            print(f"✅ Interactions created: {interaction_count}")
            print(f"❌ Errors: {other_count}")
            print(f"📊 Total processed: {session_count + interaction_count + other_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Critical error during migration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def transform_session_document(old_doc):
        """Transform user activity document to session format"""
        session_data = old_doc.get('session_data', {})
        
        new_doc = {
            "id": old_doc['id'],
            "partition_key": old_doc.get('user_id', 'unknown'),
            "user_id": old_doc.get('user_id', 'unknown'),
            "document_type": "user_session",
            "session_id": session_data.get('session_id', old_doc['id']),
            "start_time": session_data.get('start_time', old_doc.get('timestamp')),
            "end_time": session_data.get('end_time'),
            "duration_seconds": session_data.get('duration_seconds'),
            "platform": session_data.get('platform', 'web'),
            "device_info": session_data.get('device_info', {}),
            "location": session_data.get('location'),
            "ip_address": session_data.get('ip_address'),
            "user_agent": session_data.get('user_agent'),
            "interactions_count": session_data.get('interactions_count', 0),
            "session_quality": session_data.get('session_quality', 'good'),
            "created_at": old_doc.get('created_at', old_doc.get('timestamp')),
            "updated_at": old_doc.get('updated_at', old_doc.get('timestamp')),
            "_ttl": 7776000  # 90 days
        }
        
        # Remove None values
        return {k: v for k, v in new_doc.items() if v is not None}
    
    def transform_interaction_document(old_doc):
        """Transform user activity document to interaction format"""
        interaction_data = old_doc.get('interaction_data', {})
        conversation_data = old_doc.get('conversation_data', {})
        
        new_doc = {
            "id": old_doc['id'],
            "partition_key": old_doc.get('user_id', 'unknown'),
            "user_id": old_doc.get('user_id', 'unknown'),
            "document_type": "user_interaction",
            "interaction_id": interaction_data.get('interaction_id', old_doc['id']),
            "session_id": interaction_data.get('session_id', old_doc.get('session_id')),
            "timestamp": old_doc.get('timestamp'),
            "personality_id": interaction_data.get('personality_id', conversation_data.get('personality_id', 'krishna')),
            "interaction_type": interaction_data.get('interaction_type', 'chat'),
            "user_input": interaction_data.get('user_input', conversation_data.get('user_input', old_doc.get('user_input'))),
            "ai_response": interaction_data.get('ai_response', conversation_data.get('ai_response', old_doc.get('ai_response'))),
            "response_time_ms": interaction_data.get('response_time_ms'),
            "user_feedback": interaction_data.get('user_feedback'),
            "feedback_rating": interaction_data.get('feedback_rating'),
            "content_flags": interaction_data.get('content_flags', []),
            "context_data": interaction_data.get('context_data', conversation_data),
            "created_at": old_doc.get('created_at', old_doc.get('timestamp')),
            "updated_at": old_doc.get('updated_at', old_doc.get('timestamp')),
            "_ttl": 15552000  # 180 days
        }
        
        # Remove None values
        return {k: v for k, v in new_doc.items() if v is not None}
    
    def transform_generic_activity_document(old_doc):
        """Transform generic activity document to interaction format"""
        new_doc = {
            "id": old_doc['id'],
            "partition_key": old_doc.get('user_id', 'unknown'),
            "user_id": old_doc.get('user_id', 'unknown'),
            "document_type": "user_interaction",
            "interaction_id": old_doc['id'],
            "session_id": old_doc.get('session_id'),
            "timestamp": old_doc.get('timestamp'),
            "personality_id": old_doc.get('personality_id', 'krishna'),
            "interaction_type": old_doc.get('activity_type', 'chat'),
            "user_input": old_doc.get('user_input'),
            "ai_response": old_doc.get('ai_response'),
            "context_data": {
                "original_activity_type": old_doc.get('activity_type'),
                "original_document_type": old_doc.get('document_type'),
                "migrated_from": "user_activity"
            },
            "created_at": old_doc.get('created_at', old_doc.get('timestamp')),
            "updated_at": old_doc.get('updated_at', old_doc.get('timestamp')),
            "_ttl": 15552000  # 180 days
        }
        
        # Include any additional fields from original document
        for key, value in old_doc.items():
            if key not in new_doc and not key.startswith('_'):
                if new_doc.get('context_data') is None:
                    new_doc['context_data'] = {}
                new_doc['context_data'][f'original_{key}'] = value
        
        # Remove None values
        return {k: v for k, v in new_doc.items() if v is not None}
    
    def validate_migration():
        """Validate the migration was successful"""
        print("\n🔍 VALIDATING USER ACTIVITY MIGRATION")
        print("-" * 50)
        
        # Get connection
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        client = CosmosClient.from_connection_string(connection_string)
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        database = client.get_database_client(database_name)
        
        source_container = database.get_container_client('user_activity')
        sessions_container = database.get_container_client('user_sessions')
        interactions_container = database.get_container_client('user_interactions')
        
        try:
            # Count documents
            count_query = "SELECT VALUE COUNT(1) FROM c"
            
            source_count_result = list(source_container.query_items(query=count_query, enable_cross_partition_query=True))
            source_count = source_count_result[0] if source_count_result else 0
            
            sessions_count_result = list(sessions_container.query_items(query=count_query, enable_cross_partition_query=True))
            sessions_count = sessions_count_result[0] if sessions_count_result else 0
            
            interactions_count_result = list(interactions_container.query_items(query=count_query, enable_cross_partition_query=True))
            interactions_count = interactions_count_result[0] if interactions_count_result else 0
            
            total_migrated = sessions_count + interactions_count
            
            print(f"📊 Source (user_activity): {source_count} documents")
            print(f"📊 Sessions: {sessions_count} documents")
            print(f"📊 Interactions: {interactions_count} documents")
            print(f"📊 Total migrated: {total_migrated} documents")
            
            if total_migrated >= source_count:
                print("✅ All user activity data migrated successfully!")
                return True
            else:
                print(f"⚠️ Some data may not have migrated (missing: {source_count - total_migrated})")
                return False
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
    
    def main():
        """Main migration function"""
        success = migrate_user_activity()
        
        if success:
            validation_success = validate_migration()
            return validation_success
        else:
            return False

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
