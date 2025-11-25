"""
Semantic Chunker - Intelligent chunking with clause awareness and semantic boundaries.
"""

import re
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChunkConfig:
    """Configuration for chunking behavior."""

    chunk_size: int = 1000  # Target chunk size in characters
    chunk_overlap: int = 200  # Overlap between chunks
    min_chunk_size: int = 100  # Minimum chunk size
    max_chunk_size: int = 2000  # Maximum chunk size
    respect_clause_boundaries: bool = True  # Don't split clauses
    respect_sentence_boundaries: bool = True  # Split on sentence boundaries
    respect_paragraph_boundaries: bool = True  # Prefer paragraph boundaries


class SemanticChunker:
    """
    Intelligent text chunker that respects semantic and structural boundaries.
    """

    # Sentence boundary markers
    SENTENCE_ENDINGS = r'[.!?]\s+'

    # Paragraph markers
    PARAGRAPH_MARKER = r'\n\s*\n'

    def __init__(self, config: Optional[ChunkConfig] = None):
        """
        Initialize semantic chunker.

        Args:
            config: Chunking configuration
        """
        self.config = config or ChunkConfig()
        self.sentence_regex = re.compile(self.SENTENCE_ENDINGS)
        self.paragraph_regex = re.compile(self.PARAGRAPH_MARKER)

    def chunk_text(
        self,
        text: str,
        clause_number: Optional[str] = None,
        preserve_structure: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Chunk text with semantic awareness.

        Args:
            text: Text to chunk
            clause_number: Optional clause number for context
            preserve_structure: Whether to preserve structural boundaries

        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or len(text.strip()) < self.config.min_chunk_size:
            return [{
                'text': text,
                'start_char': 0,
                'end_char': len(text),
                'chunk_method': 'whole'
            }]

        # Choose chunking strategy
        if preserve_structure and self.config.respect_paragraph_boundaries:
            chunks = self._chunk_by_paragraphs(text)
        elif self.config.respect_sentence_boundaries:
            chunks = self._chunk_by_sentences(text)
        else:
            chunks = self._chunk_by_size(text)

        # Add overlap if configured
        if self.config.chunk_overlap > 0:
            chunks = self._add_overlap(chunks, text)

        # Add metadata
        for i, chunk in enumerate(chunks):
            chunk['chunk_index'] = i
            chunk['total_chunks'] = len(chunks)
            if clause_number:
                chunk['clause_number'] = clause_number

        logger.debug(f"Created {len(chunks)} chunks from {len(text)} characters")
        return chunks

    def _chunk_by_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk text by paragraph boundaries.

        Args:
            text: Text to chunk

        Returns:
            List of chunks
        """
        # Split by paragraphs
        paragraphs = self.paragraph_regex.split(text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = []
        current_size = 0
        start_char = 0

        for para in paragraphs:
            para_size = len(para)

            # If single paragraph is too large, split it further
            if para_size > self.config.max_chunk_size:
                # Flush current chunk first
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append({
                        'text': chunk_text,
                        'start_char': start_char,
                        'end_char': start_char + len(chunk_text),
                        'chunk_method': 'paragraph'
                    })
                    start_char += len(chunk_text)
                    current_chunk = []
                    current_size = 0

                # Split large paragraph by sentences
                para_chunks = self._chunk_by_sentences(para)
                for pc in para_chunks:
                    pc['start_char'] += start_char
                    pc['end_char'] += start_char
                    chunks.append(pc)
                    start_char = pc['end_char']
                continue

            # Check if adding paragraph exceeds max size
            if current_size + para_size > self.config.max_chunk_size and current_chunk:
                # Create chunk from accumulated paragraphs
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'start_char': start_char,
                    'end_char': start_char + len(chunk_text),
                    'chunk_method': 'paragraph'
                })
                start_char += len(chunk_text)
                current_chunk = []
                current_size = 0

            # Add paragraph to current chunk
            current_chunk.append(para)
            current_size += para_size

            # If we've reached a good chunk size, finalize it
            if current_size >= self.config.chunk_size:
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'start_char': start_char,
                    'end_char': start_char + len(chunk_text),
                    'chunk_method': 'paragraph'
                })
                start_char += len(chunk_text)
                current_chunk = []
                current_size = 0

        # Add remaining content
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'start_char': start_char,
                'end_char': start_char + len(chunk_text),
                'chunk_method': 'paragraph'
            })

        return chunks

    def _chunk_by_sentences(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk text by sentence boundaries.

        Args:
            text: Text to chunk

        Returns:
            List of chunks
        """
        # Split into sentences
        sentences = self.sentence_regex.split(text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = []
        current_size = 0
        start_char = 0

        for sentence in sentences:
            sent_size = len(sentence)

            # If single sentence is too large, split by size
            if sent_size > self.config.max_chunk_size:
                # Flush current chunk
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    chunks.append({
                        'text': chunk_text,
                        'start_char': start_char,
                        'end_char': start_char + len(chunk_text),
                        'chunk_method': 'sentence'
                    })
                    start_char += len(chunk_text)
                    current_chunk = []
                    current_size = 0

                # Split large sentence
                sent_chunks = self._chunk_by_size(sentence)
                for sc in sent_chunks:
                    sc['start_char'] += start_char
                    sc['end_char'] += start_char
                    chunks.append(sc)
                    start_char = sc['end_char']
                continue

            # Check if adding sentence exceeds max size
            if current_size + sent_size > self.config.max_chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'start_char': start_char,
                    'end_char': start_char + len(chunk_text),
                    'chunk_method': 'sentence'
                })
                start_char += len(chunk_text)
                current_chunk = []
                current_size = 0

            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_size += sent_size

            # If we've reached target size, finalize
            if current_size >= self.config.chunk_size:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'start_char': start_char,
                    'end_char': start_char + len(chunk_text),
                    'chunk_method': 'sentence'
                })
                start_char += len(chunk_text)
                current_chunk = []
                current_size = 0

        # Add remaining sentences
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'start_char': start_char,
                'end_char': start_char + len(chunk_text),
                'chunk_method': 'sentence'
            })

        return chunks

    def _chunk_by_size(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk text by fixed size (fallback method).

        Args:
            text: Text to chunk

        Returns:
            List of chunks
        """
        chunks = []
        text_len = len(text)
        start = 0

        while start < text_len:
            end = min(start + self.config.chunk_size, text_len)

            # Try to break at word boundary
            if end < text_len:
                # Look for space within last 100 chars
                last_space = text.rfind(' ', end - 100, end)
                if last_space > start:
                    end = last_space

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'start_char': start,
                    'end_char': end,
                    'chunk_method': 'fixed_size'
                })

            start = end

        return chunks

    def _add_overlap(self, chunks: List[Dict[str, Any]], original_text: str) -> List[Dict[str, Any]]:
        """
        Add overlap between chunks.

        Args:
            chunks: List of chunks
            original_text: Original text

        Returns:
            Chunks with overlap added
        """
        if len(chunks) <= 1:
            return chunks

        overlapped_chunks = []

        for i, chunk in enumerate(chunks):
            chunk_text = chunk['text']
            start_char = chunk['start_char']
            end_char = chunk['end_char']

            # Add overlap from previous chunk
            if i > 0 and self.config.chunk_overlap > 0:
                overlap_start = max(0, start_char - self.config.chunk_overlap)
                overlap_text = original_text[overlap_start:start_char]

                # Try to start at sentence boundary
                sentences = self.sentence_regex.split(overlap_text)
                if len(sentences) > 1:
                    overlap_text = sentences[-1]

                chunk_text = overlap_text + chunk_text
                start_char = overlap_start

            # Add overlap to next chunk
            if i < len(chunks) - 1 and self.config.chunk_overlap > 0:
                overlap_end = min(len(original_text), end_char + self.config.chunk_overlap)
                overlap_text = original_text[end_char:overlap_end]

                # Try to end at sentence boundary
                sentences = self.sentence_regex.split(overlap_text)
                if len(sentences) > 0:
                    overlap_text = sentences[0]

                chunk_text = chunk_text + overlap_text
                end_char = overlap_end

            overlapped_chunks.append({
                **chunk,
                'text': chunk_text,
                'start_char': start_char,
                'end_char': end_char,
                'has_overlap': i > 0 or i < len(chunks) - 1
            })

        return overlapped_chunks

    def chunk_section(
        self,
        section_text: str,
        clause_number: str,
        clause_title: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk a section while preserving clause context.

        Args:
            section_text: Section text
            clause_number: Clause number
            clause_title: Clause title

        Returns:
            List of chunks with clause metadata
        """
        chunks = self.chunk_text(section_text, clause_number=clause_number)

        # Add clause context to each chunk
        for chunk in chunks:
            chunk['clause_title'] = clause_title
            chunk['clause_number'] = clause_number

        return chunks

    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistics about chunks.

        Args:
            chunks: List of chunks

        Returns:
            Dictionary of statistics
        """
        if not chunks:
            return {}

        sizes = [len(chunk['text']) for chunk in chunks]

        return {
            'total_chunks': len(chunks),
            'total_characters': sum(sizes),
            'avg_chunk_size': sum(sizes) / len(sizes),
            'min_chunk_size': min(sizes),
            'max_chunk_size': max(sizes),
            'median_chunk_size': sorted(sizes)[len(sizes) // 2]
        }
