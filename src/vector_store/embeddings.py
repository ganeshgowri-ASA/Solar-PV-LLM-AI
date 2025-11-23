"""Embedding generation service using OpenAI"""

from typing import List, Union
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from src.config.settings import settings
from src.logging.logger import get_logger
from src.utils.errors import EmbeddingError

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating embeddings using OpenAI"""

    def __init__(self):
        """Initialize the embedding service"""
        try:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.EMBEDDING_MODEL
            self.dimension = settings.EMBEDDING_DIMENSION
            logger.info(
                f"Embedding service initialized with model: {self.model}, "
                f"dimension: {self.dimension}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise EmbeddingError(f"Failed to initialize embedding service: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            if not text or not text.strip():
                raise EmbeddingError("Cannot generate embedding for empty text")

            logger.debug(f"Generating embedding for text of length {len(text)}")

            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimension
            )

            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with dimension {len(embedding)}")

            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise EmbeddingError(f"Failed to generate embedding: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = None
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches

        Args:
            texts: List of input texts to embed
            batch_size: Size of batches for processing (defaults to settings.BATCH_SIZE)

        Returns:
            List of embedding vectors

        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            if not texts:
                raise EmbeddingError("Cannot generate embeddings for empty text list")

            if batch_size is None:
                batch_size = settings.BATCH_SIZE

            logger.info(f"Generating embeddings for {len(texts)} texts in batches of {batch_size}")

            embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                logger.debug(f"Processing batch {i // batch_size + 1} with {len(batch)} texts")

                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    dimensions=self.dimension
                )

                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise EmbeddingError(f"Failed to generate batch embeddings: {e}")

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this service

        Returns:
            Integer dimension of embeddings
        """
        return self.dimension
