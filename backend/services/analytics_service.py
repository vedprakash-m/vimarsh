"""
Analytics Service for Vimarsh
Comprehensive user analytics, query tracking, and popularity metrics
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
from collections import defaultdict, Counter

try:
    from models.vimarsh_models import (
        UserAnalyticsEvent, EventType, PersonalityUsageStats, 
        DailyAnalyticsSummary, model_to_dict, 
        dict_to_model, generate_analytics_id
    )
    from services.database_service import DatabaseService
    from services.cache_service import CacheService
except ImportError as e:
    logging.warning(f"Import warning in analytics_service: {e}")
    # Mock classes for testing
    UserAnalyticsEvent = None
    EventType = None
    PersonalityUsageStats = None

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for tracking and analyzing user interactions"""
    
    def __init__(self):
        """Initialize analytics service"""
        self.db_service = DatabaseService()
        self.cache_service = CacheService()
        
        # Local storage for development
        self.local_storage_path = "data/analytics"
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        # Cache popular queries
        self.popular_queries_cache = {}
        self.personality_stats_cache = {}
        
        logger.info("📊 Analytics Service initialized")
    
    async def track_event(
        self,
        user_id: str,
        session_id: str,
        event_type: EventType,
        event_data: Dict[str, Any],
        personality_id: str = None,
        response_quality: str = None,
        response_time_ms: int = None,
        tokens_used: int = None,
        cost_usd: float = None
    ) -> bool:
        """Track a user analytics event"""
        try:
            # Create analytics event
            event = UserAnalyticsEvent(
                id=generate_analytics_id(),
                user_id=user_id,
                session_id=session_id,
                event_type=event_type,
                event_data=event_data,
                timestamp=datetime.utcnow().isoformat(),
                personality_id=personality_id,
                response_quality=response_quality,
                response_time_ms=response_time_ms,
                tokens_used=tokens_used,
                cost_usd=cost_usd
            )
            
            # Save to database
            await self._save_event_to_db(event)
            
            # Update real-time caches
            await self._update_real_time_stats(event)
            
            logger.info(f"Tracked analytics event: {event_type.value} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking analytics event: {e}")
            return False
    
    async def track_query(
        self,
        user_id: str,
        session_id: str,
        query: str,
        personality_id: str,
        response: str,
        response_time_ms: int,
        tokens_used: int = None,
        cost_usd: float = None,
        citations: List[str] = None
    ) -> bool:
        """Track a spiritual guidance query"""
        try:
            event_data = {
                "query": query,
                "response_length": len(response),
                "personality": personality_id,
                "citations_count": len(citations) if citations else 0,
                "has_citations": bool(citations)
            }
            
            # Determine response quality based on various factors
            response_quality = self._determine_response_quality(
                response, response_time_ms, citations
            )
            
            await self.track_event(
                user_id=user_id,
                session_id=session_id,
                event_type=EventType.QUERY_RECEIVED,
                event_data=event_data,
                personality_id=personality_id,
                response_quality=response_quality,
                response_time_ms=response_time_ms,
                tokens_used=tokens_used,
                cost_usd=cost_usd
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error tracking query: {e}")
            return False
    
    async def get_personality_stats(
        self,
        time_period: str = "7d"  # 1d, 7d, 30d, all
    ) -> Dict[str, PersonalityUsageStats]:
        """Get personality usage statistics"""
        try:
            # Check cache first
            cache_key = f"personality_stats:{time_period}"
            cached_stats = self.cache_service.get(cache_key)
            
            if cached_stats:
                logger.info(f"Retrieved personality stats from cache: {time_period}")
                return cached_stats
            
            # Calculate stats from events
            events = await self._get_events_by_period(time_period)
            stats = self._calculate_personality_stats(events)
            
            # Cache results for 1 hour
            self.cache_service.put(cache_key, stats, ttl=3600)
            
            logger.info(f"Calculated personality stats for {time_period}: {len(stats)} personalities")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting personality stats: {e}")
            return {}
    
    async def get_popular_questions(
        self,
        personality_id: str = None,
        limit: int = 10,
        time_period: str = "7d"
    ) -> List[Dict[str, Any]]:
        """Get most popular questions"""
        try:
            cache_key = f"popular_questions:{personality_id or 'all'}:{time_period}:{limit}"
            cached_questions = self.cache_service.get(cache_key)
            
            if cached_questions:
                logger.info("Retrieved popular questions from cache")
                return cached_questions
            
            # Get events and analyze queries
            events = await self._get_events_by_period(time_period)
            
            # Filter by personality if specified
            if personality_id:
                events = [e for e in events if e.personality_id == personality_id]
            
            # Extract and count queries
            query_counter = Counter()
            query_details = {}
            
            for event in events:
                if event.event_type == EventType.QUERY_RECEIVED:
                    query = event.event_data.get('query', '').strip()
                    if query and len(query) > 10:  # Filter out very short queries
                        query_counter[query] += 1
                        
                        # Store additional details
                        if query not in query_details:
                            query_details[query] = {
                                'query': query,
                                'count': 0,
                                'personalities': set(),
                                'avg_response_time': 0,
                                'total_response_time': 0,
                                'response_times': []
                            }
                        
                        details = query_details[query]
                        details['count'] += 1
                        details['personalities'].add(event.personality_id or 'unknown')
                        
                        if event.response_time_ms:
                            details['response_times'].append(event.response_time_ms)
                            details['total_response_time'] += event.response_time_ms
                            details['avg_response_time'] = details['total_response_time'] / len(details['response_times'])
            
            # Format results
            popular_questions = []
            for query, count in query_counter.most_common(limit):
                details = query_details[query]
                popular_questions.append({
                    'query': query,
                    'count': count,
                    'personalities': list(details['personalities']),
                    'avg_response_time_ms': round(details['avg_response_time'], 2),
                    'popularity_score': count  # Can be enhanced with more factors
                })
            
            # Cache results for 2 hours
            self.cache_service.put(cache_key, popular_questions, ttl=7200)
            
            logger.info(f"Found {len(popular_questions)} popular questions")
            return popular_questions
            
        except Exception as e:
            logger.error(f"Error getting popular questions: {e}")
            return []
    
    async def get_user_analytics(
        self,
        user_id: str,
        time_period: str = "30d"
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a specific user"""
        try:
            # Get user events
            events = await self._get_user_events(user_id, time_period)
            
            if not events:
                return {
                    'user_id': user_id,
                    'total_queries': 0,
                    'total_sessions': 0,
                    'personality_usage': {},
                    'avg_response_time': 0,
                    'total_cost': 0,
                    'activity_timeline': []
                }
            
            # Calculate analytics
            analytics = self._calculate_user_analytics(events, user_id)
            
            logger.info(f"Generated user analytics for {user_id}: {analytics['total_queries']} queries")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            return {}
    
    async def generate_daily_summary(self, date: str = None) -> DailyAnalyticsSummary:
        """Generate daily analytics summary"""
        try:
            if date is None:
                date = datetime.utcnow().strftime('%Y-%m-%d')
            
            # Get events for the day
            events = await self._get_events_by_date(date)
            
            # Calculate summary statistics
            summary = self._calculate_daily_summary(events, date)
            
            # Save summary to database
            await self._save_daily_summary(summary)
            
            logger.info(f"Generated daily summary for {date}: {summary.total_queries} queries")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            return DailyAnalyticsSummary(id="", date=date or datetime.utcnow().strftime('%Y-%m-%d'))
    
    async def get_performance_insights(
        self,
        time_period: str = "7d"
    ) -> Dict[str, Any]:
        """Get performance insights and recommendations"""
        try:
            events = await self._get_events_by_period(time_period)
            
            insights = {
                'total_queries': len([e for e in events if e.event_type == EventType.QUERY_RECEIVED]),
                'avg_response_time': 0,
                'error_rate': 0,
                'personality_performance': {},
                'peak_usage_hours': [],
                'recommendations': []
            }
            
            if not events:
                return insights
            
            # Calculate response times
            response_times = [e.response_time_ms for e in events if e.response_time_ms]
            if response_times:
                insights['avg_response_time'] = sum(response_times) / len(response_times)
            
            # Calculate error rate
            error_events = [e for e in events if e.event_type == EventType.ERROR_OCCURRED]
            total_events = len(events)
            if total_events > 0:
                insights['error_rate'] = len(error_events) / total_events * 100
            
            # Personality performance
            personality_events = defaultdict(list)
            for event in events:
                if event.personality_id:
                    personality_events[event.personality_id].append(event)
            
            for personality, p_events in personality_events.items():
                p_response_times = [e.response_time_ms for e in p_events if e.response_time_ms]
                insights['personality_performance'][personality] = {
                    'total_queries': len([e for e in p_events if e.event_type == EventType.QUERY_RECEIVED]),
                    'avg_response_time': sum(p_response_times) / len(p_response_times) if p_response_times else 0,
                    'error_count': len([e for e in p_events if e.event_type == EventType.ERROR_OCCURRED])
                }
            
            # Generate recommendations
            insights['recommendations'] = self._generate_performance_recommendations(insights)
            
            logger.info(f"Generated performance insights for {time_period}")
            return insights
            
        except Exception as e:
            logger.error(f"Error getting performance insights: {e}")
            return {}
    
    # Private helper methods
    
    def _determine_response_quality(
        self,
        response: str,
        response_time_ms: int,
        citations: List[str] = None
    ) -> str:
        """Determine response quality based on various factors"""
        score = 0
        
        # Response length factor
        if len(response) > 100:
            score += 1
        if len(response) > 300:
            score += 1
        
        # Response time factor
        if response_time_ms < 3000:  # Under 3 seconds
            score += 2
        elif response_time_ms < 5000:  # Under 5 seconds
            score += 1
        
        # Citations factor
        if citations and len(citations) > 0:
            score += 2
        
        # Content quality indicators
        quality_indicators = ['wisdom', 'guidance', 'spiritual', 'divine', 'sacred', 'truth']
        if any(indicator in response.lower() for indicator in quality_indicators):
            score += 1
        
        # Determine quality level
        if score >= 5:
            return 'high'
        elif score >= 3:
            return 'medium'
        else:
            return 'low'
    
    async def _save_event_to_db(self, event: UserAnalyticsEvent) -> bool:
        """Save analytics event to database"""
        try:
            if hasattr(self.db_service, 'save_analytics_event'):
                return await self.db_service.save_analytics_event(model_to_dict(event))
        except Exception as e:
            logger.warning(f"Database unavailable, using local storage: {e}")
        
        return self._save_event_to_local(event)
    
    def _save_event_to_local(self, event: UserAnalyticsEvent) -> bool:
        """Save event to local JSON storage"""
        try:
            # Organize by date for easier querying
            event_date = event.timestamp[:10]  # YYYY-MM-DD
            date_dir = os.path.join(self.local_storage_path, event_date)
            os.makedirs(date_dir, exist_ok=True)
            
            event_file = os.path.join(date_dir, f"{event.id}.json")
            with open(event_file, 'w', encoding='utf-8') as f:
                json.dump(model_to_dict(event), f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Error saving local analytics event: {e}")
            return False
    
    async def _get_events_by_period(self, time_period: str) -> List[UserAnalyticsEvent]:
        """Get analytics events for a time period"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            
            if time_period == "1d":
                start_date = end_date - timedelta(days=1)
            elif time_period == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_period == "30d":
                start_date = end_date - timedelta(days=30)
            else:  # "all"
                start_date = end_date - timedelta(days=365)  # Last year
            
            # Try database first
            if hasattr(self.db_service, 'get_analytics_events_by_period'):
                events_data = await self.db_service.get_analytics_events_by_period(
                    start_date.isoformat(), end_date.isoformat()
                )
                return [dict_to_model(data, UserAnalyticsEvent) for data in events_data]
        
        except Exception as e:
            logger.warning(f"Database unavailable, using local storage: {e}")
        
        return self._get_events_by_period_local(start_date, end_date)
    
    def _get_events_by_period_local(self, start_date: datetime, end_date: datetime) -> List[UserAnalyticsEvent]:
        """Get events from local storage for a time period"""
        try:
            events = []
            current_date = start_date
            
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                date_dir = os.path.join(self.local_storage_path, date_str)
                
                if os.path.exists(date_dir):
                    for filename in os.listdir(date_dir):
                        if filename.endswith('.json'):
                            event_path = os.path.join(date_dir, filename)
                            try:
                                with open(event_path, 'r', encoding='utf-8') as f:
                                    event_data = json.load(f)
                                events.append(dict_to_model(event_data, UserAnalyticsEvent))
                            except Exception:
                                continue
                
                current_date += timedelta(days=1)
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting local events: {e}")
            return []
    
    def _calculate_personality_stats(self, events: List[UserAnalyticsEvent]) -> Dict[str, PersonalityUsageStats]:
        """Calculate personality usage statistics from events"""
        personality_stats = {}
        personality_data = defaultdict(lambda: {
            'queries': 0,
            'users': set(),
            'response_times': [],
            'costs': [],
            'tokens': []
        })
        
        for event in events:
            if event.personality_id and event.event_type == EventType.QUERY_RECEIVED:
                data = personality_data[event.personality_id]
                data['queries'] += 1
                data['users'].add(event.user_id)
                
                if event.response_time_ms:
                    data['response_times'].append(event.response_time_ms)
                if event.cost_usd:
                    data['costs'].append(event.cost_usd)
                if event.tokens_used:
                    data['tokens'].append(event.tokens_used)
        
        # Calculate final stats
        for personality_id, data in personality_data.items():
            stats = PersonalityUsageStats(
                personality_id=personality_id,
                total_queries=data['queries'],
                total_users=len(data['users']),
                avg_response_time_ms=sum(data['response_times']) / len(data['response_times']) if data['response_times'] else 0,
                success_rate=100.0,  # Can be calculated from error events
                total_tokens_used=sum(data['tokens']),
                total_cost_usd=sum(data['costs']),
                last_updated=datetime.utcnow().isoformat()
            )
            personality_stats[personality_id] = stats
        
        return personality_stats
    
    async def _update_real_time_stats(self, event: UserAnalyticsEvent):
        """Update real-time statistics caches"""
        try:
            # Update personality stats cache
            if event.personality_id:
                cache_key = f"realtime_personality:{event.personality_id}"
                current_stats = self.cache_service.get(cache_key) or {
                    'queries_today': 0,
                    'avg_response_time': 0,
                    'last_query': None
                }
                
                if event.event_type == EventType.QUERY_RECEIVED:
                    current_stats['queries_today'] += 1
                    current_stats['last_query'] = event.timestamp
                    
                    if event.response_time_ms:
                        # Update running average
                        current_avg = current_stats['avg_response_time']
                        query_count = current_stats['queries_today']
                        new_avg = ((current_avg * (query_count - 1)) + event.response_time_ms) / query_count
                        current_stats['avg_response_time'] = new_avg
                
                self.cache_service.put(cache_key, current_stats, ttl=86400)  # 24 hours
        
        except Exception as e:
            logger.warning(f"Error updating real-time stats: {e}")
    
    def _generate_performance_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations based on insights"""
        recommendations = []
        
        # Response time recommendations
        if insights['avg_response_time'] > 5000:
            recommendations.append("Consider optimizing response generation - average response time is over 5 seconds")
        
        # Error rate recommendations
        if insights['error_rate'] > 5:
            recommendations.append("High error rate detected - investigate and fix common failure points")
        
        # Personality performance recommendations
        for personality, perf in insights['personality_performance'].items():
            if perf['avg_response_time'] > 6000:
                recommendations.append(f"{personality} personality has slow response times - may need optimization")
            if perf['error_count'] > 10:
                recommendations.append(f"{personality} personality has high error count - check configuration")
        
        return recommendations

# Global service instance
analytics_service = AnalyticsService()
