"""Data models for RAG engine."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class Document(BaseModel):
    """Document model with content and metadata."""

    id: str = Field(..., description="Unique document identifier")
    content: str = Field(..., description="Document text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    embedding: Optional[List[float]] = Field(default=None, description="Document embedding vector")

    class Config:
        arbitrary_types_allowed = True


class RetrievalResult(BaseModel):
    """Result from retrieval operation."""

    document: Document
    score: float = Field(..., description="Relevance score")
    rank: int = Field(..., description="Rank position")
    retrieval_method: str = Field(..., description="Method used for retrieval")

    class Config:
        arbitrary_types_allowed = True


class RAGContext(BaseModel):
    """Context assembled for RAG prompt."""

    query: str = Field(..., description="Original query")
    retrieved_docs: List[RetrievalResult] = Field(..., description="Retrieved documents")
    context_text: str = Field(..., description="Formatted context text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True

    def format_context(self, template: Optional[str] = None) -> str:
        """
        Format context for prompt.

        Args:
            template: Optional custom template for formatting

        Returns:
            Formatted context string
        """
        if template:
            return template.format(
                query=self.query,
                context=self.context_text,
                metadata=self.metadata
            )

        # Default formatting
        context_parts = []
        for i, result in enumerate(self.retrieved_docs, 1):
            doc_text = f"[{i}] {result.document.content}"
            if result.document.metadata:
                metadata_str = ", ".join(
                    f"{k}: {v}" for k, v in result.document.metadata.items()
                    if k not in ['embedding', 'id']
                )
                if metadata_str:
                    doc_text += f"\n(Metadata: {metadata_str})"
            context_parts.append(doc_text)

        return "\n\n".join(context_parts)
