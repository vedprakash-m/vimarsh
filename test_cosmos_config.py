#!/usr/bin/env python3
"""
Quick test script to check Cosmos DB configuration
"""
import os
import requests
import json

def test_azure_function_cosmos_config():
    """Test the Azure Function's Cosmos DB configuration"""
    print("🧪 Testing Azure Function Cosmos DB Configuration")
    print("=" * 60)
    
    try:
        # Test the health endpoint
        health_url = "https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net/api/health"
        response = requests.get(health_url, timeout=30)
        
        if response.status_code == 200:
            health_data = response.json()
            
            print(f"✅ Health endpoint responded: {response.status_code}")
            print(f"📊 Overall status: {health_data.get('overall_status', 'unknown')}")
            print(f"📈 Deployment readiness: {health_data.get('deployment_readiness', 'unknown')}")
            
            # Check vector search specifically
            vector_search = health_data.get('services', {}).get('vector_search', {})
            print("\n🔍 Vector Search Service:")
            print(f"   Available: {vector_search.get('available', False)}")
            print(f"   Status: {vector_search.get('status', 'unknown')}")
            print(f"   Error: {vector_search.get('error_message', 'none')}")
            
            # Show health details
            health_details = vector_search.get('health_details', {})
            if health_details:
                print("   Health Details:")
                for key, value in health_details.items():
                    print(f"     {key}: {value}")
            
            # Test a simple guidance request to see if Cosmos DB is working
            print("\n🤖 Testing Guidance API (should work even without vector search):")
            guidance_url = "https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net/api/guidance"
            guidance_payload = {
                "query": "What is dharma?",
                "personality_id": "krishna",
                "language": "English"
            }
            
            guidance_response = requests.post(
                guidance_url, 
                json=guidance_payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            print(f"   Status: {guidance_response.status_code}")
            if guidance_response.status_code == 200:
                guidance_data = guidance_response.json()
                response_source = guidance_data.get('metadata', {}).get('response_source', 'unknown')
                print(f"   Response source: {response_source}")
                print(f"   Response length: {len(guidance_data.get('response', ''))}")
                print("   ✅ Guidance API working")
            else:
                print(f"   ❌ Guidance API failed: {guidance_response.text[:200]}")
            
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")

if __name__ == "__main__":
    test_azure_function_cosmos_config()
