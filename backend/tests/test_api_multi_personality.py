#!/usr/bin/env python3
"""
Test API endpoint with multi-personality support
"""

import asyncio
import json
import logging
from unittest.mock import Mock

# Mock Azure Functions request
class MockHttpRequest:
    def __init__(self, body_data):
        self.body_data = body_data
        self.headers = {
            'x-user-id': 'test_user',
            'x-user-email': 'test@example.com',
            'x-session-id': 'test_session'
        }
    
    def get_body(self):
        return json.dumps(self.body_data).encode('utf-8')
    
    def get_json(self):
        return self.body_data

# Import the function after setting up the mock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from function_app import guidance_endpoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_api_personalities():
    """Test API with different personalities"""
    
    query = "What is the meaning of life?"
    personalities = [
        ('krishna', 'Lord Krishna'),
        ('einstein', 'Albert Einstein'),
        ('marcus_aurelius', 'Marcus Aurelius')
    ]
    
    for personality_id, personality_name in personalities:
        logger.info(f"\n🧠 Testing API with {personality_name}...")
        
        # Create mock request
        request_data = {
            "query": query,
            "language": "English",
            "personality_id": personality_id
        }
        
        mock_request = MockHttpRequest(request_data)
        
        try:
            # Call the API function
            response = await guidance_endpoint(mock_request)
            
            # Parse response
            response_data = json.loads(response.get_body().decode('utf-8'))
            
            logger.info(f"✅ Status: {response.status_code}")
            logger.info(f"📝 Response: {response_data['response'][:150]}...")
            logger.info(f"🎯 Confidence: {response_data['metadata']['confidence']}")
            
        except Exception as e:
            logger.error(f"❌ Error testing {personality_id}: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_personalities())