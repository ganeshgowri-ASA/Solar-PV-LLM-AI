"""
Citation Formatter - Format citations in various academic styles.

This module provides formatters for different citation styles, with primary
support for IEC (International Electrotechnical Commission) style.
"""

from typing import List, Optional
from abc import ABC, abstractmethod


class CitationFormatter(ABC):
    """Abstract base class for citation formatters."""

    @abstractmethod
    def format_citation(self, citation) -> str:
        """Format a single citation."""
        pass

    @abstractmethod
    def format_reference_list(self, citations: List) -> str:
        """Format a complete reference list."""
        pass


class IECCitationFormatter(CitationFormatter):
    """
    Formatter for IEC citation style.

    IEC style typically follows:
    [N] Standard ID, "Title", Year, Clause/Section.
    Example: [1] IEC 61215-1, "Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 1", 2021, Clause 5.2.
    """

    def format_citation(self, citation) -> str:
        """
        Format a single citation in IEC style.

        Args:
            citation: Citation object to format

        Returns:
            Formatted citation string
        """
        # Start with citation number
        formatted = f"[{citation.citation_id}]"

        parts = []

        # Add standard ID if available
        if citation.standard_id:
            parts.append(citation.standard_id)

        # Add title if available
        if citation.title:
            # Add quotes around title
            title = citation.title
            if not title.startswith('"'):
                title = f'"{title}"'
            parts.append(title)

        # Add year if available
        if citation.year:
            parts.append(str(citation.year))

        # Add clause reference if available
        if citation.clause_ref:
            # Ensure it's properly formatted
            clause = citation.clause_ref
            if not clause.lower().startswith(('clause', 'section', 'annex')):
                clause = f"Clause {clause}"
            parts.append(clause)

        # Add page if available (and no clause)
        elif citation.page:
            parts.append(f"p. {citation.page}")

        # Add URL if available
        if citation.url:
            parts.append(f"Available: {citation.url}")

        # Join citation number with parts
        if parts:
            formatted += " " + ", ".join(parts)

        # Ensure it ends with a period
        if not formatted.endswith('.'):
            formatted += '.'

        return formatted

    def format_reference_list(self, citations: List) -> str:
        """
        Format a complete reference list in IEC style.

        Args:
            citations: List of Citation objects

        Returns:
            Formatted reference list as string
        """
        if not citations:
            return ""

        # Sort citations by citation_id
        sorted_citations = sorted(citations, key=lambda c: c.citation_id)

        # Format header
        reference_list = ["References", "=" * 50, ""]

        # Format each citation
        for citation in sorted_citations:
            formatted = self.format_citation(citation)
            reference_list.append(formatted)

        # Join with newlines
        return "\n".join(reference_list)


class IEEECitationFormatter(CitationFormatter):
    """
    Formatter for IEEE citation style.

    IEEE style typically follows:
    [N] Author(s), "Title," Standard ID, Year.
    Example: [1] "Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 1," IEC 61215-1, 2021.
    """

    def format_citation(self, citation) -> str:
        """
        Format a single citation in IEEE style.

        Args:
            citation: Citation object to format

        Returns:
            Formatted citation string
        """
        parts = [f"[{citation.citation_id}]"]

        # Add title if available
        if citation.title:
            title = citation.title
            if not title.startswith('"'):
                title = f'"{title}"'
            # IEEE uses comma after title
            if not title.endswith(',') and not title.endswith('",'):
                if title.endswith('"'):
                    title = title[:-1] + ',"'
                else:
                    title += ','
            parts.append(title)

        # Add standard ID if available
        if citation.standard_id:
            parts.append(citation.standard_id)

        # Add year if available
        if citation.year:
            parts.append(str(citation.year))

        # Add clause/section if available
        if citation.clause_ref:
            parts.append(f"sec. {citation.clause_ref}")
        elif citation.page:
            parts.append(f"p. {citation.page}")

        # Add URL if available
        if citation.url:
            parts.append(f"[Online]. Available: {citation.url}")

        # Join parts with comma and space (except for first part)
        if len(parts) > 1:
            formatted = parts[0] + " " + ", ".join(parts[1:])
        else:
            formatted = parts[0]

        # Ensure it ends with a period
        if not formatted.endswith('.'):
            formatted += '.'

        return formatted

    def format_reference_list(self, citations: List) -> str:
        """
        Format a complete reference list in IEEE style.

        Args:
            citations: List of Citation objects

        Returns:
            Formatted reference list as string
        """
        if not citations:
            return ""

        # Sort citations by citation_id
        sorted_citations = sorted(citations, key=lambda c: c.citation_id)

        # Format header
        reference_list = ["REFERENCES", ""]

        # Format each citation
        for citation in sorted_citations:
            formatted = self.format_citation(citation)
            reference_list.append(formatted)

        # Join with newlines
        return "\n".join(reference_list)


class APACitationFormatter(CitationFormatter):
    """
    Formatter for APA citation style.

    APA style typically follows:
    Author(s). (Year). Title. Standard ID. URL
    Example: International Electrotechnical Commission. (2021). Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 1 (IEC 61215-1).
    """

    def format_citation(self, citation) -> str:
        """
        Format a single citation in APA style.

        Args:
            citation: Citation object to format

        Returns:
            Formatted citation string
        """
        parts = [f"[{citation.citation_id}]"]

        # Extract organization from standard ID
        if citation.standard_id:
            org = self._get_organization_name(citation.standard_id)
            if org:
                parts.append(org + ".")

        # Add year if available
        if citation.year:
            parts.append(f"({citation.year}).")

        # Add title if available
        if citation.title:
            parts.append(citation.title + ".")

        # Add standard ID in parentheses
        if citation.standard_id:
            parts.append(f"({citation.standard_id}).")

        # Add URL if available
        if citation.url:
            parts.append(citation.url)

        # Join parts with spaces
        formatted = " ".join(parts)

        return formatted

    def _get_organization_name(self, standard_id: str) -> Optional[str]:
        """Get full organization name from standard ID prefix."""
        org_map = {
            'IEC': 'International Electrotechnical Commission',
            'ISO': 'International Organization for Standardization',
            'IEEE': 'Institute of Electrical and Electronics Engineers',
            'ASTM': 'American Society for Testing and Materials',
            'EN': 'European Committee for Standardization',
            'UL': 'Underwriters Laboratories',
        }

        for prefix, name in org_map.items():
            if standard_id.startswith(prefix):
                return name

        return None

    def format_reference_list(self, citations: List) -> str:
        """
        Format a complete reference list in APA style.

        Args:
            citations: List of Citation objects

        Returns:
            Formatted reference list as string
        """
        if not citations:
            return ""

        # Sort citations by citation_id
        sorted_citations = sorted(citations, key=lambda c: c.citation_id)

        # Format header
        reference_list = ["References", ""]

        # Format each citation
        for citation in sorted_citations:
            formatted = self.format_citation(citation)
            reference_list.append(formatted)

        # Join with newlines
        return "\n".join(reference_list)


def get_formatter(style: str = 'iec') -> CitationFormatter:
    """
    Get a citation formatter for the specified style.

    Args:
        style: Citation style ('iec', 'ieee', 'apa')

    Returns:
        CitationFormatter instance

    Raises:
        ValueError: If style is not supported
    """
    formatters = {
        'iec': IECCitationFormatter,
        'ieee': IEEECitationFormatter,
        'apa': APACitationFormatter,
    }

    style_lower = style.lower()
    if style_lower not in formatters:
        raise ValueError(
            f"Unsupported citation style: {style}. "
            f"Supported styles: {', '.join(formatters.keys())}"
        )

    return formatters[style_lower]()
