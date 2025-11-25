"""Unit tests for CitationFormatter."""

import pytest
from src.citation_manager.citation_formatter import (
    CitationFormatter,
    IECFormatter,
    IEEEFormatter,
    ISOFormatter,
    APAFormatter
)
from src.citation_manager.citation_models import (
    Citation,
    CitationStyle,
    ClauseReference
)
from src.citation_manager.reference_tracker import create_standard_metadata


class TestIECFormatter:
    """Test cases for IEC formatter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = IECFormatter()

    def test_format_inline(self):
        """Test formatting inline citation."""
        result = self.formatter.format_inline(1)
        assert result == "[1]"

        result = self.formatter.format_inline(42)
        assert result == "[42]"

    def test_format_reference_standard(self):
        """Test formatting reference for a standard."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="Photovoltaic (PV) module safety qualification - Part 1: Requirements for construction",
            organization="IEC",
            year=2016
        )

        result = self.formatter.format_reference(1, metadata)

        assert "[1]" in result
        assert "IEC 61730-1:2016" in result
        assert "Photovoltaic (PV) module safety qualification" in result

    def test_format_reference_with_clause(self):
        """Test formatting reference with clause number."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety qualification",
            organization="IEC"
        )

        clause_ref = ClauseReference(
            document_id="IEC 61730-1:2016",
            clause_number="5.2.1"
        )

        result = self.formatter.format_reference(1, metadata, [clause_ref])

        assert "[1]" in result
        assert "IEC 61730-1:2016" in result
        assert "Clause 5.2.1" in result

    def test_format_reference_multiple_clauses(self):
        """Test formatting reference with multiple clause numbers."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        clause_refs = [
            ClauseReference(document_id="IEC 61730-1:2016", clause_number="5.2.1"),
            ClauseReference(document_id="IEC 61730-1:2016", clause_number="10.3")
        ]

        result = self.formatter.format_reference(1, metadata, clause_refs)

        assert "Clause 5.2.1, 10.3" in result


class TestIEEEFormatter:
    """Test cases for IEEE formatter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = IEEEFormatter()

    def test_format_inline(self):
        """Test formatting inline citation."""
        result = self.formatter.format_inline(1)
        assert result == "[1]"

    def test_format_reference_standard(self):
        """Test formatting reference in IEEE style."""
        metadata = create_standard_metadata(
            standard_id="IEEE 1547-2018",
            title="Standard for Interconnection and Interoperability",
            organization="IEEE",
            year=2018
        )

        result = self.formatter.format_reference(1, metadata)

        assert "[1]" in result
        assert "IEEE 1547-2018" in result
        assert '"' in result  # IEEE uses quotes around titles


class TestISOFormatter:
    """Test cases for ISO formatter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = ISOFormatter()

    def test_format_inline(self):
        """Test formatting inline citation."""
        result = self.formatter.format_inline(1)
        assert result == "[1]"


class TestAPAFormatter:
    """Test cases for APA formatter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = APAFormatter()

    def test_format_inline(self):
        """Test formatting inline citation in APA style."""
        result = self.formatter.format_inline(1)
        assert result == "(1)"  # APA uses parentheses


class TestCitationFormatter:
    """Test cases for main CitationFormatter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = CitationFormatter(style=CitationStyle.IEC)

    def test_initialization_default(self):
        """Test default initialization."""
        formatter = CitationFormatter()
        assert formatter.style == CitationStyle.IEC

    def test_initialization_with_style(self):
        """Test initialization with specific style."""
        formatter = CitationFormatter(style=CitationStyle.IEEE)
        assert formatter.style == CitationStyle.IEEE

    def test_set_style(self):
        """Test changing citation style."""
        self.formatter.set_style(CitationStyle.IEEE)
        assert self.formatter.style == CitationStyle.IEEE

        self.formatter.set_style(CitationStyle.APA)
        assert self.formatter.style == CitationStyle.APA

    def test_format_inline_citation(self):
        """Test formatting inline citation."""
        citation = Citation(
            citation_number=1,
            document_id="doc1"
        )

        result = self.formatter.format_inline_citation(citation)
        assert result == "[1]"

        # Change to APA style
        self.formatter.set_style(CitationStyle.APA)
        result = self.formatter.format_inline_citation(citation)
        assert result == "(1)"

    def test_format_reference_entry(self):
        """Test formatting reference entry."""
        citation = Citation(
            citation_number=1,
            document_id="IEC 61730-1:2016"
        )

        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety qualification",
            organization="IEC"
        )

        result = self.formatter.format_reference_entry(citation, metadata)

        assert "[1]" in result
        assert "IEC 61730-1:2016" in result
        assert "PV module safety qualification" in result

    def test_format_reference_list(self):
        """Test formatting complete reference list."""
        citations = [
            Citation(citation_number=1, document_id="doc1"),
            Citation(citation_number=2, document_id="doc2"),
            Citation(citation_number=3, document_id="doc1"),  # Duplicate doc
        ]

        documents = {
            "doc1": create_standard_metadata(
                standard_id="IEC 61730-1:2016",
                title="PV module safety",
                organization="IEC"
            ),
            "doc2": create_standard_metadata(
                standard_id="IEC 61215-1:2016",
                title="PV module design qualification",
                organization="IEC"
            )
        }

        result = self.formatter.format_reference_list(
            citations,
            documents,
            include_header=True
        )

        assert "References" in result
        assert "[1]" in result
        assert "[2]" in result
        assert "IEC 61730-1:2016" in result
        assert "IEC 61215-1:2016" in result

    def test_format_reference_list_without_header(self):
        """Test formatting reference list without header."""
        citations = [
            Citation(citation_number=1, document_id="doc1")
        ]

        documents = {
            "doc1": create_standard_metadata(
                standard_id="IEC 61730-1:2016",
                title="PV module safety",
                organization="IEC"
            )
        }

        result = self.formatter.format_reference_list(
            citations,
            documents,
            include_header=False
        )

        assert "References" not in result
        assert "[1]" in result

    def test_create_formatted_citation(self):
        """Test creating FormattedCitation object."""
        citation = Citation(
            citation_number=1,
            document_id="doc1"
        )

        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        formatted = self.formatter.create_formatted_citation(citation, metadata)

        assert formatted.citation_number == 1
        assert formatted.inline_format == "[1]"
        assert "IEC 61730-1:2016" in formatted.reference_format
        assert formatted.style == CitationStyle.IEC

    def test_format_complete_response(self):
        """Test formatting complete response with citations."""
        response_text = "The module must meet safety requirements[1] and performance standards[2]."

        citations = [
            Citation(citation_number=1, document_id="doc1"),
            Citation(citation_number=2, document_id="doc2")
        ]

        documents = {
            "doc1": create_standard_metadata(
                standard_id="IEC 61730-1:2016",
                title="PV module safety",
                organization="IEC"
            ),
            "doc2": create_standard_metadata(
                standard_id="IEC 61215-1:2016",
                title="PV module performance",
                organization="IEC"
            )
        }

        result = self.formatter.format_complete_response(
            response_text,
            citations,
            documents,
            insert_inline=False
        )

        assert response_text in result
        assert "References" in result
        assert "[1]" in result
        assert "[2]" in result
        assert "IEC 61730-1:2016" in result
        assert "IEC 61215-1:2016" in result

    def test_format_empty_citations(self):
        """Test formatting with no citations."""
        response_text = "This is a response with no citations."

        result = self.formatter.format_complete_response(
            response_text,
            [],
            {},
            insert_inline=False
        )

        # Should just return the original text
        assert response_text in result
