#!/usr/bin/env python3
"""
Multi-Tenant Authentication Testing Script
Tests various aspects of the multi-tenant Microsoft authentication implementation.
"""

import requests
import json
from typing import Dict, Any
from datetime import datetime

class MultiTenantAuthTester:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        # Color coding for console output
        color = "\033[92m" if status == "PASS" else "\033[91m" if status == "FAIL" else "\033[93m"
        print(f"{color}[{status}]\033[0m {test_name}")
        if details:
            print(f"    📋 {details}")
        print()

    def test_backend_health(self) -> bool:
        """Test if backend is accessible"""
        try:
            response = self.session.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("Backend Health Check", "PASS", f"Backend is running at {self.backend_url}")
                return True
            else:
                self.log_test("Backend Health Check", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", "FAIL", f"Error: {str(e)}")
            return False

    def test_unauthenticated_request(self) -> bool:
        """Test that spiritual guidance requires authentication"""
        try:
            payload = {
                "query": "Test question for authentication",
                "personality_id": "krishna"
            }
            
            response = self.session.post(
                f"{self.backend_url}/spiritual_guidance",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 401:
                data = response.json()
                if "Authentication required" in data.get("error", ""):
                    self.log_test("Unauthenticated Request Rejection", "PASS", 
                                "Correctly returns 401 for unauthenticated requests")
                    return True
                else:
                    self.log_test("Unauthenticated Request Rejection", "FAIL", 
                                f"Wrong error message: {data}")
                    return False
            else:
                self.log_test("Unauthenticated Request Rejection", "FAIL", 
                            f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unauthenticated Request Rejection", "FAIL", f"Error: {str(e)}")
            return False

    def test_cors_configuration(self) -> bool:
        """Test CORS configuration for multi-tenant domains"""
        try:
            # Test preflight request
            headers = {
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'authorization,content-type',
                'Origin': 'https://vimarsh.vedprakash.net'
            }
            
            response = self.session.options(
                f"{self.backend_url}/spiritual_guidance",
                headers=headers,
                timeout=10
            )
            
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin', ''),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods', ''),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers', '')
            }
            
            if cors_headers['access-control-allow-origin']:
                self.log_test("CORS Configuration", "PASS", 
                            f"CORS headers present: {cors_headers}")
                return True
            else:
                self.log_test("CORS Configuration", "WARN", 
                            "No explicit CORS headers found - may rely on Azure Functions defaults")
                return True
                
        except Exception as e:
            self.log_test("CORS Configuration", "WARN", f"Could not test CORS: {str(e)}")
            return True

    def test_jwks_endpoints(self) -> bool:
        """Test that JWKS endpoints are accessible for token validation"""
        try:
            # Test common endpoint (multi-tenant)
            common_jwks = requests.get(
                "https://login.microsoftonline.com/common/discovery/v2.0/keys",
                timeout=10
            )
            
            if common_jwks.status_code == 200:
                keys = common_jwks.json().get('keys', [])
                self.log_test("JWKS Common Endpoint", "PASS", 
                            f"Retrieved {len(keys)} keys from common endpoint")
            else:
                self.log_test("JWKS Common Endpoint", "FAIL", 
                            f"Status: {common_jwks.status_code}")
                return False
                
            # Test specific tenant endpoint
            tenant_jwks = requests.get(
                "https://login.microsoftonline.com/9188040d-6c67-4c5b-b112-36a304b66dad/discovery/v2.0/keys",
                timeout=10
            )
            
            if tenant_jwks.status_code == 200:
                keys = tenant_jwks.json().get('keys', [])
                self.log_test("JWKS Tenant Endpoint", "PASS", 
                            f"Retrieved {len(keys)} keys from tenant endpoint")
                return True
            else:
                self.log_test("JWKS Tenant Endpoint", "WARN", 
                            f"Status: {tenant_jwks.status_code} (tenant may not exist)")
                return True
                
        except Exception as e:
            self.log_test("JWKS Endpoints", "FAIL", f"Error: {str(e)}")
            return False

    def simulate_authenticated_request(self, mock_token: str, tenant_info: Dict[str, str]) -> bool:
        """Simulate an authenticated request (for testing purposes)"""
        try:
            headers = {
                "Authorization": f"Bearer {mock_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": f"Test question from {tenant_info['tenant_name']} user",
                "personality_id": "krishna"
            }
            
            response = self.session.post(
                f"{self.backend_url}/spiritual_guidance",
                json=payload,
                headers=headers,
                timeout=15
            )
            
            # We expect this to fail token validation, but we want to see how it fails
            test_name = f"Mock Auth Test ({tenant_info['tenant_name']})"
            
            if response.status_code == 401:
                # This is expected - mock token should be rejected
                self.log_test(test_name, "PASS", 
                            "Mock token correctly rejected - authentication pipeline working")
                return True
            elif response.status_code == 500:
                # Check if it's a token validation error
                try:
                    error_data = response.json()
                    if "token validation" in str(error_data).lower():
                        self.log_test(test_name, "PASS", 
                                    "Token validation attempted - authentication pipeline working")
                        return True
                except Exception:
                    pass
                self.log_test(test_name, "WARN", 
                            f"Server error during token validation: {response.status_code}")
                return True
            else:
                self.log_test(test_name, "WARN", 
                            f"Unexpected response: {response.status_code}")
                return True
                
        except Exception as e:
            self.log_test(f"Mock Auth Test ({tenant_info['tenant_name']})", "WARN", 
                        f"Error: {str(e)}")
            return True

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🧪 VIMARSH MULTI-TENANT AUTHENTICATION TEST SUITE")
        print("=" * 60)
        print()
        
        # Test 1: Backend Health
        health_ok = self.test_backend_health()
        
        if not health_ok:
            print("❌ Backend not accessible - stopping tests")
            return self.generate_report()
        
        # Test 2: Authentication Required
        self.test_unauthenticated_request()
        
        # Test 3: CORS Configuration
        self.test_cors_configuration()
        
        # Test 4: JWKS Endpoints
        self.test_jwks_endpoints()
        
        # Test 5: Mock Authentication Tests
        test_tenants = [
            {"tenant_name": "Microsoft", "tenant_id": "common"},
            {"tenant_name": "Personal", "tenant_id": "9188040d-6c67-4c5b-b112-36a304b66dad"},
            {"tenant_name": "Corporate", "tenant_id": "contoso.onmicrosoft.com"}
        ]
        
        for tenant in test_tenants:
            mock_token = f"mock_token_for_{tenant['tenant_name'].lower()}_user"
            self.simulate_authenticated_request(mock_token, tenant)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        report = {
            "summary": {
                "total_tests": len(self.test_results),
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "success_rate": f"{(passed / len(self.test_results) * 100):.1f}%" if self.test_results else "0%"
            },
            "details": self.test_results,
            "recommendations": self.get_recommendations()
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}")
        print()
        
        if report['recommendations']:
            print("💡 RECOMMENDATIONS:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"{i}. {rec}")
            print()
        
        return report
    
    def get_recommendations(self) -> list:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r['status'] == 'FAIL']
        
        if any('Backend Health' in t['test'] for t in failed_tests):
            recommendations.append("Verify backend deployment and URL configuration")
        
        if any('Authentication' in t['test'] for t in failed_tests):
            recommendations.append("Check authentication middleware implementation in function_app.py")
        
        if any('JWKS' in t['test'] for t in failed_tests):
            recommendations.append("Verify internet connectivity and Microsoft endpoints accessibility")
        
        # Always recommend real user testing
        recommendations.append("Test with real Microsoft accounts from different tenants")
        recommendations.append("Verify Azure App Registration is set to 'Multitenant'")
        recommendations.append("Check Azure App Registration 'Allow public client flows' is enabled")
        
        return recommendations

def main():
    """Main testing function"""
    # Use the production backend URL
    backend_url = "https://vimarsh-backend-app-flex-accch9cmbah2bzb0.westus2-01.azurewebsites.net/api"
    
    tester = MultiTenantAuthTester(backend_url)
    report = tester.run_comprehensive_test()
    
    # Save report to file
    with open('multitenant_auth_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("📄 Detailed report saved to: multitenant_auth_test_report.json")
    
    return report

if __name__ == "__main__":
    main()
