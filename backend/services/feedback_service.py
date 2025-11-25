"""
Feedback collection and analysis service
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from backend.models.database import (
    UserFeedback, FeedbackComment, FeedbackTag, QueryResponse,
    Query, ReviewStatus, FeedbackRating
)
from backend.models.schemas import (
    FeedbackCreate, FeedbackCommentCreate, FeedbackTagCreate,
    FeedbackResponse, FeedbackStats, FeedbackForReview
)
from backend.config import get_settings

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for handling user feedback operations"""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def create_feedback(
        self,
        feedback_data: FeedbackCreate,
        user_id: Optional[int] = None
    ) -> UserFeedback:
        """Create new feedback entry"""
        logger.info(f"Creating feedback for response_id={feedback_data.response_id}")

        # Check if response exists
        response = self.db.query(QueryResponse).filter(
            QueryResponse.id == feedback_data.response_id
        ).first()

        if not response:
            raise ValueError(f"Response with id {feedback_data.response_id} not found")

        # Check if feedback already exists for this response
        existing = self.db.query(UserFeedback).filter(
            UserFeedback.response_id == feedback_data.response_id
        ).first()

        if existing:
            raise ValueError(f"Feedback already exists for response {feedback_data.response_id}")

        # Create feedback
        feedback = UserFeedback(
            response_id=feedback_data.response_id,
            user_id=user_id,
            rating=feedback_data.rating,
            is_helpful=feedback_data.is_helpful,
            is_accurate=feedback_data.is_accurate,
            is_complete=feedback_data.is_complete,
            review_status=ReviewStatus.PENDING
        )

        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)

        logger.info(f"Created feedback id={feedback.id}, rating={feedback.rating}")
        return feedback

    def add_comment(
        self,
        feedback_id: int,
        comment_data: FeedbackCommentCreate
    ) -> FeedbackComment:
        """Add comment to feedback"""
        logger.info(f"Adding comment to feedback_id={feedback_id}")

        # Verify feedback exists
        feedback = self.db.query(UserFeedback).filter(
            UserFeedback.id == feedback_id
        ).first()

        if not feedback:
            raise ValueError(f"Feedback with id {feedback_id} not found")

        comment = FeedbackComment(
            feedback_id=feedback_id,
            comment_text=comment_data.comment_text,
            comment_type=comment_data.comment_type
        )

        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)

        logger.info(f"Added comment id={comment.id}")
        return comment

    def add_tag(
        self,
        feedback_id: int,
        tag_data: FeedbackTagCreate
    ) -> FeedbackTag:
        """Add tag to feedback"""
        logger.info(f"Adding tag '{tag_data.tag_name}' to feedback_id={feedback_id}")

        # Verify feedback exists
        feedback = self.db.query(UserFeedback).filter(
            UserFeedback.id == feedback_id
        ).first()

        if not feedback:
            raise ValueError(f"Feedback with id {feedback_id} not found")

        # Check if tag already exists
        existing = self.db.query(FeedbackTag).filter(
            and_(
                FeedbackTag.feedback_id == feedback_id,
                FeedbackTag.tag_name == tag_data.tag_name
            )
        ).first()

        if existing:
            logger.warning(f"Tag '{tag_data.tag_name}' already exists for feedback {feedback_id}")
            return existing

        tag = FeedbackTag(
            feedback_id=feedback_id,
            tag_name=tag_data.tag_name,
            category=tag_data.category
        )

        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)

        logger.info(f"Added tag id={tag.id}")
        return tag

    def get_feedback(self, feedback_id: int) -> Optional[UserFeedback]:
        """Get feedback by ID"""
        return self.db.query(UserFeedback).filter(
            UserFeedback.id == feedback_id
        ).first()

    def update_review_status(
        self,
        feedback_id: int,
        status: ReviewStatus
    ) -> UserFeedback:
        """Update feedback review status"""
        logger.info(f"Updating feedback {feedback_id} status to {status}")

        feedback = self.get_feedback(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback with id {feedback_id} not found")

        feedback.review_status = status
        if status in [ReviewStatus.APPROVED, ReviewStatus.REJECTED]:
            feedback.reviewed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(feedback)

        logger.info(f"Updated feedback {feedback_id} status")
        return feedback

    def get_feedbacks_for_review(
        self,
        limit: int = 50,
        min_rating: Optional[int] = None,
        max_confidence: Optional[float] = None
    ) -> List[Tuple[UserFeedback, QueryResponse, Query]]:
        """
        Get feedbacks that need review based on criteria:
        - Low ratings
        - Low confidence scores
        - Pending review status
        """
        logger.info("Fetching feedbacks for review")

        # Build query
        query = self.db.query(UserFeedback, QueryResponse, Query).join(
            QueryResponse, UserFeedback.response_id == QueryResponse.id
        ).join(
            Query, QueryResponse.query_id == Query.id
        ).filter(
            UserFeedback.review_status == ReviewStatus.PENDING
        )

        # Apply filters
        conditions = []

        # Low rating filter
        if min_rating is None:
            min_rating = self.settings.feedback_negative_rating_threshold
        conditions.append(UserFeedback.rating <= min_rating)

        # Low confidence filter
        if max_confidence is None:
            max_confidence = self.settings.feedback_confidence_threshold
        conditions.append(
            or_(
                QueryResponse.confidence_score.is_(None),
                QueryResponse.confidence_score <= max_confidence
            )
        )

        # Apply OR condition (match any criteria)
        query = query.filter(or_(*conditions))

        # Order by created date (oldest first)
        query = query.order_by(UserFeedback.created_at.asc())

        # Limit results
        results = query.limit(limit).all()

        logger.info(f"Found {len(results)} feedbacks for review")
        return results

    def get_low_confidence_responses(
        self,
        confidence_threshold: Optional[float] = None,
        limit: int = 100
    ) -> List[Tuple[QueryResponse, Query]]:
        """Get responses with low confidence scores"""
        if confidence_threshold is None:
            confidence_threshold = self.settings.feedback_confidence_threshold

        logger.info(f"Fetching low confidence responses (threshold={confidence_threshold})")

        results = self.db.query(QueryResponse, Query).join(
            Query, QueryResponse.query_id == Query.id
        ).filter(
            or_(
                QueryResponse.confidence_score.is_(None),
                QueryResponse.confidence_score <= confidence_threshold
            )
        ).order_by(QueryResponse.created_at.desc()).limit(limit).all()

        logger.info(f"Found {len(results)} low confidence responses")
        return results

    def get_negative_feedbacks(
        self,
        rating_threshold: Optional[int] = None,
        days: int = 30,
        limit: int = 100
    ) -> List[UserFeedback]:
        """Get negative feedbacks within time period"""
        if rating_threshold is None:
            rating_threshold = self.settings.feedback_negative_rating_threshold

        logger.info(f"Fetching negative feedbacks (rating <= {rating_threshold})")

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        results = self.db.query(UserFeedback).filter(
            and_(
                UserFeedback.rating <= rating_threshold,
                UserFeedback.created_at >= cutoff_date
            )
        ).order_by(UserFeedback.created_at.desc()).limit(limit).all()

        logger.info(f"Found {len(results)} negative feedbacks")
        return results

    def get_feedback_statistics(
        self,
        days: Optional[int] = None
    ) -> FeedbackStats:
        """Get aggregated feedback statistics"""
        logger.info("Calculating feedback statistics")

        query = self.db.query(UserFeedback)

        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(UserFeedback.created_at >= cutoff_date)

        feedbacks = query.all()
        total_count = len(feedbacks)

        if total_count == 0:
            return FeedbackStats(
                total_count=0,
                avg_rating=0.0,
                rating_distribution={},
                positive_feedback_rate=0.0,
                pending_review_count=0
            )

        # Calculate average rating
        avg_rating = sum(f.rating.value for f in feedbacks) / total_count

        # Rating distribution
        rating_dist = {}
        for rating in FeedbackRating:
            count = sum(1 for f in feedbacks if f.rating == rating)
            rating_dist[rating.value] = count

        # Positive feedback rate (rating >= 4)
        positive_count = sum(1 for f in feedbacks if f.rating.value >= 4)
        positive_rate = positive_count / total_count

        # Pending review count
        pending_count = sum(
            1 for f in feedbacks if f.review_status == ReviewStatus.PENDING
        )

        stats = FeedbackStats(
            total_count=total_count,
            avg_rating=round(avg_rating, 2),
            rating_distribution=rating_dist,
            positive_feedback_rate=round(positive_rate, 2),
            pending_review_count=pending_count
        )

        logger.info(f"Statistics: {stats}")
        return stats

    def bulk_update_review_status(
        self,
        feedback_ids: List[int],
        status: ReviewStatus
    ) -> int:
        """Bulk update review status for multiple feedbacks"""
        logger.info(f"Bulk updating {len(feedback_ids)} feedbacks to {status}")

        updated = self.db.query(UserFeedback).filter(
            UserFeedback.id.in_(feedback_ids)
        ).update(
            {
                "review_status": status,
                "reviewed_at": datetime.utcnow() if status in [
                    ReviewStatus.APPROVED, ReviewStatus.REJECTED
                ] else None
            },
            synchronize_session=False
        )

        self.db.commit()

        logger.info(f"Updated {updated} feedbacks")
        return updated

    def get_feedbacks_for_training(
        self,
        min_rating: int = 4,
        include_reviewed_only: bool = True
    ) -> List[Tuple[UserFeedback, QueryResponse, Query]]:
        """
        Get high-quality feedbacks for model training
        - High ratings (positive examples)
        - Reviewed and approved
        """
        logger.info(f"Fetching feedbacks for training (min_rating={min_rating})")

        query = self.db.query(UserFeedback, QueryResponse, Query).join(
            QueryResponse, UserFeedback.response_id == QueryResponse.id
        ).join(
            Query, QueryResponse.query_id == Query.id
        ).filter(
            UserFeedback.rating >= min_rating
        )

        if include_reviewed_only:
            query = query.filter(
                UserFeedback.review_status == ReviewStatus.APPROVED
            )

        results = query.all()

        logger.info(f"Found {len(results)} feedbacks for training")
        return results

    def analyze_feedback_trends(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Analyze feedback trends over time"""
        logger.info(f"Analyzing feedback trends for last {days} days")

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get feedbacks grouped by day
        daily_stats = self.db.query(
            func.date(UserFeedback.created_at).label("date"),
            func.count(UserFeedback.id).label("count"),
            func.avg(UserFeedback.rating).label("avg_rating")
        ).filter(
            UserFeedback.created_at >= cutoff_date
        ).group_by(
            func.date(UserFeedback.created_at)
        ).order_by("date").all()

        trends = {
            "daily_stats": [
                {
                    "date": str(stat.date),
                    "count": stat.count,
                    "avg_rating": round(float(stat.avg_rating), 2)
                }
                for stat in daily_stats
            ],
            "total_feedbacks": sum(s.count for s in daily_stats),
            "overall_avg_rating": round(
                sum(s.avg_rating * s.count for s in daily_stats) /
                sum(s.count for s in daily_stats), 2
            ) if daily_stats else 0.0
        }

        logger.info(f"Trend analysis complete: {trends['total_feedbacks']} feedbacks")
        return trends
