"""
Diagnostics blueprint — diagnostic, test, health, health/embeddings.

Extracted from function_app.py (lines 296-776).
"""

import azure.functions as func
import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

bp = func.Blueprint()

# ── shared references (lazy imports avoid circular deps) ─────────────────────

def _cors():
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "https://vimarsh.vedmishra.com",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }


def _service_flags():
    """Lazy-import service availability flags from the shared context."""
    try:
        from routes.shared_services import (
            personality_models_available,
            personality_service_available,
            enhanced_llm_available,
            enhanced_rag_available,
            memory_service_available,
            database_personality_available,
            FALLBACK_PERSONALITIES,
            get_personality_list,
            azure_chat_deployment,
        )
        return {
            "personality_models_available": personality_models_available,
            "personality_service_available": personality_service_available,
            "enhanced_llm_available": enhanced_llm_available,
            "enhanced_rag_available": enhanced_rag_available,
            "memory_service_available": memory_service_available,
            "database_personality_available": database_personality_available,
            "FALLBACK_PERSONALITIES": FALLBACK_PERSONALITIES,
            "get_personality_list": get_personality_list,
            "azure_chat_deployment": azure_chat_deployment,
        }
    except ImportError:
        return None


# ── routes ───────────────────────────────────────────────────────────────────

@bp.route(route="diagnostic", methods=["GET"])
async def diagnostic_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Diagnostic endpoint to test Enhanced RAG service dependencies"""
    try:
        logger.info("🧪 Diagnostic endpoint triggered.")

        ctx = _service_flags() or {}
        azure_chat_deployment = ctx.get("azure_chat_deployment", "vimarsh-chat-gpt5mini")

        diagnostic_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tests": {},
            "summary": {},
        }

        # Test 1 – environment variables
        required_vars = [
            "AZURE_COSMOS_CONNECTION_STRING",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
            "AZURE_COSMOS_DATABASE_NAME",
            "AZURE_COSMOS_CONTAINER_NAME",
        ]
        env_test = {"missing": [], "present": []}
        for var in required_vars:
            value = os.getenv(var)
            if value:
                env_test["present"].append({"var": var, "length": len(value)})
            else:
                env_test["missing"].append(var)
        diagnostic_results["tests"]["environment_variables"] = env_test

        # Test 2 – package imports
        import_test = {}
        try:
            from openai import AzureOpenAI  # noqa: F401
            import_test["azure_openai"] = "available"
        except ImportError as e:
            import_test["azure_openai"] = f"missing: {e}"
        try:
            import azure.cosmos.cosmos_client  # noqa: F401
            import_test["azure_cosmos"] = "available"
        except ImportError as e:
            import_test["azure_cosmos"] = f"missing: {e}"
        diagnostic_results["tests"]["package_imports"] = import_test

        # Test 3 – Cosmos DB connection
        cosmos_test = {"status": "unknown", "error": None}
        try:
            connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
            if connection_string:
                import azure.cosmos.cosmos_client as cosmos_client
                client = cosmos_client.CosmosClient.from_connection_string(connection_string)
                db_name = os.getenv("AZURE_COSMOS_DATABASE_NAME", "vimarsh-multi-personality")
                ctr_name = os.getenv("AZURE_COSMOS_CONTAINER_NAME", "personality_vectors")
                database = client.get_database_client(db_name)
                container = database.get_container_client(ctr_name)
                container.read()
                cosmos_test["status"] = "connected"
                cosmos_test["database"] = db_name
                cosmos_test["container"] = ctr_name
            else:
                cosmos_test["status"] = "no_connection_string"
        except Exception as e:
            cosmos_test["status"] = "failed"
            cosmos_test["error"] = str(e)
        diagnostic_results["tests"]["cosmos_db"] = cosmos_test

        # Test 4 – Azure OpenAI Chat
        azure_openai_test = {"status": "unknown", "error": None}
        try:
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if endpoint and api_key:
                from openai import AzureOpenAI
                client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version="2024-08-01-preview")
                response = client.chat.completions.create(
                    model=azure_chat_deployment,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=50,
                )
                if response and response.choices:
                    azure_openai_test["status"] = "working"
                    azure_openai_test["deployment"] = azure_chat_deployment
                    azure_openai_test["response_sample"] = response.choices[0].message.content[:100]
                else:
                    azure_openai_test["status"] = "no_response"
            else:
                azure_openai_test["status"] = "no_credentials"
        except Exception as e:
            azure_openai_test["status"] = "failed"
            azure_openai_test["error"] = str(e)
        diagnostic_results["tests"]["azure_openai_chat"] = azure_openai_test

        # Test 5 – RAG service
        rag_test = {"status": "unknown", "error": None}
        try:
            from services.enhanced_rag_service_v6 import EnhancedRAGService
            EnhancedRAGService()
            rag_test["status"] = "initialized"
        except Exception as e:
            rag_test["status"] = "failed"
            rag_test["error"] = str(e)
        diagnostic_results["tests"]["enhanced_rag_service"] = rag_test

        # Summary
        env_ok = len(env_test["missing"]) == 0
        imports_ok = all("available" in s for s in import_test.values())
        cosmos_ok = cosmos_test["status"] == "connected"
        openai_ok = azure_openai_test["status"] == "working"
        rag_ok = rag_test["status"] == "initialized"

        diagnostic_results["summary"] = {
            "environment_variables": "pass" if env_ok else "fail",
            "package_imports": "pass" if imports_ok else "fail",
            "cosmos_db": "pass" if cosmos_ok else "fail",
            "azure_openai_chat": "pass" if openai_ok else "fail",
            "enhanced_rag_service": "pass" if rag_ok else "fail",
            "overall_status": "pass" if all([env_ok, imports_ok, cosmos_ok, openai_ok, rag_ok]) else "fail",
        }

        return func.HttpResponse(json.dumps(diagnostic_results, indent=2), status_code=200, headers=_cors())

    except Exception as e:
        logger.error(f"❌ Diagnostic endpoint error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Diagnostic test failed", "message": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="test", methods=["GET", "POST"])
def test_simple(req: func.HttpRequest) -> func.HttpResponse:
    """Simple test endpoint to verify basic functionality"""
    try:
        logger.info("🧪 Simple test endpoint triggered.")
        try:
            req_body = req.get_json()
            if not req_body:
                req_body = {}
        except Exception:
            req_body = {}

        ctx = _service_flags() or {}
        response_data = {
            "status": "success",
            "message": "Simple test endpoint working",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "received_data": req_body,
            "services_status": {
                "personality_service_available": ctx.get("personality_service_available", False),
                "enhanced_llm_available": ctx.get("enhanced_llm_available", False),
                "enhanced_rag_available": ctx.get("enhanced_rag_available", False),
                "memory_service_available": ctx.get("memory_service_available", False),
            },
        }
        return func.HttpResponse(json.dumps(response_data, indent=2), status_code=200, headers=_cors())

    except Exception as e:
        logger.error(f"❌ Simple test endpoint error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Simple test error", "message": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="health", methods=["GET"])
async def health_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced health check endpoint with comprehensive service status"""
    try:
        from core.capability_manifest import capability_manifest_service

        ctx = _service_flags() or {}
        FALLBACK_PERSONALITIES = ctx.get("FALLBACK_PERSONALITIES", {})
        database_personality_available = ctx.get("database_personality_available", False)
        personality_models_available = ctx.get("personality_models_available", False)
        get_personality_list = ctx.get("get_personality_list")

        manifest = capability_manifest_service.generate_manifest()

        if FALLBACK_PERSONALITIES:
            personality_ids = list(FALLBACK_PERSONALITIES.keys())
            total_personalities = len(personality_ids)
        elif (database_personality_available or personality_models_available) and get_personality_list:
            personalities = await get_personality_list()
            total_personalities = len(personalities)
            personality_ids = [p["id"] for p in personalities]
        else:
            personality_ids = []
            total_personalities = 0

        health_data = {
            "status": "healthy" if manifest.overall_status.value == "operational" else "degraded",
            "service": "vimarsh-enhanced",
            "version": "2.1-capability-aware",
            "architecture": "modular-with-fallbacks",
            "timestamp": manifest.timestamp,
            "deployment_readiness": manifest.deployment_readiness,
            "overall_status": manifest.overall_status.value,
            "personalities_available": total_personalities,
            "personalities": personality_ids,
            "services": {
                name: {
                    "available": cap.available,
                    "status": cap.status.value,
                    "fallback_mode": cap.fallback_mode.value,
                    "error_message": cap.error_message,
                    "failure_rate_24h": cap.failure_rate_24h,
                    "response_time_ms": cap.response_time_ms,
                    "health_details": cap.health_details or {},
                }
                for name, cap in manifest.capabilities.items()
            },
            "legacy_services": {
                "personality_models": personality_models_available,
                "personality_service": ctx.get("personality_service_available", False),
                "memory_service": ctx.get("memory_service_available", False),
                "fallback_mode": not (personality_models_available and ctx.get("personality_service_available", False)),
            },
            "active_fallbacks": manifest.active_fallbacks,
            "recommendations": manifest.recommendations,
            "user_impact": manifest.user_impact,
            "service_counts": {
                "operational": sum(1 for cap in manifest.capabilities.values() if cap.status.value == "operational"),
                "degraded": sum(1 for cap in manifest.capabilities.values() if cap.status.value == "degraded"),
                "unavailable": sum(1 for cap in manifest.capabilities.values() if cap.status.value == "unavailable"),
            },
        }

        return func.HttpResponse(json.dumps(health_data, indent=2), status_code=200, headers=_cors())

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return func.HttpResponse(
            json.dumps({
                "status": "degraded",
                "service": "vimarsh-enhanced",
                "version": "2.1-fallback",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "fallback_reason": "Capability manifest service unavailable",
            }),
            status_code=500,
            headers=_cors(),
        )


@bp.route(route="health/embeddings", methods=["GET"])
async def health_embeddings_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Health check for embedding quality across all personalities."""
    try:
        import statistics
        from azure.cosmos import CosmosClient

        connection_string = os.getenv("AZURE_COSMOS_CONNECTION_STRING")
        if not connection_string:
            return func.HttpResponse(
                json.dumps({"status": "error", "message": "AZURE_COSMOS_CONNECTION_STRING not configured"}),
                status_code=500,
                headers=_cors(),
            )

        cosmos_client = CosmosClient.from_connection_string(connection_string)
        database = cosmos_client.get_database_client("vimarsh-multi-personality")
        container = database.get_container_client("personality_vectors")

        all_personalities = [
            "krishna", "buddha", "jesus_christ", "rumi", "swami_vivekananda",
            "marcus_aurelius", "lao_tzu", "confucius", "aristotle", "plato", "socrates",
            "chanakya", "abraham_lincoln", "benjamin_franklin", "george_washington",
            "mahatma_gandhi", "martin_luther_king_jr",
            "albert_einstein", "isaac_newton", "nikola_tesla", "archimedes", "leonardo_da_vinci",
            "rabindranath_tagore", "william_shakespeare",
            "sigmund_freud",
        ]

        name_variations = {
            "buddha": ["buddha", "Buddha"],
            "jesus_christ": ["jesus_christ", "Jesus Christ", "Jesus"],
            "rumi": ["rumi", "Rumi"],
            "marcus_aurelius": ["marcus_aurelius", "Marcus Aurelius"],
            "lao_tzu": ["lao_tzu", "Lao Tzu"],
            "confucius": ["confucius", "Confucius"],
            "chanakya": ["chanakya", "Chanakya"],
            "abraham_lincoln": ["abraham_lincoln", "Lincoln"],
            "albert_einstein": ["albert_einstein", "Einstein"],
            "isaac_newton": ["isaac_newton", "Newton"],
            "nikola_tesla": ["nikola_tesla", "Tesla"],
        }

        results = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_personalities": len(all_personalities),
            "healthy_embeddings": 0,
            "zero_embeddings": 0,
            "missing_embeddings": 0,
            "personalities": {},
        }

        for personality in all_personalities:
            variations = name_variations.get(personality, [personality])
            found = False

            for var in variations:
                query = (
                    f"SELECT TOP 1 c.embedding FROM c "
                    f"WHERE (c.personality_id = '{var}' OR c.personality = '{var}') "
                    f"AND IS_DEFINED(c.embedding)"
                )
                try:
                    items = list(container.query_items(query=query, enable_cross_partition_query=True))
                    if items:
                        emb = items[0].get("embedding", [])
                        if emb and len(emb) == 768:
                            found = True
                            non_zero = sum(1 for v in emb if v != 0)
                            if non_zero == 0:
                                results["personalities"][personality] = {
                                    "status": "zero_embedding", "non_zero_count": 0, "dimension": 768,
                                }
                                results["zero_embeddings"] += 1
                                results["status"] = "degraded"
                            elif non_zero < 100:
                                results["personalities"][personality] = {
                                    "status": "suspicious", "non_zero_count": non_zero, "dimension": 768,
                                    "warning": "Very few non-zero values",
                                }
                                results["healthy_embeddings"] += 1
                            else:
                                avg_mag = statistics.mean([abs(v) for v in emb])
                                results["personalities"][personality] = {
                                    "status": "healthy", "non_zero_count": non_zero, "dimension": 768,
                                    "avg_magnitude": round(avg_mag, 6),
                                }
                                results["healthy_embeddings"] += 1
                            break
                except Exception as e:
                    logger.warning(f"Query error for {var}: {e}")

            if not found:
                results["personalities"][personality] = {"status": "missing", "message": "No documents with embeddings found"}
                results["missing_embeddings"] += 1
                results["status"] = "degraded"

        if results["zero_embeddings"] > 0 or results["missing_embeddings"] > 0:
            results["status"] = "degraded"
            results["recommendation"] = f"Re-embed {results['zero_embeddings']} personalities with zero embeddings"

        status_code = 200 if results["status"] == "healthy" else 503
        return func.HttpResponse(json.dumps(results, indent=2), status_code=status_code, headers=_cors())

    except Exception as e:
        logger.error(f"❌ Embeddings health check failed: {e}")
        return func.HttpResponse(
            json.dumps({"status": "error", "message": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500,
            headers=_cors(),
        )
