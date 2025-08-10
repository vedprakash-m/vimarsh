#!/usr/bin/env python3
"""
Wisdom Journal Service - Production Database Integration
======================================================

Phase 2 feature implementation for tracking user insights, reflections,
and spiritual milestones with full Cosmos DB integration.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import uuid

from models.conversation_models import (
    WisdomJournalEntry, JournalEntryType, 
    create_wisdom_journal_entry
)

logger = logging.getLogger(__name__)

class WisdomJournalService:
    """Service for managing personal wisdom journal with database integration."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Phase 2 database service
        try:
            from services.phase2_database_service import phase2_db_service
            self.database_service = phase2_db_service
            self.logger.info("✅ Using Phase 2 database service for wisdom journal")
        except ImportError:
            self.database_service = None
            self.logger.warning("🔶 Phase 2 database service not available")
        
        # Maintain in-memory cache for performance
        self._journal_cache: Dict[str, List[WisdomJournalEntry]] = {}
    
    async def create_journal_entry(
        self,
        user_id: str,
        content: str,
        entry_type: JournalEntryType,
        title: Optional[str] = None,
        personality_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WisdomJournalEntry:
        """Create a new wisdom journal entry with database storage."""
        
        try:
            # Generate title if not provided
            if not title:
                title = content[:50] + "..." if len(content) > 50 else content
            
            # Create the journal entry
            entry = create_wisdom_journal_entry(
                user_id=user_id,
                entry_type=entry_type,
                title=title,
                content=content,
                personality_id=personality_id,
                source_session_id=conversation_id
            )
            
            # Add tags and metadata if provided
            if tags:
                entry.tags = tags
            if metadata:
                entry.metadata.update(metadata)
            
            # Store in database if available
            database_stored = False
            if self.database_service:
                try:
                    stored = await self.database_service.store_wisdom_journal_entry(entry)
                    if stored:
                        self.logger.info(f"💾 Stored journal entry in database: {entry.id}")
                        database_stored = True
                    else:
                        self.logger.warning(f"⚠️ Failed to store in database, using memory fallback")
                except Exception as e:
                    self.logger.error(f"❌ Database storage failed: {e}")
            
            # Update cache
            if user_id not in self._journal_cache:
                self._journal_cache[user_id] = []
            self._journal_cache[user_id].append(entry)
            
            # Extract insights if this is from a conversation
            if conversation_id:
                await self._extract_conversation_insights(user_id, conversation_id, entry)
            
            self.logger.info(
                f"✅ Created wisdom journal entry for user {user_id}: {entry_type.value} "
                f"(DB: {'✓' if database_stored else '✗'})"
            )
            return entry
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create journal entry: {e}")
            raise
    
    async def get_user_journal_entries(
        self,
        user_id: str,
        entry_type: Optional[JournalEntryType] = None,
        personality_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[WisdomJournalEntry]:
        """Get user's journal entries with optional filtering."""
        
        try:
            # Try database first
            if self.database_service:
                try:
                    entries = await self.database_service.get_user_journal_entries(
                        user_id, entry_type, limit
                    )
                    
                    # Apply additional filters that database doesn't handle
                    filtered_entries = []
                    for entry in entries:
                        if personality_id and entry.personality_id != personality_id:
                            continue
                        if start_date and entry.created_at < start_date:
                            continue
                        if end_date and entry.created_at > end_date:
                            continue
                        filtered_entries.append(entry)
                    
                    self.logger.info(f"📚 Retrieved {len(filtered_entries)} journal entries from database")
                    return filtered_entries
                    
                except Exception as e:
                    self.logger.error(f"❌ Database retrieval failed: {e}")
            
            # Fallback to cache
            user_entries = self._journal_cache.get(user_id, [])
            if not user_entries:
                return []
            
            # Apply filters
            filtered_entries = []
            for entry in user_entries:
                if entry_type and entry.entry_type != entry_type:
                    continue
                if personality_id and entry.personality_id != personality_id:
                    continue
                if start_date and entry.created_at < start_date:
                    continue
                if end_date and entry.created_at > end_date:
                    continue
                filtered_entries.append(entry)
            
            # Sort by creation date (newest first) and limit
            filtered_entries.sort(key=lambda x: x.created_at, reverse=True)
            result = filtered_entries[:limit]
            
            self.logger.info(f"📚 Retrieved {len(result)} journal entries from cache")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to retrieve journal entries: {e}")
            return []
    
    async def search_journal_entries(
        self,
        user_id: str,
        query: str,
        entry_type: Optional[JournalEntryType] = None,
        personality_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
        min_similarity: float = 0.3
    ) -> List[Tuple[WisdomJournalEntry, float]]:
        """Semantic search through user's wisdom journal entries."""
        
        try:
            # Try database search first
            if self.database_service:
                try:
                    search_terms = query.lower().split()
                    results = await self.database_service.search_journal_entries(
                        user_id, search_terms, limit * 2  # Get more for filtering
                    )
                    
                    # Apply additional filters
                    filtered_results = []
                    for entry, score in results:
                        if entry_type and entry.entry_type != entry_type:
                            continue
                        if personality_id and entry.personality_id != personality_id:
                            continue
                        if tags and not any(tag in entry.tags for tag in tags):
                            continue
                        if score >= min_similarity:
                            filtered_results.append((entry, score))
                    
                    # Sort and limit
                    filtered_results.sort(key=lambda x: x[1], reverse=True)
                    result = filtered_results[:limit]
                    
                    self.logger.info(f"🔍 Found {len(result)} journal entries in database search")
                    return result
                    
                except Exception as e:
                    self.logger.error(f"❌ Database search failed: {e}")
            
            # Fallback to cache search
            user_entries = self._journal_cache.get(user_id, [])
            if not user_entries:
                return []
            
            # Filter and score entries
            filtered_entries = []
            for entry in user_entries:
                # Apply filters
                if entry_type and entry.entry_type != entry_type:
                    continue
                if personality_id and entry.personality_id != personality_id:
                    continue
                if tags and not any(tag in entry.tags for tag in tags):
                    continue
                
                # Calculate similarity
                similarity = self._calculate_similarity(query.lower(), entry.content.lower())
                if similarity >= min_similarity:
                    filtered_entries.append((entry, similarity))
            
            # Sort by similarity and limit results
            filtered_entries.sort(key=lambda x: x[1], reverse=True)
            result = filtered_entries[:limit]
            
            self.logger.info(f"🔍 Found {len(result)} journal entries in cache search")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Journal search failed: {e}")
            return []
    
    async def update_journal_entry(
        self,
        user_id: str,
        entry_id: str,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing journal entry."""
        
        try:
            # First, get the entry from database or cache
            entries = await self.get_user_journal_entries(user_id, limit=1000)
            target_entry = None
            
            for entry in entries:
                if entry.id == entry_id:
                    target_entry = entry
                    break
            
            if not target_entry:
                self.logger.warning(f"Entry {entry_id} not found for user {user_id}")
                return False
            
            # Update fields
            if content:
                target_entry.content = content
                target_entry.updated_at = datetime.now()
            
            if tags is not None:
                target_entry.tags = tags
            
            if metadata:
                target_entry.metadata.update(metadata)
            
            # Store updated entry in database
            if self.database_service:
                try:
                    stored = await self.database_service.store_wisdom_journal_entry(target_entry)
                    if stored:
                        self.logger.info(f"💾 Updated journal entry in database: {entry_id}")
                    else:
                        self.logger.warning(f"⚠️ Failed to update in database")
                except Exception as e:
                    self.logger.error(f"❌ Database update failed: {e}")
            
            # Update cache
            user_entries = self._journal_cache.get(user_id, [])
            for i, entry in enumerate(user_entries):
                if entry.id == entry_id:
                    user_entries[i] = target_entry
                    break
            
            self.logger.info(f"✅ Updated journal entry {entry_id} for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update journal entry: {e}")
            return False
    
    async def delete_journal_entry(self, user_id: str, entry_id: str) -> bool:
        """Delete a journal entry."""
        
        try:
            # Note: Database doesn't have delete method yet, so we'll skip database deletion
            # Remove from cache
            user_entries = self._journal_cache.get(user_id, [])
            
            for i, entry in enumerate(user_entries):
                if entry.id == entry_id:
                    user_entries.pop(i)
                    self.logger.info(f"🗑️ Deleted journal entry {entry_id} for user {user_id}")
                    return True
            
            self.logger.warning(f"Entry {entry_id} not found for user {user_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete journal entry: {e}")
            return False
    
    async def get_journal_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics about user's journal activity."""
        
        try:
            user_entries = await self.get_user_journal_entries(user_id, limit=1000)
            
            if not user_entries:
                return {"total_entries": 0}
            
            # Calculate analytics
            total_entries = len(user_entries)
            entries_by_type = {}
            entries_by_personality = {}
            recent_activity = 0
            
            week_ago = datetime.now() - timedelta(days=7)
            
            for entry in user_entries:
                # Count by type
                entry_type = entry.entry_type.value
                entries_by_type[entry_type] = entries_by_type.get(entry_type, 0) + 1
                
                # Count by personality
                if entry.personality_id:
                    entries_by_personality[entry.personality_id] = entries_by_personality.get(entry.personality_id, 0) + 1
                
                # Recent activity
                if entry.created_at >= week_ago:
                    recent_activity += 1
            
            # Find most active personality
            most_active_personality = max(entries_by_personality.items(), key=lambda x: x[1])[0] if entries_by_personality else None
            
            # Growth trend
            month_ago = datetime.now() - timedelta(days=30)
            recent_entries = [e for e in user_entries if e.created_at >= month_ago]
            growth_trend = "increasing" if len(recent_entries) > total_entries * 0.3 else "stable"
            
            # Calculate weeks since first entry
            first_entry_date = min(e.created_at for e in user_entries)
            weeks_active = max(1, (datetime.now() - first_entry_date).days / 7)
            
            analytics = {
                "total_entries": total_entries,
                "entries_by_type": entries_by_type,
                "entries_by_personality": entries_by_personality,
                "recent_activity_week": recent_activity,
                "most_active_personality": most_active_personality,
                "growth_trend": growth_trend,
                "avg_entries_per_week": round(total_entries / weeks_active, 2)
            }
            
            self.logger.info(f"📊 Generated journal analytics for user {user_id}")
            return analytics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate journal analytics: {e}")
            return {"error": str(e)}
    
    async def suggest_related_entries(
        self,
        user_id: str,
        current_entry_id: str,
        limit: int = 5
    ) -> List[Tuple[WisdomJournalEntry, float]]:
        """Suggest journal entries related to the current one."""
        
        try:
            user_entries = await self.get_user_journal_entries(user_id, limit=1000)
            current_entry = None
            
            # Find current entry
            for entry in user_entries:
                if entry.id == current_entry_id:
                    current_entry = entry
                    break
            
            if not current_entry:
                return []
            
            # Find similar entries
            related_entries = []
            for entry in user_entries:
                if entry.id == current_entry_id:
                    continue
                
                similarity = self._calculate_similarity(
                    current_entry.content.lower(),
                    entry.content.lower()
                )
                
                if similarity > 0.4:  # Minimum similarity threshold
                    related_entries.append((entry, similarity))
            
            # Sort by similarity and limit
            related_entries.sort(key=lambda x: x[1], reverse=True)
            result = related_entries[:limit]
            
            self.logger.info(f"🔗 Found {len(result)} related entries for {current_entry_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to find related entries: {e}")
            return []
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple similarity calculation using word overlap."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def _extract_conversation_insights(
        self,
        user_id: str,
        conversation_id: str,
        journal_entry: WisdomJournalEntry
    ) -> None:
        """Extract insights from conversation and potentially create additional entries."""
        
        try:
            # Simple insight extraction based on keywords
            content = journal_entry.content.lower()
            
            # Look for spiritual insights
            spiritual_keywords = {
                "dharma": "understanding of righteous duty",
                "karma": "awareness of action and consequence",
                "meditation": "practice of mindfulness",
                "compassion": "cultivation of loving-kindness",
                "wisdom": "pursuit of deeper understanding"
            }
            
            for keyword, insight_description in spiritual_keywords.items():
                if keyword in content:
                    # Create additional insight entry
                    await self.create_journal_entry(
                        user_id=user_id,
                        content=f"Insight about {keyword}: {insight_description}",
                        entry_type=JournalEntryType.INSIGHT,
                        title=f"Auto-extracted: {keyword.title()}",
                        personality_id=journal_entry.personality_id,
                        conversation_id=conversation_id,
                        tags=["auto-extracted", keyword],
                        metadata={"source_entry_id": journal_entry.id}
                    )
                    break  # Only create one auto-insight per entry
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to extract conversation insights: {e}")


# Global instance
wisdom_journal_service = WisdomJournalService()


# Test function
async def test_wisdom_journal_service():
    """Test the wisdom journal service functionality."""
    print("🧪 Testing Wisdom Journal Service with Database Integration...")
    
    service = wisdom_journal_service
    test_user_id = "test_user_123"
    
    try:
        # Create a test entry
        entry = await service.create_journal_entry(
            user_id=test_user_id,
            content="Today I learned about the importance of detachment in spiritual practice. Like Krishna teaches in the Bhagavad Gita, we must act without attachment to results.",
            entry_type=JournalEntryType.INSIGHT,
            personality_id="krishna",
            tags=["detachment", "bhagavad-gita", "spiritual-practice"]
        )
        print(f"✅ Created journal entry: {entry.id}")
        
        # Search for entries
        search_results = await service.search_journal_entries(
            user_id=test_user_id,
            query="spiritual practice detachment",
            limit=5
        )
        print(f"✅ Found {len(search_results)} entries in search")
        
        # Get all entries
        all_entries = await service.get_user_journal_entries(test_user_id)
        print(f"✅ Retrieved {len(all_entries)} total entries")
        
        # Get analytics
        analytics = await service.get_journal_analytics(test_user_id)
        print(f"✅ Generated analytics: {analytics.get('total_entries', 0)} total entries")
        
        print("🎉 Wisdom Journal Service test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_wisdom_journal_service())
