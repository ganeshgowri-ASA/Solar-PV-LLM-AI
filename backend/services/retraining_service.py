"""
Model retraining service with job scheduling and orchestration
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session

from backend.models.database import (
    TrainingRun, TrainingStatus, RetrainingFeedback,
    UserFeedback, QueryResponse, Query, ModelDeployment
)
from backend.services.feedback_service import FeedbackService
from backend.services.llm_service import LoRAFineTuner
from backend.config import get_settings

logger = logging.getLogger(__name__)


class RetrainingService:
    """
    Service for orchestrating model retraining based on user feedback
    """

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.feedback_service = FeedbackService(db)
        self.fine_tuner = LoRAFineTuner()

    def should_trigger_retraining(self) -> Dict[str, Any]:
        """
        Determine if retraining should be triggered based on:
        - Sufficient feedback collected
        - Negative feedback rate
        - Low confidence responses
        - Time since last training

        Returns:
            {
                "should_retrain": bool,
                "reason": str,
                "metrics": dict
            }
        """
        logger.info("Evaluating retraining criteria")

        # Get feedback statistics
        stats = self.feedback_service.get_feedback_statistics(days=30)

        # Get last training run
        last_training = self.db.query(TrainingRun).order_by(
            TrainingRun.created_at.desc()
        ).first()

        # Calculate metrics
        metrics = {
            "total_feedback_count": stats.total_count,
            "avg_rating": stats.avg_rating,
            "positive_feedback_rate": stats.positive_feedback_rate,
            "pending_review_count": stats.pending_review_count,
            "days_since_last_training": None
        }

        if last_training:
            days_since = (datetime.utcnow() - last_training.created_at).days
            metrics["days_since_last_training"] = days_since

        # Evaluate criteria
        reasons = []

        # Criterion 1: Sufficient feedback collected
        min_feedback = self.settings.retraining_min_feedback_count
        if stats.total_count >= min_feedback:
            reasons.append(f"Sufficient feedback collected ({stats.total_count} >= {min_feedback})")

        # Criterion 2: Low average rating
        if stats.avg_rating < 3.5:
            reasons.append(f"Low average rating ({stats.avg_rating})")

        # Criterion 3: Low positive feedback rate
        if stats.positive_feedback_rate < 0.6:
            reasons.append(f"Low positive feedback rate ({stats.positive_feedback_rate})")

        # Criterion 4: Time-based retraining (e.g., weekly)
        if last_training:
            days_since = metrics["days_since_last_training"]
            if days_since >= 7:  # Weekly retraining
                reasons.append(f"Scheduled retraining (last trained {days_since} days ago)")

        should_retrain = len(reasons) > 0

        recommendation = {
            "should_retrain": should_retrain,
            "reason": " | ".join(reasons) if reasons else "No retraining needed",
            "metrics": metrics
        }

        logger.info(f"Retraining recommendation: {recommendation}")
        return recommendation

    def create_training_run(
        self,
        model_name: str,
        training_type: str = "lora",
        base_model: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> TrainingRun:
        """
        Create a new training run

        Args:
            model_name: Name for the trained model
            training_type: Type of training (lora, full, vector_update)
            base_model: Base model to fine-tune from
            config: Training configuration

        Returns:
            Created TrainingRun instance
        """
        logger.info(f"Creating training run: {model_name}")

        # Generate version
        version = f"{model_name}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        training_run = TrainingRun(
            model_name=model_name,
            model_version=version,
            base_model=base_model or self.settings.llm_model,
            training_type=training_type,
            status=TrainingStatus.PENDING,
            training_config=config or self._get_default_config()
        )

        self.db.add(training_run)
        self.db.commit()
        self.db.refresh(training_run)

        logger.info(f"Created training run id={training_run.id}, version={version}")
        return training_run

    def prepare_training_data(
        self,
        training_run_id: int,
        min_rating: int = 4,
        include_negative_examples: bool = True
    ) -> Dict[str, Any]:
        """
        Prepare training data from feedback

        Args:
            training_run_id: ID of the training run
            min_rating: Minimum rating for positive examples
            include_negative_examples: Whether to include negative examples

        Returns:
            {
                "positive_examples": list,
                "negative_examples": list,
                "total_count": int
            }
        """
        logger.info(f"Preparing training data for run {training_run_id}")

        # Get high-quality feedbacks (positive examples)
        positive_feedbacks = self.feedback_service.get_feedbacks_for_training(
            min_rating=min_rating,
            include_reviewed_only=True
        )

        positive_examples = []
        for feedback, response, query in positive_feedbacks:
            example = {
                "prompt": query.query_text,
                "completion": response.response_text,
                "rating": feedback.rating.value,
                "confidence": response.confidence_score
            }
            positive_examples.append(example)

            # Link feedback to training run
            link = RetrainingFeedback(
                training_run_id=training_run_id,
                feedback_id=feedback.id,
                included=True,
                weight=1.0
            )
            self.db.add(link)

        # Get negative feedbacks for learning what not to do
        negative_examples = []
        if include_negative_examples:
            negative_feedbacks = self.feedback_service.get_negative_feedbacks(
                rating_threshold=2,
                days=30,
                limit=50
            )

            for feedback in negative_feedbacks:
                response = self.db.query(QueryResponse).filter(
                    QueryResponse.id == feedback.response_id
                ).first()
                query = self.db.query(Query).filter(
                    Query.id == response.query_id
                ).first()

                # For negative examples, we might want to provide corrected responses
                # or use them for reinforcement learning
                example = {
                    "prompt": query.query_text,
                    "completion": response.response_text,
                    "rating": feedback.rating.value,
                    "confidence": response.confidence_score,
                    "type": "negative"
                }
                negative_examples.append(example)

                # Link feedback to training run
                link = RetrainingFeedback(
                    training_run_id=training_run_id,
                    feedback_id=feedback.id,
                    included=True,
                    weight=0.5  # Lower weight for negative examples
                )
                self.db.add(link)

        self.db.commit()

        result = {
            "positive_examples": positive_examples,
            "negative_examples": negative_examples,
            "total_count": len(positive_examples) + len(negative_examples)
        }

        logger.info(
            f"Prepared {result['total_count']} training examples "
            f"({len(positive_examples)} positive, {len(negative_examples)} negative)"
        )

        return result

    def execute_training(
        self,
        training_run_id: int,
        training_data: Dict[str, Any]
    ) -> TrainingRun:
        """
        Execute the training process

        Args:
            training_run_id: ID of the training run
            training_data: Prepared training data

        Returns:
            Updated TrainingRun instance
        """
        logger.info(f"Executing training for run {training_run_id}")

        training_run = self.db.query(TrainingRun).filter(
            TrainingRun.id == training_run_id
        ).first()

        if not training_run:
            raise ValueError(f"Training run {training_run_id} not found")

        try:
            # Update status to running
            training_run.status = TrainingStatus.RUNNING
            training_run.started_at = datetime.utcnow()
            training_run.dataset_size = training_data["total_count"]
            training_run.feedback_count = training_data["total_count"]
            self.db.commit()

            # Prepare training file
            training_file = f"{self.settings.retraining_checkpoint_dir}/{training_run.model_version}_train.jsonl"

            # Use only positive examples for training (negative examples could be used differently)
            examples = training_data["positive_examples"]

            self.fine_tuner.prepare_training_data(
                examples=examples,
                output_path=training_file
            )

            # Start training
            output_dir = f"{self.settings.retraining_checkpoint_dir}/{training_run.model_version}"

            training_result = self.fine_tuner.train_lora(
                training_data_path=training_file,
                output_dir=output_dir,
                model_name=training_run.model_version
            )

            # Update training run with results
            training_run.checkpoint_path = output_dir
            training_run.status = TrainingStatus.COMPLETED
            training_run.completed_at = datetime.utcnow()
            training_run.duration_seconds = int(
                (training_run.completed_at - training_run.started_at).total_seconds()
            )
            training_run.metrics = training_result

            self.db.commit()
            self.db.refresh(training_run)

            logger.info(f"Training completed successfully for run {training_run_id}")
            return training_run

        except Exception as e:
            logger.error(f"Training failed for run {training_run_id}: {e}")

            training_run.status = TrainingStatus.FAILED
            training_run.error_message = str(e)
            training_run.completed_at = datetime.utcnow()
            self.db.commit()

            raise

    def trigger_retraining_pipeline(
        self,
        model_name: str,
        training_type: str = "lora",
        min_rating: int = 4
    ) -> Dict[str, Any]:
        """
        Trigger the complete retraining pipeline

        Steps:
        1. Create training run
        2. Prepare training data from feedback
        3. Execute training
        4. Return training run info

        Args:
            model_name: Name for the trained model
            training_type: Type of training
            min_rating: Minimum rating for training examples

        Returns:
            Training run information
        """
        logger.info(f"Triggering retraining pipeline for {model_name}")

        # Step 1: Create training run
        training_run = self.create_training_run(
            model_name=model_name,
            training_type=training_type
        )

        # Step 2: Prepare training data
        training_data = self.prepare_training_data(
            training_run_id=training_run.id,
            min_rating=min_rating
        )

        if training_data["total_count"] == 0:
            logger.warning("No training data available")
            training_run.status = TrainingStatus.CANCELLED
            training_run.error_message = "No training data available"
            self.db.commit()

            return {
                "success": False,
                "message": "No training data available",
                "training_run_id": training_run.id
            }

        # Step 3: Execute training (this could be async in production)
        try:
            training_run = self.execute_training(training_run.id, training_data)

            return {
                "success": True,
                "message": "Training completed successfully",
                "training_run_id": training_run.id,
                "model_version": training_run.model_version,
                "training_examples": training_data["total_count"],
                "status": training_run.status.value
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Training failed: {str(e)}",
                "training_run_id": training_run.id
            }

    def deploy_model(
        self,
        training_run_id: int,
        deactivate_current: bool = True
    ) -> ModelDeployment:
        """
        Deploy a trained model to production

        Args:
            training_run_id: ID of the training run to deploy
            deactivate_current: Whether to deactivate currently active model

        Returns:
            ModelDeployment instance
        """
        logger.info(f"Deploying model from training run {training_run_id}")

        training_run = self.db.query(TrainingRun).filter(
            TrainingRun.id == training_run_id
        ).first()

        if not training_run:
            raise ValueError(f"Training run {training_run_id} not found")

        if training_run.status != TrainingStatus.COMPLETED:
            raise ValueError(f"Training run {training_run_id} is not completed")

        # Deactivate current active model
        if deactivate_current:
            active_deployments = self.db.query(ModelDeployment).filter(
                ModelDeployment.is_active == True
            ).all()

            for deployment in active_deployments:
                deployment.is_active = False
                deployment.deactivated_at = datetime.utcnow()
                logger.info(f"Deactivated deployment {deployment.id}")

        # Create new deployment
        deployment = ModelDeployment(
            training_run_id=training_run_id,
            model_version=training_run.model_version,
            is_active=True,
            deployed_at=datetime.utcnow(),
            deployment_config={
                "model_path": training_run.checkpoint_path,
                "training_type": training_run.training_type
            }
        )

        self.db.add(deployment)
        self.db.commit()
        self.db.refresh(deployment)

        logger.info(f"Deployed model version {deployment.model_version}")
        return deployment

    def rollback_deployment(
        self,
        deployment_id: int,
        rollback_to_version: Optional[str] = None
    ) -> ModelDeployment:
        """
        Rollback a model deployment

        Args:
            deployment_id: ID of deployment to rollback
            rollback_to_version: Optional specific version to rollback to

        Returns:
            Updated deployment
        """
        logger.info(f"Rolling back deployment {deployment_id}")

        deployment = self.db.query(ModelDeployment).filter(
            ModelDeployment.id == deployment_id
        ).first()

        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")

        # Deactivate current
        deployment.is_active = False
        deployment.deactivated_at = datetime.utcnow()

        # Find previous deployment or specified version
        if rollback_to_version:
            previous = self.db.query(ModelDeployment).filter(
                ModelDeployment.model_version == rollback_to_version
            ).first()
        else:
            previous = self.db.query(ModelDeployment).filter(
                ModelDeployment.id < deployment_id
            ).order_by(ModelDeployment.id.desc()).first()

        if previous:
            previous.is_active = True
            previous.deployed_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Rolled back to version {previous.model_version}")
            return previous
        else:
            self.db.commit()
            logger.warning("No previous deployment found for rollback")
            return deployment

    def get_training_runs(
        self,
        status: Optional[TrainingStatus] = None,
        limit: int = 10
    ) -> List[TrainingRun]:
        """Get training runs with optional status filter"""
        query = self.db.query(TrainingRun)

        if status:
            query = query.filter(TrainingRun.status == status)

        return query.order_by(TrainingRun.created_at.desc()).limit(limit).all()

    def get_active_deployment(self) -> Optional[ModelDeployment]:
        """Get currently active model deployment"""
        return self.db.query(ModelDeployment).filter(
            ModelDeployment.is_active == True
        ).first()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default training configuration"""
        return {
            "lora_r": self.settings.lora_r,
            "lora_alpha": self.settings.lora_alpha,
            "lora_dropout": self.settings.lora_dropout,
            "lora_target_modules": self.settings.lora_target_modules,
            "batch_size": self.settings.training_batch_size,
            "epochs": self.settings.training_epochs,
            "learning_rate": self.settings.training_learning_rate,
            "gradient_accumulation_steps": self.settings.training_gradient_accumulation_steps
        }
