"""Clause-aware semantic chunking for IEC documents."""

import logging
import re
import uuid
from typing import List, Optional, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .models import Chunk, ClauseInfo, DocumentMetadata

logger = logging.getLogger(__name__)


class ClauseAwareChunker:
    """Chunker that respects clause boundaries and creates semantic chunks."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100,
        max_chunk_size: int = 2000,
        clause_aware: bool = True,
    ):
        """Initialize the chunker.

        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            min_chunk_size: Minimum chunk size
            max_chunk_size: Maximum chunk size
            clause_aware: Whether to respect clause boundaries
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.clause_aware = clause_aware

        # Initialize LangChain's recursive text splitter
        # Custom separators prioritizing semantic boundaries
        self.separators = [
            "\n\n\n",  # Multiple line breaks (section boundaries)
            "\n\n",  # Paragraph breaks
            "\n",  # Line breaks
            ". ",  # Sentence boundaries
            ", ",  # Clause boundaries within sentences
            " ",  # Word boundaries
            "",  # Character level
        ]

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=self.separators,
        )

    def chunk_document(
        self,
        text: str,
        clauses: List[ClauseInfo],
        metadata: DocumentMetadata,
        page_texts: Optional[Dict[int, str]] = None,
    ) -> List[Chunk]:
        """Chunk document with clause awareness.

        Args:
            text: Full document text
            clauses: List of extracted clauses
            metadata: Document metadata
            page_texts: Optional mapping of page numbers to text

        Returns:
            List of Chunk objects
        """
        if self.clause_aware and clauses:
            chunks = self._chunk_by_clause(text, clauses, metadata, page_texts)
        else:
            chunks = self._chunk_recursive(text, metadata, page_texts)

        # Post-process chunks
        chunks = self._post_process_chunks(chunks)

        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks

    def _chunk_by_clause(
        self,
        text: str,
        clauses: List[ClauseInfo],
        metadata: DocumentMetadata,
        page_texts: Optional[Dict[int, str]] = None,
    ) -> List[Chunk]:
        """Chunk document respecting clause boundaries.

        Args:
            text: Full document text
            clauses: List of clause info
            metadata: Document metadata
            page_texts: Optional page text mapping

        Returns:
            List of chunks
        """
        all_chunks = []
        chunk_index = 0

        # Sort clauses by their position in text
        sorted_clauses = self._sort_clauses_by_position(text, clauses)

        for i, clause in enumerate(sorted_clauses):
            # Extract text for this clause
            next_clause = sorted_clauses[i + 1] if i + 1 < len(sorted_clauses) else None
            clause_text = self._extract_clause_text(text, clause, next_clause)

            if not clause_text or len(clause_text) < self.min_chunk_size:
                continue

            # If clause text is small enough, create single chunk
            if len(clause_text) <= self.max_chunk_size:
                chunk = self._create_chunk(
                    content=clause_text,
                    chunk_index=chunk_index,
                    clause_info=clause,
                    page_texts=page_texts,
                    text=text,
                )
                all_chunks.append(chunk)
                chunk_index += 1

            else:
                # Split large clause into multiple chunks
                sub_chunks = self._split_large_clause(
                    clause_text, clause, chunk_index, page_texts, text
                )
                all_chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)

        # Add overlap markers
        for i in range(len(all_chunks)):
            if i > 0:
                all_chunks[i].overlap_with_previous = self.chunk_overlap > 0
            if i < len(all_chunks) - 1:
                all_chunks[i].overlap_with_next = self.chunk_overlap > 0

        return all_chunks

    def _chunk_recursive(
        self,
        text: str,
        metadata: DocumentMetadata,
        page_texts: Optional[Dict[int, str]] = None,
    ) -> List[Chunk]:
        """Chunk document using recursive character splitting.

        Args:
            text: Full document text
            metadata: Document metadata
            page_texts: Optional page text mapping

        Returns:
            List of chunks
        """
        # Use LangChain's text splitter
        text_chunks = self.text_splitter.split_text(text)

        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            if len(chunk_text) >= self.min_chunk_size:
                chunk = self._create_chunk(
                    content=chunk_text,
                    chunk_index=i,
                    clause_info=None,
                    page_texts=page_texts,
                    text=text,
                )
                chunks.append(chunk)

        # Add overlap markers
        for i in range(len(chunks)):
            if i > 0:
                chunks[i].overlap_with_previous = self.chunk_overlap > 0
            if i < len(chunks) - 1:
                chunks[i].overlap_with_next = self.chunk_overlap > 0

        return chunks

    def _split_large_clause(
        self,
        clause_text: str,
        clause_info: ClauseInfo,
        start_index: int,
        page_texts: Optional[Dict[int, str]],
        full_text: str,
    ) -> List[Chunk]:
        """Split a large clause into multiple chunks.

        Args:
            clause_text: Text of the clause
            clause_info: Clause information
            start_index: Starting chunk index
            page_texts: Page text mapping
            full_text: Full document text

        Returns:
            List of chunks
        """
        # Use text splitter for sub-chunking
        sub_texts = self.text_splitter.split_text(clause_text)

        chunks = []
        for i, sub_text in enumerate(sub_texts):
            if len(sub_text) >= self.min_chunk_size:
                chunk = self._create_chunk(
                    content=sub_text,
                    chunk_index=start_index + i,
                    clause_info=clause_info,
                    page_texts=page_texts,
                    text=full_text,
                )
                chunks.append(chunk)

        return chunks

    def _create_chunk(
        self,
        content: str,
        chunk_index: int,
        clause_info: Optional[ClauseInfo],
        page_texts: Optional[Dict[int, str]],
        text: str,
    ) -> Chunk:
        """Create a Chunk object.

        Args:
            content: Chunk text content
            chunk_index: Index of chunk in document
            clause_info: Associated clause info
            page_texts: Page text mapping
            text: Full document text

        Returns:
            Chunk object
        """
        # Generate unique chunk ID
        chunk_id = str(uuid.uuid4())

        # Count characters and words
        char_count = len(content)
        word_count = len(content.split())

        # Find page numbers for this chunk
        page_numbers = self._find_pages_for_chunk(content, page_texts, text)

        return Chunk(
            chunk_id=chunk_id,
            content=content,
            clause_info=clause_info,
            page_numbers=page_numbers,
            char_count=char_count,
            word_count=word_count,
            chunk_index=chunk_index,
        )

    def _extract_clause_text(
        self, text: str, clause: ClauseInfo, next_clause: Optional[ClauseInfo]
    ) -> str:
        """Extract text for a specific clause.

        Args:
            text: Full document text
            clause: Current clause
            next_clause: Next clause (for boundary)

        Returns:
            Clause text
        """
        # Find clause start
        clause_patterns = [
            rf"^{re.escape(clause.clause_number)}\s+{re.escape(clause.title[:50] if clause.title else '')}",
            rf"^{re.escape(clause.clause_number)}\s+",
            rf"Clause\s+{re.escape(clause.clause_number)}",
        ]

        start_pos = None
        for pattern in clause_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                start_pos = match.end()
                break

        if start_pos is None:
            return ""

        # Find clause end
        end_pos = len(text)
        if next_clause:
            next_patterns = [
                rf"^{re.escape(next_clause.clause_number)}\s+",
                rf"Clause\s+{re.escape(next_clause.clause_number)}",
            ]

            for pattern in next_patterns:
                match = re.search(pattern, text[start_pos:], re.MULTILINE | re.IGNORECASE)
                if match:
                    end_pos = start_pos + match.start()
                    break

        return text[start_pos:end_pos].strip()

    def _sort_clauses_by_position(
        self, text: str, clauses: List[ClauseInfo]
    ) -> List[ClauseInfo]:
        """Sort clauses by their position in the text.

        Args:
            text: Full document text
            clauses: List of clauses

        Returns:
            Sorted list of clauses
        """
        clause_positions = []

        for clause in clauses:
            # Find position in text
            pattern = rf"^{re.escape(clause.clause_number)}\s+"
            match = re.search(pattern, text, re.MULTILINE)

            if match:
                clause_positions.append((match.start(), clause))

        # Sort by position
        clause_positions.sort(key=lambda x: x[0])

        return [clause for _, clause in clause_positions]

    def _find_pages_for_chunk(
        self, chunk_content: str, page_texts: Optional[Dict[int, str]], full_text: str
    ) -> List[int]:
        """Find page numbers that contain the chunk content.

        Args:
            chunk_content: Chunk text
            page_texts: Page text mapping
            full_text: Full document text

        Returns:
            List of page numbers
        """
        if not page_texts:
            return []

        # Find chunk position in full text
        chunk_start = full_text.find(chunk_content[:100])  # Match first 100 chars
        if chunk_start == -1:
            return []

        chunk_end = chunk_start + len(chunk_content)

        # Find which pages contain this range
        pages = []
        current_pos = 0

        for page_num in sorted(page_texts.keys()):
            page_text = page_texts[page_num]
            page_start = current_pos
            page_end = current_pos + len(page_text)

            # Check if chunk overlaps with this page
            if not (chunk_end < page_start or chunk_start > page_end):
                pages.append(page_num)

            current_pos = page_end + 2  # Account for separator

        return pages

    def _post_process_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Post-process chunks for consistency.

        Args:
            chunks: List of chunks

        Returns:
            Processed chunks
        """
        processed = []

        for chunk in chunks:
            # Skip very small chunks
            if chunk.char_count < self.min_chunk_size:
                logger.debug(f"Skipping small chunk: {chunk.char_count} chars")
                continue

            # Trim whitespace
            chunk.content = chunk.content.strip()
            chunk.char_count = len(chunk.content)
            chunk.word_count = len(chunk.content.split())

            processed.append(chunk)

        return processed
