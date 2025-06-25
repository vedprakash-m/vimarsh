#!/usr/bin/env python3
"""
Comprehensive PWA Testing Suite Runner
Executes all PWA-related tests and generates detailed reports.
"""

import sys
import json
import time
from pathlib import Path

# Add the tests directory to the path
sys.path.append(str(Path(__file__).parent))

# Import test modules
from test_pwa_features import run_pwa_tests
from test_pwa_offline import run_offline_tests


def run_comprehensive_pwa_tests():
    """Run all PWA tests and generate comprehensive report"""
    
    print("🚀 VIMARSH PWA COMPREHENSIVE TESTING SUITE")
    print("=" * 80)
    print("Testing Progressive Web App features, offline capabilities,")
    print("and spiritual guidance accessibility for the Vimarsh platform.")
    print("=" * 80)
    print()
    
    start_time = time.time()
    all_results = {}
    
    # Test 1: Core PWA Features
    print("📱 Phase 1: Core PWA Features Testing")
    print("-" * 50)
    try:
        pwa_success = run_pwa_tests()
        all_results["core_pwa_features"] = {
            "success": pwa_success,
            "phase": "Core PWA Features",
            "tested_features": [
                "PWA Manifest validation",
                "Service Worker registration", 
                "Caching strategies",
                "Install prompts",
                "Performance metrics"
            ]
        }
        print(f"✅ Core PWA Features: {'PASSED' if pwa_success else 'FAILED'}")
    except Exception as e:
        print(f"❌ Core PWA Features FAILED: {str(e)}")
        all_results["core_pwa_features"] = {
            "success": False,
            "error": str(e),
            "phase": "Core PWA Features"
        }
    
    print("\n" + "=" * 80 + "\n")
    
    # Test 2: Offline Behavior & Installation
    print("🔌 Phase 2: Offline Behavior & Installation Testing")
    print("-" * 50)
    try:
        offline_results = run_offline_tests()
        offline_success = offline_results["success_rate"] >= 80
        all_results["offline_behavior"] = {
            **offline_results,
            "success": offline_success,
            "phase": "Offline Behavior & Installation"
        }
        print(f"✅ Offline Behavior: {'PASSED' if offline_success else 'FAILED'}")
    except Exception as e:
        print(f"❌ Offline Behavior FAILED: {str(e)}")
        all_results["offline_behavior"] = {
            "success": False,
            "error": str(e),
            "phase": "Offline Behavior & Installation"
        }
    
    print("\n" + "=" * 80 + "\n")
    
    # Calculate overall results
    end_time = time.time()
    total_duration = end_time - start_time
    
    successful_phases = sum(1 for result in all_results.values() if result.get("success", False))
    total_phases = len(all_results)
    overall_success_rate = (successful_phases / total_phases) * 100
    
    # Generate summary
    print("📊 COMPREHENSIVE PWA TESTING SUMMARY")
    print("=" * 60)
    print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
    print(f"🎯 Overall Success Rate: {overall_success_rate:.1f}%")
    print(f"✅ Successful Phases: {successful_phases}/{total_phases}")
    print()
    
    # Detailed phase results
    print("📋 Phase-by-Phase Results:")
    for phase_key, result in all_results.items():
        status = "✅ PASSED" if result.get("success", False) else "❌ FAILED" 
        phase_name = result.get("phase", phase_key)
        print(f"   {status} {phase_name}")
        
        if "tested_features" in result:
            print(f"     Features: {len(result['tested_features'])} tested")
        
        if "success_rate" in result:
            print(f"     Success Rate: {result['success_rate']:.1f}%")
        
        if "error" in result:
            print(f"     Error: {result['error']}")
    
    print()
    
    # PWA Readiness Assessment
    print("🔍 PWA READINESS ASSESSMENT")
    print("=" * 40)
    
    readiness_checks = {
        "Manifest Valid": all_results.get("core_pwa_features", {}).get("success", False),
        "Service Worker": all_results.get("core_pwa_features", {}).get("success", False),
        "Offline Capable": all_results.get("offline_behavior", {}).get("success", False),
        "Installable": all_results.get("offline_behavior", {}).get("success", False),
    }
    
    for check, passed in readiness_checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    
    ready_for_production = all(readiness_checks.values())
    print()
    print(f"🚀 Production Ready: {'YES' if ready_for_production else 'NO'}")
    
    if not ready_for_production:
        print("\n⚠️  Issues to resolve before production:")
        for check, passed in readiness_checks.items():
            if not passed:
                print(f"   • {check} needs attention")
    
    print()
    
    # Spiritual Content PWA Features
    print("🕉️  SPIRITUAL CONTENT PWA FEATURES")
    print("=" * 45)
    spiritual_features = [
        "📿 Offline access to sacred texts and wisdom",
        "🎯 Cached spiritual guidance for seekers",
        "🔤 Sanskrit font support for Devanagari text",
        "🗣️  Voice interface with pronunciation support",
        "💾 Conversation history preserved offline",
        "🔄 Background sync for spiritual conversations",
        "📱 Native app-like experience for spiritual seekers",
        "🌐 Progressive enhancement for all devices"
    ]
    
    for feature in spiritual_features:
        print(f"   {feature}")
    
    print()
    
    # Generate detailed JSON report
    comprehensive_report = {
        "test_suite": "Vimarsh PWA Comprehensive Testing",
        "timestamp": time.time(),
        "duration_seconds": total_duration,
        "overall_success_rate": overall_success_rate,
        "production_ready": ready_for_production,
        "phase_results": all_results,
        "readiness_checks": readiness_checks,
        "spiritual_pwa_features": [
            "Offline sacred text access",
            "Cached spiritual guidance", 
            "Sanskrit font support",
            "Voice interface optimization",
            "Conversation preservation",
            "Background sync",
            "Native app experience"
        ],
        "recommendations": [
            "Test on real mobile devices",
            "Verify app store compatibility", 
            "Test with various network conditions",
            "Validate accessibility compliance",
            "Optimize cache size and performance"
        ] if not ready_for_production else [
            "PWA is ready for production deployment",
            "Consider A/B testing install prompts",
            "Monitor offline usage analytics",
            "Gather user feedback on app experience"
        ]
    }
    
    # Save comprehensive report
    report_path = Path(__file__).parent.parent.parent / "pwa_comprehensive_test_report.json"
    with open(report_path, 'w') as f:
        json.dump(comprehensive_report, f, indent=2)
    
    # Create markdown summary
    markdown_report = generate_markdown_report(comprehensive_report)
    markdown_path = Path(__file__).parent.parent.parent / "pwa_test_summary.md"
    with open(markdown_path, 'w') as f:
        f.write(markdown_report)
    
    print(f"📄 Comprehensive report: {report_path}")
    print(f"📄 Summary report: {markdown_path}")
    print()
    
    # Final verdict
    if ready_for_production:
        print("🎉 VIMARSH PWA IS READY FOR PRODUCTION!")
        print("   The Progressive Web App features are working correctly")
        print("   and provide excellent offline spiritual guidance experience.")
    else:
        print("⚠️  PWA NEEDS IMPROVEMENT BEFORE PRODUCTION")
        print("   Some features require attention before deployment.")
    
    return ready_for_production, comprehensive_report


def generate_markdown_report(report_data):
    """Generate markdown summary report"""
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(report_data["timestamp"]))
    
    markdown = f"""# Vimarsh PWA Testing Summary

**Generated:** {timestamp}  
**Duration:** {report_data['duration_seconds']:.2f} seconds  
**Overall Success Rate:** {report_data['overall_success_rate']:.1f}%  
**Production Ready:** {'✅ YES' if report_data['production_ready'] else '❌ NO'}

## Test Phases

"""
    
    for phase_key, result in report_data["phase_results"].items():
        status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
        phase_name = result.get("phase", phase_key)
        markdown += f"### {status} {phase_name}\n\n"
        
        if "success_rate" in result:
            markdown += f"- **Success Rate:** {result['success_rate']:.1f}%\n"
        
        if "tested_features" in result:
            markdown += f"- **Features Tested:** {len(result['tested_features'])}\n"
            for feature in result['tested_features']:
                markdown += f"  - {feature}\n"
        
        if "error" in result:
            markdown += f"- **Error:** {result['error']}\n"
        
        markdown += "\n"
    
    markdown += """## PWA Readiness Checklist

"""
    
    for check, passed in report_data["readiness_checks"].items():
        status = "✅" if passed else "❌"
        markdown += f"- {status} {check}\n"
    
    markdown += f"""

## Spiritual Content PWA Features

"""
    
    for feature in report_data["spiritual_pwa_features"]:
        markdown += f"- 🕉️ {feature}\n"
    
    markdown += f"""

## Recommendations

"""
    
    for rec in report_data["recommendations"]:
        markdown += f"- {rec}\n"
    
    return markdown


if __name__ == "__main__":
    success, report = run_comprehensive_pwa_tests()
    exit(0 if success else 1)
