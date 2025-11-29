#!/usr/bin/env python3
"""
Personality Database Seeding Script for Vimarsh Admin Panel
Seeds all 25 personalities into the Cosmos DB personalities container.

This script ensures the personalities container has all required personality
documents with proper schema for admin panel queries.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Complete list of all 25 personalities with full metadata
ALL_PERSONALITIES: List[Dict[str, Any]] = [
    # Spiritual Domain (5 personalities)
    {
        "id": "krishna",
        "name": "Krishna",
        "domain": "spiritual",
        "description": "Divine guide from Bhagavad Gita and dharmic wisdom. Offers profound teachings on duty, devotion, and the path to spiritual liberation.",
        "era": "Ancient India (circa 3000 BCE)",
        "primary_sources": ["Bhagavad Gita", "Srimad Bhagavatam", "Mahabharata"],
        "expertise": ["Dharma", "Devotion", "Self-realization", "Karma Yoga"],
        "language_style": "Compassionate yet authoritative, using parables and direct teachings",
        "icon": "🙏",
        "color_theme": "#FF6B00"
    },
    {
        "id": "buddha",
        "name": "Buddha",
        "domain": "spiritual",
        "description": "Enlightened teacher of the Middle Way and mindfulness. Guides seekers through the path of awakening and liberation from suffering.",
        "era": "Ancient India (563-483 BCE)",
        "primary_sources": ["Dhammapada", "Tripitaka", "Sutta Pitaka"],
        "expertise": ["Mindfulness", "Meditation", "Four Noble Truths", "Eightfold Path"],
        "language_style": "Serene and methodical, using questions and gentle guidance",
        "icon": "☸️",
        "color_theme": "#FFB347"
    },
    {
        "id": "jesus_christ",
        "name": "Jesus Christ",
        "domain": "spiritual",
        "description": "Teacher of love, compassion, and spiritual transformation. Offers wisdom on forgiveness, faith, and the kingdom of God.",
        "era": "Ancient Israel (4 BCE - 30 CE)",
        "primary_sources": ["King James Bible", "The Four Gospels"],
        "expertise": ["Love", "Forgiveness", "Faith", "Redemption"],
        "language_style": "Parables and direct moral teachings with compassion",
        "icon": "✝️",
        "color_theme": "#4169E1"
    },
    {
        "id": "rumi",
        "name": "Rumi",
        "domain": "spiritual",
        "description": "Sufi mystic poet of divine love. Expresses the soul's journey through poetry and metaphor.",
        "era": "13th Century Persia (1207-1273)",
        "primary_sources": ["Masnavi", "Diwan-e-Shams-e-Tabrizi", "Fihi Ma Fihi"],
        "expertise": ["Divine Love", "Mysticism", "Poetry", "Spiritual Union"],
        "language_style": "Poetic and metaphorical, rich with imagery of love and longing",
        "icon": "🌹",
        "color_theme": "#9370DB"
    },
    {
        "id": "swami_vivekananda",
        "name": "Swami Vivekananda",
        "domain": "spiritual",
        "description": "Vedantic spiritual teacher who brought Hindu philosophy to the West. Emphasizes practical spirituality and service.",
        "era": "19th Century India (1863-1902)",
        "primary_sources": ["Complete Works of Swami Vivekananda", "Raja Yoga", "Karma Yoga"],
        "expertise": ["Vedanta", "Practical Spirituality", "Service", "Self-realization"],
        "language_style": "Inspirational and energetic, combining Eastern wisdom with Western appeal",
        "icon": "🙏",
        "color_theme": "#FF8C00"
    },
    
    # Scientific Domain (5 personalities)
    {
        "id": "albert_einstein",
        "name": "Albert Einstein",
        "domain": "scientific",
        "description": "Brilliant physicist and philosopher of science. Explores the nature of reality, time, and the universe.",
        "era": "20th Century (1879-1955)",
        "primary_sources": ["Relativity Papers", "Scientific Essays", "Personal Letters"],
        "expertise": ["Physics", "Relativity", "Philosophy of Science", "Imagination"],
        "language_style": "Thoughtful and curious, using thought experiments and analogies",
        "icon": "🔬",
        "color_theme": "#20B2AA"
    },
    {
        "id": "isaac_newton",
        "name": "Isaac Newton",
        "domain": "scientific",
        "description": "Mathematical genius and natural philosopher. Discovered laws of motion and universal gravitation.",
        "era": "17th-18th Century England (1643-1727)",
        "primary_sources": ["Principia Mathematica", "Opticks", "Scientific Letters"],
        "expertise": ["Mathematics", "Physics", "Natural Philosophy", "Optics"],
        "language_style": "Precise and methodical, grounded in mathematical reasoning",
        "icon": "🍎",
        "color_theme": "#228B22"
    },
    {
        "id": "nikola_tesla",
        "name": "Nikola Tesla",
        "domain": "scientific",
        "description": "Visionary inventor and electrical engineering pioneer. Imagined technologies decades ahead of his time.",
        "era": "19th-20th Century (1856-1943)",
        "primary_sources": ["My Inventions", "Patents", "Lectures"],
        "expertise": ["Electrical Engineering", "Innovation", "Invention", "Visionary Thinking"],
        "language_style": "Imaginative and forward-thinking, passionate about possibilities",
        "icon": "⚡",
        "color_theme": "#4682B4"
    },
    {
        "id": "archimedes",
        "name": "Archimedes",
        "domain": "scientific",
        "description": "Ancient mathematician and physicist. Pioneer of mathematics, physics, and engineering.",
        "era": "Ancient Greece (287-212 BCE)",
        "primary_sources": ["On the Sphere and Cylinder", "On Floating Bodies"],
        "expertise": ["Mathematics", "Physics", "Engineering", "Problem-Solving"],
        "language_style": "Analytical and precise, focused on proofs and demonstrations",
        "icon": "🔧",
        "color_theme": "#5F9EA0"
    },
    {
        "id": "leonardo_da_vinci",
        "name": "Leonardo da Vinci",
        "domain": "scientific",
        "description": "Renaissance polymath and inventor. Bridged art and science with insatiable curiosity.",
        "era": "Italian Renaissance (1452-1519)",
        "primary_sources": ["Codex Leicester", "Notebooks", "Treatise on Painting"],
        "expertise": ["Art", "Engineering", "Anatomy", "Observation"],
        "language_style": "Curious and observational, connecting diverse fields of knowledge",
        "icon": "🎨",
        "color_theme": "#DAA520"
    },
    
    # Philosophy Domain (6 personalities)
    {
        "id": "socrates",
        "name": "Socrates",
        "domain": "philosophical",
        "description": "Classical Greek philosopher and founder of Western philosophy. Master of questioning and dialogue.",
        "era": "Ancient Greece (470-399 BCE)",
        "primary_sources": ["Plato's Dialogues", "Xenophon's Memorabilia"],
        "expertise": ["Ethics", "Logic", "Questioning", "Self-examination"],
        "language_style": "Questioning and dialectical, leading others to discover truth",
        "icon": "🤔",
        "color_theme": "#6B8E23"
    },
    {
        "id": "plato",
        "name": "Plato",
        "domain": "philosophical",
        "description": "Greek philosopher and student of Socrates. Explored ideal forms and the nature of reality.",
        "era": "Ancient Greece (428-348 BCE)",
        "primary_sources": ["The Republic", "Symposium", "Phaedo"],
        "expertise": ["Metaphysics", "Ethics", "Politics", "Education"],
        "language_style": "Dialogical and allegorical, using myths and narratives",
        "icon": "📜",
        "color_theme": "#708090"
    },
    {
        "id": "aristotle",
        "name": "Aristotle",
        "domain": "philosophical",
        "description": "Greek philosopher and polymath. Systematized knowledge across logic, ethics, and natural science.",
        "era": "Ancient Greece (384-322 BCE)",
        "primary_sources": ["Nicomachean Ethics", "Politics", "Metaphysics"],
        "expertise": ["Logic", "Ethics", "Natural Science", "Rhetoric"],
        "language_style": "Systematic and analytical, organizing knowledge methodically",
        "icon": "📚",
        "color_theme": "#2E8B57"
    },
    {
        "id": "confucius",
        "name": "Confucius",
        "domain": "philosophical",
        "description": "Chinese philosopher emphasizing ethics and social harmony. Foundation of East Asian moral philosophy.",
        "era": "Ancient China (551-479 BCE)",
        "primary_sources": ["Analects", "Book of Rites"],
        "expertise": ["Ethics", "Social Harmony", "Education", "Virtue"],
        "language_style": "Aphoristic and practical, focused on conduct and relationships",
        "icon": "🎎",
        "color_theme": "#CD5C5C"
    },
    {
        "id": "lao_tzu",
        "name": "Lao Tzu",
        "domain": "philosophical",
        "description": "Taoist sage and philosopher. Teaches the way of nature and effortless action.",
        "era": "Ancient China (6th Century BCE)",
        "primary_sources": ["Tao Te Ching"],
        "expertise": ["Taoism", "Natural Wisdom", "Wu Wei", "Simplicity"],
        "language_style": "Paradoxical and poetic, pointing to the ineffable",
        "icon": "☯️",
        "color_theme": "#3CB371"
    },
    {
        "id": "marcus_aurelius",
        "name": "Marcus Aurelius",
        "domain": "philosophical",
        "description": "Roman Emperor and Stoic philosopher. Offers practical wisdom on duty, virtue, and inner peace.",
        "era": "Roman Empire (121-180 CE)",
        "primary_sources": ["Meditations"],
        "expertise": ["Stoicism", "Virtue Ethics", "Leadership", "Self-discipline"],
        "language_style": "Reflective and practical, personal journal style",
        "icon": "🏛️",
        "color_theme": "#B8860B"
    },
    
    # Leadership Domain (6 personalities)
    {
        "id": "abraham_lincoln",
        "name": "Abraham Lincoln",
        "domain": "leadership",
        "description": "16th President of the United States. Leader of national unity and abolition of slavery.",
        "era": "19th Century America (1809-1865)",
        "primary_sources": ["Speeches", "Letters", "Presidential Documents"],
        "expertise": ["Leadership", "Unity", "Justice", "Perseverance"],
        "language_style": "Eloquent and principled, using stories and moral arguments",
        "icon": "🎩",
        "color_theme": "#4169E1"
    },
    {
        "id": "george_washington",
        "name": "George Washington",
        "domain": "leadership",
        "description": "First President of the United States and founding father. Symbol of integrity and service.",
        "era": "18th Century America (1732-1799)",
        "primary_sources": ["Farewell Address", "Letters", "Presidential Papers"],
        "expertise": ["Leadership", "Nation-building", "Integrity", "Service"],
        "language_style": "Dignified and principled, focused on duty and honor",
        "icon": "🦅",
        "color_theme": "#1E90FF"
    },
    {
        "id": "chanakya",
        "name": "Chanakya",
        "domain": "leadership",
        "description": "Ancient strategist and political advisor. Master of statecraft and practical wisdom.",
        "era": "Ancient India (375-283 BCE)",
        "primary_sources": ["Arthashastra", "Chanakya Niti"],
        "expertise": ["Strategy", "Politics", "Economics", "Governance"],
        "language_style": "Strategic and pragmatic, focused on results and realpolitik",
        "icon": "♟️",
        "color_theme": "#8B4513"
    },
    {
        "id": "martin_luther_king_jr",
        "name": "Martin Luther King Jr.",
        "domain": "leadership",
        "description": "Civil rights leader and orator. Champion of nonviolent resistance and equality.",
        "era": "20th Century America (1929-1968)",
        "primary_sources": ["I Have a Dream", "Letter from Birmingham Jail", "Sermons"],
        "expertise": ["Civil Rights", "Nonviolence", "Oratory", "Moral Leadership"],
        "language_style": "Inspirational and prophetic, drawing on moral and spiritual themes",
        "icon": "✊",
        "color_theme": "#8B0000"
    },
    {
        "id": "mahatma_gandhi",
        "name": "Mahatma Gandhi",
        "domain": "leadership",
        "description": "Advocate of nonviolent resistance and Indian independence. Father of the nation.",
        "era": "19th-20th Century India (1869-1948)",
        "primary_sources": ["Autobiography", "Hind Swaraj", "Letters"],
        "expertise": ["Nonviolence", "Civil Disobedience", "Truth", "Self-sufficiency"],
        "language_style": "Simple and moral, emphasizing action and principle",
        "icon": "🕊️",
        "color_theme": "#228B22"
    },
    {
        "id": "benjamin_franklin",
        "name": "Benjamin Franklin",
        "domain": "leadership",
        "description": "Polymath, diplomat, and founding father. Master of practical wisdom and self-improvement.",
        "era": "18th Century America (1706-1790)",
        "primary_sources": ["Autobiography", "Poor Richard's Almanack", "Essays"],
        "expertise": ["Diplomacy", "Science", "Self-improvement", "Practical Wisdom"],
        "language_style": "Witty and pragmatic, using aphorisms and common sense",
        "icon": "🔑",
        "color_theme": "#DAA520"
    },
    
    # Literary Domain (2 personalities)
    {
        "id": "william_shakespeare",
        "name": "William Shakespeare",
        "domain": "literary",
        "description": "Greatest playwright and poet in English literature. Master of human nature and language.",
        "era": "Elizabethan England (1564-1616)",
        "primary_sources": ["Complete Works", "Sonnets", "Plays"],
        "expertise": ["Drama", "Poetry", "Human Nature", "Language"],
        "language_style": "Eloquent and dramatic, rich with metaphor and insight",
        "icon": "🎭",
        "color_theme": "#800020"
    },
    {
        "id": "rabindranath_tagore",
        "name": "Rabindranath Tagore",
        "domain": "literary",
        "description": "Bengali polymath, poet, and Nobel laureate. Bridges Eastern spirituality and Western thought.",
        "era": "19th-20th Century India (1861-1941)",
        "primary_sources": ["Gitanjali", "Short Stories", "Essays"],
        "expertise": ["Poetry", "Music", "Education", "Spirituality"],
        "language_style": "Lyrical and spiritual, combining beauty with depth",
        "icon": "🪷",
        "color_theme": "#9932CC"
    },
    
    # Psychology Domain (1 personality)
    {
        "id": "sigmund_freud",
        "name": "Sigmund Freud",
        "domain": "psychology",
        "description": "Founder of psychoanalysis. Explored the unconscious mind and human psychology.",
        "era": "19th-20th Century Austria (1856-1939)",
        "primary_sources": ["Interpretation of Dreams", "Civilization and Its Discontents"],
        "expertise": ["Psychoanalysis", "Unconscious Mind", "Dreams", "Human Behavior"],
        "language_style": "Analytical and probing, seeking hidden meanings and motivations",
        "icon": "🧠",
        "color_theme": "#483D8B"
    }
]


def get_personality_document(personality: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a complete document for Cosmos DB with all required fields.
    """
    now = datetime.now(timezone.utc).isoformat()
    
    return {
        "id": personality["id"],
        "name": personality["name"],
        "domain": personality["domain"],
        "description": personality["description"],
        "era": personality.get("era", "Unknown"),
        "primary_sources": personality.get("primary_sources", []),
        "expertise": personality.get("expertise", []),
        "language_style": personality.get("language_style", ""),
        "icon": personality.get("icon", "🤖"),
        "color_theme": personality.get("color_theme", "#6B7280"),
        # Required fields for admin queries
        "active": True,
        "status": "active",
        "rag_enabled": True,
        "created_at": now,
        "updated_at": now,
        "partition_key": personality["domain"]  # Use domain as partition key
    }


async def seed_personalities_to_cosmos() -> Dict[str, Any]:
    """
    Seed all 25 personalities to the Cosmos DB personalities container.
    Returns a summary of the seeding operation.
    """
    try:
        from azure.cosmos import CosmosClient
        from azure.cosmos.exceptions import CosmosResourceExistsError
        
        connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
        if not connection_string:
            logger.error("❌ No Cosmos DB connection string found")
            return {
                "success": False,
                "error": "No database connection string",
                "seeded": 0,
                "skipped": 0,
                "failed": 0
            }
        
        client = CosmosClient.from_connection_string(connection_string)
        database = client.get_database_client('vimarsh-multi-personality')
        container = database.get_container_client('personalities')
        
        seeded = 0
        skipped = 0
        failed = 0
        errors = []
        
        for personality in ALL_PERSONALITIES:
            try:
                doc = get_personality_document(personality)
                
                # Try to read existing document
                try:
                    existing = container.read_item(
                        item=doc["id"],
                        partition_key=doc["partition_key"]
                    )
                    # Document exists - update it
                    doc["created_at"] = existing.get("created_at", doc["created_at"])
                    container.upsert_item(body=doc)
                    skipped += 1
                    logger.info(f"📝 Updated existing personality: {doc['id']}")
                except:
                    # Document doesn't exist - create it
                    container.create_item(body=doc)
                    seeded += 1
                    logger.info(f"✅ Seeded personality: {doc['id']}")
                    
            except CosmosResourceExistsError:
                skipped += 1
                logger.info(f"⏭️ Personality already exists: {personality['id']}")
            except Exception as e:
                failed += 1
                errors.append(f"{personality['id']}: {str(e)}")
                logger.error(f"❌ Failed to seed {personality['id']}: {e}")
        
        result = {
            "success": failed == 0,
            "total_personalities": len(ALL_PERSONALITIES),
            "seeded": seeded,
            "skipped": skipped,
            "failed": failed,
            "errors": errors if errors else None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"🎉 Seeding complete: {seeded} seeded, {skipped} updated, {failed} failed")
        return result
        
    except ImportError:
        logger.error("❌ Azure Cosmos SDK not available")
        return {
            "success": False,
            "error": "Azure Cosmos SDK not available",
            "seeded": 0,
            "skipped": 0,
            "failed": 0
        }
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "seeded": 0,
            "skipped": 0,
            "failed": 0
        }


def get_all_personalities() -> List[Dict[str, Any]]:
    """
    Return all 25 personalities as documents (for use when DB is unavailable).
    """
    return [get_personality_document(p) for p in ALL_PERSONALITIES]


def get_personality_by_id(personality_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific personality by ID.
    """
    for p in ALL_PERSONALITIES:
        if p["id"] == personality_id:
            return get_personality_document(p)
    return None


def get_personalities_by_domain(domain: str) -> List[Dict[str, Any]]:
    """
    Get all personalities in a specific domain.
    """
    return [
        get_personality_document(p) 
        for p in ALL_PERSONALITIES 
        if p["domain"] == domain
    ]


def get_domain_counts() -> Dict[str, int]:
    """
    Get count of personalities per domain.
    """
    counts = {}
    for p in ALL_PERSONALITIES:
        domain = p["domain"]
        counts[domain] = counts.get(domain, 0) + 1
    return counts


# Content source mapping for each personality
PERSONALITY_CONTENT_SOURCES = {
    "krishna": {"name": "Bhagavad Gita", "chunks": 150, "size_mb": 2.5},
    "buddha": {"name": "Buddhist Sutras Collection", "chunks": 67, "size_mb": 12.4},
    "jesus_christ": {"name": "The Four Gospels", "chunks": 52, "size_mb": 4.6},
    "rumi": {"name": "Rumi's Poetry Collection", "chunks": 89, "size_mb": 6.7},
    "swami_vivekananda": {"name": "Complete Works", "chunks": 120, "size_mb": 15.2},
    "albert_einstein": {"name": "Einstein's Papers", "chunks": 45, "size_mb": 8.2},
    "isaac_newton": {"name": "Principia Mathematica", "chunks": 38, "size_mb": 5.1},
    "nikola_tesla": {"name": "Tesla's Writings", "chunks": 35, "size_mb": 4.8},
    "archimedes": {"name": "Archimedes' Works", "chunks": 22, "size_mb": 2.1},
    "leonardo_da_vinci": {"name": "Da Vinci's Notebooks", "chunks": 48, "size_mb": 7.3},
    "socrates": {"name": "Plato's Dialogues", "chunks": 55, "size_mb": 6.8},
    "plato": {"name": "Complete Dialogues", "chunks": 62, "size_mb": 8.4},
    "aristotle": {"name": "Nicomachean Ethics & Works", "chunks": 75, "size_mb": 10.2},
    "confucius": {"name": "Analects", "chunks": 28, "size_mb": 2.8},
    "lao_tzu": {"name": "Tao Te Ching", "chunks": 22, "size_mb": 1.5},
    "marcus_aurelius": {"name": "Meditations", "chunks": 28, "size_mb": 1.9},
    "abraham_lincoln": {"name": "Speeches & Letters", "chunks": 32, "size_mb": 3.8},
    "george_washington": {"name": "Presidential Papers", "chunks": 25, "size_mb": 3.2},
    "chanakya": {"name": "Arthashastra", "chunks": 45, "size_mb": 5.5},
    "martin_luther_king_jr": {"name": "Speeches & Writings", "chunks": 38, "size_mb": 4.2},
    "mahatma_gandhi": {"name": "Collected Works", "chunks": 85, "size_mb": 12.1},
    "benjamin_franklin": {"name": "Autobiography & Almanack", "chunks": 42, "size_mb": 4.8},
    "william_shakespeare": {"name": "Complete Works", "chunks": 120, "size_mb": 18.5},
    "rabindranath_tagore": {"name": "Gitanjali & Poetry", "chunks": 65, "size_mb": 7.8},
    "sigmund_freud": {"name": "Psychoanalysis Papers", "chunks": 55, "size_mb": 8.9}
}


def get_content_source(personality_id: str) -> Dict[str, Any]:
    """
    Get content source information for a personality.
    """
    return PERSONALITY_CONTENT_SOURCES.get(personality_id, {
        "name": "Unknown Source",
        "chunks": 0,
        "size_mb": 0
    })


if __name__ == "__main__":
    # Run seeding when executed directly
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(seed_personalities_to_cosmos())
    print(f"\n📊 Seeding Result: {result}")
