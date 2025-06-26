"""
Vimarsh User Feedback Collection and Analytics System
Comprehensive feedback collection, analysis, and continuous improvement processes
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import os

# Analytics and ML imports
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.sentiment import SentimentAnalyzer
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    logging.warning("Analytics libraries not available - using basic feedback processing")

class FeedbackType(Enum):
    """Types of feedback that can be collected"""
    RATING = "rating"
    TEXT_FEEDBACK = "text_feedback"
    VOICE_FEEDBACK = "voice_feedback"
    SPIRITUAL_ACCURACY = "spiritual_accuracy"
    USER_EXPERIENCE = "user_experience"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    CONTENT_SUGGESTION = "content_suggestion"

class FeedbackSentiment(Enum):
    """Sentiment analysis results"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class FeedbackPriority(Enum):
    """Priority levels for feedback processing"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class UserFeedback:
    """Individual user feedback item"""
    feedback_id: str
    user_id: str
    session_id: str
    feedback_type: FeedbackType
    timestamp: datetime
    rating: Optional[int]  # 1-5 scale
    text_content: Optional[str]
    voice_transcript: Optional[str]
    context: Dict[str, Any]  # Query, response, etc.
    sentiment: Optional[FeedbackSentiment]
    priority: FeedbackPriority
    spiritual_context: Dict[str, Any]
    processed: bool = False
    response_generated: bool = False

@dataclass
class FeedbackAnalytics:
    """Analytics results for feedback collection"""
    total_feedback_count: int
    average_rating: float
    sentiment_distribution: Dict[str, int]
    common_themes: List[str]
    improvement_suggestions: List[str]
    spiritual_accuracy_score: float
    user_satisfaction_trend: List[float]
    feature_requests: Dict[str, int]

@dataclass
class ContinuousImprovementMetrics:
    """Metrics for continuous improvement tracking"""
    response_quality_trend: List[float]
    user_engagement_metrics: Dict[str, float]
    spiritual_content_accuracy: float
    feature_adoption_rates: Dict[str, float]
    performance_improvements: Dict[str, Any]
    cost_optimization_impact: Dict[str, float]
    user_retention_metrics: Dict[str, float]

class VimarshFeedbackCollector:
    """
    Comprehensive feedback collection and analysis system
    """
    
    def __init__(self, 
                 feedback_storage_path: str = "logs/feedback",
                 analytics_enabled: bool = True,
                 spiritual_validation: bool = True):
        self.feedback_storage_path = feedback_storage_path
        self.analytics_enabled = analytics_enabled and ANALYTICS_AVAILABLE
        self.spiritual_validation = spiritual_validation
        self.logger = logging.getLogger(__name__)
        
        # Initialize feedback storage
        os.makedirs(feedback_storage_path, exist_ok=True)
        
        # Feedback processing queue
        self.feedback_queue = []
        self.processed_feedback = []
        
        # Analytics components
        if self.analytics_enabled:
            self.sentiment_analyzer = self._initialize_sentiment_analyzer()
            self.theme_extractor = TfidfVectorizer(max_features=100, stop_words='english')
        
        # Spiritual guidance for feedback
        self.spiritual_feedback_principles = {
            'gratitude': 'Approach feedback with gratitude, as each comment is a gift for improvement',
            'dharmic_response': 'Respond to feedback with dharmic principles of truth and compassion',
            'learning_mindset': 'Every feedback is an opportunity for spiritual and technical growth',
            'service_orientation': 'Use feedback to better serve the spiritual needs of users'
        }

    def _initialize_sentiment_analyzer(self):
        """Initialize sentiment analysis components"""
        if not ANALYTICS_AVAILABLE:
            return None
        
        # Simple rule-based sentiment for spiritual content
        return {
            'positive_words': ['helpful', 'insightful', 'peaceful', 'wise', 'enlightening', 'blessed'],
            'negative_words': ['confusing', 'wrong', 'unhelpful', 'inappropriate', 'offensive'],
            'spiritual_positive': ['dharmic', 'divine', 'sacred', 'spiritual', 'meaningful'],
            'spiritual_negative': ['unspiritual', 'inappropriate', 'disrespectful']
        }

    async def collect_feedback(self, 
                             user_id: str,
                             session_id: str,
                             feedback_type: FeedbackType,
                             rating: Optional[int] = None,
                             text_content: Optional[str] = None,
                             voice_transcript: Optional[str] = None,
                             context: Optional[Dict[str, Any]] = None) -> str:
        """Collect user feedback with comprehensive context"""
        
        feedback_id = str(uuid.uuid4())
        
        # Analyze sentiment if text content provided
        sentiment = None
        if text_content and self.analytics_enabled:
            sentiment = self._analyze_sentiment(text_content)
        
        # Determine priority based on content and type
        priority = self._determine_priority(feedback_type, rating, text_content)
        
        # Extract spiritual context
        spiritual_context = self._extract_spiritual_context(text_content, context or {})
        
        feedback = UserFeedback(
            feedback_id=feedback_id,
            user_id=user_id,
            session_id=session_id,
            feedback_type=feedback_type,
            timestamp=datetime.now(),
            rating=rating,
            text_content=text_content,
            voice_transcript=voice_transcript,
            context=context or {},
            sentiment=sentiment,
            priority=priority,
            spiritual_context=spiritual_context
        )
        
        # Add to processing queue
        self.feedback_queue.append(feedback)
        
        # Process immediately if high priority
        if priority in [FeedbackPriority.CRITICAL, FeedbackPriority.HIGH]:
            await self._process_high_priority_feedback(feedback)
        
        # Store feedback
        await self._store_feedback(feedback)
        
        self.logger.info(f"Feedback collected: {feedback_id} - Type: {feedback_type.value}, Priority: {priority.value}")
        
        return feedback_id

    def _analyze_sentiment(self, text: str) -> FeedbackSentiment:
        """Analyze sentiment of feedback text"""
        if not self.sentiment_analyzer:
            return FeedbackSentiment.NEUTRAL
        
        text_lower = text.lower()
        positive_score = 0
        negative_score = 0
        
        # Count positive indicators
        for word in self.sentiment_analyzer['positive_words']:
            positive_score += text_lower.count(word)
        for word in self.sentiment_analyzer['spiritual_positive']:
            positive_score += text_lower.count(word) * 2  # Weight spiritual terms higher
        
        # Count negative indicators
        for word in self.sentiment_analyzer['negative_words']:
            negative_score += text_lower.count(word)
        for word in self.sentiment_analyzer['spiritual_negative']:
            negative_score += text_lower.count(word) * 2
        
        # Determine sentiment
        net_score = positive_score - negative_score
        if net_score >= 2:
            return FeedbackSentiment.VERY_POSITIVE
        elif net_score >= 1:
            return FeedbackSentiment.POSITIVE
        elif net_score <= -2:
            return FeedbackSentiment.VERY_NEGATIVE
        elif net_score <= -1:
            return FeedbackSentiment.NEGATIVE
        else:
            return FeedbackSentiment.NEUTRAL

    def _determine_priority(self, 
                          feedback_type: FeedbackType, 
                          rating: Optional[int], 
                          text_content: Optional[str]) -> FeedbackPriority:
        """Determine feedback priority based on type and content"""
        
        # Critical priorities
        if feedback_type == FeedbackType.BUG_REPORT:
            return FeedbackPriority.CRITICAL
        
        if rating is not None and rating <= 2:
            return FeedbackPriority.HIGH
        
        if text_content:
            critical_keywords = ['bug', 'error', 'crash', 'broken', 'inappropriate', 'offensive']
            if any(keyword in text_content.lower() for keyword in critical_keywords):
                return FeedbackPriority.CRITICAL
            
            high_keywords = ['problem', 'issue', 'wrong', 'incorrect', 'unhelpful']
            if any(keyword in text_content.lower() for keyword in high_keywords):
                return FeedbackPriority.HIGH
        
        # Spiritual accuracy feedback is high priority
        if feedback_type == FeedbackType.SPIRITUAL_ACCURACY:
            return FeedbackPriority.HIGH
        
        # Feature requests are medium priority
        if feedback_type == FeedbackType.FEATURE_REQUEST:
            return FeedbackPriority.MEDIUM
        
        return FeedbackPriority.LOW

    def _extract_spiritual_context(self, text_content: Optional[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract spiritual context and themes from feedback"""
        
        spiritual_context = {
            'contains_spiritual_terms': False,
            'spiritual_accuracy_concern': False,
            'dharmic_feedback': False,
            'sanskrit_terms_mentioned': False,
            'scripture_references': [],
            'spiritual_satisfaction': None
        }
        
        if not text_content:
            return spiritual_context
        
        text_lower = text_content.lower()
        
        # Check for spiritual terms
        spiritual_terms = ['dharma', 'karma', 'moksha', 'bhakti', 'krishna', 'arjuna', 'gita', 'spiritual', 'divine']
        spiritual_context['contains_spiritual_terms'] = any(term in text_lower for term in spiritual_terms)
        
        # Check for Sanskrit terms
        sanskrit_terms = ['om', 'namaste', 'guru', 'yoga', 'meditation', 'mantra', 'chakra']
        spiritual_context['sanskrit_terms_mentioned'] = any(term in text_lower for term in sanskrit_terms)
        
        # Check for accuracy concerns
        accuracy_keywords = ['wrong', 'incorrect', 'inaccurate', 'not authentic', 'inappropriate']
        spiritual_context['spiritual_accuracy_concern'] = any(keyword in text_lower for keyword in accuracy_keywords)
        
        # Check for dharmic feedback approach
        dharmic_keywords = ['respectful', 'grateful', 'blessed', 'thankful', 'humble']
        spiritual_context['dharmic_feedback'] = any(keyword in text_lower for keyword in dharmic_keywords)
        
        # Extract scripture references
        scriptures = ['bhagavad gita', 'mahabharata', 'bhagavatam', 'upanishads']
        spiritual_context['scripture_references'] = [s for s in scriptures if s in text_lower]
        
        return spiritual_context

    async def _process_high_priority_feedback(self, feedback: UserFeedback):
        """Process high-priority feedback immediately"""
        
        if feedback.priority == FeedbackPriority.CRITICAL:
            await self._handle_critical_feedback(feedback)
        elif feedback.priority == FeedbackPriority.HIGH:
            await self._handle_high_priority_feedback(feedback)

    async def _handle_critical_feedback(self, feedback: UserFeedback):
        """Handle critical feedback (bugs, inappropriate content)"""
        
        self.logger.critical(f"Critical feedback received: {feedback.feedback_id}")
        
        # Immediate notifications
        await self._send_critical_alert(feedback)
        
        # If spiritual accuracy issue, flag for expert review
        if (feedback.feedback_type == FeedbackType.SPIRITUAL_ACCURACY or 
            feedback.spiritual_context.get('spiritual_accuracy_concern')):
            await self._flag_for_expert_review(feedback)

    async def _handle_high_priority_feedback(self, feedback: UserFeedback):
        """Handle high-priority feedback"""
        
        self.logger.warning(f"High priority feedback received: {feedback.feedback_id}")
        
        # Queue for rapid response
        await self._queue_for_rapid_response(feedback)

    async def _store_feedback(self, feedback: UserFeedback):
        """Store feedback to persistent storage"""
        
        # Daily feedback file
        date_str = feedback.timestamp.strftime("%Y%m%d")
        feedback_file = os.path.join(self.feedback_storage_path, f"feedback_{date_str}.json")
        
        # Load existing feedback for the day
        daily_feedback = []
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r') as f:
                    daily_feedback = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading feedback file: {e}")
        
        # Add new feedback
        daily_feedback.append(asdict(feedback))
        
        # Save updated feedback
        try:
            with open(feedback_file, 'w') as f:
                json.dump(daily_feedback, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving feedback: {e}")

    async def analyze_feedback_trends(self, days: int = 30) -> FeedbackAnalytics:
        """Analyze feedback trends over specified period"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        all_feedback = await self._load_feedback_range(start_date, end_date)
        
        if not all_feedback:
            return FeedbackAnalytics(
                total_feedback_count=0,
                average_rating=0.0,
                sentiment_distribution={},
                common_themes=[],
                improvement_suggestions=[],
                spiritual_accuracy_score=0.0,
                user_satisfaction_trend=[],
                feature_requests={}
            )
        
        # Calculate analytics
        total_count = len(all_feedback)
        
        # Average rating
        ratings = [f.rating for f in all_feedback if f.rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Sentiment distribution
        sentiment_dist = {}
        for feedback in all_feedback:
            if feedback.sentiment:
                sentiment = feedback.sentiment.value
                sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1
        
        # Extract common themes
        common_themes = await self._extract_common_themes(all_feedback)
        
        # Generate improvement suggestions
        improvement_suggestions = await self._generate_improvement_suggestions(all_feedback)
        
        # Spiritual accuracy score
        spiritual_accuracy = self._calculate_spiritual_accuracy_score(all_feedback)
        
        # User satisfaction trend
        satisfaction_trend = self._calculate_satisfaction_trend(all_feedback, days)
        
        # Feature requests
        feature_requests = self._analyze_feature_requests(all_feedback)
        
        return FeedbackAnalytics(
            total_feedback_count=total_count,
            average_rating=avg_rating,
            sentiment_distribution=sentiment_dist,
            common_themes=common_themes,
            improvement_suggestions=improvement_suggestions,
            spiritual_accuracy_score=spiritual_accuracy,
            user_satisfaction_trend=satisfaction_trend,
            feature_requests=feature_requests
        )

    async def _load_feedback_range(self, start_date: datetime, end_date: datetime) -> List[UserFeedback]:
        """Load feedback from date range"""
        
        all_feedback = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y%m%d")
            feedback_file = os.path.join(self.feedback_storage_path, f"feedback_{date_str}.json")
            
            if os.path.exists(feedback_file):
                try:
                    with open(feedback_file, 'r') as f:
                        daily_feedback = json.load(f)
                    
                    for fb_data in daily_feedback:
                        # Convert back to UserFeedback object
                        fb_data['feedback_type'] = FeedbackType(fb_data['feedback_type'])
                        if fb_data.get('sentiment'):
                            fb_data['sentiment'] = FeedbackSentiment(fb_data['sentiment'])
                        fb_data['priority'] = FeedbackPriority(fb_data['priority'])
                        fb_data['timestamp'] = datetime.fromisoformat(fb_data['timestamp'])
                        
                        feedback = UserFeedback(**fb_data)
                        all_feedback.append(feedback)
                        
                except Exception as e:
                    self.logger.error(f"Error loading feedback from {feedback_file}: {e}")
            
            current_date += timedelta(days=1)
        
        return all_feedback

    async def _extract_common_themes(self, feedback_list: List[UserFeedback]) -> List[str]:
        """Extract common themes from feedback text"""
        
        if not self.analytics_enabled:
            return ['theme_analysis_not_available']
        
        # Collect all text content
        texts = []
        for feedback in feedback_list:
            if feedback.text_content:
                texts.append(feedback.text_content)
            if feedback.voice_transcript:
                texts.append(feedback.voice_transcript)
        
        if not texts:
            return []
        
        try:
            # Use TF-IDF to find common themes
            tfidf_matrix = self.theme_extractor.fit_transform(texts)
            feature_names = self.theme_extractor.get_feature_names_out()
            
            # Get top features (themes)
            scores = tfidf_matrix.sum(axis=0).A1
            feature_scores = list(zip(feature_names, scores))
            feature_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top 10 themes
            return [feature for feature, score in feature_scores[:10] if score > 0.1]
            
        except Exception as e:
            self.logger.error(f"Error extracting themes: {e}")
            return ['theme_extraction_error']

    async def _generate_improvement_suggestions(self, feedback_list: List[UserFeedback]) -> List[str]:
        """Generate improvement suggestions based on feedback analysis"""
        
        suggestions = []
        
        # Count common issues
        issue_counts = {}
        positive_counts = {}
        
        for feedback in feedback_list:
            if not feedback.text_content:
                continue
            
            text_lower = feedback.text_content.lower()
            
            # Check for common issues
            if 'slow' in text_lower or 'performance' in text_lower:
                issue_counts['performance'] = issue_counts.get('performance', 0) + 1
            
            if 'voice' in text_lower and ('problem' in text_lower or 'issue' in text_lower):
                issue_counts['voice_issues'] = issue_counts.get('voice_issues', 0) + 1
            
            if 'spiritual' in text_lower and ('wrong' in text_lower or 'incorrect' in text_lower):
                issue_counts['spiritual_accuracy'] = issue_counts.get('spiritual_accuracy', 0) + 1
            
            if 'confusing' in text_lower or 'unclear' in text_lower:
                issue_counts['clarity'] = issue_counts.get('clarity', 0) + 1
            
            # Check for positive aspects
            if 'helpful' in text_lower or 'useful' in text_lower:
                positive_counts['helpful'] = positive_counts.get('helpful', 0) + 1
            
            if 'accurate' in text_lower or 'correct' in text_lower:
                positive_counts['accuracy'] = positive_counts.get('accuracy', 0) + 1
        
        # Generate suggestions based on issues
        if issue_counts.get('performance', 0) >= 3:
            suggestions.append("Optimize response time and system performance")
        
        if issue_counts.get('voice_issues', 0) >= 2:
            suggestions.append("Improve voice recognition and text-to-speech quality")
        
        if issue_counts.get('spiritual_accuracy', 0) >= 2:
            suggestions.append("Enhance spiritual content accuracy validation")
        
        if issue_counts.get('clarity', 0) >= 3:
            suggestions.append("Improve response clarity and user interface design")
        
        # Add spiritual guidance suggestions
        suggestions.append("Continue dharmic approach to user feedback and improvement")
        suggestions.append("Integrate user suggestions with spiritual wisdom principles")
        
        return suggestions

    def _calculate_spiritual_accuracy_score(self, feedback_list: List[UserFeedback]) -> float:
        """Calculate spiritual accuracy score based on feedback"""
        
        spiritual_feedback = [f for f in feedback_list 
                            if f.feedback_type == FeedbackType.SPIRITUAL_ACCURACY or
                               f.spiritual_context.get('contains_spiritual_terms', False)]
        
        if not spiritual_feedback:
            return 0.85  # Default good score if no spiritual feedback
        
        positive_spiritual = 0
        total_spiritual = len(spiritual_feedback)
        
        for feedback in spiritual_feedback:
            if feedback.rating and feedback.rating >= 4:
                positive_spiritual += 1
            elif feedback.sentiment in [FeedbackSentiment.POSITIVE, FeedbackSentiment.VERY_POSITIVE]:
                positive_spiritual += 1
            elif not feedback.spiritual_context.get('spiritual_accuracy_concern', False):
                positive_spiritual += 1
        
        return positive_spiritual / total_spiritual if total_spiritual > 0 else 0.85

    def _calculate_satisfaction_trend(self, feedback_list: List[UserFeedback], days: int) -> List[float]:
        """Calculate user satisfaction trend over time"""
        
        if not feedback_list:
            return []
        
        # Group feedback by day
        daily_satisfaction = {}
        
        for feedback in feedback_list:
            date_key = feedback.timestamp.strftime("%Y-%m-%d")
            
            if date_key not in daily_satisfaction:
                daily_satisfaction[date_key] = []
            
            # Calculate satisfaction score
            satisfaction = 0.5  # Neutral default
            if feedback.rating:
                satisfaction = feedback.rating / 5.0
            elif feedback.sentiment == FeedbackSentiment.VERY_POSITIVE:
                satisfaction = 0.9
            elif feedback.sentiment == FeedbackSentiment.POSITIVE:
                satisfaction = 0.7
            elif feedback.sentiment == FeedbackSentiment.NEGATIVE:
                satisfaction = 0.3
            elif feedback.sentiment == FeedbackSentiment.VERY_NEGATIVE:
                satisfaction = 0.1
            
            daily_satisfaction[date_key].append(satisfaction)
        
        # Calculate daily averages
        trend = []
        for date_key in sorted(daily_satisfaction.keys()):
            daily_scores = daily_satisfaction[date_key]
            daily_avg = sum(daily_scores) / len(daily_scores)
            trend.append(daily_avg)
        
        return trend

    def _analyze_feature_requests(self, feedback_list: List[UserFeedback]) -> Dict[str, int]:
        """Analyze and count feature requests"""
        
        feature_requests = {}
        
        for feedback in feedback_list:
            if feedback.feedback_type != FeedbackType.FEATURE_REQUEST:
                continue
            
            if not feedback.text_content:
                continue
            
            text_lower = feedback.text_content.lower()
            
            # Common feature request patterns
            if 'offline' in text_lower:
                feature_requests['offline_mode'] = feature_requests.get('offline_mode', 0) + 1
            
            if 'language' in text_lower and ('more' in text_lower or 'other' in text_lower):
                feature_requests['more_languages'] = feature_requests.get('more_languages', 0) + 1
            
            if 'notification' in text_lower or 'reminder' in text_lower:
                feature_requests['notifications'] = feature_requests.get('notifications', 0) + 1
            
            if 'export' in text_lower or 'save' in text_lower:
                feature_requests['export_conversations'] = feature_requests.get('export_conversations', 0) + 1
            
            if 'search' in text_lower:
                feature_requests['search_functionality'] = feature_requests.get('search_functionality', 0) + 1
            
            if 'personalization' in text_lower or 'customize' in text_lower:
                feature_requests['personalization'] = feature_requests.get('personalization', 0) + 1
        
        return feature_requests

    async def generate_improvement_plan(self, analytics: FeedbackAnalytics) -> Dict[str, Any]:
        """Generate a comprehensive improvement plan based on feedback analytics"""
        
        improvement_plan = {
            'priority_actions': [],
            'short_term_goals': [],
            'long_term_goals': [],
            'spiritual_enhancements': [],
            'technical_improvements': [],
            'user_experience_updates': [],
            'success_metrics': {},
            'timeline': {},
            'resource_requirements': {}
        }
        
        # Priority actions based on critical feedback
        if analytics.average_rating < 3.5:
            improvement_plan['priority_actions'].append({
                'action': 'Address low user satisfaction ratings',
                'severity': 'critical',
                'estimated_effort': 'high'
            })
        
        if analytics.spiritual_accuracy_score < 0.8:
            improvement_plan['priority_actions'].append({
                'action': 'Improve spiritual content accuracy',
                'severity': 'high',
                'estimated_effort': 'medium'
            })
        
        # Short-term goals (1-3 months)
        improvement_plan['short_term_goals'] = [
            'Implement top 3 user-requested features',
            'Improve response time by 20%',
            'Enhance voice recognition accuracy',
            'Strengthen spiritual content validation'
        ]
        
        # Long-term goals (3-12 months)
        improvement_plan['long_term_goals'] = [
            'Achieve 4.5+ average user rating',
            'Implement advanced personalization features',
            'Expand to additional spiritual traditions',
            'Develop expert community platform'
        ]
        
        # Spiritual enhancements
        improvement_plan['spiritual_enhancements'] = [
            'Expand Sanskrit pronunciation accuracy',
            'Add more diverse spiritual perspectives',
            'Implement wisdom progression tracking',
            'Create guided meditation features'
        ]
        
        # Technical improvements based on feedback
        for suggestion in analytics.improvement_suggestions:
            if 'performance' in suggestion.lower():
                improvement_plan['technical_improvements'].append('Optimize system performance and response times')
            elif 'voice' in suggestion.lower():
                improvement_plan['technical_improvements'].append('Enhance voice processing capabilities')
            elif 'accuracy' in suggestion.lower():
                improvement_plan['technical_improvements'].append('Improve content accuracy validation systems')
        
        # Success metrics
        improvement_plan['success_metrics'] = {
            'user_satisfaction': 'Achieve 4.5+ average rating',
            'spiritual_accuracy': 'Maintain 95%+ spiritual accuracy score',
            'response_time': 'Sub-1 second response time',
            'user_retention': '80%+ monthly active user retention',
            'feature_adoption': '60%+ adoption rate for new features'
        }
        
        return improvement_plan

    async def _send_critical_alert(self, feedback: UserFeedback):
        """Send critical feedback alert to administrators"""
        
        alert_data = {
            'feedback_id': feedback.feedback_id,
            'user_id': feedback.user_id,
            'type': feedback.feedback_type.value,
            'priority': feedback.priority.value,
            'content': feedback.text_content[:200] if feedback.text_content else None,
            'timestamp': feedback.timestamp.isoformat(),
            'spiritual_context': feedback.spiritual_context
        }
        
        # Log critical alert
        self.logger.critical(f"CRITICAL FEEDBACK ALERT: {json.dumps(alert_data, indent=2)}")
        
        # In production, this would send email/SMS/Slack notifications
        print(f"🚨 CRITICAL FEEDBACK ALERT: {feedback.feedback_id}")

    async def _flag_for_expert_review(self, feedback: UserFeedback):
        """Flag feedback for expert spiritual review"""
        
        expert_review_data = {
            'feedback_id': feedback.feedback_id,
            'spiritual_concern': True,
            'review_priority': 'high',
            'expert_notification_sent': True,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store expert review flag
        expert_file = os.path.join(self.feedback_storage_path, "expert_review_queue.json")
        
        expert_queue = []
        if os.path.exists(expert_file):
            try:
                with open(expert_file, 'r') as f:
                    expert_queue = json.load(f)
            except Exception:
                pass
        
        expert_queue.append(expert_review_data)
        
        try:
            with open(expert_file, 'w') as f:
                json.dump(expert_queue, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving expert review queue: {e}")

    async def _queue_for_rapid_response(self, feedback: UserFeedback):
        """Queue feedback for rapid response"""
        
        # In production, this would integrate with customer service systems
        self.logger.info(f"Queued for rapid response: {feedback.feedback_id}")

    async def generate_feedback_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive feedback report"""
        
        analytics = await self.analyze_feedback_trends(days)
        improvement_plan = await self.generate_improvement_plan(analytics)
        
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'analysis_period_days': days,
                'spiritual_guidance': self.spiritual_feedback_principles
            },
            'feedback_analytics': asdict(analytics),
            'improvement_plan': improvement_plan,
            'dharmic_insights': {
                'gratitude_message': f"We are grateful for {analytics.total_feedback_count} pieces of feedback from our spiritual community",
                'learning_opportunity': f"Each feedback is a step on our dharmic path of continuous improvement",
                'service_commitment': "We commit to using this feedback to better serve the spiritual needs of all users",
                'wisdom_gained': f"Average spiritual accuracy of {analytics.spiritual_accuracy_score:.1%} reflects our dedication to authentic spiritual guidance"
            },
            'next_actions': {
                'immediate': 'Process high-priority feedback within 24 hours',
                'short_term': 'Implement top user-requested improvements',
                'long_term': 'Achieve dharmic excellence in spiritual guidance technology'
            }
        }
        
        return report

    async def generate_improvement_metrics(self, days: int = 7) -> ContinuousImprovementMetrics:
        """Generate continuous improvement metrics"""
        
        # Load feedback data
        feedback_data = await self._load_feedback_data(days)
        
        # Calculate response quality trend (simplified)
        quality_scores = []
        for feedback in feedback_data:
            if feedback.rating:
                quality_scores.append(feedback.rating / 5.0)
        
        response_quality_trend = quality_scores[-7:] if quality_scores else [0.8]
        
        # Calculate user engagement metrics
        unique_users = len(set(f.user_id for f in feedback_data))
        total_sessions = len(set(f.session_id for f in feedback_data))
        
        user_engagement_metrics = {
            "active_users": unique_users,
            "total_sessions": total_sessions,
            "feedback_rate": len(feedback_data) / max(total_sessions, 1),
            "engagement_score": min(unique_users / 100, 1.0)  # Normalized to 100 users
        }
        
        # Calculate spiritual content accuracy
        spiritual_feedback = [f for f in feedback_data if f.feedback_type == FeedbackType.SPIRITUAL_ACCURACY]
        spiritual_ratings = [f.rating for f in spiritual_feedback if f.rating]
        spiritual_accuracy = sum(spiritual_ratings) / (len(spiritual_ratings) * 5) if spiritual_ratings else 0.9
        
        # Feature adoption rates (simulated)
        feature_adoption_rates = {
            "voice_interface": 0.45,
            "citation_system": 0.78,
            "multi_language": 0.32,
            "feedback_system": 1.0
        }
        
        # Performance improvements (simulated)
        performance_improvements = {
            "response_time_ms": 1200,
            "error_rate": 0.02,
            "uptime": 0.998,
            "cache_hit_rate": 0.85
        }
        
        # Cost optimization impact (simulated)
        cost_optimization_impact = {
            "cost_reduction": 0.15,
            "efficiency_gain": 0.12,
            "resource_utilization": 0.88
        }
        
        # User retention metrics (simulated)
        user_retention_metrics = {
            "daily_retention": 0.68,
            "weekly_retention": 0.45,
            "monthly_retention": 0.32,
            "satisfaction_score": sum(f.rating for f in feedback_data if f.rating) / (len([f for f in feedback_data if f.rating]) * 5) if any(f.rating for f in feedback_data) else 0.8
        }
        
        return ContinuousImprovementMetrics(
            response_quality_trend=response_quality_trend,
            user_engagement_metrics=user_engagement_metrics,
            spiritual_content_accuracy=spiritual_accuracy,
            feature_adoption_rates=feature_adoption_rates,
            performance_improvements=performance_improvements,
            cost_optimization_impact=cost_optimization_impact,
            user_retention_metrics=user_retention_metrics
        )

    async def generate_improvement_suggestions(self) -> List[str]:
        """Generate specific improvement suggestions based on feedback analysis"""
        
        # Load recent feedback
        feedback_data = await self._load_feedback_data(days=7)
        
        suggestions = []
        
        # Analyze ratings
        ratings = [f.rating for f in feedback_data if f.rating]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            if avg_rating < 4.0:
                suggestions.append("Focus on improving response quality - average rating below 4.0")
        
        # Analyze spiritual accuracy concerns
        spiritual_concerns = [f for f in feedback_data if f.feedback_type == FeedbackType.SPIRITUAL_ACCURACY and f.rating and f.rating < 4]
        if spiritual_concerns:
            suggestions.append("Review spiritual accuracy - multiple concerns reported")
        
        # Analyze feature requests
        feature_requests = [f for f in feedback_data if f.feedback_type == FeedbackType.FEATURE_REQUEST]
        if feature_requests:
            suggestions.append(f"Consider implementing {len(feature_requests)} feature requests")
        
        # Analyze bug reports
        bug_reports = [f for f in feedback_data if f.feedback_type == FeedbackType.BUG_REPORT]
        if bug_reports:
            suggestions.append(f"Address {len(bug_reports)} reported bugs")
        
        # Default suggestions if no specific feedback
        if not suggestions:
            suggestions = [
                "Continue monitoring user satisfaction metrics",
                "Maintain current spiritual content quality standards",
                "Consider proactive user engagement improvements"
            ]
        
        return suggestions

    async def _load_feedback_data(self, days: int = 7) -> List[UserFeedback]:
        """Load feedback data from storage for the specified number of days"""
        
        feedback_data = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            # Load from processed feedback
            for feedback in self.processed_feedback:
                if feedback.timestamp >= cutoff_date:
                    feedback_data.append(feedback)
            
            # Load from stored files
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime("%Y%m%d")
                file_path = os.path.join(self.feedback_storage_path, f"feedback_{date_str}.json")
                
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            stored_data = json.load(f)
                            
                        for item in stored_data:
                            try:
                                # Convert stored data back to UserFeedback object
                                feedback = UserFeedback(
                                    feedback_id=item.get('feedback_id', ''),
                                    user_id=item.get('user_id', ''),
                                    session_id=item.get('session_id', ''),
                                    feedback_type=FeedbackType(item.get('feedback_type', 'text_feedback')),
                                    timestamp=datetime.fromisoformat(item.get('timestamp', datetime.now().isoformat())),
                                    rating=item.get('rating'),
                                    text_content=item.get('text_content'),
                                    voice_transcript=item.get('voice_transcript'),
                                    context=item.get('context', {}),
                                    sentiment=FeedbackSentiment(item.get('sentiment', 'neutral')) if item.get('sentiment') else None,
                                    priority=FeedbackPriority(item.get('priority', 'medium')),
                                    spiritual_context=item.get('spiritual_context', {}),
                                    processed=item.get('processed', False),
                                    response_generated=item.get('response_generated', False)
                                )
                                
                                if feedback.timestamp >= cutoff_date:
                                    feedback_data.append(feedback)
                                    
                            except (ValueError, KeyError) as e:
                                self.logger.error(f"Error parsing feedback item: {e}")
                                continue
                                
                    except (json.JSONDecodeError, IOError) as e:
                        self.logger.error(f"Error loading feedback from {file_path}: {e}")
                        continue
            
        except Exception as e:
            self.logger.error(f"Error loading feedback data: {e}")
        
        return feedback_data

# Convenience functions for easy integration
async def collect_user_feedback(user_id: str, 
                              session_id: str,
                              feedback_type: str,
                              rating: Optional[int] = None,
                              text_content: Optional[str] = None,
                              context: Optional[Dict[str, Any]] = None) -> str:
    """Convenient function to collect user feedback"""
    
    collector = VimarshFeedbackCollector()
    feedback_type_enum = FeedbackType(feedback_type)
    
    return await collector.collect_feedback(
        user_id=user_id,
        session_id=session_id,
        feedback_type=feedback_type_enum,
        rating=rating,
        text_content=text_content,
        context=context
    )

async def generate_weekly_feedback_report() -> Dict[str, Any]:
    """Generate weekly feedback report"""
    
    collector = VimarshFeedbackCollector()
    return await collector.generate_feedback_report(days=7)

# CLI interface for standalone usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Vimarsh Feedback Collection and Analysis")
    parser.add_argument('--action', choices=['collect', 'analyze', 'report'], default='report',
                       help='Action to perform')
    parser.add_argument('--days', type=int, default=7, help='Days to analyze')
    parser.add_argument('--output', help='Output file for report')
    
    args = parser.parse_args()
    
    async def main():
        collector = VimarshFeedbackCollector()
        
        if args.action == 'analyze':
            analytics = await collector.analyze_feedback_trends(args.days)
            result = asdict(analytics)
        elif args.action == 'report':
            result = await collector.generate_feedback_report(args.days)
        else:
            print("Use collect action through the API")
            return
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"Report saved to {args.output}")
        else:
            print(json.dumps(result, indent=2, default=str))
    
    asyncio.run(main())
