"""
Performance Monitoring and Caching API Endpoints for Vimarsh Admin Interface

This module provides REST API endpoints for performance monitoring,
cache management, and optimization recommendations.
"""

import logging
import json
from typing import Dict, Any, List, Optional
import azure.functions as func
from datetime import datetime

logger = logging.getLogger(__name__)

# Import performance services
try:
    from services.personality_cache_service import personality_cache_service, CacheType, CacheLevel
    from services.performance_monitor import performance_monitor
    PERFORMANCE_SERVICES_AVAILABLE = True
except ImportError:
    PERFORMANCE_SERVICES_AVAILABLE = False
    logger.warning("Performance services not available")

async def get_cache_metrics(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get cache performance metrics.
    
    Query Parameters:
        - personality_id: Filter by specific personality (optional)
    """
    try:
        if not PERFORMANCE_SERVICES_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Performance services not available",
                    "metrics": {}
                }),
                mimetype="application/json",
                status_code=503
            )
        
        personality_id = req.params.get('personality_id')
        
        # Get cache metrics
        cache_metrics = personality_cache_service.get_cache_metrics(personality_id)
        
        return func.HttpResponse(
            json.dumps({
                "cache_metrics": cache_metrics,
                "timestamp": datetime.now().isoformat()
            }, default=str),
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
        logger.error(f"Failed to get cache metrics: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to load cache metrics",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )

async def get_performance_metrics(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get performance metrics.
    
    Query Parameters:
        - personality_id: Filter by specific personality (optional)
    """
    try:
        if not PERFORMANCE_SERVICES_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Performance services not available",
                    "metrics": {}
                }),
                mimetype="application/json",
                status_code=503
            )
        
        personality_id = req.params.get('personality_id')
        
        if personality_id:
            # Get personality-specific metrics
            personality_metrics = performance_monitor.get_personality_metrics(personality_id)
            cache_metrics = personality_cache_service.get_performance_metrics(personality_id)
            
            metrics = {
                "personality_id": personality_id,
                "performance": personality_metrics,
                "cache": cache_metrics
            }
        else:
            # Get system-wide metrics
            system_metrics = performance_monitor.get_system_metrics()
            cache_metrics = personality_cache_service.get_performance_metrics()
            
            metrics = {
                "system": system_metrics,
                "cache": cache_metrics
            }
        
        return func.HttpResponse(
            json.dumps({
                "metrics": metrics,
                "timestamp": datetime.now().isoformat()
            }, default=str),
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
        logger.error(f"Failed to get performance metrics: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to load performance metrics",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )

async def get_performance_report(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get comprehensive performance report.
    
    Query Parameters:
        - personality_id: Filter by specific personality (optional)
        - time_range_hours: Time range for report (default: 24)
    """
    try:
        if not PERFORMANCE_SERVICES_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Performance services not available",
                    "report": {}
                }),
                mimetype="application/json",
                status_code=503
            )
        
        personality_id = req.params.get('personality_id')
        time_range_hours = int(req.params.get('time_range_hours', 24))
        
        # Get performance report
        report = performance_monitor.get_performance_report(personality_id, time_range_hours)
        
        return func.HttpResponse(
            json.dumps({
                "report": report,
                "parameters": {
                    "personality_id": personality_id,
                    "time_range_hours": time_range_hours
                },
                "generated_at": datetime.now().isoformat()
            }, default=str),
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
        logger.error(f"Failed to get performance report: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to generate performance report",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )

async def get_performance_alerts(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get active performance alerts.
    
    Query Parameters:
        - personality_id: Filter by specific personality (optional)
    """
    try:
        if not PERFORMANCE_SERVICES_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Performance services not available",
                    "alerts": []
                }),
                mimetype="application/json",
                status_code=503
            )
        
        personality_id = req.params.get('personality_id')
        
        # Get active alerts
        alerts = performance_monitor.get_active_alerts(personality_id)
        
        return func.HttpResponse(
            json.dumps({
                "alerts": alerts,
                "count": len(alerts),
                "timestamp": datetime.now().isoformat()
            }, default=str),
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
        logger.error(f"Failed to get performance alerts: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to load performance alerts",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )

async def resolve_alert(req: func.HttpRequest) -> func.HttpResponse:
    """
    Resolve a performance alert.
    
    Expected JSON body:
    {
        "alert_id": "alert_123"
    }
    """
    try:
        if not PERFORMANCE_SERVICES_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Performance services not available"
                }),
                mimetype="application/json",
                status_code=503
            )
        
        body = req.get_json()
        if not body:
            raise ValueError("Request body is required")
        
        alert_id = body.get('alert_id')
        if not alert_id:
            raise ValueError("alert_id is required")
        
        # Resolve alert
        success = performance_monitor.resolve_alert(alert_id)
        
        if success:
            return func.HttpResponse(
                json.dumps({
                    "message": f"Alert {alert_id} resolved successfully",
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
            return func.HttpResponse(
                json.dumps({
                    "error": f"Alert {alert_id} not found or already resolved"
                }),
                mimetype="application/json",
                status_code=404
            )
        
    except Exception as e:
        logger.error(f"Failed to resolve alert: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to resolve alert",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

async def get_optimization_recommendations(req: func.HttpRequest) -> func.HttpResponse:
    """
    Get performance optimization recommendations.
    
    Query Parameters:
        - personality_id: Filter by specific personality (optional)
    """
    try:
        if not PERFORMANCE_SERVICES_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Performance services not available",
                    "recommendations": []
                }),
                mimetype="application/json",
                status_code=503
            )
        
        personality_id = req.params.get('personality_id')
        
        # Get optimization recommendations
        recommendations = performance_monitor.get_optimization_recommendations(personality_id)
        
        return func.HttpResponse(
            json.dumps({
                "recommendations": recommendations,
                "count": len(recommendations),
                "personality_id": personality_id,
                "generated_at": datetime.now().isoformat()
            }, default=str),
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
        logger.error(f"Failed to get optimization recommendations: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to load optimization recommendations",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )

async def warm_cache(req: func.HttpRequest) -> func.HttpResponse:
    """
    Warm cache for specific personality.
    
    Expected JSON body:
    {
        "personality_id": "krishna"
    }
    """
    try:
        if not PERFORMANCE_SERVICES_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Performance services not available"
                }),
                mimetype="application/json",
                status_code=503
            )
        
        body = req.get_json()
        if not body:
            raise ValueError("Request body is required")
        
        personality_id = body.get('personality_id')
        if not personality_id:
            raise ValueError("personality_id is required")
        
        # Warm cache
        success = await personality_cache_service.warm_cache(personality_id)
        
        if success:
            return func.HttpResponse(
                json.dumps({
                    "message": f"Cache warming initiated for {personality_id}",
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
            return func.HttpResponse(
                json.dumps({
                    "error": f"Cache warming failed for {personality_id}"
                }),
                mimetype="application/json",
                status_code=500
            )
        
    except Exception as e:
        logger.error(f"Failed to warm cache: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to warm cache",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

async def invalidate_cache(req: func.HttpRequest) -> func.HttpResponse:
    """
    Invalidate cache entries.
    
    Expected JSON body:
    {
        "personality_id": "krishna",  // optional
        "cache_type": "response_cache",  // optional
        "key": "specific_key"  // optional
    }
    """
    try:
        if not PERFORMANCE_SERVICES_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Performance services not available"
                }),
                mimetype="application/json",
                status_code=503
            )
        
        body = req.get_json()
        if not body:
            raise ValueError("Request body is required")
        
        personality_id = body.get('personality_id')
        cache_type_str = body.get('cache_type')
        key = body.get('key')
        
        # Convert cache type string to enum
        cache_type = None
        if cache_type_str:
            try:
                cache_type = CacheType(cache_type_str)
            except ValueError:
                raise ValueError(f"Invalid cache_type: {cache_type_str}")
        
        # Invalidate cache
        success = await personality_cache_service.invalidate(
            key=key,
            personality_id=personality_id,
            cache_type=cache_type
        )
        
        if success:
            return func.HttpResponse(
                json.dumps({
                    "message": "Cache invalidation completed",
                    "success": True,
                    "parameters": {
                        "personality_id": personality_id,
                        "cache_type": cache_type_str,
                        "key": key
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
        else:
            return func.HttpResponse(
                json.dumps({
                    "error": "Cache invalidation failed"
                }),
                mimetype="application/json",
                status_code=500
            )
        
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to invalidate cache",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=400
        )

async def optimize_cache(req: func.HttpRequest) -> func.HttpResponse:
    """
    Optimize cache performance and cleanup.
    """
    try:
        if not PERFORMANCE_SERVICES_AVAILABLE:
            return func.HttpResponse(
                json.dumps({
                    "error": "Performance services not available"
                }),
                mimetype="application/json",
                status_code=503
            )
        
        # Optimize cache
        optimization_results = await personality_cache_service.optimize_cache()
        
        return func.HttpResponse(
            json.dumps({
                "message": "Cache optimization completed",
                "results": optimization_results,
                "timestamp": datetime.now().isoformat()
            }, default=str),
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
        logger.error(f"Failed to optimize cache: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Failed to optimize cache",
                "message": str(e)
            }),
            mimetype="application/json",
            status_code=500
        )