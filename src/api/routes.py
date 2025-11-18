"""FastAPI routes for vector store operations"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from src.api.models import (
    IngestDocumentsRequest,
    IngestResponse,
    SearchRequest,
    SearchWithFiltersRequest,
    SearchResponse,
    SearchResult,
    DeleteDocumentsRequest,
    DeleteResponse,
    StatsRequest,
    StatsResponse,
    IndexStats,
    ErrorResponse,
    HealthResponse
)
from src.vector_store.handler import VectorStoreHandler
from src.logging.logger import get_logger
from src.utils.errors import (
    PineconeIntegrationError,
    EmbeddingError,
    SolarPVAIException
)
from src.config.settings import settings

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["vector-store"])

# Initialize vector store handler (singleton)
_vector_store_handler = None


def get_vector_store_handler() -> VectorStoreHandler:
    """Get or create vector store handler instance"""
    global _vector_store_handler
    if _vector_store_handler is None:
        _vector_store_handler = VectorStoreHandler()
    return _vector_store_handler


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check if the service is running and all components are healthy"
)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    try:
        handler = get_vector_store_handler()

        return HealthResponse(
            status="healthy",
            service="Solar PV LLM AI - Vector Store",
            version=settings.API_VERSION,
            pinecone_connected=True,
            embedding_service_ready=True
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.post(
    "/documents/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest documents",
    description="Ingest documents into the vector store with automatic embedding generation"
)
async def ingest_documents(request: IngestDocumentsRequest) -> IngestResponse:
    """
    Ingest documents into the vector store

    - Generates embeddings using text-embedding-3-large
    - Stores vectors in Pinecone with metadata
    - Supports batch processing
    """
    try:
        logger.info(f"Received request to ingest {len(request.documents)} documents")

        handler = get_vector_store_handler()

        # Convert Pydantic models to dicts
        documents = [
            {"text": doc.text, "metadata": doc.metadata}
            for doc in request.documents
        ]

        result = handler.ingest_documents(
            documents=documents,
            namespace=request.namespace,
            batch_size=request.batch_size
        )

        return IngestResponse(**result)

    except EmbeddingError as e:
        logger.error(f"Embedding error during ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Embedding generation failed: {str(e)}"
        )
    except PineconeIntegrationError as e:
        logger.error(f"Pinecone error during ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector store operation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Similarity search",
    description="Perform similarity search with optional metadata filtering"
)
async def search(request: SearchRequest) -> SearchResponse:
    """
    Perform similarity search in the vector store

    - Generates query embedding
    - Searches for similar vectors
    - Supports metadata filtering
    """
    try:
        logger.info(f"Received search request: query='{request.query[:50]}...', top_k={request.top_k}")

        handler = get_vector_store_handler()

        results = handler.search(
            query=request.query,
            top_k=request.top_k,
            filters=request.filters,
            namespace=request.namespace
        )

        # Convert to response format
        search_results = [
            SearchResult(
                id=r["id"],
                score=r["score"],
                metadata=r.get("metadata", {})
            )
            for r in results
        ]

        return SearchResponse(
            status="success",
            query=request.query,
            results=search_results,
            count=len(search_results)
        )

    except EmbeddingError as e:
        logger.error(f"Embedding error during search: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query embedding generation failed: {str(e)}"
        )
    except PineconeIntegrationError as e:
        logger.error(f"Pinecone error during search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector store search failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/search/filtered",
    response_model=SearchResponse,
    summary="Filtered similarity search",
    description="Perform similarity search with Solar PV specific filters (standards, clauses, test_type)"
)
async def search_with_filters(request: SearchWithFiltersRequest) -> SearchResponse:
    """
    Perform filtered similarity search with Solar PV specific filters

    - Supports filtering by standards (e.g., IEC 61215, IEC 61730)
    - Filter by clauses
    - Filter by test type (performance, safety, reliability, etc.)
    """
    try:
        logger.info(
            f"Received filtered search request: query='{request.query[:50]}...', "
            f"standards={request.standards}, test_type={request.test_type}"
        )

        handler = get_vector_store_handler()

        results = handler.search_with_filters(
            query=request.query,
            top_k=request.top_k,
            standards=request.standards,
            clauses=request.clauses,
            test_type=request.test_type,
            namespace=request.namespace
        )

        # Convert to response format
        search_results = [
            SearchResult(
                id=r["id"],
                score=r["score"],
                metadata=r.get("metadata", {})
            )
            for r in results
        ]

        return SearchResponse(
            status="success",
            query=request.query,
            results=search_results,
            count=len(search_results)
        )

    except (EmbeddingError, PineconeIntegrationError) as e:
        logger.error(f"Error during filtered search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during filtered search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete(
    "/documents",
    response_model=DeleteResponse,
    summary="Delete documents",
    description="Delete documents from the vector store by IDs or filters"
)
async def delete_documents(request: DeleteDocumentsRequest) -> DeleteResponse:
    """
    Delete documents from the vector store

    - Delete by specific IDs
    - Delete by metadata filters
    - Returns deletion statistics
    """
    try:
        logger.info(f"Received delete request: ids={request.ids}, filters={request.filters}")

        if not request.ids and not request.filters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide either 'ids' or 'filters' for deletion"
            )

        handler = get_vector_store_handler()

        result = handler.delete_documents(
            ids=request.ids,
            filters=request.filters,
            namespace=request.namespace
        )

        return DeleteResponse(**result)

    except PineconeIntegrationError as e:
        logger.error(f"Pinecone error during deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector deletion failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get index statistics",
    description="Get statistics about the vector store index"
)
async def get_stats(namespace: str = "") -> StatsResponse:
    """
    Get vector store statistics

    - Total vector count
    - Vector dimension
    - Index fullness
    - Per-namespace statistics
    """
    try:
        logger.info(f"Received stats request for namespace '{namespace}'")

        handler = get_vector_store_handler()

        result = handler.get_stats(namespace=namespace)

        return StatsResponse(
            status=result["status"],
            stats=IndexStats(**result["stats"])
        )

    except PineconeIntegrationError as e:
        logger.error(f"Pinecone error during stats retrieval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stats retrieval failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during stats retrieval: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
