"""
Citation Manager for formatting and validating source citations.
"""
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger

from app.models.schemas import Citation


class CitationManager:
    """
    Citation Manager for handling document citations and references.
    Supports multiple citation formats and deduplication.
    """

    CITATION_FORMATS = {
        "apa": "APA (American Psychological Association)",
        "mla": "MLA (Modern Language Association)",
        "chicago": "Chicago Manual of Style",
        "ieee": "IEEE"
    }

    def __init__(self):
        """Initialize citation manager."""
        logger.info("Citation Manager initialized")

    def format_citation(
        self,
        citation: Citation,
        format_style: str = "apa"
    ) -> str:
        """
        Format citation in specified style.

        Args:
            citation: Citation object
            format_style: Citation format (apa, mla, chicago, ieee)

        Returns:
            Formatted citation string
        """
        if format_style.lower() == "apa":
            return self._format_apa(citation)
        elif format_style.lower() == "mla":
            return self._format_mla(citation)
        elif format_style.lower() == "chicago":
            return self._format_chicago(citation)
        elif format_style.lower() == "ieee":
            return self._format_ieee(citation)
        else:
            return self._format_default(citation)

    def _format_apa(self, citation: Citation) -> str:
        """Format citation in APA style."""
        parts = [citation.source]
        if citation.page:
            parts.append(f"p. {citation.page}")
        return f"{', '.join(parts)}."

    def _format_mla(self, citation: Citation) -> str:
        """Format citation in MLA style."""
        parts = [citation.source]
        if citation.page:
            parts.append(str(citation.page))
        return f"{'. '.join(parts)}."

    def _format_chicago(self, citation: Citation) -> str:
        """Format citation in Chicago style."""
        parts = [citation.source]
        if citation.page:
            parts.append(str(citation.page))
        return f"{', '.join(parts)}."

    def _format_ieee(self, citation: Citation) -> str:
        """Format citation in IEEE style."""
        return f"[{citation.source}]"

    def _format_default(self, citation: Citation) -> str:
        """Format citation in default style."""
        return f"{citation.source} (relevance: {citation.relevance_score:.2f})"

    def deduplicate_citations(
        self,
        citations: List[Citation],
        threshold: float = 0.9
    ) -> List[Citation]:
        """
        Remove duplicate citations based on source and similarity.

        Args:
            citations: List of citations
            threshold: Similarity threshold for deduplication

        Returns:
            Deduplicated citations
        """
        if not citations:
            return []

        # Sort by relevance score (highest first)
        sorted_citations = sorted(
            citations,
            key=lambda x: x.relevance_score,
            reverse=True
        )

        # Deduplicate
        unique_citations = []
        seen_sources = set()

        for citation in sorted_citations:
            source_key = citation.source.lower()
            if source_key not in seen_sources:
                unique_citations.append(citation)
                seen_sources.add(source_key)

        logger.info(
            f"Deduplicated {len(citations)} citations to {len(unique_citations)} unique sources"
        )
        return unique_citations

    def rank_citations(
        self,
        citations: List[Citation],
        query: str = None
    ) -> List[Citation]:
        """
        Rank citations by relevance and quality.

        Args:
            citations: List of citations
            query: Original query for context

        Returns:
            Ranked citations
        """
        # Sort by relevance score
        ranked = sorted(
            citations,
            key=lambda x: x.relevance_score,
            reverse=True
        )

        logger.info(f"Ranked {len(ranked)} citations by relevance")
        return ranked

    def generate_bibliography(
        self,
        citations: List[Citation],
        format_style: str = "apa"
    ) -> str:
        """
        Generate formatted bibliography from citations.

        Args:
            citations: List of citations
            format_style: Citation format style

        Returns:
            Formatted bibliography text
        """
        if not citations:
            return "No sources cited."

        # Deduplicate and rank
        unique_citations = self.deduplicate_citations(citations)
        ranked_citations = self.rank_citations(unique_citations)

        # Format each citation
        bibliography_lines = ["# References\n"]
        for i, citation in enumerate(ranked_citations, 1):
            formatted = self.format_citation(citation, format_style)
            bibliography_lines.append(f"{i}. {formatted}")

        return "\n".join(bibliography_lines)

    def validate_citation(self, citation: Citation) -> bool:
        """
        Validate citation has required fields.

        Args:
            citation: Citation to validate

        Returns:
            True if valid
        """
        if not citation.source:
            logger.warning("Citation missing source")
            return False

        if not (0 <= citation.relevance_score <= 1):
            logger.warning(f"Invalid relevance score: {citation.relevance_score}")
            return False

        return True

    def get_citation_stats(self, citations: List[Citation]) -> Dict:
        """
        Get statistics about citations.

        Args:
            citations: List of citations

        Returns:
            Citation statistics
        """
        if not citations:
            return {
                "total_citations": 0,
                "unique_sources": 0,
                "average_relevance": 0.0
            }

        unique_sources = len(set(c.source for c in citations))
        avg_relevance = sum(c.relevance_score for c in citations) / len(citations)

        return {
            "total_citations": len(citations),
            "unique_sources": unique_sources,
            "average_relevance": round(avg_relevance, 3),
            "top_source": max(citations, key=lambda x: x.relevance_score).source
        }


# Global citation manager instance
citation_manager = CitationManager()
