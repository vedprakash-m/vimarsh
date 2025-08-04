#!/usr/bin/env python3
"""
Test specific personalities that should have different responses
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

# Import the functions after setting up the mock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from function_app import guidance_endpoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_specific_personalities():
    """Test the specific personalities that should have different responses"""
    
    query = "What is the meaning of life?"
    
    # Test the personalities that should have specific fallback responses
    personalities_to_test = [
        ('krishna', 'Lord Krishna'),
        ('einstein', 'Albert Einstein'),
        ('marcus_aurelius', 'Marcus Aurelius'),
        ('lincoln', 'Abraham Lincoln')  # This might not exist but let's test
    ]
    
    for personality_id, personality_name in personalities_to_test:
        logger.info(f"\n🧠 Testing {personality_name} (ID: {personality_id})...")
        
        try:
            # Create mock request
            request_data = {
                "query": query,
                "language": "English",
                "personality_id": personality_id
            }
            
            mock_request = MockHttpRequest(request_data)
            
            # Call the API function
            response = await guidance_endpoint(mock_request)
            
            # Parse response
            response_data = json.loads(response.get_body().decode('utf-8'))
            
            logger.info(f"✅ Status: {response.status_code}")
            logger.info(f"📝 Response: {response_data['response'][:200]}...")
            logger.info(f"🎯 Confidence: {response_data['metadata']['confidence']}")
            
        except Exception as e:
            logger.error(f"❌ Error testing {personality_id}: {e}")

if __name__ == "__main__":
    asyncio.run(test_specific_personalities())