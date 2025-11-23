"""
Unit tests for citation formatters.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from citations.citation_formatter import (
    IECCitationFormatter,
    IEEECitationFormatter,
    APACitationFormatter,
    get_formatter
)
from citations.citation_manager import Citation


class TestIECCitationFormatter:
    """Test cases for IEC citation formatter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = IECCitationFormatter()

    def test_format_citation_full(self):
        """Test formatting a citation with all fields."""
        citation = Citation(
            citation_id=1,
            standard_id="IEC 61215-1",
            title="Terrestrial photovoltaic (PV) modules - Design qualification",
            year="2021",
            clause_ref="Clause 5.2",
            url="https://webstore.iec.ch/publication/1"
        )

        formatted = self.formatter.format_citation(citation)

        assert "[1]" in formatted
        assert "IEC 61215-1" in formatted
        assert "2021" in formatted
        assert "Clause 5.2" in formatted
        assert formatted.endswith('.')

    def test_format_citation_minimal(self):
        """Test formatting a citation with minimal fields."""
        citation = Citation(
            citation_id=2,
            standard_id="IEC 61730"
        )

        formatted = self.formatter.format_citation(citation)

        assert "[2]" in formatted
        assert "IEC 61730" in formatted
        assert formatted.endswith('.')

    def test_format_reference_list(self):
        """Test formatting a complete reference list."""
        citations = [
            Citation(
                citation_id=1,
                standard_id="IEC 61215",
                title="PV Module Testing",
                year="2021"
            ),
            Citation(
                citation_id=2,
                standard_id="IEC 61730",
                title="PV Module Safety",
                year="2020"
            )
        ]

        formatted = self.formatter.format_reference_list(citations)

        assert "References" in formatted
        assert "[1]" in formatted
        assert "[2]" in formatted
        assert "IEC 61215" in formatted
        assert "IEC 61730" in formatted

    def test_format_empty_list(self):
        """Test formatting an empty reference list."""
        formatted = self.formatter.format_reference_list([])
        assert formatted == ""

    def test_title_quoting(self):
        """Test that titles are properly quoted."""
        citation = Citation(
            citation_id=1,
            standard_id="IEC 61215",
            title="PV Module Testing"
        )

        formatted = self.formatter.format_citation(citation)

        assert '"PV Module Testing"' in formatted


class TestIEEECitationFormatter:
    """Test cases for IEEE citation formatter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = IEEECitationFormatter()

    def test_format_citation_full(self):
        """Test formatting a citation with all fields."""
        citation = Citation(
            citation_id=1,
            standard_id="IEEE 1547",
            title="Interconnection and Interoperability",
            year="2018",
            url="https://standards.ieee.org/1547"
        )

        formatted = self.formatter.format_citation(citation)

        assert "[1]" in formatted
        assert "IEEE 1547" in formatted
        assert "2018" in formatted
        assert formatted.endswith('.')

    def test_format_reference_list(self):
        """Test formatting IEEE reference list."""
        citations = [
            Citation(
                citation_id=1,
                standard_id="IEEE 1547",
                title="Interconnection Standard"
            )
        ]

        formatted = self.formatter.format_reference_list(citations)

        assert "REFERENCES" in formatted
        assert "[1]" in formatted


class TestAPACitationFormatter:
    """Test cases for APA citation formatter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = APACitationFormatter()

    def test_format_citation_full(self):
        """Test formatting a citation with all fields."""
        citation = Citation(
            citation_id=1,
            standard_id="IEC 61215",
            title="PV Module Testing",
            year="2021"
        )

        formatted = self.formatter.format_citation(citation)

        assert "[1]" in formatted
        assert "2021" in formatted or "(2021)" in formatted

    def test_get_organization_name(self):
        """Test extracting organization names."""
        org_iec = self.formatter._get_organization_name("IEC 61215")
        assert org_iec == "International Electrotechnical Commission"

        org_ieee = self.formatter._get_organization_name("IEEE 1547")
        assert org_ieee == "Institute of Electrical and Electronics Engineers"

        org_iso = self.formatter._get_organization_name("ISO 9001")
        assert org_iso == "International Organization for Standardization"


class TestGetFormatter:
    """Test cases for get_formatter function."""

    def test_get_iec_formatter(self):
        """Test getting IEC formatter."""
        formatter = get_formatter('iec')
        assert isinstance(formatter, IECCitationFormatter)

    def test_get_ieee_formatter(self):
        """Test getting IEEE formatter."""
        formatter = get_formatter('ieee')
        assert isinstance(formatter, IEEECitationFormatter)

    def test_get_apa_formatter(self):
        """Test getting APA formatter."""
        formatter = get_formatter('apa')
        assert isinstance(formatter, APACitationFormatter)

    def test_case_insensitive(self):
        """Test that formatter names are case-insensitive."""
        formatter = get_formatter('IEC')
        assert isinstance(formatter, IECCitationFormatter)

    def test_invalid_style(self):
        """Test that invalid styles raise ValueError."""
        with pytest.raises(ValueError):
            get_formatter('invalid')
