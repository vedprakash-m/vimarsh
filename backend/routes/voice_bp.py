"""
Voice blueprint — voice/synthesize, voice/info.

Extracted from function_app.py (lines 3460-3677).
"""

import azure.functions as func
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

bp = func.Blueprint()

# ── service init ─────────────────────────────────────────────────────────────

azure_speech_service = None
azure_speech_available = False

try:
    from services.azure_speech_service import AzureSpeechService, get_speech_service
    azure_speech_service = get_speech_service()
    azure_speech_available = azure_speech_service.is_available
    if azure_speech_available:
        logger.info("🎙️ Azure Speech Service initialized (voice blueprint)")
    else:
        logger.warning("⚠️ Azure Speech Service not configured (missing AZURE_SPEECH_KEY)")
except ImportError as e:
    logger.warning(f"⚠️ Azure Speech Service not available: {e}")
except Exception as e:
    logger.warning(f"⚠️ Azure Speech Service init failed: {e}")


def _cors():
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "https://vimarsh.vedmishra.com",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }


# ── routes ───────────────────────────────────────────────────────────────────

@bp.route(route="voice/synthesize", methods=["POST", "OPTIONS"])
async def voice_synthesize(req: func.HttpRequest) -> func.HttpResponse:
    """Synthesize speech from text using personality-specific Azure Neural Voices."""
    if req.method == "OPTIONS":
        return func.HttpResponse(
            "", status_code=204,
            headers={**_cors(), "Access-Control-Allow-Headers": "Content-Type, Authorization"},
        )

    try:
        logger.info("🎙️ Voice synthesis request received")

        if not azure_speech_available:
            return func.HttpResponse(
                json.dumps({
                    "error": "Voice synthesis service not available",
                    "message": "Azure Speech Service is not configured",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }),
                status_code=503, headers=_cors(),
            )

        try:
            req_body = req.get_json()
        except Exception:
            return func.HttpResponse(
                json.dumps({"error": "Invalid request body", "message": "Expected JSON with 'text' field"}),
                status_code=400, headers=_cors(),
            )

        text = req_body.get("text", "").strip()
        if not text:
            return func.HttpResponse(
                json.dumps({"error": "Missing required field", "message": "The 'text' field is required and cannot be empty"}),
                status_code=400, headers=_cors(),
            )

        personality = req_body.get("personality", "krishna")
        audio_format = req_body.get("format", "mp3")

        valid_formats = ["mp3", "mp3-hd", "wav", "ogg"]
        if audio_format not in valid_formats:
            return func.HttpResponse(
                json.dumps({"error": "Invalid audio format", "message": f"Format must be one of: {', '.join(valid_formats)}"}),
                status_code=400, headers=_cors(),
            )

        audio_data = azure_speech_service.synthesize_speech(
            text=text, personality=personality, audio_format=audio_format, use_ssml=True,
        )

        if audio_data is None:
            return func.HttpResponse(
                json.dumps({"error": "Speech synthesis failed", "message": "Unable to generate audio for the provided text"}),
                status_code=500, headers=_cors(),
            )

        content_types = {"mp3": "audio/mpeg", "mp3-hd": "audio/mpeg", "wav": "audio/wav", "ogg": "audio/ogg"}
        content_type = content_types.get(audio_format, "audio/mpeg")

        logger.info(f"✅ Voice synthesis completed for {personality}: {len(audio_data)} bytes")

        return func.HttpResponse(
            audio_data,
            status_code=200,
            headers={
                "Content-Type": content_type,
                "Content-Length": str(len(audio_data)),
                "Access-Control-Allow-Origin": "https://vimarsh.vedmishra.com",
                "Access-Control-Allow-Credentials": "true",
                "Cache-Control": "public, max-age=3600",
            },
        )

    except ValueError as e:
        logger.error(f"❌ Voice synthesis configuration error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Service configuration error", "message": str(e)}),
            status_code=503, headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Voice synthesis error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Voice synthesis failed", "message": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500, headers=_cors(),
        )


@bp.route(route="voice/info", methods=["GET"])
async def voice_info(req: func.HttpRequest) -> func.HttpResponse:
    """Get information about available voice configurations and service status."""
    try:
        from config.voice_config import get_all_voice_configs

        voice_configs = get_all_voice_configs()

        personalities = {}
        for name, config in voice_configs.items():
            if "_" in name and name.replace("_", "") not in name:
                personalities[name] = {
                    "voice_name": config.voice_name,
                    "gender": config.gender,
                    "locale": config.locale,
                    "style": config.style,
                    "description": config.description,
                }

        return func.HttpResponse(
            json.dumps(
                {
                    "service_available": azure_speech_available,
                    "total_personalities": len(personalities),
                    "personalities": personalities,
                    "supported_formats": ["mp3", "mp3-hd", "wav", "ogg"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                indent=2,
            ),
            status_code=200, headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Voice info error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get voice info", "message": str(e)}),
            status_code=500, headers=_cors(),
        )
