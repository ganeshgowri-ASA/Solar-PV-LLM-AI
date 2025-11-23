"""Re-ranking modules for improving retrieval relevance."""
from typing import List, Optional
from abc import ABC, abstractmethod
import logging

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False

try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False

from ..utils.data_models import RetrievalResult

logger = logging.getLogger(__name__)


class Reranker(ABC):
    """Abstract base class for re-rankers."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None,
    ) -> List[RetrievalResult]:
        """
        Re-rank retrieval results.

        Args:
            query: Query text
            results: List of retrieval results to re-rank
            top_k: Number of top results to return (None = return all)

        Returns:
            Re-ranked list of results
        """
        pass


class CohereReranker(Reranker):
    """
    Re-ranker using Cohere's rerank API.

    Cohere provides state-of-the-art re-ranking models.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "rerank-english-v3.0",
        max_chunks_per_doc: Optional[int] = None,
    ):
        """
        Initialize Cohere re-ranker.

        Args:
            api_key: Cohere API key
            model: Cohere rerank model name
            max_chunks_per_doc: Maximum chunks per document for long documents
        """
        if not COHERE_AVAILABLE:
            raise ImportError("cohere is not installed. Install with: pip install cohere")

        self.client = cohere.Client(api_key)
        self.model = model
        self.max_chunks_per_doc = max_chunks_per_doc

        logger.info(f"Initialized CohereReranker with model: {model}")

    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None,
    ) -> List[RetrievalResult]:
        """
        Re-rank results using Cohere's rerank API.

        Args:
            query: Query text
            results: List of retrieval results to re-rank
            top_k: Number of top results to return

        Returns:
            Re-ranked list of results
        """
        if not results:
            return []

        if top_k is None:
            top_k = len(results)

        logger.info(f"Re-ranking {len(results)} results with Cohere (top_k={top_k})")

        # Prepare documents
        documents = [result.document.content for result in results]

        # Call Cohere rerank API
        try:
            rerank_response = self.client.rerank(
                query=query,
                documents=documents,
                top_n=min(top_k, len(documents)),
                model=self.model,
                max_chunks_per_doc=self.max_chunks_per_doc,
            )

            # Create re-ranked results
            reranked_results = []
            for rank, result in enumerate(rerank_response.results, 1):
                original_result = results[result.index]
                reranked_results.append(
                    RetrievalResult(
                        document=original_result.document,
                        score=result.relevance_score,
                        rank=rank,
                        retrieval_method=f"{original_result.retrieval_method}_cohere_reranked"
                    )
                )

            logger.info(f"Successfully re-ranked to {len(reranked_results)} results")
            return reranked_results

        except Exception as e:
            logger.error(f"Error during Cohere reranking: {e}")
            logger.warning("Returning original results without re-ranking")
            return results[:top_k]


class CrossEncoderReranker(Reranker):
    """
    Re-ranker using cross-encoder models from sentence-transformers.

    Cross-encoders jointly encode query and document for better relevance scoring.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        device: Optional[str] = None,
    ):
        """
        Initialize cross-encoder re-ranker.

        Args:
            model_name: Name of the cross-encoder model
            device: Device to run model on ('cuda', 'cpu', or None for auto)
        """
        if not CROSS_ENCODER_AVAILABLE:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install with: pip install sentence-transformers"
            )

        logger.info(f"Loading cross-encoder model: {model_name}")
        self.model = CrossEncoder(model_name, device=device)
        self.model_name = model_name

        logger.info(f"Initialized CrossEncoderReranker with model: {model_name}")

    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None,
        batch_size: int = 32,
    ) -> List[RetrievalResult]:
        """
        Re-rank results using cross-encoder model.

        Args:
            query: Query text
            results: List of retrieval results to re-rank
            top_k: Number of top results to return
            batch_size: Batch size for model inference

        Returns:
            Re-ranked list of results
        """
        if not results:
            return []

        if top_k is None:
            top_k = len(results)

        logger.info(
            f"Re-ranking {len(results)} results with CrossEncoder (top_k={top_k})"
        )

        # Prepare query-document pairs
        pairs = [[query, result.document.content] for result in results]

        # Get cross-encoder scores
        try:
            scores = self.model.predict(pairs, batch_size=batch_size, show_progress_bar=False)

            # Create scored results
            scored_results = [
                (result, float(score))
                for result, score in zip(results, scores)
            ]

            # Sort by score (descending)
            scored_results.sort(key=lambda x: x[1], reverse=True)

            # Create re-ranked results
            reranked_results = []
            for rank, (result, score) in enumerate(scored_results[:top_k], 1):
                reranked_results.append(
                    RetrievalResult(
                        document=result.document,
                        score=score,
                        rank=rank,
                        retrieval_method=f"{result.retrieval_method}_crossencoder_reranked"
                    )
                )

            logger.info(f"Successfully re-ranked to {len(reranked_results)} results")
            return reranked_results

        except Exception as e:
            logger.error(f"Error during cross-encoder reranking: {e}")
            logger.warning("Returning original results without re-ranking")
            return results[:top_k]


class NoOpReranker(Reranker):
    """No-op re-ranker that returns results unchanged."""

    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None,
    ) -> List[RetrievalResult]:
        """Return results unchanged."""
        if top_k is None:
            return results
        return results[:top_k]


def create_reranker(
    reranker_type: str = "none",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> Reranker:
    """
    Factory function to create a re-ranker.

    Args:
        reranker_type: Type of re-ranker ("cohere", "cross-encoder", or "none")
        api_key: API key (for Cohere)
        model: Model name
        **kwargs: Additional arguments for specific re-rankers

    Returns:
        Reranker instance
    """
    if reranker_type == "cohere":
        if not api_key:
            raise ValueError("API key required for Cohere re-ranker")
        model = model or "rerank-english-v3.0"
        return CohereReranker(api_key=api_key, model=model, **kwargs)

    elif reranker_type == "cross-encoder":
        model = model or "cross-encoder/ms-marco-MiniLM-L-6-v2"
        return CrossEncoderReranker(model_name=model, **kwargs)

    elif reranker_type == "none":
        return NoOpReranker()

    else:
        raise ValueError(f"Unknown reranker type: {reranker_type}")
