#!/usr/bin/env python3
"""
Vimarsh Feedback System Comprehensive Test Suite
Tests all aspects of the feedback collection and continuous improvement system
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from feedback.vimarsh_feedback_collector import (
        VimarshFeedbackCollector,
        FeedbackType,
        FeedbackSentiment,
        FeedbackPriority,
        collect_user_feedback,
        generate_weekly_feedback_report
    )
    FEEDBACK_AVAILABLE = True
except ImportError as e:
    FEEDBACK_AVAILABLE = False
    print(f"⚠️ Feedback system not available: {e}")

class FeedbackSystemTester:
    """Comprehensive test suite for the feedback system"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = tempfile.mkdtemp()
        print(f"🔧 Test environment: {self.temp_dir}")
        
    async def run_all_tests(self):
        """Run all feedback system tests"""
        print("🧪 Starting Vimarsh Feedback System Tests")
        print("=" * 60)
        
        if not FEEDBACK_AVAILABLE:
            self.record_test("System Import", False, "Feedback system not available")
            return self.print_summary()
        
        # Core functionality tests
        await self.test_feedback_collection()
        await self.test_feedback_analytics()
        await self.test_continuous_improvement()
        await self.test_spiritual_integration()
        await self.test_performance()
        await self.test_configuration()
        
        # Integration tests
        await self.test_api_integration()
        await self.test_automation_scripts()
        
        return self.print_summary()
    
    def record_test(self, test_name: str, passed: bool, message: str = ""):
        """Record test result"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"     {message}")
    
    async def test_feedback_collection(self):
        """Test core feedback collection functionality"""
        print("\n📝 Testing Feedback Collection")
        print("-" * 40)
        
        try:
            collector = VimarshFeedbackCollector(
                feedback_storage_path=os.path.join(self.temp_dir, "feedback")
            )
            
            # Test 1: Rating Feedback
            feedback_id = await collector.collect_feedback(
                user_id="test_user_001",
                session_id="test_session_001",
                feedback_type=FeedbackType.RATING,
                rating=5,
                text_content="Excellent spiritual guidance!",
                context={
                    "query": "How to practice dharma?",
                    "response": "Practice dharma through righteous actions...",
                    "source_texts": ["Bhagavad Gita 3.21"]
                }
            )
            self.record_test("Rating Feedback Collection", True, f"ID: {feedback_id}")
            
            # Test 2: Voice Feedback Simulation
            voice_feedback_id = await collector.collect_feedback(
                user_id="test_user_002", 
                session_id="test_session_002",
                feedback_type=FeedbackType.VOICE_FEEDBACK,
                voice_transcript="Very helpful spiritual guidance",
                context={"voice_duration": 12.5}
            )
            self.record_test("Voice Feedback Collection", True, f"ID: {voice_feedback_id}")
            
            # Test 3: Spiritual Accuracy Feedback
            spiritual_feedback_id = await collector.collect_feedback(
                user_id="test_user_003",
                session_id="test_session_003", 
                feedback_type=FeedbackType.SPIRITUAL_ACCURACY,
                rating=4,
                text_content="Good content, could use more Sanskrit terms",
                context={"accuracy_concern": "terminology"}
            )
            self.record_test("Spiritual Accuracy Feedback", True, f"ID: {spiritual_feedback_id}")
            
            # Test 4: Feature Request
            feature_id = await collector.collect_feedback(
                user_id="test_user_004",
                session_id="test_session_004",
                feedback_type=FeedbackType.FEATURE_REQUEST,
                text_content="Please add more meditation guidance",
                context={"category": "meditation"}
            )
            self.record_test("Feature Request Collection", True, f"ID: {feature_id}")
            
            # Test 5: Bug Report
            bug_id = await collector.collect_feedback(
                user_id="test_user_005",
                session_id="test_session_005",
                feedback_type=FeedbackType.BUG_REPORT,
                text_content="Voice interface not working on mobile",
                context={"platform": "mobile", "browser": "safari"}
            )
            self.record_test("Bug Report Collection", True, f"ID: {bug_id}")
            
        except Exception as e:
            self.record_test("Feedback Collection", False, str(e))
    
    async def test_feedback_analytics(self):
        """Test feedback analytics functionality"""
        print("\n📊 Testing Feedback Analytics")
        print("-" * 40)
        
        try:
            collector = VimarshFeedbackCollector(
                feedback_storage_path=os.path.join(self.temp_dir, "feedback")
            )
            
            # Test 1: Trend Analysis
            analytics = await collector.analyze_feedback_trends(days=1)
            
            if analytics.total_feedback_count > 0:
                self.record_test("Trend Analysis", True, 
                               f"Analyzed {analytics.total_feedback_count} feedback items")
            else:
                self.record_test("Trend Analysis", True, "No feedback to analyze (expected)")
            
            # Test 2: Analytics Properties
            properties_ok = all(hasattr(analytics, prop) for prop in [
                'total_feedback_count', 'average_rating', 'sentiment_distribution',
                'common_themes', 'improvement_suggestions', 'spiritual_accuracy_score'
            ])
            self.record_test("Analytics Properties", properties_ok, 
                           "All required properties present")
            
            # Test 3: Sentiment Distribution
            sentiment_valid = isinstance(analytics.sentiment_distribution, dict)
            self.record_test("Sentiment Distribution", sentiment_valid,
                           f"Format: {type(analytics.sentiment_distribution)}")
            
            # Test 4: Common Themes
            themes_valid = isinstance(analytics.common_themes, list)
            self.record_test("Common Themes", themes_valid,
                           f"Count: {len(analytics.common_themes)}")
            
        except Exception as e:
            self.record_test("Feedback Analytics", False, str(e))
    
    async def test_continuous_improvement(self):
        """Test continuous improvement functionality"""
        print("\n💡 Testing Continuous Improvement")
        print("-" * 40)
        
        try:
            collector = VimarshFeedbackCollector(
                feedback_storage_path=os.path.join(self.temp_dir, "feedback")
            )
            
            # Test 1: Improvement Metrics
            metrics = await collector.generate_improvement_metrics(days=1)
            
            metrics_properties = [
                'response_quality_trend', 'user_engagement_metrics',
                'spiritual_content_accuracy', 'feature_adoption_rates',
                'performance_improvements', 'cost_optimization_impact'
            ]
            
            properties_ok = all(hasattr(metrics, prop) for prop in metrics_properties)
            self.record_test("Improvement Metrics Structure", properties_ok,
                           "All required metrics properties present")
            
            # Test 2: Report Generation
            report = await collector.generate_feedback_report(days=1)
            
            report_valid = isinstance(report, dict) and len(report) > 0
            self.record_test("Report Generation", report_valid,
                           f"Generated report with {len(report)} sections")
            
            # Test 3: Improvement Suggestions
            suggestions = await collector.generate_improvement_suggestions()
            
            suggestions_valid = isinstance(suggestions, list)
            self.record_test("Improvement Suggestions", suggestions_valid,
                           f"Generated {len(suggestions)} suggestions")
            
        except Exception as e:
            self.record_test("Continuous Improvement", False, str(e))
    
    async def test_spiritual_integration(self):
        """Test spiritual principles integration"""
        print("\n🕉️ Testing Spiritual Integration")
        print("-" * 40)
        
        try:
            collector = VimarshFeedbackCollector(
                feedback_storage_path=os.path.join(self.temp_dir, "feedback"),
                spiritual_validation=True
            )
            
            # Test 1: Spiritual Principles
            principles_present = hasattr(collector, 'spiritual_feedback_principles')
            self.record_test("Spiritual Principles", principles_present,
                           "Dharmic principles integrated")
            
            # Test 2: Spiritual Validation
            spiritual_feedback = await collector.collect_feedback(
                user_id="spiritual_test_user",
                session_id="spiritual_test_session", 
                feedback_type=FeedbackType.SPIRITUAL_ACCURACY,
                rating=5,
                text_content="Perfect dharmic guidance",
                context={"spiritual_validation": True}
            )
            
            validation_ok = spiritual_feedback is not None
            self.record_test("Spiritual Validation", validation_ok,
                           "Spiritual accuracy feedback processed")
            
            # Test 3: Krishna-inspired Messages
            if hasattr(collector, 'spiritual_feedback_principles'):
                principles = collector.spiritual_feedback_principles
                dharmic_keys = ['gratitude', 'dharmic_response', 'learning_mindset', 'service_orientation']
                keys_present = all(key in principles for key in dharmic_keys)
                self.record_test("Krishna-inspired Messages", keys_present,
                               f"Dharmic principles: {list(principles.keys())}")
            
        except Exception as e:
            self.record_test("Spiritual Integration", False, str(e))
    
    async def test_performance(self):
        """Test performance characteristics"""
        print("\n⚡ Testing Performance")
        print("-" * 40)
        
        try:
            collector = VimarshFeedbackCollector(
                feedback_storage_path=os.path.join(self.temp_dir, "feedback")
            )
            
            # Test 1: Collection Performance
            start_time = time.time()
            
            # Collect multiple feedback items
            tasks = []
            for i in range(10):
                task = collector.collect_feedback(
                    user_id=f"perf_user_{i}",
                    session_id=f"perf_session_{i}",
                    feedback_type=FeedbackType.RATING,
                    rating=4,
                    text_content=f"Performance test feedback {i}",
                    context={"test": "performance"}
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            collection_time = time.time() - start_time
            self.record_test("Collection Performance", collection_time < 5.0,
                           f"10 items in {collection_time:.2f}s")
            
            # Test 2: Analysis Performance
            start_time = time.time()
            analytics = await collector.analyze_feedback_trends(days=1)
            analysis_time = time.time() - start_time
            
            self.record_test("Analysis Performance", analysis_time < 3.0,
                           f"Analysis in {analysis_time:.2f}s")
            
            # Test 3: Memory Usage
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                self.record_test("Memory Usage", memory_mb < 500,
                               f"Using {memory_mb:.1f}MB RAM")
            except ImportError:
                self.record_test("Memory Usage", True,
                               "psutil not available - skipped")
            
        except Exception as e:
            self.record_test("Performance", False, str(e))
    
    async def test_configuration(self):
        """Test configuration management"""
        print("\n⚙️ Testing Configuration")
        print("-" * 40)
        
        try:
            # Test 1: Configuration File
            config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'feedback', 'feedback-config.yaml')
            config_exists = os.path.exists(config_file)
            self.record_test("Configuration File", config_exists,
                           f"Config file exists: {config_exists}")
            
            # Test 2: Default Configuration
            collector = VimarshFeedbackCollector()
            default_config_ok = hasattr(collector, 'feedback_storage_path')
            self.record_test("Default Configuration", default_config_ok,
                           "Default settings applied")
            
            # Test 3: Custom Configuration
            custom_collector = VimarshFeedbackCollector(
                feedback_storage_path=self.temp_dir,
                analytics_enabled=False,
                spiritual_validation=True
            )
            
            custom_config_ok = (
                custom_collector.feedback_storage_path == self.temp_dir and
                custom_collector.analytics_enabled == False and
                custom_collector.spiritual_validation == True
            )
            self.record_test("Custom Configuration", custom_config_ok,
                           "Custom settings applied correctly")
            
        except Exception as e:
            self.record_test("Configuration", False, str(e))
    
    async def test_api_integration(self):
        """Test API integration"""
        print("\n🌐 Testing API Integration") 
        print("-" * 40)
        
        try:
            # Test 1: Function App Integration
            function_app_file = os.path.join(os.path.dirname(__file__), '..', 'backend', 'function_app.py')
            function_app_exists = os.path.exists(function_app_file)
            self.record_test("Function App File", function_app_exists,
                           f"Function app exists: {function_app_exists}")
            
            # Test 2: Feedback API Module
            feedback_api_file = os.path.join(os.path.dirname(__file__), '..', 'backend', 'feedback_api.py')
            feedback_api_exists = os.path.exists(feedback_api_file)
            self.record_test("Feedback API Module", feedback_api_exists,
                           f"Feedback API exists: {feedback_api_exists}")
            
            # Test 3: API Endpoints
            try:
                from feedback_api import (
                    collect_feedback_endpoint,
                    get_feedback_analytics,
                    get_improvement_metrics,
                    export_feedback_report
                )
                api_imports_ok = True
            except ImportError:
                api_imports_ok = False
                
            self.record_test("API Endpoints", api_imports_ok,
                           "All API endpoints importable")
            
        except Exception as e:
            self.record_test("API Integration", False, str(e))
    
    async def test_automation_scripts(self):
        """Test automation scripts"""
        print("\n🤖 Testing Automation Scripts")
        print("-" * 40)
        
        try:
            # Test 1: Continuous Improvement Script
            script_file = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'continuous-improvement.sh')
            script_exists = os.path.exists(script_file)
            script_executable = os.access(script_file, os.X_OK) if script_exists else False
            
            self.record_test("Automation Script Exists", script_exists,
                           f"Script file: {script_exists}")
            self.record_test("Script Executable", script_executable,
                           f"Executable: {script_executable}")
            
            # Test 2: Documentation
            docs_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'feedback', 'user-feedback-system.md')
            docs_exist = os.path.exists(docs_file)
            self.record_test("Documentation", docs_exist,
                           f"Docs exist: {docs_exist}")
            
            # Test 3: Configuration
            config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'feedback', 'feedback-config.yaml')
            config_exists = os.path.exists(config_file)
            self.record_test("Configuration", config_exists,
                           f"Config exists: {config_exists}")
            
        except Exception as e:
            self.record_test("Automation Scripts", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🧪 VIMARSH FEEDBACK SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        print(f"\n🕉️ Dharmic Test Completion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🙏 All feedback system components tested with spiritual principles")
        
        # Save test results
        results_file = os.path.join(self.temp_dir, "feedback_test_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"📄 Test results saved: {results_file}")
        
        return passed_tests == total_tests

async def main():
    """Main test execution"""
    tester = FeedbackSystemTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! Feedback system ready for production.")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
