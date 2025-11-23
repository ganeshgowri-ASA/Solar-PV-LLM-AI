"""
RAG (Retrieval-Augmented Generation) Service
Handles semantic search and context retrieval from Pinecone.
"""

import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from .pinecone_config import (
    get_pinecone_config,
    PineconeConfig,
    Namespaces,
    BATCH_LIMITS,
    CONSISTENCY_WAIT_SECONDS
)


@dataclass
class SearchResult:
    """Container for search results"""
    hits: List[Dict[str, Any]]
    context: str
    citations: List[Dict[str, Any]]
    query: str
    namespace: str


class RAGService:
    """
    RAG service for Solar PV knowledge base.
    Handles vector search, context building, and citation extraction.
    """

    def __init__(self, config: Optional[PineconeConfig] = None):
        """
        Initialize RAG service.

        Args:
            config: Pinecone configuration (uses default if not provided)
        """
        self.config = config
        self._pc = None
        self._index = None

    def _get_client(self):
        """Lazy initialization of Pinecone client"""
        if self._pc is None:
            try:
                from pinecone import Pinecone
                if self.config is None:
                    self.config = get_pinecone_config()
                self._pc = Pinecone(api_key=self.config.api_key)
            except ImportError:
                raise ImportError(
                    "Pinecone package not installed. "
                    "Install with: pip install pinecone"
                )
            except ValueError as e:
                raise ValueError(f"Pinecone configuration error: {e}")
        return self._pc

    def _get_index(self):
        """Get Pinecone index"""
        if self._index is None:
            pc = self._get_client()
            self._index = pc.Index(self.config.index_name)
        return self._index

    def search(
        self,
        query: str,
        namespace: str = None,
        top_k: int = 5,
        filters: Dict[str, Any] = None,
        rerank: bool = True
    ) -> SearchResult:
        """
        Perform semantic search on the knowledge base.

        Args:
            query: Search query text
            namespace: Pinecone namespace (default: solar_pv_docs)
            top_k: Number of results to return
            filters: Metadata filters
            rerank: Whether to apply reranking

        Returns:
            SearchResult with hits, context, and citations
        """
        namespace = namespace or self.config.namespace
        index = self._get_index()

        # Build query
        query_dict = {
            "top_k": top_k * 2 if rerank else top_k,
            "inputs": {"text": query}
        }

        if filters:
            query_dict["filter"] = filters

        # Execute search with optional reranking
        if rerank:
            results = index.search(
                namespace=namespace,
                query=query_dict,
                rerank={
                    "model": self.config.rerank_model,
                    "top_n": top_k,
                    "rank_fields": ["content"]
                }
            )
        else:
            results = index.search(
                namespace=namespace,
                query=query_dict
            )

        # Process results
        hits = results.result.hits if hasattr(results, 'result') else []

        return SearchResult(
            hits=hits,
            context=self._build_context(hits),
            citations=self._extract_citations(hits),
            query=query,
            namespace=namespace
        )

    def _build_context(self, hits: List[Dict[str, Any]]) -> str:
        """Build context string from search hits"""
        context_parts = []
        for i, hit in enumerate(hits):
            content = hit.get('fields', {}).get('content', '')
            if content:
                context_parts.append(f"[{i+1}] {content}")
        return "\n\n".join(context_parts)

    def _extract_citations(self, hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract citation information from hits"""
        citations = []
        for i, hit in enumerate(hits):
            fields = hit.get('fields', {})
            citations.append({
                "ref": i + 1,
                "id": hit.get('_id', 'unknown'),
                "source": hit.get('_id', 'Unknown Source'),
                "text": fields.get('content', ''),
                "score": hit.get('_score', 0.0),
                "category": fields.get('category', 'general'),
                "topic": fields.get('topic', 'General'),
                "difficulty": fields.get('difficulty', 'intermediate')
            })
        return citations

    def upsert_records(
        self,
        records: List[Dict[str, Any]],
        namespace: str = None,
        wait_for_consistency: bool = True
    ) -> Dict[str, Any]:
        """
        Upsert records to the knowledge base.

        Args:
            records: List of records to upsert
            namespace: Target namespace
            wait_for_consistency: Wait for indexing to complete

        Returns:
            Upsert result summary
        """
        namespace = namespace or self.config.namespace
        index = self._get_index()

        # Batch upsert respecting limits
        batch_size = BATCH_LIMITS["text_records"]
        total_upserted = 0

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            index.upsert_records(namespace, batch)
            total_upserted += len(batch)
            time.sleep(0.1)  # Rate limiting

        if wait_for_consistency:
            time.sleep(CONSISTENCY_WAIT_SECONDS)

        return {
            "success": True,
            "upserted_count": total_upserted,
            "namespace": namespace
        }

    def delete_records(
        self,
        ids: List[str],
        namespace: str = None
    ) -> Dict[str, Any]:
        """
        Delete records by ID.

        Args:
            ids: List of record IDs to delete
            namespace: Target namespace

        Returns:
            Delete result summary
        """
        namespace = namespace or self.config.namespace
        index = self._get_index()

        index.delete(namespace=namespace, ids=ids)

        return {
            "success": True,
            "deleted_count": len(ids),
            "namespace": namespace
        }

    def fetch_records(
        self,
        ids: List[str],
        namespace: str = None
    ) -> Dict[str, Any]:
        """
        Fetch records by ID.

        Args:
            ids: List of record IDs to fetch
            namespace: Target namespace

        Returns:
            Fetched records
        """
        namespace = namespace or self.config.namespace
        index = self._get_index()

        result = index.fetch(namespace=namespace, ids=ids)

        return {
            "success": True,
            "records": result.vectors if hasattr(result, 'vectors') else {},
            "namespace": namespace
        }


# Singleton service instance
_service_instance: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get or create RAG service singleton.

    Returns:
        RAGService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = RAGService()
    return _service_instance
