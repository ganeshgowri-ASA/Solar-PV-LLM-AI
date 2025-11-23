"""
Tests for feedback service
"""
import pytest
from backend.services.feedback_service import FeedbackService
from backend.models.database import UserFeedback, QueryResponse, Query, ReviewStatus, FeedbackRating
from backend.models.schemas import FeedbackCreate


def test_create_feedback(test_db):
    """Test creating feedback"""
    # Create query and response first
    query = Query(query_text="Test query")
    test_db.add(query)
    test_db.commit()
    test_db.refresh(query)

    response = QueryResponse(
        query_id=query.id,
        response_text="Test response",
        model_version="test-v1",
        confidence_score=0.95
    )
    test_db.add(response)
    test_db.commit()
    test_db.refresh(response)

    # Create feedback
    service = FeedbackService(test_db)
    feedback_data = FeedbackCreate(
        response_id=response.id,
        rating=FeedbackRating.EXCELLENT,
        is_helpful=True
    )

    feedback = service.create_feedback(feedback_data)

    assert feedback.id is not None
    assert feedback.response_id == response.id
    assert feedback.rating == FeedbackRating.EXCELLENT
    assert feedback.is_helpful is True
    assert feedback.review_status == ReviewStatus.PENDING


def test_get_low_confidence_responses(test_db):
    """Test getting low confidence responses"""
    # Create query and low confidence response
    query = Query(query_text="Test query")
    test_db.add(query)
    test_db.commit()

    response = QueryResponse(
        query_id=query.id,
        response_text="Test response",
        model_version="test-v1",
        confidence_score=0.65  # Low confidence
    )
    test_db.add(response)
    test_db.commit()

    # Get low confidence responses
    service = FeedbackService(test_db)
    results = service.get_low_confidence_responses(confidence_threshold=0.8)

    assert len(results) > 0
    assert results[0][0].confidence_score <= 0.8


def test_get_feedback_statistics(test_db):
    """Test feedback statistics calculation"""
    # Create test data
    query = Query(query_text="Test query")
    test_db.add(query)
    test_db.commit()

    response = QueryResponse(
        query_id=query.id,
        response_text="Test response",
        model_version="test-v1"
    )
    test_db.add(response)
    test_db.commit()

    # Create multiple feedbacks
    feedbacks = [
        UserFeedback(response_id=response.id, rating=FeedbackRating.EXCELLENT),
        UserFeedback(response_id=response.id, rating=FeedbackRating.GOOD),
        UserFeedback(response_id=response.id, rating=FeedbackRating.BAD),
    ]

    # Note: We need different response IDs, so let's adjust
    for i, fb in enumerate(feedbacks):
        resp = QueryResponse(
            query_id=query.id,
            response_text=f"Response {i}",
            model_version="test-v1"
        )
        test_db.add(resp)
        test_db.commit()
        fb.response_id = resp.id
        test_db.add(fb)

    test_db.commit()

    # Get statistics
    service = FeedbackService(test_db)
    stats = service.get_feedback_statistics()

    assert stats.total_count == 3
    assert stats.avg_rating > 0
    assert stats.positive_feedback_rate >= 0


def test_bulk_update_review_status(test_db):
    """Test bulk updating review status"""
    # Create test feedbacks
    query = Query(query_text="Test query")
    test_db.add(query)
    test_db.commit()

    feedback_ids = []
    for i in range(3):
        response = QueryResponse(
            query_id=query.id,
            response_text=f"Response {i}",
            model_version="test-v1"
        )
        test_db.add(response)
        test_db.commit()

        feedback = UserFeedback(
            response_id=response.id,
            rating=FeedbackRating.GOOD
        )
        test_db.add(feedback)
        test_db.commit()
        feedback_ids.append(feedback.id)

    # Bulk update
    service = FeedbackService(test_db)
    updated_count = service.bulk_update_review_status(
        feedback_ids,
        ReviewStatus.APPROVED
    )

    assert updated_count == 3

    # Verify updates
    for fb_id in feedback_ids:
        fb = test_db.query(UserFeedback).filter(UserFeedback.id == fb_id).first()
        assert fb.review_status == ReviewStatus.APPROVED
        assert fb.reviewed_at is not None
