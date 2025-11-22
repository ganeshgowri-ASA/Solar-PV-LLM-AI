"""
Metadata schema for IEC standards documents and chunks.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class IECMetadata(BaseModel):
    """Metadata for IEC standard documents."""

    standard_id: str = Field(..., description="IEC standard identifier (e.g., IEC 61215-1)")
    edition: Optional[str] = Field(None, description="Edition number (e.g., '4.0', '2021')")
    year: Optional[int] = Field(None, description="Publication year")
    title: str = Field(..., description="Full title of the standard")
    scope: Optional[str] = Field(None, description="Scope of the standard")
    keywords: List[str] = Field(default_factory=list, description="Key terms and topics")

    class Config:
        json_schema_extra = {
            "example": {
                "standard_id": "IEC 61215-1",
                "edition": "4.0",
                "year": 2021,
                "title": "Terrestrial photovoltaic (PV) modules - Design qualification and type approval",
                "scope": "Design qualification and type approval for crystalline silicon PV modules",
                "keywords": ["photovoltaic", "PV modules", "design qualification"]
            }
        }


class ClauseMetadata(BaseModel):
    """Metadata for IEC standard clauses and sections."""

    clause_number: str = Field(..., description="Clause number (e.g., '5.2.3')")
    clause_title: str = Field(..., description="Title of the clause")
    parent_clause: Optional[str] = Field(None, description="Parent clause number")
    level: int = Field(..., description="Hierarchical level (1 for main, 2 for sub, etc.)")
    section_type: str = Field(..., description="Type: clause, annex, figure, table, note")

    class Config:
        json_schema_extra = {
            "example": {
                "clause_number": "5.2.3",
                "clause_title": "Thermal cycling test",
                "parent_clause": "5.2",
                "level": 3,
                "section_type": "clause"
            }
        }


class ChunkMetadata(BaseModel):
    """Complete metadata for a text chunk from IEC standard."""

    # Document-level metadata
    document: IECMetadata

    # Clause-level metadata
    clause: ClauseMetadata

    # Chunk-specific metadata
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    chunk_index: int = Field(..., description="Sequential index of chunk in document")
    page_numbers: List[int] = Field(..., description="Page numbers where chunk appears")
    char_count: int = Field(..., description="Character count of chunk")
    word_count: int = Field(..., description="Word count of chunk")

    # Context metadata
    previous_chunk_id: Optional[str] = Field(None, description="ID of previous chunk")
    next_chunk_id: Optional[str] = Field(None, description="ID of next chunk")
    related_clauses: List[str] = Field(default_factory=list, description="Related clause references")

    # Processing metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processing_version: str = Field(default="0.1.0", description="Version of processing pipeline")

    class Config:
        json_schema_extra = {
            "example": {
                "document": {
                    "standard_id": "IEC 61215-1",
                    "edition": "4.0",
                    "year": 2021,
                    "title": "Terrestrial PV modules",
                    "keywords": ["photovoltaic"]
                },
                "clause": {
                    "clause_number": "5.2.3",
                    "clause_title": "Thermal cycling test",
                    "level": 3,
                    "section_type": "clause"
                },
                "chunk_id": "iec-61215-1_chunk_042",
                "chunk_index": 42,
                "page_numbers": [15, 16],
                "char_count": 856,
                "word_count": 142
            }
        }


class DocumentMetadata(BaseModel):
    """High-level metadata for processed document."""

    source_file: str = Field(..., description="Original PDF filename")
    iec_metadata: IECMetadata
    total_chunks: int = Field(..., description="Total number of chunks created")
    total_pages: int = Field(..., description="Total pages in document")
    total_characters: int = Field(..., description="Total characters in document")
    processing_date: datetime = Field(default_factory=datetime.utcnow)
    chunk_statistics: Dict[str, Any] = Field(default_factory=dict, description="Statistics about chunks")

    class Config:
        json_schema_extra = {
            "example": {
                "source_file": "IEC_61215-1_2021.pdf",
                "total_chunks": 156,
                "total_pages": 48,
                "total_characters": 89234,
                "chunk_statistics": {
                    "avg_chunk_size": 572,
                    "min_chunk_size": 100,
                    "max_chunk_size": 1200
                }
            }
        }


class QAPair(BaseModel):
    """Question-Answer pair generated from a chunk."""

    question: str = Field(..., description="Generated question")
    answer: str = Field(..., description="Answer extracted from chunk")
    chunk_id: str = Field(..., description="Source chunk ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    question_type: str = Field(..., description="Type: factual, procedural, conceptual, etc.")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the temperature range for the thermal cycling test?",
                "answer": "The thermal cycling test uses temperatures from -40°C to +85°C",
                "chunk_id": "iec-61215-1_chunk_042",
                "confidence": 0.92,
                "question_type": "factual"
            }
        }


class ProcessedChunk(BaseModel):
    """Complete processed chunk with text, metadata, and Q&A pairs."""

    text: str = Field(..., description="Chunk text content")
    metadata: ChunkMetadata
    qa_pairs: List[QAPair] = Field(default_factory=list, description="Generated Q&A pairs")
    embeddings: Optional[List[float]] = Field(None, description="Text embeddings (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "The thermal cycling test subjects the module to...",
                "metadata": {"chunk_id": "iec-61215-1_chunk_042"},
                "qa_pairs": [
                    {
                        "question": "What does the thermal cycling test evaluate?",
                        "answer": "Module performance under temperature variations",
                        "chunk_id": "iec-61215-1_chunk_042",
                        "confidence": 0.89,
                        "question_type": "conceptual"
                    }
                ]
            }
        }
