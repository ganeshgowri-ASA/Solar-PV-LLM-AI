"""Hybrid retrieval combining BM25 and vector similarity search."""
from typing import List, Optional, Dict
import logging
from collections import defaultdict

from .vector_retriever import VectorRetriever
from .bm25_retriever import BM25Retriever
from ..utils.data_models import Document, RetrievalResult

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid retriever combining BM25 keyword search and vector similarity search.

    Uses Reciprocal Rank Fusion (RRF) to combine results from both methods.
    """

    def __init__(
        self,
        vector_retriever: VectorRetriever,
        bm25_retriever: BM25Retriever,
        alpha: float = 0.5,
        rrf_k: int = 60,
    ):
        """
        Initialize hybrid retriever.

        Args:
            vector_retriever: Vector similarity retriever
            bm25_retriever: BM25 keyword retriever
            alpha: Weight for vector search (1-alpha for BM25)
                  Set to 0.5 for equal weighting
            rrf_k: Constant for Reciprocal Rank Fusion (default 60)
        """
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.alpha = alpha
        self.rrf_k = rrf_k

        logger.info(
            f"Initialized HybridRetriever with alpha={alpha}, "
            f"RRF k={rrf_k}"
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        retrieval_top_k: Optional[int] = None,
        fusion_method: str = "rrf",
    ) -> List[RetrievalResult]:
        """
        Retrieve documents using hybrid search.

        Args:
            query: Query text
            top_k: Final number of documents to return
            retrieval_top_k: Number of documents to retrieve from each method
                           (defaults to 2 * top_k for better fusion)
            fusion_method: Method to combine results ("rrf" or "weighted")

        Returns:
            List of RetrievalResult objects
        """
        if retrieval_top_k is None:
            retrieval_top_k = max(top_k * 2, 20)

        logger.info(
            f"Hybrid retrieval for query: {query[:100]}... "
            f"(method={fusion_method}, top_k={top_k})"
        )

        # Retrieve from both methods
        vector_results = self.vector_retriever.retrieve(query, top_k=retrieval_top_k)
        bm25_results = self.bm25_retriever.retrieve(query, top_k=retrieval_top_k)

        logger.info(
            f"Retrieved {len(vector_results)} vector results, "
            f"{len(bm25_results)} BM25 results"
        )

        # Combine results
        if fusion_method == "rrf":
            combined_results = self._reciprocal_rank_fusion(
                vector_results, bm25_results, top_k
            )
        elif fusion_method == "weighted":
            combined_results = self._weighted_fusion(
                vector_results, bm25_results, top_k
            )
        else:
            raise ValueError(f"Unknown fusion method: {fusion_method}")

        logger.info(f"Hybrid retrieval returned {len(combined_results)} documents")
        return combined_results

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[RetrievalResult],
        bm25_results: List[RetrievalResult],
        top_k: int,
    ) -> List[RetrievalResult]:
        """
        Combine results using Reciprocal Rank Fusion (RRF).

        RRF formula: score = sum(1 / (k + rank_i)) for each retrieval method

        Args:
            vector_results: Results from vector retrieval
            bm25_results: Results from BM25 retrieval
            top_k: Number of final results to return

        Returns:
            Combined and re-ranked results
        """
        # Calculate RRF scores
        rrf_scores: Dict[str, float] = defaultdict(float)
        doc_map: Dict[str, Document] = {}

        # Add vector results
        for result in vector_results:
            doc_id = result.document.id
            rrf_scores[doc_id] += self.alpha / (self.rrf_k + result.rank)
            doc_map[doc_id] = result.document

        # Add BM25 results
        for result in bm25_results:
            doc_id = result.document.id
            rrf_scores[doc_id] += (1 - self.alpha) / (self.rrf_k + result.rank)
            if doc_id not in doc_map:
                doc_map[doc_id] = result.document

        # Sort by RRF score
        sorted_doc_ids = sorted(
            rrf_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        # Create results
        combined_results = []
        for rank, (doc_id, score) in enumerate(sorted_doc_ids, 1):
            combined_results.append(
                RetrievalResult(
                    document=doc_map[doc_id],
                    score=score,
                    rank=rank,
                    retrieval_method="hybrid_rrf"
                )
            )

        return combined_results

    def _weighted_fusion(
        self,
        vector_results: List[RetrievalResult],
        bm25_results: List[RetrievalResult],
        top_k: int,
    ) -> List[RetrievalResult]:
        """
        Combine results using weighted score fusion.

        Args:
            vector_results: Results from vector retrieval
            bm25_results: Results from BM25 retrieval
            top_k: Number of final results to return

        Returns:
            Combined and re-ranked results
        """
        # Normalize scores for each method
        vector_scores = self._normalize_scores(
            {r.document.id: r.score for r in vector_results}
        )
        bm25_scores = self._normalize_scores(
            {r.document.id: r.score for r in bm25_results}
        )

        # Combine scores
        combined_scores: Dict[str, float] = defaultdict(float)
        doc_map: Dict[str, Document] = {}

        for result in vector_results:
            doc_id = result.document.id
            combined_scores[doc_id] += self.alpha * vector_scores.get(doc_id, 0)
            doc_map[doc_id] = result.document

        for result in bm25_results:
            doc_id = result.document.id
            combined_scores[doc_id] += (1 - self.alpha) * bm25_scores.get(doc_id, 0)
            if doc_id not in doc_map:
                doc_map[doc_id] = result.document

        # Sort by combined score
        sorted_doc_ids = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        # Create results
        combined_results = []
        for rank, (doc_id, score) in enumerate(sorted_doc_ids, 1):
            combined_results.append(
                RetrievalResult(
                    document=doc_map[doc_id],
                    score=score,
                    rank=rank,
                    retrieval_method="hybrid_weighted"
                )
            )

        return combined_results

    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize scores to [0, 1] range using min-max normalization.

        Args:
            scores: Dictionary of document IDs to scores

        Returns:
            Normalized scores
        """
        if not scores:
            return {}

        score_values = list(scores.values())
        min_score = min(score_values)
        max_score = max(score_values)

        if max_score == min_score:
            return {doc_id: 1.0 for doc_id in scores}

        return {
            doc_id: (score - min_score) / (max_score - min_score)
            for doc_id, score in scores.items()
        }

    def add_documents(self, documents: List[Document]):
        """
        Add documents to both retrievers.

        Args:
            documents: List of Document objects to add
        """
        logger.info(f"Adding {len(documents)} documents to hybrid retriever")
        self.vector_retriever.add_documents(documents)
        self.bm25_retriever.add_documents(documents)
