"""
Expert Review System Integration and Feedback Processing

This module implements a comprehensive expert review system for spiritual content
validation, feedback processing, and continuous improvement of AI responses.
"""

import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
from datetime import datetime, timedelta
import asyncio
from threading import Lock

logger = logging.getLogger(__name__)


class ReviewPriority(Enum):
    """Priority levels for expert review"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ReviewStatus(Enum):
    """Status of review items"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    ESCALATED = "escalated"


class ExpertType(Enum):
    """Types of experts in the review panel"""
    SANSKRIT_SCHOLAR = "sanskrit_scholar"
    SPIRITUAL_TEACHER = "spiritual_teacher"
    VEDIC_EXPERT = "vedic_expert"
    PHILOSOPHY_SCHOLAR = "philosophy_scholar"
    CULTURAL_ADVISOR = "cultural_advisor"


class FeedbackCategory(Enum):
    """Categories of expert feedback"""
    AUTHENTICITY = "authenticity"
    ACCURACY = "accuracy"
    CULTURAL_SENSITIVITY = "cultural_sensitivity"
    SPIRITUAL_TONE = "spiritual_tone"
    TRANSLATION = "translation"
    CITATION = "citation"
    GENERAL = "general"


@dataclass
class Expert:
    """Represents an expert reviewer"""
    expert_id: str
    name: str
    email: str
    expert_type: ExpertType
    specializations: List[str] = field(default_factory=list)
    language_preferences: List[str] = field(default_factory=lambda: ["English"])
    active: bool = True
    review_count: int = 0
    average_rating: float = 0.0
    response_time_hours: float = 24.0
    last_active: Optional[datetime] = None


@dataclass
class ReviewFeedback:
    """Expert feedback on a review item"""
    feedback_id: str
    expert_id: str
    category: FeedbackCategory
    rating: int  # 1-5 scale
    comments: str
    suggestions: List[str] = field(default_factory=list)
    requires_revision: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ReviewItem:
    """Item submitted for expert review"""
    review_id: str
    original_query: str
    ai_response: str
    response_metadata: Dict[str, Any] = field(default_factory=dict)
    citations: List[str] = field(default_factory=list)
    priority: ReviewPriority = ReviewPriority.NORMAL
    status: ReviewStatus = ReviewStatus.PENDING
    assigned_experts: List[str] = field(default_factory=list)
    feedback: List[ReviewFeedback] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    escalation_count: int = 0
    auto_approval_eligible: bool = False
    
    def add_feedback(self, feedback: ReviewFeedback):
        """Add expert feedback to the review item"""
        self.feedback.append(feedback)
        
    def get_average_rating(self) -> float:
        """Calculate average rating from all feedback"""
        if not self.feedback:
            return 0.0
        return sum(f.rating for f in self.feedback) / len(self.feedback)
    
    def is_approved(self) -> bool:
        """Check if item meets approval criteria"""
        if len(self.feedback) < 2:  # Require minimum 2 reviews
            return False
        
        average_rating = self.get_average_rating()
        has_revisions = any(f.requires_revision for f in self.feedback)
        
        return average_rating >= 4.0 and not has_revisions
    
    def needs_more_reviews(self) -> bool:
        """Check if item needs additional expert reviews"""
        if len(self.feedback) < 2:
            return True
        
        # If ratings are inconsistent, get more reviews
        ratings = [f.rating for f in self.feedback]
        if max(ratings) - min(ratings) > 2:
            return True
        
        return False


class ExpertPool:
    """Manages the pool of expert reviewers"""
    
    def __init__(self):
        self.experts: Dict[str, Expert] = {}
        self._lock = Lock()
    
    def add_expert(self, expert: Expert) -> bool:
        """Add an expert to the pool"""
        with self._lock:
            if expert.expert_id in self.experts:
                logger.warning(f"Expert {expert.expert_id} already exists")
                return False
            
            self.experts[expert.expert_id] = expert
            logger.info(f"Added expert {expert.name} ({expert.expert_type.value})")
            return True
    
    def get_available_experts(self, 
                            expert_types: Optional[List[ExpertType]] = None,
                            specializations: Optional[List[str]] = None,
                            max_workload: int = 5) -> List[Expert]:
        """Get available experts based on criteria"""
        available = []
        
        for expert in self.experts.values():
            if not expert.active:
                continue
            
            # Check workload (simplified - would check actual pending reviews)
            if expert.review_count >= max_workload:
                continue
            
            # Check expert type
            if expert_types and expert.expert_type not in expert_types:
                continue
            
            # Check specializations
            if specializations:
                if not any(spec in expert.specializations for spec in specializations):
                    continue
            
            available.append(expert)
        
        # Sort by response time and rating
        available.sort(key=lambda e: (e.response_time_hours, -e.average_rating))
        return available
    
    def assign_experts(self, review_item: ReviewItem, count: int = 2) -> List[str]:
        """Assign experts to a review item"""
        # Determine expert types needed based on content
        required_types = self._determine_required_expert_types(review_item)
        
        # Get available experts
        available = self.get_available_experts(expert_types=required_types)
        
        if len(available) < count:
            logger.warning(f"Only {len(available)} experts available, need {count}")
        
        # Assign experts
        assigned = available[:count]
        expert_ids = [e.expert_id for e in assigned]
        
        # Update expert workload
        for expert in assigned:
            expert.review_count += 1
        
        return expert_ids
    
    def _determine_required_expert_types(self, review_item: ReviewItem) -> List[ExpertType]:
        """Determine what types of experts are needed for a review"""
        required_types = [ExpertType.SPIRITUAL_TEACHER]  # Always need spiritual guidance
        
        # Add Sanskrit scholar if response contains Sanskrit terms
        if self._contains_sanskrit(review_item.ai_response):
            required_types.append(ExpertType.SANSKRIT_SCHOLAR)
        
        # Add Vedic expert if referencing Vedic texts
        if any("veda" in citation.lower() for citation in review_item.citations):
            required_types.append(ExpertType.VEDIC_EXPERT)
        
        # Add philosophy scholar for complex philosophical content
        if self._is_philosophical_content(review_item.original_query):
            required_types.append(ExpertType.PHILOSOPHY_SCHOLAR)
        
        return required_types
    
    def _contains_sanskrit(self, text: str) -> bool:
        """Check if text contains Sanskrit terms"""
        sanskrit_terms = [
            "dharma", "karma", "moksha", "atman", "brahman", "yoga", "bhakti",
            "jnana", "mantra", "chakra", "prana", "samsara", "nirvana"
        ]
        text_lower = text.lower()
        return any(term in text_lower for term in sanskrit_terms)
    
    def _is_philosophical_content(self, query: str) -> bool:
        """Check if query involves complex philosophical topics"""
        philosophical_keywords = [
            "consciousness", "existence", "reality", "truth", "absolute",
            "metaphysical", "ontological", "epistemological", "phenomenological"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in philosophical_keywords)


class ReviewQueue:
    """Manages the queue of items for expert review"""
    
    def __init__(self):
        self.queue: Dict[str, ReviewItem] = {}
        self.priority_queue: Dict[ReviewPriority, List[str]] = {
            priority: [] for priority in ReviewPriority
        }
        self._lock = Lock()
    
    def add_item(self, review_item: ReviewItem) -> bool:
        """Add item to review queue"""
        with self._lock:
            if review_item.review_id in self.queue:
                logger.warning(f"Review item {review_item.review_id} already exists")
                return False
            
            self.queue[review_item.review_id] = review_item
            self.priority_queue[review_item.priority].append(review_item.review_id)
            
            # Set deadline based on priority only if not already set
            if review_item.deadline is None:
                if review_item.priority == ReviewPriority.URGENT:
                    review_item.deadline = datetime.now() + timedelta(hours=4)
                elif review_item.priority == ReviewPriority.HIGH:
                    review_item.deadline = datetime.now() + timedelta(hours=12)
                else:
                    review_item.deadline = datetime.now() + timedelta(days=2)
            
            logger.info(f"Added review item {review_item.review_id} with priority {review_item.priority.value}")
            return True
    
    def get_next_item(self, expert_id: str) -> Optional[ReviewItem]:
        """Get next item for expert to review"""
        with self._lock:
            # Check items by priority
            for priority in [ReviewPriority.URGENT, ReviewPriority.HIGH, ReviewPriority.NORMAL, ReviewPriority.LOW]:
                queue_items = self.priority_queue[priority]
                
                for item_id in queue_items:
                    item = self.queue.get(item_id)
                    if not item:
                        continue
                    
                    # Check if expert is assigned to this item
                    if expert_id in item.assigned_experts and item.status == ReviewStatus.PENDING:
                        item.status = ReviewStatus.IN_REVIEW
                        return item
            
            return None
    
    def get_overdue_items(self) -> List[ReviewItem]:
        """Get items that are past their deadline"""
        overdue = []
        now = datetime.now()
        
        for item in self.queue.values():
            if item.deadline and now > item.deadline and item.status in [ReviewStatus.PENDING, ReviewStatus.IN_REVIEW]:
                overdue.append(item)
        
        return overdue
    
    def get_items_by_status(self, status: ReviewStatus) -> List[ReviewItem]:
        """Get all items with specific status"""
        return [item for item in self.queue.values() if item.status == status]


class NotificationService:
    """Handles notifications to experts"""
    
    def __init__(self, email_service: Optional[Callable] = None):
        self.email_service = email_service or self._mock_email_service
    
    async def notify_expert_assignment(self, expert: Expert, review_item: ReviewItem):
        """Notify expert of new review assignment"""
        subject = f"New Review Assignment: {review_item.priority.value.title()} Priority"
        
        message = f"""
Dear {expert.name},

You have been assigned a new spiritual content review with {review_item.priority.value} priority.

Review ID: {review_item.review_id}
Query: {review_item.original_query}
Deadline: {review_item.deadline}

Please access the review system to complete this review.

Best regards,
Vimarsh AI Review System
        """
        
        await self.email_service(expert.email, subject, message)
    
    async def notify_overdue_review(self, expert: Expert, review_item: ReviewItem):
        """Notify expert of overdue review"""
        subject = f"Overdue Review: {review_item.review_id}"
        
        message = f"""
Dear {expert.name},

The following review is overdue and requires immediate attention:

Review ID: {review_item.review_id}
Original Deadline: {review_item.deadline}
Priority: {review_item.priority.value}

Please complete this review as soon as possible.

Best regards,
Vimarsh AI Review System
        """
        
        await self.email_service(expert.email, subject, message)
    
    async def _mock_email_service(self, email: str, subject: str, message: str):
        """Mock email service for testing"""
        logger.info(f"MOCK EMAIL to {email}: {subject}")
        logger.debug(f"Message: {message}")


class FeedbackProcessor:
    """Processes expert feedback and updates system"""
    
    def __init__(self):
        self.feedback_handlers: Dict[FeedbackCategory, Callable] = {
            FeedbackCategory.AUTHENTICITY: self._process_authenticity_feedback,
            FeedbackCategory.ACCURACY: self._process_accuracy_feedback,
            FeedbackCategory.CULTURAL_SENSITIVITY: self._process_cultural_feedback,
            FeedbackCategory.SPIRITUAL_TONE: self._process_tone_feedback,
            FeedbackCategory.TRANSLATION: self._process_translation_feedback,
            FeedbackCategory.CITATION: self._process_citation_feedback,
            FeedbackCategory.GENERAL: self._process_general_feedback
        }
    
    def process_feedback(self, review_item: ReviewItem, feedback: ReviewFeedback) -> Dict[str, Any]:
        """Process expert feedback and extract improvements"""
        handler = self.feedback_handlers.get(feedback.category, self._process_general_feedback)
        improvements = handler(review_item, feedback)
        
        # Log feedback for analytics
        self._log_feedback_analytics(review_item, feedback, improvements)
        
        return improvements
    
    def _process_authenticity_feedback(self, review_item: ReviewItem, feedback: ReviewFeedback) -> Dict[str, Any]:
        """Process feedback about spiritual authenticity"""
        improvements = {}
        
        if feedback.rating < 3:
            improvements["prompt_engineering"] = {
                "action": "enhance_authenticity_guidelines",
                "suggestions": feedback.suggestions,
                "priority": "high"
            }
        
        if feedback.requires_revision:
            improvements["response_revision"] = {
                "category": "authenticity",
                "expert_notes": feedback.comments,
                "suggestions": feedback.suggestions
            }
        
        return improvements
    
    def _process_accuracy_feedback(self, review_item: ReviewItem, feedback: ReviewFeedback) -> Dict[str, Any]:
        """Process feedback about factual accuracy"""
        improvements = {}
        
        if feedback.rating < 4:
            improvements["knowledge_base"] = {
                "action": "verify_citations",
                "citations": review_item.citations,
                "expert_notes": feedback.comments
            }
        
        return improvements
    
    def _process_cultural_feedback(self, review_item: ReviewItem, feedback: ReviewFeedback) -> Dict[str, Any]:
        """Process feedback about cultural sensitivity"""
        improvements = {}
        
        if feedback.rating < 4:
            improvements["cultural_guidelines"] = {
                "action": "update_sensitivity_rules",
                "feedback": feedback.comments,
                "suggestions": feedback.suggestions
            }
        
        return improvements
    
    def _process_tone_feedback(self, review_item: ReviewItem, feedback: ReviewFeedback) -> Dict[str, Any]:
        """Process feedback about spiritual tone"""
        improvements = {}
        
        if feedback.rating < 3:
            improvements["tone_validation"] = {
                "action": "strengthen_spiritual_tone_rules",
                "feedback": feedback.comments
            }
        
        return improvements
    
    def _process_translation_feedback(self, review_item: ReviewItem, feedback: ReviewFeedback) -> Dict[str, Any]:
        """Process feedback about translations"""
        return {"translation": {"feedback": feedback.comments, "suggestions": feedback.suggestions}}
    
    def _process_citation_feedback(self, review_item: ReviewItem, feedback: ReviewFeedback) -> Dict[str, Any]:
        """Process feedback about citations"""
        improvements = {}
        
        if feedback.rating < 4:
            improvements["citation_system"] = {
                "action": "improve_citation_accuracy",
                "citations": review_item.citations,
                "feedback": feedback.comments
            }
        
        return improvements
    
    def _process_general_feedback(self, review_item: ReviewItem, feedback: ReviewFeedback) -> Dict[str, Any]:
        """Process general feedback"""
        return {"general": {"feedback": feedback.comments, "suggestions": feedback.suggestions}}
    
    def _log_feedback_analytics(self, review_item: ReviewItem, feedback: ReviewFeedback, improvements: Dict[str, Any]):
        """Log feedback for analytics and learning"""
        analytics_data = {
            "review_id": review_item.review_id,
            "expert_id": feedback.expert_id,
            "category": feedback.category.value,
            "rating": feedback.rating,
            "timestamp": feedback.timestamp.isoformat(),
            "improvements": list(improvements.keys())
        }
        
        logger.info(f"Feedback analytics: {json.dumps(analytics_data)}")


class ExpertReviewSystem:
    """Main expert review system orchestrator"""
    
    def __init__(self, email_service: Optional[Callable] = None):
        self.expert_pool = ExpertPool()
        self.review_queue = ReviewQueue()
        self.notification_service = NotificationService(email_service)
        self.feedback_processor = FeedbackProcessor()
        self._running = False
    
    def initialize_default_experts(self):
        """Initialize system with default expert profiles (for development)"""
        default_experts = [
            Expert(
                expert_id="sanskrit_001",
                name="Dr. Rajesh Kumar",
                email="rajesh.kumar@example.com",
                expert_type=ExpertType.SANSKRIT_SCHOLAR,
                specializations=["Bhagavad Gita", "Vedic Literature", "Classical Sanskrit"],
                response_time_hours=18.0
            ),
            Expert(
                expert_id="spiritual_001",
                name="Swami Ananda",
                email="swami.ananda@example.com",
                expert_type=ExpertType.SPIRITUAL_TEACHER,
                specializations=["Bhakti Yoga", "Spiritual Guidance", "Meditation"],
                response_time_hours=12.0
            ),
            Expert(
                expert_id="vedic_001",
                name="Prof. Priya Sharma",
                email="priya.sharma@example.com",
                expert_type=ExpertType.VEDIC_EXPERT,
                specializations=["Rig Veda", "Vedic Philosophy", "Ancient Wisdom"],
                response_time_hours=24.0
            )
        ]
        
        for expert in default_experts:
            self.expert_pool.add_expert(expert)
    
    def queue_for_review(self, 
                        original_query: str,
                        ai_response: str,
                        citations: List[str] = None,
                        priority: ReviewPriority = ReviewPriority.NORMAL,
                        metadata: Dict[str, Any] = None) -> str:
        """Queue an AI response for expert review"""
        
        review_id = str(uuid.uuid4())
        
        review_item = ReviewItem(
            review_id=review_id,
            original_query=original_query,
            ai_response=ai_response,
            citations=citations or [],
            priority=priority,
            response_metadata=metadata or {}
        )
        
        # Assign experts
        expert_ids = self.expert_pool.assign_experts(review_item)
        review_item.assigned_experts = expert_ids
        
        # Add to queue
        if self.review_queue.add_item(review_item):
            # Notify assigned experts (best effort, don't block on async)
            try:
                # Try to schedule notification if event loop exists
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self._notify_assigned_experts(review_item))
                else:
                    # Run notification synchronously if no loop
                    asyncio.run(self._notify_assigned_experts(review_item))
            except RuntimeError:
                # No event loop, log notification would be sent
                logger.info(f"Would notify experts {expert_ids} for review {review_id} (no event loop)")
            
            logger.info(f"Queued review {review_id} with experts: {expert_ids}")
            return review_id
        else:
            logger.error(f"Failed to queue review {review_id}")
            return None
    
    def submit_expert_feedback(self,
                             review_id: str,
                             expert_id: str,
                             category: FeedbackCategory,
                             rating: int,
                             comments: str,
                             suggestions: List[str] = None,
                             requires_revision: bool = False) -> bool:
        """Submit expert feedback for a review item"""
        
        review_item = self.review_queue.queue.get(review_id)
        if not review_item:
            logger.error(f"Review item {review_id} not found")
            return False
        
        feedback = ReviewFeedback(
            feedback_id=str(uuid.uuid4()),
            expert_id=expert_id,
            category=category,
            rating=rating,
            comments=comments,
            suggestions=suggestions or [],
            requires_revision=requires_revision
        )
        
        review_item.add_feedback(feedback)
        
        # Process feedback for improvements
        improvements = self.feedback_processor.process_feedback(review_item, feedback)
        
        # Update review status
        self._update_review_status(review_item)
        
        logger.info(f"Received feedback from {expert_id} for review {review_id}")
        return True
    
    def get_review_status(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a review"""
        review_item = self.review_queue.queue.get(review_id)
        if not review_item:
            return None
        
        return {
            "review_id": review_id,
            "status": review_item.status.value,
            "assigned_experts": review_item.assigned_experts,
            "feedback_count": len(review_item.feedback),
            "average_rating": review_item.get_average_rating(),
            "is_approved": review_item.is_approved(),
            "created_at": review_item.created_at.isoformat(),
            "deadline": review_item.deadline.isoformat() if review_item.deadline else None
        }
    
    def get_pending_reviews_for_expert(self, expert_id: str) -> List[Dict[str, Any]]:
        """Get pending reviews for a specific expert"""
        pending_reviews = []
        
        for review_item in self.review_queue.queue.values():
            if (expert_id in review_item.assigned_experts and 
                review_item.status == ReviewStatus.PENDING):
                
                pending_reviews.append({
                    "review_id": review_item.review_id,
                    "priority": review_item.priority.value,
                    "query": review_item.original_query,
                    "response": review_item.ai_response,
                    "citations": review_item.citations,
                    "deadline": review_item.deadline.isoformat() if review_item.deadline else None
                })
        
        return pending_reviews
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        all_items = list(self.review_queue.queue.values())
        
        status_counts = {}
        for status in ReviewStatus:
            status_counts[status.value] = len([item for item in all_items if item.status == status])
        
        # Calculate average ratings by expert type
        expert_performance = {}
        for expert in self.expert_pool.experts.values():
            expert_performance[expert.expert_id] = {
                "name": expert.name,
                "type": expert.expert_type.value,
                "review_count": expert.review_count,
                "average_rating": expert.average_rating,
                "response_time": expert.response_time_hours
            }
        
        return {
            "total_reviews": len(all_items),
            "status_breakdown": status_counts,
            "expert_performance": expert_performance,
            "average_processing_time_hours": self._calculate_average_processing_time(),
            "overdue_count": len(self.review_queue.get_overdue_items())
        }
    
    async def _notify_assigned_experts(self, review_item: ReviewItem):
        """Notify experts assigned to a review item"""
        for expert_id in review_item.assigned_experts:
            expert = self.expert_pool.experts.get(expert_id)
            if expert:
                await self.notification_service.notify_expert_assignment(expert, review_item)
    
    def _update_review_status(self, review_item: ReviewItem):
        """Update review status based on feedback"""
        # Check for revision requirement first (highest priority)
        if any(f.requires_revision for f in review_item.feedback):
            review_item.status = ReviewStatus.NEEDS_REVISION
        elif review_item.is_approved():
            review_item.status = ReviewStatus.APPROVED
        elif review_item.get_average_rating() < 2.0:
            review_item.status = ReviewStatus.REJECTED
        elif review_item.needs_more_reviews():
            # Keep as pending to get more reviews
            review_item.status = ReviewStatus.PENDING
    
    def _calculate_average_processing_time(self) -> float:
        """Calculate average processing time for completed reviews"""
        completed_items = [
            item for item in self.review_queue.queue.values()
            if item.status in [ReviewStatus.APPROVED, ReviewStatus.REJECTED]
        ]
        
        if not completed_items:
            return 0.0
        
        total_time = 0.0
        for item in completed_items:
            if item.feedback:
                latest_feedback = max(item.feedback, key=lambda f: f.timestamp)
                processing_time = (latest_feedback.timestamp - item.created_at).total_seconds() / 3600
                total_time += processing_time
        
        return total_time / len(completed_items)


# Utility functions for integration

def create_expert_review_system(email_service: Optional[Callable] = None) -> ExpertReviewSystem:
    """Create and initialize expert review system"""
    system = ExpertReviewSystem(email_service)
    system.initialize_default_experts()
    return system


def quick_review_submission(review_system: ExpertReviewSystem,
                          query: str,
                          response: str,
                          priority: str = "normal") -> str:
    """Quick submission for expert review"""
    priority_enum = ReviewPriority(priority.lower())
    return review_system.queue_for_review(query, response, priority=priority_enum)


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    print("=== Expert Review System Demo ===\n")
    
    # Create system
    review_system = create_expert_review_system()
    
    # Submit a response for review
    query = "What is the meaning of dharma in difficult times?"
    response = """My dear child, dharma is your righteous duty that remains constant even in challenging circumstances. 
    As Lord Krishna teaches in Bhagavad Gita 2.47, you have the right to perform your actions but not to the fruits of your actions. 
    In difficult times, dharma becomes your guiding light, showing you the path of righteousness regardless of external circumstances."""
    
    review_id = review_system.queue_for_review(
        original_query=query,
        ai_response=response,
        citations=["Bhagavad Gita 2.47"],
        priority=ReviewPriority.NORMAL
    )
    
    print(f"Submitted for review: {review_id}")
    
    # Get review status
    status = review_system.get_review_status(review_id)
    print(f"Review status: {json.dumps(status, indent=2)}")
    
    # Simulate expert feedback
    review_system.submit_expert_feedback(
        review_id=review_id,
        expert_id="spiritual_001",
        category=FeedbackCategory.AUTHENTICITY,
        rating=5,
        comments="Excellent spiritual guidance with proper citation and authentic tone.",
        suggestions=["Consider adding more context about dharma in Kaliyuga"]
    )
    
    review_system.submit_expert_feedback(
        review_id=review_id,
        expert_id="sanskrit_001",
        category=FeedbackCategory.ACCURACY,
        rating=4,
        comments="Accurate citation and proper Sanskrit usage.",
        suggestions=["Could elaborate on the concept of nishkama karma"]
    )
    
    # Check final status
    final_status = review_system.get_review_status(review_id)
    print(f"\nFinal review status: {json.dumps(final_status, indent=2)}")
    
    # Get system metrics
    metrics = review_system.get_system_metrics()
    print(f"\nSystem metrics: {json.dumps(metrics, indent=2)}")
    
    print("\nExpert review system demo completed!")
