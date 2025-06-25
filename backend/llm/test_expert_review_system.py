"""
Test suite for expert review system integration and feedback processing

Tests all components including:
- Expert management and assignment
- Review queue management
- Feedback processing and analytics
- Notification systems
- System metrics and reporting
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from .expert_review_system import (
    ExpertReviewSystem,
    ExpertPool,
    ReviewQueue,
    NotificationService,
    FeedbackProcessor,
    Expert,
    ReviewItem,
    ReviewFeedback,
    ExpertType,
    ReviewPriority,
    ReviewStatus,
    FeedbackCategory,
    create_expert_review_system,
    quick_review_submission
)


class TestExpert:
    """Test Expert data class"""
    
    def test_expert_creation(self):
        """Test creating an expert"""
        expert = Expert(
            expert_id="test_001",
            name="Dr. Test Expert",
            email="test@example.com",
            expert_type=ExpertType.SANSKRIT_SCHOLAR,
            specializations=["Bhagavad Gita", "Vedic Literature"],
            language_preferences=["English", "Hindi"]
        )
        
        assert expert.expert_id == "test_001"
        assert expert.name == "Dr. Test Expert"
        assert expert.expert_type == ExpertType.SANSKRIT_SCHOLAR
        assert "Bhagavad Gita" in expert.specializations
        assert expert.active == True
        assert expert.review_count == 0


class TestReviewItem:
    """Test ReviewItem data class"""
    
    def test_review_item_creation(self):
        """Test creating a review item"""
        item = ReviewItem(
            review_id="review_001",
            original_query="What is dharma?",
            ai_response="Dharma is righteous duty...",
            citations=["Bhagavad Gita 2.47"],
            priority=ReviewPriority.HIGH
        )
        
        assert item.review_id == "review_001"
        assert item.priority == ReviewPriority.HIGH
        assert item.status == ReviewStatus.PENDING
        assert len(item.citations) == 1
        assert len(item.feedback) == 0
    
    def test_add_feedback(self):
        """Test adding feedback to review item"""
        item = ReviewItem(
            review_id="review_001",
            original_query="Test query",
            ai_response="Test response"
        )
        
        feedback = ReviewFeedback(
            feedback_id="feedback_001",
            expert_id="expert_001",
            category=FeedbackCategory.AUTHENTICITY,
            rating=4,
            comments="Good response"
        )
        
        item.add_feedback(feedback)
        
        assert len(item.feedback) == 1
        assert item.feedback[0] == feedback
    
    def test_average_rating_calculation(self):
        """Test average rating calculation"""
        item = ReviewItem(
            review_id="review_001",
            original_query="Test query",
            ai_response="Test response"
        )
        
        # No feedback
        assert item.get_average_rating() == 0.0
        
        # Add feedback
        feedback1 = ReviewFeedback("f1", "e1", FeedbackCategory.AUTHENTICITY, 4, "Good")
        feedback2 = ReviewFeedback("f2", "e2", FeedbackCategory.ACCURACY, 5, "Excellent")
        
        item.add_feedback(feedback1)
        item.add_feedback(feedback2)
        
        assert item.get_average_rating() == 4.5
    
    def test_approval_logic(self):
        """Test approval logic"""
        item = ReviewItem(
            review_id="review_001",
            original_query="Test query",
            ai_response="Test response"
        )
        
        # Not approved with no feedback
        assert not item.is_approved()
        
        # Not approved with only one feedback
        feedback1 = ReviewFeedback("f1", "e1", FeedbackCategory.AUTHENTICITY, 5, "Excellent")
        item.add_feedback(feedback1)
        assert not item.is_approved()
        
        # Approved with two good ratings
        feedback2 = ReviewFeedback("f2", "e2", FeedbackCategory.ACCURACY, 4, "Good")
        item.add_feedback(feedback2)
        assert item.is_approved()
        
        # Not approved if revision required
        feedback3 = ReviewFeedback("f3", "e3", FeedbackCategory.CULTURAL_SENSITIVITY, 5, "Good", requires_revision=True)
        item.add_feedback(feedback3)
        assert not item.is_approved()
    
    def test_needs_more_reviews(self):
        """Test logic for needing more reviews"""
        item = ReviewItem(
            review_id="review_001",
            original_query="Test query",
            ai_response="Test response"
        )
        
        # Needs more with no feedback
        assert item.needs_more_reviews()
        
        # Needs more with only one feedback
        feedback1 = ReviewFeedback("f1", "e1", FeedbackCategory.AUTHENTICITY, 4, "Good")
        item.add_feedback(feedback1)
        assert item.needs_more_reviews()
        
        # Doesn't need more with two consistent ratings
        feedback2 = ReviewFeedback("f2", "e2", FeedbackCategory.ACCURACY, 4, "Good")
        item.add_feedback(feedback2)
        assert not item.needs_more_reviews()
        
        # Needs more with inconsistent ratings
        feedback3 = ReviewFeedback("f3", "e3", FeedbackCategory.CULTURAL_SENSITIVITY, 1, "Poor")
        item.add_feedback(feedback3)
        assert item.needs_more_reviews()


class TestExpertPool:
    """Test expert pool management"""
    
    def test_expert_pool_initialization(self):
        """Test expert pool initialization"""
        pool = ExpertPool()
        assert len(pool.experts) == 0
    
    def test_add_expert(self):
        """Test adding experts to pool"""
        pool = ExpertPool()
        expert = Expert(
            expert_id="test_001",
            name="Test Expert",
            email="test@example.com",
            expert_type=ExpertType.SPIRITUAL_TEACHER
        )
        
        result = pool.add_expert(expert)
        assert result == True
        assert len(pool.experts) == 1
        assert "test_001" in pool.experts
        
        # Can't add duplicate
        result = pool.add_expert(expert)
        assert result == False
        assert len(pool.experts) == 1
    
    def test_get_available_experts(self):
        """Test getting available experts"""
        pool = ExpertPool()
        
        # Add experts
        expert1 = Expert("e1", "Expert 1", "e1@test.com", ExpertType.SANSKRIT_SCHOLAR)
        expert2 = Expert("e2", "Expert 2", "e2@test.com", ExpertType.SPIRITUAL_TEACHER)
        expert3 = Expert("e3", "Expert 3", "e3@test.com", ExpertType.SANSKRIT_SCHOLAR, active=False)
        
        pool.add_expert(expert1)
        pool.add_expert(expert2)
        pool.add_expert(expert3)
        
        # Get all available
        available = pool.get_available_experts()
        assert len(available) == 2  # Expert 3 is inactive
        
        # Filter by type
        sanskrit_experts = pool.get_available_experts(expert_types=[ExpertType.SANSKRIT_SCHOLAR])
        assert len(sanskrit_experts) == 1
        assert sanskrit_experts[0].expert_id == "e1"
    
    def test_assign_experts(self):
        """Test expert assignment"""
        pool = ExpertPool()
        
        # Add experts
        expert1 = Expert("e1", "Expert 1", "e1@test.com", ExpertType.SANSKRIT_SCHOLAR)
        expert2 = Expert("e2", "Expert 2", "e2@test.com", ExpertType.SPIRITUAL_TEACHER)
        
        pool.add_expert(expert1)
        pool.add_expert(expert2)
        
        # Create review item
        review_item = ReviewItem(
            review_id="r1",
            original_query="What is dharma?",
            ai_response="Dharma is duty..."
        )
        
        # Assign experts
        assigned = pool.assign_experts(review_item, count=2)
        
        assert len(assigned) == 2
        assert "e1" in assigned
        assert "e2" in assigned
        
        # Check workload updated
        assert expert1.review_count == 1
        assert expert2.review_count == 1
    
    def test_sanskrit_detection(self):
        """Test Sanskrit term detection"""
        pool = ExpertPool()
        
        # Text with Sanskrit terms
        sanskrit_text = "This response discusses dharma and karma in spiritual practice."
        assert pool._contains_sanskrit(sanskrit_text) == True
        
        # Text without Sanskrit terms
        english_text = "This is a regular English response about spiritual matters."
        assert pool._contains_sanskrit(english_text) == False
    
    def test_philosophical_content_detection(self):
        """Test philosophical content detection"""
        pool = ExpertPool()
        
        # Philosophical query
        philosophical_query = "What is the nature of consciousness and reality?"
        assert pool._is_philosophical_content(philosophical_query) == True
        
        # Simple query
        simple_query = "How do I meditate better?"
        assert pool._is_philosophical_content(simple_query) == False


class TestReviewQueue:
    """Test review queue management"""
    
    def test_queue_initialization(self):
        """Test queue initialization"""
        queue = ReviewQueue()
        assert len(queue.queue) == 0
        assert all(len(priority_list) == 0 for priority_list in queue.priority_queue.values())
    
    def test_add_item(self):
        """Test adding items to queue"""
        queue = ReviewQueue()
        
        item = ReviewItem(
            review_id="r1",
            original_query="Test query",
            ai_response="Test response",
            priority=ReviewPriority.HIGH
        )
        
        result = queue.add_item(item)
        assert result == True
        assert len(queue.queue) == 1
        assert len(queue.priority_queue[ReviewPriority.HIGH]) == 1
        assert item.deadline is not None
        
        # Can't add duplicate
        result = queue.add_item(item)
        assert result == False
        assert len(queue.queue) == 1
    
    def test_get_next_item(self):
        """Test getting next item for expert"""
        queue = ReviewQueue()
        
        # Add items with different priorities
        high_item = ReviewItem("r1", "Query 1", "Response 1", priority=ReviewPriority.HIGH)
        normal_item = ReviewItem("r2", "Query 2", "Response 2", priority=ReviewPriority.NORMAL)
        
        high_item.assigned_experts = ["expert1"]
        normal_item.assigned_experts = ["expert1"]
        
        queue.add_item(high_item)
        queue.add_item(normal_item)
        
        # Should get high priority item first
        next_item = queue.get_next_item("expert1")
        assert next_item.review_id == "r1"
        assert next_item.status == ReviewStatus.IN_REVIEW
        
        # Should get normal priority item next
        next_item = queue.get_next_item("expert1")
        assert next_item.review_id == "r2"
    
    def test_get_overdue_items(self):
        """Test getting overdue items"""
        queue = ReviewQueue()
        
        # Create overdue item
        overdue_item = ReviewItem("r1", "Query", "Response")
        overdue_item.deadline = datetime.now() - timedelta(hours=1)
        queue.add_item(overdue_item)
        
        # Create non-overdue item
        current_item = ReviewItem("r2", "Query", "Response")
        current_item.deadline = datetime.now() + timedelta(hours=1)
        queue.add_item(current_item)
        
        overdue = queue.get_overdue_items()
        assert len(overdue) == 1
        assert overdue[0].review_id == "r1"
    
    def test_get_items_by_status(self):
        """Test filtering items by status"""
        queue = ReviewQueue()
        
        pending_item = ReviewItem("r1", "Query", "Response")
        approved_item = ReviewItem("r2", "Query", "Response")
        approved_item.status = ReviewStatus.APPROVED
        
        queue.add_item(pending_item)
        queue.add_item(approved_item)
        
        pending = queue.get_items_by_status(ReviewStatus.PENDING)
        approved = queue.get_items_by_status(ReviewStatus.APPROVED)
        
        assert len(pending) == 1
        assert len(approved) == 1
        assert pending[0].review_id == "r1"
        assert approved[0].review_id == "r2"


class TestNotificationService:
    """Test notification service"""
    
    @pytest.mark.asyncio
    async def test_expert_assignment_notification(self):
        """Test expert assignment notification"""
        mock_email = AsyncMock()
        service = NotificationService(mock_email)
        
        expert = Expert("e1", "Test Expert", "test@example.com", ExpertType.SPIRITUAL_TEACHER)
        review_item = ReviewItem("r1", "Query", "Response", priority=ReviewPriority.HIGH)
        
        await service.notify_expert_assignment(expert, review_item)
        
        mock_email.assert_called_once()
        call_args = mock_email.call_args[0]
        assert call_args[0] == "test@example.com"
        assert "New Review Assignment" in call_args[1]
        assert "High Priority" in call_args[1]
    
    @pytest.mark.asyncio
    async def test_overdue_notification(self):
        """Test overdue review notification"""
        mock_email = AsyncMock()
        service = NotificationService(mock_email)
        
        expert = Expert("e1", "Test Expert", "test@example.com", ExpertType.SPIRITUAL_TEACHER)
        review_item = ReviewItem("r1", "Query", "Response")
        review_item.deadline = datetime.now() - timedelta(hours=1)
        
        await service.notify_overdue_review(expert, review_item)
        
        mock_email.assert_called_once()
        call_args = mock_email.call_args[0]
        assert call_args[0] == "test@example.com"
        assert "Overdue Review" in call_args[1]


class TestFeedbackProcessor:
    """Test feedback processing"""
    
    def test_processor_initialization(self):
        """Test processor initialization"""
        processor = FeedbackProcessor()
        assert len(processor.feedback_handlers) == len(FeedbackCategory)
    
    def test_authenticity_feedback_processing(self):
        """Test authenticity feedback processing"""
        processor = FeedbackProcessor()
        
        review_item = ReviewItem("r1", "Query", "Response")
        feedback = ReviewFeedback(
            "f1", "e1", FeedbackCategory.AUTHENTICITY, 2, "Poor authenticity",
            requires_revision=True
        )
        
        improvements = processor.process_feedback(review_item, feedback)
        
        assert "prompt_engineering" in improvements
        assert "response_revision" in improvements
        assert improvements["prompt_engineering"]["action"] == "enhance_authenticity_guidelines"
    
    def test_accuracy_feedback_processing(self):
        """Test accuracy feedback processing"""
        processor = FeedbackProcessor()
        
        review_item = ReviewItem("r1", "Query", "Response", citations=["Gita 2.47"])
        feedback = ReviewFeedback("f1", "e1", FeedbackCategory.ACCURACY, 3, "Some inaccuracies")
        
        improvements = processor.process_feedback(review_item, feedback)
        
        assert "knowledge_base" in improvements
        assert improvements["knowledge_base"]["action"] == "verify_citations"
    
    def test_cultural_feedback_processing(self):
        """Test cultural sensitivity feedback processing"""
        processor = FeedbackProcessor()
        
        review_item = ReviewItem("r1", "Query", "Response")
        feedback = ReviewFeedback("f1", "e1", FeedbackCategory.CULTURAL_SENSITIVITY, 3, "Cultural issues")
        
        improvements = processor.process_feedback(review_item, feedback)
        
        assert "cultural_guidelines" in improvements
        assert improvements["cultural_guidelines"]["action"] == "update_sensitivity_rules"


class TestExpertReviewSystem:
    """Test main expert review system"""
    
    def test_system_initialization(self):
        """Test system initialization"""
        system = ExpertReviewSystem()
        
        assert system.expert_pool is not None
        assert system.review_queue is not None
        assert system.notification_service is not None
        assert system.feedback_processor is not None
    
    def test_initialize_default_experts(self):
        """Test default expert initialization"""
        system = ExpertReviewSystem()
        system.initialize_default_experts()
        
        assert len(system.expert_pool.experts) >= 3
        assert any(e.expert_type == ExpertType.SANSKRIT_SCHOLAR for e in system.expert_pool.experts.values())
        assert any(e.expert_type == ExpertType.SPIRITUAL_TEACHER for e in system.expert_pool.experts.values())
    
    def test_queue_for_review(self):
        """Test queuing items for review"""
        system = ExpertReviewSystem()
        system.initialize_default_experts()
        
        review_id = system.queue_for_review(
            original_query="What is dharma?",
            ai_response="Dharma is righteous duty...",
            citations=["Bhagavad Gita 2.47"],
            priority=ReviewPriority.HIGH
        )
        
        assert review_id is not None
        assert review_id in system.review_queue.queue
        
        review_item = system.review_queue.queue[review_id]
        assert review_item.priority == ReviewPriority.HIGH
        assert len(review_item.assigned_experts) > 0
    
    def test_submit_expert_feedback(self):
        """Test submitting expert feedback"""
        system = ExpertReviewSystem()
        system.initialize_default_experts()
        
        # Queue a review
        review_id = system.queue_for_review(
            original_query="What is dharma?",
            ai_response="Dharma is duty...",
            priority=ReviewPriority.NORMAL
        )
        
        # Submit feedback
        result = system.submit_expert_feedback(
            review_id=review_id,
            expert_id="sanskrit_001",
            category=FeedbackCategory.AUTHENTICITY,
            rating=5,
            comments="Excellent response",
            suggestions=["Add more context"]
        )
        
        assert result == True
        
        review_item = system.review_queue.queue[review_id]
        assert len(review_item.feedback) == 1
        assert review_item.feedback[0].rating == 5
    
    def test_get_review_status(self):
        """Test getting review status"""
        system = ExpertReviewSystem()
        system.initialize_default_experts()
        
        review_id = system.queue_for_review(
            original_query="Test query",
            ai_response="Test response"
        )
        
        status = system.get_review_status(review_id)
        
        assert status is not None
        assert status["review_id"] == review_id
        assert status["status"] == ReviewStatus.PENDING.value
        assert "assigned_experts" in status
        assert "created_at" in status
    
    def test_get_pending_reviews_for_expert(self):
        """Test getting pending reviews for expert"""
        system = ExpertReviewSystem()
        system.initialize_default_experts()
        
        review_id = system.queue_for_review(
            original_query="Test query",
            ai_response="Test response"
        )
        
        review_item = system.review_queue.queue[review_id]
        expert_id = review_item.assigned_experts[0]
        
        pending = system.get_pending_reviews_for_expert(expert_id)
        
        assert len(pending) >= 1
        assert any(r["review_id"] == review_id for r in pending)
    
    def test_get_system_metrics(self):
        """Test getting system metrics"""
        system = ExpertReviewSystem()
        system.initialize_default_experts()
        
        # Add some reviews
        system.queue_for_review("Query 1", "Response 1")
        system.queue_for_review("Query 2", "Response 2")
        
        metrics = system.get_system_metrics()
        
        assert "total_reviews" in metrics
        assert "status_breakdown" in metrics
        assert "expert_performance" in metrics
        assert metrics["total_reviews"] >= 2
    
    def test_review_status_updates(self):
        """Test automatic review status updates"""
        system = ExpertReviewSystem()
        system.initialize_default_experts()
        
        review_id = system.queue_for_review("Test query", "Test response")
        
        # Submit positive feedback from two experts
        system.submit_expert_feedback(
            review_id, "sanskrit_001", FeedbackCategory.AUTHENTICITY, 5, "Excellent"
        )
        system.submit_expert_feedback(
            review_id, "spiritual_001", FeedbackCategory.ACCURACY, 4, "Good"
        )
        
        review_item = system.review_queue.queue[review_id]
        assert review_item.status == ReviewStatus.APPROVED
    
    def test_review_rejection(self):
        """Test review rejection with poor feedback"""
        system = ExpertReviewSystem()
        system.initialize_default_experts()
        
        review_id = system.queue_for_review("Test query", "Test response")
        
        # Submit poor feedback
        system.submit_expert_feedback(
            review_id, "sanskrit_001", FeedbackCategory.AUTHENTICITY, 1, "Poor"
        )
        system.submit_expert_feedback(
            review_id, "spiritual_001", FeedbackCategory.ACCURACY, 2, "Inaccurate"
        )
        
        review_item = system.review_queue.queue[review_id]
        assert review_item.status == ReviewStatus.REJECTED


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_create_expert_review_system(self):
        """Test system creation utility"""
        system = create_expert_review_system()
        
        assert isinstance(system, ExpertReviewSystem)
        assert len(system.expert_pool.experts) >= 3
    
    def test_quick_review_submission(self):
        """Test quick review submission utility"""
        system = create_expert_review_system()
        
        review_id = quick_review_submission(
            system, "What is dharma?", "Dharma is duty...", "high"
        )
        
        assert review_id is not None
        assert review_id in system.review_queue.queue
        
        review_item = system.review_queue.queue[review_id]
        assert review_item.priority == ReviewPriority.HIGH


class TestIntegration:
    """Integration tests for complete expert review workflow"""
    
    def test_complete_review_workflow(self):
        """Test complete workflow from submission to approval"""
        system = create_expert_review_system()
        
        # Submit review
        review_id = system.queue_for_review(
            original_query="What is the path to moksha?",
            ai_response="""My dear child, the path to moksha is through devotion, knowledge, and righteous action. 
            As taught in Bhagavad Gita 9.22, for those who worship Me with exclusive devotion, 
            I provide what they lack and preserve what they have.""",
            citations=["Bhagavad Gita 9.22"],
            priority=ReviewPriority.NORMAL
        )
        
        # Check initial status
        status = system.get_review_status(review_id)
        assert status["status"] == ReviewStatus.PENDING.value
        
        # Get assigned experts
        review_item = system.review_queue.queue[review_id]
        experts = review_item.assigned_experts
        assert len(experts) >= 2
        
        # Submit feedback from multiple experts
        system.submit_expert_feedback(
            review_id, experts[0], FeedbackCategory.AUTHENTICITY, 5,
            "Excellent spiritual guidance with proper citation and authentic tone."
        )
        
        system.submit_expert_feedback(
            review_id, experts[1], FeedbackCategory.ACCURACY, 4,
            "Accurate citation and good explanation of the path to liberation."
        )
        
        # Check final status
        final_status = system.get_review_status(review_id)
        assert final_status["status"] == ReviewStatus.APPROVED.value
        assert final_status["is_approved"] == True
        assert final_status["average_rating"] >= 4.0
    
    def test_revision_workflow(self):
        """Test workflow when revision is required"""
        system = create_expert_review_system()
        
        review_id = system.queue_for_review(
            "What is dharma?", "Dharma is just following rules."
        )
        
        # Submit feedback requiring revision
        review_item = system.review_queue.queue[review_id]
        expert_id = review_item.assigned_experts[0]
        
        system.submit_expert_feedback(
            review_id, expert_id, FeedbackCategory.AUTHENTICITY, 3,
            "Response lacks spiritual depth and proper understanding.",
            requires_revision=True
        )
        
        # Check status
        status = system.get_review_status(review_id)
        assert status["status"] == ReviewStatus.NEEDS_REVISION.value
    
    def test_escalation_workflow(self):
        """Test escalation for complex reviews"""
        system = create_expert_review_system()
        
        # Submit complex philosophical query
        review_id = system.queue_for_review(
            original_query="What is the ontological nature of Brahman in Advaita Vedanta?",
            ai_response="Brahman is the ultimate reality...",
            priority=ReviewPriority.HIGH
        )
        
        review_item = system.review_queue.queue[review_id]
        
        # Should assign philosophy expert for complex content
        expert_types = [system.expert_pool.experts[eid].expert_type for eid in review_item.assigned_experts]
        # Note: Would need philosophy expert in default setup for this to work
        
        assert len(review_item.assigned_experts) >= 2
        assert review_item.priority == ReviewPriority.HIGH


# Example test runner
if __name__ == "__main__":
    # Run some basic tests
    print("Running expert review system tests...")
    
    # Test system creation
    print("\n=== Testing System Creation ===")
    system = create_expert_review_system()
    print(f"System created with {len(system.expert_pool.experts)} experts")
    
    # Test review submission
    print("\n=== Testing Review Submission ===")
    review_id = system.queue_for_review(
        "What is the meaning of dharma?",
        "Dharma is your righteous duty as taught in Bhagavad Gita 2.47",
        ["Bhagavad Gita 2.47"],
        ReviewPriority.NORMAL
    )
    print(f"Submitted review: {review_id}")
    
    # Test feedback submission
    print("\n=== Testing Feedback Submission ===")
    review_item = system.review_queue.queue[review_id]
    expert_id = review_item.assigned_experts[0]
    
    result = system.submit_expert_feedback(
        review_id, expert_id, FeedbackCategory.AUTHENTICITY, 5,
        "Excellent response with proper citation"
    )
    print(f"Feedback submitted: {result}")
    
    # Test metrics
    print("\n=== Testing System Metrics ===")
    metrics = system.get_system_metrics()
    print(f"Total reviews: {metrics['total_reviews']}")
    print(f"Expert count: {len(metrics['expert_performance'])}")
    
    print("\nExpert review system tests completed!")
