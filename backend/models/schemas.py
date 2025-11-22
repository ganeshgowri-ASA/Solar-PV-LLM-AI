"""Pydantic schemas for API request/response models."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ExpertiseLevel(str, Enum):
    """User expertise level for tailored responses."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class CalculationType(str, Enum):
    """Types of solar PV calculations."""
    SYSTEM_SIZE = "system_size"
    ENERGY_OUTPUT = "energy_output"
    ROI = "roi"
    PAYBACK_PERIOD = "payback_period"
    PANEL_COUNT = "panel_count"
    INVERTER_SIZE = "inverter_size"
    BATTERY_SIZE = "battery_size"


# Citation model for RAG responses
class Citation(BaseModel):
    """Citation from source documents."""
    source: str = Field(..., description="Source document or standard name")
    section: Optional[str] = Field(None, description="Section reference")
    page: Optional[int] = Field(None, description="Page number if applicable")
    text: str = Field(..., description="Cited text excerpt")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score 0-1")


# Chat models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., min_length=1, max_length=2000, description="User's question")
    expertise_level: ExpertiseLevel = Field(
        default=ExpertiseLevel.INTERMEDIATE,
        description="User's expertise level"
    )
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    include_citations: bool = Field(default=True, description="Include source citations")
    stream: bool = Field(default=False, description="Enable streaming response")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="AI-generated response")
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    conversation_id: str = Field(..., description="Conversation ID")
    expertise_level: ExpertiseLevel = Field(..., description="Response expertise level")
    confidence_score: float = Field(..., ge=0, le=1, description="Response confidence")
    follow_up_questions: List[str] = Field(default_factory=list, description="Suggested follow-ups")


# Search models
class StandardDocument(BaseModel):
    """Solar PV standard document."""
    id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    standard_code: str = Field(..., description="Standard code (e.g., IEC 61724)")
    category: str = Field(..., description="Category (e.g., Installation, Safety)")
    summary: str = Field(..., description="Document summary")
    relevance_score: float = Field(..., ge=0, le=1, description="Search relevance")
    sections: List[str] = Field(default_factory=list, description="Relevant sections")


class SearchRequest(BaseModel):
    """Request model for standards search."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    categories: Optional[List[str]] = Field(None, description="Filter by categories")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum results")
    include_summaries: bool = Field(default=True, description="Include document summaries")


class SearchResponse(BaseModel):
    """Response model for standards search."""
    results: List[StandardDocument] = Field(..., description="Search results")
    total_count: int = Field(..., description="Total matching documents")
    query: str = Field(..., description="Original search query")
    categories_found: List[str] = Field(default_factory=list, description="Categories in results")


# Calculator models
class CalculatorRequest(BaseModel):
    """Request model for solar calculations."""
    calculation_type: CalculationType = Field(..., description="Type of calculation")
    parameters: Dict[str, Any] = Field(..., description="Calculation parameters")
    location: Optional[str] = Field(None, description="Location for solar irradiance")
    include_explanation: bool = Field(default=True, description="Include step-by-step explanation")


class CalculatorResponse(BaseModel):
    """Response model for solar calculations."""
    result: Dict[str, Any] = Field(..., description="Calculation results")
    calculation_type: CalculationType = Field(..., description="Type of calculation")
    explanation: Optional[str] = Field(None, description="Step-by-step explanation")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    unit: str = Field(..., description="Result unit")


# Image analysis models
class ImageAnalysisRequest(BaseModel):
    """Request model for image analysis."""
    image_base64: str = Field(..., description="Base64 encoded image")
    analysis_type: str = Field(
        default="general",
        description="Type of analysis (general, defect_detection, shading, layout)"
    )
    include_recommendations: bool = Field(default=True, description="Include recommendations")


class ImageAnalysisResponse(BaseModel):
    """Response model for image analysis."""
    analysis: str = Field(..., description="Analysis results")
    detected_elements: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Detected elements in image"
    )
    issues_found: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Issues or defects found"
    )
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    confidence_score: float = Field(..., ge=0, le=1, description="Analysis confidence")
