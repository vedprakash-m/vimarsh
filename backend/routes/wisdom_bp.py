"""
Wisdom & sharing blueprint — wisdom-of-day, wisdom/history, wisdom/save,
share/track, share/{shareId}, og-image/{share_id}.

Extracted from function_app.py (lines 2761-3459).
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


# ── Wisdom of the day ───────────────────────────────────────────────────────

_WISDOM_COLLECTION = [
    {"quote": "The unexamined life is not worth living.", "personality_id": "socrates", "personality_name": "Socrates", "domain": "philosophical", "source": "Apology of Socrates"},
    {"quote": "Be the change you wish to see in the world.", "personality_id": "mahatma_gandhi", "personality_name": "Mahatma Gandhi", "domain": "leadership", "source": "Personal Philosophy"},
    {"quote": "You must not lose faith in humanity. Humanity is an ocean; if a few drops of the ocean are dirty, the ocean does not become dirty.", "personality_id": "mahatma_gandhi", "personality_name": "Mahatma Gandhi", "domain": "leadership", "source": "Personal Letters"},
    {"quote": "Imagination is more important than knowledge. Knowledge is limited. Imagination encircles the world.", "personality_id": "albert_einstein", "personality_name": "Albert Einstein", "domain": "scientific", "source": "Interview, 1929"},
    {"quote": "The important thing is not to stop questioning. Curiosity has its own reason for existence.", "personality_id": "albert_einstein", "personality_name": "Albert Einstein", "domain": "scientific", "source": "Personal Memoir"},
    {"quote": "Karmanye vadhikaraste ma phaleshu kadachana - You have the right to work, but not to the fruits of your work.", "personality_id": "krishna", "personality_name": "Lord Krishna", "domain": "spiritual", "source": "Bhagavad Gita 2.47"},
    {"quote": "The mind is everything. What you think you become.", "personality_id": "buddha", "personality_name": "Gautama Buddha", "domain": "spiritual", "source": "Dhammapada"},
    {"quote": "Peace comes from within. Do not seek it without.", "personality_id": "buddha", "personality_name": "Gautama Buddha", "domain": "spiritual", "source": "Buddhist Teachings"},
    {"quote": "The wound is the place where the Light enters you.", "personality_id": "rumi", "personality_name": "Rumi", "domain": "spiritual", "source": "Masnavi"},
    {"quote": "Let yourself be silently drawn by the strange pull of what you really love.", "personality_id": "rumi", "personality_name": "Rumi", "domain": "spiritual", "source": "Poetry Collection"},
    {"quote": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "personality_id": "aristotle", "personality_name": "Aristotle", "domain": "philosophical", "source": "Nicomachean Ethics"},
    {"quote": "To be, or not to be, that is the question.", "personality_id": "william_shakespeare", "personality_name": "William Shakespeare", "domain": "literary", "source": "Hamlet"},
    {"quote": "All the world's a stage, and all the men and women merely players.", "personality_id": "william_shakespeare", "personality_name": "William Shakespeare", "domain": "literary", "source": "As You Like It"},
    {"quote": "Arise, awake, and stop not till the goal is reached.", "personality_id": "swami_vivekananda", "personality_name": "Swami Vivekananda", "domain": "spiritual", "source": "Lectures and Discourses"},
    {"quote": "You cannot believe in God until you believe in yourself.", "personality_id": "swami_vivekananda", "personality_name": "Swami Vivekananda", "domain": "spiritual", "source": "Complete Works"},
    {"quote": "Love your neighbor as yourself.", "personality_id": "jesus_christ", "personality_name": "Jesus Christ", "domain": "spiritual", "source": "Gospel of Matthew 22:39"},
    {"quote": "The journey of a thousand miles begins with a single step.", "personality_id": "lao_tzu", "personality_name": "Lao Tzu", "domain": "philosophical", "source": "Tao Te Ching"},
    {"quote": "He who knows others is wise; he who knows himself is enlightened.", "personality_id": "lao_tzu", "personality_name": "Lao Tzu", "domain": "philosophical", "source": "Tao Te Ching"},
    {"quote": "It is not the strongest of the species that survives, but the most adaptable.", "personality_id": "marcus_aurelius", "personality_name": "Marcus Aurelius", "domain": "philosophical", "source": "Meditations"},
    {"quote": "Very little is needed to make a happy life; it is all within yourself, in your way of thinking.", "personality_id": "marcus_aurelius", "personality_name": "Marcus Aurelius", "domain": "philosophical", "source": "Meditations"},
    {"quote": "I have a dream that my four little children will one day live in a nation where they will not be judged by the color of their skin but by the content of their character.", "personality_id": "martin_luther_king_jr", "personality_name": "Martin Luther King Jr.", "domain": "leadership", "source": "I Have a Dream Speech"},
    {"quote": "Darkness cannot drive out darkness; only light can do that. Hate cannot drive out hate; only love can do that.", "personality_id": "martin_luther_king_jr", "personality_name": "Martin Luther King Jr.", "domain": "leadership", "source": "Strength to Love"},
    {"quote": "A house divided against itself cannot stand.", "personality_id": "abraham_lincoln", "personality_name": "Abraham Lincoln", "domain": "leadership", "source": "House Divided Speech"},
    {"quote": "In the end, it's not the years in your life that count. It's the life in your years.", "personality_id": "abraham_lincoln", "personality_name": "Abraham Lincoln", "domain": "leadership", "source": "Attributed"},
    {"quote": "If you tell the truth, you don't have to remember anything.", "personality_id": "benjamin_franklin", "personality_name": "Benjamin Franklin", "domain": "leadership", "source": "Poor Richard's Almanack"},
    {"quote": "An investment in knowledge pays the best interest.", "personality_id": "benjamin_franklin", "personality_name": "Benjamin Franklin", "domain": "leadership", "source": "The Way to Wealth"},
    {"quote": "Before you embark on a journey of revenge, dig two graves.", "personality_id": "confucius", "personality_name": "Confucius", "domain": "philosophical", "source": "Analects"},
    {"quote": "It does not matter how slowly you go as long as you do not stop.", "personality_id": "confucius", "personality_name": "Confucius", "domain": "philosophical", "source": "Analects"},
    {"quote": "The future belongs to those who prepare for it today.", "personality_id": "chanakya", "personality_name": "Chanakya", "domain": "leadership", "source": "Arthashastra"},
    {"quote": "A person should not be too honest. Straight trees are cut first.", "personality_id": "chanakya", "personality_name": "Chanakya", "domain": "leadership", "source": "Chanakya Neeti"},
]


@bp.route(route="wisdom-of-day", methods=["GET", "OPTIONS"])
async def wisdom_of_day(req: func.HttpRequest) -> func.HttpResponse:
    """Get the wisdom of the day — rotating daily quote."""
    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=204, headers=_cors())
    try:
        today = datetime.now(timezone.utc).date()
        day_of_year = today.timetuple().tm_yday
        idx = day_of_year % len(_WISDOM_COLLECTION)
        todays_wisdom = _WISDOM_COLLECTION[idx]

        logger.info(f"📜 Wisdom of the day served: {todays_wisdom['personality_name']}")
        return func.HttpResponse(
            json.dumps({"wisdom": todays_wisdom, "date": today.isoformat(), "day_number": day_of_year, "total_quotes": len(_WISDOM_COLLECTION)}, indent=2),
            status_code=200, headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Error in wisdom-of-day endpoint: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to get wisdom of the day", "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500, headers=_cors(),
        )


# ── Share tracking ───────────────────────────────────────────────────────────

@bp.route(route="share/track", methods=["POST", "OPTIONS"])
async def track_share(req: func.HttpRequest) -> func.HttpResponse:
    """Track share analytics for wisdom content."""
    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=204, headers=_cors())
    try:
        body = req.get_json()
        platform = body.get("platform", "unknown")
        content_type = body.get("content_type", "wisdom")
        personality_id = body.get("personality_id")
        domain = body.get("domain")
        logger.info(f"📤 Share tracked: platform={platform}, type={content_type}, personality={personality_id}, domain={domain}")

        return func.HttpResponse(
            json.dumps({"success": True, "message": "Share tracked successfully", "platform": platform, "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=200, headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Error tracking share: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to track share", "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500, headers=_cors(),
        )


@bp.route(route="share/{shareId}", methods=["GET", "OPTIONS"])
async def get_shared_wisdom(req: func.HttpRequest) -> func.HttpResponse:
    """Retrieve shared wisdom by share ID."""
    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=204, headers=_cors())
    try:
        share_id = req.route_params.get("shareId")
        if not share_id:
            return func.HttpResponse(json.dumps({"error": "Share ID required"}), status_code=400, headers=_cors())

        sample_shares = {
            "demo": {
                "id": "demo",
                "text": "The unexamined life is not worth living. To find yourself, think for yourself.",
                "personality_id": "socrates", "personality_name": "Socrates", "domain": "philosophical",
                "citation": "Apology of Socrates", "shared_at": datetime.now(timezone.utc).isoformat(), "share_count": 42,
            }
        }

        wisdom = sample_shares.get(share_id, {
            "id": share_id,
            "text": "Knowledge speaks, but wisdom listens. In the journey of understanding, patience is your greatest companion.",
            "personality_id": "buddha", "personality_name": "Gautama Buddha", "domain": "spiritual",
            "citation": "Buddhist Teachings", "shared_at": datetime.now(timezone.utc).isoformat(), "share_count": 12,
        })

        logger.info(f"📖 Shared wisdom retrieved: share_id={share_id}")
        return func.HttpResponse(json.dumps(wisdom), status_code=200, headers=_cors())

    except Exception as e:
        logger.error(f"❌ Error retrieving shared wisdom: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to retrieve shared wisdom", "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500, headers=_cors(),
        )


# ── Wisdom history ───────────────────────────────────────────────────────────

_WISDOM_ARCHIVE = [
    {"id": "w1", "date": "2025-01-28", "personality_id": "krishna", "personality_name": "Lord Krishna", "domain": "spiritual", "wisdom_text": "You have the right to work, but never to the fruit of work.", "source_citation": "Bhagavad Gita 2.47", "saved": False},
    {"id": "w2", "date": "2025-01-27", "personality_id": "albert_einstein", "personality_name": "Albert Einstein", "domain": "scientific", "wisdom_text": "Imagination is more important than knowledge. Knowledge is limited. Imagination encircles the world.", "source_citation": "Interview, 1929", "saved": False},
    {"id": "w3", "date": "2025-01-26", "personality_id": "marcus_aurelius", "personality_name": "Marcus Aurelius", "domain": "philosophical", "wisdom_text": "Very little is needed to make a happy life; it is all within yourself, in your way of thinking.", "source_citation": "Meditations", "saved": False},
    {"id": "w4", "date": "2025-01-25", "personality_id": "mahatma_gandhi", "personality_name": "Mahatma Gandhi", "domain": "leadership", "wisdom_text": "Be the change you wish to see in the world.", "source_citation": "Personal Philosophy", "saved": False},
    {"id": "w5", "date": "2025-01-24", "personality_id": "buddha", "personality_name": "Gautama Buddha", "domain": "spiritual", "wisdom_text": "Peace comes from within. Do not seek it without.", "source_citation": "Buddhist Teachings", "saved": False},
    {"id": "w6", "date": "2025-01-23", "personality_id": "socrates", "personality_name": "Socrates", "domain": "philosophical", "wisdom_text": "The unexamined life is not worth living.", "source_citation": "Apology of Socrates", "saved": False},
    {"id": "w7", "date": "2025-01-22", "personality_id": "abraham_lincoln", "personality_name": "Abraham Lincoln", "domain": "leadership", "wisdom_text": "In the end, it's not the years in your life that count. It's the life in your years.", "source_citation": "Attributed", "saved": False},
    {"id": "w8", "date": "2025-01-21", "personality_id": "rumi", "personality_name": "Rumi", "domain": "spiritual", "wisdom_text": "The wound is the place where the Light enters you.", "source_citation": "Masnavi", "saved": False},
    {"id": "w9", "date": "2025-01-20", "personality_id": "nikola_tesla", "personality_name": "Nikola Tesla", "domain": "scientific", "wisdom_text": "The present is theirs; the future, for which I really worked, is mine.", "source_citation": "Interview, 1899", "saved": False},
    {"id": "w10", "date": "2025-01-19", "personality_id": "confucius", "personality_name": "Confucius", "domain": "philosophical", "wisdom_text": "It does not matter how slowly you go as long as you do not stop.", "source_citation": "Analects", "saved": False},
]


@bp.route(route="wisdom/history", methods=["GET", "OPTIONS"])
async def get_wisdom_history(req: func.HttpRequest) -> func.HttpResponse:
    """Get paginated history of daily wisdom entries."""
    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=204, headers=_cors())
    try:
        page = int(req.params.get("page", 1))
        limit = int(req.params.get("limit", 10))
        domain = req.params.get("domain")

        entries = list(_WISDOM_ARCHIVE)
        if domain and domain != "All":
            entries = [e for e in entries if e["domain"] == domain]

        total = len(entries)
        start = (page - 1) * limit
        page_entries = entries[start : start + limit]

        logger.info(f"📚 Wisdom history retrieved: page={page}, count={len(page_entries)}")
        return func.HttpResponse(
            json.dumps({"entries": page_entries, "page": page, "limit": limit, "total": total, "total_pages": (total + limit - 1) // limit}),
            status_code=200, headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Error retrieving wisdom history: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to retrieve wisdom history", "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500, headers=_cors(),
        )


@bp.route(route="wisdom/save", methods=["POST", "OPTIONS"])
async def save_wisdom(req: func.HttpRequest) -> func.HttpResponse:
    """Save a wisdom entry to user's collection."""
    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=204, headers=_cors())
    try:
        body = req.get_json()
        wisdom_id = body.get("wisdom_id")
        if not wisdom_id:
            return func.HttpResponse(json.dumps({"error": "Wisdom ID required"}), status_code=400, headers=_cors())

        logger.info(f"💾 Wisdom saved: id={wisdom_id}")
        return func.HttpResponse(
            json.dumps({"success": True, "message": "Wisdom saved to your collection", "wisdom_id": wisdom_id, "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=200, headers=_cors(),
        )
    except Exception as e:
        logger.error(f"❌ Error saving wisdom: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to save wisdom", "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500, headers=_cors(),
        )


# ── OG image ─────────────────────────────────────────────────────────────────

@bp.route(route="og-image/{share_id}", methods=["GET"])
async def get_og_image(req: func.HttpRequest) -> func.HttpResponse:
    """Generate dynamic OG images for social sharing (SVG)."""
    try:
        share_id = req.route_params.get("share_id", "")
        if not share_id:
            return func.HttpResponse("Share ID required", status_code=400, headers=_cors())

        try:
            from services.og_image_service import og_image_service
        except ImportError as e:
            logger.error(f"❌ OG image service import failed: {e}")
            return func.HttpResponse("OG image service not available", status_code=503, headers=_cors())

        sample_wisdom_data = [
            {"wisdom_text": "You have the right to work, but never to the fruit of work.", "personality": "krishna", "citation": "Bhagavad Gita 2.47"},
            {"wisdom_text": "What you think, you become. What you feel, you attract. What you imagine, you create.", "personality": "buddha", "citation": "Buddhist Wisdom"},
            {"wisdom_text": "The only true wisdom is in knowing you know nothing.", "personality": "socrates", "citation": "Socratic Dialogues"},
            {"wisdom_text": "Imagination is more important than knowledge. Knowledge is limited. Imagination encircles the world.", "personality": "einstein", "citation": "The World As I See It"},
            {"wisdom_text": "Be the change that you wish to see in the world.", "personality": "gandhi", "citation": "Mahatma Gandhi"},
        ]

        import hashlib
        hash_val = int(hashlib.md5(share_id.encode()).hexdigest(), 16)
        wisdom = sample_wisdom_data[hash_val % len(sample_wisdom_data)]

        result = og_image_service.get_image_response(
            wisdom_text=wisdom["wisdom_text"], personality=wisdom["personality"], citation=wisdom.get("citation"),
        )

        if not result.get("success"):
            logger.error(f"❌ OG image generation failed: {result.get('error')}")
            return func.HttpResponse("Failed to generate image", status_code=500, headers=_cors())

        headers = {
            **_cors(),
            "Content-Type": "image/svg+xml; charset=utf-8",
            "Cache-Control": "public, max-age=86400",
        }
        logger.info(f"🖼️ OG image generated for share_id={share_id}")
        return func.HttpResponse(result["content"], status_code=200, headers=headers)

    except Exception as e:
        logger.error(f"❌ OG image endpoint error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to generate OG image", "message": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}),
            status_code=500, headers=_cors(),
        )
