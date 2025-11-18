"""Data models for the LLM Orchestrator."""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class QueryType(str, Enum):
    """Types of queries supported by the orchestrator."""

    STANDARD_INTERPRETATION = "standard_interpretation"
    CALCULATION = "calculation"
    IMAGE_ANALYSIS = "image_analysis"
    TECHNICAL_EXPLANATION = "technical_explanation"
    CODE_GENERATION = "code_generation"


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    GPT = "gpt"
    CLAUDE = "claude"
    HYBRID = "hybrid"


class QueryRequest(BaseModel):
    """Request model for query processing."""

    query: str = Field(..., description="The user's query text")
    query_type: Optional[QueryType] = Field(
        None, description="Optional explicit query type classification"
    )
    preferred_llm: Optional[LLMProvider] = Field(
        None, description="Optional LLM preference"
    )
    image_data: Optional[str] = Field(
        None, description="Base64 encoded image data for image analysis"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional context for the query"
    )
    max_tokens: Optional[int] = Field(2000, description="Maximum tokens in response")
    temperature: Optional[float] = Field(0.7, description="LLM temperature parameter")


class ClassificationResult(BaseModel):
    """Result of query classification."""

    query_type: QueryType
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    features: Optional[Dict[str, Any]] = None


class LLMResponse(BaseModel):
    """Response from an LLM provider."""

    provider: LLMProvider
    content: str
    model: str
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class OrchestratorResponse(BaseModel):
    """Final response from the orchestrator."""

    response: str
    primary_llm: LLMProvider
    query_type: QueryType
    classification_confidence: float
    responses: List[LLMResponse] = Field(default_factory=list)
    is_hybrid: bool = False
    fallback_used: bool = False
    total_latency_ms: float
    metadata: Optional[Dict[str, Any]] = None
