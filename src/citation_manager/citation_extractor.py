"""Citation extractor for identifying and extracting citation references.

This module provides functionality to extract standard IDs, clause references,
and other citation-worthy content from documents and LLM responses.
"""

import re
from typing import List, Dict, Optional, Tuple, Set
import logging

from .citation_models import ClauseReference, Citation, DocumentMetadata
from .citation_tracker import CitationTracker
from .reference_tracker import ReferenceTracker

logger = logging.getLogger(__name__)


class CitationExtractor:
    """Extracts citations from text and matches them to source documents.

    This class provides methods to:
    1. Extract standard IDs (IEC, IEEE, ISO, etc.) from text
    2. Extract clause/section references
    3. Match text to source documents from retrieval context
    4. Insert inline citations into LLM responses
    """

    # Regex patterns for standard identification
    STANDARD_PATTERNS = {
        'iec': re.compile(r'IEC\s+(\d+(?:-\d+)?(?:-\d+)?(?::\d{4})?(?:\+[A-Z]+\d*:\d{4})?)', re.IGNORECASE),
        'ieee': re.compile(r'IEEE\s+(\d+(?:\.\d+)?(?:-\d{4})?)', re.IGNORECASE),
        'iso': re.compile(r'ISO\s+(\d+(?:-\d+)?(?::\d{4})?)', re.IGNORECASE),
        'nec': re.compile(r'NEC\s+(\d+(?:\.\d+)?)', re.IGNORECASE),
        'ul': re.compile(r'UL\s+(\d+)', re.IGNORECASE),
    }

    # Regex patterns for clause/section references
    CLAUSE_PATTERNS = [
        re.compile(r'(?:Clause|Section|§)\s+(\d+(?:\.\d+)*)', re.IGNORECASE),
        re.compile(r'(?:Annex|Appendix)\s+([A-Z](?:\.\d+)*)', re.IGNORECASE),
        re.compile(r'(?:Table|Figure)\s+(\d+(?:\.\d+)*)', re.IGNORECASE),
        re.compile(r'(?:Article)\s+(\d+(?:\.\d+)*)', re.IGNORECASE),
    ]

    def __init__(
        self,
        citation_tracker: Optional[CitationTracker] = None,
        reference_tracker: Optional[ReferenceTracker] = None
    ):
        """Initialize the citation extractor.

        Args:
            citation_tracker: Optional citation tracker instance
            reference_tracker: Optional reference tracker instance
        """
        self.citation_tracker = citation_tracker or CitationTracker()
        self.reference_tracker = reference_tracker or ReferenceTracker()

    def extract_standard_ids(self, text: str) -> List[Tuple[str, str]]:
        """Extract standard IDs from text.

        Args:
            text: Text to search for standard IDs

        Returns:
            List of tuples (organization, standard_id)
        """
        found_standards = []

        for org, pattern in self.STANDARD_PATTERNS.items():
            matches = pattern.finditer(text)
            for match in matches:
                standard_id = f"{org.upper()} {match.group(1)}"
                found_standards.append((org.upper(), standard_id))
                logger.debug(f"Found standard: {standard_id}")

        return found_standards

    def extract_clause_references(self, text: str) -> List[str]:
        """Extract clause/section references from text.

        Args:
            text: Text to search for clause references

        Returns:
            List of clause reference strings
        """
        found_clauses = []

        for pattern in self.CLAUSE_PATTERNS:
            matches = pattern.finditer(text)
            for match in matches:
                clause_ref = match.group(0)
                found_clauses.append(clause_ref)
                logger.debug(f"Found clause reference: {clause_ref}")

        return found_clauses

    def create_clause_reference(
        self,
        document_id: str,
        clause_number: str,
        clause_title: Optional[str] = None,
        page_number: Optional[int] = None,
        excerpt: Optional[str] = None
    ) -> ClauseReference:
        """Create a ClauseReference object.

        Args:
            document_id: Document identifier
            clause_number: Clause/section number
            clause_title: Optional clause title
            page_number: Optional page number
            excerpt: Optional text excerpt

        Returns:
            ClauseReference object
        """
        return ClauseReference(
            document_id=document_id,
            clause_number=clause_number,
            clause_title=clause_title,
            page_number=page_number,
            excerpt=excerpt
        )

    def match_text_to_documents(
        self,
        text: str,
        retrieved_documents: List[Dict],
        similarity_threshold: float = 0.7
    ) -> List[Tuple[str, float, Optional[str]]]:
        """Match text segments to source documents.

        Args:
            text: Text to analyze
            retrieved_documents: List of documents from RAG retrieval
                Each should have: {'document_id', 'content', 'metadata', 'score'}
            similarity_threshold: Minimum similarity score to consider a match

        Returns:
            List of tuples (document_id, confidence, matched_excerpt)
        """
        matches = []

        # Simple keyword-based matching
        # In production, this would use embeddings or more sophisticated matching
        text_lower = text.lower()

        for doc in retrieved_documents:
            doc_id = doc.get('document_id', '')
            doc_content = doc.get('content', '')
            doc_score = doc.get('score', 0.0)

            # Check if document content appears in the text or vice versa
            if doc_content.lower() in text_lower or any(
                word in doc_content.lower()
                for word in text_lower.split()
                if len(word) > 4
            ):
                # Extract a relevant excerpt
                excerpt = self._extract_excerpt(text, doc_content)
                confidence = min(1.0, doc_score + 0.3)  # Boost confidence for matches

                if confidence >= similarity_threshold:
                    matches.append((doc_id, confidence, excerpt))
                    logger.debug(f"Matched document {doc_id} with confidence {confidence:.2f}")

        return matches

    def _extract_excerpt(self, text: str, doc_content: str, max_length: int = 150) -> str:
        """Extract a relevant excerpt from document content.

        Args:
            text: The text being analyzed
            doc_content: Document content to extract from
            max_length: Maximum excerpt length

        Returns:
            Extracted excerpt
        """
        # Simple approach: take the first max_length characters
        excerpt = doc_content[:max_length]
        if len(doc_content) > max_length:
            excerpt += "..."
        return excerpt

    def inject_citations(
        self,
        text: str,
        citations: List[Citation],
        citation_format: str = "[{number}]"
    ) -> str:
        """Inject inline citations into text.

        Args:
            text: Original text
            citations: List of citations to inject
            citation_format: Format string for citations (default: "[{number}]")

        Returns:
            Text with citations injected
        """
        # Sort citations by matched_text position if available
        # For now, we'll append citations at sentence ends where relevant

        result = text

        for citation in sorted(citations, key=lambda c: c.citation_number):
            citation_marker = citation_format.format(number=citation.citation_number)

            if citation.matched_text:
                # Try to find the matched text and insert citation after it
                matched_text = citation.matched_text
                if matched_text in result:
                    # Insert citation after the matched text
                    result = result.replace(
                        matched_text,
                        f"{matched_text}{citation_marker}",
                        1  # Only replace first occurrence
                    )
                    logger.debug(f"Injected citation {citation.citation_number} after '{matched_text[:50]}...'")
                else:
                    logger.warning(f"Could not find matched text for citation {citation.citation_number}")

        return result

    def extract_citations_from_response(
        self,
        response_text: str,
        retrieved_documents: List[Dict],
        auto_inject: bool = True
    ) -> Dict:
        """Extract and optionally inject citations from an LLM response.

        This is the main method that orchestrates the citation extraction process.

        Args:
            response_text: The LLM-generated response text
            retrieved_documents: Documents retrieved from RAG that were used
            auto_inject: Whether to automatically inject citations into text

        Returns:
            Dictionary with:
                - original_text: Original response
                - text_with_citations: Response with citations (if auto_inject=True)
                - citations: List of Citation objects
                - document_matches: Document matching information
        """
        logger.info("Starting citation extraction from response")

        # Reset tracker for new response
        self.citation_tracker.reset()

        citations = []
        document_matches = []

        # 1. Extract standard IDs mentioned in response
        standard_ids = self.extract_standard_ids(response_text)
        logger.debug(f"Found {len(standard_ids)} standard IDs")

        # 2. Extract clause references
        clause_refs = self.extract_clause_references(response_text)
        logger.debug(f"Found {len(clause_refs)} clause references")

        # 3. Match response text to retrieved documents
        doc_matches = self.match_text_to_documents(response_text, retrieved_documents)
        logger.debug(f"Matched {len(doc_matches)} documents")

        # 4. Create citations for matched documents
        for doc_id, confidence, excerpt in doc_matches:
            # Find relevant clause references for this document
            doc_clause_refs = []

            # Check if document metadata is in reference tracker
            doc_metadata = self.reference_tracker.get_document(doc_id)
            if doc_metadata:
                # Extract clauses that might be relevant to this document
                for clause_ref_text in clause_refs:
                    clause_ref_obj = self.create_clause_reference(
                        document_id=doc_id,
                        clause_number=clause_ref_text,
                        excerpt=excerpt
                    )
                    doc_clause_refs.append(clause_ref_obj)

            # Create citation
            citation = self.citation_tracker.create_citation(
                document_id=doc_id,
                clause_references=doc_clause_refs,
                matched_text=excerpt,
                confidence=confidence
            )
            citations.append(citation)
            document_matches.append({
                'document_id': doc_id,
                'confidence': confidence,
                'excerpt': excerpt,
                'citation_number': citation.citation_number
            })

            # Update reference tracker usage
            if self.reference_tracker.has_document(doc_id):
                self.reference_tracker.increment_usage(doc_id)

        # 5. Inject citations if requested
        text_with_citations = response_text
        if auto_inject and citations:
            text_with_citations = self.inject_citations(response_text, citations)

        logger.info(f"Citation extraction complete: {len(citations)} citations created")

        return {
            'original_text': response_text,
            'text_with_citations': text_with_citations,
            'citations': citations,
            'document_matches': document_matches,
            'standard_ids_found': standard_ids,
            'clause_refs_found': clause_refs
        }

    def extract_citations_from_context(
        self,
        context_chunks: List[Dict]
    ) -> List[ClauseReference]:
        """Extract clause references from retrieval context chunks.

        Args:
            context_chunks: List of context chunks from RAG
                Each should have: {'document_id', 'content', 'metadata'}

        Returns:
            List of ClauseReference objects found in context
        """
        clause_references = []

        for chunk in context_chunks:
            doc_id = chunk.get('document_id', '')
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})

            # Extract clauses from this chunk
            found_clauses = self.extract_clause_references(content)

            for clause_text in found_clauses:
                clause_ref = self.create_clause_reference(
                    document_id=doc_id,
                    clause_number=clause_text,
                    excerpt=content[:200],  # Take first 200 chars as excerpt
                    page_number=metadata.get('page_number')
                )
                clause_references.append(clause_ref)

        logger.info(f"Extracted {len(clause_references)} clause references from context")
        return clause_references
