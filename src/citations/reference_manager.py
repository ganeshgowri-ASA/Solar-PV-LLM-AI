"""
Reference Manager - Manage and validate citation references.

This module provides utilities for managing citation references,
validating citations, and ensuring consistency.
"""

from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
import re


class ReferenceManager:
    """Manages citation references and validates their consistency."""

    def __init__(self):
        """Initialize reference manager."""
        self.citations_by_id: Dict[int, object] = {}
        self.citations_by_standard: Dict[str, List[object]] = defaultdict(list)

    def add_citation(self, citation) -> None:
        """
        Add a citation to the manager.

        Args:
            citation: Citation object to add
        """
        self.citations_by_id[citation.citation_id] = citation

        if citation.standard_id:
            self.citations_by_standard[citation.standard_id].append(citation)

    def add_citations(self, citations: List) -> None:
        """
        Add multiple citations to the manager.

        Args:
            citations: List of Citation objects
        """
        for citation in citations:
            self.add_citation(citation)

    def get_citation_by_id(self, citation_id: int):
        """
        Get citation by ID.

        Args:
            citation_id: Citation ID to retrieve

        Returns:
            Citation object or None
        """
        return self.citations_by_id.get(citation_id)

    def get_citations_by_standard(self, standard_id: str) -> List:
        """
        Get all citations for a given standard.

        Args:
            standard_id: Standard ID to search for

        Returns:
            List of Citation objects
        """
        return self.citations_by_standard.get(standard_id, [])

    def validate_citations(self, text: str) -> Tuple[bool, List[str]]:
        """
        Validate that all citation references in text correspond to actual citations.

        Args:
            text: Text containing citation references (e.g., [1], [2])

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Find all citation references in text
        citation_refs = self._extract_citation_references(text)

        # Check if each reference has a corresponding citation
        for ref_id in citation_refs:
            if ref_id not in self.citations_by_id:
                errors.append(f"Citation [{ref_id}] referenced but not defined")

        # Check for unused citations
        referenced_ids = set(citation_refs)
        defined_ids = set(self.citations_by_id.keys())
        unused_ids = defined_ids - referenced_ids

        if unused_ids:
            for unused_id in sorted(unused_ids):
                errors.append(f"Citation [{unused_id}] defined but not referenced")

        is_valid = len(errors) == 0
        return is_valid, errors

    def _extract_citation_references(self, text: str) -> List[int]:
        """
        Extract all citation reference IDs from text.

        Args:
            text: Text containing citation references

        Returns:
            List of citation IDs found in text
        """
        # Match patterns like [1], [2], [3]
        pattern = r'\[(\d+)\]'
        matches = re.findall(pattern, text)

        # Convert to integers and return
        return [int(m) for m in matches]

    def validate_citation_sequence(self) -> Tuple[bool, List[str]]:
        """
        Validate that citation IDs are sequential and start from 1.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not self.citations_by_id:
            return True, []

        citation_ids = sorted(self.citations_by_id.keys())

        # Check if starts from 1
        if citation_ids[0] != 1:
            errors.append(f"Citation sequence should start from 1, but starts from {citation_ids[0]}")

        # Check for gaps in sequence
        for i in range(len(citation_ids) - 1):
            if citation_ids[i + 1] != citation_ids[i] + 1:
                errors.append(
                    f"Gap in citation sequence between [{citation_ids[i]}] and [{citation_ids[i + 1]}]"
                )

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_citation_statistics(self) -> Dict[str, any]:
        """
        Get statistics about citations.

        Returns:
            Dictionary with citation statistics
        """
        stats = {
            'total_citations': len(self.citations_by_id),
            'citations_with_standard_id': 0,
            'citations_with_clause_ref': 0,
            'citations_with_url': 0,
            'unique_standards': len(self.citations_by_standard),
            'standards': list(self.citations_by_standard.keys()),
        }

        for citation in self.citations_by_id.values():
            if citation.standard_id:
                stats['citations_with_standard_id'] += 1
            if citation.clause_ref:
                stats['citations_with_clause_ref'] += 1
            if citation.url:
                stats['citations_with_url'] += 1

        return stats

    def merge_duplicate_citations(self, citations: List) -> List:
        """
        Merge duplicate citations based on standard ID and clause reference.

        Args:
            citations: List of Citation objects

        Returns:
            List of deduplicated Citation objects
        """
        seen = {}
        merged = []

        for citation in citations:
            # Create key based on standard and clause
            key = (citation.standard_id or '', citation.clause_ref or '')

            if key not in seen:
                seen[key] = citation
                merged.append(citation)
            else:
                # Merge metadata from duplicate into existing citation
                existing = seen[key]
                if not existing.title and citation.title:
                    existing.title = citation.title
                if not existing.year and citation.year:
                    existing.year = citation.year
                if not existing.url and citation.url:
                    existing.url = citation.url

        return merged

    def renumber_citations(self, citations: List) -> List:
        """
        Renumber citations to ensure sequential IDs starting from 1.

        Args:
            citations: List of Citation objects

        Returns:
            List of Citation objects with renumbered IDs
        """
        for i, citation in enumerate(citations, start=1):
            citation.citation_id = i

        # Update internal tracking
        self.citations_by_id.clear()
        self.citations_by_standard.clear()
        self.add_citations(citations)

        return citations

    def clear(self) -> None:
        """Clear all citations from the manager."""
        self.citations_by_id.clear()
        self.citations_by_standard.clear()
