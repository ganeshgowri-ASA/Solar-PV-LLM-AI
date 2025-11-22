"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================
# Enums
# ============================================

class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"
    REVIEWER = "reviewer"


class FeedbackRatingEnum(int, Enum):
    VERY_BAD = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


class TrainingStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReviewStatusEnum(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


# ============================================
# User Schemas
# ============================================

class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRoleEnum
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ============================================
# Query and Response Schemas
# ============================================

class QueryCreate(BaseModel):
    query_text: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    id: int
    query_text: str
    created_at: datetime
    session_id: Optional[str] = None

    class Config:
        from_attributes = True


class ResponseCreate(BaseModel):
    response_text: str
    model_version: str
    confidence_score: Optional[float] = None
    latency_ms: Optional[int] = None
    token_count: Optional[int] = None


class ResponseDetail(BaseModel):
    id: int
    query_id: int
    response_text: str
    model_version: str
    confidence_score: Optional[float] = None
    latency_ms: Optional[int] = None
    token_count: Optional[int] = None
    cost_estimate: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QueryWithResponse(QueryResponse):
    response: Optional[ResponseDetail] = None
    retrieved_documents: List[Dict[str, Any]] = []


# ============================================
# Feedback Schemas
# ============================================

class FeedbackCreate(BaseModel):
    response_id: int
    rating: FeedbackRatingEnum
    is_helpful: Optional[bool] = None
    is_accurate: Optional[bool] = None
    is_complete: Optional[bool] = None


class FeedbackCommentCreate(BaseModel):
    comment_text: str = Field(..., min_length=1, max_length=5000)
    comment_type: Optional[str] = None


class FeedbackTagCreate(BaseModel):
    tag_name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = None


class FeedbackCommentResponse(BaseModel):
    id: int
    comment_text: str
    comment_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackTagResponse(BaseModel):
    id: int
    tag_name: str
    category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackResponse(BaseModel):
    id: int
    response_id: int
    rating: FeedbackRatingEnum
    is_helpful: Optional[bool] = None
    is_accurate: Optional[bool] = None
    is_complete: Optional[bool] = None
    review_status: ReviewStatusEnum
    created_at: datetime
    comments: List[FeedbackCommentResponse] = []
    tags: List[FeedbackTagResponse] = []

    class Config:
        from_attributes = True


class FeedbackUpdate(BaseModel):
    review_status: Optional[ReviewStatusEnum] = None


class FeedbackStats(BaseModel):
    total_count: int
    avg_rating: float
    rating_distribution: Dict[int, int]
    positive_feedback_rate: float
    pending_review_count: int


# ============================================
# Document and RAG Schemas
# ============================================

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    id: int
    title: str
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    content_hash: str
    version: int
    is_active: bool
    created_at: datetime
    chunk_count: int = 0

    class Config:
        from_attributes = True


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class VectorSearchRequest(BaseModel):
    query_text: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: Optional[float] = Field(default=0.7, ge=0, le=1)


class VectorSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    content: str
    relevance_score: float
    source_url: Optional[str] = None


# ============================================
# Training and Retraining Schemas
# ============================================

class TrainingRunCreate(BaseModel):
    model_name: str
    model_version: str
    base_model: Optional[str] = None
    training_type: str
    training_config: Optional[Dict[str, Any]] = None


class TrainingRunResponse(BaseModel):
    id: int
    model_name: str
    model_version: str
    base_model: Optional[str] = None
    training_type: str
    status: TrainingStatusEnum
    dataset_size: Optional[int] = None
    feedback_count: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    checkpoint_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TrainingRunUpdate(BaseModel):
    status: Optional[TrainingStatusEnum] = None
    metrics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class RetrainingRequest(BaseModel):
    model_name: str
    training_type: str = Field(default="lora")
    min_feedback_rating: Optional[int] = Field(default=1, ge=1, le=5)
    max_feedback_rating: Optional[int] = Field(default=5, ge=1, le=5)
    include_low_confidence: bool = Field(default=True)
    confidence_threshold: Optional[float] = Field(default=0.8, ge=0, le=1)
    training_config: Optional[Dict[str, Any]] = None


class ModelDeploymentCreate(BaseModel):
    training_run_id: int
    model_version: str
    deployment_config: Optional[Dict[str, Any]] = None


class ModelDeploymentResponse(BaseModel):
    id: int
    training_run_id: int
    model_version: str
    is_active: bool
    deployed_at: Optional[datetime] = None
    deactivated_at: Optional[datetime] = None
    rollback_version: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Admin Dashboard Schemas
# ============================================

class DashboardMetrics(BaseModel):
    total_queries: int
    total_feedbacks: int
    avg_rating: float
    avg_confidence: float
    avg_response_time_ms: float
    positive_feedback_rate: float
    low_confidence_count: int
    pending_review_count: int
    active_model_version: str
    last_training_run: Optional[datetime] = None


class SystemHealth(BaseModel):
    database_healthy: bool
    vector_store_healthy: bool
    llm_service_healthy: bool
    celery_healthy: bool
    overall_status: str


class FeedbackForReview(BaseModel):
    id: int
    response_id: int
    query_text: str
    response_text: str
    rating: FeedbackRatingEnum
    confidence_score: Optional[float] = None
    review_status: ReviewStatusEnum
    created_at: datetime
    comments: List[FeedbackCommentResponse] = []

    class Config:
        from_attributes = True


class RetrainingRecommendation(BaseModel):
    should_retrain: bool
    reason: str
    feedback_count: int
    low_confidence_count: int
    negative_feedback_count: int
    recommended_config: Dict[str, Any]


# ============================================
# Bulk Operations Schemas
# ============================================

class BulkFeedbackReview(BaseModel):
    feedback_ids: List[int]
    review_status: ReviewStatusEnum


class BulkDocumentUpload(BaseModel):
    documents: List[DocumentCreate]


# ============================================
# Pagination Schemas
# ============================================

class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    skip: int
    limit: int
    has_next: bool

    @validator("has_next", pre=True, always=True)
    def calculate_has_next(cls, v, values):
        return values["skip"] + values["limit"] < values["total"]
