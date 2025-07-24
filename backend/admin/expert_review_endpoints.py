"""
Expert Review API Endpoints for Vimarsh Admin Interface

This module provides REST API endpoints for expert review operations
including review queue management, expert assignment, feedback collection,
and review analytics.
"""

import logging
import json
from typing import Dict, Any, List, Optional
import azure.functions as func
from datetime import datetime

logger = logging.getLogger(__name__)

# Import the expert review service
try:
    from services.expert_review_service import expert_review_service, ReviewDomain, ReviewPriority, ReviewStatus
    EXPERT_REVIEW_SERVICE_AVAILABLE = True
except ImportError:
    EXPERT_REVIEW_SERVICE_AVAILABLE = False
    logger.warning("Expert review service not available")

async def get_review_items(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get review items with filtering capabilities.
    
    Query Parameters:
        - domain: Filter by domain (spiritual, scientific, historical, philosophical)
        - status: Filter by status (pending, in_review, approved, rejected, escalated)
        - expert_id: Filter by assigned expert
        - priority: Filter by priority (low, medium, high, critical)
    """
    try:
        if not EXPERT_REVIEW_SERVICE_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Expert review service not available",
                    "reviews": []
                }),
                mimetype="application/json",
                status_code=503
            )
        
        # Parse query parameters
        domain = req.params.get('domain')
        status = req.params.get('status')
        expert_id = req.params.get('expert_id')
        priority = req.params.get('priority')
        
        # Get all review items
        all_reviews = list(expert_review_service.review_items.values())
        
        # Apply filters
        filtered_reviews = all_reviews
        
        if domain and domain != 'all':
            try:
                domain_enum = ReviewDomain(domain)
                filtered_reviews = [r for r in filtered_reviews if r.domain == domain_enum]
            except ValueError:
                pass
        
        if status and status != 'all':
            try:
                status_enum = ReviewStatus(status)
                filtered_reviews = [r for r in filtered_reviews if r.status == status_enum]
            except ValueError:
                pass
        
        if expert_id:
            filtered_reviews = [r for r in filtered_reviews if r.assigned_expert_id == expert_id]
        
        if priority and priority != 'all':
            try:
                priority_enum = ReviewPriority(priority)
                filtered_reviews = [r for r in filtered_reviews if r.priority == priority_enum]
            except ValueError:
                pass
        
        # Convert to dict format for JSON serialization
        reviews_data = []
        for review in filtered_reviews:
            review_dict = {
                "review_id": review.review_id,
                "content_id": review.content_id,
                "content_type": review.content_type,
                "content_title": review.content_title,
                "content_preview": review.content_preview,
                "domain": review.domain.value,
                "personality_id": review.personality_id,
                "priority": review.priority.value,
                "status": review.status.value,
                "assigned_expert_id": review.assigned_expert_id,
                "created_at": review.created_at.isoformat(),
                "assigned_at": review.assigned_at.isoformat() if review.assigned_at else None,
                "due_date": review.due_date.isoformat(),
                "completed_at": review.completed_at.isoformat() if review.completed_at else None,
                "metadata": review.metadata
            }
            reviews_data.append(review_dict)
        
        return func.HttpResponse(
            json.dumps({
                "reviews": reviews_data,
                "total": len(reviews_data),
                "filters_applied": {
                    "domain": domain,
                    "status": status,
                    "expert_id": expert_id,
                    "priority": priority
                }
            }),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get review items: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to load review items",
                "message": str(e),
                "reviews": []
            }),
            mimetype="application/json",
            status_code=500
        )

async def get_experts(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get expert profiles.
    
    Query Parameters:
        - domain: Filter by domain expertise
        - active_only: Only return active experts (default: true)
    """
    try:
        if not EXPERT_REVIEW_SERVICE_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Expert review service not available",
                    "experts": []
                }),
                mimetype="application/json",
                status_code=503
            )
        
        # Parse query parameters
        domain = req.params.get('domain')
        active_only = req.params.get('active_only', 'true').lower() == 'true'
        
        # Get all experts
        all_experts = list(expert_review_service.experts.values())
        
        # Apply filters
        filtered_experts = all_experts
        
        if active_only:
            filtered_experts = [e for e in filtered_experts if e.is_active]
        
        if domain and domain != 'all':
            try:
                domain_enum = ReviewDomain(domain)
                filtered_experts = [e for e in filtered_experts if domain_enum in e.domains]
            except ValueError:
                pass
        
        # Convert to dict format for JSON serialization
        experts_data = []
        for expert in filtered_experts:
            expert_dict = {
                "expert_id": expert.expert_id,
                "name": expert.name,
                "email": expert.email,
                "domains": [d.value for d in expert.domains],
                "expertise_level": expert.expertise_level.value,
                "specializations": expert.specializations,
                "languages": expert.languages,
                "max_concurrent_reviews": expert.max_concurrent_reviews,
                "current_workload": expert.current_workload,
                "quality_score": expert.quality_score,
                "is_active": expert.is_active,
                "created_at": expert.created_at.isoformat()
            }
            experts_data.append(expert_dict)
        
        return func.HttpResponse(
            json.dumps({
                "experts": experts_data,
                "total": len(experts_data)
            }),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get experts: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to load experts",
                "message": str(e),
                "experts": []
            }),
            mimetype="application/json",
            status_code=500
        )

async def get_review_queues(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get review queue status for all domains.
    """
    try:
        if not EXPERT_REVIEW_SERVICE_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Expert review service not available",
                    "queues": {}
                }),
                mimetype="application/json",
                status_code=503
            )
        
        # Get queue data from service
        queues = await expert_review_service.get_review_queues()
        
        # Convert to dict format for JSON serialization
        queues_data = {}
        for domain, queue in queues.items():
            queues_data[domain] = {
                "domain": queue.domain.value,
                "pending_count": queue.pending_count,
                "in_review_count": queue.in_review_count,
                "overdue_count": queue.overdue_count,
                "avg_review_time_hours": queue.avg_review_time_hours,
                "expert_availability": queue.expert_availability
            }
        
        return func.HttpResponse(
            json.dumps({
                "queues": queues_data
            }),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get review queues: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to load review queues",
                "message": str(e),
                "queues": {}
            }),
            mimetype="application/json",
            status_code=500
        )

async def assign_review(req: func.HttpRequest) -> func.HttpResponse:
    """
    Assign a review to an expert.
    
    Expected JSON body:
    {
        "review_id": "review_123",
        "expert_id": "expert_456"
    }
    """
    try:
        if not EXPERT_REVIEW_SERVICE_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Expert review service not available"
                }),
                mimetype="application/json",
                status_code=503
            )
        
        # Parse request body
        body = req.get_json()
        if not body:
            raise ValueError("Request body is required")
        
        review_id = body.get('review_id')
        expert_id = body.get('expert_id')
        
        if not review_id or not expert_id:
            raise ValueError("Both review_id and expert_id are required")
        
        # Assign review
        success = await expert_review_service.assign_review(review_id, expert_id)
        
        if success:
            return func.HttpResponse(
                json.dumps({
                    "message": f"Review {review_id} assigned to expert {expert_id}",
                    "success": True
                }),
                mimetype="application/json",
                status_code=200,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
        else:
            raise Exception("Assignment failed")
        
    except Exception as e:
        logger.error(f"Failed to assign review: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to assign review",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

async def submit_feedback(req: func.HttpRequest) -> func.HttpResponse:
    """
    Submit expert feedback for a review.
    
    Expected JSON body:
    {
        "review_id": "review_123",
        "expert_id": "expert_456",
        "accuracy_score": 85.0,
        "authenticity_score": 90.0,
        "appropriateness_score": 88.0,
        "feedback_text": "Detailed feedback...",
        "suggested_improvements": ["Suggestion 1", "Suggestion 2"],
        "flags": ["factual_error"],
        "recommendation": "approved",
        "confidence_level": 85.0,
        "time_spent_minutes": 45
    }
    """
    try:
        if not EXPERT_REVIEW_SERVICE_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Expert review service not available"
                }),
                mimetype="application/json",
                status_code=503
            )
        
        # Parse request body
        body = req.get_json()
        if not body:
            raise ValueError("Request body is required")
        
        # Extract required fields
        review_id = body.get('review_id')
        expert_id = body.get('expert_id')
        accuracy_score = body.get('accuracy_score', 0.0)
        authenticity_score = body.get('authenticity_score', 0.0)
        appropriateness_score = body.get('appropriateness_score', 0.0)
        feedback_text = body.get('feedback_text', '')
        suggested_improvements = body.get('suggested_improvements', [])
        flags = body.get('flags', [])
        recommendation = body.get('recommendation', 'approved')
        confidence_level = body.get('confidence_level', 0.0)
        time_spent_minutes = body.get('time_spent_minutes', 0)
        
        if not review_id or not expert_id:
            raise ValueError("Both review_id and expert_id are required")
        
        # Convert recommendation to enum
        try:
            recommendation_enum = ReviewStatus(recommendation)
        except ValueError:
            raise ValueError(f"Invalid recommendation: {recommendation}")
        
        # Submit feedback
        feedback = await expert_review_service.submit_expert_feedback(
            review_id=review_id,
            expert_id=expert_id,
            accuracy_score=accuracy_score,
            authenticity_score=authenticity_score,
            appropriateness_score=appropriateness_score,
            feedback_text=feedback_text,
            suggested_improvements=suggested_improvements,
            flags=flags,
            recommendation=recommendation_enum,
            confidence_level=confidence_level,
            time_spent_minutes=time_spent_minutes
        )
        
        return func.HttpResponse(
            json.dumps({
                "message": "Feedback submitted successfully",
                "feedback_id": feedback.feedback_id,
                "overall_score": feedback.overall_score
            }),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to submit feedback",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

async def get_review_analytics(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get comprehensive review analytics.
    """
    try:
        if not EXPERT_REVIEW_SERVICE_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Expert review service not available",
                    "analytics": {}
                }),
                mimetype="application/json",
                status_code=503
            )
        
        # Get analytics from service
        analytics = await expert_review_service.get_review_analytics()
        
        return func.HttpResponse(
            json.dumps({
                "analytics": analytics
            }),
            mimetype="application/json",
            status_code=200,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get review analytics: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to load review analytics",
                "message": str(e),
                "analytics": {}
            }),
            mimetype="application/json",
            status_code=500
        )

async def submit_for_review(req: func.HttpRequest) -> func.HttpResponse:
    """
    Submit content for expert review.
    
    Expected JSON body:
    {
        "content_id": "content_123",
        "content_type": "response",
        "content_title": "Title",
        "content_preview": "Preview text...",
        "domain": "spiritual",
        "personality_id": "krishna",
        "priority": "medium",
        "metadata": {}
    }
    """
    try:
        if not EXPERT_REVIEW_SERVICE_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Expert review service not available"
                }),
                mimetype="application/json",
                status_code=503
            )
        
        # Parse request body
        body = req.get_json()
        if not body:
            raise ValueError("Request body is required")
        
        # Extract required fields
        content_id = body.get('content_id')
        content_type = body.get('content_type')
        content_title = body.get('content_title')
        content_preview = body.get('content_preview')
        domain = body.get('domain')
        personality_id = body.get('personality_id')
        priority = body.get('priority', 'medium')
        metadata = body.get('metadata', {})
        
        # Validate required fields
        required_fields = ['content_id', 'content_type', 'content_title', 'content_preview', 'domain', 'personality_id']
        for field in required_fields:
            if not body.get(field):
                raise ValueError(f"Missing required field: {field}")
        
        # Convert enums
        try:
            domain_enum = ReviewDomain(domain)
            priority_enum = ReviewPriority(priority)
        except ValueError as e:
            raise ValueError(f"Invalid enum value: {str(e)}")
        
        # Submit for review
        review_item = await expert_review_service.submit_for_review(
            content_id=content_id,
            content_type=content_type,
            content_title=content_title,
            content_preview=content_preview,
            domain=domain_enum,
            personality_id=personality_id,
            priority=priority_enum,
            metadata=metadata
        )
        
        return func.HttpResponse(
            json.dumps({
                "message": "Content submitted for review successfully",
                "review_id": review_item.review_id,
                "due_date": review_item.due_date.isoformat()
            }),
            mimetype="application/json",
            status_code=201,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to submit for review: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to submit for review",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )