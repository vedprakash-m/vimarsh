"""
Personalities blueprint — personalities/active.

Extracted from function_app.py (lines 778-826).
"""

import azure.functions as func
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

bp = func.Blueprint()


def _cors():
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "https://vimarsh.vedprakash.net",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }


@bp.route(route="personalities/active", methods=["GET"])
async def get_active_personalities(req: func.HttpRequest) -> func.HttpResponse:
    """Get list of active personalities with enhanced filtering"""
    try:
        from routes.shared_services import (
            database_personality_available,
            personality_models_available,
            FALLBACK_PERSONALITIES,
            get_personality_list,
            get_personalities_by_domain,
        )

        domain = req.params.get("domain", "all")
        active_only = req.params.get("active_only", "false").lower() == "true"
        logger.info(f"🎭 Getting personalities - domain: {domain}, active_only: {active_only}")

        if database_personality_available or personality_models_available:
            if domain == "all":
                personalities_data = await get_personality_list()
                if isinstance(personalities_data, list) and personalities_data and isinstance(personalities_data[0], dict):
                    personalities = personalities_data
                else:
                    personalities = []
            else:
                personality_configs = await get_personalities_by_domain(domain)
                if isinstance(personality_configs, list):
                    personalities = personality_configs
                else:
                    personalities = []
                    if isinstance(personality_configs, dict):
                        for config in personality_configs.values():
                            if hasattr(config, "id") and hasattr(config, "name"):
                                personalities.append({
                                    "id": config.id,
                                    "name": config.name,
                                    "domain": config.domain.value if hasattr(config.domain, "value") else str(config.domain),
                                    "description": config.description,
                                })

            all_data = await get_personality_list()
            if isinstance(all_data, list) and all_data and isinstance(all_data[0], dict):
                domains = list(set(p.get("domain", "unknown") for p in all_data))
            else:
                domains = ["spiritual", "scientific", "historical", "philosophical"]
        else:
            if domain == "all":
                filtered = FALLBACK_PERSONALITIES
            else:
                filtered = {k: v for k, v in FALLBACK_PERSONALITIES.items() if v["domain"] == domain}

            personalities = [
                {"id": pid, "name": info["name"], "domain": info["domain"], "description": info["description"]}
                for pid, info in filtered.items()
            ]
            domains = list(set(p["domain"] for p in FALLBACK_PERSONALITIES.values()))

        if "personalities" not in locals():
            personalities = []

        response_data = {
            "personalities": personalities,
            "total": len(personalities),
            "domains": domains,
            "service_mode": "database" if database_personality_available else ("enhanced" if personality_models_available else "fallback"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"✅ Returning {len(personalities)} personalities")
        return func.HttpResponse(json.dumps(response_data), status_code=200, headers=_cors())

    except Exception as e:
        logger.error(f"❌ Error getting personalities: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get personalities", "details": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500, headers=_cors(),
        )
