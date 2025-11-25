"""Data models for IEC PDF ingestion pipeline."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class ClauseInfo(BaseModel):
    """Information about a clause/section in the IEC document."""

    clause_number: str = Field(..., description="Clause number (e.g., '4.2.1')")
    title: Optional[str] = Field(None, description="Clause title")
    level: int = Field(..., description="Nesting level (1 for top-level, 2 for sub-clause, etc.)")
    parent_clause: Optional[str] = Field(None, description="Parent clause number")
    page_start: Optional[int] = Field(None, description="Starting page number")
    page_end: Optional[int] = Field(None, description="Ending page number")

    @validator("clause_number")
    def validate_clause_number(cls, v):
        """Validate clause number format."""
        if not v or not v[0].isdigit():
            raise ValueError("Clause number must start with a digit")
        return v

    @validator("level")
    def validate_level(cls, v):
        """Validate level is positive."""
        if v < 1:
            raise ValueError("Level must be at least 1")
        return v


class DocumentMetadata(BaseModel):
    """Metadata extracted from IEC standard document."""

    standard_id: Optional[str] = Field(None, description="IEC standard ID (e.g., 'IEC 61730-1')")
    standard_type: Optional[str] = Field(
        None, description="Standard type (e.g., 'IEC', 'IEC TR', 'IEC TS')"
    )
    edition: Optional[str] = Field(None, description="Edition number or version")
    year: Optional[int] = Field(None, description="Publication year")
    title: Optional[str] = Field(None, description="Document title")
    total_pages: Optional[int] = Field(None, description="Total number of pages")
    language: Optional[str] = Field(default="en", description="Document language")
    extracted_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of extraction"
    )
    file_path: Optional[str] = Field(None, description="Original PDF file path")
    file_size_bytes: Optional[int] = Field(None, description="PDF file size in bytes")

    @validator("year")
    def validate_year(cls, v):
        """Validate year is reasonable."""
        if v is not None and (v < 1900 or v > 2100):
            raise ValueError("Year must be between 1900 and 2100")
        return v


class QAPair(BaseModel):
    """Atomic question-answer pair for retrieval."""

    question: str = Field(..., description="Generated question")
    answer: str = Field(..., description="Answer derived from chunk")
    question_type: Optional[str] = Field(
        None, description="Type of question (factual, conceptual, application)"
    )
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence score (0-1)"
    )
    keywords: List[str] = Field(default_factory=list, description="Key terms in Q&A pair")


class Chunk(BaseModel):
    """A chunk of text from the document with metadata."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., description="Text content of the chunk")
    clause_info: Optional[ClauseInfo] = Field(None, description="Associated clause information")
    page_numbers: List[int] = Field(default_factory=list, description="Page numbers in chunk")
    char_count: int = Field(..., description="Character count")
    word_count: int = Field(..., description="Word count")
    chunk_index: int = Field(..., description="Sequential index in document")
    overlap_with_previous: bool = Field(
        default=False, description="Whether chunk overlaps with previous"
    )
    overlap_with_next: bool = Field(default=False, description="Whether chunk overlaps with next")
    qa_pairs: List[QAPair] = Field(default_factory=list, description="Generated Q&A pairs")
    embedding_vector: Optional[List[float]] = Field(
        None, description="Optional embedding vector"
    )

    @validator("content")
    def validate_content(cls, v):
        """Validate content is not empty."""
        if not v or not v.strip():
            raise ValueError("Chunk content cannot be empty")
        return v

    @validator("char_count", "word_count", "chunk_index")
    def validate_positive(cls, v):
        """Validate counts are positive."""
        if v < 0:
            raise ValueError("Count must be non-negative")
        return v


class ProcessedDocument(BaseModel):
    """Complete processed document with all chunks and metadata."""

    document_id: str = Field(..., description="Unique document identifier")
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    chunks: List[Chunk] = Field(..., description="All document chunks")
    clauses: List[ClauseInfo] = Field(default_factory=list, description="All extracted clauses")
    processing_stats: Dict[str, Any] = Field(
        default_factory=dict, description="Processing statistics"
    )
    processed_at: datetime = Field(
        default_factory=datetime.utcnow, description="Processing timestamp"
    )

    @validator("chunks")
    def validate_chunks(cls, v):
        """Validate at least one chunk exists."""
        if not v:
            raise ValueError("Document must have at least one chunk")
        return v

    def get_chunk_count(self) -> int:
        """Get total number of chunks."""
        return len(self.chunks)

    def get_total_qa_pairs(self) -> int:
        """Get total number of Q&A pairs across all chunks."""
        return sum(len(chunk.qa_pairs) for chunk in self.chunks)

    def get_chunks_by_clause(self, clause_number: str) -> List[Chunk]:
        """Get all chunks for a specific clause."""
        return [
            chunk
            for chunk in self.chunks
            if chunk.clause_info and chunk.clause_info.clause_number == clause_number
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive document statistics."""
        return {
            "total_chunks": self.get_chunk_count(),
            "total_qa_pairs": self.get_total_qa_pairs(),
            "total_clauses": len(self.clauses),
            "total_characters": sum(chunk.char_count for chunk in self.chunks),
            "total_words": sum(chunk.word_count for chunk in self.chunks),
            "avg_chunk_size": (
                sum(chunk.char_count for chunk in self.chunks) / len(self.chunks)
                if self.chunks
                else 0
            ),
            "chunks_with_qa": sum(1 for chunk in self.chunks if chunk.qa_pairs),
            "metadata": self.metadata.dict(),
        }


class IngestionConfig(BaseModel):
    """Configuration for ingestion pipeline."""

    pdf_extract_images: bool = False
    pdf_extract_tables: bool = True
    pdf_preserve_layout: bool = True

    chunk_size: int = Field(1000, ge=100, le=10000)
    chunk_overlap: int = Field(200, ge=0, le=1000)
    clause_aware: bool = True
    min_chunk_size: int = Field(100, ge=50)
    max_chunk_size: int = Field(2000, ge=500)

    qa_enabled: bool = True
    qa_provider: str = Field("anthropic", pattern="^(openai|anthropic)$")
    qa_model: str = "claude-3-haiku-20240307"
    qa_temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_questions_per_chunk: int = Field(3, ge=1, le=10)

    output_format: str = Field("json", pattern="^(json|jsonl)$")
    include_metadata: bool = True
    include_source: bool = True
    include_qa: bool = True
    pretty_print: bool = True
    output_dir: str = "data/output"

    log_level: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    @validator("chunk_overlap")
    def validate_overlap(cls, v, values):
        """Validate overlap is less than chunk size."""
        if "chunk_size" in values and v >= values["chunk_size"]:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return v
