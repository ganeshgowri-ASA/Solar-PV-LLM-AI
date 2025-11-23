"""Citation formatter for generating formatted citations in various styles.

This module provides functionality to format citations according to different
standards including IEC, IEEE, ISO, APA, and others.
"""

from typing import List, Dict, Optional
import logging
from abc import ABC, abstractmethod

from .citation_models import (
    Citation,
    DocumentMetadata,
    FormattedCitation,
    CitationStyle,
    DocumentType,
    ClauseReference
)

logger = logging.getLogger(__name__)


class CitationStyleFormatter(ABC):
    """Abstract base class for citation style formatters."""

    @abstractmethod
    def format_inline(self, citation_number: int) -> str:
        """Format inline citation marker.

        Args:
            citation_number: The citation number

        Returns:
            Formatted inline citation (e.g., '[1]', '(1)', etc.)
        """
        pass

    @abstractmethod
    def format_reference(
        self,
        citation_number: int,
        metadata: DocumentMetadata,
        clause_refs: Optional[List[ClauseReference]] = None
    ) -> str:
        """Format full reference entry.

        Args:
            citation_number: The citation number
            metadata: Document metadata
            clause_refs: Optional list of clause references

        Returns:
            Formatted reference entry
        """
        pass


class IECFormatter(CitationStyleFormatter):
    """Formatter for IEC citation style.

    IEC format typically follows:
    [1] IEC 61730-1:2016, Photovoltaic (PV) module safety qualification - Part 1: Requirements for construction
    [2] IEC 61215-1:2016, Terrestrial photovoltaic (PV) modules - Design qualification and type approval, Clause 10.2
    """

    def format_inline(self, citation_number: int) -> str:
        """Format inline citation as [number]."""
        return f"[{citation_number}]"

    def format_reference(
        self,
        citation_number: int,
        metadata: DocumentMetadata,
        clause_refs: Optional[List[ClauseReference]] = None
    ) -> str:
        """Format reference in IEC style."""
        parts = [f"[{citation_number}]"]

        # Standard ID or title
        if metadata.standard_metadata:
            std_meta = metadata.standard_metadata
            parts.append(std_meta.standard_id)

            # Add title
            parts.append(std_meta.title)

            # Add edition if available
            if std_meta.edition:
                parts.append(std_meta.edition)

        else:
            # Non-standard document
            if metadata.authors:
                authors_str = ", ".join(metadata.authors[:3])
                if len(metadata.authors) > 3:
                    authors_str += " et al."
                parts.append(authors_str)

            parts.append(metadata.title)

            if metadata.year:
                parts.append(f"({metadata.year})")

            if metadata.publisher:
                parts.append(metadata.publisher)

        # Add clause references if any
        if clause_refs:
            clause_strs = [ref.clause_number for ref in clause_refs]
            if clause_strs:
                clause_part = "Clause " + ", ".join(clause_strs)
                parts.append(clause_part)

        # Join with appropriate separators
        # First separator after number, then commas
        if len(parts) > 1:
            result = parts[0] + " " + ", ".join(parts[1:])
        else:
            result = parts[0]

        return result


class IEEEFormatter(CitationStyleFormatter):
    """Formatter for IEEE citation style.

    IEEE format:
    [1] IEC 61730-1:2016, "Photovoltaic (PV) module safety qualification - Part 1: Requirements for construction."
    """

    def format_inline(self, citation_number: int) -> str:
        """Format inline citation as [number]."""
        return f"[{citation_number}]"

    def format_reference(
        self,
        citation_number: int,
        metadata: DocumentMetadata,
        clause_refs: Optional[List[ClauseReference]] = None
    ) -> str:
        """Format reference in IEEE style."""
        parts = [f"[{citation_number}]"]

        if metadata.standard_metadata:
            std_meta = metadata.standard_metadata
            parts.append(f'{std_meta.standard_id}, "{std_meta.title}."')
        else:
            if metadata.authors:
                authors_str = ", ".join(metadata.authors[:3])
                if len(metadata.authors) > 3:
                    authors_str += " et al."
                parts.append(authors_str + ",")

            parts.append(f'"{metadata.title},"')

            if metadata.publisher:
                parts.append(metadata.publisher + ",")

            if metadata.year:
                parts.append(f"{metadata.year}.")

        # Add clause references
        if clause_refs:
            clause_strs = [ref.clause_number for ref in clause_refs]
            if clause_strs:
                parts.append("Clause " + ", ".join(clause_strs) + ".")

        return " ".join(parts)


class ISOFormatter(CitationStyleFormatter):
    """Formatter for ISO citation style.

    ISO format similar to IEC.
    """

    def format_inline(self, citation_number: int) -> str:
        """Format inline citation as [number]."""
        return f"[{citation_number}]"

    def format_reference(
        self,
        citation_number: int,
        metadata: DocumentMetadata,
        clause_refs: Optional[List[ClauseReference]] = None
    ) -> str:
        """Format reference in ISO style."""
        # ISO style is very similar to IEC
        iec_formatter = IECFormatter()
        return iec_formatter.format_reference(citation_number, metadata, clause_refs)


class APAFormatter(CitationStyleFormatter):
    """Formatter for APA citation style.

    APA format:
    1. Author, A. A. (Year). Title of work. Publisher.
    """

    def format_inline(self, citation_number: int) -> str:
        """Format inline citation as (number)."""
        return f"({citation_number})"

    def format_reference(
        self,
        citation_number: int,
        metadata: DocumentMetadata,
        clause_refs: Optional[List[ClauseReference]] = None
    ) -> str:
        """Format reference in APA style."""
        parts = [f"{citation_number}."]

        if metadata.authors:
            # Format authors: Last, F. M.
            authors_str = ", ".join(metadata.authors[:7])
            if len(metadata.authors) > 7:
                authors_str += ", et al."
            parts.append(authors_str + ".")

        if metadata.year:
            parts.append(f"({metadata.year}).")

        parts.append(metadata.title + ".")

        if metadata.publisher:
            parts.append(metadata.publisher + ".")

        # Add URL if available
        if metadata.url:
            parts.append(metadata.url)

        return " ".join(parts)


class CitationFormatter:
    """Main citation formatter that supports multiple styles."""

    FORMATTERS = {
        CitationStyle.IEC: IECFormatter(),
        CitationStyle.IEEE: IEEEFormatter(),
        CitationStyle.ISO: ISOFormatter(),
        CitationStyle.APA: APAFormatter(),
    }

    def __init__(self, style: CitationStyle = CitationStyle.IEC):
        """Initialize the citation formatter.

        Args:
            style: The citation style to use (default: IEC)
        """
        self.style = style
        self.formatter = self.FORMATTERS.get(style, IECFormatter())
        logger.debug(f"Initialized citation formatter with {style.value} style")

    def set_style(self, style: CitationStyle):
        """Change the citation style.

        Args:
            style: The new citation style
        """
        self.style = style
        self.formatter = self.FORMATTERS.get(style, IECFormatter())
        logger.debug(f"Changed citation style to {style.value}")

    def format_inline_citation(self, citation: Citation) -> str:
        """Format a single inline citation.

        Args:
            citation: The citation to format

        Returns:
            Formatted inline citation marker
        """
        return self.formatter.format_inline(citation.citation_number)

    def format_reference_entry(
        self,
        citation: Citation,
        metadata: DocumentMetadata
    ) -> str:
        """Format a single reference list entry.

        Args:
            citation: The citation
            metadata: Document metadata

        Returns:
            Formatted reference entry
        """
        return self.formatter.format_reference(
            citation.citation_number,
            metadata,
            citation.clause_references
        )

    def format_reference_list(
        self,
        citations: List[Citation],
        documents: Dict[str, DocumentMetadata],
        include_header: bool = True
    ) -> str:
        """Format a complete reference list.

        Args:
            citations: List of all citations
            documents: Dictionary mapping document IDs to metadata
            include_header: Whether to include "References" header

        Returns:
            Formatted reference section
        """
        lines = []

        if include_header:
            lines.append("References")
            lines.append("=" * 50)
            lines.append("")

        # Group citations by document and sort by citation number
        doc_citations = {}
        for citation in citations:
            if citation.document_id not in doc_citations:
                doc_citations[citation.document_id] = []
            doc_citations[citation.document_id].append(citation)

        # Get unique citations (first citation for each document)
        unique_citations = []
        seen_docs = set()
        for citation in sorted(citations, key=lambda c: c.citation_number):
            if citation.document_id not in seen_docs:
                unique_citations.append(citation)
                seen_docs.add(citation.document_id)

        # Format each reference
        for citation in unique_citations:
            metadata = documents.get(citation.document_id)
            if metadata:
                ref_entry = self.format_reference_entry(citation, metadata)
                lines.append(ref_entry)
            else:
                logger.warning(f"No metadata found for document {citation.document_id}")
                lines.append(f"[{citation.citation_number}] {citation.document_id}")

        return "\n".join(lines)

    def create_formatted_citation(
        self,
        citation: Citation,
        metadata: DocumentMetadata
    ) -> FormattedCitation:
        """Create a FormattedCitation object.

        Args:
            citation: The citation
            metadata: Document metadata

        Returns:
            FormattedCitation object
        """
        return FormattedCitation(
            citation_number=citation.citation_number,
            inline_format=self.format_inline_citation(citation),
            reference_format=self.format_reference_entry(citation, metadata),
            style=self.style
        )

    def format_complete_response(
        self,
        response_text: str,
        citations: List[Citation],
        documents: Dict[str, DocumentMetadata],
        insert_inline: bool = True
    ) -> str:
        """Format a complete response with citations and references.

        Args:
            response_text: The response text
            citations: List of citations
            documents: Document metadata
            insert_inline: Whether to insert inline citations

        Returns:
            Complete formatted response with reference list
        """
        result_parts = []

        # Add response text (with inline citations if requested)
        if insert_inline:
            # Text should already have inline citations from extractor
            result_parts.append(response_text)
        else:
            result_parts.append(response_text)

        # Add spacing
        result_parts.append("\n")

        # Add reference list
        if citations:
            ref_list = self.format_reference_list(citations, documents, include_header=True)
            result_parts.append(ref_list)

        return "\n".join(result_parts)
