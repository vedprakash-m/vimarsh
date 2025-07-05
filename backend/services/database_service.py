"""
Simple database service for spiritual texts storage and retrieval.
Implements local JSON storage for development and Cosmos DB for production.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class SpiritualText:
    """Represents a spiritual text document"""
    id: str
    title: str
    content: str
    source: str  # e.g., "Bhagavad Gita", "Mahabharata", "Srimad Bhagavatam"
    chapter: Optional[str] = None
    verse: Optional[str] = None
    category: str = "general"  # e.g., "dharma", "karma", "devotion"
    language: str = "English"
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class DatabaseService:
    """Simple database service with local JSON storage for development"""
    
    def __init__(self):
        self.storage_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'spiritual_texts.json')
        self.is_cosmos_enabled = self._check_cosmos_config()
        
        if not self.is_cosmos_enabled:
            self._init_local_storage()
    
    def _check_cosmos_config(self) -> bool:
        """Check if Cosmos DB is configured"""
        cosmos_conn = os.getenv('AZURE_COSMOS_CONNECTION_STRING', '')
        return cosmos_conn and cosmos_conn != 'dev-mode-local-storage'
    
    def _init_local_storage(self):
        """Initialize local JSON storage"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        if not os.path.exists(self.storage_path):
            # Create initial spiritual texts
            initial_texts = [
                SpiritualText(
                    id="bg_2_47",
                    title="On Duty Without Attachment",
                    content="You have a right to perform your prescribed duty, but not to the fruits of action. Never consider yourself to be the cause of the results of your activities, and never be attached to not doing your duty.",
                    source="Bhagavad Gita",
                    chapter="2",
                    verse="47",
                    category="dharma"
                ),
                SpiritualText(
                    id="bg_6_19",
                    title="Steady Mind in Meditation",
                    content="As a lamp in a windless place does not waver, so the transcendentalist, whose mind is controlled, remains always steady in his meditation on the transcendent Self.",
                    source="Bhagavad Gita",
                    chapter="6",
                    verse="19",
                    category="meditation"
                ),
                SpiritualText(
                    id="bg_12_6_7",
                    title="Devotion and Surrender",
                    content="But those who worship Me, giving up all their activities unto Me and being devoted to Me without deviation, engaged in devotional service and always meditating upon Me, having fixed their minds upon Me, O son of Pritha—for them I am the swift deliverer from the ocean of birth and death.",
                    source="Bhagavad Gita",
                    chapter="12",
                    verse="6-7",
                    category="devotion"
                ),
                SpiritualText(
                    id="bg_2_14",
                    title="Accepting Pleasure and Pain",
                    content="O son of Kunti, the nonpermanent appearance of happiness and distress, and their disappearance in due course, are like the appearance and disappearance of winter and summer seasons. They arise from sense perception, O scion of Bharata, and one must learn to tolerate them without being disturbed.",
                    source="Bhagavad Gita",
                    chapter="2",
                    verse="14",
                    category="equanimity"
                ),
                SpiritualText(
                    id="bg_2_20",
                    title="Eternal Nature of the Soul",
                    content="For the soul there is neither birth nor death nor, having once been, does he ever cease to be. He is unborn, eternal, permanent, and primeval. He is not slain when the body is slain.",
                    source="Bhagavad Gita",
                    chapter="2",
                    verse="20",
                    category="soul"
                )
            ]
            
            self._save_local_data([asdict(text) for text in initial_texts])
            logger.info(f"✅ Initialized local storage with {len(initial_texts)} spiritual texts")
    
    def _load_local_data(self) -> List[Dict[str, Any]]:
        """Load data from local JSON storage"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_local_data(self, data: List[Dict[str, Any]]):
        """Save data to local JSON storage"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_spiritual_text(self, text_id: str) -> Optional[SpiritualText]:
        """Get a specific spiritual text by ID"""
        if self.is_cosmos_enabled:
            return self._get_from_cosmos(text_id)
        else:
            return self._get_from_local(text_id)
    
    def _get_from_local(self, text_id: str) -> Optional[SpiritualText]:
        """Get spiritual text from local storage"""
        data = self._load_local_data()
        for item in data:
            if item.get('id') == text_id:
                return SpiritualText(**item)
        return None
    
    def search_spiritual_texts(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[SpiritualText]:
        """Search spiritual texts by content or category"""
        if self.is_cosmos_enabled:
            return self._search_in_cosmos(query, category, limit)
        else:
            return self._search_in_local(query, category, limit)
    
    def _search_in_local(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[SpiritualText]:
        """Search in local storage"""
        data = self._load_local_data()
        results = []
        
        query_lower = query.lower()
        
        for item in data:
            # Check category filter
            if category and item.get('category') != category:
                continue
            
            # Search in content, title, or source
            if (query_lower in item.get('content', '').lower() or
                query_lower in item.get('title', '').lower() or
                query_lower in item.get('source', '').lower()):
                results.append(SpiritualText(**item))
            
            if len(results) >= limit:
                break
        
        return results
    
    def add_spiritual_text(self, text: SpiritualText) -> bool:
        """Add a new spiritual text"""
        if self.is_cosmos_enabled:
            return self._add_to_cosmos(text)
        else:
            return self._add_to_local(text)
    
    def _add_to_local(self, text: SpiritualText) -> bool:
        """Add spiritual text to local storage"""
        try:
            data = self._load_local_data()
            data.append(asdict(text))
            self._save_local_data(data)
            logger.info(f"✅ Added spiritual text: {text.id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add spiritual text: {e}")
            return False
    
    def get_all_spiritual_texts(self) -> List[SpiritualText]:
        """Get all spiritual texts"""
        if self.is_cosmos_enabled:
            return self._get_all_from_cosmos()
        else:
            return self._get_all_from_local()
    
    def _get_all_from_local(self) -> List[SpiritualText]:
        """Get all spiritual texts from local storage"""
        data = self._load_local_data()
        return [SpiritualText(**item) for item in data]
    
    def get_texts_by_category(self, category: str) -> List[SpiritualText]:
        """Get texts by category"""
        if self.is_cosmos_enabled:
            return self._get_category_from_cosmos(category)
        else:
            return self._get_category_from_local(category)
    
    def _get_category_from_local(self, category: str) -> List[SpiritualText]:
        """Get texts by category from local storage"""
        data = self._load_local_data()
        return [SpiritualText(**item) for item in data if item.get('category') == category]
    
    # Cosmos DB methods (placeholder for future implementation)
    def _get_from_cosmos(self, text_id: str) -> Optional[SpiritualText]:
        """Get spiritual text from Cosmos DB (placeholder)"""
        logger.warning("Cosmos DB not implemented yet, using local storage")
        return self._get_from_local(text_id)
    
    def _search_in_cosmos(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[SpiritualText]:
        """Search in Cosmos DB (placeholder)"""
        logger.warning("Cosmos DB not implemented yet, using local storage")
        return self._search_in_local(query, category, limit)
    
    def _add_to_cosmos(self, text: SpiritualText) -> bool:
        """Add to Cosmos DB (placeholder)"""
        logger.warning("Cosmos DB not implemented yet, using local storage")
        return self._add_to_local(text)
    
    def _get_all_from_cosmos(self) -> List[SpiritualText]:
        """Get all from Cosmos DB (placeholder)"""
        logger.warning("Cosmos DB not implemented yet, using local storage")
        return self._get_all_from_local()
    
    def _get_category_from_cosmos(self, category: str) -> List[SpiritualText]:
        """Get category from Cosmos DB (placeholder)"""
        logger.warning("Cosmos DB not implemented yet, using local storage")
        return self._get_category_from_local(category)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get database health status"""
        try:
            if self.is_cosmos_enabled:
                # TODO: Implement Cosmos DB health check
                return {
                    "status": "healthy",
                    "storage_type": "cosmos_db",
                    "connection": "placeholder"
                }
            else:
                texts = self._get_all_from_local()
                return {
                    "status": "healthy",
                    "storage_type": "local_json",
                    "total_texts": len(texts),
                    "storage_path": self.storage_path
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global database service instance
db_service = DatabaseService()
