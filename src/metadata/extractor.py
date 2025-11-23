"""
IEC Metadata Extractor - Extract metadata from IEC standard PDFs.
"""

import re
from typing import Optional, Dict, Any, List
from .schema import IECMetadata, ClauseMetadata


class IECMetadataExtractor:
    """Extract metadata from IEC standard documents."""

    # Common IEC standard patterns
    STANDARD_ID_PATTERNS = [
        r'IEC\s+(\d{5}(?:-\d+)?(?:-\d+)?)',  # IEC 61215-1-3
        r'IEC/TS\s+(\d{5}(?:-\d+)?)',  # IEC/TS 62804-1
        r'IEC/TR\s+(\d{5}(?:-\d+)?)',  # IEC/TR reports
    ]

    EDITION_PATTERNS = [
        r'Edition\s+(\d+\.?\d*)',
        r'(\d+\.?\d*)\s+edition',
        r'(?:First|Second|Third|Fourth|Fifth)\s+edition',
    ]

    YEAR_PATTERNS = [
        r'©?\s*IEC[:\s]+(\d{4})',
        r'Publication\s+year[:\s]+(\d{4})',
        r'\b(20\d{2})\b',  # Years 2000-2099
    ]

    CLAUSE_PATTERNS = [
        r'^(\d+(?:\.\d+)*)\s+(.+)$',  # 5.2.3 Title
        r'^([A-Z])\s+\((?:normative|informative)\)\s+(.+)$',  # Annex A (normative) Title
    ]

    def __init__(self):
        self.standard_id_regex = [re.compile(p, re.IGNORECASE) for p in self.STANDARD_ID_PATTERNS]
        self.edition_regex = [re.compile(p, re.IGNORECASE) for p in self.EDITION_PATTERNS]
        self.year_regex = [re.compile(p) for p in self.YEAR_PATTERNS]
        self.clause_regex = [re.compile(p, re.MULTILINE) for p in self.CLAUSE_PATTERNS]

    def extract_standard_id(self, text: str) -> Optional[str]:
        """
        Extract IEC standard identifier from text.

        Args:
            text: Text to search for standard ID

        Returns:
            Standard ID string or None
        """
        # Search first 2000 characters (usually in header/title page)
        search_text = text[:2000]

        for regex in self.standard_id_regex:
            match = regex.search(search_text)
            if match:
                std_id = match.group(0).strip()
                # Normalize spacing
                std_id = re.sub(r'\s+', ' ', std_id)
                return std_id

        return None

    def extract_edition(self, text: str) -> Optional[str]:
        """
        Extract edition information from text.

        Args:
            text: Text to search for edition

        Returns:
            Edition string or None
        """
        search_text = text[:3000]

        for regex in self.edition_regex:
            match = regex.search(search_text)
            if match:
                edition = match.group(1) if match.lastindex else match.group(0)
                # Convert word editions to numbers
                word_to_num = {
                    'first': '1.0',
                    'second': '2.0',
                    'third': '3.0',
                    'fourth': '4.0',
                    'fifth': '5.0'
                }
                edition_lower = edition.lower()
                for word, num in word_to_num.items():
                    if word in edition_lower:
                        return num
                return edition.strip()

        return None

    def extract_year(self, text: str) -> Optional[int]:
        """
        Extract publication year from text.

        Args:
            text: Text to search for year

        Returns:
            Year as integer or None
        """
        search_text = text[:3000]
        years_found = []

        for regex in self.year_regex:
            matches = regex.finditer(search_text)
            for match in matches:
                try:
                    year = int(match.group(1))
                    if 2000 <= year <= 2030:  # Reasonable range for IEC standards
                        years_found.append(year)
                except (ValueError, IndexError):
                    continue

        # Return most recent year found
        return max(years_found) if years_found else None

    def extract_title(self, text: str, standard_id: Optional[str] = None) -> str:
        """
        Extract document title from text.

        Args:
            text: Text to search for title
            standard_id: Standard ID to help locate title

        Returns:
            Title string
        """
        search_text = text[:3000]
        lines = search_text.split('\n')

        # Look for title after standard ID
        if standard_id:
            for i, line in enumerate(lines):
                if standard_id in line and i + 1 < len(lines):
                    # Title often on next few lines
                    potential_title = []
                    for j in range(i + 1, min(i + 5, len(lines))):
                        title_line = lines[j].strip()
                        if title_line and len(title_line) > 10:
                            # Skip lines with just metadata
                            if not re.match(r'^(Edition|IEC|©|\d{4})', title_line):
                                potential_title.append(title_line)
                            if len(potential_title) >= 2:
                                break
                    if potential_title:
                        return ' '.join(potential_title)

        # Fallback: look for longest line in first section
        title_candidates = [line.strip() for line in lines if len(line.strip()) > 20]
        if title_candidates:
            return max(title_candidates, key=len)

        return "Untitled IEC Standard"

    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from document text.

        Args:
            text: Document text

        Returns:
            List of keywords
        """
        # Common keywords for solar PV standards
        pv_keywords = [
            'photovoltaic', 'PV', 'solar', 'module', 'panel', 'cell',
            'crystalline', 'silicon', 'thin-film', 'performance', 'testing',
            'qualification', 'design', 'safety', 'reliability', 'efficiency',
            'power', 'voltage', 'current', 'irradiance', 'temperature'
        ]

        keywords_found = []
        text_lower = text.lower()

        for keyword in pv_keywords:
            if keyword.lower() in text_lower:
                keywords_found.append(keyword)

        return keywords_found[:10]  # Limit to top 10

    def extract_document_metadata(self, text: str) -> IECMetadata:
        """
        Extract complete document metadata from text.

        Args:
            text: Full document text

        Returns:
            IECMetadata object
        """
        standard_id = self.extract_standard_id(text)
        if not standard_id:
            standard_id = "IEC-UNKNOWN"

        edition = self.extract_edition(text)
        year = self.extract_year(text)
        title = self.extract_title(text, standard_id)
        keywords = self.extract_keywords(text)

        return IECMetadata(
            standard_id=standard_id,
            edition=edition,
            year=year,
            title=title,
            keywords=keywords
        )

    def parse_clause_number(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse clause/section number and title from text line.

        Args:
            text: Text line potentially containing clause info

        Returns:
            Dictionary with clause info or None
        """
        text = text.strip()

        # Try numeric clauses (e.g., "5.2.3 Title")
        for regex in self.clause_regex:
            match = regex.match(text)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    clause_num = groups[0]
                    clause_title = groups[1].strip()

                    # Determine level from clause number
                    if '.' in clause_num:
                        level = len(clause_num.split('.'))
                        parent = '.'.join(clause_num.split('.')[:-1])
                    else:
                        level = 1
                        parent = None

                    # Determine if annex
                    section_type = 'annex' if clause_num.isalpha() else 'clause'

                    return {
                        'clause_number': clause_num,
                        'clause_title': clause_title,
                        'parent_clause': parent,
                        'level': level,
                        'section_type': section_type
                    }

        return None

    def extract_clause_metadata(self, clause_text: str, clause_number: str = None) -> ClauseMetadata:
        """
        Extract clause metadata from clause text.

        Args:
            clause_text: Text of the clause
            clause_number: Optional clause number if known

        Returns:
            ClauseMetadata object
        """
        # Try to parse from first line if clause_number not provided
        if not clause_number:
            first_line = clause_text.split('\n')[0]
            parsed = self.parse_clause_number(first_line)
            if parsed:
                return ClauseMetadata(**parsed)

        # Default fallback
        return ClauseMetadata(
            clause_number=clause_number or "0",
            clause_title="Unknown Section",
            parent_clause=None,
            level=1,
            section_type="clause"
        )

    def extract_scope(self, text: str) -> Optional[str]:
        """
        Extract the scope section from document.

        Args:
            text: Full document text

        Returns:
            Scope text or None
        """
        # Look for "Scope" section (usually clause 1)
        scope_pattern = r'(?:^|\n)1\s+Scope\s*\n(.*?)(?=\n\d+\s+[A-Z]|\n[A-Z]\s+\(|$)'
        match = re.search(scope_pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            scope_text = match.group(1).strip()
            # Clean up and limit length
            scope_text = re.sub(r'\s+', ' ', scope_text)
            return scope_text[:500]

        return None
