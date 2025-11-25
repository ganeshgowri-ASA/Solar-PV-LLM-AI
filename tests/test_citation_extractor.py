"""Unit tests for CitationExtractor."""

import pytest
from src.citation_manager.citation_extractor import CitationExtractor
from src.citation_manager.citation_tracker import CitationTracker
from src.citation_manager.reference_tracker import ReferenceTracker, create_standard_metadata


class TestCitationExtractor:
    """Test cases for CitationExtractor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = CitationTracker()
        self.ref_tracker = ReferenceTracker()
        self.extractor = CitationExtractor(
            citation_tracker=self.tracker,
            reference_tracker=self.ref_tracker
        )

    def test_extract_standard_ids_iec(self):
        """Test extracting IEC standard IDs."""
        text = "According to IEC 61730-1:2016 and IEC 61215, the module must..."
        standards = self.extractor.extract_standard_ids(text)

        assert len(standards) == 2
        assert ("IEC", "IEC 61730-1:2016") in standards
        assert ("IEC", "IEC 61215") in standards

    def test_extract_standard_ids_ieee(self):
        """Test extracting IEEE standard IDs."""
        text = "IEEE 1547-2018 defines the requirements for..."
        standards = self.extractor.extract_standard_ids(text)

        assert len(standards) == 1
        assert ("IEEE", "IEEE 1547-2018") in standards

    def test_extract_standard_ids_iso(self):
        """Test extracting ISO standard IDs."""
        text = "As per ISO 9001:2015 and ISO 14001..."
        standards = self.extractor.extract_standard_ids(text)

        assert len(standards) == 2
        assert ("ISO", "ISO 9001:2015") in standards
        assert ("ISO", "ISO 14001") in standards

    def test_extract_standard_ids_mixed(self):
        """Test extracting mixed standard IDs."""
        text = "Compliance with IEC 61730, IEEE 1547, and ISO 9001 is required."
        standards = self.extractor.extract_standard_ids(text)

        assert len(standards) == 3
        assert any(s[0] == "IEC" for s in standards)
        assert any(s[0] == "IEEE" for s in standards)
        assert any(s[0] == "ISO" for s in standards)

    def test_extract_clause_references(self):
        """Test extracting clause references."""
        text = "According to Clause 5.2.1 and Section 10.3, as shown in Table 4..."
        clauses = self.extractor.extract_clause_references(text)

        assert len(clauses) >= 3
        assert any("5.2.1" in c for c in clauses)
        assert any("10.3" in c for c in clauses)
        assert any("Table" in c for c in clauses)

    def test_extract_clause_references_annex(self):
        """Test extracting annex references."""
        text = "See Annex A and Appendix B for details."
        clauses = self.extractor.extract_clause_references(text)

        assert len(clauses) >= 2
        assert any("Annex A" in c for c in clauses)
        assert any("Appendix B" in c for c in clauses)

    def test_create_clause_reference(self):
        """Test creating clause reference objects."""
        clause_ref = self.extractor.create_clause_reference(
            document_id="IEC 61730-1:2016",
            clause_number="5.2.1",
            clause_title="Module construction",
            page_number=15,
            excerpt="The module must be constructed..."
        )

        assert clause_ref.document_id == "IEC 61730-1:2016"
        assert clause_ref.clause_number == "5.2.1"
        assert clause_ref.clause_title == "Module construction"
        assert clause_ref.page_number == 15
        assert clause_ref.excerpt == "The module must be constructed..."

    def test_match_text_to_documents(self):
        """Test matching text to documents."""
        text = "The photovoltaic module must meet safety requirements."

        retrieved_docs = [
            {
                'document_id': 'IEC 61730-1:2016',
                'content': 'Photovoltaic module safety qualification requirements',
                'score': 0.95,
                'metadata': {}
            },
            {
                'document_id': 'IEC 61215-1:2016',
                'content': 'Design qualification and type approval for modules',
                'score': 0.80,
                'metadata': {}
            }
        ]

        matches = self.extractor.match_text_to_documents(
            text,
            retrieved_docs,
            similarity_threshold=0.7
        )

        assert len(matches) >= 1
        assert all(len(match) == 3 for match in matches)  # (doc_id, confidence, excerpt)
        assert all(match[1] >= 0.7 for match in matches)  # Check confidence threshold

    def test_inject_citations(self):
        """Test injecting citations into text."""
        from src.citation_manager.citation_models import Citation

        text = "The module must meet safety requirements according to IEC 61730."

        citation = Citation(
            citation_number=1,
            document_id="IEC 61730-1:2016",
            matched_text="safety requirements",
            confidence=0.95
        )

        result = self.extractor.inject_citations(text, [citation])

        assert "[1]" in result
        assert "safety requirements[1]" in result

    def test_inject_multiple_citations(self):
        """Test injecting multiple citations."""
        from src.citation_manager.citation_models import Citation

        text = "Module safety is critical. Performance testing is required."

        citations = [
            Citation(
                citation_number=1,
                document_id="doc1",
                matched_text="safety",
                confidence=0.95
            ),
            Citation(
                citation_number=2,
                document_id="doc2",
                matched_text="Performance testing",
                confidence=0.90
            )
        ]

        result = self.extractor.inject_citations(text, citations)

        assert "[1]" in result
        assert "[2]" in result

    def test_extract_citations_from_response(self):
        """Test complete citation extraction from response."""
        # Add a document to reference tracker
        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV Module Safety Qualification",
            organization="IEC"
        )
        self.ref_tracker.add_document(doc)

        response_text = "The module must meet IEC 61730 safety requirements."

        retrieved_docs = [
            {
                'document_id': 'IEC 61730-1:2016',
                'content': 'Safety requirements for photovoltaic modules',
                'score': 0.95,
                'metadata': {}
            }
        ]

        result = self.extractor.extract_citations_from_response(
            response_text,
            retrieved_docs,
            auto_inject=True
        )

        assert 'original_text' in result
        assert 'text_with_citations' in result
        assert 'citations' in result
        assert 'document_matches' in result
        assert result['original_text'] == response_text

    def test_extract_citations_from_context(self):
        """Test extracting clause references from context chunks."""
        context_chunks = [
            {
                'document_id': 'IEC 61730-1:2016',
                'content': 'Clause 5.2.1 defines module construction requirements...',
                'metadata': {'page_number': 15}
            },
            {
                'document_id': 'IEC 61730-1:2016',
                'content': 'Section 10.3 covers electrical safety...',
                'metadata': {'page_number': 30}
            }
        ]

        clause_refs = self.extractor.extract_citations_from_context(context_chunks)

        assert len(clause_refs) >= 2
        assert all(ref.document_id == 'IEC 61730-1:2016' for ref in clause_refs)

    def test_no_citations_for_empty_text(self):
        """Test that empty text produces no citations."""
        result = self.extractor.extract_citations_from_response(
            response_text="",
            retrieved_documents=[],
            auto_inject=False
        )

        assert len(result['citations']) == 0
        assert result['text_with_citations'] == ""

    def test_citation_confidence_threshold(self):
        """Test that low confidence matches are filtered out."""
        text = "Some generic text about modules."

        retrieved_docs = [
            {
                'document_id': 'doc1',
                'content': 'Completely unrelated content',
                'score': 0.3,
                'metadata': {}
            }
        ]

        matches = self.extractor.match_text_to_documents(
            text,
            retrieved_docs,
            similarity_threshold=0.7
        )

        # Should have no matches due to low confidence
        assert len(matches) == 0
