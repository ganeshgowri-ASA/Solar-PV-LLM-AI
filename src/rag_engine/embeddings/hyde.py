"""HyDE (Hypothetical Document Embeddings) implementation."""
from typing import Optional, List
import logging

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class HyDE:
    """
    HyDE (Hypothetical Document Embeddings) implementation.

    HyDE generates a hypothetical answer/document for a query using an LLM,
    then uses that hypothetical document for retrieval instead of the original query.
    This can improve retrieval by bridging the semantic gap between queries and documents.

    Reference: "Precise Zero-Shot Dense Retrieval without Relevance Labels"
    (Gao et al., 2022)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        prompt_template: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 256,
    ):
        """
        Initialize HyDE.

        Args:
            api_key: OpenAI API key
            model: OpenAI model name
            prompt_template: Template for generating hypothetical documents
                           Must contain {query} placeholder
            temperature: Sampling temperature for LLM
            max_tokens: Maximum tokens for generated hypothetical document
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai is not installed. Install with: pip install openai")

        if api_key:
            openai.api_key = api_key

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Default prompt template
        if prompt_template is None:
            prompt_template = (
                "Please write a passage to answer the question.\n"
                "Question: {query}\n"
                "Passage:"
            )

        self.prompt_template = prompt_template

        logger.info(f"Initialized HyDE with model: {model}")

    def generate_hypothetical_document(self, query: str) -> str:
        """
        Generate a hypothetical document for a query.

        Args:
            query: Input query

        Returns:
            Generated hypothetical document
        """
        logger.info(f"Generating hypothetical document for query: {query[:100]}...")

        # Format prompt
        prompt = self.prompt_template.format(query=query)

        try:
            # Call OpenAI API
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            hypothetical_doc = response.choices[0].message.content.strip()

            logger.info(f"Generated hypothetical document: {hypothetical_doc[:100]}...")
            return hypothetical_doc

        except Exception as e:
            logger.error(f"Error generating hypothetical document: {e}")
            logger.warning("Falling back to original query")
            return query

    def generate_multiple_hypothetical_documents(
        self,
        query: str,
        num_documents: int = 3,
    ) -> List[str]:
        """
        Generate multiple diverse hypothetical documents for a query.

        This can improve robustness by creating multiple perspectives.

        Args:
            query: Input query
            num_documents: Number of hypothetical documents to generate

        Returns:
            List of generated hypothetical documents
        """
        logger.info(
            f"Generating {num_documents} hypothetical documents for query: {query[:100]}..."
        )

        hypothetical_docs = []

        for i in range(num_documents):
            prompt = self.prompt_template.format(query=query)

            try:
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    n=1,  # Generate one at a time for better control
                )

                hypothetical_doc = response.choices[0].message.content.strip()
                hypothetical_docs.append(hypothetical_doc)

                logger.debug(f"Generated hypothetical doc {i+1}: {hypothetical_doc[:50]}...")

            except Exception as e:
                logger.error(f"Error generating hypothetical document {i+1}: {e}")

        if not hypothetical_docs:
            logger.warning("No hypothetical documents generated, using original query")
            hypothetical_docs = [query]

        logger.info(f"Successfully generated {len(hypothetical_docs)} hypothetical documents")
        return hypothetical_docs

    def enhance_query(self, query: str, mode: str = "single") -> str:
        """
        Enhance a query using HyDE.

        Args:
            query: Original query
            mode: Enhancement mode ("single" or "combined")
                 "single": Return single hypothetical document
                 "combined": Combine original query with hypothetical document

        Returns:
            Enhanced query
        """
        if mode == "single":
            return self.generate_hypothetical_document(query)

        elif mode == "combined":
            hypothetical_doc = self.generate_hypothetical_document(query)
            # Combine original query and hypothetical document
            return f"{query}\n\n{hypothetical_doc}"

        else:
            raise ValueError(f"Unknown mode: {mode}")


class MultiHyDE(HyDE):
    """
    Multi-document HyDE that generates multiple hypothetical documents.

    This variant can be used with retrievers that support multiple queries.
    """

    def __init__(
        self,
        num_documents: int = 3,
        **kwargs
    ):
        """
        Initialize Multi-HyDE.

        Args:
            num_documents: Number of hypothetical documents to generate
            **kwargs: Additional arguments for HyDE base class
        """
        super().__init__(**kwargs)
        self.num_documents = num_documents

    def enhance_query(self, query: str, mode: str = "multiple") -> List[str]:
        """
        Enhance a query by generating multiple hypothetical documents.

        Args:
            query: Original query
            mode: Enhancement mode (kept for compatibility)

        Returns:
            List of enhanced queries (including original + hypothetical docs)
        """
        hypothetical_docs = self.generate_multiple_hypothetical_documents(
            query, self.num_documents
        )

        # Optionally include original query
        return [query] + hypothetical_docs
