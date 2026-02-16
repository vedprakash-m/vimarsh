"""
Guidance blueprint — guidance endpoint, template fallback helpers.

Extracted from function_app.py (lines 2161-2759).
This is the core RAG pipeline entrypoint.
"""

import azure.functions as func
import json
import logging
from datetime import datetime, timezone
from typing import Optional

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


# ── lazy service accessor ───────────────────────────────────────────────────

def _ctx():
    """Lazy-import shared services to avoid circular imports."""
    from routes.shared_services import (
        FALLBACK_PERSONALITIES,
        database_personality_available,
        personality_models_available,
        personality_service_available,
        enhanced_llm_available,
        enhanced_rag_available,
        memory_service_available,
        hierarchical_memory_available,
        engagement_available,
        optimized_personality_service,
        enhanced_llm_service,
        enhanced_rag_service,
        conversation_memory_service,
        hierarchical_memory_service,
        database_personality_service,
        engagement_service_instance,
        achievement_service_instance,
        get_personality_list,
        get_personality_config,
    )
    return {
        "FALLBACK_PERSONALITIES": FALLBACK_PERSONALITIES,
        "database_personality_available": database_personality_available,
        "personality_models_available": personality_models_available,
        "personality_service_available": personality_service_available,
        "enhanced_llm_available": enhanced_llm_available,
        "enhanced_rag_available": enhanced_rag_available,
        "memory_service_available": memory_service_available,
        "hierarchical_memory_available": hierarchical_memory_available,
        "engagement_available": engagement_available,
        "optimized_personality_service": optimized_personality_service,
        "enhanced_llm_service": enhanced_llm_service,
        "enhanced_rag_service": enhanced_rag_service,
        "conversation_memory_service": conversation_memory_service,
        "hierarchical_memory_service": hierarchical_memory_service,
        "database_personality_service": database_personality_service,
        "engagement_service_instance": engagement_service_instance,
        "achievement_service_instance": achievement_service_instance,
        "get_personality_list": get_personality_list,
        "get_personality_config": get_personality_config,
    }


# ── mutable module-level state for lazy RAG init ─────────────────────────────

_rag_service_initialized = False
_rag_service_instance = None
_rag_available = True  # starts True, set False on init failure


def _get_rag_service():
    global _rag_service_initialized, _rag_service_instance, _rag_available
    if _rag_service_initialized:
        return _rag_service_instance
    try:
        from services.enhanced_rag_service_v6 import EnhancedRAGService
        _rag_service_instance = EnhancedRAGService()
        _rag_service_initialized = True
        logger.info("✅ Enhanced RAG service initialized (guidance blueprint)")
        return _rag_service_instance
    except Exception as init_err:
        logger.warning(f"⚠️ Enhanced RAG init failed: {init_err}")
        _rag_service_initialized = True  # prevent retries
        _rag_available = False
        return None


# ── template fallback ────────────────────────────────────────────────────────

_FALLBACK_RESPONSES = {
    "krishna": (
        "Beloved devotee, in the Bhagavad Gita 2.47, I teach: "
        '"You have the right to perform your prescribed duty, but not to the fruits of action." '
        "This timeless wisdom guides us to act with devotion while surrendering attachment to outcomes. "
        "Focus on righteous action with love and dedication. May you find peace in dharmic living. 🙏"
    ),
    "buddha": (
        "Dear friend, suffering arises from attachment and craving. "
        "Through mindful awareness and the Noble Eightfold Path, we can find liberation. "
        "Practice compassion for all beings and remember — the present moment is all we truly have. "
        "May you find peace and wisdom on your path."
    ),
    "default": "I apologize, but I'm currently unable to provide personalized guidance. Please try again in a moment.",
}


async def _get_template_fallback_response(personality_id: str, ctx=None):
    """Get template fallback with metadata (database-first)."""
    ctx = ctx or _ctx()
    if ctx["database_personality_available"] or ctx["personality_models_available"]:
        try:
            config = await ctx["get_personality_config"](personality_id)
            if config and hasattr(config, "response_templates"):
                templates = config.response_templates
                if templates and templates.default_response:
                    response_text = templates.default_response
                else:
                    response_text = _FALLBACK_RESPONSES.get(personality_id, _FALLBACK_RESPONSES["default"])
            else:
                response_text = _FALLBACK_RESPONSES.get(personality_id, _FALLBACK_RESPONSES["default"])
        except Exception:
            response_text = _FALLBACK_RESPONSES.get(personality_id, _FALLBACK_RESPONSES["default"])
    else:
        response_text = _FALLBACK_RESPONSES.get(personality_id, _FALLBACK_RESPONSES["default"])

    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service_version": "fallback_v1.0",
        "response_source": "template_fallback",
        "memory_enhanced": False,
        "database_enhanced": ctx["database_personality_available"],
    }
    return response_text, metadata


# ── main guidance route ──────────────────────────────────────────────────────

@bp.route(route="guidance", methods=["POST"])
async def guidance_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Enhanced guidance endpoint with modular service integration."""
    try:
        ctx = _ctx()

        # ── parse request ────────────────────────────────────────────────
        try:
            query_data = req.get_json()
        except ValueError:
            return func.HttpResponse(json.dumps({"error": "Invalid JSON in request body"}), status_code=400, headers=_cors())

        if not query_data:
            return func.HttpResponse(json.dumps({"error": "Request body is required"}), status_code=400, headers=_cors())

        user_query = query_data.get("query", "").strip()
        personality_id = query_data.get("personality_id", "krishna")
        language = query_data.get("language", "English")

        # ── resolve user_id ──────────────────────────────────────────────
        user_id = query_data.get("user_id") or query_data.get("session_id")
        persistent_user_id = None
        try:
            from auth.enhanced_unified_auth_service import EnhancedUnifiedAuthService
            auth_service = EnhancedUnifiedAuthService()
            authenticated_user = await auth_service.extract_user_from_request(req)
            if authenticated_user:
                persistent_user_id = await auth_service.get_persistent_user_id(authenticated_user)
                logger.info(f"🔗 Persistent user ID: {persistent_user_id}")
        except Exception as auth_err:
            logger.warning(f"⚠️ Could not get persistent user ID: {auth_err}")

        if persistent_user_id:
            user_id = persistent_user_id
        elif not user_id:
            user_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(user_query[:50]) % 10000}"

        if not user_query:
            return func.HttpResponse(json.dumps({"error": "Query is required"}), status_code=400, headers=_cors())

        # ── validate personality ─────────────────────────────────────────
        get_personality_list = ctx["get_personality_list"]
        FALLBACK = ctx["FALLBACK_PERSONALITIES"]

        if ctx["database_personality_available"] or ctx["personality_models_available"]:
            data = await get_personality_list()
            valid_personalities = [p.get("id", "") for p in data if isinstance(p, dict)] if isinstance(data, list) else list(FALLBACK.keys())
        else:
            valid_personalities = list(FALLBACK.keys()) if not ctx["personality_service_available"] else ctx["optimized_personality_service"].get_available_personalities()

        if personality_id not in valid_personalities:
            logger.warning(f"Invalid personality: {personality_id}, defaulting to Krishna")
            personality_id = "krishna"

        # ── build conversation context (hierarchical → basic) ────────────
        conversation_context = ""
        conversation_id = None
        memory_enhanced_context = None
        session_id = query_data.get("session_id") or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if ctx["hierarchical_memory_available"] and ctx["hierarchical_memory_service"]:
            try:
                memory_enhanced_context = await ctx["hierarchical_memory_service"].assemble_working_memory(
                    user_id=user_id, personality_id=personality_id, session_id=session_id,
                    current_query=user_query, current_messages=[],
                )
                parts = []
                if memory_enhanced_context.user_profile_context:
                    parts.append(f"About the seeker:\n{memory_enhanced_context.user_profile_context}")
                if memory_enhanced_context.relationship_context:
                    parts.append(f"Our journey together:\n{memory_enhanced_context.relationship_context}")
                if memory_enhanced_context.recent_session_summaries:
                    parts.append("Previous conversations:\n" + "\n".join(f"- {s}" for s in memory_enhanced_context.recent_session_summaries[:3]))
                if memory_enhanced_context.relevant_past_insights:
                    parts.append("Relevant wisdom shared before:\n" + "\n".join(f"- {i}" for i in memory_enhanced_context.relevant_past_insights[:3]))
                if memory_enhanced_context.retrieved_memories:
                    parts.append("Related memories:\n" + "\n".join(f"- {m}" for m in memory_enhanced_context.retrieved_memories[:3]))
                conversation_context = "\n\n".join(parts)
                logger.info(f"🧠 Hierarchical memory context: {len(conversation_context)} chars, quality: {memory_enhanced_context.context_quality_score:.2f}")
            except Exception as e:
                logger.warning(f"⚠️ Hierarchical memory failed: {e}")

        if not conversation_context and ctx["memory_service_available"]:
            try:
                conversation_id = await ctx["conversation_memory_service"].start_conversation(user_id=user_id, personality_id=personality_id)
                context_data = await ctx["conversation_memory_service"].get_conversation_context(conversation_id=conversation_id, user_id=user_id)
                if context_data and hasattr(context_data, "recent_messages") and context_data.recent_messages:
                    from models.conversation_models import MessageType
                    msgs = []
                    for msg in context_data.recent_messages[-3:]:
                        if msg.message_type == MessageType.USER_QUERY:
                            msgs.append(f"Previous question: {msg.content}")
                        elif msg.message_type == MessageType.PERSONALITY_RESPONSE:
                            msgs.append(f"My previous response: {msg.content[:200]}...")
                    conversation_context = "\n".join(msgs)
                logger.info(f"🧠 Basic conversation context: {len(conversation_context)} chars")
            except Exception as mem_err:
                logger.warning(f"⚠️ Failed to retrieve conversation context: {mem_err}")

        # ── generate response (RAG → LLM → personality → template) ─────
        response_source = "template_fallback"
        response_text = None
        response_metadata = {}

        # Attempt 1: Enhanced RAG
        if ctx["enhanced_rag_available"]:
            try:
                rag = _get_rag_service()
                if rag:
                    user_preferences = None
                    try:
                        if user_id:
                            from services.preferences_service import preferences_service as prefs_svc
                            user_preferences = prefs_svc.get_preferences(user_id)
                    except Exception:
                        pass

                    rag_response = await rag.generate_enhanced_response(
                        query=user_query, personality_id=personality_id,
                        context=conversation_context, user_preferences=user_preferences,
                    )
                    if rag_response and rag_response.content:
                        response_text = rag_response.content
                        response_metadata = {
                            "content_backed": rag_response.content_backed,
                            "confidence_score": rag_response.confidence_score,
                            "citations": rag_response.rag_context.citations if rag_response.rag_context else [],
                            "chunks_used": len(rag_response.rag_context.relevant_chunks) if rag_response.rag_context else 0,
                            "retrieval_method": rag_response.rag_context.retrieval_method if rag_response.rag_context else "none",
                            "avg_similarity": rag_response.rag_context.avg_similarity_score if rag_response.rag_context else 0.0,
                            "memory_enhanced": bool(conversation_context),
                            **rag_response.metadata,
                        }
                        response_source = rag_response.response_source
                        logger.info(f"✅ RAG response (confidence: {rag_response.confidence_score:.3f}, content-backed: {rag_response.content_backed})")
                    else:
                        raise Exception("RAG returned empty")
                else:
                    raise Exception("RAG service unavailable")
            except Exception as rag_err:
                logger.warning(f"⚠️ RAG failed: {rag_err}")

        # Attempt 2: Enhanced LLM
        if response_text is None and ctx["enhanced_llm_available"] and ctx["enhanced_llm_service"]:
            try:
                eq = f"Previous conversation context:\n{conversation_context}\n\nCurrent question: {user_query}" if conversation_context else user_query
                llm_resp = await ctx["enhanced_llm_service"].generate_response_with_monitoring(query=eq, personality_id=personality_id, language=language)
                if llm_resp and llm_resp.get("success"):
                    response_text = llm_resp["content"]
                    response_metadata = llm_resp.get("metadata", {})
                    response_metadata["memory_enhanced"] = bool(conversation_context)
                    response_metadata["content_backed"] = False
                    response_source = llm_resp.get("source", "enhanced_llm")
                    logger.info(f"✅ LLM response (source: {response_source})")
                else:
                    raise Exception("LLM returned no valid response")
            except Exception as llm_err:
                logger.warning(f"⚠️ LLM failed: {llm_err}")

        # Attempt 3: Standard personality service
        if response_text is None and ctx["personality_service_available"] and ctx["optimized_personality_service"]:
            eq = f"Previous conversation context:\n{conversation_context}\n\nCurrent question: {user_query}" if conversation_context else user_query
            srv_resp = ctx["optimized_personality_service"].generate_response(eq, personality_id, language)
            response_text = srv_resp["content"]
            response_metadata = srv_resp["metadata"]
            response_metadata["memory_enhanced"] = bool(conversation_context)
            response_metadata["content_backed"] = False
            response_source = "personality_service"

        # Attempt 4: Template fallback (always works)
        if response_text is None:
            response_text, response_metadata = await _get_template_fallback_response(personality_id, ctx)
            response_metadata["content_backed"] = False
            response_source = "template_fallback"

        # ── store in memory ──────────────────────────────────────────────
        if ctx["hierarchical_memory_available"] and ctx["hierarchical_memory_service"]:
            try:
                from models.memory_models import MessageRole, EmotionalTone
                emotional_keywords = {
                    EmotionalTone.TROUBLED: ["worried", "anxious", "stressed", "struggling", "lost", "confused"],
                    EmotionalTone.HOPEFUL: ["hope", "wish", "dream", "aspire", "looking forward"],
                    EmotionalTone.CURIOUS: ["what", "how", "why", "explain", "understand", "tell me"],
                    EmotionalTone.GRATEFUL: ["thank", "grateful", "appreciate", "blessed"],
                    EmotionalTone.SEEKING: ["help", "guide", "seek", "searching", "need"],
                }
                user_emotion = EmotionalTone.NEUTRAL
                ql = user_query.lower()
                for emotion, kws in emotional_keywords.items():
                    if any(kw in ql for kw in kws):
                        user_emotion = emotion
                        break

                await ctx["hierarchical_memory_service"].store_message(user_id=user_id, personality_id=personality_id, session_id=session_id, role=MessageRole.USER, content=user_query, emotional_tone=user_emotion)
                await ctx["hierarchical_memory_service"].store_message(user_id=user_id, personality_id=personality_id, session_id=session_id, role=MessageRole.ASSISTANT, content=response_text, emotional_tone=EmotionalTone.CALM)
                logger.info(f"💾 Stored in hierarchical memory (session: {session_id})")
            except Exception as e:
                logger.warning(f"⚠️ Hierarchical memory store failed: {e}")
        elif ctx["memory_service_available"] and ctx["conversation_memory_service"] and conversation_id:
            try:
                await ctx["conversation_memory_service"].add_message(conversation_id=conversation_id, user_id=user_id, personality_id=personality_id, message_type="user_query", content=user_query)
                await ctx["conversation_memory_service"].add_message(conversation_id=conversation_id, user_id=user_id, personality_id=personality_id, message_type="personality_response", content=response_text)
                logger.info("💾 Stored conversation exchange in memory")
            except Exception as e:
                logger.error(f"❌ Failed to store conversation: {e}")

        # ── personality info ─────────────────────────────────────────────
        if ctx["personality_models_available"]:
            config = await ctx["get_personality_config"](personality_id)
            if config and hasattr(config, "id"):
                personality_info = {"id": config.id, "name": config.name, "domain": config.domain.value, "description": config.description}
            else:
                fi = FALLBACK[personality_id]
                personality_info = {"id": personality_id, "name": fi["name"], "domain": fi["domain"], "description": fi["description"]}
        else:
            fi = FALLBACK[personality_id]
            personality_info = {"id": personality_id, "name": fi["name"], "domain": fi["domain"], "description": fi["description"]}

        # ── engagement tracking (non-blocking) ───────────────────────────
        newly_unlocked = []
        engagement_data = None
        if ctx["engagement_available"] and ctx["engagement_service_instance"] and user_id != "anonymous":
            try:
                await ctx["engagement_service_instance"].record_check_in(user_id)
                await ctx["engagement_service_instance"].record_activity(
                    user_id=user_id, activity_type="conversation",
                    metadata={"personality_id": personality_id, "domain": personality_info.get("domain", ""), "query_length": len(user_query), "response_length": len(response_text)},
                )
                engagement_data = await ctx["engagement_service_instance"].get_engagement_data(user_id)
                if engagement_data and ctx["achievement_service_instance"]:
                    stats = engagement_data.get("stats", {})
                    streaks = engagement_data.get("streaks", {})
                    metrics = {
                        "streak": streaks.get("current_streak", 0),
                        "total_conversations": stats.get("total_conversations", 0),
                        "personalities_met": stats.get("personalities_met", []),
                        "domains_explored": stats.get("domains_explored", []),
                        "total_insights_saved": stats.get("total_insights_saved", 0),
                        "total_shares": stats.get("total_shares", 0),
                        "onboarding_complete": True,
                    }
                    newly_unlocked = await ctx["achievement_service_instance"].check_and_unlock_achievements(user_id=user_id, metrics=metrics)
                    if newly_unlocked:
                        logger.info(f"🏆 {len(newly_unlocked)} achievements unlocked for {user_id}")
                logger.info(f"📊 Engagement tracked for {user_id}")
            except Exception as eng_err:
                logger.warning(f"⚠️ Engagement tracking failed (non-blocking): {eng_err}")

        # ── build response ───────────────────────────────────────────────
        response = {
            "response": response_text,
            "personality": personality_info,
            "metadata": {
                **response_metadata,
                "language": language,
                "query_length": len(user_query),
                "response_length": len(response_text),
                "service_mode": "enhanced" if ctx["enhanced_llm_available"] else ("standard" if ctx["personality_service_available"] else "fallback"),
                "response_source": response_source,
                "ai_generated": response_source not in ["template_fallback", "hardcoded_fallback"],
            },
        }
        if newly_unlocked:
            response["achievements_unlocked"] = newly_unlocked
        if engagement_data:
            streaks = engagement_data.get("streaks", {})
            response["engagement"] = {"current_streak": streaks.get("current_streak", 0), "streak_updated": True}

        logger.info(f"✅ {personality_info['name']} response generated successfully")
        return func.HttpResponse(json.dumps(response, indent=2), status_code=200, headers=_cors())

    except Exception as e:
        logger.error(f"❌ Error in guidance endpoint: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500, headers=_cors(),
        )
