"""Unit tests for ReferenceTracker."""

import pytest
import tempfile
import json
from pathlib import Path

from src.citation_manager.reference_tracker import ReferenceTracker, create_standard_metadata
from src.citation_manager.citation_models import DocumentType


class TestReferenceTracker:
    """Test cases for ReferenceTracker class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = ReferenceTracker()

    def test_initialization(self):
        """Test tracker initialization."""
        assert self.tracker.get_document_count() == 0

    def test_add_document(self):
        """Test adding a document."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety qualification",
            organization="IEC"
        )

        doc_id = self.tracker.add_document(metadata)
        assert doc_id == "IEC 61730-1:2016"
        assert self.tracker.get_document_count() == 1

    def test_add_duplicate_document(self):
        """Test that adding same document updates it."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.tracker.add_document(metadata)
        self.tracker.add_document(metadata)

        assert self.tracker.get_document_count() == 1

    def test_get_document(self):
        """Test retrieving document by ID."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.tracker.add_document(metadata)
        retrieved = self.tracker.get_document("IEC 61730-1:2016")

        assert retrieved is not None
        assert retrieved.document_id == "IEC 61730-1:2016"
        assert retrieved.title == "PV module safety"

    def test_get_nonexistent_document(self):
        """Test retrieving document that doesn't exist."""
        result = self.tracker.get_document("nonexistent")
        assert result is None

    def test_has_document(self):
        """Test checking if document exists."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.tracker.add_document(metadata)

        assert self.tracker.has_document("IEC 61730-1:2016")
        assert not self.tracker.has_document("nonexistent")

    def test_increment_usage(self):
        """Test incrementing document usage count."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.tracker.add_document(metadata)

        count = self.tracker.increment_usage("IEC 61730-1:2016")
        assert count == 1

        count = self.tracker.increment_usage("IEC 61730-1:2016")
        assert count == 2

    def test_increment_usage_nonexistent_document(self):
        """Test that incrementing usage for nonexistent document raises error."""
        with pytest.raises(ValueError, match="not tracked"):
            self.tracker.increment_usage("nonexistent")

    def test_get_usage_count(self):
        """Test getting usage count."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.tracker.add_document(metadata)
        self.tracker.increment_usage("IEC 61730-1:2016")
        self.tracker.increment_usage("IEC 61730-1:2016")

        count = self.tracker.get_usage_count("IEC 61730-1:2016")
        assert count == 2

        # Nonexistent document should return 0
        count = self.tracker.get_usage_count("nonexistent")
        assert count == 0

    def test_get_all_documents(self):
        """Test getting all documents."""
        doc1 = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )
        doc2 = create_standard_metadata(
            standard_id="IEC 61215-1:2016",
            title="PV module performance",
            organization="IEC"
        )

        self.tracker.add_document(doc1)
        self.tracker.add_document(doc2)

        all_docs = self.tracker.get_all_documents()
        assert len(all_docs) == 2

    def test_get_documents_by_type(self):
        """Test filtering documents by type."""
        doc1 = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.tracker.add_document(doc1)

        standards = self.tracker.get_documents_by_type(DocumentType.STANDARD)
        assert len(standards) == 1
        assert standards[0].document_type == DocumentType.STANDARD

    def test_get_standards(self):
        """Test getting all standard documents."""
        doc1 = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.tracker.add_document(doc1)

        standards = self.tracker.get_standards()
        assert len(standards) == 1

    def test_search_by_title(self):
        """Test searching documents by title."""
        doc1 = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV Module Safety Qualification",
            organization="IEC"
        )
        doc2 = create_standard_metadata(
            standard_id="IEC 61215-1:2016",
            title="PV Module Performance Testing",
            organization="IEC"
        )

        self.tracker.add_document(doc1)
        self.tracker.add_document(doc2)

        # Case-insensitive search
        results = self.tracker.search_by_title("safety")
        assert len(results) == 1
        assert "Safety" in results[0].title

        # Search for "Module" should find both
        results = self.tracker.search_by_title("module")
        assert len(results) == 2

    def test_search_by_title_case_sensitive(self):
        """Test case-sensitive title search."""
        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV Module Safety",
            organization="IEC"
        )

        self.tracker.add_document(doc)

        results = self.tracker.search_by_title("Module", case_sensitive=True)
        assert len(results) == 1

        results = self.tracker.search_by_title("module", case_sensitive=True)
        assert len(results) == 0

    def test_search_by_standard_id(self):
        """Test searching by standard ID."""
        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.tracker.add_document(doc)

        result = self.tracker.search_by_standard_id("IEC 61730-1:2016")
        assert result is not None
        assert result.standard_metadata.standard_id == "IEC 61730-1:2016"

        result = self.tracker.search_by_standard_id("nonexistent")
        assert result is None

    def test_get_most_cited_documents(self):
        """Test getting most cited documents."""
        doc1 = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )
        doc2 = create_standard_metadata(
            standard_id="IEC 61215-1:2016",
            title="PV module performance",
            organization="IEC"
        )

        self.tracker.add_document(doc1)
        self.tracker.add_document(doc2)

        # Cite doc1 three times, doc2 once
        self.tracker.increment_usage("IEC 61730-1:2016")
        self.tracker.increment_usage("IEC 61730-1:2016")
        self.tracker.increment_usage("IEC 61730-1:2016")
        self.tracker.increment_usage("IEC 61215-1:2016")

        most_cited = self.tracker.get_most_cited_documents(limit=2)
        assert len(most_cited) == 2
        assert most_cited[0][1] == 3  # First should have 3 citations
        assert most_cited[1][1] == 1  # Second should have 1 citation

    def test_clear(self):
        """Test clearing all documents."""
        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.tracker.add_document(doc)
        self.tracker.increment_usage("IEC 61730-1:2016")

        assert self.tracker.get_document_count() == 1

        self.tracker.clear()

        assert self.tracker.get_document_count() == 0
        assert self.tracker.get_usage_count("IEC 61730-1:2016") == 0

    def test_export_import_json(self):
        """Test exporting and importing documents to/from JSON."""
        doc1 = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )
        doc2 = create_standard_metadata(
            standard_id="IEC 61215-1:2016",
            title="PV module performance",
            organization="IEC"
        )

        self.tracker.add_document(doc1)
        self.tracker.add_document(doc2)
        self.tracker.increment_usage("IEC 61730-1:2016")

        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name

        try:
            self.tracker.export_to_json(temp_path)

            # Create new tracker and import
            new_tracker = ReferenceTracker()
            new_tracker.import_from_json(temp_path)

            assert new_tracker.get_document_count() == 2
            assert new_tracker.has_document("IEC 61730-1:2016")
            assert new_tracker.has_document("IEC 61215-1:2016")
            assert new_tracker.get_usage_count("IEC 61730-1:2016") == 1

        finally:
            Path(temp_path).unlink()

    def test_get_statistics(self):
        """Test getting statistics."""
        doc1 = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.tracker.add_document(doc1)
        self.tracker.increment_usage("IEC 61730-1:2016")
        self.tracker.increment_usage("IEC 61730-1:2016")

        stats = self.tracker.get_statistics()

        assert stats['total_documents'] == 1
        assert stats['total_citations'] == 2
        assert stats['document_types']['standard'] == 1
        assert stats['average_citations_per_document'] == 2.0

    def test_repr(self):
        """Test string representation."""
        doc = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        self.tracker.add_document(doc)

        repr_str = repr(self.tracker)
        assert "ReferenceTracker" in repr_str
        assert "documents=1" in repr_str


class TestCreateStandardMetadata:
    """Test cases for create_standard_metadata helper function."""

    def test_create_basic_standard(self):
        """Test creating basic standard metadata."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        assert metadata.document_id == "IEC 61730-1:2016"
        assert metadata.document_type == DocumentType.STANDARD
        assert metadata.title == "PV module safety"
        assert metadata.standard_metadata is not None
        assert metadata.standard_metadata.organization == "IEC"

    def test_create_standard_with_year_extraction(self):
        """Test that year is extracted from standard_id if not provided."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC"
        )

        assert metadata.year == 2016
        assert metadata.standard_metadata.year == 2016

    def test_create_standard_with_all_fields(self):
        """Test creating standard with all optional fields."""
        metadata = create_standard_metadata(
            standard_id="IEC 61730-1:2016",
            title="PV module safety",
            organization="IEC",
            year=2016,
            edition="2nd edition",
            url="https://webstore.iec.ch/publication/1234"
        )

        assert metadata.standard_metadata.edition == "2nd edition"
        assert metadata.url == "https://webstore.iec.ch/publication/1234"
