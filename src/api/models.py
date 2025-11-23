"""Pydantic models for API requests and responses"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# Request Models

class DocumentInput(BaseModel):
    """Model for a single document input"""
    text: str = Field(..., description="Document text content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Document metadata (standards, clauses, test_type, etc.)"
    )


class IngestDocumentsRequest(BaseModel):
    """Request model for ingesting documents"""
    documents: List[DocumentInput] = Field(..., description="List of documents to ingest")
    namespace: str = Field(default="", description="Optional namespace for organization")
    batch_size: Optional[int] = Field(
        default=None,
        description="Batch size for processing (defaults to config)"
    )


class SearchRequest(BaseModel):
    """Request model for similarity search"""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata filters"
    )
    namespace: str = Field(default="", description="Optional namespace to search in")


class SearchWithFiltersRequest(BaseModel):
    """Request model for Solar PV specific filtered search"""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    standards: Optional[str] = Field(
        default=None,
        description="Filter by standards (e.g., 'IEC 61215', 'IEC 61730')"
    )
    clauses: Optional[List[str]] = Field(
        default=None,
        description="Filter by specific clauses"
    )
    test_type: Optional[str] = Field(
        default=None,
        description="Filter by test type (e.g., 'performance', 'safety', 'reliability')"
    )
    namespace: str = Field(default="", description="Optional namespace to search in")


class DeleteDocumentsRequest(BaseModel):
    """Request model for deleting documents"""
    ids: Optional[List[str]] = Field(
        default=None,
        description="List of document IDs to delete"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Delete documents matching these filters"
    )
    namespace: str = Field(default="", description="Namespace to delete from")


class StatsRequest(BaseModel):
    """Request model for getting index statistics"""
    namespace: str = Field(default="", description="Optional namespace")


# Response Models

class IngestResponse(BaseModel):
    """Response model for document ingestion"""
    status: str = Field(..., description="Operation status")
    documents_ingested: int = Field(..., description="Number of documents successfully ingested")
    namespace: str = Field(..., description="Namespace used")
    batches_processed: int = Field(..., description="Number of batches processed")


class SearchResult(BaseModel):
    """Model for a single search result"""
    id: str = Field(..., description="Document ID")
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")


class SearchResponse(BaseModel):
    """Response model for search operations"""
    status: str = Field(default="success", description="Operation status")
    query: str = Field(..., description="Original query text")
    results: List[SearchResult] = Field(..., description="Search results")
    count: int = Field(..., description="Number of results returned")


class DeleteResponse(BaseModel):
    """Response model for delete operations"""
    status: str = Field(..., description="Operation status")
    deletion_info: Dict[str, Any] = Field(..., description="Deletion details")


class IndexStats(BaseModel):
    """Model for index statistics"""
    total_vector_count: int = Field(..., description="Total number of vectors in index")
    dimension: int = Field(..., description="Vector dimension")
    index_fullness: float = Field(..., description="Index fullness percentage")
    namespaces: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description="Statistics per namespace"
    )


class StatsResponse(BaseModel):
    """Response model for stats operations"""
    status: str = Field(..., description="Operation status")
    stats: IndexStats = Field(..., description="Index statistics")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    pinecone_connected: bool = Field(..., description="Pinecone connection status")
    embedding_service_ready: bool = Field(..., description="Embedding service status")
