"""
Personality Management API Endpoints for Vimarsh Admin Interface

This module provides REST API endpoints for managing AI personalities including:
- CRUD operations for personalities
- Personality discovery and search
- Knowledge base association
- Expert review integration
- Personality testing and validation
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import azure.functions as func

# Import services
try:
    from services.personality_service import PersonalityService
    from models.personality_models import (
        PersonalityConfig,
        PersonalityDomain,
        PersonalityResponse,
        PersonalityValidationResult,
        PERSONALITY_CONFIGS,
        get_personality_config,
        get_personalities_by_domain,
        get_personality_list
    )
    from auth.unified_auth_service import require_auth, get_current_user
    from core.error_handling import handle_api_error, APIError
    SERVICES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Service imports failed: {e}")
    SERVICES_AVAILABLE = False

logger = logging.getLogger(__name__)


def create_personality_response(personality: PersonalityConfig) -> Dict[str, Any]:
    """Create API response for personality"""
    return {
        'id': personality.id,
        'name': personality.name,
        'domain': personality.domain.value,
        'description': personality.description,
        'safety_level': personality.safety_level.value,
        'max_response_length': personality.max_response_length,
        'greeting_style': personality.greeting_style,
        'tone_indicators': personality.tone_indicators
    }
    }


def create_validation_response(result: PersonalityValidationResult) -> Dict[str, Any]:
    """Create API response for validation result"""
    return {
        'is_valid': result.is_valid,
        'errors': result.errors,
        'warnings': result.warnings,
        'suggestions': result.suggestions,
        'score': result.score
    }


@require_auth(['admin', 'personality_manager'])
async def create_personality(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new personality"""
    try:
        if not SERVICES_AVAILABLE:
            raise APIError("Services not available", 503)
        
        # Get current user
        current_user = get_current_user(req)
        if not current_user:
            raise APIError("Authentication required", 401)
        
        # Parse request body
        try:
            body = req.get_json()
        except ValueError:
            raise APIError("Invalid JSON in request body", 400)
        
        if not body:
            raise APIError("Request body is required", 400)
        
        # Validate required fields
        required_fields = ['name', 'domain', 'description']
        missing_fields = [field for field in required_fields if not body.get(field)]
        if missing_fields:
            raise APIError(f"Missing required fields: {', '.join(missing_fields)}", 400)
        
        # Validate domain
        try:
            PersonalityDomain(body['domain'])
        except ValueError:
            valid_domains = [d.value for d in PersonalityDomain]
            raise APIError(f"Invalid domain. Valid options: {', '.join(valid_domains)}", 400)
        
        # Create personality
        personality = await personality_service.create_personality(
            personality_data=body,
            created_by=current_user.email
        )
        
        logger.info(f"✅ Created personality: {personality.id} by {current_user.email}")
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'message': 'Personality created successfully',
                'personality': create_personality_response(personality)
            }),
            status_code=201,
            headers={'Content-Type': 'application/json'}
        )
        
    except APIError as e:
        return handle_api_error(e)
    except Exception as e:
        logger.error(f"❌ Failed to create personality: {str(e)}")
        return handle_api_error(APIError("Failed to create personality", 500))


@require_auth(['admin', 'personality_manager', 'personality_viewer'])
async def get_personality(req: func.HttpRequest) -> func.HttpResponse:
    """Get personality by ID"""
    try:
        if not SERVICES_AVAILABLE:
            raise APIError("Services not available", 503)
        
        # Get personality ID from route
        personality_id = req.route_params.get('personality_id')
        if not personality_id:
            raise APIError("Personality ID is required", 400)
        
        # Get personality
        personality = await personality_service.get_personality(personality_id)
        if not personality:
            raise APIError("Personality not found", 404)
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'personality': create_personality_response(personality)
            }),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except APIError as e:
        return handle_api_error(e)
    except Exception as e:
        logger.error(f"❌ Failed to get personality: {str(e)}")
        return handle_api_error(APIError("Failed to get personality", 500))


@require_auth(['admin', 'personality_manager'])
async def update_personality(req: func.HttpRequest) -> func.HttpResponse:
    """Update personality"""
    try:
        if not SERVICES_AVAILABLE:
            raise APIError("Services not available", 503)
        
        # Get current user
        current_user = get_current_user(req)
        if not current_user:
            raise APIError("Authentication required", 401)
        
        # Get personality ID from route
        personality_id = req.route_params.get('personality_id')
        if not personality_id:
            raise APIError("Personality ID is required", 400)
        
        # Parse request body
        try:
            body = req.get_json()
        except ValueError:
            raise APIError("Invalid JSON in request body", 400)
        
        if not body:
            raise APIError("Request body is required", 400)
        
        # Validate domain if provided
        if 'domain' in body:
            try:
                PersonalityDomain(body['domain'])
            except ValueError:
                valid_domains = [d.value for d in PersonalityDomain]
                raise APIError(f"Invalid domain. Valid options: {', '.join(valid_domains)}", 400)
        
        # Update personality
        personality = await personality_service.update_personality(
            personality_id=personality_id,
            updates=body,
            updated_by=current_user.email
        )
        
        if not personality:
            raise APIError("Personality not found", 404)
        
        logger.info(f"✅ Updated personality: {personality_id} by {current_user.email}")
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'message': 'Personality updated successfully',
                'personality': create_personality_response(personality)
            }),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except APIError as e:
        return handle_api_error(e)
    except Exception as e:
        logger.error(f"❌ Failed to update personality: {str(e)}")
        return handle_api_error(APIError("Failed to update personality", 500))


@require_auth(['admin', 'personality_manager'])
async def delete_personality(req: func.HttpRequest) -> func.HttpResponse:
    """Delete (archive) personality"""
    try:
        if not SERVICES_AVAILABLE:
            raise APIError("Services not available", 503)
        
        # Get current user
        current_user = get_current_user(req)
        if not current_user:
            raise APIError("Authentication required", 401)
        
        # Get personality ID from route
        personality_id = req.route_params.get('personality_id')
        if not personality_id:
            raise APIError("Personality ID is required", 400)
        
        # Check for force parameter
        force = req.params.get('force', '').lower() == 'true'
        
        # Delete personality
        success = await personality_service.delete_personality(
            personality_id=personality_id,
            deleted_by=current_user.email,
            force=force
        )
        
        if not success:
            raise APIError("Failed to delete personality", 500)
        
        logger.info(f"✅ Deleted personality: {personality_id} by {current_user.email}")
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'message': 'Personality deleted successfully'
            }),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except APIError as e:
        return handle_api_error(e)
    except Exception as e:
        logger.error(f"❌ Failed to delete personality: {str(e)}")
        return handle_api_error(APIError("Failed to delete personality", 500))


@require_auth(['admin', 'personality_manager', 'personality_viewer'])
async def search_personalities(req: func.HttpRequest) -> func.HttpResponse:
    """Search personalities with filters"""
    try:
        if not SERVICES_AVAILABLE:
            raise APIError("Services not available", 503)
        
        # Parse query parameters
        domain = req.params.get('domain')
        status = req.params.get('status')
        is_active = req.params.get('is_active')
        expert_approved = req.params.get('expert_approved')
        tags = req.params.get('tags', '').split(',') if req.params.get('tags') else []
        search_query = req.params.get('q')
        limit = int(req.params.get('limit', '50'))
        offset = int(req.params.get('offset', '0'))
        
        # Create search filter
        filters = PersonalitySearchFilter()
        
        if domain:
            try:
                filters.domain = PersonalityDomain(domain)
            except ValueError:
                valid_domains = [d.value for d in PersonalityDomain]
                raise APIError(f"Invalid domain. Valid options: {', '.join(valid_domains)}", 400)
        
        if status:
            try:
                filters.status = PersonalityStatus(status)
            except ValueError:
                valid_statuses = [s.value for s in PersonalityStatus]
                raise APIError(f"Invalid status. Valid options: {', '.join(valid_statuses)}", 400)
        
        if is_active is not None:
            filters.is_active = is_active.lower() == 'true'
        
        if expert_approved is not None:
            filters.expert_approved = expert_approved.lower() == 'true'
        
        if tags:
            filters.tags = [tag.strip() for tag in tags if tag.strip()]
        
        if search_query:
            filters.search_query = search_query
        
        # Search personalities
        personalities = await personality_service.search_personalities(
            filters=filters,
            limit=limit,
            offset=offset
        )
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'personalities': [create_personality_response(p) for p in personalities],
                'count': len(personalities),
                'limit': limit,
                'offset': offset
            }),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except APIError as e:
        return handle_api_error(e)
    except Exception as e:
        logger.error(f"❌ Failed to search personalities: {str(e)}")
        return handle_api_error(APIError("Failed to search personalities", 500))


@require_auth(['admin', 'personality_manager', 'personality_viewer'])
async def get_personalities_by_domain(req: func.HttpRequest) -> func.HttpResponse:
    """Get personalities by domain"""
    try:
        if not SERVICES_AVAILABLE:
            raise APIError("Services not available", 503)
        
        # Get domain from route
        domain_str = req.route_params.get('domain')
        if not domain_str:
            raise APIError("Domain is required", 400)
        
        try:
            domain = PersonalityDomain(domain_str)
        except ValueError:
            valid_domains = [d.value for d in PersonalityDomain]
            raise APIError(f"Invalid domain. Valid options: {', '.join(valid_domains)}", 400)
        
        # Get active only parameter
        active_only = req.params.get('active_only', 'true').lower() == 'true'
        
        # Get personalities
        personalities = await personality_service.get_personalities_by_domain(
            domain=domain,
            active_only=active_only
        )
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'domain': domain.value,
                'personalities': [create_personality_response(p) for p in personalities],
                'count': len(personalities)
            }),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except APIError as e:
        return handle_api_error(e)
    except Exception as e:
        logger.error(f"❌ Failed to get personalities by domain: {str(e)}")
        return handle_api_error(APIError("Failed to get personalities by domain", 500))


@require_auth(['admin', 'personality_manager'])
async def validate_personality(req: func.HttpRequest) -> func.HttpResponse:
    """Validate personality configuration"""
    try:
        if not SERVICES_AVAILABLE:
            raise APIError("Services not available", 503)
        
        # Get personality ID from route
        personality_id = req.route_params.get('personality_id')
        if not personality_id:
            raise APIError("Personality ID is required", 400)
        
        # Get personality
        personality = await personality_service.get_personality(personality_id)
        if not personality:
            raise APIError("Personality not found", 404)
        
        # Validate personality
        validation_result = await personality_service.validate_personality(personality)
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'validation': create_validation_response(validation_result)
            }),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except APIError as e:
        return handle_api_error(e)
    except Exception as e:
        logger.error(f"❌ Failed to validate personality: {str(e)}")
        return handle_api_error(APIError("Failed to validate personality", 500))


@require_auth(['admin', 'personality_manager'])
async def associate_knowledge_base(req: func.HttpRequest) -> func.HttpResponse:
    """Associate knowledge base with personality"""
    try:
        if not SERVICES_AVAILABLE:
            raise APIError("Services not available", 503)
        
        # Get personality ID from route
        personality_id = req.route_params.get('personality_id')
        if not personality_id:
            raise APIError("Personality ID is required", 400)
        
        # Parse request body
        try:
            body = req.get_json()
        except ValueError:
            raise APIError("Invalid JSON in request body", 400)
        
        if not body or 'knowledge_base_ids' not in body:
            raise APIError("knowledge_base_ids is required", 400)
        
        knowledge_base_ids = body['knowledge_base_ids']
        if not isinstance(knowledge_base_ids, list):
            raise APIError("knowledge_base_ids must be a list", 400)
        
        # Associate knowledge base
        success = await personality_service.associate_knowledge_base(
            personality_id=personality_id,
            knowledge_base_ids=knowledge_base_ids
        )
        
        if not success:
            raise APIError("Failed to associate knowledge base", 500)
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'message': 'Knowledge base associated successfully'
            }),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except APIError as e:
        return handle_api_error(e)
    except Exception as e:
        logger.error(f"❌ Failed to associate knowledge base: {str(e)}")
        return handle_api_error(APIError("Failed to associate knowledge base", 500))


async def discover_personalities(req: func.HttpRequest) -> func.HttpResponse:
    """Discover personalities based on user query (public endpoint)"""
    try:
        if not SERVICES_AVAILABLE:
            raise APIError("Services not available", 503)
        
        # Get query parameter
        query = req.params.get('q', '').strip()
        if not query:
            raise APIError("Query parameter 'q' is required", 400)
        
        max_results = int(req.params.get('max_results', '10'))
        
        # Discover personalities
        personalities = await personality_service.discover_personalities(
            user_query=query,
            max_results=max_results
        )
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'query': query,
                'personalities': [create_personality_response(p) for p in personalities],
                'count': len(personalities)
            }),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except APIError as e:
        return handle_api_error(e)
    except Exception as e:
        logger.error(f"❌ Failed to discover personalities: {str(e)}")
        return handle_api_error(APIError("Failed to discover personalities", 500))


async def get_active_personalities(req: func.HttpRequest) -> func.HttpResponse:
    """Get all active personalities (public endpoint)"""
    try:
        if not SERVICES_AVAILABLE:
            raise APIError("Services not available", 503)
        
        # Get active personalities
        personalities = await personality_service.get_active_personalities()
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'personalities': [create_personality_response(p) for p in personalities],
                'count': len(personalities)
            }),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except APIError as e:
        return handle_api_error(e)
    except Exception as e:
        logger.error(f"❌ Failed to get active personalities: {str(e)}")
        return handle_api_error(APIError("Failed to get active personalities", 500))


# Route mapping for Azure Functions
PERSONALITY_ROUTES = {
    'POST /admin/personalities': create_personality,
    'GET /admin/personalities/{personality_id}': get_personality,
    'PUT /admin/personalities/{personality_id}': update_personality,
    'DELETE /admin/personalities/{personality_id}': delete_personality,
    'GET /admin/personalities': search_personalities,
    'GET /admin/personalities/domain/{domain}': get_personalities_by_domain,
    'POST /admin/personalities/{personality_id}/validate': validate_personality,
    'POST /admin/personalities/{personality_id}/knowledge-base': associate_knowledge_base,
    'GET /personalities/discover': discover_personalities,
    'GET /personalities/active': get_active_personalities,
}