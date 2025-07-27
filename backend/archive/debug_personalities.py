#!/usr/bin/env python3
"""
Debug personality IDs and check what's available
"""

import asyncio
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.personality_service import personality_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_personalities():
    """Debug available personalities"""
    logger.info("🔍 Debugging available personalities...")
    
    try:
        personalities = await personality_service.get_active_personalities()
        
        logger.info(f"Found {len(personalities)} personalities:")
        for personality in personalities:
            logger.info(f"  ID: {personality.id}")
            logger.info(f"  Name: {personality.name}")
            logger.info(f"  Display Name: {personality.display_name}")
            logger.info(f"  Domain: {personality.domain.value}")
            logger.info(f"  Description: {personality.description[:100]}...")
            logger.info("  ---")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_personalities())