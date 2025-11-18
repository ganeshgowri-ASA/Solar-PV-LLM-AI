"""Unified vector store handler combining embeddings and Pinecone operations"""

from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime

from src.vector_store.embeddings import EmbeddingService
from src.vector_store.pinecone_client import PineconeClient
from src.logging.logger import get_logger
from src.utils.errors import PineconeIntegrationError, EmbeddingError

logger = get_logger(__name__)


class VectorStoreHandler:
    """
    Unified handler for vector store operations
    Combines embedding generation and Pinecone vector operations
    """

    def __init__(self):
        """Initialize the vector store handler"""
        try:
            logger.info("Initializing VectorStoreHandler")
            self.embedding_service = EmbeddingService()
            self.pinecone_client = PineconeClient()
            logger.info("VectorStoreHandler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize VectorStoreHandler: {e}")
            raise

    def _generate_id(self, text: str, prefix: str = "doc") -> str:
        """
        Generate a unique ID for a document

        Args:
            text: Document text
            prefix: ID prefix

        Returns:
            Unique ID string
        """
        hash_obj = hashlib.md5(text.encode())
        return f"{prefix}_{hash_obj.hexdigest()}"

    def ingest_documents(
        self,
        documents: List[Dict[str, Any]],
        namespace: str = "",
        batch_size: int = None
    ) -> Dict[str, Any]:
        """
        Ingest documents into the vector store

        Args:
            documents: List of document dictionaries with format:
                      [{"text": "...", "metadata": {...}}, ...]
            namespace: Optional namespace for organizing documents
            batch_size: Batch size for operations

        Returns:
            Dictionary with ingestion statistics

        Raises:
            EmbeddingError: If embedding generation fails
            PineconeIntegrationError: If vector upsert fails
        """
        try:
            logger.info(f"Ingesting {len(documents)} documents into namespace '{namespace}'")

            # Extract texts and metadatas
            texts = [doc.get("text", "") for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]

            # Validate
            if not all(texts):
                raise ValueError("All documents must have non-empty 'text' field")

            # Generate embeddings
            logger.info("Generating embeddings for documents")
            embeddings = self.embedding_service.generate_embeddings_batch(
                texts, batch_size=batch_size
            )

            # Generate IDs
            ids = []
            for i, (text, metadata) in enumerate(zip(texts, metadatas)):
                # Use provided ID or generate one
                doc_id = metadata.get("id", self._generate_id(text))
                ids.append(doc_id)

                # Add timestamp to metadata
                if "timestamp" not in metadata:
                    metadata["timestamp"] = datetime.utcnow().isoformat()

                # Add text snippet to metadata for reference
                if "text_snippet" not in metadata:
                    metadata["text_snippet"] = text[:200]

            # Upsert to Pinecone
            logger.info("Upserting vectors to Pinecone")
            result = self.pinecone_client.upsert_batch(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                namespace=namespace,
                batch_size=batch_size
            )

            logger.info(f"Successfully ingested {result['upserted_count']} documents")

            return {
                "status": "success",
                "documents_ingested": result["upserted_count"],
                "namespace": namespace,
                "batches_processed": result.get("batches", 1)
            }

        except (EmbeddingError, PineconeIntegrationError) as e:
            logger.error(f"Failed to ingest documents: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during document ingestion: {e}")
            raise PineconeIntegrationError(f"Document ingestion failed: {e}")

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        namespace: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using text query

        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters (e.g., {"standards": "IEC 61215"})
            namespace: Optional namespace to search in

        Returns:
            List of search results with scores and metadata

        Raises:
            EmbeddingError: If query embedding generation fails
            PineconeIntegrationError: If search operation fails
        """
        try:
            logger.info(
                f"Searching for query: '{query[:50]}...' with top_k={top_k}, "
                f"filters={filters}, namespace='{namespace}'"
            )

            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query)

            # Search in Pinecone
            results = self.pinecone_client.similarity_search(
                query_vector=query_embedding,
                top_k=top_k,
                filter_dict=filters,
                namespace=namespace,
                include_metadata=True,
                include_values=False
            )

            logger.info(f"Search returned {len(results)} results")

            return results

        except (EmbeddingError, PineconeIntegrationError) as e:
            logger.error(f"Search failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            raise PineconeIntegrationError(f"Search failed: {e}")

    def search_with_filters(
        self,
        query: str,
        top_k: int = 10,
        standards: Optional[str] = None,
        clauses: Optional[List[str]] = None,
        test_type: Optional[str] = None,
        namespace: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Search with Solar PV specific filters

        Args:
            query: Search query text
            top_k: Number of results to return
            standards: Filter by standards (e.g., "IEC 61215", "IEC 61730")
            clauses: Filter by specific clauses
            test_type: Filter by test type (e.g., "performance", "safety")
            namespace: Optional namespace

        Returns:
            List of search results

        Raises:
            EmbeddingError: If query embedding generation fails
            PineconeIntegrationError: If search operation fails
        """
        try:
            # Build filter dictionary
            filters = {}

            if standards:
                filters["standards"] = standards

            if clauses:
                filters["clauses"] = {"$in": clauses}

            if test_type:
                filters["test_type"] = test_type

            logger.info(f"Searching with Solar PV filters: {filters}")

            return self.search(
                query=query,
                top_k=top_k,
                filters=filters if filters else None,
                namespace=namespace
            )

        except Exception as e:
            logger.error(f"Filtered search failed: {e}")
            raise

    def delete_documents(
        self,
        ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        namespace: str = ""
    ) -> Dict[str, Any]:
        """
        Delete documents from the vector store

        Args:
            ids: List of document IDs to delete
            filters: Delete documents matching these filters
            namespace: Namespace to delete from

        Returns:
            Dictionary with deletion statistics

        Raises:
            PineconeIntegrationError: If deletion fails
        """
        try:
            logger.info(f"Deleting documents: ids={ids}, filters={filters}, namespace='{namespace}'")

            result = self.pinecone_client.delete_vectors(
                ids=ids,
                filter_dict=filters,
                namespace=namespace,
                delete_all=False
            )

            logger.info(f"Successfully deleted documents: {result}")

            return {
                "status": "success",
                "deletion_info": result
            }

        except PineconeIntegrationError as e:
            logger.error(f"Failed to delete documents: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during deletion: {e}")
            raise PineconeIntegrationError(f"Document deletion failed: {e}")

    def get_stats(self, namespace: str = "") -> Dict[str, Any]:
        """
        Get vector store statistics

        Args:
            namespace: Optional namespace

        Returns:
            Dictionary with statistics

        Raises:
            PineconeIntegrationError: If stats retrieval fails
        """
        try:
            logger.info(f"Fetching stats for namespace '{namespace}'")

            stats = self.pinecone_client.get_index_stats(namespace=namespace)

            logger.info(f"Retrieved stats: {stats}")

            return {
                "status": "success",
                "stats": stats
            }

        except PineconeIntegrationError as e:
            logger.error(f"Failed to get stats: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while getting stats: {e}")
            raise PineconeIntegrationError(f"Stats retrieval failed: {e}")
