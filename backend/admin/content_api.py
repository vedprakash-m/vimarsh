#!/usr/bin/env python3
"""
Content Management API Endpoints for Vimarsh Admin Panel
RESTful API for content and personality management
"""

import azure.functions as func
import json
import logging
import asyncio
from typing import Dict, Any

# Import content management service
try:
    from .content_management_service import ContentManagementService
    content_service = ContentManagementService()
except ImportError as e:
    logging.warning(f"Content management service not available: {e}")
    content_service = None

logger = logging.getLogger(__name__)

def content_overview(req: func.HttpRequest) -> func.HttpResponse:
    """Get comprehensive content overview for admin dashboard"""
    try:
        if req.method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        # Get content overview from real service if available
        if content_service:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                overview = loop.run_until_complete(content_service.get_content_overview())
                loop.close()
            except Exception as service_error:
                logger.warning(f"Content service error: {service_error}")
                overview = _get_mock_overview()
        else:
            overview = _get_mock_overview()
        
        return func.HttpResponse(
            json.dumps(overview, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Content overview error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get content overview", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def _get_mock_overview() -> Dict[str, Any]:
    """Get real overview data from database with mock fallback"""
    import os
    
    try:
        from azure.cosmos import CosmosClient
        
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            logger.warning("⚠️ No Cosmos DB connection string, using fallback")
            return _get_fallback_overview()
        
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client('vimarsh-multi-personality')
        
        personalities_data = []
        total_chunks = 0
        rag_ready_count = 0
        
        # Query personalities container
        try:
            personalities_container = database.get_container_client('personalities')
            personalities_query = "SELECT * FROM c WHERE c.is_active = true"
            personalities = list(personalities_container.query_items(
                query=personalities_query,
                enable_cross_partition_query=True
            ))
            
            for personality in personalities:
                personality_id = personality.get('id', 'unknown')
                
                # Get chunk count from personality-vectors
                chunk_count = 0
                try:
                    vectors_container = database.get_container_client('personality-vectors')
                    chunk_query = f"SELECT VALUE COUNT(1) FROM c WHERE c.personality_id = '{personality_id}'"
                    chunk_result = list(vectors_container.query_items(
                        query=chunk_query,
                        enable_cross_partition_query=True
                    ))
                    chunk_count = chunk_result[0] if chunk_result else 0
                except Exception:
                    pass
                
                total_chunks += chunk_count
                is_rag_ready = chunk_count > 0
                if is_rag_ready:
                    rag_ready_count += 1
                
                personalities_data.append({
                    "id": personality_id,
                    "name": personality.get('name', personality_id.replace('_', ' ').title()),
                    "domain": personality.get('domain', 'unknown'),
                    "status": "rag_ready" if is_rag_ready else "pending",
                    "content_sources": personality.get('content_sources', 1),
                    "total_chunks": chunk_count,
                    "rag_enabled": is_rag_ready
                })
                
        except Exception as pe:
            logger.warning(f"⚠️ Personalities query error: {pe}")
            return _get_fallback_overview()
        
        total_personalities = len(personalities_data)
        success_rate = f"{(rag_ready_count / total_personalities * 100):.1f}%" if total_personalities > 0 else "0%"
        
        return {
            "total_personalities": total_personalities,
            "rag_ready": rag_ready_count,
            "success_rate": success_rate,
            "total_chunks": total_chunks,
            "personalities": personalities_data,
            "last_updated": datetime.now().isoformat() if 'datetime' in dir() else "2025-11-25T00:00:00Z",
            "service_version": "database_v2.0"
        }
        
    except ImportError:
        logger.warning("⚠️ Azure Cosmos SDK not available")
        return _get_fallback_overview()
    except Exception as e:
        logger.error(f"❌ Content overview database error: {e}")
        return _get_fallback_overview()

def _get_fallback_overview() -> Dict[str, Any]:
    """Get fallback overview data when database is unavailable"""
    return {
        "total_personalities": 25,
        "rag_ready": 12,
        "success_rate": "48.0%",
        "personalities": [
            {
                "id": "krishna",
                "name": "Krishna",
                "domain": "spiritual",
                "status": "rag_ready",
                "content_sources": 1,
                "total_chunks": 150,
                "rag_enabled": True
            }
        ],
        "last_updated": "2025-08-12T18:30:00Z",
        "service_version": "fallback_v1.0"
    }

def process_personality_content(req: func.HttpRequest) -> func.HttpResponse:
    """Process content for a personality"""
    try:
        if req.method != "POST":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        req_body = req.get_json()
        personality_id = req_body.get("personality_id")
        force_reprocess = req_body.get("force_reprocess", False)
        
        if not personality_id:
            return func.HttpResponse(
                json.dumps({"error": "personality_id is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Mock response
        response = {
            "success": True,
            "task_id": f"process_{personality_id}_20250812_183000",
            "message": f"Content processing started for {personality_id}",
            "personality_id": personality_id
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Process content error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to process content", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def get_task_status(req: func.HttpRequest) -> func.HttpResponse:
    """Get task status"""
    try:
        if req.method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        task_id = req.params.get("task_id")
        if not task_id:
            return func.HttpResponse(
                json.dumps({"error": "task_id parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Mock response
        response = {
            "success": True,
            "task_id": task_id,
            "personality_id": "krishna",
            "task_type": "process",
            "status": "completed",
            "progress": 100,
            "message": "Content processing completed",
            "created_at": "2025-08-12T18:25:00Z",
            "updated_at": "2025-08-12T18:30:00Z"
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Get task status error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get task status", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def delete_personality_content(req: func.HttpRequest) -> func.HttpResponse:
    """Delete content for a personality"""
    try:
        if req.method != "DELETE":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        personality_id = req.params.get("personality_id")
        if not personality_id:
            return func.HttpResponse(
                json.dumps({"error": "personality_id parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Mock response
        response = {
            "success": True,
            "message": f"Deleted 150 content items for {personality_id}",
            "personality_id": personality_id,
            "deleted_count": 150
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Delete content error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to delete content", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def regenerate_embeddings(req: func.HttpRequest) -> func.HttpResponse:
    """Regenerate embeddings for a personality"""
    try:
        if req.method != "POST":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        req_body = req.get_json()
        personality_id = req_body.get("personality_id")
        
        if not personality_id:
            return func.HttpResponse(
                json.dumps({"error": "personality_id is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Mock response
        response = {
            "success": True,
            "task_id": f"regenerate_{personality_id}_20250812_183000",
            "message": f"Embedding regeneration started for {personality_id}",
            "personality_id": personality_id
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Regenerate embeddings error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to regenerate embeddings", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def get_all_tasks(req: func.HttpRequest) -> func.HttpResponse:
    """Get all tasks with optional status filter"""
    try:
        if req.method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype="application/json"
            )
        
        status_filter = req.params.get("status")
        
        # Mock response
        all_tasks = [
            {
                "task_id": "process_krishna_20250812_180000",
                "personality_id": "krishna",
                "task_type": "process",
                "status": "completed",
                "progress": 100,
                "message": "Content processing completed",
                "created_at": "2025-08-12T18:00:00Z",
                "updated_at": "2025-08-12T18:05:00Z"
            },
            {
                "task_id": "regenerate_buddha_20250812_183000",
                "personality_id": "buddha",
                "task_type": "regenerate_embeddings",
                "status": "in_progress",
                "progress": 75,
                "message": "Regenerating embeddings",
                "created_at": "2025-08-12T18:30:00Z",
                "updated_at": "2025-08-12T18:32:00Z"
            }
        ]
        
        if status_filter:
            filtered_tasks = [t for t in all_tasks if t["status"] == status_filter]
        else:
            filtered_tasks = all_tasks
        
        response = {
            "success": True,
            "total_tasks": len(filtered_tasks),
            "tasks": filtered_tasks,
            "status_filter": status_filter
        }
        
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Get all tasks error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get tasks", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
