#!/usr/bin/env python3
"""
Update personality IDs to use simple names for easier reference
"""

import asyncio
import logging
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.personality_service import personality_service, PersonalitySearchFilter
from services.database_service import db_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_personality_ids():
    """Update personality IDs to simple names"""
    
    # Get all personalities
    personalities = await personality_service.search_personalities(
        PersonalitySearchFilter()
    )
    
    logger.info(f"Found {len(personalities)} personalities")
    
    # Map current personalities to simple IDs
    id_mapping = {}
    for personality in personalities:
        if 'krishna' in personality.name.lower():
            id_mapping[personality.id] = 'krishna'
        elif 'einstein' in personality.name.lower():
            id_mapping[personality.id] = 'einstein'
        elif 'lincoln' in personality.name.lower():
            id_mapping[personality.id] = 'lincoln'
        elif 'marcus' in personality.name.lower() or 'aurelius' in personality.name.lower():
            id_mapping[personality.id] = 'marcus_aurelius'
    
    logger.info(f"ID mapping: {id_mapping}")
    
    # Create new personalities with simple IDs
    for old_id, new_id in id_mapping.items():
        old_personality = await personality_service.get_personality(old_id)
        if old_personality:
            # Create new personality data with simple ID
            personality_data = {
                'id': new_id,
                'name': old_personality.name,
                'display_name': old_personality.display_name,
                'domain': old_personality.domain.value,
                'time_period': old_personality.time_period,
                'description': old_personality.description,
                'tone_characteristics': old_personality.tone_characteristics,
                'vocabulary_preferences': old_personality.vocabulary_preferences,
                'response_patterns': old_personality.response_patterns,
                'expertise_areas': old_personality.expertise_areas,
                'cultural_context': old_personality.cultural_context,
                'language_style': old_personality.language_style,
                'system_prompt': old_personality.system_prompt,
                'is_active': True,
                'status': 'active'
            }
            
            try:
                new_personality = await personality_service.create_personality(
                    personality_data, 'system_update'
                )
                logger.info(f"✅ Created personality with simple ID: {new_id}")
                
                # Archive old personality
                await personality_service.delete_personality(old_id, 'system_update')
                logger.info(f"✅ Archived old personality: {old_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to update personality {old_id} -> {new_id}: {e}")

if __name__ == "__main__":
    asyncio.run(update_personality_ids())