"""Reference tracker for managing document metadata and source tracking.

This module provides functionality to track and manage metadata for all
documents that are referenced in responses.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
import logging
import json
from pathlib import Path

from .citation_models import DocumentMetadata, DocumentType, StandardMetadata

logger = logging.getLogger(__name__)


class ReferenceTracker:
    """Tracks and manages metadata for referenced documents.

    This class maintains a registry of all documents that have been referenced,
    including their metadata and retrieval information.
    """

    def __init__(self):
        """Initialize the reference tracker."""
        self._documents: Dict[str, DocumentMetadata] = {}
        self._document_usage: Dict[str, int] = {}  # Track how many times each doc is cited

    def add_document(self, metadata: DocumentMetadata) -> str:
        """Add or update a document in the tracker.

        Args:
            metadata: Document metadata to add

        Returns:
            The document ID
        """
        doc_id = metadata.document_id
        if doc_id in self._documents:
            logger.debug(f"Updating existing document: {doc_id}")
        else:
            logger.debug(f"Adding new document: {doc_id}")
            self._document_usage[doc_id] = 0

        self._documents[doc_id] = metadata
        return doc_id

    def get_document(self, document_id: str) -> Optional[DocumentMetadata]:
        """Get document metadata by ID.

        Args:
            document_id: The document ID to look up

        Returns:
            DocumentMetadata if found, None otherwise
        """
        return self._documents.get(document_id)

    def has_document(self, document_id: str) -> bool:
        """Check if a document is tracked.

        Args:
            document_id: The document ID to check

        Returns:
            True if document is tracked, False otherwise
        """
        return document_id in self._documents

    def increment_usage(self, document_id: str) -> int:
        """Increment the usage counter for a document.

        Args:
            document_id: The document ID

        Returns:
            The updated usage count

        Raises:
            ValueError: If document is not tracked
        """
        if document_id not in self._documents:
            raise ValueError(f"Document {document_id} not tracked")

        self._document_usage[document_id] = self._document_usage.get(document_id, 0) + 1
        logger.debug(f"Document {document_id} usage count: {self._document_usage[document_id]}")
        return self._document_usage[document_id]

    def get_usage_count(self, document_id: str) -> int:
        """Get the usage count for a document.

        Args:
            document_id: The document ID

        Returns:
            The usage count (0 if not tracked)
        """
        return self._document_usage.get(document_id, 0)

    def get_all_documents(self) -> List[DocumentMetadata]:
        """Get all tracked documents.

        Returns:
            List of all document metadata
        """
        return list(self._documents.values())

    def get_documents_by_type(self, doc_type: DocumentType) -> List[DocumentMetadata]:
        """Get all documents of a specific type.

        Args:
            doc_type: The document type to filter by

        Returns:
            List of matching documents
        """
        return [
            doc for doc in self._documents.values()
            if doc.document_type == doc_type
        ]

    def get_standards(self) -> List[DocumentMetadata]:
        """Get all standard documents.

        Returns:
            List of all standard documents
        """
        return self.get_documents_by_type(DocumentType.STANDARD)

    def search_by_title(self, query: str, case_sensitive: bool = False) -> List[DocumentMetadata]:
        """Search documents by title.

        Args:
            query: Search query string
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            List of matching documents
        """
        if not case_sensitive:
            query = query.lower()

        matches = []
        for doc in self._documents.values():
            title = doc.title if case_sensitive else doc.title.lower()
            if query in title:
                matches.append(doc)

        return matches

    def search_by_standard_id(self, standard_id: str) -> Optional[DocumentMetadata]:
        """Search for a document by standard ID.

        Args:
            standard_id: The standard ID to search for (e.g., 'IEC 61730-1:2016')

        Returns:
            DocumentMetadata if found, None otherwise
        """
        for doc in self._documents.values():
            if doc.standard_metadata and doc.standard_metadata.standard_id == standard_id:
                return doc
        return None

    def get_most_cited_documents(self, limit: int = 10) -> List[tuple[DocumentMetadata, int]]:
        """Get the most frequently cited documents.

        Args:
            limit: Maximum number of documents to return

        Returns:
            List of tuples (DocumentMetadata, usage_count) sorted by usage
        """
        sorted_docs = sorted(
            [(self._documents[doc_id], count) for doc_id, count in self._document_usage.items()],
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_docs[:limit]

    def clear(self):
        """Clear all tracked documents and usage data."""
        self._documents.clear()
        self._document_usage.clear()
        logger.debug("Reference tracker cleared")

    def export_to_json(self, file_path: str):
        """Export tracked documents to JSON file.

        Args:
            file_path: Path to save the JSON file
        """
        data = {
            "documents": {
                doc_id: doc.model_dump(mode='json')
                for doc_id, doc in self._documents.items()
            },
            "usage": self._document_usage,
            "exported_at": datetime.now().isoformat()
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(self._documents)} documents to {file_path}")

    def import_from_json(self, file_path: str):
        """Import documents from JSON file.

        Args:
            file_path: Path to the JSON file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON format is invalid
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "documents" not in data:
            raise ValueError("Invalid JSON format: missing 'documents' key")

        for doc_id, doc_data in data["documents"].items():
            metadata = DocumentMetadata(**doc_data)
            self._documents[doc_id] = metadata

        if "usage" in data:
            self._document_usage.update(data["usage"])

        logger.info(f"Imported {len(self._documents)} documents from {file_path}")

    def get_document_count(self) -> int:
        """Get the total number of tracked documents.

        Returns:
            Number of documents
        """
        return len(self._documents)

    def get_statistics(self) -> Dict:
        """Get statistics about tracked documents.

        Returns:
            Dictionary with statistics
        """
        doc_types = {}
        for doc in self._documents.values():
            doc_type = doc.document_type.value
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

        total_usage = sum(self._document_usage.values())

        return {
            "total_documents": len(self._documents),
            "total_citations": total_usage,
            "document_types": doc_types,
            "average_citations_per_document": (
                total_usage / len(self._documents) if self._documents else 0
            )
        }

    def __repr__(self) -> str:
        """String representation of the tracker."""
        return f"ReferenceTracker(documents={len(self._documents)})"


def create_standard_metadata(
    standard_id: str,
    title: str,
    organization: str = "IEC",
    year: Optional[int] = None,
    edition: Optional[str] = None,
    url: Optional[str] = None
) -> DocumentMetadata:
    """Helper function to create metadata for a standard document.

    Args:
        standard_id: Standard identifier (e.g., 'IEC 61730-1:2016')
        title: Full title of the standard
        organization: Standards organization (default: 'IEC')
        year: Publication year
        edition: Edition information
        url: URL to the standard

    Returns:
        DocumentMetadata object configured for a standard
    """
    # Extract year from standard_id if not provided and it's in the ID
    if year is None and ':' in standard_id:
        try:
            year = int(standard_id.split(':')[1])
        except (ValueError, IndexError):
            pass

    standard_meta = StandardMetadata(
        standard_id=standard_id,
        title=title,
        organization=organization,
        year=year,
        edition=edition,
        url=url
    )

    return DocumentMetadata(
        document_id=standard_id,
        document_type=DocumentType.STANDARD,
        title=title,
        year=year,
        publisher=organization,
        url=url,
        standard_metadata=standard_meta,
        retrieved_date=datetime.now()
    )
