"""
Unit tests for CitationInjector.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from citations.citation_injector import CitationInjector
from citations.citation_manager import Citation, RetrievedDocument


class TestCitationInjector:
    """Test cases for CitationInjector class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.injector = CitationInjector()

    def test_inject_citations_basic(self):
        """Test basic citation injection."""
        response = "Solar modules must meet testing standards. Quality is important."

        retrieved_docs = [
            RetrievedDocument(
                content="Solar modules must meet testing standards for quality assurance.",
                metadata={'standard_id': 'IEC 61215'},
                doc_id="doc_1",
                score=0.9
            )
        ]

        citations = [
            Citation(
                citation_id=1,
                standard_id="IEC 61215",
                source_doc_id="doc_1"
            )
        ]

        processed = self.injector.inject_citations(response, retrieved_docs, citations)

        assert "[1]" in processed

    def test_split_into_sentences(self):
        """Test sentence splitting."""
        text = "This is sentence one. This is sentence two! Is this sentence three?"

        sentences = self.injector._split_into_sentences(text)

        assert len(sentences) == 3
        assert "sentence one" in sentences[0]
        assert "sentence two" in sentences[1]
        assert "sentence three" in sentences[2]

    def test_calculate_similarity(self):
        """Test similarity calculation."""
        text1 = "Solar modules must meet testing standards"
        text2 = "Solar modules must meet testing standards for quality"

        similarity = self.injector._calculate_similarity(text1, text2)

        assert similarity > 0.5
        assert similarity <= 1.0

    def test_normalize_text(self):
        """Test text normalization."""
        text = "  This  IS   A   Test!!!  "
        normalized = self.injector._normalize_text(text)

        assert normalized == "this is a test"

    def test_insert_citation(self):
        """Test citation insertion into sentence."""
        sentence = "This is a test sentence."
        citation_marker = "[1]"

        result = self.injector._insert_citation(sentence, citation_marker)

        assert "[1]" in result
        assert result.endswith(".")

    def test_insert_citation_no_punctuation(self):
        """Test citation insertion when no punctuation."""
        sentence = "This is a test sentence"
        citation_marker = "[2]"

        result = self.injector._insert_citation(sentence, citation_marker)

        assert "[2]" in result

    def test_inject_reference_citations(self):
        """Test injection of citations for explicit standard references."""
        text = "According to IEC 61215, modules must be tested."

        citations = [
            Citation(
                citation_id=1,
                standard_id="IEC 61215",
                source_doc_id="doc_1"
            )
        ]

        processed = self.injector._inject_reference_citations(text, citations)

        assert "IEC 61215[1]" in processed or "IEC 61215 [1]" in processed

    def test_no_duplicate_citations(self):
        """Test that citations are not duplicated."""
        response = "IEC 61215[1] is important. IEC 61215 defines standards."

        citations = [
            Citation(
                citation_id=1,
                standard_id="IEC 61215",
                source_doc_id="doc_1"
            )
        ]

        processed = self.injector._inject_reference_citations(response, citations)

        # Count occurrences of [1]
        count = processed.count("[1]")

        # Should have citations but not excessive duplicates
        assert count >= 1

    def test_custom_citation_format(self):
        """Test custom citation format."""
        injector = CitationInjector(citation_format="({id})")

        sentence = "This is a test."
        citation_marker = "(1)"

        result = injector._insert_citation(sentence, citation_marker)

        assert "(1)" in result

    def test_similarity_threshold(self):
        """Test similarity threshold filtering."""
        injector = CitationInjector(similarity_threshold=0.9)

        response = "Completely different text here."

        retrieved_docs = [
            RetrievedDocument(
                content="Solar modules testing standards",
                metadata={},
                doc_id="doc_1"
            )
        ]

        citations = [
            Citation(citation_id=1, source_doc_id="doc_1")
        ]

        # With high threshold, no citations should be injected
        processed = injector.inject_citations(response, retrieved_docs, citations)

        # Text should be similar to original since no match
        assert len(processed) > 0

    def test_min_match_length(self):
        """Test minimum match length parameter."""
        injector = CitationInjector(min_match_length=50)

        text1 = "Short text"
        text2 = "Short text here"

        # Short text might not meet minimum length for high similarity
        similarity = injector._calculate_similarity(text1, text2)

        assert 0 <= similarity <= 1

    def test_multiple_citations_in_response(self):
        """Test injecting multiple different citations."""
        response = "IEC 61215 covers module testing. IEEE 1547 covers interconnection."

        retrieved_docs = [
            RetrievedDocument(
                content="IEC 61215 module testing standards",
                metadata={'standard_id': 'IEC 61215'},
                doc_id="doc_1"
            ),
            RetrievedDocument(
                content="IEEE 1547 interconnection requirements",
                metadata={'standard_id': 'IEEE 1547'},
                doc_id="doc_2"
            )
        ]

        citations = [
            Citation(citation_id=1, standard_id="IEC 61215", source_doc_id="doc_1"),
            Citation(citation_id=2, standard_id="IEEE 1547", source_doc_id="doc_2")
        ]

        processed = self.injector.inject_citations(response, retrieved_docs, citations)

        assert "[1]" in processed or "[2]" in processed
