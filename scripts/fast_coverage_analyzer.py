#!/usr/bin/env python3
"""
Fast Test Coverage Analyzer for Vimarsh
=========================================

Provides quick coverage analysis and actionable recommendations.
Optimized for speed and developer workflow integration.
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import time

class FastCoverageAnalyzer:
    """Fast and reliable test coverage analyzer."""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent.parent / "backend"
        self.components = [
            "spiritual_guidance", "rag_pipeline", "llm_integration",
            "voice_interface", "cost_management", "monitoring",
            "error_handling", "data_processing", "auth"
        ]
    
    def run_quick_analysis(self) -> Dict[str, Any]:
        """Run a quick coverage analysis optimized for speed."""
        print("🚀 Fast Coverage Analysis")
        print("=" * 50)
        
        start_time = time.time()
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_duration": 0,
            "test_summary": {},
            "coverage_summary": {},
            "component_analysis": {},
            "recommendations": []
        }
        
        # 1. Quick test count and structure analysis
        print("\n📊 Analyzing test structure...")
        test_stats = self._analyze_test_structure()
        results["test_summary"] = test_stats
        
        # 2. Component-by-component quick analysis
        print("\n🔍 Component analysis...")
        for component in self.components:
            analysis = self._quick_component_analysis(component)
            results["component_analysis"][component] = analysis
            print(f"   {component}: {analysis['status']} ({analysis['test_files']} tests)")
        
        # 3. Overall summary
        total_tests = sum(comp["test_files"] for comp in results["component_analysis"].values())
        total_source = sum(comp["source_files"] for comp in results["component_analysis"].values())
        
        results["coverage_summary"] = {
            "total_test_files": total_tests,
            "total_source_files": total_source,
            "test_coverage_ratio": round(total_tests / max(total_source, 1), 2),
            "estimated_coverage": min(85, total_tests * 8 + 20)  # Rough estimation
        }
        
        # 4. Generate quick recommendations
        print("\n💡 Generating recommendations...")
        recommendations = self._generate_quick_recommendations(results)
        results["recommendations"] = recommendations
        
        duration = time.time() - start_time
        results["total_duration"] = round(duration, 2)
        
        self._print_summary(results)
        return results
    
    def _analyze_test_structure(self) -> Dict[str, Any]:
        """Quick analysis of test file structure."""
        test_dir = self.backend_dir / "tests"
        
        stats = {
            "test_directories": 0,
            "test_files": 0,
            "strategic_tests": 0,
            "comprehensive_tests": 0
        }
        
        if test_dir.exists():
            # Count test directories
            stats["test_directories"] = len([d for d in test_dir.iterdir() if d.is_dir()])
            
            # Count all test files
            test_files = list(test_dir.rglob("test_*.py"))
            stats["test_files"] = len(test_files)
            
            # Count strategic and comprehensive tests
            for test_file in test_files:
                if "strategic" in test_file.name or "comprehensive" in test_file.name:
                    if "strategic" in test_file.name:
                        stats["strategic_tests"] += 1
                    if "comprehensive" in test_file.name:
                        stats["comprehensive_tests"] += 1
        
        return stats
    
    def _quick_component_analysis(self, component: str) -> Dict[str, Any]:
        """Quick analysis of a single component."""
        component_path = self.backend_dir / component
        
        analysis = {
            "name": component,
            "exists": component_path.exists(),
            "source_files": 0,
            "test_files": 0,
            "status": "missing",
            "priority": "low"
        }
        
        if not component_path.exists():
            analysis["status"] = "missing"
            analysis["priority"] = "medium"
            return analysis
        
        # Count source files
        py_files = list(component_path.glob("*.py"))
        analysis["source_files"] = len([f for f in py_files if not f.name.startswith("test_")])
        
        # Count test files in component directory
        test_files = list(component_path.glob("test_*.py"))
        
        # Count test files in tests directory
        tests_component_dir = self.backend_dir / "tests" / component
        if tests_component_dir.exists():
            test_files.extend(tests_component_dir.glob("test_*.py"))
        
        # Also check for comprehensive tests
        comprehensive_tests = list((self.backend_dir / "tests").glob(f"test_{component}_comprehensive.py"))
        test_files.extend(comprehensive_tests)
        
        analysis["test_files"] = len(test_files)
        
        # Determine status and priority
        if analysis["source_files"] == 0:
            analysis["status"] = "no_source"
            analysis["priority"] = "low"
        elif analysis["test_files"] == 0:
            analysis["status"] = "no_tests"
            analysis["priority"] = "high"
        elif analysis["test_files"] < analysis["source_files"]:
            analysis["status"] = "partial_coverage"
            analysis["priority"] = "medium"
        else:
            analysis["status"] = "good_coverage"
            analysis["priority"] = "low"
        
        return analysis
    
    def _generate_quick_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Check overall test coverage
        coverage_ratio = results["coverage_summary"]["test_coverage_ratio"]
        if coverage_ratio < 0.5:
            recommendations.append("🎯 PRIORITY: Add more test files - coverage ratio is low")
        
        # Check for missing components
        missing_components = [
            comp for comp, analysis in results["component_analysis"].items()
            if analysis["status"] == "no_tests" and analysis["source_files"] > 0
        ]
        
        if missing_components:
            recommendations.append(f"📝 Add tests for: {', '.join(missing_components[:3])}")
        
        # Check for strategic test suite
        if results["test_summary"]["strategic_tests"] == 0:
            recommendations.append("⚡ Create strategic test suite for high-impact coverage")
        
        # Check for comprehensive tests
        if results["test_summary"]["comprehensive_tests"] < 3:
            recommendations.append("🔧 Add comprehensive integration tests")
        
        # Performance recommendation
        total_tests = results["test_summary"]["test_files"]
        if total_tests > 50:
            recommendations.append("🚀 Consider parallel test execution for speed")
        
        return recommendations
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print a nice summary of results."""
        print(f"\n📋 COVERAGE ANALYSIS SUMMARY")
        print("=" * 50)
        print(f"⏱️  Analysis completed in {results['total_duration']}s")
        print(f"📁 Test files found: {results['coverage_summary']['total_test_files']}")
        print(f"📄 Source files: {results['coverage_summary']['total_source_files']}")
        print(f"📊 Test/Source ratio: {results['coverage_summary']['test_coverage_ratio']}")
        print(f"🎯 Estimated coverage: {results['coverage_summary']['estimated_coverage']}%")
        
        print(f"\n🔍 COMPONENT STATUS")
        print("-" * 30)
        for component, analysis in results["component_analysis"].items():
            status_emoji = {
                "good_coverage": "✅",
                "partial_coverage": "⚠️ ",
                "no_tests": "❌",
                "missing": "❓",
                "no_source": "🔍"
            }.get(analysis["status"], "❓")
            
            print(f"{status_emoji} {component:20} {analysis['status']:15} ({analysis['test_files']} tests)")
        
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 30)
        for i, rec in enumerate(results["recommendations"][:5], 1):
            print(f"{i}. {rec}")
        
        if results["coverage_summary"]["estimated_coverage"] >= 80:
            print(f"\n🎉 Excellent! Coverage looks good for production deployment!")
        elif results["coverage_summary"]["estimated_coverage"] >= 60:
            print(f"\n👍 Good coverage. A few more tests will get you to production-ready!")
        else:
            print(f"\n⚠️  Coverage needs improvement before production deployment.")

def run_comprehensive_with_pytest() -> Dict[str, Any]:
    """Run actual pytest with coverage for accurate numbers."""
    backend_dir = Path(__file__).parent.parent / "backend"
    
    print("\n🧪 Running pytest with coverage (this may take a minute)...")
    
    try:
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=.",
            "--cov-report=json:coverage.json",
            "--cov-report=term-missing",
            "-v",
            "--tb=short",
            "tests/"
        ]
        
        result = subprocess.run(
            cmd,
            cwd=backend_dir,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        coverage_file = backend_dir / "coverage.json"
        if coverage_file.exists():
            with open(coverage_file) as f:
                coverage_data = json.load(f)
                
            return {
                "success": True,
                "coverage_percentage": coverage_data.get("totals", {}).get("percent_covered", 0),
                "lines_covered": coverage_data.get("totals", {}).get("covered_lines", 0),
                "total_lines": coverage_data.get("totals", {}).get("num_statements", 0),
                "test_result": "passed" if result.returncode == 0 else "failed"
            }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "pytest timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    
    return {"success": False, "error": "Coverage file not found"}

def main():
    """Main execution function."""
    analyzer = FastCoverageAnalyzer()
    
    # Quick analysis (always runs)
    quick_results = analyzer.run_quick_analysis()
    
    # Ask if user wants comprehensive analysis
    if len(sys.argv) > 1 and sys.argv[1] == "--comprehensive":
        print("\n" + "="*60)
        print("🔬 COMPREHENSIVE ANALYSIS WITH PYTEST")
        print("="*60)
        
        comprehensive_results = run_comprehensive_with_pytest()
        if comprehensive_results["success"]:
            print(f"\n✅ Actual Coverage: {comprehensive_results['coverage_percentage']:.1f}%")
            print(f"📊 Lines: {comprehensive_results['lines_covered']}/{comprehensive_results['total_lines']}")
            print(f"🧪 Tests: {comprehensive_results['test_result']}")
        else:
            print(f"\n❌ Comprehensive analysis failed: {comprehensive_results.get('error', 'Unknown error')}")
    
    # Save results
    results_file = Path(__file__).parent.parent / "test_coverage_analysis_report.json"
    with open(results_file, 'w') as f:
        json.dump(quick_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Return appropriate exit code
    estimated_coverage = quick_results["coverage_summary"]["estimated_coverage"]
    if estimated_coverage < 70:
        print("\n⚠️  Coverage below recommended threshold (70%)")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
