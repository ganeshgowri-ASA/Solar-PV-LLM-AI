"""
Citation Manager - Core orchestration for citation tracking and injection.

This module provides the main CitationManager class that coordinates citation
tracking, extraction, formatting, and injection for LLM responses.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class RetrievedDocument:
    """Represents a document retrieved from the RAG system."""
    content: str
    metadata: Dict[str, Any]
    doc_id: str
    score: float = 0.0


@dataclass
class Citation:
    """Represents a single citation with its metadata."""
    citation_id: int
    standard_id: Optional[str] = None
    clause_ref: Optional[str] = None
    title: Optional[str] = None
    year: Optional[str] = None
    url: Optional[str] = None
    page: Optional[str] = None
    source_doc_id: str = ""
    match_text: str = ""


class CitationTracker:
    """Tracks citation numbers across responses and manages citation state."""

    def __init__(self, start_index: int = 1):
        """
        Initialize citation tracker.

        Args:
            start_index: Starting citation number (default: 1)
        """
        self.current_index = start_index
        self.citations: List[Citation] = []
        self.citation_map: Dict[str, int] = {}  # Maps doc_id to citation_id

    def add_citation(self, citation: Citation) -> int:
        """
        Add a citation and return its citation ID.

        Args:
            citation: Citation object to add

        Returns:
            Citation ID assigned to this citation
        """
        # Check if we already have a citation for this source
        cache_key = self._get_cache_key(citation)

        if cache_key in self.citation_map:
            return self.citation_map[cache_key]

        # Assign new citation ID
        citation.citation_id = self.current_index
        self.citations.append(citation)
        self.citation_map[cache_key] = self.current_index

        self.current_index += 1
        return citation.citation_id

    def _get_cache_key(self, citation: Citation) -> str:
        """Generate a unique cache key for a citation."""
        # Use standard_id + clause_ref as primary key, fallback to doc_id
        if citation.standard_id and citation.clause_ref:
            return f"{citation.standard_id}:{citation.clause_ref}"
        elif citation.standard_id:
            return citation.standard_id
        return citation.source_doc_id

    def get_citations(self) -> List[Citation]:
        """Get all citations in order."""
        return list(self.citations)  # Return a copy to prevent external modifications

    def reset(self):
        """Reset the tracker for a new response."""
        self.current_index = 1
        self.citations.clear()
        self.citation_map.clear()


class CitationManager:
    """
    Main citation manager that orchestrates citation extraction,
    tracking, injection, and formatting.
    """

    def __init__(self, reset_per_response: bool = True):
        """
        Initialize citation manager.

        Args:
            reset_per_response: Whether to reset citation numbers for each response
        """
        self.tracker = CitationTracker()
        self.reset_per_response = reset_per_response

    def process_response(
        self,
        llm_response: str,
        retrieved_docs: List[RetrievedDocument],
        inject_citations: bool = True
    ) -> Tuple[str, List[Citation]]:
        """
        Process an LLM response by extracting citations from retrieved documents
        and injecting them into the response.

        Args:
            llm_response: The LLM-generated response text
            retrieved_docs: List of documents retrieved from RAG
            inject_citations: Whether to inject inline citations (default: True)

        Returns:
            Tuple of (processed_response, citations_list)
        """
        if self.reset_per_response:
            self.tracker.reset()

        # Extract citations from retrieved documents
        from .citation_extractor import CitationExtractor
        extractor = CitationExtractor()

        for doc in retrieved_docs:
            citation_data = extractor.extract_metadata(doc.metadata, doc.content)
            citation = Citation(
                citation_id=0,  # Will be assigned by tracker
                standard_id=citation_data.get('standard_id'),
                clause_ref=citation_data.get('clause_ref'),
                title=citation_data.get('title'),
                year=citation_data.get('year'),
                url=citation_data.get('url'),
                page=citation_data.get('page'),
                source_doc_id=doc.doc_id,
                match_text=doc.content[:200]  # Store snippet for matching
            )
            self.tracker.add_citation(citation)

        # Inject inline citations if requested
        if inject_citations:
            from .citation_injector import CitationInjector
            injector = CitationInjector()
            processed_response = injector.inject_citations(
                llm_response,
                retrieved_docs,
                self.tracker.get_citations()
            )
        else:
            processed_response = llm_response

        return processed_response, self.tracker.get_citations()

    def format_references(
        self,
        citations: Optional[List[Citation]] = None,
        style: str = 'iec'
    ) -> str:
        """
        Format citations as a reference list.

        Args:
            citations: List of citations to format (uses tracker citations if None)
            style: Citation style ('iec', 'ieee', 'apa')

        Returns:
            Formatted reference list as string
        """
        if citations is None:
            citations = self.tracker.get_citations()

        if not citations:
            return ""

        from .citation_formatter import IECCitationFormatter
        formatter = IECCitationFormatter()

        return formatter.format_reference_list(citations)

    def get_citations(self) -> List[Citation]:
        """Get current citations from tracker."""
        return self.tracker.get_citations()
