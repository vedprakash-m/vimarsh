#!/usr/bin/env python3
"""
Database Migration Script for Vimarsh
Initializes Cosmos DB with production-aligned structure and default data

Production Setup:
- Database: vimarsh-db
- Containers: spiritual-texts, conversations

This script initializes:
1. Default personality configurations (Krishna, Buddha, etc.)
2. Sample spiritual texts with personality associations
3. Database structure validation
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add backend directory to path to import services
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from services.database_service import (
    db_service, 
    PersonalityConfig, 
    EnhancedSpiritualText,
    UserStats,
    Conversation,
    UsageRecord
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Database migration for comprehensive Vimarsh setup"""
    
    def __init__(self):
        self.db = db_service
        
    async def run_migration(self):
        """Run complete database migration"""
        logger.info("🚀 Starting Vimarsh database migration...")
        
        try:
            # Step 1: Initialize personality configurations
            await self.init_personality_configs()
            
            # Step 2: Initialize enhanced spiritual texts
            await self.init_enhanced_spiritual_texts()
            
            # Step 3: Create sample admin data (for testing)
            await self.init_sample_admin_data()
            
            # Step 4: Validate database structure
            await self.validate_database()
            
            logger.info("✅ Database migration completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise
    
    async def init_personality_configs(self):
        """Initialize personality configurations"""
        logger.info("📝 Initializing personality configurations...")
        
        personalities = [
            PersonalityConfig(
                id="krishna_config",
                personalityName="krishna",
                displayName="Lord Krishna",
                description="Divine teacher from Bhagavad Gita, embodying wisdom, compassion, and spiritual guidance",
                systemPrompt="""You are Lord Krishna, the divine teacher and guide from the Bhagavad Gita. 
                You embody infinite compassion, wisdom, and love. Provide spiritual guidance with Sanskrit citations.""",
                associatedBooks=["Bhagavad Gita", "Srimad Bhagavatam", "Mahabharata"],
                vectorNamespace="krishna",
                isActive=True
            ),
            PersonalityConfig(
                id="buddha_config",
                personalityName="buddha",
                displayName="Buddha",
                description="Enlightened teacher of Buddhism, sharing wisdom on suffering, mindfulness, and liberation",
                systemPrompt="""You are Buddha, the enlightened teacher. Share wisdom on the Four Noble Truths, 
                mindfulness, and the path to liberation from suffering.""",
                associatedBooks=["Dhammapada", "Lotus Sutra", "Tripitaka"],
                vectorNamespace="buddha",
                isActive=True
            ),
            PersonalityConfig(
                id="jesus_config",
                personalityName="jesus",
                displayName="Jesus Christ",
                description="Teacher of love, compassion, and divine grace from Christian tradition",
                systemPrompt="""You are Jesus Christ, teacher of love and compassion. 
                Share wisdom on love, forgiveness, and spiritual transformation.""",
                associatedBooks=["New Testament", "Gospel of Matthew", "Gospel of John"],
                vectorNamespace="jesus",
                isActive=True
            ),
            PersonalityConfig(
                id="lao_tzu_config",
                personalityName="lao_tzu",
                displayName="Lao Tzu",
                description="Ancient Chinese philosopher and founder of Taoism, teaching about the Way",
                systemPrompt="""You are Lao Tzu, sage of the Tao. Share wisdom about wu wei, 
                natural harmony, and the Way that cannot be named.""",
                associatedBooks=["Tao Te Ching", "Zhuangzi"],
                vectorNamespace="lao_tzu",
                isActive=True
            ),
            PersonalityConfig(
                id="rumi_config",
                personalityName="rumi",
                displayName="Rumi",
                description="Sufi mystic poet, teaching about divine love and spiritual union",
                systemPrompt="""You are Rumi, the Sufi mystic poet. Share wisdom about divine love, 
                spiritual union, and the journey of the soul to the Beloved.""",
                associatedBooks=["Masnavi", "Divan-e Shams-e Tabrizi"],
                vectorNamespace="rumi",
                isActive=True
            )
        ]
        
        for personality in personalities:
            success = await self.db.save_personality_config(personality)
            if success:
                logger.info(f"✅ Saved personality: {personality.displayName}")
            else:
                logger.warning(f"⚠️ Failed to save personality: {personality.displayName}")
    
    async def init_enhanced_spiritual_texts(self):
        """Initialize enhanced spiritual texts with personality associations"""
        logger.info("📚 Initializing enhanced spiritual texts...")
        
        enhanced_texts = [
            # Krishna texts
            EnhancedSpiritualText(
                id="krishna_bg_2_47",
                title="On Duty Without Attachment",
                content="You have a right to perform your prescribed duty, but not to the fruits of action. Never consider yourself to be the cause of the results of your activities, and never be attached to not doing your duty.",
                source="Bhagavad Gita",
                chapter="2",
                verse="47",
                category="dharma",
                personality="krishna",
                vectorNamespace="krishna"
            ),
            EnhancedSpiritualText(
                id="krishna_bg_6_19",
                title="Steady Mind in Meditation", 
                content="As a lamp in a windless place does not waver, so the transcendentalist, whose mind is controlled, remains always steady in his meditation on the transcendent Self.",
                source="Bhagavad Gita",
                chapter="6",
                verse="19",
                category="meditation",
                personality="krishna",
                vectorNamespace="krishna"
            ),
            
            # Buddha texts
            EnhancedSpiritualText(
                id="buddha_dhp_1",
                title="Mind is Everything",
                content="All that we are is the result of what we have thought. The mind is everything. What we think we become.",
                source="Dhammapada",
                chapter="1",
                verse="1",
                category="mindfulness",
                personality="buddha",
                vectorNamespace="buddha"
            ),
            EnhancedSpiritualText(
                id="buddha_dhp_183",
                title="The Teaching of All Buddhas",
                content="Avoid all evil, cultivate good, purify your mind - this is the teaching of all the Buddhas.",
                source="Dhammapada",
                chapter="14",
                verse="183",
                category="ethics",
                personality="buddha",
                vectorNamespace="buddha"
            ),
            
            # Jesus texts
            EnhancedSpiritualText(
                id="jesus_mt_5_44",
                title="Love Your Enemies",
                content="But I tell you, love your enemies and pray for those who persecute you, that you may be children of your Father in heaven.",
                source="Gospel of Matthew",
                chapter="5",
                verse="44",
                category="love",
                personality="jesus",
                vectorNamespace="jesus"
            ),
            
            # Lao Tzu texts
            EnhancedSpiritualText(
                id="lao_tzu_ttc_1",
                title="The Tao That Can Be Spoken",
                content="The Tao that can be spoken is not the eternal Tao. The name that can be named is not the eternal name.",
                source="Tao Te Ching",
                chapter="1",
                verse="1",
                category="mystery",
                personality="lao_tzu",
                vectorNamespace="lao_tzu"
            ),
            
            # Rumi texts
            EnhancedSpiritualText(
                id="rumi_masnavi_1",
                title="The Reed's Lament",
                content="Listen to the reed, how it tells a tale, complaining of separations, saying: Since I was parted from the reedbed, my lament has caused man and woman to moan.",
                source="Masnavi",
                chapter="1",
                verse="1",
                category="divine_love",
                personality="rumi",
                vectorNamespace="rumi"
            )
        ]
        
        for text in enhanced_texts:
            success = await self.db.save_enhanced_spiritual_text(text)
            if success:
                logger.info(f"✅ Saved enhanced text: {text.title} ({text.personality})")
            else:
                logger.warning(f"⚠️ Failed to save text: {text.title}")
    
    async def init_sample_admin_data(self):
        """Initialize sample admin data for testing"""
        logger.info("📊 Initializing sample admin data...")
        
        # Sample user stats
        sample_stats = UserStats(
            id="stats_admin_user",
            userId="admin_user_123",
            userEmail="vedprakash.m@outlook.com",
            totalRequests=50,
            totalTokens=7500,
            totalCostUsd=2.50,
            currentMonthTokens=3000,
            currentMonthCostUsd=1.25,
            lastRequest=datetime.now().isoformat(),
            avgTokensPerRequest=150.0,
            favoriteModel="gemini-2.5-flash",
            personalityUsage={"krishna": 40, "buddha": 8, "jesus": 2},
            qualityBreakdown={"high": 45, "medium": 4, "low": 1},
            riskScore=0.1,
            isBlocked=False
        )
        
        success = await self.db.save_user_stats(sample_stats)
        if success:
            logger.info("✅ Saved sample user stats")
        
        # Sample usage record
        sample_usage = UsageRecord(
            id="usage_admin_001",
            userId="admin_user_123", 
            userEmail="vedprakash.m@outlook.com",
            sessionId="session_123",
            timestamp=datetime.now().isoformat(),
            model="gemini-2.5-flash",
            inputTokens=100,
            outputTokens=150,
            totalTokens=250,
            costUsd=0.05,
            requestType="spiritual_guidance",
            responseQuality="high",
            personality="krishna"
        )
        
        success = await self.db.save_usage_record(sample_usage)
        if success:
            logger.info("✅ Saved sample usage record")
        
        # Sample conversation
        sample_conversation = Conversation(
            id="conv_admin_001",
            userId="admin_user_123",
            userEmail="vedprakash.m@outlook.com",
            sessionId="session_123",
            timestamp=datetime.now().isoformat(),
            question="How can I find my dharma?",
            response="Dear soul, your dharma is discovered through self-reflection and service to others...",
            citations=["Bhagavad Gita 2.47"],
            personality="krishna",
            metadata={
                "model": "gemini-2.5-flash",
                "tokens": 250,
                "cost": 0.05,
                "language": "English"
            }
        )
        
        success = await self.db.save_conversation(sample_conversation)
        if success:
            logger.info("✅ Saved sample conversation")
    
    async def validate_database(self):
        """Validate database structure and data"""
        logger.info("🔍 Validating database structure...")
        
        # Test personality retrieval
        personalities = await self.db.get_all_personalities()
        logger.info(f"✅ Found {len(personalities)} active personalities")
        
        # Test Krishna-specific texts
        krishna_texts = await self.db.get_texts_by_personality("krishna", 10)
        logger.info(f"✅ Found {len(krishna_texts)} Krishna texts")
        
        # Test vector namespace
        krishna_namespace_texts = await self.db.get_texts_by_vector_namespace("krishna", 10)
        logger.info(f"✅ Found {len(krishna_namespace_texts)} texts in Krishna namespace")
        
        # Test admin data
        usage_records = await self.db.get_usage_records(30, 100)
        logger.info(f"✅ Found {len(usage_records)} usage records")
        
        top_users = await self.db.get_top_users(10)
        logger.info(f"✅ Found {len(top_users)} user stats")

async def main():
    """Run the database migration"""
    migration = DatabaseMigration()
    await migration.run_migration()

if __name__ == "__main__":
    # Check if we're in the correct environment
    print("🚀 Vimarsh Database Migration")
    print("=" * 50)
    print(f"Environment: {'Production' if db_service.is_cosmos_enabled else 'Development'}")
    print(f"Database: vimarsh-db")
    print(f"Containers: spiritual-texts, conversations")
    print("=" * 50)
    
    # Run migration
    asyncio.run(main())
