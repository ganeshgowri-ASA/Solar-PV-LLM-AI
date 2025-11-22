"""
Q&A Generator - Generate question-answer pairs from text chunks for retrieval.
"""

import os
import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..metadata.schema import QAPair

logger = logging.getLogger(__name__)


@dataclass
class QAConfig:
    """Configuration for Q&A generation."""

    model: str = "gpt-4-turbo-preview"
    max_questions_per_chunk: int = 3
    min_confidence: float = 0.7
    temperature: float = 0.3
    generate_diverse_types: bool = True  # Generate different question types


class QAGenerator:
    """
    Generate question-answer pairs from text chunks.
    """

    QUESTION_TYPES = [
        "factual",  # What, when, where questions
        "procedural",  # How-to questions
        "conceptual",  # Why, explain questions
        "comparative",  # Compare/contrast questions
        "conditional"  # What if, scenario questions
    ]

    SYSTEM_PROMPT = """You are an expert at creating question-answer pairs from technical documents, specifically IEC standards for solar photovoltaic systems.

Your task is to generate high-quality, specific questions and answers from the provided text chunk. The questions should:
1. Be directly answerable from the text
2. Be specific and technical, not vague
3. Cover important information in the chunk
4. Vary in type (factual, procedural, conceptual, etc.)
5. Be useful for retrieval and testing knowledge

For each question, also provide:
- A clear, concise answer extracted from the text
- A confidence score (0.0-1.0) based on how well the text supports the answer
- The question type (factual, procedural, conceptual, comparative, conditional)

Generate {num_questions} question-answer pairs in JSON format."""

    USER_PROMPT_TEMPLATE = """Text chunk from IEC standard:
Clause: {clause_number} - {clause_title}
Standard: {standard_id}

Text:
{text}

Generate {num_questions} question-answer pairs as a JSON array with this format:
[
  {{
    "question": "...",
    "answer": "...",
    "confidence": 0.0-1.0,
    "question_type": "factual|procedural|conceptual|comparative|conditional"
  }}
]"""

    def __init__(self, config: Optional[QAConfig] = None, api_key: Optional[str] = None):
        """
        Initialize Q&A generator.

        Args:
            config: Q&A generation configuration
            api_key: OpenAI API key (optional, will try env var)
        """
        self.config = config or QAConfig()

        # Initialize OpenAI client
        if OPENAI_AVAILABLE:
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.enabled = True
            else:
                logger.warning("OpenAI API key not found. Q&A generation will use rule-based fallback.")
                self.client = None
                self.enabled = False
        else:
            logger.warning("OpenAI package not installed. Q&A generation will use rule-based fallback.")
            self.client = None
            self.enabled = False

    def generate_qa_pairs(
        self,
        text: str,
        chunk_id: str,
        clause_number: str = "",
        clause_title: str = "",
        standard_id: str = "",
        num_questions: Optional[int] = None
    ) -> List[QAPair]:
        """
        Generate Q&A pairs from text chunk.

        Args:
            text: Text chunk
            chunk_id: Chunk identifier
            clause_number: Clause number
            clause_title: Clause title
            standard_id: Standard identifier
            num_questions: Number of questions to generate

        Returns:
            List of QAPair objects
        """
        if not text or len(text.strip()) < 50:
            logger.debug(f"Text too short for Q&A generation: {len(text)} chars")
            return []

        num_questions = num_questions or self.config.max_questions_per_chunk

        # Use OpenAI if available, otherwise fallback to rule-based
        if self.enabled and self.client:
            try:
                return self._generate_with_openai(
                    text, chunk_id, clause_number, clause_title, standard_id, num_questions
                )
            except Exception as e:
                logger.error(f"OpenAI Q&A generation failed: {e}")
                logger.info("Falling back to rule-based Q&A generation")
                return self._generate_rule_based(text, chunk_id, clause_number, clause_title)
        else:
            return self._generate_rule_based(text, chunk_id, clause_number, clause_title)

    def _generate_with_openai(
        self,
        text: str,
        chunk_id: str,
        clause_number: str,
        clause_title: str,
        standard_id: str,
        num_questions: int
    ) -> List[QAPair]:
        """
        Generate Q&A pairs using OpenAI API.

        Args:
            text: Text chunk
            chunk_id: Chunk identifier
            clause_number: Clause number
            clause_title: Clause title
            standard_id: Standard identifier
            num_questions: Number of questions

        Returns:
            List of QAPair objects
        """
        # Prepare prompt
        system_prompt = self.SYSTEM_PROMPT.format(num_questions=num_questions)
        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            clause_number=clause_number,
            clause_title=clause_title,
            standard_id=standard_id,
            text=text[:2000],  # Limit text length
            num_questions=num_questions
        )

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.config.temperature,
            response_format={"type": "json_object"}
        )

        # Parse response
        import json
        result = json.loads(response.choices[0].message.content)

        # Handle different response formats
        qa_data = result.get('qa_pairs') or result.get('questions') or result

        # If result is a dict with a list inside, extract it
        if isinstance(qa_data, dict):
            for key in qa_data:
                if isinstance(qa_data[key], list):
                    qa_data = qa_data[key]
                    break

        if not isinstance(qa_data, list):
            logger.warning(f"Unexpected OpenAI response format: {result}")
            return []

        # Convert to QAPair objects
        qa_pairs = []
        for item in qa_data:
            try:
                qa_pair = QAPair(
                    question=item['question'],
                    answer=item['answer'],
                    chunk_id=chunk_id,
                    confidence=float(item.get('confidence', 0.8)),
                    question_type=item.get('question_type', 'factual')
                )

                # Filter by confidence
                if qa_pair.confidence >= self.config.min_confidence:
                    qa_pairs.append(qa_pair)
            except (KeyError, ValueError) as e:
                logger.warning(f"Failed to parse Q&A pair: {e}")
                continue

        return qa_pairs

    def _generate_rule_based(
        self,
        text: str,
        chunk_id: str,
        clause_number: str,
        clause_title: str
    ) -> List[QAPair]:
        """
        Generate Q&A pairs using rule-based approach (fallback).

        Args:
            text: Text chunk
            chunk_id: Chunk identifier
            clause_number: Clause number
            clause_title: Clause title

        Returns:
            List of QAPair objects
        """
        qa_pairs = []

        # Generate question from clause title
        if clause_title:
            qa_pairs.append(QAPair(
                question=f"What does clause {clause_number} ({clause_title}) specify?",
                answer=text[:200] + "..." if len(text) > 200 else text,
                chunk_id=chunk_id,
                confidence=0.7,
                question_type="factual"
            ))

        # Look for definitions
        definition_pattern = r'(.+?)\s+(?:is defined as|means|refers to|is)\s+(.+?)(?:\.|$)'
        matches = re.finditer(definition_pattern, text, re.IGNORECASE)
        for match in matches:
            term = match.group(1).strip()
            definition = match.group(2).strip()
            if len(term) < 50 and len(definition) > 10:
                qa_pairs.append(QAPair(
                    question=f"What is {term}?",
                    answer=definition,
                    chunk_id=chunk_id,
                    confidence=0.8,
                    question_type="factual"
                ))
            if len(qa_pairs) >= self.config.max_questions_per_chunk:
                break

        # Look for requirements (shall/must statements)
        requirement_pattern = r'(.+?)\s+(?:shall|must)\s+(.+?)(?:\.|$)'
        matches = re.finditer(requirement_pattern, text, re.IGNORECASE)
        for match in matches:
            subject = match.group(1).strip()
            requirement = match.group(2).strip()
            if len(subject) < 100:
                qa_pairs.append(QAPair(
                    question=f"What are the requirements for {subject}?",
                    answer=f"{subject} shall {requirement}",
                    chunk_id=chunk_id,
                    confidence=0.75,
                    question_type="procedural"
                ))
            if len(qa_pairs) >= self.config.max_questions_per_chunk:
                break

        # Look for numerical values and ranges
        number_pattern = r'(\w+(?:\s+\w+)*)\s+(?:is|are|equals?|ranges? from)\s+([0-9.,]+(?:\s*(?:to|-|–)\s*[0-9.,]+)?)\s*([A-Za-z°%]+)?'
        matches = re.finditer(number_pattern, text)
        for match in matches:
            parameter = match.group(1).strip()
            value = match.group(2).strip()
            unit = match.group(3).strip() if match.group(3) else ""
            qa_pairs.append(QAPair(
                question=f"What is the value/range of {parameter}?",
                answer=f"{value} {unit}".strip(),
                chunk_id=chunk_id,
                confidence=0.85,
                question_type="factual"
            ))
            if len(qa_pairs) >= self.config.max_questions_per_chunk:
                break

        # Ensure we have at least one Q&A pair
        if not qa_pairs:
            # Generic question based on first sentence
            sentences = text.split('.')
            if sentences:
                first_sentence = sentences[0].strip()
                qa_pairs.append(QAPair(
                    question=f"What information is provided in clause {clause_number}?",
                    answer=first_sentence,
                    chunk_id=chunk_id,
                    confidence=0.6,
                    question_type="factual"
                ))

        return qa_pairs[:self.config.max_questions_per_chunk]

    def validate_qa_pair(self, qa_pair: QAPair, source_text: str) -> bool:
        """
        Validate that Q&A pair is answerable from source text.

        Args:
            qa_pair: Q&A pair to validate
            source_text: Source text

        Returns:
            True if valid
        """
        # Check if answer appears in source (approximately)
        answer_words = set(qa_pair.answer.lower().split())
        source_words = set(source_text.lower().split())

        # At least 50% of answer words should appear in source
        overlap = len(answer_words & source_words) / len(answer_words) if answer_words else 0

        return overlap >= 0.5 and qa_pair.confidence >= self.config.min_confidence
