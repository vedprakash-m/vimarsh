#!/usr/bin/env python3
"""
Demo script for AI Cost Analytics Dashboard
Demonstrates cost tracking, trend analysis, and optimization recommendations
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from cost_management.analytics_dashboard import CostAnalyticsDashboard, ReportType
    print("✅ Successfully imported analytics dashboard")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def main():
    """Run the analytics dashboard demo"""
    print("🎯 Vimarsh AI Cost Analytics Dashboard Demo")
    print("=" * 60)
    
    try:
        # Initialize dashboard
        dashboard = CostAnalyticsDashboard("data/demo_analytics")
        print("✅ Analytics dashboard initialized")
        
        # Add sample cost data
        print("\n📊 Adding sample cost data...")
        sample_data = [
            ("user_vedprakash", "gemini-pro", 0.0045, 1500, "spiritual_guidance"),
            ("user_devotee1", "gemini-flash", 0.0012, 1200, "voice_response"),
            ("user_vedprakash", "gemini-flash", 0.0008, 800, "spiritual_guidance"),
            ("user_expert", "gemini-pro", 0.0055, 1800, "expert_review"),
            ("user_devotee2", "gemini-flash", 0.0009, 900, "spiritual_guidance"),
            ("user_devotee1", "gemini-pro", 0.0040, 1400, "spiritual_guidance"),
        ]
        
        for user_id, model, cost, tokens, operation in sample_data:
            await dashboard.add_cost_record(
                user_id=user_id,
                model=model,
                cost=cost,
                tokens=tokens,
                operation_type=operation
            )
        
        print(f"✅ Added {len(sample_data)} cost records")
        
        # Generate cost metrics
        print("\n💰 Cost Metrics Analysis")
        print("-" * 30)
        metrics = await dashboard.generate_cost_metrics()
        
        print(f"📈 Total Cost: ${metrics.total_cost:.4f}")
        print(f"⚡ Total Operations: {metrics.operation_count}")
        print(f"💸 Average Cost/Operation: ${metrics.average_cost_per_operation:.4f}")
        print(f"🎯 Efficiency Score: {metrics.efficiency_score:.1f}/100")
        print(f"🤖 Cost by Model:")
        for model, cost in metrics.cost_by_model.items():
            print(f"   - {model}: ${cost:.4f}")
        print(f"👥 Cost by User:")
        for user, cost in metrics.cost_by_user.items():
            print(f"   - {user}: ${cost:.4f}")
        
        # Analyze trends
        print("\n📈 Trend Analysis")
        print("-" * 20)
        trends = await dashboard.analyze_trends(period_days=7)
        
        print(f"📊 Growth Rate: {trends.growth_rate:.1f}%")
        print(f"📉 Trend Direction: {trends.trend_direction}")
        print(f"🎯 Confidence Level: {trends.confidence_level:.1f}%")
        print(f"🔄 Seasonal Pattern: {'Yes' if trends.seasonal_pattern else 'No'}")
        if trends.anomalies_detected:
            print(f"⚠️  Anomalies Detected: {len(trends.anomalies_detected)}")
        
        # Generate optimization recommendations
        print("\n💡 Optimization Recommendations")
        print("-" * 35)
        recommendations = await dashboard.generate_optimization_recommendations(metrics)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec.recommendation}")
                print(f"   💰 Potential Savings: ${rec.potential_savings:.4f}")
                print(f"   🎯 Priority: {rec.priority}/5")
                print(f"   🔧 Effort: {rec.implementation_effort}")
                print(f"   📋 Impact: {rec.impact_description}")
        else:
            print("✅ No specific optimizations needed - system is running efficiently!")
        
        # Generate comprehensive dashboard report
        print("\n📋 Dashboard Report Generation")
        print("-" * 32)
        report = await dashboard.generate_dashboard_report(ReportType.DAILY)
        
        print(f"📊 Report Type: {report['report_type']}")
        print(f"📅 Period: {report['period']['duration_days']} day(s)")
        print(f"💰 Total Cost: ${report['summary']['total_cost']:.4f}")
        print(f"⚡ Operations: {report['summary']['operations']}")
        print(f"🎯 Efficiency: {report['summary']['efficiency_score']:.1f}/100")
        print(f"📈 Growth Rate: {report['summary']['growth_rate']:.1f}%")
        print(f"💡 Recommendations: {len(report['recommendations'])}")
        print(f"💾 Potential Total Savings: ${report['summary']['potential_savings']:.4f}")
        
        print("\n" + "=" * 60)
        print("✅ Analytics dashboard demo completed successfully!")
        print("🎯 Ready for Task 7.10 completion!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
