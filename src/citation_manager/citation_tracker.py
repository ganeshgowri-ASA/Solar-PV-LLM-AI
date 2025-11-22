"""Citation tracker for managing citation numbers across responses.

This module provides functionality to track and increment citation numbers,
ensuring each citation gets a unique sequential number within a response.
"""

from typing import Dict, List, Optional, Set
from collections import defaultdict
import logging

from .citation_models import Citation, DocumentMetadata

logger = logging.getLogger(__name__)


class CitationTracker:
    """Tracks citation numbers and manages citation assignment within a response.

    This class ensures that:
    1. Each citation gets a unique sequential number
    2. Multiple references to the same document can be tracked
    3. Citation numbers start from 1 for each new response
    """

    def __init__(self):
        """Initialize the citation tracker."""
        self._current_number = 0
        self._document_to_numbers: Dict[str, List[int]] = defaultdict(list)
        self._number_to_citation: Dict[int, Citation] = {}
        self._used_numbers: Set[int] = set()

    def reset(self):
        """Reset the tracker for a new response."""
        self._current_number = 0
        self._document_to_numbers.clear()
        self._number_to_citation.clear()
        self._used_numbers.clear()
        logger.debug("Citation tracker reset")

    def get_next_number(self) -> int:
        """Get the next available citation number.

        Returns:
            The next sequential citation number
        """
        self._current_number += 1
        self._used_numbers.add(self._current_number)
        logger.debug(f"Generated citation number: {self._current_number}")
        return self._current_number

    def register_citation(self, citation: Citation) -> int:
        """Register a citation and assign it a number if not already assigned.

        Args:
            citation: The citation to register

        Returns:
            The assigned citation number

        Raises:
            ValueError: If citation number is already in use
        """
        if citation.citation_number in self._used_numbers:
            if citation.citation_number in self._number_to_citation:
                existing = self._number_to_citation[citation.citation_number]
                if existing.document_id != citation.document_id:
                    raise ValueError(
                        f"Citation number {citation.citation_number} already assigned "
                        f"to different document"
                    )
            logger.debug(f"Citation number {citation.citation_number} already registered")
            return citation.citation_number

        # Register the citation
        self._used_numbers.add(citation.citation_number)
        self._number_to_citation[citation.citation_number] = citation
        self._document_to_numbers[citation.document_id].append(citation.citation_number)

        # Update current number if this citation number is higher
        if citation.citation_number > self._current_number:
            self._current_number = citation.citation_number

        logger.debug(
            f"Registered citation {citation.citation_number} for document {citation.document_id}"
        )
        return citation.citation_number

    def create_citation(
        self,
        document_id: str,
        clause_references: Optional[List] = None,
        matched_text: Optional[str] = None,
        confidence: float = 1.0
    ) -> Citation:
        """Create a new citation with an auto-assigned number.

        Args:
            document_id: ID of the document being cited
            clause_references: Optional list of clause references
            matched_text: Optional text that triggered the citation
            confidence: Confidence score for the citation match

        Returns:
            A new Citation object with assigned number
        """
        citation_number = self.get_next_number()
        citation = Citation(
            citation_number=citation_number,
            document_id=document_id,
            clause_references=clause_references or [],
            matched_text=matched_text,
            confidence=confidence
        )
        self.register_citation(citation)
        return citation

    def get_citation_by_number(self, number: int) -> Optional[Citation]:
        """Get a citation by its number.

        Args:
            number: The citation number to look up

        Returns:
            The Citation object if found, None otherwise
        """
        return self._number_to_citation.get(number)

    def get_citations_for_document(self, document_id: str) -> List[Citation]:
        """Get all citations for a specific document.

        Args:
            document_id: The document ID to look up

        Returns:
            List of citations for this document
        """
        citation_numbers = self._document_to_numbers.get(document_id, [])
        return [
            self._number_to_citation[num]
            for num in citation_numbers
            if num in self._number_to_citation
        ]

    def has_citation_for_document(self, document_id: str) -> bool:
        """Check if a document has already been cited.

        Args:
            document_id: The document ID to check

        Returns:
            True if document has been cited, False otherwise
        """
        return document_id in self._document_to_numbers

    def get_first_citation_number_for_document(self, document_id: str) -> Optional[int]:
        """Get the first citation number used for a document.

        Useful for subsequent references to use the same number.

        Args:
            document_id: The document ID to look up

        Returns:
            The first citation number if document has been cited, None otherwise
        """
        numbers = self._document_to_numbers.get(document_id, [])
        return numbers[0] if numbers else None

    def get_all_citations(self) -> List[Citation]:
        """Get all registered citations in number order.

        Returns:
            List of all citations sorted by citation number
        """
        return [
            self._number_to_citation[num]
            for num in sorted(self._number_to_citation.keys())
        ]

    def get_unique_document_ids(self) -> Set[str]:
        """Get set of all unique document IDs that have been cited.

        Returns:
            Set of document IDs
        """
        return set(self._document_to_numbers.keys())

    def get_citation_count(self) -> int:
        """Get the total number of citations registered.

        Returns:
            Total number of citations
        """
        return len(self._number_to_citation)

    def get_document_count(self) -> int:
        """Get the number of unique documents cited.

        Returns:
            Number of unique documents
        """
        return len(self._document_to_numbers)

    def __repr__(self) -> str:
        """String representation of the tracker."""
        return (
            f"CitationTracker("
            f"citations={self.get_citation_count()}, "
            f"documents={self.get_document_count()}, "
            f"next_number={self._current_number + 1})"
        )
