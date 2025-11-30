"""
Memory Analytics Service for Vimarsh

This service provides analytics and insights on user memory patterns,
helping understand engagement, emotional journeys, and growth over time.

Phase 4.8 Implementation
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from collections import Counter

from models.memory_models import (
    MemoryProfile,
    RelationshipState,
    SessionSummary,
    RelationshipDepth
)
from services.hierarchical_memory_service import get_memory_service

logger = logging.getLogger(__name__)


class MemoryAnalyticsService:
    """
    Service for analyzing user memory patterns and generating insights.
    
    Provides:
    - Engagement analytics
    - Emotional journey analysis
    - Topic preference patterns
    - Growth trajectory insights
    - Relationship strength metrics
    """
    
    def __init__(self):
        """Initialize the analytics service."""
        self.memory_service = get_memory_service()
        logger.info("📊 MemoryAnalyticsService initialized")
    
    async def get_user_analytics(
        self,
        user_id: str,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analytics for a user.
        
        Args:
            user_id: The user's unique identifier
            time_range_days: Number of days to analyze
            
        Returns:
            Dict with various analytics categories
        """
        analytics = {
            "generated_at": datetime.utcnow().isoformat(),
            "time_range_days": time_range_days,
            "engagement": {},
            "emotional_patterns": {},
            "topic_preferences": {},
            "relationship_insights": {},
            "growth_trajectory": {},
            "recommendations": []
        }
        
        try:
            # Get user data
            profile = await self.memory_service.get_or_create_memory_profile(user_id)
            relationships = await self.memory_service.get_all_relationships(user_id)
            
            # Gather all sessions within time range
            all_sessions: List[SessionSummary] = []
            for relationship in relationships:
                sessions = await self.memory_service.get_recent_sessions(
                    user_id, relationship.personality_id, limit=50
                )
                all_sessions.extend(sessions)
            
            # Filter by time range
            cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
            recent_sessions = [s for s in all_sessions if s.start_time >= cutoff_date]
            
            # Generate analytics
            analytics["engagement"] = self._analyze_engagement(
                profile, relationships, recent_sessions
            )
            analytics["emotional_patterns"] = self._analyze_emotions(recent_sessions)
            analytics["topic_preferences"] = self._analyze_topics(
                recent_sessions, relationships
            )
            analytics["relationship_insights"] = self._analyze_relationships(relationships)
            analytics["growth_trajectory"] = self._analyze_growth(
                profile, relationships, recent_sessions
            )
            analytics["recommendations"] = self._generate_recommendations(analytics)
            
            logger.info(f"📊 Generated analytics for user {user_id[:8]}...")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error generating analytics: {e}")
            return analytics
    
    def _analyze_engagement(
        self,
        profile: MemoryProfile,
        relationships: List[RelationshipState],
        sessions: List[SessionSummary]
    ) -> Dict[str, Any]:
        """Analyze user engagement patterns."""
        if not sessions:
            return {
                "total_sessions": 0,
                "average_session_duration": 0,
                "sessions_per_week": 0,
                "most_active_day": None,
                "engagement_trend": "insufficient_data"
            }
        
        total_duration = sum(s.duration_minutes for s in sessions if s.duration_minutes)
        avg_duration = total_duration / len(sessions) if sessions else 0
        
        # Calculate sessions per week
        if sessions:
            date_range = (
                max(s.start_time for s in sessions) - 
                min(s.start_time for s in sessions)
            ).days + 1
            weeks = max(date_range / 7, 1)
            sessions_per_week = len(sessions) / weeks
        else:
            sessions_per_week = 0
        
        # Find most active day
        day_counts: Dict[str, int] = {}
        for session in sessions:
            day = session.start_time.strftime("%A")
            day_counts[day] = day_counts.get(day, 0) + 1
        
        most_active_day = max(day_counts.items(), key=lambda x: x[1])[0] if day_counts else None
        
        # Analyze engagement trend
        trend = self._calculate_engagement_trend(sessions)
        
        return {
            "total_sessions": len(sessions),
            "total_duration_minutes": total_duration,
            "average_session_duration": round(avg_duration, 1),
            "sessions_per_week": round(sessions_per_week, 1),
            "most_active_day": most_active_day,
            "day_distribution": day_counts,
            "engagement_trend": trend,
            "total_messages": sum(s.message_count for s in sessions if s.message_count)
        }
    
    def _calculate_engagement_trend(
        self,
        sessions: List[SessionSummary]
    ) -> str:
        """Calculate if engagement is increasing, stable, or decreasing."""
        if len(sessions) < 4:
            return "insufficient_data"
        
        # Sort by date
        sorted_sessions = sorted(sessions, key=lambda s: s.start_time)
        
        # Split into halves
        midpoint = len(sorted_sessions) // 2
        first_half = sorted_sessions[:midpoint]
        second_half = sorted_sessions[midpoint:]
        
        # Compare average frequency
        first_half_per_day = len(first_half) / max(
            (first_half[-1].start_time - first_half[0].start_time).days, 1
        ) if len(first_half) > 1 else 0
        
        second_half_per_day = len(second_half) / max(
            (second_half[-1].start_time - second_half[0].start_time).days, 1
        ) if len(second_half) > 1 else 0
        
        if second_half_per_day > first_half_per_day * 1.2:
            return "increasing"
        elif second_half_per_day < first_half_per_day * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_emotions(
        self,
        sessions: List[SessionSummary]
    ) -> Dict[str, Any]:
        """Analyze emotional patterns across sessions."""
        if not sessions:
            return {
                "dominant_emotions": [],
                "positive_ratio": 0,
                "emotional_growth": "insufficient_data"
            }
        
        starting_emotions: List[str] = []
        ending_emotions: List[str] = []
        all_emotions: List[str] = []
        
        positive_emotions = {"peaceful", "hopeful", "grateful", "inspired", "joyful", "content"}
        challenging_emotions = {"troubled", "confused", "anxious", "uncertain", "sad", "angry"}
        
        for session in sessions:
            if session.starting_emotion:
                starting_emotions.append(session.starting_emotion.lower())
                all_emotions.append(session.starting_emotion.lower())
            if session.ending_emotion:
                ending_emotions.append(session.ending_emotion.lower())
                all_emotions.append(session.ending_emotion.lower())
            
            # Include emotions from arc
            if session.emotional_arc:
                for arc_point in session.emotional_arc:
                    if tone := arc_point.get("tone"):
                        all_emotions.append(tone.lower())
        
        # Count occurrences
        emotion_counts = Counter(all_emotions)
        dominant = emotion_counts.most_common(5)
        
        # Calculate positive transformation ratio
        transformations = 0
        positive_transformations = 0
        for session in sessions:
            if session.starting_emotion and session.ending_emotion:
                transformations += 1
                start_lower = session.starting_emotion.lower()
                end_lower = session.ending_emotion.lower()
                if start_lower in challenging_emotions and end_lower in positive_emotions:
                    positive_transformations += 1
        
        transformation_ratio = (
            positive_transformations / transformations 
            if transformations > 0 else 0
        )
        
        # Calculate overall positive emotion ratio
        positive_count = sum(
            1 for e in all_emotions if e in positive_emotions
        )
        positive_ratio = positive_count / len(all_emotions) if all_emotions else 0
        
        return {
            "dominant_emotions": [e[0] for e in dominant],
            "emotion_distribution": dict(dominant),
            "positive_ratio": round(positive_ratio, 2),
            "transformation_ratio": round(transformation_ratio, 2),
            "total_transformations": transformations,
            "positive_transformations": positive_transformations,
            "emotional_growth": self._assess_emotional_growth(
                starting_emotions, ending_emotions
            )
        }
    
    def _assess_emotional_growth(
        self,
        starting: List[str],
        ending: List[str]
    ) -> str:
        """Assess emotional growth pattern."""
        if len(starting) < 3 or len(ending) < 3:
            return "insufficient_data"
        
        positive = {"peaceful", "hopeful", "grateful", "inspired"}
        
        start_positive = sum(1 for e in starting if e in positive)
        end_positive = sum(1 for e in ending if e in positive)
        
        if end_positive > start_positive * 1.3:
            return "positive_growth"
        elif end_positive < start_positive * 0.7:
            return "needs_attention"
        else:
            return "stable"
    
    def _analyze_topics(
        self,
        sessions: List[SessionSummary],
        relationships: List[RelationshipState]
    ) -> Dict[str, Any]:
        """Analyze topic preferences and patterns."""
        all_topics: List[str] = []
        
        for session in sessions:
            all_topics.extend(session.topics or [])
        
        for relationship in relationships:
            all_topics.extend(relationship.key_themes)
        
        topic_counts = Counter(all_topics)
        top_topics = topic_counts.most_common(10)
        
        # Analyze topic diversity
        unique_topics = len(set(all_topics))
        topic_diversity = unique_topics / len(all_topics) if all_topics else 0
        
        return {
            "top_topics": [t[0] for t in top_topics],
            "topic_distribution": dict(top_topics),
            "unique_topics": unique_topics,
            "total_topic_mentions": len(all_topics),
            "topic_diversity": round(topic_diversity, 2),
            "diversity_assessment": (
                "highly_diverse" if topic_diversity > 0.5 else
                "moderately_diverse" if topic_diversity > 0.3 else
                "focused"
            )
        }
    
    def _analyze_relationships(
        self,
        relationships: List[RelationshipState]
    ) -> Dict[str, Any]:
        """Analyze relationship patterns across personalities."""
        if not relationships:
            return {
                "total_personalities": 0,
                "strongest_bond": None,
                "deepest_relationship": None
            }
        
        # Find strongest bond (most interactions)
        strongest = max(
            relationships,
            key=lambda r: r.interaction_count
        )
        
        # Find deepest relationship
        deepest = max(
            relationships,
            key=lambda r: r.depth_level.value
        )
        
        # Personality engagement distribution
        engagement_dist = {
            r.personality_id: r.interaction_count 
            for r in relationships
        }
        
        # Average trust and engagement scores
        avg_trust = sum(r.trust_score for r in relationships) / len(relationships)
        avg_engagement = sum(r.engagement_score for r in relationships) / len(relationships)
        
        # Depth distribution
        depth_counts: Dict[str, int] = {}
        for r in relationships:
            depth_name = r.depth_level.name
            depth_counts[depth_name] = depth_counts.get(depth_name, 0) + 1
        
        return {
            "total_personalities": len(relationships),
            "strongest_bond": {
                "personality": strongest.personality_id,
                "interactions": strongest.interaction_count,
                "duration_hours": round(strongest.total_duration_minutes / 60, 1)
            },
            "deepest_relationship": {
                "personality": deepest.personality_id,
                "depth": deepest.depth_level.name
            },
            "engagement_distribution": engagement_dist,
            "depth_distribution": depth_counts,
            "average_trust_score": round(avg_trust, 2),
            "average_engagement_score": round(avg_engagement, 2),
            "total_milestones": sum(len(r.milestones) for r in relationships)
        }
    
    def _analyze_growth(
        self,
        profile: MemoryProfile,
        relationships: List[RelationshipState],
        sessions: List[SessionSummary]
    ) -> Dict[str, Any]:
        """Analyze overall growth trajectory."""
        growth = {
            "journey_start": None,
            "total_journey_days": 0,
            "milestones_achieved": 0,
            "depth_progression": [],
            "key_insights_count": 0,
            "growth_indicators": []
        }
        
        # Find journey start
        first_interaction = None
        for r in relationships:
            if r.first_interaction:
                if first_interaction is None or r.first_interaction < first_interaction:
                    first_interaction = r.first_interaction
        
        if first_interaction:
            growth["journey_start"] = first_interaction.isoformat()
            growth["total_journey_days"] = (datetime.utcnow() - first_interaction).days
        
        # Count milestones
        growth["milestones_achieved"] = sum(len(r.milestones) for r in relationships)
        
        # Count key insights
        growth["key_insights_count"] = sum(
            len(s.key_insights) for s in sessions if s.key_insights
        )
        
        # Track depth progression
        for r in relationships:
            if r.depth_level.value >= RelationshipDepth.FAMILIAR.value:
                growth["depth_progression"].append({
                    "personality": r.personality_id,
                    "depth": r.depth_level.name,
                    "interactions": r.interaction_count
                })
        
        # Identify growth indicators
        if profile.total_sessions > 10:
            growth["growth_indicators"].append("Dedicated seeker (10+ sessions)")
        
        if len(relationships) >= 3:
            growth["growth_indicators"].append("Multi-perspective explorer (3+ guides)")
        
        deep_relationships = [
            r for r in relationships 
            if r.depth_level.value >= RelationshipDepth.TRUSTED.value
        ]
        if deep_relationships:
            growth["growth_indicators"].append(f"Deep bonds formed ({len(deep_relationships)} trusted)")
        
        return growth
    
    def _generate_recommendations(
        self,
        analytics: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate personalized recommendations based on analytics."""
        recommendations = []
        
        # Engagement recommendations
        engagement = analytics.get("engagement", {})
        if engagement.get("engagement_trend") == "decreasing":
            recommendations.append({
                "type": "engagement",
                "message": "Your visit frequency has decreased. Consider setting a regular time for reflection.",
                "priority": "medium"
            })
        
        if engagement.get("average_session_duration", 0) < 5:
            recommendations.append({
                "type": "engagement",
                "message": "Your sessions are quite brief. Longer conversations often yield deeper insights.",
                "priority": "low"
            })
        
        # Emotional recommendations
        emotions = analytics.get("emotional_patterns", {})
        if emotions.get("emotional_growth") == "needs_attention":
            recommendations.append({
                "type": "emotional",
                "message": "Your emotional patterns suggest you might benefit from exploring stress management topics.",
                "priority": "high"
            })
        
        if emotions.get("transformation_ratio", 0) > 0.6:
            recommendations.append({
                "type": "emotional",
                "message": "Your conversations often lead to positive emotional shifts. You're making great progress!",
                "priority": "celebration"
            })
        
        # Topic recommendations
        topics = analytics.get("topic_preferences", {})
        if topics.get("diversity_assessment") == "focused":
            recommendations.append({
                "type": "exploration",
                "message": "You tend to focus on specific topics. Consider exploring new areas for fresh perspectives.",
                "priority": "low"
            })
        
        # Relationship recommendations
        relationships = analytics.get("relationship_insights", {})
        if relationships.get("total_personalities", 0) == 1:
            recommendations.append({
                "type": "exploration",
                "message": "You've been consulting with one guide. Other personalities offer different wisdom traditions.",
                "priority": "medium"
            })
        
        return recommendations
    
    async def get_personality_comparison(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Compare user's engagement across different personalities.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            Comparative analysis across personalities
        """
        comparison = {
            "personalities": [],
            "summary": {}
        }
        
        try:
            relationships = await self.memory_service.get_all_relationships(user_id)
            
            for relationship in relationships:
                sessions = await self.memory_service.get_recent_sessions(
                    user_id, relationship.personality_id, limit=20
                )
                
                personality_data = {
                    "personality_id": relationship.personality_id,
                    "depth": relationship.depth_level.name,
                    "interactions": relationship.interaction_count,
                    "total_minutes": relationship.total_duration_minutes,
                    "key_themes": relationship.key_themes[:5],
                    "trust_score": relationship.trust_score,
                    "milestones": len(relationship.milestones),
                    "avg_session_duration": (
                        sum(s.duration_minutes for s in sessions if s.duration_minutes) /
                        len(sessions) if sessions else 0
                    )
                }
                
                comparison["personalities"].append(personality_data)
            
            # Generate summary
            if comparison["personalities"]:
                total_interactions = sum(
                    p["interactions"] for p in comparison["personalities"]
                )
                comparison["summary"] = {
                    "total_personalities": len(comparison["personalities"]),
                    "total_interactions": total_interactions,
                    "most_consulted": max(
                        comparison["personalities"],
                        key=lambda p: p["interactions"]
                    )["personality_id"],
                    "deepest_bond": max(
                        comparison["personalities"],
                        key=lambda p: RelationshipDepth[p["depth"]].value
                    )["personality_id"]
                }
            
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Error generating personality comparison: {e}")
            return comparison
    
    async def get_time_series_data(
        self,
        user_id: str,
        days: int = 30,
        granularity: str = "day"
    ) -> Dict[str, Any]:
        """
        Get time series data for visualization.
        
        Args:
            user_id: The user's unique identifier
            days: Number of days to include
            granularity: "day" or "week"
            
        Returns:
            Time series data for charts
        """
        time_series = {
            "sessions_over_time": [],
            "duration_over_time": [],
            "emotions_over_time": []
        }
        
        try:
            relationships = await self.memory_service.get_all_relationships(user_id)
            
            # Gather all sessions
            all_sessions: List[SessionSummary] = []
            for relationship in relationships:
                sessions = await self.memory_service.get_recent_sessions(
                    user_id, relationship.personality_id, limit=100
                )
                all_sessions.extend(sessions)
            
            # Filter by date range
            cutoff = datetime.utcnow() - timedelta(days=days)
            filtered = [s for s in all_sessions if s.start_time >= cutoff]
            
            # Group by date
            by_date: Dict[str, List[SessionSummary]] = {}
            for session in filtered:
                if granularity == "week":
                    date_key = session.start_time.strftime("%Y-W%W")
                else:
                    date_key = session.start_time.strftime("%Y-%m-%d")
                
                if date_key not in by_date:
                    by_date[date_key] = []
                by_date[date_key].append(session)
            
            # Build time series
            for date_key in sorted(by_date.keys()):
                sessions = by_date[date_key]
                
                time_series["sessions_over_time"].append({
                    "date": date_key,
                    "count": len(sessions)
                })
                
                time_series["duration_over_time"].append({
                    "date": date_key,
                    "total_minutes": sum(
                        s.duration_minutes for s in sessions if s.duration_minutes
                    )
                })
                
                # Track emotions
                emotions_in_period: List[str] = []
                for s in sessions:
                    if s.ending_emotion:
                        emotions_in_period.append(s.ending_emotion)
                
                if emotions_in_period:
                    emotion_counts = Counter(emotions_in_period)
                    dominant = emotion_counts.most_common(1)[0][0]
                    time_series["emotions_over_time"].append({
                        "date": date_key,
                        "dominant_emotion": dominant
                    })
            
            return time_series
            
        except Exception as e:
            logger.error(f"❌ Error generating time series: {e}")
            return time_series


# Singleton instance
_analytics_service_instance: Optional[MemoryAnalyticsService] = None


def get_analytics_service() -> MemoryAnalyticsService:
    """Get or create the singleton analytics service instance."""
    global _analytics_service_instance
    if _analytics_service_instance is None:
        _analytics_service_instance = MemoryAnalyticsService()
    return _analytics_service_instance
