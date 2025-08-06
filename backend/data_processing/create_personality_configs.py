#!/usr/bin/env python3
"""
Create personality configurations from migrated vector data
Extracts unique personalities and creates configuration documents
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
    
    def create_personality_configs():
        """Extract and create personality configurations"""
        print("👑 CREATING PERSONALITY CONFIGURATIONS")
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
        vectors_container = database.get_container_client('personality_vectors')
        personalities_container = database.get_container_client('personalities')
        
        # Get unique personalities from vector data
        print("🔍 Analyzing personality data from vectors...")
        
        query = """
        SELECT DISTINCT c.personality_id
        FROM c 
        WHERE IS_DEFINED(c.personality_id) AND c.personality_id != null
        """
        
        unique_personalities = []
        for item in vectors_container.query_items(query=query, enable_cross_partition_query=True):
            personality_id = item['personality_id']
            if personality_id and personality_id not in unique_personalities:
                unique_personalities.append(personality_id)
        
        print(f"📊 Found {len(unique_personalities)} unique personalities: {unique_personalities}")
        
        # Pre-defined personality configurations
        personality_configs = {
            "krishna": {
                "display_name": "Lord Krishna",
                "domain": "spiritual",
                "description": "Divine guide from Hindu traditions, emphasizing dharma, karma yoga, and devotion",
                "system_prompt": "I am Krishna, the divine charioteer from the Bhagavad Gita. I guide souls toward their highest dharma through wisdom, compassion, and divine love. My teachings emphasize selfless action, devotion, and the eternal truth that transcends material existence.",
                "cultural_context": "hindu",
                "foundational_texts": ["bhagavad_gita", "srimad_bhagavatam", "mahabharata"],
                "core_teachings": ["dharma", "karma_yoga", "bhakti", "detachment", "divine_love"],
                "personality_traits": ["wise", "compassionate", "playful", "divine", "protective"]
            },
            "rama": {
                "display_name": "Lord Rama",
                "domain": "spiritual",
                "description": "Ideal king and avatar representing righteousness, duty, and moral excellence",
                "system_prompt": "I am Rama, the ideal king and embodiment of dharma. I guide through principles of righteousness, duty, and moral excellence, showing the path of honor and virtue.",
                "cultural_context": "hindu",
                "foundational_texts": ["ramayana", "valmiki_ramayana"],
                "core_teachings": ["dharma", "duty", "righteousness", "honor", "devotion"],
                "personality_traits": ["righteous", "dutiful", "noble", "gentle", "steadfast"]
            },
            "hanuman": {
                "display_name": "Lord Hanuman",
                "domain": "spiritual",
                "description": "Divine devotee representing strength, courage, and unwavering devotion",
                "system_prompt": "I am Hanuman, the devoted servant of Lord Rama. I embody strength, courage, and unwavering devotion. I guide through challenges with fearless determination and pure bhakti.",
                "cultural_context": "hindu",
                "foundational_texts": ["ramayana", "hanuman_chalisa"],
                "core_teachings": ["devotion", "courage", "strength", "service", "humility"],
                "personality_traits": ["devoted", "strong", "humble", "fearless", "protective"]
            },
            "shiva": {
                "display_name": "Lord Shiva",
                "domain": "spiritual",
                "description": "The destroyer and transformer, representing cosmic consciousness and spiritual liberation",
                "system_prompt": "I am Shiva, the cosmic dancer and destroyer of illusion. I guide through transformation, meditation, and the realization of ultimate truth beyond form.",
                "cultural_context": "hindu",
                "foundational_texts": ["shiva_purana", "vigyan_bhairav_tantra"],
                "core_teachings": ["meditation", "transformation", "detachment", "cosmic_consciousness"],
                "personality_traits": ["transcendent", "meditative", "powerful", "ascetic", "transformative"]
            },
            "devi": {
                "display_name": "Divine Mother",
                "domain": "spiritual",
                "description": "The universal mother representing divine feminine energy, protection, and nurturing wisdom",
                "system_prompt": "I am the Divine Mother, the universal source of love and protection. I guide with nurturing wisdom, fierce protection when needed, and unconditional maternal love.",
                "cultural_context": "hindu",
                "foundational_texts": ["devi_mahatmya", "lalita_sahasranama"],
                "core_teachings": ["divine_feminine", "protection", "nurturing", "empowerment"],
                "personality_traits": ["nurturing", "protective", "powerful", "loving", "wise"]
            }
            # Add more as needed based on discovered personalities
        }
        
        created_count = 0
        
        # Create personality configuration documents
        for personality_id in unique_personalities:
            try:
                if personality_id in personality_configs:
                    config = personality_configs[personality_id]
                else:
                    # Create default config for unknown personalities
                    config = {
                        "display_name": personality_id.title(),
                        "domain": "spiritual",
                        "description": f"Spiritual guide from {personality_id} tradition",
                        "system_prompt": f"I am {personality_id.title()}, offering guidance from ancient wisdom.",
                        "cultural_context": "hindu",
                        "foundational_texts": ["unknown"],
                        "core_teachings": ["wisdom", "guidance"],
                        "personality_traits": ["wise", "compassionate"]
                    }
                
                # Get associated sources for this personality
                sources_query = f"""
                SELECT DISTINCT c.source
                FROM c 
                WHERE c.personality_id = '{personality_id}'
                """
                
                sources = []
                for source_item in vectors_container.query_items(query=sources_query, enable_cross_partition_query=True):
                    sources.append(source_item['source'])
                
                # Create the configuration document
                doc = {
                    "id": f"personality_{personality_id}",
                    "partition_key": personality_id,
                    "personality_id": personality_id,
                    "document_type": "personality_config",
                    **config,
                    "associated_sources": sources,
                    "is_active": True,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "updated_at": datetime.utcnow().isoformat() + "Z"
                }
                
                personalities_container.create_item(doc)
                print(f"✅ Created personality config: {personality_id} (sources: {len(sources)})")
                created_count += 1
                
            except Exception as e:
                print(f"❌ Error creating config for {personality_id}: {e}")
        
        print(f"\n🎉 PERSONALITY CONFIGURATIONS COMPLETED")
        print("=" * 50)
        print(f"✅ Created: {created_count} personality configurations")
        print(f"📊 From: {len(unique_personalities)} unique personalities")
        
        return created_count > 0
    
    def validate_personality_configs():
        """Validate personality configurations"""
        print("\n🔍 VALIDATING PERSONALITY CONFIGURATIONS")
        print("-" * 50)
        
        # Get connection
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        client = CosmosClient.from_connection_string(connection_string)
        database_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'vimarsh-multi-personality')
        database = client.get_database_client(database_name)
        
        personalities_container = database.get_container_client('personalities')
        
        try:
            # Count configurations
            count_query = "SELECT VALUE COUNT(1) FROM c"
            count_result = list(personalities_container.query_items(query=count_query, enable_cross_partition_query=True))
            count = count_result[0] if count_result else 0
            
            print(f"📊 Total personality configurations: {count}")
            
            if count == 0:
                print("❌ No personality configurations found!")
                return False
            
            # Sample configurations
            sample_query = "SELECT c.personality_id, c.display_name, c.domain FROM c"
            samples = list(personalities_container.query_items(query=sample_query, enable_cross_partition_query=True))
            
            print("📋 Created configurations:")
            for sample in samples:
                print(f"   • {sample['personality_id']}: {sample['display_name']} ({sample['domain']})")
            
            print("✅ Personality configurations validation passed")
            return True
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
    
    def main():
        """Main function"""
        success = create_personality_configs()
        
        if success:
            validation_success = validate_personality_configs()
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
