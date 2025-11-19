"""
Tests for the IEC PDF ingestion pipeline.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.metadata import IECMetadataExtractor, IECMetadata, ClauseMetadata
from src.chunking import SemanticChunker, ChunkConfig
from src.qa_generation import QAGenerator, QAConfig


class TestMetadataExtractor:
    """Test metadata extraction."""

    def test_extract_standard_id(self):
        """Test standard ID extraction."""
        extractor = IECMetadataExtractor()

        # Test various formats
        test_cases = [
            ("IEC 61215-1:2021 Photovoltaic modules", "IEC 61215-1"),
            ("IEC/TS 62804-1 Test methods", "IEC/TS 62804-1"),
            ("Standard IEC 60904-1", "IEC 60904-1"),
        ]

        for text, expected in test_cases:
            result = extractor.extract_standard_id(text)
            assert expected in result

    def test_extract_year(self):
        """Test year extraction."""
        extractor = IECMetadataExtractor()

        text = "© IEC 2021 - Photovoltaic modules"
        year = extractor.extract_year(text)
        assert year == 2021

    def test_extract_edition(self):
        """Test edition extraction."""
        extractor = IECMetadataExtractor()

        test_cases = [
            ("Edition 4.0", "4.0"),
            ("Fourth edition", "4.0"),
            ("2nd edition", "2.0"),
        ]

        for text, expected in test_cases:
            result = extractor.extract_edition(text)
            assert result == expected

    def test_parse_clause_number(self):
        """Test clause parsing."""
        extractor = IECMetadataExtractor()

        clause_text = "5.2.3 Thermal cycling test"
        result = extractor.parse_clause_number(clause_text)

        assert result is not None
        assert result['clause_number'] == "5.2.3"
        assert result['clause_title'] == "Thermal cycling test"
        assert result['level'] == 3
        assert result['parent_clause'] == "5.2"


class TestSemanticChunker:
    """Test semantic chunking."""

    def test_chunk_by_paragraphs(self):
        """Test paragraph-based chunking."""
        config = ChunkConfig(chunk_size=100, chunk_overlap=20)
        chunker = SemanticChunker(config)

        text = """This is paragraph one. It contains some text.

This is paragraph two. It has different content.

This is paragraph three. More information here."""

        chunks = chunker.chunk_text(text)

        assert len(chunks) > 0
        assert all('text' in c for c in chunks)
        assert all('chunk_method' in c for c in chunks)

    def test_chunk_size_limits(self):
        """Test chunk size constraints."""
        config = ChunkConfig(
            chunk_size=500,
            min_chunk_size=100,
            max_chunk_size=1000
        )
        chunker = SemanticChunker(config)

        # Generate long text
        text = " ".join(["Test sentence."] * 200)
        chunks = chunker.chunk_text(text)

        for chunk in chunks:
            chunk_size = len(chunk['text'])
            assert chunk_size >= config.min_chunk_size or chunk_size == len(text)
            assert chunk_size <= config.max_chunk_size

    def test_chunk_overlap(self):
        """Test chunk overlap."""
        config = ChunkConfig(chunk_size=100, chunk_overlap=20)
        chunker = SemanticChunker(config)

        text = " ".join(["Word"] * 100)
        chunks = chunker.chunk_text(text)

        if len(chunks) > 1:
            # Check that chunks have overlap
            assert any(c.get('has_overlap') for c in chunks)


class TestQAGenerator:
    """Test Q&A generation."""

    def test_rule_based_generation(self):
        """Test rule-based Q&A generation."""
        config = QAConfig()
        generator = QAGenerator(config)

        text = """The thermal cycling test shall be performed at temperatures
        ranging from -40°C to +85°C. The module is defined as a photovoltaic
        panel assembly."""

        qa_pairs = generator._generate_rule_based(
            text=text,
            chunk_id="test_001",
            clause_number="5.2.3",
            clause_title="Thermal cycling test"
        )

        assert len(qa_pairs) > 0
        assert all(qa.question for qa in qa_pairs)
        assert all(qa.answer for qa in qa_pairs)
        assert all(qa.chunk_id == "test_001" for qa in qa_pairs)

    def test_qa_validation(self):
        """Test Q&A pair validation."""
        config = QAConfig(min_confidence=0.7)
        generator = QAGenerator(config)

        from src.metadata.schema import QAPair

        # Valid Q&A pair
        qa_pair = QAPair(
            question="What is the temperature range?",
            answer="The temperature ranges from -40°C to +85°C",
            chunk_id="test",
            confidence=0.9,
            question_type="factual"
        )

        source_text = "The test is performed at temperatures from -40°C to +85°C"
        assert generator.validate_qa_pair(qa_pair, source_text)

        # Invalid Q&A pair (answer not in source)
        qa_pair_invalid = QAPair(
            question="What is the voltage?",
            answer="The voltage is 1000V",
            chunk_id="test",
            confidence=0.9,
            question_type="factual"
        )
        assert not generator.validate_qa_pair(qa_pair_invalid, source_text)


class TestChunkStatistics:
    """Test chunk statistics calculation."""

    def test_statistics_calculation(self):
        """Test statistics calculation."""
        chunker = SemanticChunker()

        chunks = [
            {'text': 'a' * 100},
            {'text': 'b' * 200},
            {'text': 'c' * 150},
        ]

        stats = chunker.get_chunk_statistics(chunks)

        assert stats['total_chunks'] == 3
        assert stats['total_characters'] == 450
        assert stats['avg_chunk_size'] == 150
        assert stats['min_chunk_size'] == 100
        assert stats['max_chunk_size'] == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
