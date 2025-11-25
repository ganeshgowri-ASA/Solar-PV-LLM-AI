"""Main citation manager module.

This module provides the main CitationManager class that orchestrates
all citation functionality including extraction, tracking, and formatting.
"""

from typing import List, Dict, Optional
import logging

from .citation_models import (
    Citation,
    CitationExtractionResult,
    CitationStyle,
    DocumentMetadata,
    ResponseCitations
)
from .citation_tracker import CitationTracker
from .citation_extractor import CitationExtractor
from .citation_formatter import CitationFormatter
from .reference_tracker import ReferenceTracker

logger = logging.getLogger(__name__)


class CitationManager:
    """Main citation manager that orchestrates all citation operations.

    This class provides a high-level interface for:
    1. Processing LLM responses and adding citations
    2. Managing document references
    3. Formatting citations in various styles
    4. Tracking citation usage across responses

    Example usage:
        >>> manager = CitationManager(style=CitationStyle.IEC)
        >>>
        >>> # Add source documents
        >>> manager.add_document(doc_metadata)
        >>>
        >>> # Process a response
        >>> result = manager.process_response(
        ...     response_text="The module must meet IEC 61730 requirements.",
        ...     retrieved_documents=[...]
        ... )
        >>>
        >>> print(result.text_with_citations)
        >>> print(result.reference_section)
    """

    def __init__(
        self,
        style: CitationStyle = CitationStyle.IEC,
        auto_inject_citations: bool = True
    ):
        """Initialize the citation manager.

        Args:
            style: Citation style to use (default: IEC)
            auto_inject_citations: Whether to automatically inject citations (default: True)
        """
        self.citation_tracker = CitationTracker()
        self.reference_tracker = ReferenceTracker()
        self.citation_extractor = CitationExtractor(
            citation_tracker=self.citation_tracker,
            reference_tracker=self.reference_tracker
        )
        self.citation_formatter = CitationFormatter(style=style)
        self.auto_inject_citations = auto_inject_citations

        self._response_counter = 0
        logger.info(f"Citation manager initialized with {style.value} style")

    def add_document(self, metadata: DocumentMetadata) -> str:
        """Add a document to the reference tracker.

        Args:
            metadata: Document metadata to add

        Returns:
            The document ID
        """
        return self.reference_tracker.add_document(metadata)

    def add_documents(self, documents: List[DocumentMetadata]) -> List[str]:
        """Add multiple documents to the reference tracker.

        Args:
            documents: List of document metadata to add

        Returns:
            List of document IDs
        """
        return [self.add_document(doc) for doc in documents]

    def get_document(self, document_id: str) -> Optional[DocumentMetadata]:
        """Get document metadata by ID.

        Args:
            document_id: The document ID

        Returns:
            DocumentMetadata if found, None otherwise
        """
        return self.reference_tracker.get_document(document_id)

    def set_citation_style(self, style: CitationStyle):
        """Change the citation style.

        Args:
            style: The new citation style
        """
        self.citation_formatter.set_style(style)
        logger.info(f"Citation style changed to {style.value}")

    def process_response(
        self,
        response_text: str,
        retrieved_documents: List[Dict],
        response_id: Optional[str] = None
    ) -> CitationExtractionResult:
        """Process an LLM response and add citations.

        This is the main method for processing responses. It:
        1. Extracts citations from the response
        2. Matches text to source documents
        3. Injects inline citations (if enabled)
        4. Formats the reference section

        Args:
            response_text: The LLM-generated response text
            retrieved_documents: Documents from RAG retrieval
                Each should have: {'document_id', 'content', 'metadata', 'score'}
            response_id: Optional ID for this response (auto-generated if not provided)

        Returns:
            CitationExtractionResult with complete citation information
        """
        # Generate response ID if not provided
        if response_id is None:
            self._response_counter += 1
            response_id = f"response_{self._response_counter}"

        logger.info(f"Processing response {response_id}")

        # Reset tracker for new response
        self.citation_tracker.reset()

        # Extract citations
        extraction_result = self.citation_extractor.extract_citations_from_response(
            response_text=response_text,
            retrieved_documents=retrieved_documents,
            auto_inject=self.auto_inject_citations
        )

        citations = extraction_result['citations']
        text_with_citations = extraction_result['text_with_citations']

        # Get document metadata for all cited documents
        cited_document_ids = {c.document_id for c in citations}
        documents = {
            doc_id: self.reference_tracker.get_document(doc_id)
            for doc_id in cited_document_ids
        }

        # Remove None values (documents not in tracker)
        documents = {k: v for k, v in documents.items() if v is not None}

        # Format reference section
        reference_section = ""
        if citations:
            reference_section = self.citation_formatter.format_reference_list(
                citations=citations,
                documents=documents,
                include_header=True
            )

        # Create result
        result = CitationExtractionResult(
            original_text=response_text,
            text_with_citations=text_with_citations,
            citations_found=citations,
            reference_section=reference_section,
            extraction_metadata={
                'response_id': response_id,
                'citation_count': len(citations),
                'document_count': len(cited_document_ids),
                'standard_ids_found': extraction_result.get('standard_ids_found', []),
                'clause_refs_found': extraction_result.get('clause_refs_found', [])
            }
        )

        logger.info(
            f"Response processed: {len(citations)} citations, "
            f"{len(cited_document_ids)} documents"
        )

        return result

    def create_response_citations(
        self,
        response_id: str,
        citations: List[Citation]
    ) -> ResponseCitations:
        """Create a ResponseCitations object for a response.

        Args:
            response_id: ID of the response
            citations: List of citations

        Returns:
            ResponseCitations object
        """
        response_citations = ResponseCitations(response_id=response_id)

        for citation in citations:
            response_citations.add_citation(citation)

            # Add document metadata if available
            doc = self.reference_tracker.get_document(citation.document_id)
            if doc:
                response_citations.referenced_documents[citation.document_id] = doc

        return response_citations

    def format_response_with_citations(
        self,
        response_text: str,
        citations: List[Citation]
    ) -> str:
        """Format a response with citations and reference list.

        Args:
            response_text: The response text (should already have inline citations)
            citations: List of citations

        Returns:
            Complete formatted response with reference section
        """
        # Get document metadata
        cited_document_ids = {c.document_id for c in citations}
        documents = {
            doc_id: self.reference_tracker.get_document(doc_id)
            for doc_id in cited_document_ids
        }
        documents = {k: v for k, v in documents.items() if v is not None}

        return self.citation_formatter.format_complete_response(
            response_text=response_text,
            citations=citations,
            documents=documents,
            insert_inline=False  # Assume already inserted
        )

    def get_statistics(self) -> Dict:
        """Get statistics about citations and references.

        Returns:
            Dictionary with statistics
        """
        ref_stats = self.reference_tracker.get_statistics()

        return {
            **ref_stats,
            'citation_tracker': {
                'current_citation_count': self.citation_tracker.get_citation_count(),
                'current_document_count': self.citation_tracker.get_document_count()
            },
            'responses_processed': self._response_counter
        }

    def export_references(self, file_path: str):
        """Export all tracked references to a JSON file.

        Args:
            file_path: Path to save the JSON file
        """
        self.reference_tracker.export_to_json(file_path)
        logger.info(f"References exported to {file_path}")

    def import_references(self, file_path: str):
        """Import references from a JSON file.

        Args:
            file_path: Path to the JSON file
        """
        self.reference_tracker.import_from_json(file_path)
        logger.info(f"References imported from {file_path}")

    def reset(self):
        """Reset all trackers (useful between sessions or for testing)."""
        self.citation_tracker.reset()
        self.reference_tracker.clear()
        self._response_counter = 0
        logger.info("Citation manager reset")

    def __repr__(self) -> str:
        """String representation of the citation manager."""
        stats = self.get_statistics()
        return (
            f"CitationManager("
            f"style={self.citation_formatter.style.value}, "
            f"documents={stats['total_documents']}, "
            f"responses={stats['responses_processed']})"
        )
