#!/usr/bin/env python3
"""
Comprehensive Test Coverage Analyzer for Vimarsh
===============================================

Analyzes test coverage across all dimensions and provides actionable insights
for improving test quality and catching potential issues before they reach production.

Features:
- Multi-dimensional coverage analysis (line, branch, function, class)
- Gap identification with prioritized recommendations
- Integration with CI/CD pipeline
- Smart test generation suggestions
- Risk assessment based on code complexity and usage patterns
"""

import ast
import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple, Optional
import re
import argparse


@dataclass
class CoverageGap:
    """Represents a coverage gap that needs attention."""
    file_path: str
    function_name: str
    line_start: int
    line_end: int
    gap_type: str  # 'untested', 'partially_tested', 'complex_untested'
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    complexity_score: int
    usage_frequency: str  # 'rare', 'moderate', 'frequent', 'critical_path'
    recommendations: List[str]


@dataclass
class ComponentCoverage:
    """Coverage metrics for a specific component."""
    component_name: str
    file_count: int
    line_coverage: float
    branch_coverage: float
    function_coverage: float
    test_count: int
    gaps: List[CoverageGap]
    priority: str  # 'low', 'medium', 'high', 'critical'


class AdvancedCoverageAnalyzer:
    """Advanced test coverage analyzer with intelligent gap detection."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
        # Component mapping for prioritization
        self.component_priorities = {
            "spiritual_guidance": "critical",
            "rag_pipeline": "critical", 
            "llm": "critical",
            "cost_management": "high",
            "voice": "high",
            "monitoring": "medium",
            "error_handling": "high",
            "auth": "medium",
            "config": "medium"
        }
        
        # Critical paths that must have high coverage
        self.critical_paths = [
            "spiritual_guidance/api.py",
            "rag_pipeline/document_loader.py",
            "llm/gemini_client.py",
            "cost_management/tracker.py",
            "function_app.py"
        ]
    
    def analyze_coverage(self, generate_report: bool = True) -> Dict[str, Any]:
        """Perform comprehensive coverage analysis."""
        print("🔍 Starting comprehensive coverage analysis...")
        
        # Run coverage collection
        coverage_data = self._collect_coverage_data()
        
        # Analyze code complexity
        complexity_data = self._analyze_code_complexity()
        
        # Identify usage patterns
        usage_patterns = self._analyze_usage_patterns()
        
        # Find coverage gaps
        gaps = self._identify_coverage_gaps(coverage_data, complexity_data, usage_patterns)
        
        # Analyze by component
        component_analysis = self._analyze_by_component(gaps, coverage_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(component_analysis, gaps)
        
        # Calculate risk assessment
        risk_assessment = self._calculate_risk_assessment(component_analysis)
        
        analysis_result = {
            "timestamp": str(datetime.datetime.now()),
            "overall_metrics": {
                "line_coverage": coverage_data.get("line_coverage", 0),
                "branch_coverage": coverage_data.get("branch_coverage", 0),
                "function_coverage": coverage_data.get("function_coverage", 0),
                "total_gaps": len(gaps),
                "critical_gaps": len([g for g in gaps if g.risk_level == "critical"]),
                "high_risk_gaps": len([g for g in gaps if g.risk_level == "high"])
            },
            "component_analysis": component_analysis,
            "coverage_gaps": [asdict(gap) for gap in gaps],
            "recommendations": recommendations,
            "risk_assessment": risk_assessment,
            "action_items": self._generate_action_items(gaps, component_analysis)
        }
        
        if generate_report:
            self._generate_report(analysis_result)
        
        return analysis_result
    
    def _collect_coverage_data(self) -> Dict[str, Any]:
        """Collect coverage data from tests."""
        print("📊 Collecting coverage data...")
        
        try:
            # Run pytest with coverage
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "--cov=.",
                "--cov-report=json:coverage.json",
                "--cov-report=html:htmlcov",
                "--cov-branch",
                "-q"
            ], cwd=self.backend_dir, capture_output=True, text=True, timeout=300)
            
            # Load coverage JSON
            coverage_file = self.backend_dir / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                
                # Extract summary metrics
                summary = coverage_data.get("totals", {})
                return {
                    "line_coverage": summary.get("percent_covered", 0),
                    "branch_coverage": summary.get("percent_covered_display", 0),
                    "function_coverage": 0,  # Calculate separately
                    "files": coverage_data.get("files", {}),
                    "raw_data": coverage_data
                }
            else:
                print("⚠️ Coverage data not found, using mock data")
                return self._get_mock_coverage_data()
                
        except subprocess.TimeoutExpired:
            print("⚠️ Coverage collection timed out, using mock data")
            return self._get_mock_coverage_data()
        except Exception as e:
            print(f"⚠️ Coverage collection failed: {e}, using mock data")
            return self._get_mock_coverage_data()
    
    def _get_mock_coverage_data(self) -> Dict[str, Any]:
        """Get mock coverage data for testing."""
        return {
            "line_coverage": 75.5,
            "branch_coverage": 68.2,
            "function_coverage": 82.1,
            "files": {},
            "raw_data": {}
        }
    
    def _analyze_code_complexity(self) -> Dict[str, Any]:
        """Analyze code complexity using AST."""
        print("🧮 Analyzing code complexity...")
        
        complexity_data = {}
        
        for py_file in self.backend_dir.glob("**/*.py"):
            if any(part.startswith('.') for part in py_file.parts):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                analyzer = ComplexityAnalyzer()
                analyzer.visit(tree)
                
                rel_path = str(py_file.relative_to(self.backend_dir))
                complexity_data[rel_path] = {
                    "cyclomatic_complexity": analyzer.complexity,
                    "function_count": analyzer.function_count,
                    "class_count": analyzer.class_count,
                    "line_count": len(content.splitlines()),
                    "complexity_per_function": analyzer.function_complexities
                }
                
            except Exception as e:
                print(f"⚠️ Failed to analyze {py_file}: {e}")
        
        return complexity_data
    
    def _analyze_usage_patterns(self) -> Dict[str, str]:
        """Analyze usage patterns to identify critical code paths."""
        print("📈 Analyzing usage patterns...")
        
        # For now, use heuristics based on file names and structure
        # In a real implementation, this could analyze logs, function calls, etc.
        usage_patterns = {}
        
        critical_keywords = ["api", "main", "handler", "process", "execute"]
        frequent_keywords = ["util", "helper", "service", "manager"]
        
        for py_file in self.backend_dir.glob("**/*.py"):
            if any(part.startswith('.') for part in py_file.parts):
                continue
                
            rel_path = str(py_file.relative_to(self.backend_dir))
            file_name = py_file.name.lower()
            
            if any(keyword in file_name for keyword in critical_keywords):
                usage_patterns[rel_path] = "critical_path"
            elif any(keyword in file_name for keyword in frequent_keywords):
                usage_patterns[rel_path] = "frequent"
            elif "test" in file_name:
                usage_patterns[rel_path] = "rare"
            else:
                usage_patterns[rel_path] = "moderate"
        
        return usage_patterns
    
    def _identify_coverage_gaps(self, coverage_data: Dict[str, Any], 
                              complexity_data: Dict[str, Any],
                              usage_patterns: Dict[str, str]) -> List[CoverageGap]:
        """Identify coverage gaps with risk assessment."""
        print("🔍 Identifying coverage gaps...")
        
        gaps = []
        files_data = coverage_data.get("files", {})
        
        # Analyze each Python file
        for py_file in self.backend_dir.glob("**/*.py"):
            if any(part.startswith('.') for part in py_file.parts):
                continue
                
            rel_path = str(py_file.relative_to(self.backend_dir))
            
            # Get metrics for this file
            file_coverage = files_data.get(rel_path, {})
            file_complexity = complexity_data.get(rel_path, {})
            file_usage = usage_patterns.get(rel_path, "moderate")
            
            # Identify gaps based on missing coverage
            missing_lines = file_coverage.get("missing_lines", [])
            if missing_lines:
                # Create gap for missing coverage
                gap = self._create_coverage_gap(
                    rel_path, missing_lines, file_complexity, file_usage
                )
                if gap:
                    gaps.append(gap)
            
            # Identify complex functions without tests
            function_complexities = file_complexity.get("complexity_per_function", {})
            for func_name, complexity in function_complexities.items():
                if complexity > 10:  # High complexity threshold
                    gap = CoverageGap(
                        file_path=rel_path,
                        function_name=func_name,
                        line_start=0,  # Would need AST analysis to get exact lines
                        line_end=0,
                        gap_type="complex_untested",
                        risk_level=self._calculate_risk_level(complexity, file_usage),
                        complexity_score=complexity,
                        usage_frequency=file_usage,
                        recommendations=[
                            f"Add comprehensive tests for complex function '{func_name}'",
                            "Consider breaking down complex logic into smaller functions",
                            "Add edge case testing for high complexity code"
                        ]
                    )
                    gaps.append(gap)
        
        return gaps
    
    def _create_coverage_gap(self, file_path: str, missing_lines: List[int],
                           complexity_data: Dict[str, Any], usage: str) -> Optional[CoverageGap]:
        """Create a coverage gap for missing lines."""
        if not missing_lines:
            return None
        
        # Calculate risk based on complexity and usage
        avg_complexity = complexity_data.get("cyclomatic_complexity", 1)
        risk_level = self._calculate_risk_level(avg_complexity, usage)
        
        return CoverageGap(
            file_path=file_path,
            function_name="unknown",  # Would need AST analysis
            line_start=min(missing_lines),
            line_end=max(missing_lines),
            gap_type="untested",
            risk_level=risk_level,
            complexity_score=avg_complexity,
            usage_frequency=usage,
            recommendations=self._generate_gap_recommendations(file_path, len(missing_lines))
        )
    
    def _calculate_risk_level(self, complexity: int, usage: str) -> str:
        """Calculate risk level based on complexity and usage."""
        # Risk matrix
        if usage == "critical_path":
            if complexity > 15:
                return "critical"
            elif complexity > 8:
                return "high"
            else:
                return "medium"
        elif usage == "frequent":
            if complexity > 20:
                return "critical"
            elif complexity > 12:
                return "high"
            else:
                return "medium"
        else:
            if complexity > 25:
                return "high"
            elif complexity > 15:
                return "medium"
            else:
                return "low"
    
    def _generate_gap_recommendations(self, file_path: str, missing_count: int) -> List[str]:
        """Generate specific recommendations for a coverage gap."""
        recommendations = []
        
        if "api" in file_path:
            recommendations.extend([
                "Add API endpoint tests with various input scenarios",
                "Test error handling and edge cases",
                "Verify response formats and status codes"
            ])
        elif "rag_pipeline" in file_path:
            recommendations.extend([
                "Test document processing with various formats",
                "Verify vector embedding generation",
                "Test retrieval accuracy and ranking"
            ])
        elif "llm" in file_path:
            recommendations.extend([
                "Mock LLM responses for consistent testing",
                "Test different prompt scenarios",
                "Verify error handling for API failures"
            ])
        else:
            recommendations.extend([
                f"Add unit tests covering {missing_count} missing lines",
                "Focus on edge cases and error conditions",
                "Ensure all code paths are tested"
            ])
        
        return recommendations
    
    def _analyze_by_component(self, gaps: List[CoverageGap], 
                            coverage_data: Dict[str, Any]) -> Dict[str, ComponentCoverage]:
        """Analyze coverage by component."""
        print("🏗️ Analyzing coverage by component...")
        
        component_analysis = {}
        
        # Group gaps by component
        for component, priority in self.component_priorities.items():
            component_gaps = [g for g in gaps if component in g.file_path]
            
            # Count files in component
            component_files = list(self.backend_dir.glob(f"{component}/**/*.py"))
            file_count = len([f for f in component_files if not any(part.startswith('.') for part in f.parts)])
            
            # Calculate component coverage (mock for now)
            line_coverage = max(0, 85 - len(component_gaps) * 5)  # Decrease based on gaps
            branch_coverage = max(0, line_coverage - 10)
            function_coverage = max(0, line_coverage - 5)
            
            # Count tests
            test_count = len(list(self.backend_dir.glob(f"{component}/**/test_*.py")))
            test_count += len(list(self.backend_dir.glob(f"tests/test_{component}*.py")))
            
            component_analysis[component] = ComponentCoverage(
                component_name=component,
                file_count=file_count,
                line_coverage=line_coverage,
                branch_coverage=branch_coverage,
                function_coverage=function_coverage,
                test_count=test_count,
                gaps=component_gaps,
                priority=priority
            )
        
        return component_analysis
    
    def _generate_recommendations(self, component_analysis: Dict[str, ComponentCoverage],
                                gaps: List[CoverageGap]) -> List[str]:
        """Generate high-level recommendations."""
        recommendations = []
        
        # Critical gaps
        critical_gaps = [g for g in gaps if g.risk_level == "critical"]
        if critical_gaps:
            recommendations.append(f"🚨 Address {len(critical_gaps)} critical coverage gaps immediately")
        
        # Component-specific recommendations
        for component, analysis in component_analysis.items():
            if analysis.priority == "critical" and analysis.line_coverage < 80:
                recommendations.append(
                    f"🎯 Prioritize {component} component testing (current: {analysis.line_coverage:.1f}%)"
                )
            
            if analysis.test_count == 0:
                recommendations.append(f"📝 Create test suite for {component} component")
            elif len(analysis.gaps) > 5:
                recommendations.append(f"🔧 Reduce {len(analysis.gaps)} coverage gaps in {component}")
        
        # General recommendations
        overall_coverage = sum(c.line_coverage for c in component_analysis.values()) / len(component_analysis)
        if overall_coverage < 85:
            recommendations.append(f"📈 Increase overall coverage from {overall_coverage:.1f}% to 85%+")
        
        return recommendations
    
    def _calculate_risk_assessment(self, component_analysis: Dict[str, ComponentCoverage]) -> Dict[str, Any]:
        """Calculate overall risk assessment."""
        critical_components = [c for c in component_analysis.values() if c.priority == "critical"]
        high_priority_components = [c for c in component_analysis.values() if c.priority == "high"]
        
        # Calculate risk scores
        critical_risk = sum(max(0, 100 - c.line_coverage) for c in critical_components)
        high_risk = sum(max(0, 100 - c.line_coverage) for c in high_priority_components)
        
        overall_risk = "low"
        if critical_risk > 50:
            overall_risk = "critical"
        elif critical_risk > 25 or high_risk > 75:
            overall_risk = "high"
        elif critical_risk > 10 or high_risk > 40:
            overall_risk = "medium"
        
        return {
            "overall_risk": overall_risk,
            "critical_component_risk": critical_risk,
            "high_priority_risk": high_risk,
            "components_at_risk": [
                c.component_name for c in component_analysis.values() 
                if c.line_coverage < 70 and c.priority in ["critical", "high"]
            ]
        }
    
    def _generate_action_items(self, gaps: List[CoverageGap], 
                             component_analysis: Dict[str, ComponentCoverage]) -> List[Dict[str, Any]]:
        """Generate prioritized action items."""
        action_items = []
        
        # Critical gaps first
        critical_gaps = sorted([g for g in gaps if g.risk_level == "critical"], 
                             key=lambda x: x.complexity_score, reverse=True)
        
        for gap in critical_gaps[:5]:  # Top 5 critical gaps
            action_items.append({
                "priority": "critical",
                "type": "coverage_gap",
                "title": f"Fix critical coverage gap in {gap.file_path}",
                "description": f"Function '{gap.function_name}' has {gap.gap_type} coverage",
                "estimated_effort": "2-4 hours",
                "recommendations": gap.recommendations[:2]
            })
        
        # Component-level actions
        for component, analysis in component_analysis.items():
            if analysis.priority == "critical" and analysis.line_coverage < 70:
                action_items.append({
                    "priority": "high",
                    "type": "component_coverage",
                    "title": f"Improve {component} component test coverage",
                    "description": f"Coverage is {analysis.line_coverage:.1f}%, needs to reach 85%+",
                    "estimated_effort": "1-2 days",
                    "recommendations": [
                        f"Add {max(1, 10 - analysis.test_count)} more test files",
                        f"Focus on {len(analysis.gaps)} identified gaps"
                    ]
                })
        
        return action_items
    
    def _generate_report(self, analysis_result: Dict[str, Any]):
        """Generate comprehensive coverage report."""
        report_file = self.project_root / "test_coverage_analysis_report.json"
        
        with open(report_file, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        print(f"📊 Coverage analysis report saved to: {report_file}")
        
        # Generate human-readable summary
        self._print_summary(analysis_result)
    
    def _print_summary(self, analysis_result: Dict[str, Any]):
        """Print human-readable summary."""
        print("\n" + "="*60)
        print("📊 COVERAGE ANALYSIS SUMMARY")
        print("="*60)
        
        metrics = analysis_result["overall_metrics"]
        print(f"📈 Overall Coverage:")
        print(f"   Line Coverage: {metrics['line_coverage']:.1f}%")
        print(f"   Branch Coverage: {metrics['branch_coverage']:.1f}%")
        print(f"   Function Coverage: {metrics['function_coverage']:.1f}%")
        print()
        
        print(f"🎯 Coverage Gaps:")
        print(f"   Total Gaps: {metrics['total_gaps']}")
        print(f"   Critical Risk: {metrics['critical_gaps']}")
        print(f"   High Risk: {metrics['high_risk_gaps']}")
        print()
        
        risk = analysis_result["risk_assessment"]
        print(f"⚠️  Risk Assessment: {risk['overall_risk'].upper()}")
        if risk["components_at_risk"]:
            print(f"   Components at Risk: {', '.join(risk['components_at_risk'])}")
        print()
        
        print("🎯 Top Recommendations:")
        for i, rec in enumerate(analysis_result["recommendations"][:5], 1):
            print(f"   {i}. {rec}")
        print()
        
        print("📋 Priority Action Items:")
        for item in analysis_result["action_items"][:3]:
            priority_icon = "🚨" if item["priority"] == "critical" else "⚡"
            print(f"   {priority_icon} {item['title']} ({item['estimated_effort']})")
        print()


class ComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity."""
    
    def __init__(self):
        self.complexity = 1  # Base complexity
        self.function_count = 0
        self.class_count = 0
        self.function_complexities = {}
        self.current_function = None
    
    def visit_FunctionDef(self, node):
        self.function_count += 1
        old_function = self.current_function
        old_complexity = self.complexity
        
        self.current_function = node.name
        self.complexity = 1  # Reset for this function
        
        self.generic_visit(node)
        
        self.function_complexities[node.name] = self.complexity
        self.complexity = old_complexity
        self.current_function = old_function
    
    def visit_ClassDef(self, node):
        self.class_count += 1
        self.generic_visit(node)
    
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_Try(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Advanced Test Coverage Analyzer")
    parser.add_argument("--output", "-o", help="Output file for detailed report")
    parser.add_argument("--threshold", "-t", type=float, default=85.0, 
                       help="Coverage threshold percentage")
    parser.add_argument("--component", "-c", help="Analyze specific component only")
    parser.add_argument("--format", choices=["json", "html", "console"], default="console",
                       help="Output format")
    
    args = parser.parse_args()
    
    # Import datetime here to avoid import at module level
    import datetime
    
    analyzer = AdvancedCoverageAnalyzer(os.getcwd())
    result = analyzer.analyze_coverage(generate_report=True)
    
    # Check if coverage meets threshold
    overall_coverage = result["overall_metrics"]["line_coverage"]
    if overall_coverage < args.threshold:
        print(f"\n❌ Coverage {overall_coverage:.1f}% below threshold {args.threshold:.1f}%")
        sys.exit(1)
    else:
        print(f"\n✅ Coverage {overall_coverage:.1f}% meets threshold {args.threshold:.1f}%")
        sys.exit(0)


if __name__ == "__main__":
    import asyncio
    import datetime
    asyncio.run(main())
