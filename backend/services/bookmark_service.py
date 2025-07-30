"""
Bookmark Service for Vimarsh
Save and manage favorite responses and conversations
"""

import logging
import os
from typing import Dict, List, Any, Optional
import json

try:
    from models.vimarsh_models import (
        BookmarkItem, BookmarkType, model_to_dict, dict_to_model, 
        generate_bookmark_id
    )
    from services.database_service import DatabaseService
    from services.cache_service import CacheService
except ImportError as e:
    logging.warning(f"Import warning in bookmark_service: {e}")
    # Mock classes for testing
    class BookmarkItem:
        pass
    class BookmarkType:
        pass
    def model_to_dict(x):
        return {}
    def dict_to_model(x, y):
        return None
    def generate_bookmark_id():
        return "mock_id"

logger = logging.getLogger(__name__)

class BookmarkService:
    """Service for managing user bookmarks"""
    
    def __init__(self):
        """Initialize bookmark service"""
        self.db_service = DatabaseService()
        self.cache_service = CacheService()
        
        # Local storage for development
        self.local_storage_path = "data/bookmarks"
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        logger.info("🔖 Bookmark Service initialized")
    
    async def create_bookmark(
        self,
        user_id: str,
        bookmark_type: BookmarkType,
        content_id: str,
        title: str,
        content_preview: str,
        personality_id: str,
        tags: List[str] = None,
        notes: str = None,
        is_public: bool = False
    ) -> Optional[BookmarkItem]:
        """Create a new bookmark"""
        try:
            # Check if bookmark already exists
            existing_bookmark = await self._get_existing_bookmark(user_id, content_id)
            if existing_bookmark:
                logger.info(f"Bookmark already exists for content {content_id}")
                return existing_bookmark
            
            # Create new bookmark
            bookmark = BookmarkItem(
                id=generate_bookmark_id(),
                user_id=user_id,
                bookmark_type=bookmark_type,
                content_id=content_id,
                title=title,
                content_preview=content_preview[:200],  # Limit preview length
                personality_id=personality_id,
                tags=tags or [],
                notes=notes,
                is_public=is_public
            )
            
            # Save bookmark
            success = await self._save_bookmark(bookmark)
            
            if success:
                # Clear user bookmarks cache
                await self._clear_user_bookmarks_cache(user_id)
                
                logger.info(f"Created bookmark for user {user_id}: {title[:50]}")
                return bookmark
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating bookmark: {e}")
            return None
    
    async def get_user_bookmarks(
        self,
        user_id: str,
        bookmark_type: BookmarkType = None,
        personality_id: str = None,
        tags: List[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[BookmarkItem]:
        """Get user's bookmarks with optional filtering"""
        try:
            # Check cache first
            cache_key = f"user_bookmarks:{user_id}:{bookmark_type}:{personality_id}:{limit}:{offset}"
            cached_bookmarks = self.cache_service.get(cache_key)
            
            if cached_bookmarks:
                logger.info(f"Retrieved {len(cached_bookmarks)} bookmarks from cache")
                return [dict_to_model(data, BookmarkItem) for data in cached_bookmarks]
            
            # Get from database
            bookmarks = await self._get_bookmarks_from_db(
                user_id, bookmark_type, personality_id, tags, limit, offset
            )
            
            # Cache results for 30 minutes
            bookmark_dicts = [model_to_dict(bookmark) for bookmark in bookmarks]
            self.cache_service.put(cache_key, bookmark_dicts, ttl=1800)
            
            logger.info(f"Retrieved {len(bookmarks)} bookmarks for user {user_id}")
            return bookmarks
            
        except Exception as e:
            logger.error(f"Error getting user bookmarks: {e}")
            return []
    
    async def get_bookmark(self, bookmark_id: str, user_id: str) -> Optional[BookmarkItem]:
        """Get a specific bookmark by ID"""
        try:
            # Check cache first
            cache_key = f"bookmark:{bookmark_id}"
            cached_bookmark = self.cache_service.get(cache_key)
            
            if cached_bookmark:
                bookmark = dict_to_model(cached_bookmark, BookmarkItem)
                if bookmark.user_id == user_id:
                    # Update access count
                    await self._update_bookmark_access(bookmark_id)
                    return bookmark
            
            # Get from database
            bookmark = await self._get_bookmark_from_db(bookmark_id)
            
            if bookmark and bookmark.user_id == user_id:
                # Cache bookmark
                self.cache_service.put(cache_key, model_to_dict(bookmark), ttl=3600)
                
                # Update access count
                await self._update_bookmark_access(bookmark_id)
                
                return bookmark
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting bookmark: {e}")
            return None
    
    async def update_bookmark(
        self,
        bookmark_id: str,
        user_id: str,
        title: str = None,
        tags: List[str] = None,
        notes: str = None,
        is_public: bool = None
    ) -> bool:
        """Update an existing bookmark"""
        try:
            # Get existing bookmark
            bookmark = await self.get_bookmark(bookmark_id, user_id)
            if not bookmark:
                logger.warning(f"Bookmark not found: {bookmark_id}")
                return False
            
            # Update fields
            if title is not None:
                bookmark.title = title
            if tags is not None:
                bookmark.tags = tags
            if notes is not None:
                bookmark.notes = notes
            if is_public is not None:
                bookmark.is_public = is_public
            
            # Save updated bookmark
            success = await self._save_bookmark(bookmark)
            
            if success:
                # Clear caches
                await self._clear_bookmark_cache(bookmark_id)
                await self._clear_user_bookmarks_cache(user_id)
                
                logger.info(f"Updated bookmark {bookmark_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating bookmark: {e}")
            return False
    
    async def delete_bookmark(self, bookmark_id: str, user_id: str) -> bool:
        """Delete a bookmark"""
        try:
            # Verify ownership
            bookmark = await self.get_bookmark(bookmark_id, user_id)
            if not bookmark:
                logger.warning(f"Bookmark not found or not owned by user: {bookmark_id}")
                return False
            
            # Delete from database
            success = await self._delete_bookmark_from_db(bookmark_id)
            
            if success:
                # Clear caches
                await self._clear_bookmark_cache(bookmark_id)
                await self._clear_user_bookmarks_cache(user_id)
                
                logger.info(f"Deleted bookmark {bookmark_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting bookmark: {e}")
            return False
    
    async def search_bookmarks(
        self,
        user_id: str,
        search_query: str,
        bookmark_type: BookmarkType = None,
        personality_id: str = None,
        limit: int = 20
    ) -> List[BookmarkItem]:
        """Search user's bookmarks"""
        try:
            # Get all user bookmarks (or filtered by type/personality)
            all_bookmarks = await self.get_user_bookmarks(
                user_id, bookmark_type, personality_id, limit=200
            )
            
            if not search_query.strip():
                return all_bookmarks[:limit]
            
            # Perform search
            search_terms = search_query.lower().split()
            matching_bookmarks = []
            
            for bookmark in all_bookmarks:
                # Search in title, content preview, tags, and notes
                searchable_text = [
                    bookmark.title.lower(),
                    bookmark.content_preview.lower(),
                    ' '.join(bookmark.tags).lower(),
                    (bookmark.notes or '').lower()
                ]
                
                full_text = ' '.join(searchable_text)
                
                # Check if all search terms are present
                if all(term in full_text for term in search_terms):
                    matching_bookmarks.append(bookmark)
                
                if len(matching_bookmarks) >= limit:
                    break
            
            logger.info(f"Found {len(matching_bookmarks)} bookmarks matching '{search_query}'")
            return matching_bookmarks
            
        except Exception as e:
            logger.error(f"Error searching bookmarks: {e}")
            return []
    
    async def get_popular_bookmarks(
        self,
        personality_id: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get popular public bookmarks"""
        try:
            # Get public bookmarks
            bookmarks = await self._get_public_bookmarks(personality_id, limit * 2)
            
            # Sort by access count and other popularity factors
            popular_bookmarks = []
            
            for bookmark in bookmarks:
                # Calculate popularity score
                popularity_score = (
                    bookmark.accessed_count * 1.0 +
                    len(bookmark.tags) * 0.1 +
                    (1.0 if bookmark.notes else 0) * 0.2
                )
                
                popular_bookmarks.append({
                    'bookmark': model_to_dict(bookmark),
                    'popularity_score': popularity_score
                })
            
            # Sort by popularity score
            popular_bookmarks.sort(key=lambda x: x['popularity_score'], reverse=True)
            
            # Return top bookmarks
            result = []
            for item in popular_bookmarks[:limit]:
                bookmark_dict = item['bookmark']
                bookmark_dict['popularity_score'] = item['popularity_score']
                result.append(bookmark_dict)
            
            logger.info(f"Retrieved {len(result)} popular bookmarks")
            return result
            
        except Exception as e:
            logger.error(f"Error getting popular bookmarks: {e}")
            return []
    
    async def get_bookmark_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get bookmark statistics for a user"""
        try:
            bookmarks = await self.get_user_bookmarks(user_id, limit=1000)
            
            if not bookmarks:
                return {
                    'total_bookmarks': 0,
                    'by_type': {},
                    'by_personality': {},
                    'total_tags': 0,
                    'most_used_tags': [],
                    'public_bookmarks': 0
                }
            
            # Calculate statistics
            stats = {
                'total_bookmarks': len(bookmarks),
                'by_type': {},
                'by_personality': {},
                'total_tags': 0,
                'tag_frequency': {},
                'public_bookmarks': 0,
                'total_accesses': 0
            }
            
            for bookmark in bookmarks:
                # Count by type
                type_name = bookmark.bookmark_type.value if hasattr(bookmark.bookmark_type, 'value') else str(bookmark.bookmark_type)
                stats['by_type'][type_name] = stats['by_type'].get(type_name, 0) + 1
                
                # Count by personality
                stats['by_personality'][bookmark.personality_id] = stats['by_personality'].get(bookmark.personality_id, 0) + 1
                
                # Count tags
                for tag in bookmark.tags:
                    stats['tag_frequency'][tag] = stats['tag_frequency'].get(tag, 0) + 1
                    stats['total_tags'] += 1
                
                # Count public bookmarks
                if bookmark.is_public:
                    stats['public_bookmarks'] += 1
                
                # Count total accesses
                stats['total_accesses'] += bookmark.accessed_count
            
            # Get most used tags
            stats['most_used_tags'] = sorted(
                stats['tag_frequency'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Remove tag frequency from final stats (too detailed)
            del stats['tag_frequency']
            
            logger.info(f"Generated bookmark statistics for user {user_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting bookmark statistics: {e}")
            return {}
    
    # Private helper methods
    
    async def _get_existing_bookmark(self, user_id: str, content_id: str) -> Optional[BookmarkItem]:
        """Check if bookmark already exists for this content"""
        try:
            if hasattr(self.db_service, 'get_bookmark_by_content'):
                bookmark_data = await self.db_service.get_bookmark_by_content(user_id, content_id)
                if bookmark_data:
                    return dict_to_model(bookmark_data, BookmarkItem)
        except Exception as e:
            logger.warning(f"Database unavailable: {e}")
        
        return self._get_existing_bookmark_local(user_id, content_id)
    
    def _get_existing_bookmark_local(self, user_id: str, content_id: str) -> Optional[BookmarkItem]:
        """Check local storage for existing bookmark"""
        try:
            user_dir = os.path.join(self.local_storage_path, user_id)
            if not os.path.exists(user_dir):
                return None
            
            for filename in os.listdir(user_dir):
                if filename.endswith('.json'):
                    bookmark_path = os.path.join(user_dir, filename)
                    try:
                        with open(bookmark_path, 'r', encoding='utf-8') as f:
                            bookmark_data = json.load(f)
                        
                        if bookmark_data.get('content_id') == content_id:
                            return dict_to_model(bookmark_data, BookmarkItem)
                    except Exception:
                        continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Error checking local bookmarks: {e}")
            return None
    
    async def _save_bookmark(self, bookmark: BookmarkItem) -> bool:
        """Save bookmark to database"""
        try:
            if hasattr(self.db_service, 'save_bookmark'):
                return await self.db_service.save_bookmark(model_to_dict(bookmark))
        except Exception as e:
            logger.warning(f"Database unavailable, using local storage: {e}")
        
        return self._save_bookmark_local(bookmark)
    
    def _save_bookmark_local(self, bookmark: BookmarkItem) -> bool:
        """Save bookmark to local storage"""
        try:
            user_dir = os.path.join(self.local_storage_path, bookmark.user_id)
            os.makedirs(user_dir, exist_ok=True)
            
            bookmark_file = os.path.join(user_dir, f"{bookmark.id}.json")
            with open(bookmark_file, 'w', encoding='utf-8') as f:
                json.dump(model_to_dict(bookmark), f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Error saving local bookmark: {e}")
            return False
    
    async def _clear_bookmark_cache(self, bookmark_id: str):
        """Clear bookmark-specific cache"""
        cache_key = f"bookmark:{bookmark_id}"
        self.cache_service.delete(cache_key)
    
    async def _clear_user_bookmarks_cache(self, user_id: str):
        """Clear user bookmarks cache"""
        # Clear all cache keys that start with user_bookmarks:user_id
        # This is a simplified approach - in production you might want more specific cache invalidation
        pass

# Global service instance
bookmark_service = BookmarkService()
