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
    """Get real overview data from database, using seeded personalities as fallback"""
    import os
    from datetime import datetime
    
    # Import all personalities from seeding script
    try:
        from admin.seed_personalities import get_all_personalities, get_content_source, ALL_PERSONALITIES
        all_known_personalities = get_all_personalities()
    except ImportError:
        all_known_personalities = []
    
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
        db_personality_ids = set()
        
        # Query personalities container (without active filter)
        try:
            personalities_container = database.get_container_client('personalities')
            personalities_query = "SELECT * FROM c"
            personalities = list(personalities_container.query_items(
                query=personalities_query,
                enable_cross_partition_query=True
            ))
            
            for personality in personalities:
                personality_id = personality.get('id', 'unknown')
                db_personality_ids.add(personality_id)
                
                # Get chunk count from personality-vectors
                chunk_count = 0
                try:
                    vectors_container = database.get_container_client('personality_vectors')
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
                    "rag_enabled": is_rag_ready,
                    "last_update": personality.get('updated_at', '')
                })
                
        except Exception as pe:
            logger.warning(f"⚠️ Personalities query error: {pe}")
        
        # Add any missing personalities from the known list
        for known_p in all_known_personalities:
            if known_p['id'] not in db_personality_ids:
                personalities_data.append({
                    "id": known_p['id'],
                    "name": known_p['name'],
                    "domain": known_p['domain'],
                    "status": "pending",
                    "content_sources": 1,
                    "total_chunks": 0,
                    "rag_enabled": False,
                    "last_update": ""
                })
        
        # If no personalities found at all, use all known personalities
        if not personalities_data:
            return _get_fallback_overview()
        
        total_personalities = len(personalities_data)
        success_rate = f"{(rag_ready_count / total_personalities * 100):.1f}%" if total_personalities > 0 else "0%"
        
        return {
            "total_personalities": total_personalities,
            "rag_ready": rag_ready_count,
            "success_rate": success_rate,
            "total_chunks": total_chunks,
            "personalities": personalities_data,
            "last_updated": datetime.now().isoformat(),
            "service_version": "database_v2.0"
        }
        
    except ImportError:
        logger.warning("⚠️ Azure Cosmos SDK not available")
        return _get_fallback_overview()
    except Exception as e:
        logger.error(f"❌ Content overview database error: {e}")
        return _get_fallback_overview()

def _get_fallback_overview() -> Dict[str, Any]:
    """Get fallback overview data with all 25 personalities when database is unavailable"""
    from datetime import datetime
    
    # Import all personalities from seeding script
    try:
        from admin.seed_personalities import get_all_personalities, get_content_source
        all_personalities = get_all_personalities()
        
        personalities_data = []
        for p in all_personalities:
            content = get_content_source(p['id'])
            personalities_data.append({
                "id": p['id'],
                "name": p['name'],
                "domain": p['domain'],
                "status": "rag_ready" if content.get('chunks', 0) > 0 else "pending",
                "content_sources": 1,
                "total_chunks": content.get('chunks', 0),
                "rag_enabled": content.get('chunks', 0) > 0
            })
        
        rag_ready = len([p for p in personalities_data if p['rag_enabled']])
        total_chunks = sum(p['total_chunks'] for p in personalities_data)
        success_rate = f"{(rag_ready / len(personalities_data) * 100):.1f}%" if personalities_data else "0%"
        
        return {
            "total_personalities": len(personalities_data),
            "rag_ready": rag_ready,
            "success_rate": success_rate,
            "total_chunks": total_chunks,
            "personalities": personalities_data,
            "last_updated": datetime.now().isoformat(),
            "service_version": "fallback_v2.0"
        }
    except ImportError:
        # Ultimate fallback with hardcoded data
        return {
            "total_personalities": 25,
            "rag_ready": 25,
            "success_rate": "100.0%",
            "total_chunks": 458,
            "personalities": [
                {"id": "krishna", "name": "Krishna", "domain": "spiritual", "status": "rag_ready", "content_sources": 1, "total_chunks": 150, "rag_enabled": True},
                {"id": "buddha", "name": "Buddha", "domain": "spiritual", "status": "rag_ready", "content_sources": 1, "total_chunks": 67, "rag_enabled": True},
                {"id": "jesus_christ", "name": "Jesus Christ", "domain": "spiritual", "status": "rag_ready", "content_sources": 1, "total_chunks": 52, "rag_enabled": True},
                {"id": "rumi", "name": "Rumi", "domain": "spiritual", "status": "rag_ready", "content_sources": 1, "total_chunks": 89, "rag_enabled": True},
                {"id": "swami_vivekananda", "name": "Swami Vivekananda", "domain": "spiritual", "status": "rag_ready", "content_sources": 1, "total_chunks": 120, "rag_enabled": True},
                {"id": "albert_einstein", "name": "Albert Einstein", "domain": "scientific", "status": "rag_ready", "content_sources": 1, "total_chunks": 45, "rag_enabled": True},
                {"id": "isaac_newton", "name": "Isaac Newton", "domain": "scientific", "status": "rag_ready", "content_sources": 1, "total_chunks": 38, "rag_enabled": True},
                {"id": "nikola_tesla", "name": "Nikola Tesla", "domain": "scientific", "status": "rag_ready", "content_sources": 1, "total_chunks": 35, "rag_enabled": True},
                {"id": "archimedes", "name": "Archimedes", "domain": "scientific", "status": "rag_ready", "content_sources": 1, "total_chunks": 22, "rag_enabled": True},
                {"id": "leonardo_da_vinci", "name": "Leonardo da Vinci", "domain": "scientific", "status": "rag_ready", "content_sources": 1, "total_chunks": 48, "rag_enabled": True},
                {"id": "socrates", "name": "Socrates", "domain": "philosophical", "status": "rag_ready", "content_sources": 1, "total_chunks": 55, "rag_enabled": True},
                {"id": "plato", "name": "Plato", "domain": "philosophical", "status": "rag_ready", "content_sources": 1, "total_chunks": 62, "rag_enabled": True},
                {"id": "aristotle", "name": "Aristotle", "domain": "philosophical", "status": "rag_ready", "content_sources": 1, "total_chunks": 75, "rag_enabled": True},
                {"id": "confucius", "name": "Confucius", "domain": "philosophical", "status": "rag_ready", "content_sources": 1, "total_chunks": 28, "rag_enabled": True},
                {"id": "lao_tzu", "name": "Lao Tzu", "domain": "philosophical", "status": "rag_ready", "content_sources": 1, "total_chunks": 22, "rag_enabled": True},
                {"id": "marcus_aurelius", "name": "Marcus Aurelius", "domain": "philosophical", "status": "rag_ready", "content_sources": 1, "total_chunks": 28, "rag_enabled": True},
                {"id": "abraham_lincoln", "name": "Abraham Lincoln", "domain": "leadership", "status": "rag_ready", "content_sources": 1, "total_chunks": 32, "rag_enabled": True},
                {"id": "george_washington", "name": "George Washington", "domain": "leadership", "status": "rag_ready", "content_sources": 1, "total_chunks": 25, "rag_enabled": True},
                {"id": "chanakya", "name": "Chanakya", "domain": "leadership", "status": "rag_ready", "content_sources": 1, "total_chunks": 45, "rag_enabled": True},
                {"id": "martin_luther_king_jr", "name": "Martin Luther King Jr.", "domain": "leadership", "status": "rag_ready", "content_sources": 1, "total_chunks": 38, "rag_enabled": True},
                {"id": "mahatma_gandhi", "name": "Mahatma Gandhi", "domain": "leadership", "status": "rag_ready", "content_sources": 1, "total_chunks": 85, "rag_enabled": True},
                {"id": "benjamin_franklin", "name": "Benjamin Franklin", "domain": "leadership", "status": "rag_ready", "content_sources": 1, "total_chunks": 42, "rag_enabled": True},
                {"id": "william_shakespeare", "name": "William Shakespeare", "domain": "literary", "status": "rag_ready", "content_sources": 1, "total_chunks": 120, "rag_enabled": True},
                {"id": "rabindranath_tagore", "name": "Rabindranath Tagore", "domain": "literary", "status": "rag_ready", "content_sources": 1, "total_chunks": 65, "rag_enabled": True},
                {"id": "sigmund_freud", "name": "Sigmund Freud", "domain": "psychology", "status": "rag_ready", "content_sources": 1, "total_chunks": 55, "rag_enabled": True}
            ],
            "last_updated": datetime.now().isoformat() if 'datetime' in dir() else "2025-11-29T00:00:00Z",
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
