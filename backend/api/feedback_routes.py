"""
API routes for feedback collection and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query as QueryParam
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database.connection import get_db
from backend.models.schemas import (
    FeedbackCreate, FeedbackResponse, FeedbackCommentCreate,
    FeedbackTagCreate, FeedbackCommentResponse, FeedbackTagResponse,
    FeedbackStats, FeedbackUpdate, BulkFeedbackReview,
    FeedbackForReview
)
from backend.models.database import ReviewStatus
from backend.services.feedback_service import FeedbackService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Create new feedback for a query response

    - **response_id**: ID of the response to provide feedback on
    - **rating**: Rating from 1 (very bad) to 5 (excellent)
    - **is_helpful**: Whether the response was helpful
    - **is_accurate**: Whether the response was accurate
    - **is_complete**: Whether the response was complete
    """
    try:
        service = FeedbackService(db)
        result = service.create_feedback(feedback)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create feedback"
        )


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db)
):
    """Get feedback by ID"""
    service = FeedbackService(db)
    feedback = service.get_feedback(feedback_id)

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with id {feedback_id} not found"
        )

    return feedback


@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: int,
    update: FeedbackUpdate,
    db: Session = Depends(get_db)
):
    """Update feedback review status"""
    try:
        service = FeedbackService(db)
        result = service.update_review_status(feedback_id, update.review_status)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update feedback"
        )


@router.post("/{feedback_id}/comments", response_model=FeedbackCommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    feedback_id: int,
    comment: FeedbackCommentCreate,
    db: Session = Depends(get_db)
):
    """Add a comment to feedback"""
    try:
        service = FeedbackService(db)
        result = service.add_comment(feedback_id, comment)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add comment"
        )


@router.post("/{feedback_id}/tags", response_model=FeedbackTagResponse, status_code=status.HTTP_201_CREATED)
def add_tag(
    feedback_id: int,
    tag: FeedbackTagCreate,
    db: Session = Depends(get_db)
):
    """Add a tag to feedback"""
    try:
        service = FeedbackService(db)
        result = service.add_tag(feedback_id, tag)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding tag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add tag"
        )


@router.get("/stats/summary", response_model=FeedbackStats)
def get_feedback_stats(
    days: Optional[int] = QueryParam(default=None, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated feedback statistics

    - **days**: Optional - limit to feedbacks from last N days
    """
    try:
        service = FeedbackService(db)
        stats = service.get_feedback_statistics(days=days)
        return stats
    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get feedback statistics"
        )


@router.get("/review/pending")
def get_pending_reviews(
    limit: int = QueryParam(default=50, ge=1, le=200),
    min_rating: Optional[int] = QueryParam(default=None, ge=1, le=5),
    max_confidence: Optional[float] = QueryParam(default=None, ge=0, le=1),
    db: Session = Depends(get_db)
):
    """
    Get feedbacks pending review

    Returns feedbacks that match any of these criteria:
    - Low rating (below threshold)
    - Low confidence score
    - Explicitly marked for review

    - **limit**: Maximum number of feedbacks to return
    - **min_rating**: Optional - override minimum rating threshold
    - **max_confidence**: Optional - override confidence threshold
    """
    try:
        service = FeedbackService(db)
        results = service.get_feedbacks_for_review(
            limit=limit,
            min_rating=min_rating,
            max_confidence=max_confidence
        )

        # Format response
        feedbacks = []
        for feedback, response, query in results:
            feedbacks.append({
                "feedback_id": feedback.id,
                "response_id": response.id,
                "query_id": query.id,
                "query_text": query.query_text,
                "response_text": response.response_text,
                "rating": feedback.rating.value,
                "confidence_score": response.confidence_score,
                "review_status": feedback.review_status.value,
                "created_at": feedback.created_at,
                "is_helpful": feedback.is_helpful,
                "is_accurate": feedback.is_accurate,
                "is_complete": feedback.is_complete
            })

        return {
            "count": len(feedbacks),
            "feedbacks": feedbacks
        }
    except Exception as e:
        logger.error(f"Error getting pending reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pending reviews"
        )


@router.post("/review/bulk-update")
def bulk_update_reviews(
    update: BulkFeedbackReview,
    db: Session = Depends(get_db)
):
    """
    Bulk update review status for multiple feedbacks

    - **feedback_ids**: List of feedback IDs to update
    - **review_status**: New status to apply to all feedbacks
    """
    try:
        service = FeedbackService(db)
        updated_count = service.bulk_update_review_status(
            update.feedback_ids,
            update.review_status
        )

        return {
            "success": True,
            "updated_count": updated_count,
            "message": f"Successfully updated {updated_count} feedbacks"
        }
    except Exception as e:
        logger.error(f"Error bulk updating reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk update reviews"
        )


@router.get("/analysis/low-confidence")
def get_low_confidence_responses(
    confidence_threshold: Optional[float] = QueryParam(default=None, ge=0, le=1),
    limit: int = QueryParam(default=100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get responses with low confidence scores

    - **confidence_threshold**: Optional - override default threshold
    - **limit**: Maximum number of responses to return
    """
    try:
        service = FeedbackService(db)
        results = service.get_low_confidence_responses(
            confidence_threshold=confidence_threshold,
            limit=limit
        )

        responses = []
        for response, query in results:
            responses.append({
                "response_id": response.id,
                "query_id": query.id,
                "query_text": query.query_text,
                "response_text": response.response_text,
                "confidence_score": response.confidence_score,
                "model_version": response.model_version,
                "created_at": response.created_at
            })

        return {
            "count": len(responses),
            "threshold": confidence_threshold,
            "responses": responses
        }
    except Exception as e:
        logger.error(f"Error getting low confidence responses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get low confidence responses"
        )


@router.get("/analysis/negative")
def get_negative_feedbacks(
    rating_threshold: Optional[int] = QueryParam(default=None, ge=1, le=5),
    days: int = QueryParam(default=30, ge=1, le=365),
    limit: int = QueryParam(default=100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get negative feedbacks within time period

    - **rating_threshold**: Optional - override default threshold
    - **days**: Number of days to look back
    - **limit**: Maximum number of feedbacks to return
    """
    try:
        service = FeedbackService(db)
        feedbacks = service.get_negative_feedbacks(
            rating_threshold=rating_threshold,
            days=days,
            limit=limit
        )

        return {
            "count": len(feedbacks),
            "threshold": rating_threshold,
            "days": days,
            "feedbacks": [
                {
                    "feedback_id": f.id,
                    "response_id": f.response_id,
                    "rating": f.rating.value,
                    "review_status": f.review_status.value,
                    "created_at": f.created_at
                }
                for f in feedbacks
            ]
        }
    except Exception as e:
        logger.error(f"Error getting negative feedbacks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get negative feedbacks"
        )


@router.get("/analysis/trends")
def get_feedback_trends(
    days: int = QueryParam(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Analyze feedback trends over time

    - **days**: Number of days to analyze
    """
    try:
        service = FeedbackService(db)
        trends = service.analyze_feedback_trends(days=days)
        return trends
    except Exception as e:
        logger.error(f"Error analyzing feedback trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze feedback trends"
        )


@router.get("/training/candidates")
def get_training_candidates(
    min_rating: int = QueryParam(default=4, ge=1, le=5),
    include_reviewed_only: bool = QueryParam(default=True),
    db: Session = Depends(get_db)
):
    """
    Get high-quality feedbacks suitable for model training

    - **min_rating**: Minimum rating for training data
    - **include_reviewed_only**: Only include reviewed and approved feedbacks
    """
    try:
        service = FeedbackService(db)
        results = service.get_feedbacks_for_training(
            min_rating=min_rating,
            include_reviewed_only=include_reviewed_only
        )

        training_data = []
        for feedback, response, query in results:
            training_data.append({
                "feedback_id": feedback.id,
                "query_text": query.query_text,
                "response_text": response.response_text,
                "rating": feedback.rating.value,
                "confidence_score": response.confidence_score,
                "model_version": response.model_version
            })

        return {
            "count": len(training_data),
            "min_rating": min_rating,
            "training_data": training_data
        }
    except Exception as e:
        logger.error(f"Error getting training candidates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get training candidates"
        )
