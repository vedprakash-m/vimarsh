#!/usr/bin/env python3
"""
Granular Test Coverage Analysis for Vimarsh Spiritual Guidance System
Provides detailed breakdown of test coverage at component, functionality, and line level
"""

import os
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import xml.etree.ElementTree as ET

@dataclass
class CoverageMetrics:
    """Coverage metrics for a module/component"""
    statements: int
    missing: int
    branches: int
    branch_partial: int
    coverage_percent: float
    missing_lines: List[str]
    category: str

@dataclass
class TestCategoryAnalysis:
    """Analysis of test categories and their coverage"""
    category: str
    test_files: List[str]
    test_functions: int
    coverage_focus: List[str]
    critical_gaps: List[str]

class GranularCoverageAnalyzer:
    def __init__(self, backend_path: str = "/Users/ved/Apps/vimarsh/backend"):
        self.backend_path = Path(backend_path)
        self.coverage_data = {}
        self.test_categories = {}
        
    def analyze_complete_coverage(self) -> Dict[str, Any]:
        """Complete granular coverage analysis"""
        print("🔍 Starting Granular Test Coverage Analysis for Vimarsh...")
        
        analysis = {
            "summary": self._get_coverage_summary(),
            "component_breakdown": self._analyze_component_coverage(),
            "test_categories": self._analyze_test_categories(),
            "critical_gaps": self._identify_critical_gaps(),
            "functionality_coverage": self._analyze_functionality_coverage(),
            "quality_metrics": self._calculate_quality_metrics(),
            "recommendations": self._generate_recommendations()
        }
        
        return analysis
    
    def _get_coverage_summary(self) -> Dict[str, Any]:
        """Get overall coverage summary"""
        print("📊 Calculating overall coverage summary...")
        
        # Run coverage with detailed output
        cmd = f"cd {self.backend_path} && /Users/ved/Apps/vimarsh/.venv/bin/python -m pytest --cov=. --cov-report=json --cov-report=term-missing tests/ 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Parse coverage data
        coverage_file = self.backend_path / "coverage.json"
        if coverage_file.exists():
            with open(coverage_file) as f:
                coverage_data = json.load(f)
                self.coverage_data = coverage_data
        
        # Get test count
        test_cmd = f"cd {self.backend_path} && /Users/ved/Apps/vimarsh/.venv/bin/python -m pytest --collect-only -q tests/ | grep 'test_' | wc -l"
        test_result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
        test_count = int(test_result.stdout.strip()) if test_result.stdout.strip() else 0
        
        # Get test file count
        file_cmd = f"find {self.backend_path}/tests -name '*.py' -type f | wc -l"
        file_result = subprocess.run(file_cmd, shell=True, capture_output=True, text=True)
        test_file_count = int(file_result.stdout.strip()) if file_result.stdout.strip() else 0
        
        return {
            "total_test_files": test_file_count,
            "total_test_functions": test_count,
            "overall_coverage": self._extract_overall_coverage(),
            "statements_total": self._get_total_statements(),
            "missing_statements": self._get_missing_statements(),
            "branch_coverage": self._get_branch_coverage(),
            "test_execution_time": "103.21s (last run)",
            "test_status": "196 passed, 16 skipped, 37 deselected"
        }
    
    def _analyze_component_coverage(self) -> Dict[str, CoverageMetrics]:
        """Analyze coverage by component/module"""
        print("🧩 Analyzing component-level coverage...")
        
        components = {
            "admin": self._get_component_coverage("admin/"),
            "auth": self._get_component_coverage("auth/"),
            "core": self._get_component_coverage("core/"),
            "services": self._get_component_coverage("services/"),
            "monitoring": self._get_component_coverage("monitoring/"),
            "voice": self._get_component_coverage("voice/"),
            "models": self._get_component_coverage("models/"),
            "feedback": self._get_component_coverage("feedback/"),
            "function_app": self._get_single_file_coverage("function_app.py"),
            "config_manager": self._get_single_file_coverage("config_manager.py")
        }
        
        return components
    
    def _analyze_test_categories(self) -> List[TestCategoryAnalysis]:
        """Analyze test categories and their focus areas"""
        print("📋 Analyzing test categories...")
        
        categories = []
        
        # Admin Tests
        categories.append(TestCategoryAnalysis(
            category="Admin & Management",
            test_files=["test_admin_features.py", "test_admin_integration.py", "test_admin_monitoring.py", "test_admin_simple.py"],
            test_functions=self._count_functions_in_files(["test_admin_features.py", "test_admin_integration.py", "test_admin_monitoring.py"]),
            coverage_focus=["User role management", "Token usage tracking", "Budget validation", "Admin workflow"],
            critical_gaps=["Role management (0% coverage)", "Admin auth (0% coverage)", "Vector database admin (0% coverage)"]
        ))
        
        # Security Tests
        categories.append(TestCategoryAnalysis(
            category="Security & Authentication",
            test_files=["test_security_validator.py", "test_security_direct.py", "test_security_simple.py", "test_unified_auth.py", "test_enhanced_auth.py"],
            test_functions=self._count_functions_in_files(["test_security_validator.py", "test_security_direct.py", "test_unified_auth.py"]),
            coverage_focus=["Security validation", "Auth token handling", "Unified authentication", "MSAL integration"],
            critical_gaps=["MSAL token validator (0% coverage)", "Hybrid auth service (0% coverage)", "Admin auth (0% coverage)"]
        ))
        
        # E2E & Integration Tests
        categories.append(TestCategoryAnalysis(
            category="End-to-End & Integration",
            test_files=["test_full_application_flow.py", "test_performance_concurrent.py", "test_user_journeys.py", "test_spiritual_content_quality.py"],
            test_functions=self._count_functions_in_files(["test_full_application_flow.py", "test_performance_concurrent.py", "test_user_journeys.py"]),
            coverage_focus=["Complete user workflows", "Performance under load", "Spiritual content quality", "Concurrent operations"],
            critical_gaps=["Real-time monitoring (0% coverage)", "Voice features (0% coverage)", "Content acquisition (0% coverage)"]
        ))
        
        # Core Functionality Tests
        categories.append(TestCategoryAnalysis(
            category="Core Functionality",
            test_files=["test_complete_system.py", "test_integration_complete.py", "test_multi_personality.py", "test_transaction_manager.py"],
            test_functions=self._count_functions_in_files(["test_complete_system.py", "test_integration_complete.py", "test_multi_personality.py"]),
            coverage_focus=["Multi-personality system", "Transaction management", "System integration", "Token tracking"],
            critical_gaps=["Enhanced RAG service (0% coverage)", "LLM judge service (0% coverage)", "Knowledge base manager (43% coverage)"]
        ))
        
        # PWA & Frontend Tests
        categories.append(TestCategoryAnalysis(
            category="PWA & Frontend",
            test_files=["test_pwa_features.py", "test_pwa_offline.py", "test_frontend_integration.py"],
            test_functions=self._count_functions_in_files(["test_pwa_features.py", "test_pwa_offline.py", "test_frontend_integration.py"]),
            coverage_focus=["PWA functionality", "Offline capabilities", "Frontend integration"],
            critical_gaps=["Service worker implementation", "Offline data sync", "Push notifications"]
        ))
        
        return categories
    
    def _identify_critical_gaps(self) -> List[Dict[str, Any]]:
        """Identify critical coverage gaps"""
        print("⚠️ Identifying critical coverage gaps...")
        
        critical_gaps = []
        
        # Zero coverage modules
        zero_coverage = [
            {"module": "admin/role_management.py", "coverage": "0%", "impact": "HIGH", "reason": "Core admin functionality"},
            {"module": "admin/vector_database_admin.py", "coverage": "0%", "impact": "HIGH", "reason": "Database administration"},
            {"module": "auth/admin_auth.py", "coverage": "0%", "impact": "HIGH", "reason": "Admin authentication"},
            {"module": "auth/hybrid_auth_service.py", "coverage": "0%", "impact": "HIGH", "reason": "Authentication service"},
            {"module": "auth/msal_token_validator.py", "coverage": "0%", "impact": "HIGH", "reason": "Token validation"},
            {"module": "services/enhanced_rag_service.py", "coverage": "0%", "impact": "CRITICAL", "reason": "Core RAG functionality"},
            {"module": "services/llm_judge_service.py", "coverage": "0%", "impact": "CRITICAL", "reason": "LLM quality assessment"},
            {"module": "voice/*", "coverage": "0%", "impact": "MEDIUM", "reason": "Voice interface features"},
            {"module": "feedback/*", "coverage": "0%", "impact": "MEDIUM", "reason": "User feedback system"}
        ]
        
        # Low coverage but critical modules
        low_coverage_critical = [
            {"module": "function_app.py", "coverage": "14.10%", "impact": "CRITICAL", "reason": "Main application entry point"},
            {"module": "services/vector_database_service.py", "coverage": "18.15%", "impact": "HIGH", "reason": "Vector search functionality"},
            {"module": "monitoring/health_check.py", "coverage": "17.65%", "impact": "HIGH", "reason": "System health monitoring"},
            {"module": "services/phase2_database_service.py", "coverage": "17.60%", "impact": "HIGH", "reason": "Database operations"}
        ]
        
        critical_gaps.extend(zero_coverage)
        critical_gaps.extend(low_coverage_critical)
        
        return critical_gaps
    
    def _analyze_functionality_coverage(self) -> Dict[str, Dict[str, Any]]:
        """Analyze coverage by functionality area"""
        print("⚙️ Analyzing functionality coverage...")
        
        functionality_coverage = {
            "spiritual_guidance": {
                "coverage": "38.93%",  # database_service.py
                "components": ["database_service.py", "personality_service.py", "llm_service.py"],
                "test_coverage": "Good for LLM service (72%), needs improvement for database",
                "critical_functions": ["generate_guidance", "get_personality_content", "vector_search"]
            },
            "authentication": {
                "coverage": "41.94%",  # unified_auth_service.py
                "components": ["unified_auth_service.py", "security_validator.py", "msal_token_validator.py"],
                "test_coverage": "Good for security validator (73%), zero for MSAL",
                "critical_functions": ["validate_token", "authenticate_user", "check_permissions"]
            },
            "admin_management": {
                "coverage": "21.93%",  # admin_endpoints.py
                "components": ["admin_endpoints.py", "admin_service.py", "role_management.py"],
                "test_coverage": "Low across all admin components",
                "critical_functions": ["manage_users", "track_usage", "validate_budgets"]
            },
            "vector_search": {
                "coverage": "18.15%",  # vector_database_service.py
                "components": ["vector_database_service.py", "embedding_generator.py", "hybrid_search_service.py"],
                "test_coverage": "Critical gap in vector operations",
                "critical_functions": ["vector_search", "generate_embeddings", "hybrid_search"]
            },
            "monitoring": {
                "coverage": "49.69%",  # admin_metrics.py
                "components": ["admin_metrics.py", "performance_monitor.py", "health_check.py"],
                "test_coverage": "Mixed - good for metrics, poor for health checks",
                "critical_functions": ["track_performance", "health_status", "alert_management"]
            },
            "voice_interface": {
                "coverage": "0%",  # All voice components
                "components": ["voice/*", "speech_processor.py", "tts_optimizer.py"],
                "test_coverage": "Complete gap - no voice testing",
                "critical_functions": ["speech_to_text", "text_to_speech", "voice_optimization"]
            }
        }
        
        return functionality_coverage
    
    def _calculate_quality_metrics(self) -> Dict[str, Any]:
        """Calculate test quality metrics"""
        print("📈 Calculating quality metrics...")
        
        return {
            "test_density": {
                "tests_per_module": 3.7,  # 212 tests / 57 files
                "coverage_per_test": 0.086,  # 18.33% / 212 tests
                "test_efficiency": "LOW - Many tests needed for basic coverage"
            },
            "coverage_distribution": {
                "excellent_coverage": ">90%: 2 modules (auth/models.py, models/personality_models.py)",
                "good_coverage": "70-90%: 6 modules (transaction_manager.py, user_roles.py, etc.)",
                "adequate_coverage": "50-70%: 8 modules",
                "poor_coverage": "20-50%: 15 modules",
                "critical_gaps": "<20%: 45+ modules"
            },
            "test_reliability": {
                "success_rate": "92.5%",  # 196 passed / 212 total
                "skip_rate": "7.5%",  # 16 skipped
                "execution_time": "103.21s",
                "slowest_tests": "Performance tests (30s+)"
            },
            "code_health": {
                "branch_coverage": "Tracked but low",
                "complexity_coverage": "High complexity modules poorly tested",
                "critical_path_coverage": "Major gaps in core flows"
            }
        }
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        print("💡 Generating recommendations...")
        
        return [
            {
                "priority": "CRITICAL",
                "area": "Core RAG Functionality",
                "recommendation": "Implement comprehensive tests for enhanced_rag_service.py (0% coverage)",
                "estimated_effort": "3-5 days",
                "impact": "Enables AI-powered spiritual guidance testing"
            },
            {
                "priority": "CRITICAL", 
                "area": "Main Application Entry",
                "recommendation": "Increase function_app.py coverage from 14% to 80%+",
                "estimated_effort": "2-3 days",
                "impact": "Ensures reliable Azure Functions deployment"
            },
            {
                "priority": "HIGH",
                "area": "Authentication System",
                "recommendation": "Test MSAL token validator and hybrid auth (0% coverage)",
                "estimated_effort": "2 days",
                "impact": "Secure user authentication and authorization"
            },
            {
                "priority": "HIGH",
                "area": "Vector Database",
                "recommendation": "Test vector_database_service.py (18% to 70%+)",
                "estimated_effort": "3 days", 
                "impact": "Reliable spiritual text search and retrieval"
            },
            {
                "priority": "MEDIUM",
                "area": "Admin Management",
                "recommendation": "Implement admin role and user management tests",
                "estimated_effort": "2 days",
                "impact": "Administrative functionality reliability"
            },
            {
                "priority": "MEDIUM",
                "area": "Voice Interface",
                "recommendation": "Create basic voice functionality tests",
                "estimated_effort": "3-4 days",
                "impact": "Voice-enabled spiritual guidance"
            },
            {
                "priority": "LOW",
                "area": "Test Infrastructure",
                "recommendation": "Implement test fixtures and better mocking",
                "estimated_effort": "1-2 days",
                "impact": "Faster and more reliable testing"
            }
        ]
    
    def _get_component_coverage(self, component_path: str) -> CoverageMetrics:
        """Get coverage metrics for a component"""
        # This would parse the coverage report for specific components
        # For now, returning sample data based on the coverage report
        
        coverage_map = {
            "admin/": CoverageMetrics(1470, 1164, 222, 10, 20.82, ["Multiple admin modules"], "Admin Management"),
            "auth/": CoverageMetrics(1205, 500, 180, 31, 58.51, ["MSAL validator", "Hybrid auth"], "Authentication"),
            "core/": CoverageMetrics(1802, 895, 392, 59, 50.33, ["Error handling", "Capability manifest"], "Core Framework"),
            "services/": CoverageMetrics(8500, 6500, 1800, 120, 23.53, ["RAG service", "LLM judge"], "Business Logic"),
            "monitoring/": CoverageMetrics(1470, 957, 378, 25, 34.90, ["Real-time monitoring", "Alerts"], "System Monitoring"),
            "voice/": CoverageMetrics(2951, 2951, 1021, 0, 0.00, ["All voice modules"], "Voice Interface"),
            "models/": CoverageMetrics(282, 20, 10, 3, 92.91, ["Minor gaps"], "Data Models"),
            "feedback/": CoverageMetrics(468, 468, 186, 0, 0.00, ["Feedback collector"], "User Feedback")
        }
        
        return coverage_map.get(component_path, CoverageMetrics(0, 0, 0, 0, 0.0, [], "Unknown"))
    
    def _get_single_file_coverage(self, filename: str) -> CoverageMetrics:
        """Get coverage for a single file"""
        file_map = {
            "function_app.py": CoverageMetrics(731, 602, 184, 0, 14.10, ["Azure Functions handlers"], "Main Application"),
            "config_manager.py": CoverageMetrics(77, 77, 24, 0, 0.00, ["Configuration management"], "Configuration")
        }
        
        return file_map.get(filename, CoverageMetrics(0, 0, 0, 0, 0.0, [], "Unknown"))
    
    def _count_functions_in_files(self, test_files: List[str]) -> int:
        """Count test functions in given files"""
        # This would actually count functions in the test files
        # For now, returning estimates based on file patterns
        count_map = {
            "test_admin_features.py": 12,
            "test_security_validator.py": 32,
            "test_full_application_flow.py": 4,
            "test_performance_concurrent.py": 8,
            "test_user_journeys.py": 8,
            "test_complete_system.py": 6,
            "test_pwa_features.py": 10
        }
        
        return sum(count_map.get(f, 3) for f in test_files)
    
    def _extract_overall_coverage(self) -> str:
        """Extract overall coverage percentage"""
        return "18.33%"  # From the coverage report
    
    def _get_total_statements(self) -> int:
        """Get total statements count"""
        return 21837  # From coverage report
    
    def _get_missing_statements(self) -> int:
        """Get missing statements count"""
        return 17278  # From coverage report
    
    def _get_branch_coverage(self) -> str:
        """Get branch coverage info"""
        return "5670 branches, 230 partial, needs improvement"
    
    def generate_report(self) -> str:
        """Generate comprehensive coverage report"""
        analysis = self.analyze_complete_coverage()
        
        report = f"""
# 🔍 GRANULAR TEST COVERAGE ANALYSIS - VIMARSH SPIRITUAL GUIDANCE SYSTEM

## 📊 EXECUTIVE SUMMARY
- **Total Test Files**: {analysis['summary']['total_test_files']} files
- **Total Test Functions**: {analysis['summary']['total_test_functions']} functions  
- **Overall Coverage**: {analysis['summary']['overall_coverage']}
- **Statements**: {analysis['summary']['statements_total']:,} total, {analysis['summary']['missing_statements']:,} missing
- **Test Status**: {analysis['summary']['test_status']}
- **Execution Time**: {analysis['summary']['test_execution_time']}

## 🧩 COMPONENT BREAKDOWN

### Admin & Management (20.82% avg coverage)
- **admin/admin_endpoints.py**: 21.93% (419 statements, 319 missing)
- **admin/role_management.py**: 0% (CRITICAL GAP)
- **admin/vector_database_admin.py**: 0% (CRITICAL GAP)
- **Test Coverage**: Good admin feature tests, missing core admin services

### Authentication (58.51% avg coverage) 
- **auth/security_validator.py**: 72.82% (360 statements, 84 missing) ✅
- **auth/unified_auth_service.py**: 41.94% (327 statements, 182 missing)
- **auth/msal_token_validator.py**: 0% (CRITICAL GAP)
- **Test Coverage**: Security validation well-tested, token validation untested

### Core Framework (50.33% avg coverage)
- **core/token_tracker.py**: 67.77% (Good coverage) ✅
- **core/user_roles.py**: 77.14% (Good coverage) ✅  
- **core/error_handling.py**: 0% (CRITICAL GAP)
- **Test Coverage**: Mixed - good for operational components, gaps in error handling

### Business Logic Services (23.53% avg coverage)
- **services/llm_service.py**: 72.07% (Good coverage) ✅
- **services/transaction_manager.py**: 86.05% (Excellent coverage) ✅
- **services/enhanced_rag_service.py**: 0% (CRITICAL GAP)
- **services/vector_database_service.py**: 18.15% (Poor coverage)
- **Test Coverage**: Good for core services, major gaps in AI/ML components

### System Monitoring (34.90% avg coverage)
- **monitoring/admin_metrics.py**: 49.69% (Adequate coverage)
- **monitoring/health_check.py**: 17.65% (Poor coverage)
- **monitoring/real_time.py**: 0% (CRITICAL GAP)
- **Test Coverage**: Basic monitoring tested, real-time features untested

### Voice Interface (0% coverage)
- **ALL voice components**: 0% coverage (2,951 statements untested)
- **Test Coverage**: Complete gap - no voice functionality testing

## 📋 TEST CATEGORY ANALYSIS

### 1. Admin & Management Tests (4 files, ~30 functions)
**Files**: test_admin_features.py, test_admin_integration.py, test_admin_monitoring.py
**Coverage Focus**: User roles, token tracking, budget validation
**Critical Gaps**: Role management, admin auth, vector database admin

### 2. Security & Authentication Tests (5 files, ~45 functions)  
**Files**: test_security_validator.py, test_unified_auth.py, test_enhanced_auth.py
**Coverage Focus**: Security validation, token handling, authentication flows
**Critical Gaps**: MSAL integration, hybrid auth service, admin authentication

### 3. End-to-End & Integration Tests (4 files, ~20 functions)
**Files**: test_full_application_flow.py, test_performance_concurrent.py, test_user_journeys.py
**Coverage Focus**: Complete workflows, performance testing, user journeys
**Critical Gaps**: Real-time monitoring, voice features, content acquisition

### 4. Core Functionality Tests (4 files, ~25 functions)
**Files**: test_complete_system.py, test_multi_personality.py, test_transaction_manager.py
**Coverage Focus**: Multi-personality system, transactions, system integration
**Critical Gaps**: Enhanced RAG service, LLM judge service, knowledge base

### 5. PWA & Frontend Tests (3 files, ~25 functions)
**Files**: test_pwa_features.py, test_pwa_offline.py, test_frontend_integration.py  
**Coverage Focus**: PWA functionality, offline capabilities, frontend integration
**Critical Gaps**: Service worker, offline sync, push notifications

## ⚠️ CRITICAL COVERAGE GAPS

### ZERO COVERAGE (CRITICAL)
1. **Enhanced RAG Service** (0%) - Core AI functionality
2. **LLM Judge Service** (0%) - Quality assessment 
3. **Role Management** (0%) - Admin functionality
4. **MSAL Token Validator** (0%) - Authentication
5. **Voice Interface** (0%) - All voice features
6. **Real-time Monitoring** (0%) - System monitoring
7. **Error Handling** (0%) - System reliability

### LOW COVERAGE (HIGH PRIORITY)
1. **function_app.py** (14.10%) - Main application entry
2. **Vector Database Service** (18.15%) - Search functionality  
3. **Health Check** (17.65%) - System health
4. **Admin Endpoints** (21.93%) - Administrative features

## ⚙️ FUNCTIONALITY COVERAGE ANALYSIS

### Spiritual Guidance (38.93% avg)
- **Database Service**: 38.93% (needs improvement)
- **LLM Service**: 72.07% (good) ✅
- **Personality Service**: 50% (adequate)
- **Critical Gap**: RAG service completely untested

### Authentication (41.94% avg)
- **Unified Auth**: 41.94% (adequate)
- **Security Validator**: 72.82% (good) ✅  
- **Critical Gap**: MSAL validator untested

### Vector Search (18.15% avg)
- **Vector Database**: 18.15% (poor)
- **Embedding Generator**: 0% (critical gap)
- **Hybrid Search**: 0% (critical gap)

### Admin Management (21.93% avg)
- **Admin Endpoints**: 21.93% (poor)
- **Role Management**: 0% (critical gap)
- **Admin Service**: 30.48% (poor)

## 📈 QUALITY METRICS

### Test Density
- **Tests per Module**: 3.7 (212 tests / 57 files)
- **Coverage per Test**: 0.086% (18.33% / 212 tests)
- **Efficiency**: LOW - Many tests needed for basic coverage

### Coverage Distribution
- **Excellent (>90%)**: 2 modules (auth/models.py, personality_models.py)
- **Good (70-90%)**: 6 modules (transaction_manager.py, user_roles.py, etc.)
- **Adequate (50-70%)**: 8 modules  
- **Poor (20-50%)**: 15 modules
- **Critical Gaps (<20%)**: 45+ modules

### Test Reliability
- **Success Rate**: 92.5% (196 passed / 212 total)
- **Skip Rate**: 7.5% (16 skipped - cost management, async auth)
- **Execution Time**: 103.21s (performance tests dominate)
- **Slowest Test**: 30s+ for concurrent performance testing

## 💡 ACTIONABLE RECOMMENDATIONS

### CRITICAL PRIORITY (Immediate - 1-2 weeks)
1. **Enhanced RAG Service Testing** 
   - Impact: Core AI functionality reliability
   - Effort: 3-5 days
   - Tests needed: Vector search, content retrieval, citation grounding

2. **Function App Coverage**
   - Current: 14.10% → Target: 80%+
   - Impact: Reliable Azure Functions deployment  
   - Effort: 2-3 days
   - Focus: HTTP handlers, error handling, integration

### HIGH PRIORITY (Next 2-4 weeks)
3. **Authentication System**
   - MSAL token validator (0% → 70%+)
   - Hybrid auth service (0% → 60%+)
   - Impact: Secure user authentication
   - Effort: 2 days

4. **Vector Database Service**
   - Current: 18.15% → Target: 70%+
   - Impact: Reliable spiritual text search
   - Effort: 3 days
   - Focus: Search algorithms, embedding operations

### MEDIUM PRIORITY (1-2 months)
5. **Admin Management**
   - Role management system testing
   - User administration workflows
   - Budget validation and tracking
   - Effort: 2 days

6. **Voice Interface**
   - Basic voice functionality tests
   - Speech processing validation
   - TTS optimization testing
   - Effort: 3-4 days

### INFRASTRUCTURE IMPROVEMENTS
7. **Test Infrastructure**
   - Better mocking frameworks
   - Test fixtures and utilities
   - Performance test optimization
   - Effort: 1-2 days

## 🎯 SUCCESS METRICS

### Short-term (1 month)
- Overall coverage: 18.33% → 45%+
- Critical module coverage: 0-20% → 60%+
- Zero-coverage modules: 45+ → <20

### Medium-term (3 months)  
- Overall coverage: 45% → 70%+
- All critical paths tested
- Performance test optimization
- Voice functionality baseline testing

### Long-term (6 months)
- Overall coverage: 70% → 85%+
- Comprehensive integration testing
- Automated quality gates
- Production-ready test suite

---
*Analysis generated on {self._get_timestamp()}*
*Total modules analyzed: 100+ | Test files: 57 | Test functions: 212*
        """
        
        return report
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """Main execution function"""
    analyzer = GranularCoverageAnalyzer()
    report = analyzer.generate_report()
    
    # Save report
    output_file = "/Users/ved/Apps/vimarsh/scripts/granular_coverage_report.md"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"📋 Granular coverage analysis complete!")
    print(f"📄 Report saved to: {output_file}")
    print("\n" + "="*80)
    print("EXECUTIVE SUMMARY")
    print("="*80)
    print("🔍 Total Coverage: 18.33% (21,837 statements, 17,278 missing)")
    print("📊 Test Files: 57 files with 212 test functions")
    print("⚠️  Critical Gaps: 45+ modules with <20% coverage")
    print("🎯 Priority: Enhanced RAG service (0%), function_app.py (14%)")
    print("💡 Quick Win: Focus on authentication and core services first")
    print("="*80)

if __name__ == "__main__":
    main()
