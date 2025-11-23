"""IEC PDF Ingestion Pipeline.

This module provides tools for ingesting IEC standards PDFs with:
- Structure-preserving loading
- Metadata extraction
- Intelligent semantic chunking
- Q&A pair generation
- Structured JSON output
"""

from .models import (
    DocumentMetadata,
    ClauseInfo,
    Chunk,
    QAPair,
    ProcessedDocument,
    IngestionConfig,
)
from .pdf_loader import IECPDFLoader
from .metadata_extractor import MetadataExtractor
from .chunker import ClauseAwareChunker
from .qa_generator import QAGenerator
from .storage import DocumentStorage
from .pipeline import IngestionPipeline
from .api import IECIngestionAPI, quick_ingest, load_document
from .validation import DocumentValidator, quick_validate, print_validation_report

__all__ = [
    "DocumentMetadata",
    "ClauseInfo",
    "Chunk",
    "QAPair",
    "ProcessedDocument",
    "IngestionConfig",
    "IECPDFLoader",
    "MetadataExtractor",
    "ClauseAwareChunker",
    "QAGenerator",
    "DocumentStorage",
    "IngestionPipeline",
    "IECIngestionAPI",
    "quick_ingest",
    "load_document",
    "DocumentValidator",
    "quick_validate",
    "print_validation_report",
]
