"""Pinecone vector store client with comprehensive operations"""

import time
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from src.config.settings import settings
from src.logging.logger import get_logger
from src.utils.errors import PineconeIntegrationError

logger = get_logger(__name__)


class PineconeClient:
    """Client for managing Pinecone vector store operations"""

    def __init__(self):
        """Initialize Pinecone client and ensure index exists"""
        try:
            logger.info("Initializing Pinecone client")
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.index_name = settings.PINECONE_INDEX_NAME
            self.dimension = settings.EMBEDDING_DIMENSION

            # Ensure index exists
            self._ensure_index_exists()

            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Successfully connected to Pinecone index: {self.index_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone client: {e}")
            raise PineconeIntegrationError(f"Failed to initialize Pinecone client: {e}")

    def _ensure_index_exists(self):
        """
        Ensure the Pinecone index exists, create if it doesn't

        Creates index with:
        - Dimension: 1536 (for text-embedding-3-large)
        - Metric: cosine
        - Spec: Serverless in configured environment
        """
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]

            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")

                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.PINECONE_ENVIRONMENT
                    )
                )

                logger.info(f"Waiting for index {self.index_name} to be ready...")
                while not self.pc.describe_index(self.index_name).status['ready']:
                    time.sleep(1)

                logger.info(f"Index {self.index_name} created successfully")
            else:
                logger.info(f"Index {self.index_name} already exists")

        except Exception as e:
            logger.error(f"Failed to ensure index exists: {e}")
            raise PineconeIntegrationError(f"Failed to ensure index exists: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]],
        namespace: str = ""
    ) -> Dict[str, Any]:
        """
        Upsert vectors to Pinecone index

        Args:
            vectors: List of vector dictionaries with format:
                     [{"id": "vec1", "values": [...], "metadata": {...}}, ...]
            namespace: Optional namespace for organizing vectors

        Returns:
            Dictionary with upsert statistics

        Raises:
            PineconeIntegrationError: If upsert operation fails
        """
        try:
            if not vectors:
                raise PineconeIntegrationError("Cannot upsert empty vector list")

            logger.info(f"Upserting {len(vectors)} vectors to namespace '{namespace}'")

            response = self.index.upsert(
                vectors=vectors,
                namespace=namespace
            )

            logger.info(f"Successfully upserted {response.upserted_count} vectors")

            return {
                "upserted_count": response.upserted_count,
                "namespace": namespace,
                "total_vectors": len(vectors)
            }

        except Exception as e:
            logger.error(f"Failed to upsert vectors: {e}")
            raise PineconeIntegrationError(f"Failed to upsert vectors: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def upsert_batch(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        namespace: str = "",
        batch_size: int = None
    ) -> Dict[str, Any]:
        """
        Upsert vectors in batches with metadata

        Args:
            ids: List of unique IDs for vectors
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            namespace: Optional namespace
            batch_size: Batch size for upsert (defaults to settings.BATCH_SIZE)

        Returns:
            Dictionary with upsert statistics

        Raises:
            PineconeIntegrationError: If batch upsert fails
        """
        try:
            if len(ids) != len(embeddings) != len(metadatas):
                raise PineconeIntegrationError(
                    "Length mismatch: ids, embeddings, and metadatas must have same length"
                )

            if batch_size is None:
                batch_size = settings.BATCH_SIZE

            logger.info(
                f"Batch upserting {len(ids)} vectors in batches of {batch_size} "
                f"to namespace '{namespace}'"
            )

            total_upserted = 0

            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i + batch_size]
                batch_embeddings = embeddings[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size]

                vectors = [
                    {
                        "id": vec_id,
                        "values": embedding,
                        "metadata": metadata
                    }
                    for vec_id, embedding, metadata in zip(
                        batch_ids, batch_embeddings, batch_metadatas
                    )
                ]

                response = self.index.upsert(vectors=vectors, namespace=namespace)
                total_upserted += response.upserted_count

                logger.debug(
                    f"Batch {i // batch_size + 1}: Upserted {response.upserted_count} vectors"
                )

            logger.info(f"Successfully batch upserted {total_upserted} vectors")

            return {
                "upserted_count": total_upserted,
                "namespace": namespace,
                "total_vectors": len(ids),
                "batches": (len(ids) + batch_size - 1) // batch_size
            }

        except Exception as e:
            logger.error(f"Failed to batch upsert vectors: {e}")
            raise PineconeIntegrationError(f"Failed to batch upsert vectors: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def similarity_search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None,
        namespace: str = "",
        include_metadata: bool = True,
        include_values: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search with optional filtering

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filter (e.g., {"standards": "IEC 61215"})
            namespace: Optional namespace to search in
            include_metadata: Whether to include metadata in results
            include_values: Whether to include vector values in results

        Returns:
            List of matching results with scores and metadata

        Raises:
            PineconeIntegrationError: If search operation fails
        """
        try:
            logger.info(
                f"Performing similarity search: top_k={top_k}, "
                f"namespace='{namespace}', filter={filter_dict}"
            )

            response = self.index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter_dict,
                namespace=namespace,
                include_metadata=include_metadata,
                include_values=include_values
            )

            results = []
            for match in response.matches:
                result = {
                    "id": match.id,
                    "score": match.score
                }
                if include_metadata and hasattr(match, 'metadata'):
                    result["metadata"] = match.metadata
                if include_values and hasattr(match, 'values'):
                    result["values"] = match.values

                results.append(result)

            logger.info(f"Found {len(results)} matches")
            return results

        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            raise PineconeIntegrationError(f"Failed to perform similarity search: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def delete_vectors(
        self,
        ids: Optional[List[str]] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
        namespace: str = "",
        delete_all: bool = False
    ) -> Dict[str, Any]:
        """
        Delete vectors from the index

        Args:
            ids: List of vector IDs to delete
            filter_dict: Delete vectors matching this filter
            namespace: Namespace to delete from
            delete_all: If True, delete all vectors in namespace (use with caution!)

        Returns:
            Dictionary with deletion statistics

        Raises:
            PineconeIntegrationError: If deletion fails
        """
        try:
            if delete_all:
                logger.warning(f"Deleting ALL vectors from namespace '{namespace}'")
                self.index.delete(delete_all=True, namespace=namespace)
                return {
                    "deleted": "all",
                    "namespace": namespace
                }

            if ids:
                logger.info(f"Deleting {len(ids)} vectors by ID from namespace '{namespace}'")
                self.index.delete(ids=ids, namespace=namespace)
                return {
                    "deleted_count": len(ids),
                    "namespace": namespace,
                    "method": "by_ids"
                }

            if filter_dict:
                logger.info(f"Deleting vectors by filter from namespace '{namespace}': {filter_dict}")
                self.index.delete(filter=filter_dict, namespace=namespace)
                return {
                    "deleted": "by_filter",
                    "filter": filter_dict,
                    "namespace": namespace,
                    "method": "by_filter"
                }

            raise PineconeIntegrationError(
                "Must provide either ids, filter_dict, or set delete_all=True"
            )

        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            raise PineconeIntegrationError(f"Failed to delete vectors: {e}")

    def get_index_stats(self, namespace: str = "") -> Dict[str, Any]:
        """
        Get statistics about the index

        Args:
            namespace: Optional namespace to get stats for

        Returns:
            Dictionary with index statistics including vector count and dimension

        Raises:
            PineconeIntegrationError: If stats retrieval fails
        """
        try:
            logger.info(f"Fetching index stats for namespace '{namespace}'")

            stats = self.index.describe_index_stats()

            result = {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": {}
            }

            if stats.namespaces:
                for ns, ns_stats in stats.namespaces.items():
                    result["namespaces"][ns] = {
                        "vector_count": ns_stats.vector_count
                    }

            logger.info(f"Index stats: {result['total_vector_count']} total vectors")
            return result

        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            raise PineconeIntegrationError(f"Failed to get index stats: {e}")

    def fetch_vectors(
        self,
        ids: List[str],
        namespace: str = ""
    ) -> Dict[str, Any]:
        """
        Fetch vectors by their IDs

        Args:
            ids: List of vector IDs to fetch
            namespace: Optional namespace

        Returns:
            Dictionary mapping IDs to vector data

        Raises:
            PineconeIntegrationError: If fetch operation fails
        """
        try:
            logger.info(f"Fetching {len(ids)} vectors from namespace '{namespace}'")

            response = self.index.fetch(ids=ids, namespace=namespace)

            results = {}
            for vec_id, vector_data in response.vectors.items():
                results[vec_id] = {
                    "id": vector_data.id,
                    "values": vector_data.values,
                    "metadata": vector_data.metadata if hasattr(vector_data, 'metadata') else {}
                }

            logger.info(f"Fetched {len(results)} vectors")
            return results

        except Exception as e:
            logger.error(f"Failed to fetch vectors: {e}")
            raise PineconeIntegrationError(f"Failed to fetch vectors: {e}")
