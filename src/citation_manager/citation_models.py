"""Data models for citation management.

This module defines the core data structures used throughout the citation manager,
including document metadata, citation references, and formatted citations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field, validator


class CitationStyle(str, Enum):
    """Supported citation styles."""
    IEC = "iec"
    IEEE = "ieee"
    APA = "apa"
    ISO = "iso"


class DocumentType(str, Enum):
    """Types of documents that can be cited."""
    STANDARD = "standard"
    TECHNICAL_REPORT = "technical_report"
    ARTICLE = "article"
    BOOK = "book"
    WEBPAGE = "webpage"
    OTHER = "other"


class ClauseReference(BaseModel):
    """Represents a reference to a specific clause or section in a document."""

    document_id: str = Field(..., description="Unique identifier for the source document")
    clause_number: str = Field(..., description="Clause/section number (e.g., '5.2.1', 'Annex A')")
    clause_title: Optional[str] = Field(None, description="Title of the clause/section")
    page_number: Optional[int] = Field(None, description="Page number if available")
    excerpt: Optional[str] = Field(None, description="Relevant text excerpt from the clause")

    class Config:
        frozen = True  # Make immutable for use as dict keys


class StandardMetadata(BaseModel):
    """Metadata for technical standards (IEC, IEEE, ISO, etc.)."""

    standard_id: str = Field(..., description="Standard identifier (e.g., 'IEC 61730-1:2016')")
    title: str = Field(..., description="Full title of the standard")
    organization: str = Field(..., description="Standards organization (e.g., 'IEC', 'IEEE')")
    year: Optional[int] = Field(None, description="Year of publication")
    edition: Optional[str] = Field(None, description="Edition number (e.g., '2nd edition')")
    amendment: Optional[str] = Field(None, description="Amendment information")
    url: Optional[str] = Field(None, description="URL to the standard")
    isbn: Optional[str] = Field(None, description="ISBN if applicable")

    @validator('year')
    def validate_year(cls, v):
        """Validate that year is reasonable."""
        if v is not None and (v < 1900 or v > datetime.now().year + 1):
            raise ValueError(f"Year {v} is not valid")
        return v


class DocumentMetadata(BaseModel):
    """Complete metadata for a source document."""

    document_id: str = Field(..., description="Unique identifier")
    document_type: DocumentType = Field(..., description="Type of document")
    title: str = Field(..., description="Document title")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    year: Optional[int] = Field(None, description="Publication year")
    publisher: Optional[str] = Field(None, description="Publisher name")
    url: Optional[str] = Field(None, description="Document URL")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")

    # For standards
    standard_metadata: Optional[StandardMetadata] = Field(None, description="Additional metadata for standards")

    # Document content metadata
    total_pages: Optional[int] = Field(None, description="Total number of pages")
    language: str = Field(default="en", description="Document language")

    # Tracking
    retrieved_date: Optional[datetime] = Field(None, description="When document was retrieved/indexed")
    file_path: Optional[str] = Field(None, description="Local file path if available")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Citation(BaseModel):
    """Represents a citation instance in a response."""

    citation_number: int = Field(..., description="Sequential citation number in the response")
    document_id: str = Field(..., description="Referenced document ID")
    clause_references: List[ClauseReference] = Field(
        default_factory=list,
        description="Specific clauses/sections referenced"
    )
    matched_text: Optional[str] = Field(None, description="Text in response that triggered citation")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score for citation match")

    def __hash__(self):
        """Make Citation hashable for set operations."""
        return hash((self.citation_number, self.document_id))


class FormattedCitation(BaseModel):
    """A fully formatted citation ready for display."""

    citation_number: int = Field(..., description="Citation number")
    inline_format: str = Field(..., description="Inline citation format (e.g., '[1]')")
    reference_format: str = Field(..., description="Full reference list format")
    style: CitationStyle = Field(..., description="Citation style used")


@dataclass
class ResponseCitations:
    """Container for all citations in a single response."""

    response_id: str
    citations: List[Citation] = field(default_factory=list)
    formatted_citations: List[FormattedCitation] = field(default_factory=list)
    referenced_documents: Dict[str, DocumentMetadata] = field(default_factory=dict)

    def add_citation(self, citation: Citation):
        """Add a citation to this response."""
        self.citations.append(citation)

    def get_citation_by_number(self, number: int) -> Optional[Citation]:
        """Get citation by its number."""
        for citation in self.citations:
            if citation.citation_number == number:
                return citation
        return None

    def get_unique_documents(self) -> Set[str]:
        """Get set of unique document IDs referenced."""
        return {citation.document_id for citation in self.citations}

    def get_citations_for_document(self, document_id: str) -> List[Citation]:
        """Get all citations for a specific document."""
        return [c for c in self.citations if c.document_id == document_id]


class CitationExtractionResult(BaseModel):
    """Result from citation extraction process."""

    original_text: str = Field(..., description="Original response text")
    text_with_citations: str = Field(..., description="Text with inline citations inserted")
    citations_found: List[Citation] = Field(default_factory=list, description="Citations extracted")
    reference_section: str = Field(default="", description="Formatted reference section")
    extraction_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about extraction process"
    )
