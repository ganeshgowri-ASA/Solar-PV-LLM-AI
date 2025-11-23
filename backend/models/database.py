"""
Database models for Solar PV LLM AI System
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey,
    JSON, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from backend.database.connection import Base


# ============================================
# Enums
# ============================================

class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"
    REVIEWER = "reviewer"


class FeedbackRating(int, enum.Enum):
    """Feedback rating scale (1-5)"""
    VERY_BAD = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


class TrainingStatus(str, enum.Enum):
    """Training run status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReviewStatus(str, enum.Enum):
    """Feedback review status"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


# ============================================
# User Management Models
# ============================================

class User(Base):
    """User accounts and authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    queries = relationship("Query", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("UserFeedback", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


# ============================================
# Query and Response Models
# ============================================

class Query(Base):
    """User queries to the system"""
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query_text = Column(Text, nullable=False)
    query_embedding = Column(JSON)  # Store embedding as JSON array
    session_id = Column(String(255), index=True)  # For tracking conversation sessions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="queries")
    response = relationship("QueryResponse", back_populates="query", uselist=False, cascade="all, delete-orphan")
    retrieved_docs = relationship("RetrievedDocument", back_populates="query", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_query_user_created", "user_id", "created_at"),
        Index("idx_query_session", "session_id"),
    )

    def __repr__(self):
        return f"<Query(id={self.id}, user_id={self.user_id})>"


class QueryResponse(Base):
    """AI-generated responses to queries"""
    __tablename__ = "query_responses"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), unique=True, nullable=False)
    response_text = Column(Text, nullable=False)
    model_version = Column(String(100), nullable=False)  # e.g., "gpt-4-1.0", "custom-lora-v2"
    confidence_score = Column(Float)  # Model confidence (0-1)
    latency_ms = Column(Integer)  # Response generation time
    token_count = Column(Integer)  # Number of tokens generated
    cost_estimate = Column(Float)  # Estimated API cost
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    query = relationship("Query", back_populates="response")
    feedback = relationship("UserFeedback", back_populates="response", uselist=False, cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_response_confidence", "confidence_score"),
        Index("idx_response_model_version", "model_version"),
        Index("idx_response_created", "created_at"),
    )

    def __repr__(self):
        return f"<QueryResponse(id={self.id}, query_id={self.query_id}, confidence={self.confidence_score})>"


# ============================================
# Feedback Collection Models
# ============================================

class UserFeedback(Base):
    """User feedback on AI responses"""
    __tablename__ = "user_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("query_responses.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rating = Column(SQLEnum(FeedbackRating), nullable=False)
    is_helpful = Column(Boolean)
    is_accurate = Column(Boolean)
    is_complete = Column(Boolean)
    review_status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reviewed_at = Column(DateTime(timezone=True))

    # Relationships
    response = relationship("QueryResponse", back_populates="feedback")
    user = relationship("User", back_populates="feedbacks")
    comments = relationship("FeedbackComment", back_populates="feedback", cascade="all, delete-orphan")
    tags = relationship("FeedbackTag", back_populates="feedback", cascade="all, delete-orphan")
    retraining_inclusions = relationship("RetrainingFeedback", back_populates="feedback")

    # Indexes
    __table_args__ = (
        Index("idx_feedback_rating", "rating"),
        Index("idx_feedback_review_status", "review_status"),
        Index("idx_feedback_created", "created_at"),
    )

    def __repr__(self):
        return f"<UserFeedback(id={self.id}, response_id={self.response_id}, rating={self.rating})>"


class FeedbackComment(Base):
    """Detailed comments on feedback"""
    __tablename__ = "feedback_comments"

    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("user_feedbacks.id"), nullable=False)
    comment_text = Column(Text, nullable=False)
    comment_type = Column(String(50))  # e.g., "issue", "suggestion", "praise"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    feedback = relationship("UserFeedback", back_populates="comments")

    def __repr__(self):
        return f"<FeedbackComment(id={self.id}, feedback_id={self.feedback_id})>"


class FeedbackTag(Base):
    """Tags for categorizing feedback"""
    __tablename__ = "feedback_tags"

    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("user_feedbacks.id"), nullable=False)
    tag_name = Column(String(100), nullable=False)
    category = Column(String(100))  # e.g., "error_type", "topic", "user_intent"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    feedback = relationship("UserFeedback", back_populates="tags")

    # Indexes
    __table_args__ = (
        Index("idx_tag_name", "tag_name"),
        Index("idx_tag_category", "category"),
    )

    def __repr__(self):
        return f"<FeedbackTag(id={self.id}, tag_name={tag_name})>"


# ============================================
# Vector Store and RAG Models
# ============================================

class Document(Base):
    """Source documents in the knowledge base"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    source_url = Column(String(1000))
    source_type = Column(String(100))  # e.g., "pdf", "web", "manual"
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), unique=True, index=True)  # SHA-256 hash for deduplication
    metadata = Column(JSON)  # Additional metadata (author, date, etc.)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title})>"


class DocumentChunk(Base):
    """Chunked segments of documents for vector storage"""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Position in document
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), index=True)
    embedding_id = Column(String(255), unique=True)  # ID in vector store
    token_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chunks")
    retrievals = relationship("RetrievedDocument", back_populates="chunk")

    # Indexes
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_doc_chunk"),
        Index("idx_chunk_embedding", "embedding_id"),
    )

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"


class RetrievedDocument(Base):
    """Tracks which documents were retrieved for each query"""
    __tablename__ = "retrieved_documents"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"), nullable=False)
    relevance_score = Column(Float, nullable=False)  # Similarity score
    rank = Column(Integer, nullable=False)  # Ranking in results
    was_used = Column(Boolean, default=True)  # Whether it was included in context
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    query = relationship("Query", back_populates="retrieved_docs")
    chunk = relationship("DocumentChunk", back_populates="retrievals")

    # Indexes
    __table_args__ = (
        Index("idx_retrieved_query", "query_id"),
        Index("idx_retrieved_score", "relevance_score"),
    )

    def __repr__(self):
        return f"<RetrievedDocument(id={self.id}, query_id={self.query_id}, score={self.relevance_score})>"


# ============================================
# Model Training and Retraining Models
# ============================================

class TrainingRun(Base):
    """Tracks model training and retraining runs"""
    __tablename__ = "training_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(100), nullable=False, unique=True)
    base_model = Column(String(255))  # Base model used for fine-tuning
    training_type = Column(String(50), nullable=False)  # e.g., "full", "lora", "vector_update"
    status = Column(SQLEnum(TrainingStatus), default=TrainingStatus.PENDING, nullable=False)

    # Training parameters
    training_config = Column(JSON)  # Training hyperparameters
    dataset_size = Column(Integer)
    feedback_count = Column(Integer)

    # Metrics
    metrics = Column(JSON)  # Training and validation metrics
    loss = Column(Float)
    accuracy = Column(Float)

    # Timing
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)

    # Results
    checkpoint_path = Column(String(1000))
    error_message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    feedback_inclusions = relationship("RetrainingFeedback", back_populates="training_run")
    deployment = relationship("ModelDeployment", back_populates="training_run", uselist=False)

    # Indexes
    __table_args__ = (
        Index("idx_training_status", "status"),
        Index("idx_training_created", "created_at"),
    )

    def __repr__(self):
        return f"<TrainingRun(id={self.id}, version={self.model_version}, status={self.status})>"


class RetrainingFeedback(Base):
    """Links feedback to training runs"""
    __tablename__ = "retraining_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    training_run_id = Column(Integer, ForeignKey("training_runs.id"), nullable=False)
    feedback_id = Column(Integer, ForeignKey("user_feedbacks.id"), nullable=False)
    included = Column(Boolean, default=True, nullable=False)
    weight = Column(Float, default=1.0)  # Weight in training
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    training_run = relationship("TrainingRun", back_populates="feedback_inclusions")
    feedback = relationship("UserFeedback", back_populates="retraining_inclusions")

    # Indexes
    __table_args__ = (
        UniqueConstraint("training_run_id", "feedback_id", name="uq_training_feedback"),
        Index("idx_retraining_fb_included", "included"),
    )

    def __repr__(self):
        return f"<RetrainingFeedback(training_run_id={self.training_run_id}, feedback_id={self.feedback_id})>"


class ModelDeployment(Base):
    """Tracks model deployments to production"""
    __tablename__ = "model_deployments"

    id = Column(Integer, primary_key=True, index=True)
    training_run_id = Column(Integer, ForeignKey("training_runs.id"), nullable=False)
    model_version = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, default=False, nullable=False)
    deployment_config = Column(JSON)
    deployed_at = Column(DateTime(timezone=True))
    deactivated_at = Column(DateTime(timezone=True))
    rollback_version = Column(String(100))  # Version to rollback to if needed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    training_run = relationship("TrainingRun", back_populates="deployment")
    metrics = relationship("DeploymentMetric", back_populates="deployment", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_deployment_active", "is_active"),
        Index("idx_deployment_version", "model_version"),
    )

    def __repr__(self):
        return f"<ModelDeployment(id={self.id}, version={self.model_version}, active={self.is_active})>"


class DeploymentMetric(Base):
    """Tracks performance metrics for deployed models"""
    __tablename__ = "deployment_metrics"

    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(Integer, ForeignKey("model_deployments.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Performance metrics
    queries_count = Column(Integer, default=0)
    avg_response_time_ms = Column(Float)
    avg_confidence_score = Column(Float)
    avg_rating = Column(Float)
    positive_feedback_rate = Column(Float)
    error_rate = Column(Float)

    # Cost metrics
    total_tokens = Column(Integer)
    total_cost = Column(Float)

    # Relationships
    deployment = relationship("ModelDeployment", back_populates="metrics")

    # Indexes
    __table_args__ = (
        Index("idx_metric_deployment_time", "deployment_id", "timestamp"),
    )

    def __repr__(self):
        return f"<DeploymentMetric(id={self.id}, deployment_id={self.deployment_id})>"


# ============================================
# System Monitoring Models
# ============================================

class SystemMetric(Base):
    """System-wide performance metrics"""
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Request metrics
    queries_count = Column(Integer, default=0)
    avg_response_time_ms = Column(Float)
    error_rate = Column(Float)

    # Feedback metrics
    feedbacks_count = Column(Integer, default=0)
    avg_rating = Column(Float)
    positive_feedback_rate = Column(Float)

    # Resource metrics
    cpu_usage = Column(Float)
    memory_usage_mb = Column(Float)

    # Additional data
    metadata = Column(JSON)

    def __repr__(self):
        return f"<SystemMetric(id={self.id}, timestamp={self.timestamp})>"


class AuditLog(Base):
    """Audit trail for system actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., "model_deployed", "feedback_reviewed"
    resource_type = Column(String(100))  # e.g., "training_run", "document"
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_created", "created_at"),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action})>"
