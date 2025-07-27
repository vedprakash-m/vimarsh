#!/usr/bin/env python3
"""
Ultra Simple Krishna Service - Direct Gemini API call
This strips away ALL complexity and just makes a simple API call
"""

import os
import logging
import google.generativeai as genai
import asyncio

logger = logging.getLogger(__name__)

# Test direct API call
async def test_direct_gemini_call():
    """Test direct Gemini API call"""
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-5:]}")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Simple prompt
        prompt = """You are Lord Krishna. A devotee asks: "How can I find inner peace?"

Respond in 50 words with a Bhagavad Gita teaching."""
        
        # Generate response
        print("🤖 Calling Gemini API...")
        response = model.generate_content(prompt)
        
        if response and response.text:
            print("✅ SUCCESS! Got real AI response:")
            print("-" * 50)
            print(response.text)
            print("-" * 50)
            return True
        else:
            print("❌ No response text")
            return False
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    asyncio.run(test_direct_gemini_call())
