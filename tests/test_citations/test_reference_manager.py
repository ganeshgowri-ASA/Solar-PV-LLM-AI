"""
Unit tests for ReferenceManager.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from citations.reference_manager import ReferenceManager
from citations.citation_manager import Citation


class TestReferenceManager:
    """Test cases for ReferenceManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ReferenceManager()

    def test_add_citation(self):
        """Test adding a citation."""
        citation = Citation(
            citation_id=1,
            standard_id="IEC 61215",
            title="PV Module Testing"
        )

        self.manager.add_citation(citation)

        assert self.manager.get_citation_by_id(1) == citation

    def test_add_multiple_citations(self):
        """Test adding multiple citations."""
        citations = [
            Citation(citation_id=1, standard_id="IEC 61215"),
            Citation(citation_id=2, standard_id="IEC 61730"),
            Citation(citation_id=3, standard_id="ISO 9001")
        ]

        self.manager.add_citations(citations)

        assert self.manager.get_citation_by_id(1) is not None
        assert self.manager.get_citation_by_id(2) is not None
        assert self.manager.get_citation_by_id(3) is not None

    def test_get_citations_by_standard(self):
        """Test getting citations by standard ID."""
        citation1 = Citation(
            citation_id=1,
            standard_id="IEC 61215",
            clause_ref="Clause 5.2"
        )
        citation2 = Citation(
            citation_id=2,
            standard_id="IEC 61215",
            clause_ref="Clause 6.1"
        )
        citation3 = Citation(
            citation_id=3,
            standard_id="IEC 61730"
        )

        self.manager.add_citations([citation1, citation2, citation3])

        iec_citations = self.manager.get_citations_by_standard("IEC 61215")

        assert len(iec_citations) == 2
        assert citation1 in iec_citations
        assert citation2 in iec_citations

    def test_validate_citations_valid(self):
        """Test validation of valid citations."""
        citation = Citation(citation_id=1, standard_id="IEC 61215")
        self.manager.add_citation(citation)

        text = "According to the standard[1], testing is required."

        is_valid, errors = self.manager.validate_citations(text)

        assert is_valid
        assert len(errors) == 0

    def test_validate_citations_missing_reference(self):
        """Test validation detects missing citation definitions."""
        text = "According to the standard[1], testing is required."

        is_valid, errors = self.manager.validate_citations(text)

        assert not is_valid
        assert len(errors) > 0
        assert "not defined" in errors[0]

    def test_validate_citations_unused(self):
        """Test validation detects unused citations."""
        citation = Citation(citation_id=1, standard_id="IEC 61215")
        self.manager.add_citation(citation)

        text = "This text has no citations."

        is_valid, errors = self.manager.validate_citations(text)

        assert not is_valid
        assert len(errors) > 0
        assert "not referenced" in errors[0]

    def test_extract_citation_references(self):
        """Test extraction of citation references from text."""
        text = "Standards [1] and [2] require testing[3]."

        refs = self.manager._extract_citation_references(text)

        assert len(refs) == 3
        assert 1 in refs
        assert 2 in refs
        assert 3 in refs

    def test_validate_citation_sequence_valid(self):
        """Test validation of valid citation sequence."""
        citations = [
            Citation(citation_id=1, standard_id="IEC 61215"),
            Citation(citation_id=2, standard_id="IEC 61730"),
            Citation(citation_id=3, standard_id="ISO 9001")
        ]

        self.manager.add_citations(citations)

        is_valid, errors = self.manager.validate_citation_sequence()

        assert is_valid
        assert len(errors) == 0

    def test_validate_citation_sequence_gap(self):
        """Test validation detects gaps in citation sequence."""
        citations = [
            Citation(citation_id=1, standard_id="IEC 61215"),
            Citation(citation_id=3, standard_id="ISO 9001")  # Gap at 2
        ]

        self.manager.add_citations(citations)

        is_valid, errors = self.manager.validate_citation_sequence()

        assert not is_valid
        assert len(errors) > 0
        assert "Gap" in errors[0]

    def test_validate_citation_sequence_wrong_start(self):
        """Test validation detects incorrect starting number."""
        citations = [
            Citation(citation_id=2, standard_id="IEC 61215"),
            Citation(citation_id=3, standard_id="IEC 61730")
        ]

        self.manager.add_citations(citations)

        is_valid, errors = self.manager.validate_citation_sequence()

        assert not is_valid
        assert len(errors) > 0
        assert "start from 1" in errors[0]

    def test_get_citation_statistics(self):
        """Test getting citation statistics."""
        citations = [
            Citation(
                citation_id=1,
                standard_id="IEC 61215",
                clause_ref="Clause 5.2",
                url="https://example.com"
            ),
            Citation(
                citation_id=2,
                standard_id="IEC 61730",
                clause_ref="Clause 3.1"
            ),
            Citation(
                citation_id=3,
                title="Some document"
            )
        ]

        self.manager.add_citations(citations)

        stats = self.manager.get_citation_statistics()

        assert stats['total_citations'] == 3
        assert stats['citations_with_standard_id'] == 2
        assert stats['citations_with_clause_ref'] == 2
        assert stats['citations_with_url'] == 1
        assert stats['unique_standards'] == 2

    def test_merge_duplicate_citations(self):
        """Test merging duplicate citations."""
        citations = [
            Citation(
                citation_id=1,
                standard_id="IEC 61215",
                clause_ref="Clause 5.2",
                title="First Title"
            ),
            Citation(
                citation_id=2,
                standard_id="IEC 61215",
                clause_ref="Clause 5.2",
                year="2021"  # Different metadata
            ),
            Citation(
                citation_id=3,
                standard_id="IEC 61730"
            )
        ]

        merged = self.manager.merge_duplicate_citations(citations)

        # Should have 2 unique citations (IEC 61215 merged)
        assert len(merged) == 2

        # First citation should have merged metadata
        iec_citation = next(c for c in merged if c.standard_id == "IEC 61215")
        assert iec_citation.year == "2021"

    def test_renumber_citations(self):
        """Test renumbering citations."""
        citations = [
            Citation(citation_id=5, standard_id="IEC 61215"),
            Citation(citation_id=10, standard_id="IEC 61730"),
            Citation(citation_id=15, standard_id="ISO 9001")
        ]

        self.manager.add_citations(citations)
        renumbered = self.manager.renumber_citations(citations)

        assert renumbered[0].citation_id == 1
        assert renumbered[1].citation_id == 2
        assert renumbered[2].citation_id == 3

    def test_clear(self):
        """Test clearing all citations."""
        citation = Citation(citation_id=1, standard_id="IEC 61215")
        self.manager.add_citation(citation)

        assert self.manager.get_citation_by_id(1) is not None

        self.manager.clear()

        assert self.manager.get_citation_by_id(1) is None

    def test_get_citation_by_id_not_found(self):
        """Test getting non-existent citation."""
        result = self.manager.get_citation_by_id(999)
        assert result is None

    def test_get_citations_by_standard_not_found(self):
        """Test getting citations for non-existent standard."""
        result = self.manager.get_citations_by_standard("NONEXISTENT")
        assert len(result) == 0
