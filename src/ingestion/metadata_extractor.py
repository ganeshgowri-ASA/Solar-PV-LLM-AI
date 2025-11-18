"""Metadata extractor for IEC standard documents."""

import re
import logging
from typing import Optional, Dict, List
from pathlib import Path

from .models import DocumentMetadata

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extracts metadata from IEC standard documents."""

    # Regex patterns for IEC standards
    STANDARD_PATTERNS = [
        re.compile(r"IEC\s+(TR\s+)?(\d+(?:-\d+)*)", re.IGNORECASE),
        re.compile(r"IEC\s+(TS\s+)?(\d+(?:-\d+)*)", re.IGNORECASE),
        re.compile(r"International\s+Electrotechnical\s+Commission.*?(\d+(?:-\d+)*)", re.IGNORECASE),
    ]

    EDITION_PATTERNS = [
        re.compile(r"Edition\s+(\d+\.?\d*)", re.IGNORECASE),
        re.compile(r"(\d+)(?:st|nd|rd|th)\s+edition", re.IGNORECASE),
        re.compile(r"Ed(?:ition)?\.?\s+(\d+\.?\d*)", re.IGNORECASE),
    ]

    YEAR_PATTERNS = [
        re.compile(r"(\d{4})-(\d{2})"),  # 2020-05
        re.compile(r"(?:Copyright|©)\s*(?:IEC\s*)?(\d{4})"),
        re.compile(r"\b(20\d{2})\b"),  # Any year 2000-2099
    ]

    TITLE_PATTERNS = [
        re.compile(r"IEC\s+\d+(?:-\d+)*:\d{4}[^\n]*\n+([A-Z][^\n]{10,200})", re.MULTILINE),
        re.compile(r"^([A-Z][A-Z\s\-–—]{20,200})$", re.MULTILINE),
    ]

    def __init__(self, config: Optional[Dict] = None):
        """Initialize metadata extractor.

        Args:
            config: Optional configuration dictionary with custom patterns
        """
        self.config = config or {}

        # Allow custom patterns from config
        if "standard_patterns" in self.config:
            self.STANDARD_PATTERNS.extend(
                [re.compile(p) for p in self.config["standard_patterns"]]
            )
        if "edition_patterns" in self.config:
            self.EDITION_PATTERNS.extend(
                [re.compile(p) for p in self.config["edition_patterns"]]
            )
        if "year_patterns" in self.config:
            self.YEAR_PATTERNS.extend([re.compile(p) for p in self.config["year_patterns"]])

    def extract(
        self, text: str, existing_metadata: Optional[DocumentMetadata] = None
    ) -> DocumentMetadata:
        """Extract metadata from document text.

        Args:
            text: Full document text
            existing_metadata: Optional existing metadata to enhance

        Returns:
            DocumentMetadata object with extracted information
        """
        if existing_metadata:
            metadata = existing_metadata.copy()
        else:
            metadata = DocumentMetadata()

        # Focus on first few pages for metadata extraction
        header_text = text[:5000]

        # Extract standard ID
        if not metadata.standard_id:
            standard_id, standard_type = self._extract_standard_id(header_text)
            metadata.standard_id = standard_id
            metadata.standard_type = standard_type

        # Extract edition
        if not metadata.edition:
            metadata.edition = self._extract_edition(header_text)

        # Extract year
        if not metadata.year:
            metadata.year = self._extract_year(header_text)

        # Extract title
        if not metadata.title:
            metadata.title = self._extract_title(header_text)

        logger.info(f"Extracted metadata: {metadata.standard_id}, Edition {metadata.edition}, {metadata.year}")

        return metadata

    def _extract_standard_id(self, text: str) -> tuple[Optional[str], Optional[str]]:
        """Extract IEC standard ID from text.

        Args:
            text: Text to search

        Returns:
            Tuple of (standard_id, standard_type)
        """
        for pattern in self.STANDARD_PATTERNS:
            match = pattern.search(text)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    standard_type = groups[0].strip() if groups[0] else "IEC"
                    standard_id = groups[1].strip()
                else:
                    standard_type = "IEC"
                    standard_id = groups[0].strip() if groups else match.group(0)

                # Format standard ID
                if not standard_id.startswith("IEC"):
                    standard_id = f"IEC {standard_id}"

                return standard_id, standard_type

        logger.warning("Could not extract standard ID")
        return None, None

    def _extract_edition(self, text: str) -> Optional[str]:
        """Extract edition number from text.

        Args:
            text: Text to search

        Returns:
            Edition string or None
        """
        for pattern in self.EDITION_PATTERNS:
            match = pattern.search(text)
            if match:
                edition = match.group(1)
                logger.debug(f"Found edition: {edition}")
                return edition

        logger.warning("Could not extract edition")
        return None

    def _extract_year(self, text: str) -> Optional[int]:
        """Extract publication year from text.

        Args:
            text: Text to search

        Returns:
            Year as integer or None
        """
        years_found = []

        for pattern in self.YEAR_PATTERNS:
            matches = pattern.finditer(text)
            for match in matches:
                try:
                    # Get first capturing group (the year)
                    year_str = match.group(1)
                    year = int(year_str)

                    # Validate year range
                    if 2000 <= year <= 2030:
                        years_found.append(year)
                except (ValueError, IndexError):
                    continue

        if years_found:
            # Return the most recent year found
            year = max(years_found)
            logger.debug(f"Found year: {year}")
            return year

        logger.warning("Could not extract year")
        return None

    def _extract_title(self, text: str) -> Optional[str]:
        """Extract document title from text.

        Args:
            text: Text to search

        Returns:
            Title string or None
        """
        for pattern in self.TITLE_PATTERNS:
            match = pattern.search(text)
            if match:
                title = match.group(1).strip()

                # Clean up title
                title = re.sub(r"\s{2,}", " ", title)
                title = title.replace("\n", " ")

                # Validate title (should be reasonable length and content)
                if 10 <= len(title) <= 200 and not title.isupper():
                    logger.debug(f"Found title: {title[:50]}...")
                    return title

        # Try to find title from filename if available
        logger.warning("Could not extract title from text")
        return None

    def extract_from_filename(self, filename: str) -> DocumentMetadata:
        """Extract metadata from PDF filename.

        Args:
            filename: PDF filename

        Returns:
            DocumentMetadata with info extracted from filename
        """
        metadata = DocumentMetadata()
        filename = Path(filename).stem  # Remove extension

        # Try to extract standard ID from filename
        standard_match = re.search(r"IEC[_\s-]*(\d+(?:-\d+)*)", filename, re.IGNORECASE)
        if standard_match:
            metadata.standard_id = f"IEC {standard_match.group(1)}"

        # Try to extract year from filename
        year_match = re.search(r"(20\d{2})", filename)
        if year_match:
            metadata.year = int(year_match.group(1))

        # Try to extract edition from filename
        edition_match = re.search(r"ed(?:ition)?[_\s-]*(\d+)", filename, re.IGNORECASE)
        if edition_match:
            metadata.edition = edition_match.group(1)

        return metadata

    def validate_metadata(self, metadata: DocumentMetadata) -> tuple[bool, List[str]]:
        """Validate extracted metadata completeness.

        Args:
            metadata: DocumentMetadata to validate

        Returns:
            Tuple of (is_valid, list of missing/invalid fields)
        """
        issues = []

        if not metadata.standard_id:
            issues.append("Missing standard_id")

        if not metadata.edition:
            issues.append("Missing edition")

        if not metadata.year:
            issues.append("Missing year")
        elif metadata.year < 1950 or metadata.year > 2030:
            issues.append(f"Invalid year: {metadata.year}")

        if not metadata.title:
            issues.append("Missing title")

        is_valid = len(issues) == 0

        if not is_valid:
            logger.warning(f"Metadata validation issues: {', '.join(issues)}")

        return is_valid, issues
