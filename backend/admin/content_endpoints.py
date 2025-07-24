"""
Content Management API Endpoints for Vimarsh Admin Interface

This module provides REST API endpoints for content management operations
including upload, processing, association with personalities, and quality validation.
"""

import logging
import json
from typing import Dict, Any, List, Optional
import azure.functions as func
from datetime import datetime

logger = logging.getLogger(__name__)

# Mock content data for demonstration
MOCK_CONTENT = [
    {
        "id": "content_1",
        "title": "Bhagavad Gita Chapter 2",
        "type": "book",
        "source": "Bhagavad Gita",
        "author": "Vyasa",
        "description": "The second chapter of the Bhagavad Gita dealing with karma yoga",
        "content_preview": "You have a right to perform your prescribed duty, but not to the fruits of action...",
        "file_size": 15420,
        "upload_date": "2024-01-15T10:30:00Z",
        "status": "approved",
        "quality_score": 95.5,
        "associated_personalities": ["krishna"],
        "domain": "spiritual",
        "language": "English",
        "tags": ["dharma", "karma", "yoga", "duty"],
        "metadata": {
            "chapter": 2,
            "verses": 72,
            "tradition": "Hindu"
        }
    },
    {
        "id": "content_2", 
        "title": "Theory of Relativity",
        "type": "article",
        "source": "Physics Journal",
        "author": "Albert Einstein",
        "description": "Einstein's groundbreaking paper on special relativity",
        "content_preview": "The speed of light in a vacuum is constant for all observers...",
        "file_size": 8750,
        "upload_date": "2024-01-20T14:15:00Z",
        "status": "approved",
        "quality_score": 98.2,
        "associated_personalities": ["einstein"],
        "domain": "scientific",
        "language": "English",
        "tags": ["physics", "relativity", "spacetime", "theory"],
        "metadata": {
            "year": 1905,
            "journal": "Annalen der Physik",
            "citations": 15000
        }
    },
    {
        "id": "content_3",
        "title": "Gettysburg Address",
        "type": "document",
        "source": "Historical Speech",
        "author": "Abraham Lincoln",
        "description": "Lincoln's famous speech at Gettysburg",
        "content_preview": "Four score and seven years ago our fathers brought forth...",
        "file_size": 2100,
        "upload_date": "2024-01-25T09:45:00Z",
        "status": "approved",
        "quality_score": 92.8,
        "associated_personalities": ["lincoln"],
        "domain": "historical",
        "language": "English",
        "tags": ["democracy", "freedom", "civil war", "speech"],
        "metadata": {
            "date": "1863-11-19",
            "location": "Gettysburg, Pennsylvania",
            "duration": "2 minutes"
        }
    },
    {
        "id": "content_4",
        "title": "Meditations Book IV",
        "type": "book",
        "source": "Meditations",
        "author": "Marcus Aurelius",
        "description": "Stoic philosophical reflections on virtue and duty",
        "content_preview": "You have power over your mind - not outside events...",
        "file_size": 12300,
        "upload_date": "2024-02-01T16:20:00Z",
        "status": "pending",
        "quality_score": 89.4,
        "associated_personalities": [],
        "domain": "philosophical",
        "language": "English",
        "tags": ["stoicism", "virtue", "philosophy", "mind"],
        "metadata": {
            "book": 4,
            "entries": 53,
            "period": "Roman Empire"
        }
    }
]

async def get_content(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get content with filtering and search capabilities.
    
    Query Parameters:
        - domain: Filter by domain (spiritual, scientific, historical, philosophical)
        - status: Filter by status (pending, approved, rejected)
        - q: Search query
        - associated_only: Only return content with personality associations
    """
    try:
        # Parse query parameters
        domain = req.params.get('domain')
        status = req.params.get('status')
        search_query = req.params.get('q', '').lower()
        associated_only = req.params.get('associated_only', 'false').lower() == 'true'
        
        # Filter content
        filtered_content = MOCK_CONTENT.copy()
        
        if domain and domain != 'all':
            filtered_content = [c for c in filtered_content if c['domain'] == domain]
        
        if status and status != 'all':
            filtered_content = [c for c in filtered_content if c['status'] == status]
        
        if search_query:
            filtered_content = [
                c for c in filtered_content 
                if search_query in c['title'].lower() 
                or search_query in c['description'].lower()
                or search_query in c['author'].lower()
                or any(search_query in tag.lower() for tag in c['tags'])
            ]
        
        if associated_only:
            filtered_content = [c for c in filtered_content if c['associated_personalities']]
        
        return func.HttpResponse(
            json.dumps({
                "content": filtered_content,
                "total": len(filtered_content),
                "filters_applied": {
                    "domain": domain,
                    "status": status,
                    "search_query": search_query,
                    "associated_only": associated_only
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
        logger.error(f"Failed to get content: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to load content",
                "message": str(e),
                "content": []
            }),
            mimetype="application/json",
            status_code=500
        )

async def create_content(req: func.HttpRequest) -> func.HttpResponse:
    """
    Create new content item.
    
    Expected JSON body:
    {
        "title": "Content Title",
        "type": "book|article|document|text|pdf|url",
        "source": "Source Name",
        "author": "Author Name",
        "description": "Content description",
        "domain": "spiritual|scientific|historical|philosophical",
        "language": "English",
        "tags": ["tag1", "tag2"],
        "content": "Full content text or file data"
    }
    """
    try:
        # Parse request body
        body = req.get_json()
        if not body:
            raise ValueError("Request body is required")
        
        # Validate required fields
        required_fields = ['title', 'type', 'source', 'description', 'domain']
        for field in required_fields:
            if field not in body:
                raise ValueError(f"Missing required field: {field}")
        
        # Create new content item
        new_content = {
            "id": f"content_{datetime.now().timestamp()}",
            "title": body['title'],
            "type": body['type'],
            "source": body['source'],
            "author": body.get('author', ''),
            "description": body['description'],
            "content_preview": body.get('content', '')[:200] + "...",
            "file_size": len(body.get('content', '')),
            "upload_date": datetime.now().isoformat() + "Z",
            "status": "pending",
            "quality_score": 0.0,  # Would be calculated by content processor
            "associated_personalities": [],
            "domain": body['domain'],
            "language": body.get('language', 'English'),
            "tags": body.get('tags', []),
            "metadata": body.get('metadata', {})
        }
        
        # In a real implementation, this would save to database
        # For now, we'll just return the created content
        
        return func.HttpResponse(
            json.dumps({
                "message": "Content created successfully",
                "content": new_content
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
        logger.error(f"Failed to create content: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to create content",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

async def update_content(req: func.HttpRequest) -> func.HttpResponse:
    """
    Update existing content item.
    """
    try:
        content_id = req.route_params.get('content_id')
        if not content_id:
            raise ValueError("Content ID is required")
        
        body = req.get_json()
        if not body:
            raise ValueError("Request body is required")
        
        # In a real implementation, this would update the database
        # For now, we'll just return success
        
        return func.HttpResponse(
            json.dumps({
                "message": f"Content {content_id} updated successfully"
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
        logger.error(f"Failed to update content: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to update content",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

async def delete_content(req: func.HttpRequest) -> func.HttpResponse:
    """
    Delete content item.
    """
    try:
        content_id = req.route_params.get('content_id')
        if not content_id:
            raise ValueError("Content ID is required")
        
        # In a real implementation, this would delete from database
        # For now, we'll just return success
        
        return func.HttpResponse(
            json.dumps({
                "message": f"Content {content_id} deleted successfully"
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
        logger.error(f"Failed to delete content: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to delete content",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

async def associate_content_personalities(req: func.HttpRequest) -> func.HttpResponse:
    """
    Associate content with personalities.
    
    Expected JSON body:
    {
        "personality_ids": ["personality1", "personality2"]
    }
    """
    try:
        content_id = req.route_params.get('content_id')
        if not content_id:
            raise ValueError("Content ID is required")
        
        body = req.get_json()
        if not body:
            raise ValueError("Request body is required")
        
        personality_ids = body.get('personality_ids', [])
        
        # In a real implementation, this would update the database
        # For now, we'll just return success
        
        return func.HttpResponse(
            json.dumps({
                "message": f"Content {content_id} associated with {len(personality_ids)} personalities",
                "associations": personality_ids
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
        logger.error(f"Failed to associate content: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to associate content",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

async def validate_content_quality(req: func.HttpRequest) -> func.HttpResponse:
    """
    Validate content quality and update quality score.
    """
    try:
        content_id = req.route_params.get('content_id')
        if not content_id:
            raise ValueError("Content ID is required")
        
        # In a real implementation, this would run quality validation algorithms
        # For now, we'll simulate a quality score update
        import random
        new_quality_score = random.uniform(75.0, 98.0)
        
        return func.HttpResponse(
            json.dumps({
                "message": f"Content {content_id} quality validated",
                "quality_score": round(new_quality_score, 1)
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
        logger.error(f"Failed to validate content quality: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to validate content quality",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

async def approve_content(req: func.HttpRequest) -> func.HttpResponse:
    """
    Approve content item.
    """
    try:
        content_id = req.route_params.get('content_id')
        if not content_id:
            raise ValueError("Content ID is required")
        
        # In a real implementation, this would update the database
        # For now, we'll just return success
        
        return func.HttpResponse(
            json.dumps({
                "message": f"Content {content_id} approved successfully"
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
        logger.error(f"Failed to approve content: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to approve content",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

async def reject_content(req: func.HttpRequest) -> func.HttpResponse:
    """
    Reject content item.
    """
    try:
        content_id = req.route_params.get('content_id')
        if not content_id:
            raise ValueError("Content ID is required")
        
        # In a real implementation, this would update the database
        # For now, we'll just return success
        
        return func.HttpResponse(
            json.dumps({
                "message": f"Content {content_id} rejected successfully"
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
        logger.error(f"Failed to reject content: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to reject content",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )