"""Q&A pair generator for document chunks."""

import logging
import os
from typing import List, Optional, Dict
from anthropic import Anthropic
import openai

from .models import QAPair, Chunk, DocumentMetadata

logger = logging.getLogger(__name__)


class QAGenerator:
    """Generates atomic question-answer pairs from document chunks."""

    DEFAULT_SYSTEM_PROMPT = """You are an expert in IEC standards and solar PV systems.
Generate atomic, self-contained question-answer pairs from the given text chunk.

Requirements:
1. Each question should be specific and answerable from the context alone
2. Questions should be diverse (factual, conceptual, application-based)
3. Answers should be concise but complete
4. Questions should be standalone (include necessary context)
5. Focus on technical content, specifications, and requirements

Output format: Return a JSON array of objects with these fields:
- question: The question text
- answer: The answer text
- question_type: One of "factual", "conceptual", or "application"
- keywords: List of 3-5 key terms from the Q&A pair"""

    def __init__(
        self,
        provider: str = "anthropic",
        model: str = "claude-3-haiku-20240307",
        temperature: float = 0.7,
        max_questions_per_chunk: int = 3,
        api_key: Optional[str] = None,
    ):
        """Initialize the Q&A generator.

        Args:
            provider: LLM provider ('anthropic' or 'openai')
            model: Model name
            temperature: Generation temperature
            max_questions_per_chunk: Maximum questions to generate per chunk
            api_key: Optional API key (otherwise uses environment variable)
        """
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_questions_per_chunk = max_questions_per_chunk

        # Initialize API client
        if self.provider == "anthropic":
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("No Anthropic API key found. Q&A generation will be disabled.")
                self.client = None
            else:
                self.client = Anthropic(api_key=api_key)

        elif self.provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("No OpenAI API key found. Q&A generation will be disabled.")
                self.client = None
            else:
                openai.api_key = api_key
                self.client = openai

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def generate_qa_pairs(
        self, chunk: Chunk, metadata: Optional[DocumentMetadata] = None
    ) -> List[QAPair]:
        """Generate Q&A pairs for a chunk.

        Args:
            chunk: Chunk to generate Q&A pairs for
            metadata: Optional document metadata for context

        Returns:
            List of QAPair objects
        """
        if not self.client:
            logger.debug("Q&A generation disabled (no API key)")
            return []

        if len(chunk.content) < 100:
            logger.debug(f"Skipping Q&A for small chunk {chunk.chunk_id}")
            return []

        try:
            # Build context for generation
            context = self._build_context(chunk, metadata)

            # Generate Q&A pairs
            if self.provider == "anthropic":
                qa_pairs = self._generate_with_anthropic(context)
            elif self.provider == "openai":
                qa_pairs = self._generate_with_openai(context)
            else:
                return []

            logger.info(f"Generated {len(qa_pairs)} Q&A pairs for chunk {chunk.chunk_id}")
            return qa_pairs

        except Exception as e:
            logger.error(f"Error generating Q&A pairs: {e}")
            return []

    def _build_context(self, chunk: Chunk, metadata: Optional[DocumentMetadata]) -> str:
        """Build context string for Q&A generation.

        Args:
            chunk: Chunk to generate Q&A for
            metadata: Document metadata

        Returns:
            Context string
        """
        context_parts = []

        # Add metadata context
        if metadata:
            if metadata.standard_id:
                context_parts.append(f"Document: {metadata.standard_id}")
            if metadata.title:
                context_parts.append(f"Title: {metadata.title}")

        # Add clause context
        if chunk.clause_info:
            context_parts.append(
                f"Clause: {chunk.clause_info.clause_number}"
                + (f" - {chunk.clause_info.title}" if chunk.clause_info.title else "")
            )

        # Add chunk content
        context_parts.append(f"\nContent:\n{chunk.content}")

        return "\n".join(context_parts)

    def _generate_with_anthropic(self, context: str) -> List[QAPair]:
        """Generate Q&A pairs using Anthropic API.

        Args:
            context: Context for generation

        Returns:
            List of QAPair objects
        """
        try:
            prompt = f"""{context}

Generate {self.max_questions_per_chunk} diverse question-answer pairs from the above content.
Return ONLY a valid JSON array, no other text."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=self.temperature,
                system=self.DEFAULT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            response_text = response.content[0].text
            qa_pairs = self._parse_qa_response(response_text)

            return qa_pairs

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return []

    def _generate_with_openai(self, context: str) -> List[QAPair]:
        """Generate Q&A pairs using OpenAI API.

        Args:
            context: Context for generation

        Returns:
            List of QAPair objects
        """
        try:
            prompt = f"""{context}

Generate {self.max_questions_per_chunk} diverse question-answer pairs from the above content.
Return ONLY a valid JSON array, no other text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.DEFAULT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=2000,
            )

            # Parse response
            response_text = response.choices[0].message.content
            qa_pairs = self._parse_qa_response(response_text)

            return qa_pairs

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return []

    def _parse_qa_response(self, response_text: str) -> List[QAPair]:
        """Parse Q&A pairs from LLM response.

        Args:
            response_text: Raw response text

        Returns:
            List of QAPair objects
        """
        import json
        import re

        # Try to extract JSON array from response
        # Look for JSON array pattern
        json_match = re.search(r'\[[\s\S]*\]', response_text)

        if not json_match:
            logger.warning("No JSON array found in response")
            return []

        try:
            json_str = json_match.group(0)
            qa_data = json.loads(json_str)

            if not isinstance(qa_data, list):
                logger.warning("Response is not a JSON array")
                return []

            qa_pairs = []
            for item in qa_data:
                if isinstance(item, dict) and "question" in item and "answer" in item:
                    qa_pair = QAPair(
                        question=item.get("question", ""),
                        answer=item.get("answer", ""),
                        question_type=item.get("question_type"),
                        keywords=item.get("keywords", []),
                    )
                    qa_pairs.append(qa_pair)

            return qa_pairs

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return []

    def generate_batch(
        self, chunks: List[Chunk], metadata: Optional[DocumentMetadata] = None
    ) -> Dict[str, List[QAPair]]:
        """Generate Q&A pairs for multiple chunks.

        Args:
            chunks: List of chunks
            metadata: Document metadata

        Returns:
            Dictionary mapping chunk IDs to Q&A pairs
        """
        results = {}

        for i, chunk in enumerate(chunks):
            logger.info(f"Generating Q&A for chunk {i+1}/{len(chunks)}")
            qa_pairs = self.generate_qa_pairs(chunk, metadata)
            results[chunk.chunk_id] = qa_pairs

            # Update chunk with Q&A pairs
            chunk.qa_pairs = qa_pairs

        return results
