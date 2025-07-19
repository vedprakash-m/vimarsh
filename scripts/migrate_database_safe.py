#!/usr/bin/env python3
"""
Database Migration Script for Vimarsh - PRODUCTION SAFE VERSION
Initializes Cosmos DB with production-aligned structure and default data

Production Setup:
- Database: vimarsh-db
- Containers: spiritual-texts, conversations

This script initializes:
1. Default personality configurations (Krishna, Buddha, etc.) - ONLY IF MISSING
2. Sample spiritual texts with personality associations - ONLY IF MISSING
3. Database structure validation
4. NEVER deletes or modifies existing data
5. Creates backup before any changes
"""

import asyncio
import logging
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

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

class SafeDatabaseMigration:
    """Production-safe database migration for Vimarsh"""
    
    def __init__(self):
        self.db = db_service
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.backup_data = {}
        self.is_production = os.getenv('ENVIRONMENT', 'development') == 'production'
        
    async def run_migration(self):
        """Run complete database migration with safety checks"""
        logger.info("🚀 Starting PRODUCTION-SAFE Vimarsh database migration...")
        
        if self.is_production:
            logger.warning("🔥 PRODUCTION ENVIRONMENT DETECTED!")
            logger.warning("This migration will ONLY ADD new data, NEVER DELETE or MODIFY existing data")
            await self.confirm_production_migration()
        
        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No actual changes will be made")
        
        try:
            # Step 1: Create backup of existing data
            await self.backup_existing_data()
            
            # Step 2: Validate database structure
            await self.validate_database_structure()
            
            # Step 3: Initialize personality configurations (only if missing)
            await self.init_personality_configs()
            
            # Step 4: Initialize enhanced spiritual texts (only if missing)
            await self.init_enhanced_spiritual_texts()
            
            # Step 5: Create sample admin data ONLY in development
            if not self.is_production:
                await self.init_sample_admin_data()
            else:
                logger.info("📊 Skipping sample admin data initialization in production")
            
            # Step 6: Validate database after migration
            await self.validate_database()
            
            if self.dry_run:
                logger.info("🔍 DRY RUN COMPLETED - No actual changes were made")
            else:
                logger.info("✅ Database migration completed successfully!")
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            if not self.dry_run and self.is_production:
                logger.error("🔥 Production migration failed - manual intervention may be required")
            raise
    
    async def confirm_production_migration(self):
        """Confirm production migration with safety warnings"""
        logger.warning("=" * 60)
        logger.warning("PRODUCTION DATABASE MIGRATION SAFETY NOTICE")
        logger.warning("=" * 60)
        logger.warning("This migration will:")
        logger.warning("✅ ADD new personality configurations (if missing)")
        logger.warning("✅ ADD new spiritual texts (if missing)")
        logger.warning("✅ CREATE database structure (if missing)")
        logger.warning("❌ NEVER delete existing data")
        logger.warning("❌ NEVER modify existing data")
        logger.warning("❌ NEVER add sample/test data in production")
        logger.warning("=" * 60)
        
        if not self.dry_run:
            response = input("Type 'CONFIRM' to proceed with production migration: ")
            if response != 'CONFIRM':
                logger.info("Migration cancelled by user")
                sys.exit(0)
    
    async def backup_existing_data(self):
        """Create backup of existing production data"""
        logger.info("💾 Creating backup of existing data...")
        
        try:
            # Backup personalities
            personalities = await self.db.get_all_personalities()
            self.backup_data['personalities'] = [p.__dict__ for p in personalities]
            logger.info(f"✅ Backed up {len(personalities)} personalities")
            
            # Backup spiritual texts (sample)
            texts = await self.db.get_all_texts(limit=10)
            self.backup_data['sample_texts'] = [t.__dict__ for t in texts]
            logger.info(f"✅ Backed up sample of {len(texts)} texts")
            
            # Backup user stats
            # Note: Only backup count, not actual data for privacy
            usage_records = await self.db.get_usage_records(7, 10)  # Last 7 days, 10 records
            self.backup_data['usage_record_count'] = len(usage_records)
            logger.info(f"✅ Backed up metadata for {len(usage_records)} usage records")
            
            # Save backup to file
            backup_file = f"backup_pre_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            if not self.dry_run:
                with open(backup_file, 'w') as f:
                    json.dump(self.backup_data, f, indent=2, default=str)
                logger.info(f"💾 Backup saved to: {backup_file}")
            else:
                logger.info(f"🔍 DRY RUN: Would save backup to: {backup_file}")
                
        except Exception as e:
            logger.warning(f"⚠️ Backup creation failed (continuing): {e}")
    
    async def validate_database_structure(self):
        """Validate database structure before migration"""
        logger.info("🔍 Validating database structure...")
        
        # Test basic database connection
        try:
            await self.db.get_all_personalities()
            logger.info("✅ Database connection successful")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    async def check_data_exists(self, data_type: str, identifier: str) -> bool:
        """Check if specific data already exists"""
        try:
            if data_type == "personality":
                personalities = await self.db.get_all_personalities()
                return any(p.personalityName == identifier for p in personalities)
            elif data_type == "text":
                texts = await self.db.get_all_texts(limit=1000)
                return any(t.id == identifier for t in texts)
            return False
        except Exception as e:
            logger.warning(f"⚠️ Error checking if {data_type} exists: {e}")
            return False
    
    async def init_personality_configs(self):
        """Initialize personality configurations (only if missing)"""
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
            # Check if personality already exists
            if await self.check_data_exists("personality", personality.personalityName):
                logger.info(f"⏭️  Personality already exists: {personality.displayName}")
                continue
                
            if self.dry_run:
                logger.info(f"🔍 DRY RUN: Would create personality: {personality.displayName}")
                continue
                
            success = await self.db.save_personality_config(personality)
            if success:
                logger.info(f"✅ Created personality: {personality.displayName}")
            else:
                logger.warning(f"⚠️ Failed to create personality: {personality.displayName}")
    
    async def init_enhanced_spiritual_texts(self):
        """Initialize enhanced spiritual texts (only if missing)"""
        logger.info("📚 Initializing enhanced spiritual texts...")
        
        enhanced_texts = [
            # Krishna texts
            EnhancedSpiritualText(
                id="bg_2_47",
                title="Right to Action, Not to Fruits",
                content="कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
                source="Bhagavad Gita",
                chapter="2",
                verse="47",
                category="karma",
                personality="krishna",
                vectorNamespace="krishna",
                englishTranslation="You have the right to perform your prescribed duty, but not to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty."
            ),
            EnhancedSpiritualText(
                id="bg_18_66",
                title="Surrender to the Divine",
                content="सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज। अहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
                source="Bhagavad Gita",
                chapter="18",
                verse="66",
                category="surrender",
                personality="krishna",
                vectorNamespace="krishna",
                englishTranslation="Abandon all varieties of religion and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear."
            ),
            
            # Buddha texts
            EnhancedSpiritualText(
                id="dhammapada_1",
                title="The Mind is Everything",
                content="All that we are is the result of what we have thought. The mind is everything. What we think we become.",
                source="Dhammapada",
                chapter="1",
                verse="1",
                category="mindfulness",
                personality="buddha",
                vectorNamespace="buddha"
            ),
            
            # Jesus texts
            EnhancedSpiritualText(
                id="matthew_5_44",
                title="Love Your Enemies",
                content="But I tell you, love your enemies and pray for those who persecute you.",
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
            # Check if text already exists
            if await self.check_data_exists("text", text.id):
                logger.info(f"⏭️  Text already exists: {text.title}")
                continue
                
            if self.dry_run:
                logger.info(f"🔍 DRY RUN: Would create text: {text.title} ({text.personality})")
                continue
                
            success = await self.db.save_enhanced_spiritual_text(text)
            if success:
                logger.info(f"✅ Created text: {text.title} ({text.personality})")
            else:
                logger.warning(f"⚠️ Failed to create text: {text.title}")
    
    async def init_sample_admin_data(self):
        """Initialize sample admin data for testing - DEVELOPMENT ONLY"""
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
        
        if self.dry_run:
            logger.info("🔍 DRY RUN: Would create sample user stats")
        else:
            success = await self.db.save_user_stats(sample_stats)
            if success:
                logger.info("✅ Created sample user stats")
        
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
        
        if self.dry_run:
            logger.info("🔍 DRY RUN: Would create sample usage record")
        else:
            success = await self.db.save_usage_record(sample_usage)
            if success:
                logger.info("✅ Created sample usage record")
        
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
        
        if self.dry_run:
            logger.info("🔍 DRY RUN: Would create sample conversation")
        else:
            success = await self.db.save_conversation(sample_conversation)
            if success:
                logger.info("✅ Created sample conversation")
    
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
    migration = SafeDatabaseMigration()
    await migration.run_migration()

if __name__ == "__main__":
    # Check if we're in the correct environment
    print("🚀 Vimarsh PRODUCTION-SAFE Database Migration")
    print("=" * 60)
    print(f"Environment: {'Production' if db_service.is_cosmos_enabled else 'Development'}")
    print(f"Database: vimarsh-db")
    print(f"Containers: spiritual-texts, conversations")
    print("=" * 60)
    
    # Run migration
    asyncio.run(main())
