#!/usr/bin/env python3
"""
Admin API Integration for Vimarsh Function App
Integrate admin services with the main Azure Functions app
"""

import azure.functions as func
import json
import logging
from typing import Dict, Any

# Import admin services
try:
    from admin.content_api import (
        content_overview,
        process_personality_content,
        get_task_status,
        delete_personality_content,
        regenerate_embeddings,
        get_all_tasks
    )
    from admin.testing_validation_service import testing_service
    from admin.security_compliance_service import security_service
except ImportError as e:
    logging.warning(f"Admin services not available: {e}")
    # Create placeholder functions
    def content_overview(req: func.HttpRequest) -> func.HttpResponse:
        return func.HttpResponse(
            json.dumps({"error": "Admin services not available"}),
            status_code=503,
            mimetype="application/json"
        )
    
    def process_personality_content(req: func.HttpRequest) -> func.HttpResponse:
        return content_overview(req)
    
    def get_task_status(req: func.HttpRequest) -> func.HttpResponse:
        return content_overview(req)
    
    def delete_personality_content(req: func.HttpRequest) -> func.HttpResponse:
        return content_overview(req)
    
    def regenerate_embeddings(req: func.HttpRequest) -> func.HttpResponse:
        return content_overview(req)
    
    def get_all_tasks(req: func.HttpRequest) -> func.HttpResponse:
        return content_overview(req)

logger = logging.getLogger(__name__)

class AdminAPIIntegration:
    """Admin API Integration service for managing admin endpoints"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔧 Admin API Integration service initialized")
    
    def get_available_endpoints(self) -> Dict[str, Any]:
        """Get list of available admin endpoints"""
        return {
            "content_management": [
                "content-overview",
                "process-personality-content", 
                "get-task-status",
                "delete-personality-content",
                "regenerate-embeddings",
                "get-all-tasks"
            ],
            "testing_validation": [
                "run-infrastructure-tests",
                "run-functionality-tests", 
                "run-security-tests",
                "get-test-results"
            ],
            "security_compliance": [
                "run-vulnerability-scan",
                "run-security-audit",
                "get-compliance-report"
            ]
        }

# Admin API route handlers
def admin_content_overview(req: func.HttpRequest) -> func.HttpResponse:
    """Admin endpoint for content overview"""
    return content_overview(req)

def admin_process_content(req: func.HttpRequest) -> func.HttpResponse:
    """Admin endpoint for processing personality content"""
    return process_personality_content(req)

def admin_task_status(req: func.HttpRequest) -> func.HttpResponse:
    """Admin endpoint for task status"""
    return get_task_status(req)

def admin_delete_content(req: func.HttpRequest) -> func.HttpResponse:
    """Admin endpoint for deleting personality content"""
    return delete_personality_content(req)

def admin_regenerate_embeddings(req: func.HttpRequest) -> func.HttpResponse:
    """Admin endpoint for regenerating embeddings"""
    return regenerate_embeddings(req)

def admin_all_tasks(req: func.HttpRequest) -> func.HttpResponse:
    """Admin endpoint for getting all tasks"""
    return get_all_tasks(req)

# Testing & Validation API endpoints
def admin_start_validation(req: func.HttpRequest) -> func.HttpResponse:
    """Start a validation suite"""
    try:
        if req.method != "POST":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"success": False, "error": "Invalid JSON"}),
                status_code=400,
                mimetype="application/json"
            )
        
        suite_name = req_body.get("suite_name", "comprehensive")
        environment = req_body.get("environment", "production")
        categories = req_body.get("categories")
        options = req_body.get("options", {})
        
        # Mock response for now
        suite_id = f"{suite_name}_{environment}_20250812_103000"
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "suite_id": suite_id,
                "message": f"Validation suite '{suite_name}' started for {environment}"
            }),
            status_code=202,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error starting validation: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def admin_validation_status(req: func.HttpRequest) -> func.HttpResponse:
    """Get validation suite status"""
    try:
        if req.method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        suite_id = req.params.get("suite_id")
        if not suite_id:
            return func.HttpResponse(
                json.dumps({"success": False, "error": "suite_id is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Mock validation status
        validation_status = {
            "suite_id": suite_id,
            "suite_name": "comprehensive",
            "environment": "production",
            "started_at": "2025-08-12T10:30:00Z",
            "completed_at": None,
            "status": "running",
            "total_tests": 15,
            "passed_tests": 8,
            "failed_tests": 1,
            "skipped_tests": 6,
            "success_rate": 53.3
        }
        
        return func.HttpResponse(
            json.dumps({"success": True, "data": validation_status}),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error getting validation status: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def admin_all_validations(req: func.HttpRequest) -> func.HttpResponse:
    """Get all validation suites"""
    try:
        if req.method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        status_filter = req.params.get("status")
        
        # Mock validation suites
        all_suites = [
            {
                "suite_id": "comprehensive_production_20250812_090000",
                "suite_name": "comprehensive",
                "environment": "production",
                "status": "completed",
                "total_tests": 20,
                "passed_tests": 18,
                "failed_tests": 2,
                "success_rate": 90.0,
                "completed_at": "2025-08-12T09:15:00Z"
            },
            {
                "suite_id": "security_production_20250812_100000",
                "suite_name": "security",
                "environment": "production", 
                "status": "running",
                "total_tests": 10,
                "passed_tests": 7,
                "failed_tests": 0,
                "success_rate": 70.0,
                "completed_at": None
            }
        ]
        
        # Apply status filter if provided
        if status_filter:
            filtered_suites = [s for s in all_suites if s["status"] == status_filter]
        else:
            filtered_suites = all_suites
        
        return func.HttpResponse(
            json.dumps({"success": True, "data": filtered_suites}),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error getting all validations: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

# Security & Compliance API endpoints
def admin_start_security_audit(req: func.HttpRequest) -> func.HttpResponse:
    """Start a security audit"""
    try:
        if req.method != "POST":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"success": False, "error": "Invalid JSON"}),
                status_code=400,
                mimetype="application/json"
            )
        
        audit_type = req_body.get("audit_type", "vulnerability_scan")
        environment = req_body.get("environment", "production")
        options = req_body.get("options", {})
        
        # Mock response
        audit_id = f"{audit_type}_{environment}_20250812_103000"
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "audit_id": audit_id,
                "message": f"Security audit '{audit_type}' started for {environment}"
            }),
            status_code=202,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error starting security audit: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def admin_security_audit_status(req: func.HttpRequest) -> func.HttpResponse:
    """Get security audit status"""
    try:
        if req.method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        audit_id = req.params.get("audit_id")
        if not audit_id:
            return func.HttpResponse(
                json.dumps({"success": False, "error": "audit_id is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Mock audit status
        audit_status = {
            "audit_id": audit_id,
            "audit_type": "vulnerability_scan",
            "started_at": "2025-08-12T10:30:00Z",
            "completed_at": "2025-08-12T10:45:00Z",
            "status": "completed",
            "total_issues": 3,
            "critical_issues": 0,
            "high_issues": 1,
            "medium_issues": 2,
            "low_issues": 0
        }
        
        return func.HttpResponse(
            json.dumps({"success": True, "data": audit_status}),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error getting security audit status: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def admin_all_security_audits(req: func.HttpRequest) -> func.HttpResponse:
    """Get all security audits"""
    try:
        if req.method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        status_filter = req.params.get("status")
        
        # Mock security audits
        all_audits = [
            {
                "audit_id": "vulnerability_scan_production_20250812_090000",
                "audit_type": "vulnerability_scan",
                "status": "completed",
                "total_issues": 5,
                "critical_issues": 1,
                "high_issues": 2,
                "medium_issues": 2,
                "completed_at": "2025-08-12T09:30:00Z"
            },
            {
                "audit_id": "compliance_check_production_20250812_100000",
                "audit_type": "compliance_check",
                "status": "running",
                "total_issues": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "completed_at": None
            }
        ]
        
        # Apply status filter if provided
        if status_filter:
            filtered_audits = [a for a in all_audits if a["status"] == status_filter]
        else:
            filtered_audits = all_audits
        
        return func.HttpResponse(
            json.dumps({"success": True, "data": filtered_audits}),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error getting all security audits: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def admin_security_summary(req: func.HttpRequest) -> func.HttpResponse:
    """Get security summary"""
    try:
        if req.method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        # Mock security summary
        security_summary = {
            "total_audits": 5,
            "completed_audits": 4,
            "total_issues": 12,
            "critical_issues": 1,
            "high_issues": 3,
            "medium_issues": 5,
            "low_issues": 3,
            "last_audit": {
                "audit_id": "vulnerability_scan_production_20250812_090000",
                "audit_type": "vulnerability_scan",
                "completed_at": "2025-08-12T09:30:00Z",
                "issues_found": 5
            }
        }
        
        return func.HttpResponse(
            json.dumps({"success": True, "data": security_summary}),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error getting security summary: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

# Admin dashboard overview
def admin_dashboard_overview(req: func.HttpRequest) -> func.HttpResponse:
    """Get admin dashboard overview with all services status"""
    try:
        if req.method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        # Mock dashboard overview
        dashboard_overview = {
            "content_management": {
                "total_personalities": 19,
                "rag_ready": 8,
                "active_tasks": 2,
                "success_rate": "42.1%",
                "last_updated": "2025-08-12T10:30:00Z"
            },
            "testing_validation": {
                "total_suites": 3,
                "active_suites": 1,
                "last_success_rate": 90.0,
                "last_run": "2025-08-12T09:15:00Z"
            },
            "security_compliance": {
                "total_audits": 5,
                "open_issues": 8,
                "critical_issues": 1,
                "last_audit": "2025-08-12T09:30:00Z"
            },
            "system_health": {
                "api_status": "healthy",
                "database_status": "healthy",
                "last_health_check": "2025-08-12T10:35:00Z"
            }
        }
        
        return func.HttpResponse(
            json.dumps({"success": True, "data": dashboard_overview}),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
