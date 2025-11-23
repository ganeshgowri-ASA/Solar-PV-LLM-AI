"""
Citation Injector - Inject inline citations into LLM responses.

This module handles the injection of citation markers into LLM-generated
text based on matching content from retrieved documents.
"""

import re
from typing import List, Dict, Tuple, Set
from difflib import SequenceMatcher


class CitationInjector:
    """
    Injects inline citations into LLM responses based on content matching
    with retrieved documents.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.6,
        min_match_length: int = 30,
        citation_format: str = "[{id}]"
    ):
        """
        Initialize citation injector.

        Args:
            similarity_threshold: Minimum similarity score for matching (0-1)
            min_match_length: Minimum character length for content matching
            citation_format: Format string for citation markers (e.g., "[{id}]", "({id})")
        """
        self.similarity_threshold = similarity_threshold
        self.min_match_length = min_match_length
        self.citation_format = citation_format

    def inject_citations(
        self,
        response: str,
        retrieved_docs: List,
        citations: List
    ) -> str:
        """
        Inject inline citations into LLM response.

        Args:
            response: LLM-generated response text
            retrieved_docs: List of RetrievedDocument objects
            citations: List of Citation objects

        Returns:
            Response text with injected citations
        """
        # Build mapping from doc_id to citation_id
        doc_to_citation = {}
        for citation in citations:
            doc_to_citation[citation.source_doc_id] = citation.citation_id

        # Split response into sentences
        sentences = self._split_into_sentences(response)

        # Track which citations have been used
        used_citations: Set[int] = set()

        # Process each sentence
        processed_sentences = []
        for sentence in sentences:
            # Find best matching document for this sentence
            best_match_doc = None
            best_match_score = 0.0

            for doc in retrieved_docs:
                score = self._calculate_similarity(sentence, doc.content)
                if score > best_match_score and score >= self.similarity_threshold:
                    best_match_score = score
                    best_match_doc = doc

            # Inject citation if we found a good match
            if best_match_doc and best_match_doc.doc_id in doc_to_citation:
                citation_id = doc_to_citation[best_match_doc.doc_id]
                citation_marker = self.citation_format.format(id=citation_id)

                # Only add citation if not already used in this sentence
                if citation_marker not in sentence:
                    # Add citation at end of sentence (before period if present)
                    sentence = self._insert_citation(sentence, citation_marker)
                    used_citations.add(citation_id)

            processed_sentences.append(sentence)

        # Join sentences back together
        processed_response = ' '.join(processed_sentences)

        # Handle standard ID and clause references explicitly
        processed_response = self._inject_reference_citations(
            processed_response,
            citations
        )

        return processed_response

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Simple sentence splitting - can be enhanced with nltk if needed
        # Split on period, exclamation, or question mark followed by space
        sentences = re.split(r'([.!?]+\s+)', text)

        # Rejoin sentences with their punctuation
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                result.append(sentences[i] + sentences[i + 1])
            else:
                result.append(sentences[i])

        # Add last sentence if it doesn't have trailing punctuation
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1])

        return [s.strip() for s in result if s.strip()]

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0 and 1
        """
        # Normalize texts
        text1_clean = self._normalize_text(text1)
        text2_clean = self._normalize_text(text2)

        # Use SequenceMatcher for similarity
        matcher = SequenceMatcher(None, text1_clean, text2_clean)
        similarity = matcher.ratio()

        # Also check for substring matches
        if len(text1_clean) >= self.min_match_length:
            if text1_clean in text2_clean or text2_clean in text1_clean:
                similarity = max(similarity, 0.8)

        # Check for keyword overlap
        words1 = set(text1_clean.split())
        words2 = set(text2_clean.split())

        if len(words1) > 0 and len(words2) > 0:
            word_overlap = len(words1 & words2) / max(len(words1), len(words2))
            # Weight word overlap
            similarity = max(similarity, word_overlap * 0.7)

        return similarity

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Remove punctuation (except periods in numbers)
        text = re.sub(r'[^\w\s.]', ' ', text)

        # Remove extra spaces again
        text = ' '.join(text.split())

        return text

    def _insert_citation(self, sentence: str, citation_marker: str) -> str:
        """
        Insert citation marker at the end of a sentence.

        Args:
            sentence: Sentence text
            citation_marker: Citation marker to insert (e.g., "[1]")

        Returns:
            Sentence with citation inserted
        """
        # Find the last punctuation
        match = re.search(r'([.!?]+)(\s*)$', sentence)

        if match:
            # Insert before final punctuation
            pos = match.start(1)
            return sentence[:pos] + citation_marker + sentence[pos:]
        else:
            # No punctuation, just append
            return sentence + citation_marker

    def _inject_reference_citations(
        self,
        text: str,
        citations: List
    ) -> str:
        """
        Inject citations for explicit standard ID and clause references.

        Args:
            text: Text to process
            citations: List of Citation objects

        Returns:
            Text with citations injected
        """
        # Build patterns for each citation's standard ID and clause
        for citation in citations:
            if citation.standard_id:
                # Create pattern to match the standard ID
                pattern = re.escape(citation.standard_id)
                citation_marker = self.citation_format.format(id=citation.citation_id)

                # Replace standard ID with standard ID + citation (if not already cited)
                def replace_func(match):
                    # Check if citation already follows
                    end_pos = match.end()
                    following = text[end_pos:end_pos + 10]
                    if citation_marker in following:
                        return match.group(0)
                    return match.group(0) + citation_marker

                text = re.sub(
                    pattern,
                    replace_func,
                    text,
                    count=1  # Only first occurrence
                )

        return text
