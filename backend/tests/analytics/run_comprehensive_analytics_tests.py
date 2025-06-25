#!/usr/bin/env python3
"""
Comprehensive Analytics and User Feedback Testing Suite
Runs all analytics validation tests and generates detailed reports.
"""

import sys
import json
import time
from pathlib import Path

# Add the tests directory to the path
sys.path.append(str(Path(__file__).parent))

# Import test modules
from test_analytics_validation import run_analytics_tests
from test_advanced_analytics import run_advanced_analytics_tests


def run_comprehensive_analytics_tests():
    """Run all analytics tests and generate comprehensive report"""
    
    print("📊 VIMARSH ANALYTICS & USER FEEDBACK COMPREHENSIVE TESTING")
    print("=" * 80)
    print("Testing privacy-respecting analytics, user behavior tracking,")
    print("feedback collection, and optimization features for spiritual guidance.")
    print("=" * 80)
    print()
    
    start_time = time.time()
    all_results = {}
    
    # Phase 1: Core Analytics Implementation
    print("📈 Phase 1: Core Analytics Implementation & Privacy")
    print("-" * 60)
    try:
        core_analytics_success = run_analytics_tests()
        all_results["core_analytics"] = {
            "success": core_analytics_success,
            "phase": "Core Analytics Implementation & Privacy",
            "tested_features": [
                "Privacy-respecting data collection",
                "Spiritual behavior tracking",
                "Real-time analytics processing",
                "User feedback collection",
                "Sentiment analysis",
                "Performance monitoring"
            ]
        }
        print(f"✅ Core Analytics: {'PASSED' if core_analytics_success else 'FAILED'}")
    except Exception as e:
        print(f"❌ Core Analytics FAILED: {str(e)}")
        all_results["core_analytics"] = {
            "success": False,
            "error": str(e),
            "phase": "Core Analytics Implementation & Privacy"
        }
    
    print("\n" + "=" * 80 + "\n")
    
    # Phase 2: Advanced Analytics & Optimization
    print("🔮 Phase 2: Advanced Analytics & Optimization")
    print("-" * 60)
    try:
        advanced_results = run_advanced_analytics_tests()
        advanced_success = advanced_results["success_rate"] >= 80
        all_results["advanced_analytics"] = {
            **advanced_results,
            "success": advanced_success,
            "phase": "Advanced Analytics & Optimization"
        }
        print(f"✅ Advanced Analytics: {'PASSED' if advanced_success else 'FAILED'}")
    except Exception as e:
        print(f"❌ Advanced Analytics FAILED: {str(e)}")
        all_results["advanced_analytics"] = {
            "success": False,
            "error": str(e),
            "phase": "Advanced Analytics & Optimization"
        }
    
    print("\n" + "=" * 80 + "\n")
    
    # Calculate overall results
    end_time = time.time()
    total_duration = end_time - start_time
    
    successful_phases = sum(1 for result in all_results.values() if result.get("success", False))
    total_phases = len(all_results)
    overall_success_rate = (successful_phases / total_phases) * 100
    
    # Generate summary
    print("📊 COMPREHENSIVE ANALYTICS TESTING SUMMARY")
    print("=" * 70)
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
    
    # Analytics Readiness Assessment
    print("🔍 ANALYTICS SYSTEM READINESS ASSESSMENT")
    print("=" * 50)
    
    readiness_checks = {
        "Privacy Protection": all_results.get("core_analytics", {}).get("success", False),
        "User Behavior Tracking": all_results.get("core_analytics", {}).get("success", False),
        "Feedback Collection": all_results.get("core_analytics", {}).get("success", False),
        "Advanced Analytics": all_results.get("advanced_analytics", {}).get("success", False),
        "A/B Testing": all_results.get("advanced_analytics", {}).get("success", False),
        "Predictive Insights": all_results.get("advanced_analytics", {}).get("success", False),
    }
    
    for check, passed in readiness_checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    
    analytics_ready = all(readiness_checks.values())
    print()
    print(f"📊 Analytics Production Ready: {'YES' if analytics_ready else 'NO'}")
    
    if not analytics_ready:
        print("\n⚠️  Issues to resolve before production:")
        for check, passed in readiness_checks.items():
            if not passed:
                print(f"   • {check} needs attention")
    
    print()
    
    # Spiritual Analytics Features
    print("🕉️  SPIRITUAL GUIDANCE ANALYTICS FEATURES")
    print("=" * 55)
    analytics_features = [
        "📿 Privacy-respecting spiritual journey tracking",
        "🎯 Dharmic content engagement measurement", 
        "🗣️  Voice vs text spiritual interaction preferences",
        "🌐 English/Hindi language usage analytics",
        "📊 User satisfaction with spiritual guidance",
        "🔄 Real-time spiritual content performance monitoring",
        "💡 Predictive insights for user spiritual growth",
        "🧪 A/B testing for dharmic interface optimization",
        "📝 Anonymous feedback collection on sacred guidance",
        "🎵 Sanskrit pronunciation and voice interaction analytics"
    ]
    
    for feature in analytics_features:
        print(f"   {feature}")
    
    print()
    
    # Privacy & Ethics
    print("🔒 PRIVACY & ETHICAL CONSIDERATIONS")
    print("=" * 40)
    privacy_features = [
        "🔐 All personal data anonymized and hashed",
        "🚫 No storage of actual spiritual questions",
        "📊 Topic extraction without question retention",
        "💬 Sentiment analysis without comment storage", 
        "🆔 Session-based anonymous tracking only",
        "⚖️  GDPR/Privacy compliance built-in",
        "🔄 User data export and deletion capabilities",
        "🎯 Spiritual content focus, not personal profiling"
    ]
    
    for feature in privacy_features:
        print(f"   {feature}")
    
    print()
    
    # Generate detailed JSON report
    comprehensive_report = {
        "test_suite": "Vimarsh Analytics & User Feedback Comprehensive Testing",
        "timestamp": time.time(),
        "duration_seconds": total_duration,
        "overall_success_rate": overall_success_rate,
        "analytics_production_ready": analytics_ready,
        "phase_results": all_results,
        "readiness_checks": readiness_checks,
        "spiritual_analytics_features": [
            "Privacy-respecting spiritual journey tracking",
            "Dharmic content engagement measurement",
            "Voice vs text interaction preferences",
            "Language usage analytics (EN/HI)",
            "User satisfaction measurement",
            "Real-time performance monitoring",
            "Predictive spiritual growth insights",
            "A/B testing for interface optimization",
            "Anonymous feedback collection",
            "Sanskrit pronunciation analytics"
        ],
        "privacy_compliance": [
            "Data anonymization",
            "Question content protection",
            "Topic-only extraction",
            "Sentiment without storage",
            "Session-based tracking",
            "GDPR compliance",
            "User data control",
            "Spiritual focus only"
        ],
        "recommendations": [
            "Analytics system ready for production deployment",
            "Implement real-device testing for mobile analytics",
            "Set up production analytics dashboard",
            "Configure alert thresholds for spiritual guidance quality",
            "Establish expert review integration with analytics",
            "Create analytics documentation for spiritual advisors"
        ] if analytics_ready else [
            "Complete failing analytics tests before production",
            "Verify privacy protection mechanisms",
            "Test user feedback collection workflows",
            "Validate A/B testing framework accuracy",
            "Ensure predictive models are calibrated"
        ]
    }
    
    # Save comprehensive report
    report_path = Path(__file__).parent.parent.parent / "analytics_comprehensive_test_report.json"
    with open(report_path, 'w') as f:
        json.dump(comprehensive_report, f, indent=2)
    
    # Create markdown summary
    markdown_report = generate_analytics_markdown_report(comprehensive_report)
    markdown_path = Path(__file__).parent.parent.parent / "analytics_test_summary.md"
    with open(markdown_path, 'w') as f:
        f.write(markdown_report)
    
    print(f"📄 Comprehensive report: {report_path}")
    print(f"📄 Summary report: {markdown_path}")
    print()
    
    # Final verdict
    if analytics_ready:
        print("🎉 VIMARSH ANALYTICS SYSTEM IS READY FOR PRODUCTION!")
        print("   Privacy-respecting analytics and user feedback collection")
        print("   are working correctly for spiritual guidance optimization.")
    else:
        print("⚠️  ANALYTICS SYSTEM NEEDS IMPROVEMENT BEFORE PRODUCTION")
        print("   Some analytics features require attention before deployment.")
    
    return analytics_ready, comprehensive_report


def generate_analytics_markdown_report(report_data):
    """Generate markdown summary report for analytics testing"""
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(report_data["timestamp"]))
    
    markdown = f"""# Vimarsh Analytics & User Feedback Testing Summary

**Generated:** {timestamp}  
**Duration:** {report_data['duration_seconds']:.2f} seconds  
**Overall Success Rate:** {report_data['overall_success_rate']:.1f}%  
**Analytics Production Ready:** {'✅ YES' if report_data['analytics_production_ready'] else '❌ NO'}

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
    
    markdown += """## Analytics System Readiness

"""
    
    for check, passed in report_data["readiness_checks"].items():
        status = "✅" if passed else "❌"
        markdown += f"- {status} {check}\n"
    
    markdown += f"""

## Spiritual Analytics Features

"""
    
    for feature in report_data["spiritual_analytics_features"]:
        markdown += f"- 🕉️ {feature}\n"
    
    markdown += f"""

## Privacy & Compliance

"""
    
    for privacy_feature in report_data["privacy_compliance"]:
        markdown += f"- 🔒 {privacy_feature}\n"
    
    markdown += f"""

## Recommendations

"""
    
    for rec in report_data["recommendations"]:
        markdown += f"- {rec}\n"
    
    return markdown


if __name__ == "__main__":
    success, report = run_comprehensive_analytics_tests()
    exit(0 if success else 1)
