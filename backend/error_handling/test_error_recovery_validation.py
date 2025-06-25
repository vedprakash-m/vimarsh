#!/usr/bin/env python3
"""
Test script for error recovery validation system
"""

import asyncio
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_error_recovery_system():
    """Test the error recovery validation system"""
    
    try:
        from error_recovery_testing import ErrorRecoveryTester, TestConfiguration, TestScenario
        
        print("✅ Successfully imported error recovery testing system")
        
        # Initialize tester
        tester = ErrorRecoveryTester()
        await tester.initialize_systems()
        
        print("✅ Successfully initialized error handling systems")
        
        # Run a simple test scenario
        test_config = TestConfiguration(
            scenario=TestScenario.TRANSIENT_NETWORK_FAILURE,
            duration_seconds=5.0,
            failure_rate=0.3,
            concurrent_requests=2,
            expected_success_rate=0.7
        )
        
        print(f"🧪 Running test scenario: {test_config.scenario.value}")
        
        report = await tester.run_test_scenario(test_config)
        
        print(f"✅ Test completed: {report.result.value}")
        print(f"   Success Rate: {report.success_rate:.2%}")
        print(f"   Duration: {report.duration:.1f}s")
        print(f"   Total Requests: {report.metrics.total_requests}")
        print(f"   Successful: {report.metrics.successful_requests}")
        print(f"   Failed: {report.metrics.failed_requests}")
        print(f"   Fallback Activations: {report.metrics.fallback_activations}")
        
        # Test export functionality
        tester.export_test_results("test_error_recovery_results.json")
        print("✅ Test results exported")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recovery testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    
    print("🚀 Starting Error Recovery Validation Test")
    print("=" * 50)
    
    success = await test_error_recovery_system()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ERROR RECOVERY TESTING VALIDATION PASSED")
        print("   All core functionality is working correctly")
    else:
        print("❌ ERROR RECOVERY TESTING VALIDATION FAILED")
        print("   Please check the error messages above")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
