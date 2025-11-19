"""
Tests for metadata schemas and extraction.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.metadata.schema import (
    IECMetadata,
    ClauseMetadata,
    ChunkMetadata,
    QAPair,
    ProcessedChunk
)


class TestMetadataSchemas:
    """Test Pydantic metadata schemas."""

    def test_iec_metadata_creation(self):
        """Test IEC metadata model."""
        metadata = IECMetadata(
            standard_id="IEC 61215-1",
            edition="4.0",
            year=2021,
            title="Terrestrial photovoltaic (PV) modules",
            keywords=["photovoltaic", "PV", "modules"]
        )

        assert metadata.standard_id == "IEC 61215-1"
        assert metadata.edition == "4.0"
        assert metadata.year == 2021
        assert len(metadata.keywords) == 3

    def test_clause_metadata_creation(self):
        """Test clause metadata model."""
        clause = ClauseMetadata(
            clause_number="5.2.3",
            clause_title="Thermal cycling test",
            parent_clause="5.2",
            level=3,
            section_type="clause"
        )

        assert clause.clause_number == "5.2.3"
        assert clause.level == 3
        assert clause.parent_clause == "5.2"

    def test_qa_pair_creation(self):
        """Test Q&A pair model."""
        qa = QAPair(
            question="What is the temperature range?",
            answer="-40°C to +85°C",
            chunk_id="chunk_001",
            confidence=0.92,
            question_type="factual"
        )

        assert qa.confidence >= 0.0 and qa.confidence <= 1.0
        assert qa.question_type in ["factual", "procedural", "conceptual", "comparative", "conditional"]

    def test_chunk_metadata_defaults(self):
        """Test chunk metadata with defaults."""
        doc_meta = IECMetadata(
            standard_id="IEC 61215-1",
            title="Test Standard"
        )

        clause_meta = ClauseMetadata(
            clause_number="5",
            clause_title="Test",
            level=1,
            section_type="clause"
        )

        chunk_meta = ChunkMetadata(
            document=doc_meta,
            clause=clause_meta,
            chunk_id="test_001",
            chunk_index=0,
            page_numbers=[1],
            char_count=500,
            word_count=100
        )

        # Check defaults
        assert isinstance(chunk_meta.created_at, datetime)
        assert chunk_meta.processing_version == "0.1.0"
        assert chunk_meta.related_clauses == []

    def test_processed_chunk_complete(self):
        """Test complete processed chunk."""
        doc_meta = IECMetadata(
            standard_id="IEC 61215-1",
            title="Test"
        )

        clause_meta = ClauseMetadata(
            clause_number="5",
            clause_title="Test",
            level=1,
            section_type="clause"
        )

        chunk_meta = ChunkMetadata(
            document=doc_meta,
            clause=clause_meta,
            chunk_id="test_001",
            chunk_index=0,
            page_numbers=[1],
            char_count=100,
            word_count=20
        )

        qa_pair = QAPair(
            question="Test question?",
            answer="Test answer",
            chunk_id="test_001",
            confidence=0.8,
            question_type="factual"
        )

        chunk = ProcessedChunk(
            text="This is test text for the chunk.",
            metadata=chunk_meta,
            qa_pairs=[qa_pair]
        )

        assert len(chunk.text) > 0
        assert len(chunk.qa_pairs) == 1
        assert chunk.metadata.chunk_id == "test_001"

    def test_metadata_serialization(self):
        """Test metadata can be serialized to JSON."""
        doc_meta = IECMetadata(
            standard_id="IEC 61215-1",
            title="Test"
        )

        # Convert to dict
        data = doc_meta.model_dump(mode='json')

        assert isinstance(data, dict)
        assert data['standard_id'] == "IEC 61215-1"

        # Recreate from dict
        doc_meta_2 = IECMetadata(**data)
        assert doc_meta_2.standard_id == doc_meta.standard_id


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
