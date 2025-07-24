"""
Expert Review Service for Vimarsh Multi-Domain Content Validation

This service provides comprehensive expert review workflows for validating
AI-generated content across spiritual, historical, scientific, and philosophical domains.
It ensures authenticity, accuracy, and respect for each personality's legacy.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import uuid

logger = logging.getLogger(__name__)

class ReviewDomain(Enum):
    SPIRITUAL = "spiritual"
    HISTORICAL = "historical"
    SCIENTIFIC = "scientific"
    PHILOSOPHICAL = "philosophical"

class ReviewStatus(Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    REQUIRES_REVISION = "requires_revision"

class ReviewPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ExpertLevel(Enum):
    JUNIOR = "junior"
    SENIOR = "senior"
    LEAD = "lead"
    DOMAIN_EXPERT = "domain_expert"

@dataclass
class ExpertProfile:
    expert_id: str
    name: str
    email: str
    domains: List[ReviewDomain]
    expertise_level: ExpertLevel
    specializations: List[str]
    languages: List[str]
    availability_hours: Dict[str, Any]  # Weekly schedule
    max_concurrent_reviews: int
    current_workload: int
    quality_score: float
    created_at: datetime
    is_active: bool = True

@dataclass
class ReviewItem:
    review_id: str
    content_id: str
    content_type: str  # "response", "content", "personality_profile"
    content_title: str
    content_preview: str
    domain: ReviewDomain
    personality_id: str
    priority: ReviewPriority
    status: ReviewStatus
    assigned_expert_id: Optional[str]
    created_at: datetime
    assigned_at: Optional[datetime]
    due_date: datetime
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]

@dataclass
class ExpertFeedback:
    feedback_id: str
    review_id: str
    expert_id: str
    accuracy_score: float  # 0-100
    authenticity_score: float  # 0-100
    appropriateness_score: float  # 0-100
    overall_score: float  # 0-100
    feedback_text: str
    suggested_improvements: List[str]
    flags: List[str]  # ["factual_error", "tone_inappropriate", "citation_missing"]
    recommendation: ReviewStatus
    confidence_level: float  # 0-100
    time_spent_minutes: int
    created_at: datetime

@dataclass
class ReviewQueue:
    domain: ReviewDomain
    pending_count: int
    in_review_count: int
    overdue_count: int
    avg_review_time_hours: float
    expert_availability: int

class ExpertReviewService:
    """Central service for managing expert review workflows"""
    
    def __init__(self):
        self.experts: Dict[str, ExpertProfile] = {}
        self.review_items: Dict[str, ReviewItem] = {}
        self.feedback_history: Dict[str, List[ExpertFeedback]] = {}
        self.domain_queues: Dict[ReviewDomain, List[str]] = {
            domain: [] for domain in ReviewDomain
        }
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize with mock expert profiles and review items"""
        # Mock expert profiles
        mock_experts = [
            ExpertProfile(
                expert_id="expert_spiritual_1",
                name="Dr. Priya Sharma",
                email="priya.sharma@vedprakash.net",
                domains=[ReviewDomain.SPIRITUAL],
                expertise_level=ExpertLevel.DOMAIN_EXPERT,
                specializations=["Hindu Philosophy", "Sanskrit", "Bhagavad Gita", "Vedanta"],
                languages=["English", "Hindi", "Sanskrit"],
                availability_hours={"monday": "9-17", "tuesday": "9-17", "wednesday": "9-17"},
                max_concurrent_reviews=5,
                current_workload=2,
                quality_score=96.5,
                created_at=datetime.now() - timedelta(days=180)
            ),
            ExpertProfile(
                expert_id="expert_historical_1",
                name="Prof. Michael Thompson",
                email="m.thompson@history.edu",
                domains=[ReviewDomain.HISTORICAL],
                expertise_level=ExpertLevel.DOMAIN_EXPERT,
                specializations=["American History", "Civil War", "Presidential Studies"],
                languages=["English"],
                availability_hours={"monday": "10-16", "wednesday": "10-16", "friday": "10-16"},
                max_concurrent_reviews=3,
                current_workload=1,
                quality_score=94.2,
                created_at=datetime.now() - timedelta(days=120)
            ),
            ExpertProfile(
                expert_id="expert_scientific_1",
                name="Dr. Sarah Chen",
                email="s.chen@physics.edu",
                domains=[ReviewDomain.SCIENTIFIC],
                expertise_level=ExpertLevel.DOMAIN_EXPERT,
                specializations=["Theoretical Physics", "Relativity", "Quantum Mechanics"],
                languages=["English", "German"],
                availability_hours={"tuesday": "9-17", "thursday": "9-17"},
                max_concurrent_reviews=4,
                current_workload=3,
                quality_score=98.1,
                created_at=datetime.now() - timedelta(days=90)
            ),
            ExpertProfile(
                expert_id="expert_philosophical_1",
                name="Dr. Marcus Romano",
                email="m.romano@philosophy.edu",
                domains=[ReviewDomain.PHILOSOPHICAL],
                expertise_level=ExpertLevel.DOMAIN_EXPERT,
                specializations=["Stoicism", "Ancient Philosophy", "Ethics"],
                languages=["English", "Latin", "Greek"],
                availability_hours={"monday": "9-15", "wednesday": "9-15", "friday": "9-15"},
                max_concurrent_reviews=3,
                current_workload=1,
                quality_score=95.8,
                created_at=datetime.now() - timedelta(days=150)
            )
        ]
        
        for expert in mock_experts:
            self.experts[expert.expert_id] = expert
        
        # Mock review items
        mock_reviews = [
            ReviewItem(
                review_id="review_001",
                content_id="content_1",
                content_type="response",
                content_title="Krishna's guidance on dharma",
                content_preview="O child, dharma is the eternal law that governs righteous living...",
                domain=ReviewDomain.SPIRITUAL,
                personality_id="krishna",
                priority=ReviewPriority.HIGH,
                status=ReviewStatus.PENDING,
                assigned_expert_id=None,
                created_at=datetime.now() - timedelta(hours=2),
                assigned_at=None,
                due_date=datetime.now() + timedelta(days=2),
                completed_at=None,
                metadata={"user_query": "What is dharma?", "confidence": 0.85}
            ),
            ReviewItem(
                review_id="review_002",
                content_id="content_2",
                content_type="content",
                content_title="Einstein's Theory of Relativity",
                content_preview="The principle of relativity states that the laws of physics...",
                domain=ReviewDomain.SCIENTIFIC,
                personality_id="einstein",
                priority=ReviewPriority.MEDIUM,
                status=ReviewStatus.IN_REVIEW,
                assigned_expert_id="expert_scientific_1",
                created_at=datetime.now() - timedelta(days=1),
                assigned_at=datetime.now() - timedelta(hours=8),
                due_date=datetime.now() + timedelta(days=3),
                completed_at=None,
                metadata={"source": "Relativity: The Special and General Theory", "page": 15}
            )
        ]
        
        for review in mock_reviews:
            self.review_items[review.review_id] = review
            self.domain_queues[review.domain].append(review.review_id)
    
    async def submit_for_review(
        self,
        content_id: str,
        content_type: str,
        content_title: str,
        content_preview: str,
        domain: ReviewDomain,
        personality_id: str,
        priority: ReviewPriority = ReviewPriority.MEDIUM,
        metadata: Dict[str, Any] = None
    ) -> ReviewItem:
        """Submit content for expert review"""
        
        review_id = f"review_{uuid.uuid4().hex[:8]}"
        due_date = self._calculate_due_date(priority)
        
        review_item = ReviewItem(
            review_id=review_id,
            content_id=content_id,
            content_type=content_type,
            content_title=content_title,
            content_preview=content_preview,
            domain=domain,
            personality_id=personality_id,
            priority=priority,
            status=ReviewStatus.PENDING,
            assigned_expert_id=None,
            created_at=datetime.now(),
            assigned_at=None,
            due_date=due_date,
            completed_at=None,
            metadata=metadata or {}
        )
        
        self.review_items[review_id] = review_item
        self.domain_queues[domain].append(review_id)
        
        # Try to auto-assign if expert is available
        await self._try_auto_assign(review_item)
        
        logger.info(f"Content submitted for review: {review_id} (Domain: {domain.value})")
        return review_item
    
    async def get_review_queues(self) -> Dict[str, ReviewQueue]:
        """Get current status of all review queues"""
        queues = {}
        
        for domain in ReviewDomain:
            domain_reviews = [
                self.review_items[rid] for rid in self.domain_queues[domain]
                if rid in self.review_items
            ]
            
            pending_count = len([r for r in domain_reviews if r.status == ReviewStatus.PENDING])
            in_review_count = len([r for r in domain_reviews if r.status == ReviewStatus.IN_REVIEW])
            overdue_count = len([r for r in domain_reviews if r.due_date < datetime.now() and r.status != ReviewStatus.APPROVED])
            
            # Calculate average review time
            completed_reviews = [r for r in domain_reviews if r.completed_at]
            avg_review_time = 0.0
            if completed_reviews:
                total_time = sum([
                    (r.completed_at - r.assigned_at).total_seconds() / 3600
                    for r in completed_reviews if r.assigned_at
                ])
                avg_review_time = total_time / len(completed_reviews)
            
            # Count available experts
            available_experts = len([
                e for e in self.experts.values()
                if domain in e.domains and e.is_active and e.current_workload < e.max_concurrent_reviews
            ])
            
            queues[domain.value] = ReviewQueue(
                domain=domain,
                pending_count=pending_count,
                in_review_count=in_review_count,
                overdue_count=overdue_count,
                avg_review_time_hours=avg_review_time,
                expert_availability=available_experts
            )
        
        return queues
    
    async def assign_review(self, review_id: str, expert_id: str) -> bool:
        """Manually assign a review to an expert"""
        if review_id not in self.review_items:
            raise ValueError(f"Review {review_id} not found")
        
        if expert_id not in self.experts:
            raise ValueError(f"Expert {expert_id} not found")
        
        review = self.review_items[review_id]
        expert = self.experts[expert_id]
        
        # Validate assignment
        if review.domain not in expert.domains:
            raise ValueError(f"Expert {expert_id} not qualified for domain {review.domain.value}")
        
        if expert.current_workload >= expert.max_concurrent_reviews:
            raise ValueError(f"Expert {expert_id} at maximum capacity")
        
        # Update review and expert
        review.assigned_expert_id = expert_id
        review.assigned_at = datetime.now()
        review.status = ReviewStatus.IN_REVIEW
        expert.current_workload += 1
        
        logger.info(f"Review {review_id} assigned to expert {expert_id}")
        return True
    
    async def submit_expert_feedback(
        self,
        review_id: str,
        expert_id: str,
        accuracy_score: float,
        authenticity_score: float,
        appropriateness_score: float,
        feedback_text: str,
        suggested_improvements: List[str],
        flags: List[str],
        recommendation: ReviewStatus,
        confidence_level: float,
        time_spent_minutes: int
    ) -> ExpertFeedback:
        """Submit expert feedback for a review"""
        
        if review_id not in self.review_items:
            raise ValueError(f"Review {review_id} not found")
        
        review = self.review_items[review_id]
        if review.assigned_expert_id != expert_id:
            raise ValueError(f"Review {review_id} not assigned to expert {expert_id}")
        
        overall_score = (accuracy_score + authenticity_score + appropriateness_score) / 3
        
        feedback = ExpertFeedback(
            feedback_id=f"feedback_{uuid.uuid4().hex[:8]}",
            review_id=review_id,
            expert_id=expert_id,
            accuracy_score=accuracy_score,
            authenticity_score=authenticity_score,
            appropriateness_score=appropriateness_score,
            overall_score=overall_score,
            feedback_text=feedback_text,
            suggested_improvements=suggested_improvements,
            flags=flags,
            recommendation=recommendation,
            confidence_level=confidence_level,
            time_spent_minutes=time_spent_minutes,
            created_at=datetime.now()
        )
        
        # Update review status
        review.status = recommendation
        review.completed_at = datetime.now()
        
        # Update expert workload
        if expert_id in self.experts:
            self.experts[expert_id].current_workload -= 1
        
        # Store feedback
        if review_id not in self.feedback_history:
            self.feedback_history[review_id] = []
        self.feedback_history[review_id].append(feedback)
        
        logger.info(f"Expert feedback submitted for review {review_id} by {expert_id}")
        return feedback
    
    async def get_expert_dashboard(self, expert_id: str) -> Dict[str, Any]:
        """Get dashboard data for a specific expert"""
        if expert_id not in self.experts:
            raise ValueError(f"Expert {expert_id} not found")
        
        expert = self.experts[expert_id]
        
        # Get assigned reviews
        assigned_reviews = [
            r for r in self.review_items.values()
            if r.assigned_expert_id == expert_id and r.status == ReviewStatus.IN_REVIEW
        ]
        
        # Get completed reviews (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        completed_reviews = [
            r for r in self.review_items.values()
            if r.assigned_expert_id == expert_id 
            and r.completed_at 
            and r.completed_at > thirty_days_ago
        ]
        
        # Calculate statistics
        avg_review_time = 0.0
        if completed_reviews:
            total_time = sum([
                (r.completed_at - r.assigned_at).total_seconds() / 3600
                for r in completed_reviews if r.assigned_at
            ])
            avg_review_time = total_time / len(completed_reviews)
        
        return {
            "expert": asdict(expert),
            "assigned_reviews": [asdict(r) for r in assigned_reviews],
            "completed_reviews_count": len(completed_reviews),
            "avg_review_time_hours": avg_review_time,
            "current_workload": expert.current_workload,
            "capacity_utilization": (expert.current_workload / expert.max_concurrent_reviews) * 100
        }
    
    async def get_review_analytics(self) -> Dict[str, Any]:
        """Get comprehensive review analytics"""
        total_reviews = len(self.review_items)
        
        # Status distribution
        status_counts = {}
        for status in ReviewStatus:
            status_counts[status.value] = len([
                r for r in self.review_items.values() if r.status == status
            ])
        
        # Domain distribution
        domain_counts = {}
        for domain in ReviewDomain:
            domain_counts[domain.value] = len([
                r for r in self.review_items.values() if r.domain == domain
            ])
        
        # Priority distribution
        priority_counts = {}
        for priority in ReviewPriority:
            priority_counts[priority.value] = len([
                r for r in self.review_items.values() if r.priority == priority
            ])
        
        # Expert performance
        expert_stats = {}
        for expert_id, expert in self.experts.items():
            completed = len([
                r for r in self.review_items.values()
                if r.assigned_expert_id == expert_id and r.completed_at
            ])
            expert_stats[expert_id] = {
                "name": expert.name,
                "completed_reviews": completed,
                "current_workload": expert.current_workload,
                "quality_score": expert.quality_score
            }
        
        return {
            "total_reviews": total_reviews,
            "status_distribution": status_counts,
            "domain_distribution": domain_counts,
            "priority_distribution": priority_counts,
            "expert_performance": expert_stats,
            "queues": await self.get_review_queues()
        }
    
    def _calculate_due_date(self, priority: ReviewPriority) -> datetime:
        """Calculate due date based on priority"""
        hours_map = {
            ReviewPriority.CRITICAL: 4,
            ReviewPriority.HIGH: 24,
            ReviewPriority.MEDIUM: 72,
            ReviewPriority.LOW: 168  # 1 week
        }
        return datetime.now() + timedelta(hours=hours_map[priority])
    
    async def _try_auto_assign(self, review_item: ReviewItem) -> bool:
        """Try to automatically assign review to available expert"""
        available_experts = [
            expert for expert in self.experts.values()
            if (review_item.domain in expert.domains and 
                expert.is_active and 
                expert.current_workload < expert.max_concurrent_reviews)
        ]
        
        if not available_experts:
            return False
        
        # Sort by quality score and current workload
        available_experts.sort(key=lambda e: (-e.quality_score, e.current_workload))
        best_expert = available_experts[0]
        
        # Auto-assign
        review_item.assigned_expert_id = best_expert.expert_id
        review_item.assigned_at = datetime.now()
        review_item.status = ReviewStatus.IN_REVIEW
        best_expert.current_workload += 1
        
        logger.info(f"Auto-assigned review {review_item.review_id} to expert {best_expert.expert_id}")
        return True

# Global service instance
expert_review_service = ExpertReviewService()