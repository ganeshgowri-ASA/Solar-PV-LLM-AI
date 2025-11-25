"""
Unit tests for CitationManager and CitationTracker.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from citations.citation_manager import (
    CitationManager,
    CitationTracker,
    Citation,
    RetrievedDocument
)


class TestCitationTracker:
    """Test cases for CitationTracker class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = CitationTracker()

    def test_add_citation(self):
        """Test adding a citation."""
        citation = Citation(
            citation_id=0,
            standard_id="IEC 61215",
            title="PV Module Testing"
        )

        citation_id = self.tracker.add_citation(citation)

        assert citation_id == 1
        assert citation.citation_id == 1
        assert len(self.tracker.get_citations()) == 1

    def test_increment_citation_numbers(self):
        """Test that citation numbers increment correctly."""
        citation1 = Citation(citation_id=0, standard_id="IEC 61215")
        citation2 = Citation(citation_id=0, standard_id="IEC 61730")

        id1 = self.tracker.add_citation(citation1)
        id2 = self.tracker.add_citation(citation2)

        assert id1 == 1
        assert id2 == 2

    def test_duplicate_citation_detection(self):
        """Test that duplicate citations use the same ID."""
        citation1 = Citation(
            citation_id=0,
            standard_id="IEC 61215",
            clause_ref="Clause 5.2"
        )
        citation2 = Citation(
            citation_id=0,
            standard_id="IEC 61215",
            clause_ref="Clause 5.2"
        )

        id1 = self.tracker.add_citation(citation1)
        id2 = self.tracker.add_citation(citation2)

        assert id1 == id2
        assert len(self.tracker.get_citations()) == 1

    def test_reset_tracker(self):
        """Test resetting the tracker."""
        citation = Citation(citation_id=0, standard_id="IEC 61215")
        self.tracker.add_citation(citation)

        assert len(self.tracker.get_citations()) == 1

        self.tracker.reset()

        assert len(self.tracker.get_citations()) == 0
        assert self.tracker.current_index == 1

    def test_custom_start_index(self):
        """Test starting from a custom index."""
        tracker = CitationTracker(start_index=5)
        citation = Citation(citation_id=0, standard_id="IEC 61215")

        citation_id = tracker.add_citation(citation)

        assert citation_id == 5


class TestCitationManager:
    """Test cases for CitationManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = CitationManager()

    def test_process_response_basic(self):
        """Test basic response processing."""
        llm_response = "Solar modules must meet IEC 61215 standards."

        retrieved_docs = [
            RetrievedDocument(
                content="IEC 61215 defines testing requirements for PV modules.",
                metadata={
                    'standard_id': 'IEC 61215',
                    'title': 'PV Module Testing',
                    'year': '2021'
                },
                doc_id="doc_1",
                score=0.9
            )
        ]

        processed_response, citations = self.manager.process_response(
            llm_response,
            retrieved_docs,
            inject_citations=True
        )

        assert len(citations) == 1
        assert citations[0].standard_id == 'IEC 61215'
        assert "[1]" in processed_response

    def test_reset_per_response(self):
        """Test that citation numbers reset for each response."""
        doc1 = RetrievedDocument(
            content="Content 1",
            metadata={'standard_id': 'IEC 61215'},
            doc_id="doc_1"
        )

        # First response
        _, citations1 = self.manager.process_response(
            "First response",
            [doc1],
            inject_citations=False
        )

        # Second response
        _, citations2 = self.manager.process_response(
            "Second response",
            [doc1],
            inject_citations=False
        )

        # Both should start from 1
        assert citations1[0].citation_id == 1
        assert citations2[0].citation_id == 1

    def test_no_reset_per_response(self):
        """Test citation numbers don't reset when disabled."""
        manager = CitationManager(reset_per_response=False)

        doc1 = RetrievedDocument(
            content="Content 1",
            metadata={'standard_id': 'IEC 61215'},
            doc_id="doc_1"
        )
        doc2 = RetrievedDocument(
            content="Content 2",
            metadata={'standard_id': 'IEC 61730'},
            doc_id="doc_2"
        )

        # First response
        _, citations1 = manager.process_response(
            "First response",
            [doc1],
            inject_citations=False
        )

        # Second response
        _, citations2 = manager.process_response(
            "Second response",
            [doc2],
            inject_citations=False
        )

        # Should continue incrementing - citations2 contains ALL citations
        assert len(citations1) == 1, f"Expected 1 citation in citations1, got {len(citations1)}"
        assert citations1[0].citation_id == 1
        assert len(citations2) == 2, f"Expected 2 citations in citations2, got {len(citations2)}"  # Contains both citations
        assert citations2[1].citation_id == 2  # Check the new citation

    def test_format_references_iec(self):
        """Test formatting references in IEC style."""
        citations = [
            Citation(
                citation_id=1,
                standard_id="IEC 61215",
                title="PV Module Testing",
                year="2021",
                clause_ref="Clause 5.2"
            )
        ]

        formatted = self.manager.format_references(citations, style='iec')

        assert "References" in formatted
        assert "[1]" in formatted
        assert "IEC 61215" in formatted
        assert "2021" in formatted

    def test_multiple_documents(self):
        """Test processing multiple retrieved documents."""
        llm_response = "Testing standards are important."

        retrieved_docs = [
            RetrievedDocument(
                content="IEC 61215 content",
                metadata={'standard_id': 'IEC 61215'},
                doc_id="doc_1"
            ),
            RetrievedDocument(
                content="IEC 61730 content",
                metadata={'standard_id': 'IEC 61730'},
                doc_id="doc_2"
            ),
            RetrievedDocument(
                content="ISO 9001 content",
                metadata={'standard_id': 'ISO 9001'},
                doc_id="doc_3"
            )
        ]

        _, citations = self.manager.process_response(
            llm_response,
            retrieved_docs,
            inject_citations=False
        )

        assert len(citations) == 3
        assert citations[0].citation_id == 1
        assert citations[1].citation_id == 2
        assert citations[2].citation_id == 3

    def test_get_citations(self):
        """Test getting citations from manager."""
        doc = RetrievedDocument(
            content="Content",
            metadata={'standard_id': 'IEC 61215'},
            doc_id="doc_1"
        )

        self.manager.process_response(
            "Response",
            [doc],
            inject_citations=False
        )

        citations = self.manager.get_citations()

        assert len(citations) == 1
        assert citations[0].standard_id == 'IEC 61215'
