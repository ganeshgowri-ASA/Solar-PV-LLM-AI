"""
Citation Extractor - Extract citation metadata from documents.

This module extracts standard IDs, clause references, and other metadata
from retrieved documents for citation purposes.
"""

import re
from typing import Dict, Any, Optional, List


class CitationExtractor:
    """Extracts citation metadata from documents and their content."""

    # Regular expressions for extracting citation information
    STANDARD_ID_PATTERNS = [
        # IEC standards (e.g., IEC 61215, IEC 61730-1)
        r'IEC\s*(\d{5}(?:-\d+)?(?:-\d+)?)',
        # ISO standards (e.g., ISO 9001, ISO/IEC 17025)
        r'ISO(?:/IEC)?\s*(\d{4,5}(?:-\d+)?)',
        # IEEE standards (e.g., IEEE 1547, IEEE 802.11)
        r'IEEE\s*(\d{3,4}(?:\.\d+)?)',
        # ASTM standards (e.g., ASTM E1036)
        r'ASTM\s*([A-Z]\d{4})',
        # EN standards (e.g., EN 50530)
        r'EN\s*(\d{5})',
        # UL standards (e.g., UL 1741)
        r'UL\s*(\d{4})',
    ]

    CLAUSE_PATTERNS = [
        # Clause/Section references (e.g., Clause 5.2.1, Section 4.3)
        r'(?:Clause|Section|§)\s*(\d+(?:\.\d+)*)',
        # Subsection references (e.g., 5.2.1, 4.3.2.1)
        r'\b(\d+\.\d+(?:\.\d+)*)\b',
        # Annex references (e.g., Annex A, Appendix B)
        r'(?:Annex|Appendix)\s*([A-Z](?:\.\d+)*)',
    ]

    PAGE_PATTERNS = [
        # Page references (e.g., p. 42, pp. 10-15, page 23)
        r'(?:p\.|pp\.|page|pages)\s*(\d+(?:-\d+)?)',
    ]

    def extract_metadata(
        self,
        metadata: Dict[str, Any],
        content: str
    ) -> Dict[str, Optional[str]]:
        """
        Extract citation metadata from document metadata and content.

        Args:
            metadata: Document metadata dictionary
            content: Document text content

        Returns:
            Dictionary with extracted citation metadata
        """
        extracted = {
            'standard_id': None,
            'clause_ref': None,
            'title': None,
            'year': None,
            'url': None,
            'page': None,
            'authors': None,
            'publisher': None,
        }

        # Extract from explicit metadata first
        extracted['title'] = metadata.get('title') or metadata.get('source')
        extracted['year'] = metadata.get('year') or metadata.get('date')
        extracted['url'] = metadata.get('url') or metadata.get('source_url')
        extracted['page'] = metadata.get('page')
        extracted['authors'] = metadata.get('authors') or metadata.get('author')
        extracted['publisher'] = metadata.get('publisher')

        # Extract standard ID from metadata or content
        standard_id = metadata.get('standard_id') or metadata.get('standard')
        if not standard_id:
            standard_id = self.extract_standard_id(content)
        extracted['standard_id'] = standard_id

        # Extract clause reference from metadata or content
        clause_ref = metadata.get('clause') or metadata.get('section')
        if not clause_ref:
            clause_ref = self.extract_clause_reference(content)
        extracted['clause_ref'] = clause_ref

        # Extract year from content if not in metadata
        if not extracted['year']:
            extracted['year'] = self.extract_year(content)

        # Extract page reference from content if not in metadata
        if not extracted['page']:
            extracted['page'] = self.extract_page_reference(content)

        return extracted

    def extract_standard_id(self, text: str) -> Optional[str]:
        """
        Extract standard ID from text using pattern matching.

        Args:
            text: Text to search for standard IDs

        Returns:
            First matched standard ID or None
        """
        for pattern in self.STANDARD_ID_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Reconstruct full standard ID
                prefix = re.match(r'([A-Z]+(?:/[A-Z]+)?)', pattern.replace('\\s*', ' ')).group(1)
                return f"{prefix} {match.group(1)}"

        return None

    def extract_all_standard_ids(self, text: str) -> List[str]:
        """
        Extract all standard IDs from text.

        Args:
            text: Text to search for standard IDs

        Returns:
            List of all matched standard IDs
        """
        standard_ids = []
        for pattern in self.STANDARD_ID_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract prefix from pattern
                prefix_match = re.search(r'([A-Z]+(?:/[A-Z]+)?)', text[match.start():match.end()])
                if prefix_match:
                    standard_id = f"{prefix_match.group(1)} {match.group(1)}"
                    if standard_id not in standard_ids:
                        standard_ids.append(standard_id)

        return standard_ids

    def extract_clause_reference(self, text: str) -> Optional[str]:
        """
        Extract clause/section reference from text.

        Args:
            text: Text to search for clause references

        Returns:
            First matched clause reference or None
        """
        # Look in first 500 characters for clause references
        search_text = text[:500]

        for pattern in self.CLAUSE_PATTERNS:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                # Return the full match including the keyword if present
                full_match = match.group(0)
                return full_match

        return None

    def extract_all_clause_references(self, text: str) -> List[str]:
        """
        Extract all clause/section references from text.

        Args:
            text: Text to search for clause references

        Returns:
            List of all matched clause references
        """
        clause_refs = []
        for pattern in self.CLAUSE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ref = match.group(0)
                if ref not in clause_refs:
                    clause_refs.append(ref)

        return clause_refs

    def extract_year(self, text: str) -> Optional[str]:
        """
        Extract publication year from text.

        Args:
            text: Text to search for year

        Returns:
            Matched year or None
        """
        # Look for 4-digit years between 1980 and 2030 in first 300 chars
        search_text = text[:300]
        year_pattern = r'\b(19[89]\d|20[0-2]\d|2030)\b'
        match = re.search(year_pattern, search_text)

        if match:
            return match.group(1)

        return None

    def extract_page_reference(self, text: str) -> Optional[str]:
        """
        Extract page reference from text.

        Args:
            text: Text to search for page reference

        Returns:
            Matched page reference or None
        """
        # Look in first 200 characters
        search_text = text[:200]

        for pattern in self.PAGE_PATTERNS:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def extract_citation_context(
        self,
        text: str,
        standard_id: str,
        window: int = 100
    ) -> Optional[str]:
        """
        Extract text context around a standard ID mention.

        Args:
            text: Text to search
            standard_id: Standard ID to find
            window: Characters before and after to include

        Returns:
            Context string or None
        """
        # Escape special regex characters in standard_id
        escaped_id = re.escape(standard_id)
        match = re.search(escaped_id, text, re.IGNORECASE)

        if match:
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            context = text[start:end]

            # Clean up context
            context = ' '.join(context.split())
            return f"...{context}..."

        return None
