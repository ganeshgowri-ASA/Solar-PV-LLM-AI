"""Main RAG pipeline orchestrating all components."""
from typing import List, Optional, Dict, Any, Union
import logging
from pathlib import Path

from ..retrieval.vector_retriever import VectorRetriever
from ..retrieval.bm25_retriever import BM25Retriever
from ..retrieval.hybrid_retriever import HybridRetriever
from ..reranking.reranker import Reranker, create_reranker
from ..embeddings.hyde import HyDE
from ..utils.data_models import Document, RetrievalResult, RAGContext
from config.rag_config import RAGConfig

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Complete RAG pipeline integrating retrieval, re-ranking, and HyDE.

    This pipeline supports:
    - Vector similarity search
    - BM25 keyword search
    - Hybrid retrieval (combining both methods)
    - Re-ranking with Cohere or Cross-Encoder
    - Optional HyDE (Hypothetical Document Embeddings)
    """

    def __init__(
        self,
        config: Optional[RAGConfig] = None,
        vector_retriever: Optional[VectorRetriever] = None,
        bm25_retriever: Optional[BM25Retriever] = None,
        reranker: Optional[Reranker] = None,
        hyde: Optional[HyDE] = None,
    ):
        """
        Initialize RAG pipeline.

        Args:
            config: RAG configuration (if None, loads from environment)
            vector_retriever: Optional pre-initialized vector retriever
            bm25_retriever: Optional pre-initialized BM25 retriever
            reranker: Optional pre-initialized re-ranker
            hyde: Optional pre-initialized HyDE instance
        """
        # Load configuration
        self.config = config or RAGConfig.from_env()

        # Initialize retrievers
        self.vector_retriever = vector_retriever or VectorRetriever(
            embedding_model=self.config.vector_store.embedding_model,
            store_type=self.config.vector_store.store_type,
            store_path=self.config.vector_store.store_path,
            collection_name=self.config.vector_store.collection_name,
        )

        self.bm25_retriever = bm25_retriever or BM25Retriever()

        self.hybrid_retriever = HybridRetriever(
            vector_retriever=self.vector_retriever,
            bm25_retriever=self.bm25_retriever,
            alpha=self.config.retrieval.hybrid_alpha,
        )

        # Initialize re-ranker
        self.reranker = reranker
        if self.reranker is None and self.config.reranker.reranker_type != "none":
            self.reranker = create_reranker(
                reranker_type=self.config.reranker.reranker_type,
                api_key=self.config.reranker.cohere_api_key,
                model=self.config.reranker.cross_encoder_model,
            )

        # Initialize HyDE
        self.hyde = hyde
        if self.hyde is None and self.config.hyde.enabled:
            self.hyde = HyDE(
                api_key=self.config.hyde.openai_api_key,
                model=self.config.hyde.llm_model,
                prompt_template=self.config.hyde.prompt_template,
            )

        logger.info("RAGPipeline initialized successfully")
        logger.info(f"  - Vector store: {self.config.vector_store.store_type}")
        logger.info(f"  - Re-ranker: {self.config.reranker.reranker_type}")
        logger.info(f"  - HyDE enabled: {self.config.hyde.enabled}")

    def add_documents(self, documents: List[Document]):
        """
        Add documents to the retrieval system.

        Args:
            documents: List of Document objects to add
        """
        logger.info(f"Adding {len(documents)} documents to RAG pipeline")

        # Add to both retrievers
        self.vector_retriever.add_documents(documents)
        self.bm25_retriever.add_documents(documents)

        logger.info("Documents added successfully")

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        retrieval_method: str = "hybrid",
        use_hyde: Optional[bool] = None,
        use_reranker: bool = True,
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Query text
            top_k: Number of documents to return (uses config default if None)
            retrieval_method: "vector", "bm25", or "hybrid"
            use_hyde: Whether to use HyDE (uses config default if None)
            use_reranker: Whether to apply re-ranking

        Returns:
            List of retrieval results
        """
        if top_k is None:
            top_k = self.config.retrieval.top_k

        if use_hyde is None:
            use_hyde = self.config.hyde.enabled and self.hyde is not None

        logger.info(f"Retrieving documents for query: {query[:100]}...")
        logger.info(f"  - Method: {retrieval_method}, HyDE: {use_hyde}, Rerank: {use_reranker}")

        # Apply HyDE if enabled
        search_query = query
        if use_hyde and self.hyde:
            logger.info("Applying HyDE to enhance query")
            search_query = self.hyde.generate_hypothetical_document(query)
            logger.info(f"HyDE query: {search_query[:100]}...")

        # Retrieve documents
        if retrieval_method == "vector":
            results = self.vector_retriever.retrieve(search_query, top_k=top_k * 2)
        elif retrieval_method == "bm25":
            results = self.bm25_retriever.retrieve(search_query, top_k=top_k * 2)
        elif retrieval_method == "hybrid":
            results = self.hybrid_retriever.retrieve(search_query, top_k=top_k * 2)
        else:
            raise ValueError(f"Unknown retrieval method: {retrieval_method}")

        logger.info(f"Retrieved {len(results)} documents before re-ranking")

        # Apply re-ranking if enabled
        if use_reranker and self.reranker and results:
            logger.info("Applying re-ranking")
            # Use original query for re-ranking (not HyDE query)
            results = self.reranker.rerank(
                query=query,
                results=results,
                top_k=self.config.retrieval.top_k_rerank,
            )
            logger.info(f"Re-ranked to {len(results)} documents")
        else:
            # Just take top_k without re-ranking
            results = results[:top_k]

        return results

    def create_context(
        self,
        query: str,
        retrieval_results: Optional[List[RetrievalResult]] = None,
        **retrieval_kwargs
    ) -> RAGContext:
        """
        Create RAG context from query and retrieval results.

        Args:
            query: Query text
            retrieval_results: Optional pre-computed retrieval results
            **retrieval_kwargs: Additional arguments for retrieve() if results not provided

        Returns:
            RAGContext object with formatted context
        """
        # Retrieve if results not provided
        if retrieval_results is None:
            retrieval_results = self.retrieve(query, **retrieval_kwargs)

        # Format context text
        context_parts = []
        for result in retrieval_results:
            doc_text = result.document.content

            # Add metadata if available
            if result.document.metadata:
                metadata_items = [
                    f"{k}: {v}"
                    for k, v in result.document.metadata.items()
                    if k not in ['embedding', 'id']
                ]
                if metadata_items:
                    metadata_str = " | ".join(metadata_items)
                    doc_text = f"{doc_text}\n[Metadata: {metadata_str}]"

            context_parts.append(f"[{result.rank}] {doc_text}")

        context_text = "\n\n".join(context_parts)

        # Create RAG context
        rag_context = RAGContext(
            query=query,
            retrieved_docs=retrieval_results,
            context_text=context_text,
            metadata={
                "num_docs": len(retrieval_results),
                "retrieval_methods": list(set(r.retrieval_method for r in retrieval_results)),
            }
        )

        return rag_context

    def query(
        self,
        query: str,
        top_k: Optional[int] = None,
        retrieval_method: str = "hybrid",
        use_hyde: Optional[bool] = None,
        use_reranker: bool = True,
        return_context_only: bool = False,
    ) -> Union[RAGContext, Dict[str, Any]]:
        """
        Complete RAG query pipeline.

        Args:
            query: Query text
            top_k: Number of documents to retrieve
            retrieval_method: "vector", "bm25", or "hybrid"
            use_hyde: Whether to use HyDE
            use_reranker: Whether to apply re-ranking
            return_context_only: If True, return only RAGContext; else return full dict

        Returns:
            RAGContext or dictionary with context and metadata
        """
        logger.info(f"Processing RAG query: {query[:100]}...")

        # Retrieve and create context
        context = self.create_context(
            query=query,
            top_k=top_k,
            retrieval_method=retrieval_method,
            use_hyde=use_hyde,
            use_reranker=use_reranker,
        )

        if return_context_only:
            return context

        # Return full result
        return {
            "query": query,
            "context": context,
            "retrieved_docs": context.retrieved_docs,
            "formatted_context": context.context_text,
            "metadata": context.metadata,
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG pipeline.

        Returns:
            Dictionary with pipeline statistics
        """
        return {
            "vector_store": {
                "type": self.config.vector_store.store_type,
                "document_count": self.vector_retriever.get_document_count(),
                "embedding_model": self.config.vector_store.embedding_model,
            },
            "bm25": {
                "document_count": self.bm25_retriever.get_document_count(),
            },
            "config": {
                "top_k": self.config.retrieval.top_k,
                "top_k_rerank": self.config.retrieval.top_k_rerank,
                "hybrid_alpha": self.config.retrieval.hybrid_alpha,
                "reranker_type": self.config.reranker.reranker_type,
                "hyde_enabled": self.config.hyde.enabled,
            },
        }

    @classmethod
    def from_config_file(cls, config_path: Path) -> "RAGPipeline":
        """
        Create RAG pipeline from a configuration file.

        Args:
            config_path: Path to configuration file

        Returns:
            Initialized RAGPipeline
        """
        # This can be extended to support JSON/YAML config files
        config = RAGConfig.from_env()
        return cls(config=config)
