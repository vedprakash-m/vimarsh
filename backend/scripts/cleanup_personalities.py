"""
Cleanup Duplicate Personalities

This script removes duplicate personalities and fixes domain classifications.
"""

import asyncio
import logging
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.personality_service import personality_service
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)


async def cleanup_personalities():
    """Clean up duplicate personalities"""
    print("🧹 Cleaning up personalities...")
    
    db_service = DatabaseService()
    
    # Load all personality configs
    data = db_service._load_from_local_file(db_service.conversations_path)
    
    # Find personality configs
    personality_configs = [item for item in data if item.get('type') == 'personality_config']
    
    print(f"Found {len(personality_configs)} personality configs")
    
    # Group by personality name to find duplicates
    personality_groups = {}
    for config in personality_configs:
        # Use display name for grouping to catch variations
        display_name = config.get('displayName', config.get('personalityName', '')).lower()
        # Normalize names
        if 'krishna' in display_name:
            key = 'krishna'
        elif 'einstein' in display_name:
            key = 'einstein'
        elif 'lincoln' in display_name:
            key = 'lincoln'
        elif 'marcus' in display_name or 'aurelius' in display_name:
            key = 'marcus_aurelius'
        elif 'buddha' in display_name:
            key = 'buddha'
        elif 'jesus' in display_name:
            key = 'jesus'
        elif 'lao' in display_name or 'tzu' in display_name:
            key = 'lao_tzu'
        elif 'rumi' in display_name:
            key = 'rumi'
        else:
            key = display_name
            
        if key not in personality_groups:
            personality_groups[key] = []
        personality_groups[key].append(config)
    
    # Remove duplicates (keep the most recent one)
    cleaned_configs = []
    for name, configs in personality_groups.items():
        if len(configs) > 1:
            print(f"Found {len(configs)} duplicates for {name}")
            # Sort by creation date and keep the most recent
            configs.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
            cleaned_configs.append(configs[0])
            print(f"Keeping most recent: {configs[0].get('id')}")
        else:
            cleaned_configs.append(configs[0])
    
    # Update domain classifications
    domain_mapping = {
        'krishna': 'spiritual',
        'einstein': 'scientific', 
        'lincoln': 'historical',
        'marcus_aurelius': 'philosophical',
        'buddha': 'spiritual',
        'jesus': 'spiritual',
        'lao_tzu': 'philosophical',
        'rumi': 'spiritual'
    }
    
    for config in cleaned_configs:
        name = config.get('personalityName', '').lower()
        for key, domain in domain_mapping.items():
            if key in name:
                config['domain'] = domain
                break
    
    # Remove personality configs from original data
    other_data = [item for item in data if item.get('type') != 'personality_config']
    
    # Add cleaned configs back
    final_data = other_data + cleaned_configs
    
    # Save cleaned data
    db_service._save_to_local_file(db_service.conversations_path, final_data)
    
    print(f"✅ Cleanup complete! Reduced from {len(personality_configs)} to {len(cleaned_configs)} personalities")
    
    # Show final list
    print("\n📋 Final personality list:")
    for config in cleaned_configs:
        name = config.get('displayName', config.get('personalityName', 'Unknown'))
        domain = config.get('domain', 'unknown')
        active = config.get('isActive', False)
        print(f"   - {name} ({domain}) - Active: {active}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(cleanup_personalities())