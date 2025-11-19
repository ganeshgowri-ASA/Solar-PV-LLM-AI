"""
IEC PDF Loader - Load and parse IEC standard PDFs with structure preservation.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import pdfplumber
from PyPDF2 import PdfReader
import logging

logger = logging.getLogger(__name__)


@dataclass
class StructuredSection:
    """Represents a structured section from IEC PDF."""

    clause_number: str
    clause_title: str
    content: str
    page_numbers: List[int]
    level: int
    parent_clause: Optional[str] = None
    section_type: str = "clause"  # clause, annex, figure, table, note

    def __str__(self):
        return f"{self.clause_number} {self.clause_title}"


class IECPDFLoader:
    """
    Load and parse IEC standard PDFs while preserving structural information.
    """

    # Patterns for identifying clauses and sections
    CLAUSE_HEADER_PATTERNS = [
        r'^(\d+(?:\.\d+)*)\s+(.+)$',  # Numeric: 5.2.3 Title
        r'^([A-Z])\s+\((?:normative|informative)\)\s*(.*)$',  # Annex: A (normative) Title
        r'^(Annex\s+[A-Z])\s+\((?:normative|informative)\)\s*(.*)$',  # Annex A (normative) Title
    ]

    # Patterns for special sections
    FIGURE_PATTERN = r'Figure\s+(\d+(?:\.\d+)?)\s*[–—-]\s*(.+)'
    TABLE_PATTERN = r'Table\s+(\d+(?:\.\d+)?)\s*[–—-]\s*(.+)'
    NOTE_PATTERN = r'NOTE\s+(\d+)?\s*(.+)'

    def __init__(self, preserve_formatting: bool = True):
        """
        Initialize PDF loader.

        Args:
            preserve_formatting: Whether to preserve text formatting
        """
        self.preserve_formatting = preserve_formatting
        self.clause_regex = [re.compile(p, re.MULTILINE) for p in self.CLAUSE_HEADER_PATTERNS]
        self.figure_regex = re.compile(self.FIGURE_PATTERN, re.IGNORECASE)
        self.table_regex = re.compile(self.TABLE_PATTERN, re.IGNORECASE)
        self.note_regex = re.compile(self.NOTE_PATTERN)

    def load_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Load PDF and extract text with metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with text, page_count, and metadata
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Loading PDF: {pdf_path}")

        # Extract text and metadata
        pages_text = []
        metadata = {}

        try:
            # Use pdfplumber for better text extraction
            with pdfplumber.open(pdf_path) as pdf:
                metadata = {
                    'page_count': len(pdf.pages),
                    'filename': pdf_path.name
                }

                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    if text:
                        pages_text.append({
                            'page_number': page_num,
                            'text': text
                        })

            # Also get PDF metadata
            try:
                reader = PdfReader(str(pdf_path))
                if reader.metadata:
                    metadata.update({
                        'pdf_title': reader.metadata.get('/Title', ''),
                        'pdf_author': reader.metadata.get('/Author', ''),
                        'pdf_subject': reader.metadata.get('/Subject', ''),
                        'pdf_creator': reader.metadata.get('/Creator', ''),
                    })
            except Exception as e:
                logger.warning(f"Could not extract PDF metadata: {e}")

        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise

        # Combine all text
        full_text = '\n'.join([p['text'] for p in pages_text])

        return {
            'text': full_text,
            'pages': pages_text,
            'metadata': metadata
        }

    def identify_clause_headers(self, text: str) -> List[Dict[str, Any]]:
        """
        Identify clause headers in text.

        Args:
            text: Text to analyze

        Returns:
            List of clause header information
        """
        headers = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Check for numeric clause headers
            for regex in self.clause_regex:
                match = regex.match(line)
                if match:
                    groups = match.groups()
                    if len(groups) >= 2:
                        clause_num = groups[0]
                        clause_title = groups[1].strip() if groups[1] else ""

                        # Calculate level
                        if '.' in clause_num and clause_num[0].isdigit():
                            level = len(clause_num.split('.'))
                            parent = '.'.join(clause_num.split('.')[:-1])
                        elif clause_num.isalpha():
                            level = 1
                            parent = None
                        else:
                            level = 1
                            parent = None

                        # Determine section type
                        if 'annex' in line.lower() or clause_num.isalpha():
                            section_type = 'annex'
                        else:
                            section_type = 'clause'

                        headers.append({
                            'line_number': line_num,
                            'clause_number': clause_num,
                            'clause_title': clause_title,
                            'level': level,
                            'parent_clause': parent,
                            'section_type': section_type,
                            'raw_line': line
                        })
                        break

        return headers

    def extract_structured_sections(self, pdf_data: Dict[str, Any]) -> List[StructuredSection]:
        """
        Extract structured sections from PDF data.

        Args:
            pdf_data: PDF data from load_pdf()

        Returns:
            List of StructuredSection objects
        """
        full_text = pdf_data['text']
        pages = pdf_data['pages']

        # Identify all clause headers
        headers = self.identify_clause_headers(full_text)

        if not headers:
            logger.warning("No clause headers found, returning full text as single section")
            return [
                StructuredSection(
                    clause_number="0",
                    clause_title="Full Document",
                    content=full_text,
                    page_numbers=list(range(1, len(pages) + 1)),
                    level=0,
                    section_type="document"
                )
            ]

        sections = []
        lines = full_text.split('\n')

        # Extract content for each section
        for i, header in enumerate(headers):
            start_line = header['line_number']
            end_line = headers[i + 1]['line_number'] if i + 1 < len(headers) else len(lines)

            # Get section content
            section_lines = lines[start_line:end_line]
            content = '\n'.join(section_lines).strip()

            # Determine page numbers (approximate)
            page_numbers = self._estimate_page_numbers(
                start_line, end_line, len(lines), len(pages)
            )

            section = StructuredSection(
                clause_number=header['clause_number'],
                clause_title=header['clause_title'],
                content=content,
                page_numbers=page_numbers,
                level=header['level'],
                parent_clause=header.get('parent_clause'),
                section_type=header['section_type']
            )

            sections.append(section)

        logger.info(f"Extracted {len(sections)} structured sections")
        return sections

    def _estimate_page_numbers(
        self, start_line: int, end_line: int, total_lines: int, total_pages: int
    ) -> List[int]:
        """
        Estimate page numbers for a section based on line numbers.

        Args:
            start_line: Starting line number
            end_line: Ending line number
            total_lines: Total lines in document
            total_pages: Total pages in document

        Returns:
            List of page numbers
        """
        if total_lines == 0:
            return [1]

        # Estimate lines per page
        lines_per_page = total_lines / total_pages

        # Calculate page range
        start_page = max(1, int(start_line / lines_per_page) + 1)
        end_page = min(total_pages, int(end_line / lines_per_page) + 1)

        return list(range(start_page, end_page + 1))

    def load_and_structure(self, pdf_path: str) -> Tuple[Dict[str, Any], List[StructuredSection]]:
        """
        Load PDF and extract structured sections in one call.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (pdf_data, sections)
        """
        pdf_data = self.load_pdf(pdf_path)
        sections = self.extract_structured_sections(pdf_data)
        return pdf_data, sections

    def get_section_hierarchy(self, sections: List[StructuredSection]) -> Dict[str, Any]:
        """
        Build hierarchical structure of sections.

        Args:
            sections: List of sections

        Returns:
            Nested dictionary representing hierarchy
        """
        hierarchy = {}

        for section in sections:
            clause_num = section.clause_number
            parts = clause_num.split('.')

            # Navigate to correct position in hierarchy
            current = hierarchy
            for i, part in enumerate(parts):
                key = '.'.join(parts[:i + 1])
                if key not in current:
                    current[key] = {
                        'section': section,
                        'children': {}
                    }
                current = current[key]['children']

        return hierarchy

    def extract_references(self, text: str) -> List[str]:
        """
        Extract cross-references to other clauses.

        Args:
            text: Text to analyze

        Returns:
            List of referenced clause numbers
        """
        # Pattern for clause references
        ref_patterns = [
            r'(?:see|See|according to|as per)\s+(?:clause|Clause|section|Section)\s+(\d+(?:\.\d+)*)',
            r'(?:in|In)\s+(\d+(?:\.\d+)*)',
            r'\[(\d+(?:\.\d+)*)\]',
        ]

        references = []
        for pattern in ref_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                ref = match.group(1)
                if ref and ref not in references:
                    references.append(ref)

        return references
