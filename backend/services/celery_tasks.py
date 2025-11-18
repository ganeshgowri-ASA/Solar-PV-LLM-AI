"""
Celery tasks for async job scheduling and execution
"""
from celery import Celery
from celery.schedules import crontab
import logging
from typing import Dict, Any

from backend.config import get_settings
from backend.database.connection import get_db_context
from backend.services.retraining_service import RetrainingService

logger = logging.getLogger(__name__)

# Initialize Celery
settings = get_settings()
celery_app = Celery(
    'solar_pv_tasks',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Celery configuration
celery_app.conf.update(
    task_track_started=settings.celery_task_track_started,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


# ============================================
# Retraining Tasks
# ============================================

@celery_app.task(name='check_retraining_trigger', bind=True)
def check_retraining_trigger(self):
    """
    Periodic task to check if retraining should be triggered

    Runs on schedule (configured via RETRAINING_SCHEDULE_CRON)
    """
    logger.info("Running scheduled retraining check")

    try:
        with get_db_context() as db:
            retraining_service = RetrainingService(db)

            # Check if retraining is needed
            recommendation = retraining_service.should_trigger_retraining()

            if recommendation["should_retrain"]:
                logger.info(f"Triggering retraining: {recommendation['reason']}")

                # Trigger async retraining task
                result = execute_retraining.delay(
                    model_name=f"solar-pv-model-auto",
                    training_type="lora"
                )

                return {
                    "triggered": True,
                    "reason": recommendation["reason"],
                    "task_id": result.id,
                    "metrics": recommendation["metrics"]
                }
            else:
                logger.info("Retraining not needed at this time")
                return {
                    "triggered": False,
                    "reason": recommendation["reason"],
                    "metrics": recommendation["metrics"]
                }

    except Exception as e:
        logger.error(f"Error in retraining check: {e}")
        raise


@celery_app.task(name='execute_retraining', bind=True)
def execute_retraining(
    self,
    model_name: str,
    training_type: str = "lora",
    min_rating: int = 4
) -> Dict[str, Any]:
    """
    Execute model retraining pipeline

    Args:
        model_name: Name for the trained model
        training_type: Type of training (lora, full, vector_update)
        min_rating: Minimum rating for training examples

    Returns:
        Training result dict
    """
    logger.info(f"Starting retraining task: {model_name}")

    try:
        # Update task state to STARTED
        self.update_state(
            state='STARTED',
            meta={'stage': 'initializing', 'progress': 0}
        )

        with get_db_context() as db:
            retraining_service = RetrainingService(db)

            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'stage': 'preparing_data', 'progress': 25}
            )

            # Execute retraining pipeline
            result = retraining_service.trigger_retraining_pipeline(
                model_name=model_name,
                training_type=training_type,
                min_rating=min_rating
            )

            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'stage': 'training_complete', 'progress': 100}
            )

            logger.info(f"Retraining task completed: {result}")
            return result

    except Exception as e:
        logger.error(f"Retraining task failed: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise


@celery_app.task(name='deploy_trained_model', bind=True)
def deploy_trained_model(self, training_run_id: int) -> Dict[str, Any]:
    """
    Deploy a trained model to production

    Args:
        training_run_id: ID of the training run to deploy

    Returns:
        Deployment result dict
    """
    logger.info(f"Starting model deployment task for training run {training_run_id}")

    try:
        with get_db_context() as db:
            retraining_service = RetrainingService(db)

            # Deploy model
            deployment = retraining_service.deploy_model(
                training_run_id=training_run_id,
                deactivate_current=True
            )

            result = {
                "success": True,
                "deployment_id": deployment.id,
                "model_version": deployment.model_version,
                "deployed_at": deployment.deployed_at.isoformat()
            }

            logger.info(f"Model deployment completed: {result}")
            return result

    except Exception as e:
        logger.error(f"Model deployment failed: {e}")
        raise


# ============================================
# Vector Store Update Tasks
# ============================================

@celery_app.task(name='update_vector_store', bind=True)
def update_vector_store(self, documents: list) -> Dict[str, Any]:
    """
    Update vector store with new documents (async)

    Args:
        documents: List of documents to add

    Returns:
        Update result dict
    """
    logger.info(f"Starting vector store update task with {len(documents)} documents")

    try:
        from backend.services.rag_service import RAGService

        self.update_state(
            state='PROGRESS',
            meta={'stage': 'embedding', 'progress': 50}
        )

        rag_service = RAGService()

        # Add documents with zero downtime
        result = rag_service.update_documents_zero_downtime(documents)

        self.update_state(
            state='PROGRESS',
            meta={'stage': 'complete', 'progress': 100}
        )

        logger.info(f"Vector store update completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Vector store update failed: {e}")
        raise


# ============================================
# Metrics and Monitoring Tasks
# ============================================

@celery_app.task(name='collect_system_metrics')
def collect_system_metrics():
    """
    Periodic task to collect system metrics

    Runs every hour to track performance metrics
    """
    logger.info("Collecting system metrics")

    try:
        from backend.models.database import SystemMetric, QueryResponse, UserFeedback
        from sqlalchemy import func
        from datetime import datetime, timedelta

        with get_db_context() as db:
            # Calculate metrics for the last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)

            # Query metrics
            queries_count = db.query(QueryResponse).filter(
                QueryResponse.created_at >= one_hour_ago
            ).count()

            avg_response_time = db.query(
                func.avg(QueryResponse.latency_ms)
            ).filter(
                QueryResponse.created_at >= one_hour_ago
            ).scalar() or 0.0

            feedbacks_count = db.query(UserFeedback).filter(
                UserFeedback.created_at >= one_hour_ago
            ).count()

            avg_rating = db.query(
                func.avg(UserFeedback.rating)
            ).filter(
                UserFeedback.created_at >= one_hour_ago
            ).scalar()

            if avg_rating:
                avg_rating = float(avg_rating)
            else:
                avg_rating = 0.0

            # Calculate positive feedback rate
            positive_feedbacks = db.query(UserFeedback).filter(
                UserFeedback.created_at >= one_hour_ago,
                UserFeedback.rating >= 4
            ).count()

            positive_rate = positive_feedbacks / feedbacks_count if feedbacks_count > 0 else 0.0

            # Create metric record
            metric = SystemMetric(
                queries_count=queries_count,
                avg_response_time_ms=avg_response_time,
                feedbacks_count=feedbacks_count,
                avg_rating=avg_rating,
                positive_feedback_rate=positive_rate
            )

            db.add(metric)
            db.commit()

            logger.info(f"Collected metrics: queries={queries_count}, avg_rating={avg_rating}")

            return {
                "success": True,
                "queries_count": queries_count,
                "avg_rating": avg_rating
            }

    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        raise


# ============================================
# Celery Beat Schedule Configuration
# ============================================

celery_app.conf.beat_schedule = {
    'check-retraining-trigger': {
        'task': 'check_retraining_trigger',
        'schedule': crontab(
            minute='0',
            hour='2',
            day_of_week='0'  # Sunday at 2 AM
        ),
    },
    'collect-system-metrics': {
        'task': 'collect_system_metrics',
        'schedule': crontab(minute='0'),  # Every hour
    },
}


# ============================================
# Utility Functions
# ============================================

def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get status of a Celery task

    Args:
        task_id: Celery task ID

    Returns:
        Task status dict
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "state": result.state,
        "info": result.info,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None
    }


def cancel_task(task_id: str) -> bool:
    """
    Cancel a running task

    Args:
        task_id: Celery task ID

    Returns:
        True if cancellation was successful
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=celery_app)
    result.revoke(terminate=True)

    logger.info(f"Cancelled task {task_id}")
    return True
