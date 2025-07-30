"""
Sharing Service for Vimarsh
Share wisdom quotes and conversations
"""

import logging
import os
from typing import Dict, List, Any, Optional
import json
from urllib.parse import quote

try:
    from models.vimarsh_models import (
        SharedContent, ShareType, model_to_dict, dict_to_model,
        generate_share_id
    )
    from services.database_service import DatabaseService
    from services.cache_service import CacheService
except ImportError as e:
    logging.warning(f"Import warning in sharing_service: {e}")
    # Mock classes for testing
    class SharedContent:
        pass
    class ShareType:
        pass
    def model_to_dict(x):
        return {}
    def dict_to_model(x, y):
        return None
    def generate_share_id():
        return "mock_id"

logger = logging.getLogger(__name__)

class SharingService:
    """Service for sharing wisdom quotes and conversations"""
    
    def __init__(self):
        """Initialize sharing service"""
        self.db_service = DatabaseService()
        self.cache_service = CacheService()
        
        # Local storage for development
        self.local_storage_path = "data/shared_content"
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        # Base URL for sharing (configurable)
        self.base_share_url = os.getenv('VIMARSH_SHARE_URL', 'https://vimarsh.app/share')
        
        logger.info("🔗 Sharing Service initialized")
    
    async def create_share(
        self,
        user_id: str,
        share_type: ShareType,
        content: str,
        personality_id: str,
        title: str = None,
        description: str = None,
        is_public: bool = True,
        expires_in_days: int = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[SharedContent]:
        """Create a shareable link for content"""
        try:
            # Generate share URL
            share_id = generate_share_id()
            share_url = f"{self.base_share_url}/{share_id}"
            
            # Create share object
            shared_content = SharedContent(
                id=share_id,
                user_id=user_id,
                share_type=share_type,
                content=content,
                personality_id=personality_id,
                title=title or self._generate_title(content, personality_id),
                description=description,
                share_url=share_url,
                is_public=is_public,
                expires_in_days=expires_in_days,
                metadata=metadata or {}
            )
            
            # Save shared content
            success = await self._save_shared_content(shared_content)
            
            if success:
                # Track sharing analytics
                await self._track_share_created(user_id, personality_id, share_type)
                
                logger.info(f"Created share {share_id} for user {user_id}")
                return shared_content
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating share: {e}")
            return None
    
    async def get_shared_content(self, share_id: str) -> Optional[SharedContent]:
        """Get shared content by share ID"""
        try:
            # Check cache first
            cache_key = f"shared_content:{share_id}"
            cached_content = self.cache_service.get(cache_key)
            
            if cached_content:
                shared_content = dict_to_model(cached_content, SharedContent)
                
                # Check if not expired
                if not shared_content.is_expired():
                    # Track view
                    await self._track_share_viewed(share_id)
                    return shared_content
            
            # Get from database
            shared_content = await self._get_shared_content_from_db(share_id)
            
            if shared_content and not shared_content.is_expired():
                # Cache for 1 hour
                self.cache_service.put(cache_key, model_to_dict(shared_content), ttl=3600)
                
                # Track view
                await self._track_share_viewed(share_id)
                
                return shared_content
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting shared content: {e}")
            return None
    
    async def get_user_shares(
        self,
        user_id: str,
        share_type: ShareType = None,
        personality_id: str = None,
        include_expired: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[SharedContent]:
        """Get user's shared content"""
        try:
            # Check cache first
            cache_key = f"user_shares:{user_id}:{share_type}:{personality_id}:{include_expired}:{limit}:{offset}"
            cached_shares = self.cache_service.get(cache_key)
            
            if cached_shares:
                logger.info(f"Retrieved {len(cached_shares)} shares from cache")
                return [dict_to_model(data, SharedContent) for data in cached_shares]
            
            # Get from database
            shares = await self._get_user_shares_from_db(
                user_id, share_type, personality_id, include_expired, limit, offset
            )
            
            # Cache results for 15 minutes
            share_dicts = [model_to_dict(share) for share in shares]
            self.cache_service.put(cache_key, share_dicts, ttl=900)
            
            logger.info(f"Retrieved {len(shares)} shares for user {user_id}")
            return shares
            
        except Exception as e:
            logger.error(f"Error getting user shares: {e}")
            return []
    
    async def update_share(
        self,
        share_id: str,
        user_id: str,
        title: str = None,
        description: str = None,
        is_public: bool = None,
        expires_in_days: int = None
    ) -> bool:
        """Update shared content"""
        try:
            # Get existing share
            shared_content = await self.get_shared_content(share_id)
            if not shared_content or shared_content.user_id != user_id:
                logger.warning(f"Share not found or not owned by user: {share_id}")
                return False
            
            # Update fields
            if title is not None:
                shared_content.title = title
            if description is not None:
                shared_content.description = description
            if is_public is not None:
                shared_content.is_public = is_public
            if expires_in_days is not None:
                shared_content.expires_in_days = expires_in_days
            
            # Save updated share
            success = await self._save_shared_content(shared_content)
            
            if success:
                # Clear cache
                await self._clear_share_cache(share_id)
                await self._clear_user_shares_cache(user_id)
                
                logger.info(f"Updated share {share_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating share: {e}")
            return False
    
    async def delete_share(self, share_id: str, user_id: str) -> bool:
        """Delete shared content"""
        try:
            # Verify ownership
            shared_content = await self.get_shared_content(share_id)
            if not shared_content or shared_content.user_id != user_id:
                logger.warning(f"Share not found or not owned by user: {share_id}")
                return False
            
            # Delete from database
            success = await self._delete_shared_content_from_db(share_id)
            
            if success:
                # Clear caches
                await self._clear_share_cache(share_id)
                await self._clear_user_shares_cache(user_id)
                
                logger.info(f"Deleted share {share_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting share: {e}")
            return False
    
    async def get_popular_shares(
        self,
        personality_id: str = None,
        share_type: ShareType = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get popular shared content"""
        try:
            # Get public shares
            shares = await self._get_public_shares(personality_id, share_type, limit * 2)
            
            # Sort by popularity (views, likes, recency)
            popular_shares = []
            
            for share in shares:
                # Calculate popularity score
                popularity_score = (
                    share.view_count * 1.0 +
                    share.like_count * 2.0 +
                    (1.0 if share.description else 0) * 0.1
                )
                
                # Boost recent shares
                days_old = (share.created_at.timestamp() - share.created_at.timestamp()) / 86400
                if days_old < 7:  # Boost shares from last week
                    popularity_score *= 1.2
                
                popular_shares.append({
                    'share': model_to_dict(share),
                    'popularity_score': popularity_score
                })
            
            # Sort by popularity score
            popular_shares.sort(key=lambda x: x['popularity_score'], reverse=True)
            
            # Return top shares
            result = []
            for item in popular_shares[:limit]:
                share_dict = item['share']
                share_dict['popularity_score'] = item['popularity_score']
                result.append(share_dict)
            
            logger.info(f"Retrieved {len(result)} popular shares")
            return result
            
        except Exception as e:
            logger.error(f"Error getting popular shares: {e}")
            return []
    
    async def generate_embed_code(self, share_id: str) -> Optional[str]:
        """Generate HTML embed code for shared content"""
        try:
            shared_content = await self.get_shared_content(share_id)
            if not shared_content or not shared_content.is_public:
                return None
            
            # Generate embed HTML
            embed_html = f"""
<div class="vimarsh-embed" data-share-id="{share_id}">
    <div class="vimarsh-quote">
        <blockquote>
            {self._escape_html(shared_content.content[:200])}
            {"..." if len(shared_content.content) > 200 else ""}
        </blockquote>
        <cite>— {shared_content.personality_id}</cite>
    </div>
    <div class="vimarsh-footer">
        <a href="{shared_content.share_url}" target="_blank" class="vimarsh-link">
            View on Vimarsh
        </a>
    </div>
</div>
<style>
.vimarsh-embed {{
    max-width: 500px;
    padding: 20px;
    border-left: 4px solid #4A90E2;
    background: #f8f9fa;
    font-family: Georgia, serif;
    margin: 20px 0;
}}
.vimarsh-quote blockquote {{
    margin: 0;
    font-style: italic;
    font-size: 16px;
    line-height: 1.6;
    color: #333;
}}
.vimarsh-quote cite {{
    display: block;
    margin-top: 10px;
    font-size: 14px;
    color: #666;
    font-weight: bold;
}}
.vimarsh-footer {{
    margin-top: 15px;
    text-align: right;
}}
.vimarsh-link {{
    color: #4A90E2;
    text-decoration: none;
    font-size: 12px;
}}
</style>
"""
            
            return embed_html.strip()
            
        except Exception as e:
            logger.error(f"Error generating embed code: {e}")
            return None
    
    async def generate_social_share_urls(self, share_id: str) -> Dict[str, str]:
        """Generate social media sharing URLs"""
        try:
            shared_content = await self.get_shared_content(share_id)
            if not shared_content:
                return {}
            
            # Prepare share text
            share_text = f"{shared_content.title} - {shared_content.personality_id}"
            if shared_content.description:
                share_text += f" | {shared_content.description[:100]}"
            
            share_url = shared_content.share_url
            encoded_text = quote(share_text)
            encoded_url = quote(share_url)
            
            # Generate platform-specific URLs
            social_urls = {
                'twitter': f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}",
                'facebook': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
                'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
                'whatsapp': f"https://wa.me/?text={encoded_text} {encoded_url}",
                'telegram': f"https://t.me/share/url?url={encoded_url}&text={encoded_text}",
                'reddit': f"https://reddit.com/submit?url={encoded_url}&title={encoded_text}",
                'email': f"mailto:?subject={encoded_text}&body={encoded_url}"
            }
            
            return social_urls
            
        except Exception as e:
            logger.error(f"Error generating social share URLs: {e}")
            return {}
    
    async def get_share_analytics(self, share_id: str, user_id: str) -> Dict[str, Any]:
        """Get analytics for a shared content"""
        try:
            # Verify ownership
            shared_content = await self.get_shared_content(share_id)
            if not shared_content or shared_content.user_id != user_id:
                return {}
            
            # Get analytics data
            analytics = {
                'share_id': share_id,
                'total_views': shared_content.view_count,
                'total_likes': shared_content.like_count,
                'created_at': shared_content.created_at.isoformat(),
                'is_public': shared_content.is_public,
                'is_expired': shared_content.is_expired(),
                'share_url': shared_content.share_url
            }
            
            # Add detailed view analytics if available
            view_analytics = await self._get_view_analytics(share_id)
            if view_analytics:
                analytics.update(view_analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting share analytics: {e}")
            return {}
    
    # Private helper methods
    
    def _generate_title(self, content: str, personality_id: str) -> str:
        """Generate a title for shared content"""
        # Take first sentence or first 50 characters
        first_sentence = content.split('.')[0]
        if len(first_sentence) > 50:
            title = content[:47] + "..."
        else:
            title = first_sentence
        
        return f"{title} - {personality_id}"
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    async def _save_shared_content(self, shared_content: SharedContent) -> bool:
        """Save shared content to database"""
        try:
            if hasattr(self.db_service, 'save_shared_content'):
                return await self.db_service.save_shared_content(model_to_dict(shared_content))
        except Exception as e:
            logger.warning(f"Database unavailable, using local storage: {e}")
        
        return self._save_shared_content_local(shared_content)
    
    def _save_shared_content_local(self, shared_content: SharedContent) -> bool:
        """Save shared content to local storage"""
        try:
            share_file = os.path.join(self.local_storage_path, f"{shared_content.id}.json")
            with open(share_file, 'w', encoding='utf-8') as f:
                json.dump(model_to_dict(shared_content), f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Error saving local shared content: {e}")
            return False
    
    async def _get_shared_content_from_db(self, share_id: str):
        """Get shared content from database"""
        try:
            if hasattr(self.db_service, 'get_shared_content'):
                content_data = await self.db_service.get_shared_content(share_id)
                if content_data:
                    return dict_to_model(content_data, SharedContent)
        except Exception as e:
            logger.warning(f"Database unavailable: {e}")
        
        return self._get_shared_content_local(share_id)
    
    def _get_shared_content_local(self, share_id: str):
        """Get shared content from local storage"""
        try:
            share_file = os.path.join(self.local_storage_path, f"{share_id}.json")
            if os.path.exists(share_file):
                with open(share_file, 'r', encoding='utf-8') as f:
                    content_data = json.load(f)
                return dict_to_model(content_data, SharedContent)
            return None
        except Exception as e:
            logger.error(f"Error loading local shared content: {e}")
            return None
    
    async def _track_share_created(self, user_id: str, personality_id: str, share_type: ShareType):
        """Track share creation for analytics"""
        try:
            # This would integrate with analytics service
            pass
        except Exception as e:
            logger.warning(f"Analytics tracking failed: {e}")
    
    async def _track_share_viewed(self, share_id: str):
        """Track share view for analytics"""
        try:
            # Increment view count
            pass
        except Exception as e:
            logger.warning(f"View tracking failed: {e}")
    
    async def _clear_share_cache(self, share_id: str):
        """Clear share-specific cache"""
        cache_key = f"shared_content:{share_id}"
        self.cache_service.delete(cache_key)
    
    async def _clear_user_shares_cache(self, user_id: str):
        """Clear user shares cache"""
        # Clear all cache keys that start with user_shares:user_id
        pass

# Global service instance
sharing_service = SharingService()
