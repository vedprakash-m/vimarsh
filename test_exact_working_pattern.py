#!/usr/bin/env python3
"""
Test with the exact working pattern from our earlier success
"""

import os
import google.generativeai as genai

# Use the exact same API key
api_key = "AIzaSyBNWBue7HKe4NYnYr4kyaijx_D0YThfPOc"

# Configure exactly as before
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# Use the exact same prompt that worked
query = "How can I find inner peace?"
prompt = f"""You are Lord Krishna from the Bhagavad Gita. Answer this spiritual question: {query}

Provide wisdom in Krishna's voice, starting with 'My beloved devotee,'"""

print("🧪 Testing with exact working pattern...")
print(f"Query: {query}")
print(f"Prompt: {prompt}")

try:
    response = model.generate_content(prompt)
    
    print(f"\n📝 Response object: {response}")
    
    if response:
        print(f"📝 Response text: {repr(response.text)}")
        print(f"📝 Response candidates: {response.candidates}")
        
        if hasattr(response, 'prompt_feedback'):
            print(f"📝 Prompt feedback: {response.prompt_feedback}")
            
        if response.text:
            print(f"\n✅ SUCCESS! Got response: {response.text}")
        else:
            print(f"\n⚠️ Response object exists but text is empty")
    else:
        print(f"\n❌ No response object returned")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"❌ Error type: {type(e).__name__}")
