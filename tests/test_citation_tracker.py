"""Unit tests for CitationTracker."""

import pytest
from src.citation_manager.citation_tracker import CitationTracker
from src.citation_manager.citation_models import Citation, ClauseReference


class TestCitationTracker:
    """Test cases for CitationTracker class."""

    def test_initialization(self):
        """Test tracker initialization."""
        tracker = CitationTracker()
        assert tracker.get_citation_count() == 0
        assert tracker.get_document_count() == 0

    def test_get_next_number(self):
        """Test getting next citation number."""
        tracker = CitationTracker()
        assert tracker.get_next_number() == 1
        assert tracker.get_next_number() == 2
        assert tracker.get_next_number() == 3

    def test_create_citation(self):
        """Test creating citations with auto-assigned numbers."""
        tracker = CitationTracker()

        citation1 = tracker.create_citation(document_id="doc1")
        assert citation1.citation_number == 1
        assert citation1.document_id == "doc1"

        citation2 = tracker.create_citation(document_id="doc2")
        assert citation2.citation_number == 2
        assert citation2.document_id == "doc2"

    def test_create_citation_with_clauses(self):
        """Test creating citations with clause references."""
        tracker = CitationTracker()

        clause_ref = ClauseReference(
            document_id="doc1",
            clause_number="5.2.1",
            clause_title="Safety requirements"
        )

        citation = tracker.create_citation(
            document_id="doc1",
            clause_references=[clause_ref],
            matched_text="According to clause 5.2.1",
            confidence=0.95
        )

        assert citation.citation_number == 1
        assert len(citation.clause_references) == 1
        assert citation.matched_text == "According to clause 5.2.1"
        assert citation.confidence == 0.95

    def test_register_citation(self):
        """Test registering existing citations."""
        tracker = CitationTracker()

        citation = Citation(
            citation_number=5,
            document_id="doc1",
            clause_references=[],
            confidence=1.0
        )

        number = tracker.register_citation(citation)
        assert number == 5
        assert tracker.get_citation_count() == 1

    def test_register_duplicate_citation_number_different_document(self):
        """Test that registering same number for different document raises error."""
        tracker = CitationTracker()

        citation1 = Citation(citation_number=1, document_id="doc1")
        citation2 = Citation(citation_number=1, document_id="doc2")

        tracker.register_citation(citation1)

        with pytest.raises(ValueError, match="already assigned"):
            tracker.register_citation(citation2)

    def test_get_citation_by_number(self):
        """Test retrieving citation by number."""
        tracker = CitationTracker()

        citation = tracker.create_citation(document_id="doc1")
        retrieved = tracker.get_citation_by_number(1)

        assert retrieved is not None
        assert retrieved.citation_number == 1
        assert retrieved.document_id == "doc1"

    def test_get_citations_for_document(self):
        """Test getting all citations for a document."""
        tracker = CitationTracker()

        tracker.create_citation(document_id="doc1")
        tracker.create_citation(document_id="doc2")
        tracker.create_citation(document_id="doc1")

        doc1_citations = tracker.get_citations_for_document("doc1")
        assert len(doc1_citations) == 2
        assert all(c.document_id == "doc1" for c in doc1_citations)

    def test_has_citation_for_document(self):
        """Test checking if document has been cited."""
        tracker = CitationTracker()

        tracker.create_citation(document_id="doc1")

        assert tracker.has_citation_for_document("doc1")
        assert not tracker.has_citation_for_document("doc2")

    def test_get_first_citation_number_for_document(self):
        """Test getting first citation number for a document."""
        tracker = CitationTracker()

        tracker.create_citation(document_id="doc1")  # Citation 1
        tracker.create_citation(document_id="doc2")  # Citation 2
        tracker.create_citation(document_id="doc1")  # Citation 3

        first_num = tracker.get_first_citation_number_for_document("doc1")
        assert first_num == 1

        first_num2 = tracker.get_first_citation_number_for_document("doc2")
        assert first_num2 == 2

    def test_get_all_citations(self):
        """Test getting all citations in order."""
        tracker = CitationTracker()

        tracker.create_citation(document_id="doc1")
        tracker.create_citation(document_id="doc2")
        tracker.create_citation(document_id="doc3")

        all_citations = tracker.get_all_citations()
        assert len(all_citations) == 3
        assert [c.citation_number for c in all_citations] == [1, 2, 3]

    def test_get_unique_document_ids(self):
        """Test getting unique document IDs."""
        tracker = CitationTracker()

        tracker.create_citation(document_id="doc1")
        tracker.create_citation(document_id="doc2")
        tracker.create_citation(document_id="doc1")
        tracker.create_citation(document_id="doc3")

        unique_ids = tracker.get_unique_document_ids()
        assert unique_ids == {"doc1", "doc2", "doc3"}

    def test_reset(self):
        """Test resetting the tracker."""
        tracker = CitationTracker()

        tracker.create_citation(document_id="doc1")
        tracker.create_citation(document_id="doc2")

        assert tracker.get_citation_count() == 2

        tracker.reset()

        assert tracker.get_citation_count() == 0
        assert tracker.get_document_count() == 0
        assert tracker.get_next_number() == 1

    def test_citation_count_and_document_count(self):
        """Test citation and document counts."""
        tracker = CitationTracker()

        tracker.create_citation(document_id="doc1")
        tracker.create_citation(document_id="doc1")
        tracker.create_citation(document_id="doc2")

        assert tracker.get_citation_count() == 3
        assert tracker.get_document_count() == 2

    def test_repr(self):
        """Test string representation."""
        tracker = CitationTracker()
        tracker.create_citation(document_id="doc1")

        repr_str = repr(tracker)
        assert "CitationTracker" in repr_str
        assert "citations=1" in repr_str
        assert "documents=1" in repr_str
