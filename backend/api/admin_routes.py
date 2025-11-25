"""
Admin dashboard API routes for system management and monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query as QueryParam
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from backend.database.connection import get_db
from backend.models.schemas import (
    TrainingRunCreate, TrainingRunResponse, RetrainingRequest,
    ModelDeploymentResponse, DashboardMetrics, SystemHealth,
    TrainingRunUpdate
)
from backend.models.database import TrainingStatus
from backend.services.retraining_service import RetrainingService
from backend.services.feedback_service import FeedbackService
from backend.services.rag_service import RAGService
from backend.services.celery_tasks import (
    execute_retraining, deploy_trained_model,
    update_vector_store, get_task_status, cancel_task
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================
# Dashboard Metrics & Monitoring
# ============================================

@router.get("/dashboard/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(
    days: int = QueryParam(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard metrics

    - **days**: Number of days to analyze
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        from backend.models.database import (
            Query, QueryResponse, UserFeedback, TrainingRun, ModelDeployment
        )

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Total queries
        total_queries = db.query(Query).filter(
            Query.created_at >= cutoff_date
        ).count()

        # Total feedbacks
        total_feedbacks = db.query(UserFeedback).filter(
            UserFeedback.created_at >= cutoff_date
        ).count()

        # Average rating
        avg_rating = db.query(func.avg(UserFeedback.rating)).filter(
            UserFeedback.created_at >= cutoff_date
        ).scalar()
        avg_rating = float(avg_rating) if avg_rating else 0.0

        # Average confidence
        avg_confidence = db.query(func.avg(QueryResponse.confidence_score)).filter(
            QueryResponse.created_at >= cutoff_date,
            QueryResponse.confidence_score.isnot(None)
        ).scalar()
        avg_confidence = float(avg_confidence) if avg_confidence else 0.0

        # Average response time
        avg_response_time = db.query(func.avg(QueryResponse.latency_ms)).filter(
            QueryResponse.created_at >= cutoff_date,
            QueryResponse.latency_ms.isnot(None)
        ).scalar()
        avg_response_time = float(avg_response_time) if avg_response_time else 0.0

        # Positive feedback rate
        positive_feedbacks = db.query(UserFeedback).filter(
            UserFeedback.created_at >= cutoff_date,
            UserFeedback.rating >= 4
        ).count()
        positive_feedback_rate = positive_feedbacks / total_feedbacks if total_feedbacks > 0 else 0.0

        # Low confidence count
        low_confidence_count = db.query(QueryResponse).filter(
            QueryResponse.created_at >= cutoff_date,
            QueryResponse.confidence_score < 0.8
        ).count()

        # Pending review count
        feedback_service = FeedbackService(db)
        stats = feedback_service.get_feedback_statistics(days=days)
        pending_review_count = stats.pending_review_count

        # Active model version
        active_deployment = db.query(ModelDeployment).filter(
            ModelDeployment.is_active == True
        ).first()
        active_model_version = active_deployment.model_version if active_deployment else "base"

        # Last training run
        last_training = db.query(TrainingRun).order_by(
            TrainingRun.created_at.desc()
        ).first()
        last_training_run = last_training.created_at if last_training else None

        metrics = DashboardMetrics(
            total_queries=total_queries,
            total_feedbacks=total_feedbacks,
            avg_rating=round(avg_rating, 2),
            avg_confidence=round(avg_confidence, 3),
            avg_response_time_ms=round(avg_response_time, 2),
            positive_feedback_rate=round(positive_feedback_rate, 2),
            low_confidence_count=low_confidence_count,
            pending_review_count=pending_review_count,
            active_model_version=active_model_version,
            last_training_run=last_training_run
        )

        return metrics

    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard metrics"
        )


@router.get("/health", response_model=SystemHealth)
def get_system_health(db: Session = Depends(get_db)):
    """Check health of all system components"""
    try:
        from backend.database.connection import health_check as db_health_check

        # Database health
        db_healthy = db_health_check()

        # Vector store health
        rag_service = RAGService()
        health = rag_service.health_check()
        vector_store_healthy = health["vector_store"]
        llm_healthy = health["llm"]

        # Celery health (check if redis is accessible)
        celery_healthy = True
        try:
            from backend.services.celery_tasks import celery_app
            celery_app.control.ping(timeout=1.0)
        except:
            celery_healthy = False

        overall_status = "healthy" if all([
            db_healthy, vector_store_healthy, llm_healthy, celery_healthy
        ]) else "degraded"

        return SystemHealth(
            database_healthy=db_healthy,
            vector_store_healthy=vector_store_healthy,
            llm_service_healthy=llm_healthy,
            celery_healthy=celery_healthy,
            overall_status=overall_status
        )

    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return SystemHealth(
            database_healthy=False,
            vector_store_healthy=False,
            llm_service_healthy=False,
            celery_healthy=False,
            overall_status="error"
        )


# ============================================
# Retraining Management
# ============================================

@router.get("/retraining/recommendation")
def get_retraining_recommendation(db: Session = Depends(get_db)):
    """
    Get recommendation on whether to trigger retraining

    Analyzes current feedback and provides recommendation
    """
    try:
        retraining_service = RetrainingService(db)
        recommendation = retraining_service.should_trigger_retraining()
        return recommendation
    except Exception as e:
        logger.error(f"Error getting retraining recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get retraining recommendation"
        )


@router.post("/retraining/trigger")
def trigger_retraining(
    request: RetrainingRequest,
    db: Session = Depends(get_db)
):
    """
    Manually trigger model retraining

    Creates an async Celery task for retraining
    """
    try:
        # Trigger async retraining task
        task = execute_retraining.delay(
            model_name=request.model_name,
            training_type=request.training_type,
            min_rating=request.min_feedback_rating or 4
        )

        return {
            "success": True,
            "message": "Retraining task started",
            "task_id": task.id,
            "status": "pending"
        }

    except Exception as e:
        logger.error(f"Error triggering retraining: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger retraining: {str(e)}"
        )


@router.get("/retraining/runs", response_model=List[TrainingRunResponse])
def get_training_runs(
    status: Optional[TrainingStatus] = QueryParam(default=None),
    limit: int = QueryParam(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get training runs

    - **status**: Optional filter by status
    - **limit**: Maximum number of runs to return
    """
    try:
        retraining_service = RetrainingService(db)
        runs = retraining_service.get_training_runs(status=status, limit=limit)
        return runs
    except Exception as e:
        logger.error(f"Error getting training runs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get training runs"
        )


@router.get("/retraining/runs/{run_id}", response_model=TrainingRunResponse)
def get_training_run(run_id: int, db: Session = Depends(get_db)):
    """Get details of a specific training run"""
    try:
        from backend.models.database import TrainingRun

        run = db.query(TrainingRun).filter(TrainingRun.id == run_id).first()

        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training run {run_id} not found"
            )

        return run

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting training run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get training run"
        )


@router.get("/retraining/tasks/{task_id}")
def get_task_status_endpoint(task_id: str):
    """Get status of a retraining task"""
    try:
        status_info = get_task_status(task_id)
        return status_info
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task status"
        )


@router.post("/retraining/tasks/{task_id}/cancel")
def cancel_task_endpoint(task_id: str):
    """Cancel a running retraining task"""
    try:
        success = cancel_task(task_id)
        return {
            "success": success,
            "message": "Task cancelled",
            "task_id": task_id
        }
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel task"
        )


# ============================================
# Model Deployment Management
# ============================================

@router.post("/deployments/deploy")
def deploy_model_endpoint(
    training_run_id: int,
    db: Session = Depends(get_db)
):
    """
    Deploy a trained model to production

    - **training_run_id**: ID of the training run to deploy
    """
    try:
        # Trigger async deployment task
        task = deploy_trained_model.delay(training_run_id)

        return {
            "success": True,
            "message": "Model deployment task started",
            "task_id": task.id,
            "training_run_id": training_run_id
        }

    except Exception as e:
        logger.error(f"Error deploying model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy model: {str(e)}"
        )


@router.get("/deployments/active", response_model=ModelDeploymentResponse)
def get_active_deployment(db: Session = Depends(get_db)):
    """Get currently active model deployment"""
    try:
        retraining_service = RetrainingService(db)
        deployment = retraining_service.get_active_deployment()

        if not deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active deployment found"
            )

        return deployment

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active deployment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get active deployment"
        )


@router.post("/deployments/{deployment_id}/rollback")
def rollback_deployment_endpoint(
    deployment_id: int,
    rollback_to_version: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Rollback a model deployment

    - **deployment_id**: ID of deployment to rollback
    - **rollback_to_version**: Optional specific version to rollback to
    """
    try:
        retraining_service = RetrainingService(db)
        deployment = retraining_service.rollback_deployment(
            deployment_id=deployment_id,
            rollback_to_version=rollback_to_version
        )

        return {
            "success": True,
            "message": "Deployment rolled back",
            "deployment_id": deployment.id,
            "model_version": deployment.model_version
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error rolling back deployment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rollback deployment: {str(e)}"
        )


# ============================================
# Knowledge Base Management
# ============================================

@router.post("/knowledge-base/update")
def update_knowledge_base(
    documents: List[Dict[str, Any]]
):
    """
    Update knowledge base with new documents (zero downtime)

    Triggers async task for vector store update

    - **documents**: List of documents to add/update
    """
    try:
        # Trigger async vector store update
        task = update_vector_store.delay(documents)

        return {
            "success": True,
            "message": "Knowledge base update started",
            "task_id": task.id,
            "document_count": len(documents)
        }

    except Exception as e:
        logger.error(f"Error updating knowledge base: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update knowledge base: {str(e)}"
        )


@router.get("/knowledge-base/stats")
def get_knowledge_base_stats():
    """Get statistics about the knowledge base"""
    try:
        from backend.services.vector_store_service import VectorStoreService

        vector_store = VectorStoreService()
        stats = vector_store.get_statistics()

        return stats

    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get knowledge base stats"
        )


# ============================================
# System Configuration
# ============================================

@router.get("/config")
def get_system_config():
    """Get current system configuration (non-sensitive)"""
    from backend.config import get_settings

    settings = get_settings()

    return {
        "llm": {
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens
        },
        "rag": {
            "top_k": settings.rag_top_k,
            "similarity_threshold": settings.rag_similarity_threshold,
            "chunk_size": settings.rag_chunk_size
        },
        "feedback": {
            "confidence_threshold": settings.feedback_confidence_threshold,
            "negative_rating_threshold": settings.feedback_negative_rating_threshold
        },
        "retraining": {
            "enabled": settings.retraining_enabled,
            "min_feedback_count": settings.retraining_min_feedback_count,
            "schedule": settings.retraining_schedule_cron
        },
        "vector_store": {
            "type": settings.vector_store_type,
            "dimension": settings.vector_dimension
        }
    }


# ============================================
# Audit Logs
# ============================================

@router.get("/audit-logs")
def get_audit_logs(
    limit: int = QueryParam(default=50, ge=1, le=200),
    action: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get audit logs

    - **limit**: Maximum number of logs to return
    - **action**: Optional filter by action type
    """
    try:
        from backend.models.database import AuditLog

        query = db.query(AuditLog).order_by(AuditLog.created_at.desc())

        if action:
            query = query.filter(AuditLog.action == action)

        logs = query.limit(limit).all()

        return {
            "count": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "details": log.details,
                    "created_at": log.created_at
                }
                for log in logs
            ]
        }

    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get audit logs"
        )
