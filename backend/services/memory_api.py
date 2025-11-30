"""
Memory API Endpoints for Vimarsh

These endpoints provide access to the hierarchical memory system.
Add these routes to function_app.py to enable memory functionality.
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

import azure.functions as func

from services.hierarchical_memory_service import (
    HierarchicalMemoryService,
    get_memory_service
)
from models.memory_models import (
    MemorySearchQuery,
    WorkingMemoryContext
)

logger = logging.getLogger(__name__)


# ==============================================================================
# MEMORY API ENDPOINTS
# ==============================================================================

async def memory_context_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    GET /memory/context
    
    Retrieve assembled context for current conversation.
    
    Query Parameters:
        user_id: User identifier (required)
        personality_id: Personality identifier (required)
        session_id: Current session ID (required)
        query: Current user query for semantic search (optional)
    
    Returns:
        WorkingMemoryContext as JSON
    """
    try:
        user_id = req.params.get("user_id")
        personality_id = req.params.get("personality_id")
        session_id = req.params.get("session_id")
        current_query = req.params.get("query", "")
        
        if not user_id or not personality_id or not session_id:
            return func.HttpResponse(
                json.dumps({"error": "user_id, personality_id, and session_id are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        memory_service = get_memory_service()
        
        # Assemble working memory
        context = await memory_service.assemble_working_memory(
            user_id=user_id,
            personality_id=personality_id,
            session_id=session_id,
            current_query=current_query,
            current_messages=[]
        )
        
        # Return as JSON
        response_data = {
            "user_id": context.user_id,
            "personality_id": context.personality_id,
            "session_id": context.session_id,
            "total_tokens": context.get_total_tokens(),
            "available_tokens": context.get_available_tokens(),
            "context_quality_score": context.context_quality_score,
            "user_profile_context": context.user_profile_context,
            "relationship_context": context.relationship_context,
            "recent_session_summaries": context.recent_session_summaries,
            "relevant_past_insights": context.relevant_past_insights,
            "retrieved_memories": context.retrieved_memories,
            "assembled_at": context.assembled_at.isoformat() if context.assembled_at else None
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in memory context endpoint: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


async def memory_profile_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    GET /memory/profile
    
    Get user's memory profile and relationship states.
    
    Query Parameters:
        user_id: User identifier (required)
    
    Returns:
        MemoryProfile with relationships as JSON
    """
    try:
        user_id = req.params.get("user_id")
        
        if not user_id:
            return func.HttpResponse(
                json.dumps({"error": "user_id is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        memory_service = get_memory_service()
        
        # Get profile
        profile = await memory_service.get_or_create_memory_profile(user_id)
        
        # Get all relationships
        relationships = await memory_service.get_all_relationships(user_id)
        
        response_data = {
            "profile": profile.to_dict(),
            "relationships": [r.to_dict() for r in relationships],
            "total_relationships": len(relationships)
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in memory profile endpoint: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


async def memory_update_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    POST /memory/update
    
    Update core memory with new user information.
    
    Request Body:
        user_id: User identifier (required)
        updates: Dict of fields to update
    
    Returns:
        Updated profile
    """
    try:
        body = req.get_json()
        user_id = body.get("user_id")
        updates = body.get("updates", {})
        
        if not user_id:
            return func.HttpResponse(
                json.dumps({"error": "user_id is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        memory_service = get_memory_service()
        
        # Get existing profile
        profile = await memory_service.get_or_create_memory_profile(user_id)
        
        # Apply updates
        if "discovered_interests" in updates:
            # Merge new interests
            existing = set(profile.discovered_interests)
            existing.update(updates["discovered_interests"])
            profile.discovered_interests = list(existing)[:20]
        
        if "recurring_themes" in updates:
            existing = set(profile.recurring_themes)
            existing.update(updates["recurring_themes"])
            profile.recurring_themes = list(existing)[:20]
        
        if "communication_style" in updates:
            profile.communication_style.update(updates["communication_style"])
        
        if "life_context" in updates:
            profile.life_context.update(updates["life_context"])
        
        if "memory_preferences" in updates:
            profile.memory_preferences.update(updates["memory_preferences"])
        
        # Save
        success = await memory_service.update_memory_profile(profile)
        
        return func.HttpResponse(
            json.dumps({
                "success": success,
                "profile": profile.to_dict()
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in memory update endpoint: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


async def memory_search_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    POST /memory/search
    
    Semantic search across conversation history.
    
    Request Body:
        user_id: User identifier (required)
        query: Search query text (required)
        personality_id: Filter by personality (optional)
        max_results: Maximum results (default 10)
        min_importance_score: Minimum importance (default 0.3)
    
    Returns:
        List of matching memories with relevance scores
    """
    try:
        body = req.get_json()
        
        user_id = body.get("user_id")
        query_text = body.get("query")
        
        if not user_id or not query_text:
            return func.HttpResponse(
                json.dumps({"error": "user_id and query are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        memory_service = get_memory_service()
        
        # Build search query
        search_query = MemorySearchQuery(
            user_id=user_id,
            query_text=query_text,
            personality_id=body.get("personality_id"),
            max_results=body.get("max_results", 10),
            min_importance_score=body.get("min_importance_score", 0.3),
            include_archived=body.get("include_archived", False)
        )
        
        # Perform search
        results = await memory_service.semantic_search(search_query)
        
        return func.HttpResponse(
            json.dumps({
                "results": [r.to_dict() for r in results],
                "total_results": len(results),
                "query": query_text
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in memory search endpoint: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


async def memory_session_end_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    POST /memory/session/end
    
    End a session and generate summary with reflections.
    
    Request Body:
        user_id: User identifier (required)
        personality_id: Personality identifier (required)
        session_id: Session ID (required)
    
    Returns:
        Session summary with insights and reflection
    """
    try:
        body = req.get_json()
        
        user_id = body.get("user_id")
        personality_id = body.get("personality_id")
        session_id = body.get("session_id")
        
        if not user_id or not personality_id or not session_id:
            return func.HttpResponse(
                json.dumps({"error": "user_id, personality_id, and session_id are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        memory_service = get_memory_service()
        
        # Get recent messages for this session
        messages = await memory_service.get_recent_messages(
            user_id=user_id,
            personality_id=personality_id,
            limit=50
        )
        
        # Filter to current session
        session_messages = [m for m in messages if m.session_id == session_id]
        
        # Create and end session summary
        from models.memory_models import SessionSummary
        session = SessionSummary.create_new(user_id, personality_id, session_id)
        session = await memory_service.end_session(session, session_messages)
        
        # Update relationship after session
        relationship = await memory_service.get_or_create_relationship(user_id, personality_id)
        duration = session.duration_minutes
        topics = session.topics
        ending_emotion = session.ending_emotion
        
        relationship.update_after_interaction(duration, topics, ending_emotion)
        await memory_service.update_relationship(relationship)
        
        return func.HttpResponse(
            json.dumps({
                "session": session.to_dict(),
                "relationship_updated": True,
                "new_depth_level": relationship.depth_level.name
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in session end endpoint: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


async def memory_relationship_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    GET /memory/relationship/{personality_id}
    
    Get relationship state with specific personality.
    
    Query Parameters:
        user_id: User identifier (required)
    
    Route Parameters:
        personality_id: Personality identifier (required)
    
    Returns:
        RelationshipState as JSON
    """
    try:
        user_id = req.params.get("user_id")
        # Extract personality_id from route (would need to be passed via route params)
        personality_id = req.route_params.get("personality_id") or req.params.get("personality_id")
        
        if not user_id or not personality_id:
            return func.HttpResponse(
                json.dumps({"error": "user_id and personality_id are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        memory_service = get_memory_service()
        
        relationship = await memory_service.get_or_create_relationship(user_id, personality_id)
        
        return func.HttpResponse(
            json.dumps({
                "relationship": relationship.to_dict(),
                "depth_level_name": relationship.depth_level.name,
                "is_new": relationship.interaction_count == 0
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in relationship endpoint: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


async def memory_feedback_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    POST /memory/feedback
    
    Record memory feedback for importance scoring adjustment.
    
    Request Body:
        user_id: User identifier (required)
        message_id: Message ID to update (required)
        feedback_type: "helpful" | "not_helpful" | "important" (required)
    
    Returns:
        Updated importance score
    """
    try:
        body = req.get_json()
        
        user_id = body.get("user_id")
        message_id = body.get("message_id")
        feedback_type = body.get("feedback_type")
        
        if not user_id or not message_id or not feedback_type:
            return func.HttpResponse(
                json.dumps({"error": "user_id, message_id, and feedback_type are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Adjust importance based on feedback
        importance_adjustments = {
            "helpful": 0.2,
            "not_helpful": -0.2,
            "important": 0.3,
            "save": 0.4
        }
        
        adjustment = importance_adjustments.get(feedback_type, 0)
        
        # Note: In full implementation, this would update the message in Cosmos DB
        # For now, return success with the adjustment that would be applied
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "message_id": message_id,
                "feedback_type": feedback_type,
                "importance_adjustment": adjustment
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in feedback endpoint: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )


# ==============================================================================
# ROUTE REGISTRATION
# ==============================================================================

def register_memory_routes(app: func.FunctionApp):
    """
    Register memory API routes with the Azure Functions app.
    
    Call this from function_app.py:
        from services.memory_api import register_memory_routes
        register_memory_routes(app)
    """
    
    @app.route(route="memory/context", methods=["GET"])
    async def memory_context_route(req: func.HttpRequest) -> func.HttpResponse:
        return await memory_context_endpoint(req)
    
    @app.route(route="memory/profile", methods=["GET"])
    async def memory_profile_route(req: func.HttpRequest) -> func.HttpResponse:
        return await memory_profile_endpoint(req)
    
    @app.route(route="memory/update", methods=["POST"])
    async def memory_update_route(req: func.HttpRequest) -> func.HttpResponse:
        return await memory_update_endpoint(req)
    
    @app.route(route="memory/search", methods=["POST"])
    async def memory_search_route(req: func.HttpRequest) -> func.HttpResponse:
        return await memory_search_endpoint(req)
    
    @app.route(route="memory/session/end", methods=["POST"])
    async def memory_session_end_route(req: func.HttpRequest) -> func.HttpResponse:
        return await memory_session_end_endpoint(req)
    
    @app.route(route="memory/relationship/{personality_id}", methods=["GET"])
    async def memory_relationship_route(req: func.HttpRequest) -> func.HttpResponse:
        return await memory_relationship_endpoint(req)
    
    @app.route(route="memory/feedback", methods=["POST"])
    async def memory_feedback_route(req: func.HttpRequest) -> func.HttpResponse:
        return await memory_feedback_endpoint(req)
    
    logger.info("🧠 Memory API routes registered")
