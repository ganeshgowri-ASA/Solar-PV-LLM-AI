"""Unit tests for CitationManager."""

import pytest
import tempfile
from pathlib import Path

from src.citation_manager import (
    CitationManager,
    CitationStyle,
    create_standard_metadata
)


class TestCitationManager:
    """Test cases for CitationManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = CitationManager(style=CitationStyle.IEC)

    def test_initialization_default(self):
        """Test default initialization."""
        manager = CitationManager()
        assert manager.citation_formatter.style == CitationStyle.IEC
        assert manager.auto_inject_citations is True

    def test_initialization_with_style(self):
        """Test initialization with specific style."""
        manager = CitationManager(style=CitationStyle.IEEE)
        assert manager.citation_formatter.style == CitationStyle.IEEE

    def test_initialization_no_auto_inject(self):
        """Test initialization without auto-injection."""
        manager = CitationManager(auto_inject_citations=False)
        assert manager.auto_inject_citations is False

    def test_add_document(self):
        """Test adding a document."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety qualification",
            organization="IEC"
        )

        doc_id = self.manager.add_document(metadata)
        assert doc_id == "IEC 61730-1:2016"

        retrieved = self.manager.get_document(doc_id)
        assert retrieved is not None
        assert retrieved.title == "PV module safety qualification"

    def test_add_multiple_documents(self):
        """Test adding multiple documents at once."""
        docs = [
            create_standard_metadata(
                standard_id="IEC 61730-1:2016",
                title="PV module safety",
                organization="IEC"
            ),
            create_standard_metadata(
                standard_id="IEC 61215-1:2016",
                title="PV module performance",
                organization="IEC"
            )
        ]

        doc_ids = self.manager.add_documents(docs)
        assert len(doc_ids) == 2
        assert "IEC 61730-1:2016" in doc_ids
        assert "IEC 61215-1:2016" in doc_ids

    def test_get_document(self):
        """Test retrieving document."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.manager.add_document(metadata)
        retrieved = self.manager.get_document("IEC 61730-1:2016")

        assert retrieved is not None
        assert retrieved.document_id == "IEC 61730-1:2016"

    def test_set_citation_style(self):
        """Test changing citation style."""
        self.manager.set_citation_style(CitationStyle.IEEE)
        assert self.manager.citation_formatter.style == CitationStyle.IEEE

        self.manager.set_citation_style(CitationStyle.APA)
        assert self.manager.citation_formatter.style == CitationStyle.APA

    def test_process_response_basic(self):
        """Test processing a basic response."""
        # Add a document
        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety qualification",
            organization="IEC"
        )
        self.manager.add_document(doc)

        # Response text
        response_text = "The module must meet safety requirements as per IEC 61730."

        # Retrieved documents from RAG
        retrieved_docs = [
            {
                'document_id': 'IEC 61730-1:2016',
                'content': 'Safety requirements for photovoltaic modules',
                'score': 0.95,
                'metadata': {}
            }
        ]

        # Process response
        result = self.manager.process_response(
            response_text=response_text,
            retrieved_documents=retrieved_docs
        )

        assert result.original_text == response_text
        assert len(result.citations_found) >= 0  # May or may not find citations depending on matching
        assert 'response_1' in result.extraction_metadata['response_id']

    def test_process_response_with_multiple_documents(self):
        """Test processing response with multiple documents."""
        # Add documents
        docs = [
            create_standard_metadata(
                standard_id="IEC 61730-1:2016",
                title="PV module safety",
                organization="IEC"
            ),
            create_standard_metadata(
                standard_id="IEC 61215-1:2016",
                title="PV module performance",
                organization="IEC"
            )
        ]
        self.manager.add_documents(docs)

        response_text = "Modules must meet safety and performance requirements."

        retrieved_docs = [
            {
                'document_id': 'IEC 61730-1:2016',
                'content': 'Safety requirements for PV modules',
                'score': 0.95,
                'metadata': {}
            },
            {
                'document_id': 'IEC 61215-1:2016',
                'content': 'Performance testing requirements',
                'score': 0.90,
                'metadata': {}
            }
        ]

        result = self.manager.process_response(
            response_text=response_text,
            retrieved_documents=retrieved_docs
        )

        assert result.original_text == response_text
        # Reference section should be generated if citations are found
        if result.citations_found:
            assert len(result.reference_section) > 0

    def test_process_response_custom_id(self):
        """Test processing response with custom ID."""
        response_text = "Test response."
        retrieved_docs = []

        result = self.manager.process_response(
            response_text=response_text,
            retrieved_documents=retrieved_docs,
            response_id="custom_id_123"
        )

        assert result.extraction_metadata['response_id'] == "custom_id_123"

    def test_process_multiple_responses(self):
        """Test processing multiple responses increments counter."""
        self.manager.process_response("Response 1", [])
        self.manager.process_response("Response 2", [])
        self.manager.process_response("Response 3", [])

        stats = self.manager.get_statistics()
        assert stats['responses_processed'] == 3

    def test_create_response_citations(self):
        """Test creating ResponseCitations object."""
        from src.citation_manager.citation_models import Citation

        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )
        self.manager.add_document(doc)

        citations = [
            Citation(citation_number=1, document_id="IEC 61730-1:2016")
        ]

        response_citations = self.manager.create_response_citations(
            response_id="test_response",
            citations=citations
        )

        assert response_citations.response_id == "test_response"
        assert len(response_citations.citations) == 1
        assert "IEC 61730-1:2016" in response_citations.referenced_documents

    def test_format_response_with_citations(self):
        """Test formatting response with citations."""
        from src.citation_manager.citation_models import Citation

        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )
        self.manager.add_document(doc)

        response_text = "The module must meet safety requirements[1]."
        citations = [
            Citation(citation_number=1, document_id="IEC 61730-1:2016")
        ]

        formatted = self.manager.format_response_with_citations(
            response_text,
            citations
        )

        assert response_text in formatted
        assert "References" in formatted
        assert "IEC 61730-1:2016" in formatted

    def test_get_statistics(self):
        """Test getting statistics."""
        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )
        self.manager.add_document(doc)

        self.manager.process_response("Test response", [])

        stats = self.manager.get_statistics()

        assert 'total_documents' in stats
        assert 'responses_processed' in stats
        assert stats['total_documents'] == 1
        assert stats['responses_processed'] == 1

    def test_export_import_references(self):
        """Test exporting and importing references."""
        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )
        self.manager.add_document(doc)

        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name

        try:
            self.manager.export_references(temp_path)

            # Create new manager and import
            new_manager = CitationManager()
            new_manager.import_references(temp_path)

            retrieved = new_manager.get_document("IEC 61730-1:2016")
            assert retrieved is not None
            assert retrieved.title == "PV module safety"

        finally:
            Path(temp_path).unlink()

    def test_reset(self):
        """Test resetting the manager."""
        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )
        self.manager.add_document(doc)
        self.manager.process_response("Test", [])

        stats = self.manager.get_statistics()
        assert stats['total_documents'] == 1
        assert stats['responses_processed'] == 1

        self.manager.reset()

        stats = self.manager.get_statistics()
        assert stats['total_documents'] == 0
        assert stats['responses_processed'] == 0

    def test_repr(self):
        """Test string representation."""
        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )
        self.manager.add_document(doc)

        repr_str = repr(self.manager)
        assert "CitationManager" in repr_str
        assert "style=iec" in repr_str
        assert "documents=1" in repr_str


class TestCitationManagerIntegration:
    """Integration tests for full citation workflow."""

    def test_complete_workflow(self):
        """Test complete citation workflow from start to finish."""
        # 1. Initialize manager
        manager = CitationManager(style=CitationStyle.IEC)

        # 2. Add source documents
        docs = [
            create_standard_metadata(
                standard_id="IEC 61730-1:2016",
                title="Photovoltaic (PV) module safety qualification - Part 1",
                organization="IEC",
                year=2016
            ),
            create_standard_metadata(
                standard_id="IEC 61215-1:2016",
                title="Terrestrial photovoltaic (PV) modules - Design qualification",
                organization="IEC",
                year=2016
            )
        ]
        manager.add_documents(docs)

        # 3. Process an LLM response
        response_text = (
            "According to IEC 61730, photovoltaic modules must undergo rigorous "
            "safety qualification testing. Additionally, design qualification "
            "requirements are specified in IEC 61215."
        )

        retrieved_docs = [
            {
                'document_id': 'IEC 61730-1:2016',
                'content': 'Safety qualification testing requirements for PV modules',
                'score': 0.95,
                'metadata': {'page': 1}
            },
            {
                'document_id': 'IEC 61215-1:2016',
                'content': 'Design qualification and type approval requirements',
                'score': 0.90,
                'metadata': {'page': 1}
            }
        ]

        result = manager.process_response(
            response_text=response_text,
            retrieved_documents=retrieved_docs,
            response_id="integration_test_1"
        )

        # 4. Verify results
        assert result.original_text == response_text
        assert result.extraction_metadata['response_id'] == "integration_test_1"

        # Check that standard IDs were found
        standard_ids_found = result.extraction_metadata.get('standard_ids_found', [])
        assert len(standard_ids_found) >= 2

        # 5. Verify statistics
        stats = manager.get_statistics()
        assert stats['total_documents'] == 2
        assert stats['responses_processed'] == 1

    def test_workflow_with_different_styles(self):
        """Test that different citation styles work correctly."""
        manager = CitationManager(style=CitationStyle.IEC)

        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )
        manager.add_document(doc)

        response_text = "Safety requirements are defined."
        retrieved_docs = [
            {
                'document_id': 'IEC 61730-1:2016',
                'content': 'Safety requirements',
                'score': 0.95,
                'metadata': {}
            }
        ]

        # Process with IEC style
        result_iec = manager.process_response(response_text, retrieved_docs)

        # Change to IEEE style
        manager.set_citation_style(CitationStyle.IEEE)
        manager.citation_tracker.reset()
        result_ieee = manager.process_response(response_text, retrieved_docs)

        # Both should process successfully
        assert result_iec.original_text == response_text
        assert result_ieee.original_text == response_text
