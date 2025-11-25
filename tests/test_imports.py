"""Test that all modules can be imported correctly."""

import pytest


def test_import_models():
    """Test importing data models."""
    from src.ingestion.models import (
        DocumentMetadata,
        ClauseInfo,
        Chunk,
        QAPair,
        ProcessedDocument,
        IngestionConfig,
    )
    assert DocumentMetadata is not None
    assert ClauseInfo is not None
    assert Chunk is not None
    assert QAPair is not None
    assert ProcessedDocument is not None
    assert IngestionConfig is not None


def test_import_pdf_loader():
    """Test importing PDF loader."""
    from src.ingestion.pdf_loader import IECPDFLoader
    assert IECPDFLoader is not None


def test_import_metadata_extractor():
    """Test importing metadata extractor."""
    from src.ingestion.metadata_extractor import MetadataExtractor
    assert MetadataExtractor is not None


def test_import_chunker():
    """Test importing chunker."""
    from src.ingestion.chunker import ClauseAwareChunker
    assert ClauseAwareChunker is not None


def test_import_qa_generator():
    """Test importing Q&A generator."""
    from src.ingestion.qa_generator import QAGenerator
    assert QAGenerator is not None


def test_import_storage():
    """Test importing storage."""
    from src.ingestion.storage import DocumentStorage
    assert DocumentStorage is not None


def test_import_pipeline():
    """Test importing pipeline."""
    from src.ingestion.pipeline import IngestionPipeline
    assert IngestionPipeline is not None


def test_import_api():
    """Test importing API."""
    from src.ingestion.api import IECIngestionAPI, quick_ingest, load_document
    assert IECIngestionAPI is not None
    assert quick_ingest is not None
    assert load_document is not None


def test_import_validation():
    """Test importing validation."""
    from src.ingestion.validation import (
        DocumentValidator,
        quick_validate,
        print_validation_report,
    )
    assert DocumentValidator is not None
    assert quick_validate is not None
    assert print_validation_report is not None


def test_create_config():
    """Test creating IngestionConfig."""
    from src.ingestion.models import IngestionConfig

    config = IngestionConfig()
    assert config.chunk_size == 1000
    assert config.chunk_overlap == 200
    assert config.clause_aware is True


def test_create_metadata():
    """Test creating DocumentMetadata."""
    from src.ingestion.models import DocumentMetadata

    metadata = DocumentMetadata(
        standard_id="IEC 61730-1",
        edition="2.0",
        year=2023,
    )
    assert metadata.standard_id == "IEC 61730-1"
    assert metadata.edition == "2.0"
    assert metadata.year == 2023


def test_create_clause_info():
    """Test creating ClauseInfo."""
    from src.ingestion.models import ClauseInfo

    clause = ClauseInfo(
        clause_number="4.2.1",
        title="Temperature Testing",
        level=3,
        parent_clause="4.2",
    )
    assert clause.clause_number == "4.2.1"
    assert clause.title == "Temperature Testing"
    assert clause.level == 3


def test_create_chunk():
    """Test creating Chunk."""
    from src.ingestion.models import Chunk, ClauseInfo

    clause = ClauseInfo(
        clause_number="4.2.1",
        title="Temperature Testing",
        level=3,
    )

    chunk = Chunk(
        chunk_id="test-chunk-123",
        content="This is test content for the chunk.",
        clause_info=clause,
        page_numbers=[10, 11],
        char_count=35,
        word_count=7,
        chunk_index=0,
    )

    assert chunk.chunk_id == "test-chunk-123"
    assert chunk.char_count == 35
    assert chunk.word_count == 7
    assert chunk.clause_info.clause_number == "4.2.1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
