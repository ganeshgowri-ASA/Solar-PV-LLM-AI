"""
Unit tests for CitationExtractor.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from citations.citation_extractor import CitationExtractor


class TestCitationExtractor:
    """Test cases for CitationExtractor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = CitationExtractor()

    def test_extract_iec_standard_id(self):
        """Test extraction of IEC standard IDs."""
        text = "According to IEC 61215-1, the module should be tested..."
        standard_id = self.extractor.extract_standard_id(text)
        assert standard_id is not None
        assert "IEC" in standard_id
        assert "61215" in standard_id

    def test_extract_iso_standard_id(self):
        """Test extraction of ISO standard IDs."""
        text = "The ISO 9001 standard specifies quality management..."
        standard_id = self.extractor.extract_standard_id(text)
        assert standard_id is not None
        assert "ISO" in standard_id
        assert "9001" in standard_id

    def test_extract_ieee_standard_id(self):
        """Test extraction of IEEE standard IDs."""
        text = "IEEE 1547 defines interconnection requirements..."
        standard_id = self.extractor.extract_standard_id(text)
        assert standard_id is not None
        assert "IEEE" in standard_id
        assert "1547" in standard_id

    def test_extract_multiple_standard_ids(self):
        """Test extraction of multiple standard IDs."""
        text = "This test follows IEC 61215 and IEC 61730 standards..."
        standard_ids = self.extractor.extract_all_standard_ids(text)
        assert len(standard_ids) >= 2
        assert any("61215" in sid for sid in standard_ids)
        assert any("61730" in sid for sid in standard_ids)

    def test_extract_clause_reference(self):
        """Test extraction of clause references."""
        text = "As specified in Clause 5.2.1, the test procedure..."
        clause_ref = self.extractor.extract_clause_reference(text)
        assert clause_ref is not None
        assert "5.2.1" in clause_ref

    def test_extract_section_reference(self):
        """Test extraction of section references."""
        text = "Section 4.3 describes the methodology..."
        section_ref = self.extractor.extract_clause_reference(text)
        assert section_ref is not None
        assert "4.3" in section_ref

    def test_extract_year(self):
        """Test extraction of publication year."""
        text = "IEC 61215:2021 is the latest version..."
        year = self.extractor.extract_year(text)
        assert year == "2021"

    def test_extract_page_reference(self):
        """Test extraction of page references."""
        text = "See page 42 for more details..."
        page = self.extractor.extract_page_reference(text)
        assert page == "42"

    def test_extract_metadata_with_explicit_values(self):
        """Test metadata extraction with explicit metadata dict."""
        metadata = {
            'standard_id': 'IEC 61215-1',
            'title': 'PV Module Testing',
            'year': '2021',
            'clause': 'Clause 5.2',
        }
        content = "Some content here..."

        result = self.extractor.extract_metadata(metadata, content)

        assert result['standard_id'] == 'IEC 61215-1'
        assert result['title'] == 'PV Module Testing'
        assert result['year'] == '2021'
        assert result['clause_ref'] == 'Clause 5.2'

    def test_extract_metadata_from_content(self):
        """Test metadata extraction from content when metadata is empty."""
        metadata = {}
        content = """
        IEC 61730-1:2016 - Photovoltaic module safety qualification
        Clause 10.5.2 describes the mechanical load test procedures.
        """

        result = self.extractor.extract_metadata(metadata, content)

        assert result['standard_id'] is not None
        assert "61730" in result['standard_id']
        assert result['year'] == "2016"
        assert result['clause_ref'] is not None

    def test_extract_citation_context(self):
        """Test extraction of context around a standard ID."""
        text = "The testing procedures defined in IEC 61215 ensure module quality and safety."
        context = self.extractor.extract_citation_context(text, "IEC 61215", window=20)

        assert context is not None
        assert "IEC 61215" in context
        assert "testing" in context or "procedures" in context

    def test_no_standard_id_found(self):
        """Test when no standard ID is present."""
        text = "This is just regular text without any standards."
        standard_id = self.extractor.extract_standard_id(text)
        assert standard_id is None

    def test_extract_all_clause_references(self):
        """Test extraction of all clause references."""
        text = "Clause 5.2 and Section 6.1 as well as Annex A provide guidance."
        clause_refs = self.extractor.extract_all_clause_references(text)

        assert len(clause_refs) >= 2
        assert any("5.2" in ref for ref in clause_refs)

    def test_astm_standard_extraction(self):
        """Test extraction of ASTM standard IDs."""
        text = "According to ASTM E1036, the test should be conducted..."
        standard_id = self.extractor.extract_standard_id(text)
        assert standard_id is not None
        assert "ASTM" in standard_id
        assert "E1036" in standard_id

    def test_ul_standard_extraction(self):
        """Test extraction of UL standard IDs."""
        text = "The inverter complies with UL 1741 requirements..."
        standard_id = self.extractor.extract_standard_id(text)
        assert standard_id is not None
        assert "UL" in standard_id
        assert "1741" in standard_id
