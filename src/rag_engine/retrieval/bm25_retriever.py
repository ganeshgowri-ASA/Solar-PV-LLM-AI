"""BM25-based keyword retrieval."""
from typing import List, Optional
import logging
import pickle
from pathlib import Path

from rank_bm25 import BM25Okapi

from ..utils.data_models import Document, RetrievalResult

logger = logging.getLogger(__name__)


class BM25Retriever:
    """
    BM25-based keyword retriever.

    Uses the BM25Okapi algorithm for keyword-based document ranking.
    """

    def __init__(
        self,
        documents: Optional[List[Document]] = None,
        k1: float = 1.5,
        b: float = 0.75,
        epsilon: float = 0.25,
    ):
        """
        Initialize BM25 retriever.

        Args:
            documents: Optional initial list of documents
            k1: BM25 k1 parameter (term frequency saturation)
            b: BM25 b parameter (length normalization)
            epsilon: BM25 epsilon parameter (IDF floor)
        """
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        self.documents: List[Document] = []
        self.bm25: Optional[BM25Okapi] = None
        self.tokenized_corpus: List[List[str]] = []

        if documents:
            self.add_documents(documents)

    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization by splitting on whitespace and lowercasing.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        # Simple whitespace tokenization - can be enhanced with more sophisticated methods
        return text.lower().split()

    def add_documents(self, documents: List[Document]):
        """
        Add documents to the BM25 index.

        Args:
            documents: List of Document objects to add
        """
        if not documents:
            return

        logger.info(f"Adding {len(documents)} documents to BM25 index")

        # Tokenize new documents
        new_tokenized = [self._tokenize(doc.content) for doc in documents]

        # Add to corpus
        self.documents.extend(documents)
        self.tokenized_corpus.extend(new_tokenized)

        # Rebuild BM25 index
        logger.info("Building BM25 index...")
        self.bm25 = BM25Okapi(
            self.tokenized_corpus,
            k1=self.k1,
            b=self.b,
            epsilon=self.epsilon
        )

        logger.info(f"BM25 index now contains {len(self.documents)} documents")

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
    ) -> List[RetrievalResult]:
        """
        Retrieve top-k documents using BM25 scoring.

        Args:
            query: Query text
            top_k: Number of documents to retrieve

        Returns:
            List of RetrievalResult objects
        """
        if not self.bm25 or not self.documents:
            logger.warning("BM25 index is empty")
            return []

        logger.info(f"Retrieving top-{top_k} documents for query: {query[:100]}...")

        # Tokenize query
        tokenized_query = self._tokenize(query)

        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = scores.argsort()[-top_k:][::-1]

        # Format results
        retrieval_results = []
        for rank, idx in enumerate(top_indices, 1):
            score = float(scores[idx])
            if score <= 0:  # Skip documents with zero or negative scores
                continue

            retrieval_results.append(
                RetrievalResult(
                    document=self.documents[idx],
                    score=score,
                    rank=rank,
                    retrieval_method="bm25"
                )
            )

        logger.info(f"Retrieved {len(retrieval_results)} documents with BM25")
        return retrieval_results

    def save(self, path: Path):
        """
        Save BM25 index to disk.

        Args:
            path: Directory path to save index
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Save documents
        with open(path / "documents.pkl", "wb") as f:
            pickle.dump(self.documents, f)

        # Save tokenized corpus
        with open(path / "tokenized_corpus.pkl", "wb") as f:
            pickle.dump(self.tokenized_corpus, f)

        # Save BM25 parameters
        params = {
            "k1": self.k1,
            "b": self.b,
            "epsilon": self.epsilon,
        }
        with open(path / "params.pkl", "wb") as f:
            pickle.dump(params, f)

        logger.info(f"BM25 index saved to {path}")

    @classmethod
    def load(cls, path: Path) -> "BM25Retriever":
        """
        Load BM25 index from disk.

        Args:
            path: Directory path to load index from

        Returns:
            Loaded BM25Retriever instance
        """
        path = Path(path)

        # Load parameters
        with open(path / "params.pkl", "rb") as f:
            params = pickle.load(f)

        # Create instance
        retriever = cls(**params)

        # Load documents
        with open(path / "documents.pkl", "rb") as f:
            retriever.documents = pickle.load(f)

        # Load tokenized corpus
        with open(path / "tokenized_corpus.pkl", "rb") as f:
            retriever.tokenized_corpus = pickle.load(f)

        # Rebuild BM25 index
        if retriever.tokenized_corpus:
            retriever.bm25 = BM25Okapi(
                retriever.tokenized_corpus,
                k1=params["k1"],
                b=params["b"],
                epsilon=params["epsilon"]
            )

        logger.info(f"BM25 index loaded from {path}")
        return retriever

    def get_document_count(self) -> int:
        """Get total number of documents in the BM25 index."""
        return len(self.documents)
