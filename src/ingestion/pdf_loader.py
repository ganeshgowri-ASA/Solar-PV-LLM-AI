"""PDF loader for IEC standards that preserves document structure."""

import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pdfplumber
from PyPDF2 import PdfReader

from .models import ClauseInfo, DocumentMetadata

logger = logging.getLogger(__name__)


class IECPDFLoader:
    """Loader for IEC PDF documents that preserves clause/section structure."""

    def __init__(self, preserve_layout: bool = True, extract_tables: bool = True):
        """Initialize the PDF loader.

        Args:
            preserve_layout: Whether to preserve text layout during extraction
            extract_tables: Whether to extract tables from PDF
        """
        self.preserve_layout = preserve_layout
        self.extract_tables = extract_tables
        self.clause_patterns = [
            re.compile(r"^(\d+(?:\.\d+)*)\s+([A-Z][^\n]{0,200})$", re.MULTILINE),
            re.compile(r"^Clause\s+(\d+(?:\.\d+)*):?\s+([A-Z][^\n]{0,200})$", re.MULTILINE),
            re.compile(r"^(\d+(?:\.\d+)*)\s*\n+([A-Z][^\n]{0,200})$", re.MULTILINE),
        ]

    def load(self, pdf_path: str) -> Tuple[str, List[ClauseInfo], DocumentMetadata]:
        """Load PDF and extract text, clause structure, and metadata.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Tuple of (full_text, clauses, metadata)
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Loading PDF: {pdf_path}")

        # Extract metadata
        metadata = self._extract_basic_metadata(pdf_path)

        # Extract text with structure
        full_text, page_texts = self._extract_text_with_structure(pdf_path)

        # Extract clauses
        clauses = self._extract_clauses(full_text, page_texts)

        logger.info(
            f"Loaded PDF: {len(page_texts)} pages, "
            f"{len(full_text)} chars, {len(clauses)} clauses"
        )

        return full_text, clauses, metadata

    def _extract_basic_metadata(self, pdf_path: Path) -> DocumentMetadata:
        """Extract basic metadata from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            DocumentMetadata object
        """
        try:
            reader = PdfReader(str(pdf_path))
            info = reader.metadata if reader.metadata else {}

            return DocumentMetadata(
                title=info.get("/Title", None),
                total_pages=len(reader.pages),
                file_path=str(pdf_path),
                file_size_bytes=pdf_path.stat().st_size,
            )
        except Exception as e:
            logger.warning(f"Error extracting basic metadata: {e}")
            return DocumentMetadata(
                file_path=str(pdf_path),
                file_size_bytes=pdf_path.stat().st_size if pdf_path.exists() else None,
            )

    def _extract_text_with_structure(self, pdf_path: Path) -> Tuple[str, Dict[int, str]]:
        """Extract text from PDF while preserving structure.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (full_text, page_texts_dict)
        """
        page_texts = {}
        all_text = []

        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text with layout preservation
                    text = page.extract_text(layout=self.preserve_layout)

                    if text:
                        # Clean up text
                        text = self._clean_text(text)
                        page_texts[page_num] = text
                        all_text.append(text)

                        # Extract tables if enabled
                        if self.extract_tables:
                            tables = page.extract_tables()
                            if tables:
                                for table in tables:
                                    table_text = self._format_table(table)
                                    page_texts[page_num] += f"\n\n{table_text}"
                                    all_text.append(table_text)

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

        full_text = "\n\n".join(all_text)
        return full_text, page_texts

    def _clean_text(self, text: str) -> str:
        """Clean extracted text.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        # Remove page numbers (common patterns)
        text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^–\s*\d+\s*–\s*$", "", text, flags=re.MULTILINE)

        # Remove headers/footers (IEC specific)
        text = re.sub(r"^IEC\s+\d+(?:-\d+)*:\d{4}.*$", "", text, flags=re.MULTILINE)

        return text.strip()

    def _format_table(self, table: List[List[str]]) -> str:
        """Format extracted table as text.

        Args:
            table: Table data as list of rows

        Returns:
            Formatted table text
        """
        if not table:
            return ""

        # Simple table formatting
        formatted_rows = []
        for row in table:
            if row and any(cell for cell in row if cell):
                row_text = " | ".join(str(cell or "") for cell in row)
                formatted_rows.append(row_text)

        return "\n".join(formatted_rows)

    def _extract_clauses(
        self, full_text: str, page_texts: Dict[int, str]
    ) -> List[ClauseInfo]:
        """Extract clause/section information from text.

        Args:
            full_text: Full document text
            page_texts: Dictionary of page number to text

        Returns:
            List of ClauseInfo objects
        """
        clauses = []
        seen_clauses = set()

        # Try each pattern
        for pattern in self.clause_patterns:
            matches = pattern.finditer(full_text)

            for match in matches:
                clause_num = match.group(1)
                clause_title = match.group(2).strip() if len(match.groups()) > 1 else None

                # Skip if already seen
                if clause_num in seen_clauses:
                    continue

                seen_clauses.add(clause_num)

                # Determine nesting level
                level = clause_num.count(".") + 1

                # Determine parent clause
                parent_clause = None
                if "." in clause_num:
                    parent_clause = ".".join(clause_num.split(".")[:-1])

                # Find page number
                page_num = self._find_page_for_position(match.start(), page_texts)

                clause_info = ClauseInfo(
                    clause_number=clause_num,
                    title=clause_title,
                    level=level,
                    parent_clause=parent_clause,
                    page_start=page_num,
                )

                clauses.append(clause_info)

        # Sort clauses by clause number
        clauses.sort(key=lambda c: self._clause_sort_key(c.clause_number))

        logger.info(f"Extracted {len(clauses)} clauses")
        return clauses

    def _find_page_for_position(self, position: int, page_texts: Dict[int, str]) -> Optional[int]:
        """Find which page a text position corresponds to.

        Args:
            position: Character position in full text
            page_texts: Dictionary of page texts

        Returns:
            Page number or None
        """
        current_pos = 0
        for page_num in sorted(page_texts.keys()):
            page_text = page_texts[page_num]
            if current_pos <= position < current_pos + len(page_text):
                return page_num
            current_pos += len(page_text) + 2  # Account for \n\n separator

        return None

    def _clause_sort_key(self, clause_num: str) -> Tuple[int, ...]:
        """Generate sort key for clause number.

        Args:
            clause_num: Clause number string (e.g., '4.2.1')

        Returns:
            Tuple of integers for sorting
        """
        try:
            return tuple(int(part) for part in clause_num.split("."))
        except ValueError:
            return (0,)

    def extract_clause_text(
        self, full_text: str, clause_info: ClauseInfo, next_clause: Optional[ClauseInfo] = None
    ) -> str:
        """Extract text content for a specific clause.

        Args:
            full_text: Full document text
            clause_info: Current clause information
            next_clause: Next clause information (to determine boundary)

        Returns:
            Text content of the clause
        """
        # Find clause start
        clause_pattern = re.escape(clause_info.clause_number)
        if clause_info.title:
            title_pattern = re.escape(clause_info.title[:50])  # Match first 50 chars
            pattern = rf"{clause_pattern}\s+{title_pattern}"
        else:
            pattern = rf"^{clause_pattern}\s+"

        match = re.search(pattern, full_text, re.MULTILINE)
        if not match:
            logger.warning(f"Could not find start of clause {clause_info.clause_number}")
            return ""

        start_pos = match.end()

        # Find clause end (start of next clause or end of document)
        end_pos = len(full_text)
        if next_clause:
            next_pattern = re.escape(next_clause.clause_number)
            if next_clause.title:
                next_title_pattern = re.escape(next_clause.title[:50])
                next_search = rf"{next_pattern}\s+{next_title_pattern}"
            else:
                next_search = rf"^{next_pattern}\s+"

            next_match = re.search(next_search, full_text[start_pos:], re.MULTILINE)
            if next_match:
                end_pos = start_pos + next_match.start()

        clause_text = full_text[start_pos:end_pos].strip()
        return clause_text
