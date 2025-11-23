"""
Query and RAG API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.database.connection import get_db
from backend.models.schemas import QueryCreate, QueryWithResponse, VectorSearchRequest, VectorSearchResult
from backend.models.database import Query, QueryResponse, RetrievedDocument, DocumentChunk
from backend.services.rag_service import RAGService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryWithResponse)
def submit_query(
    query_data: QueryCreate,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Submit a query and get AI-generated response using RAG

    - **query_text**: The user's question
    - **session_id**: Optional session ID for conversation tracking

    Returns response with:
    - Generated answer
    - Retrieved source documents
    - Citations
    - Confidence score
    """
    logger.info(f"Processing query: {query_data.query_text[:100]}...")

    try:
        # Create query record
        query = Query(
            user_id=user_id,
            query_text=query_data.query_text,
            session_id=query_data.session_id
        )
        db.add(query)
        db.commit()
        db.refresh(query)

        # Process with RAG service
        rag_service = RAGService()
        rag_result = rag_service.query(
            query_text=query_data.query_text,
            include_citations=True
        )

        # Create response record
        response = QueryResponse(
            query_id=query.id,
            response_text=rag_result["response"],
            model_version=rag_result["metadata"]["model_version"],
            confidence_score=rag_result["confidence"],
            latency_ms=rag_result["metadata"]["latency_ms"],
            token_count=rag_result["metadata"]["tokens"]
        )
        db.add(response)
        db.commit()
        db.refresh(response)

        # Store retrieved documents
        for i, doc in enumerate(rag_result["retrieved_documents"]):
            # Find the document chunk
            chunk = db.query(DocumentChunk).filter(
                DocumentChunk.embedding_id == doc["id"]
            ).first()

            if chunk:
                retrieved = RetrievedDocument(
                    query_id=query.id,
                    chunk_id=chunk.id,
                    relevance_score=doc["relevance_score"],
                    rank=i + 1,
                    was_used=True
                )
                db.add(retrieved)

        db.commit()

        # Build response
        result = QueryWithResponse(
            id=query.id,
            query_text=query.query_text,
            session_id=query.session_id,
            created_at=query.created_at,
            response={
                "id": response.id,
                "query_id": query.id,
                "response_text": response.response_text,
                "model_version": response.model_version,
                "confidence_score": response.confidence_score,
                "latency_ms": response.latency_ms,
                "token_count": response.token_count,
                "cost_estimate": response.cost_estimate,
                "created_at": response.created_at
            },
            retrieved_documents=rag_result["retrieved_documents"]
        )

        logger.info(
            f"Query processed: id={query.id}, confidence={response.confidence_score}, "
            f"latency={response.latency_ms}ms"
        )

        return result

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@router.get("/{query_id}", response_model=QueryWithResponse)
def get_query(query_id: int, db: Session = Depends(get_db)):
    """Get query and response by ID"""
    query = db.query(Query).filter(Query.id == query_id).first()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query {query_id} not found"
        )

    response = db.query(QueryResponse).filter(
        QueryResponse.query_id == query_id
    ).first()

    # Get retrieved documents
    retrieved_docs = []
    if response:
        docs = db.query(RetrievedDocument).filter(
            RetrievedDocument.query_id == query_id
        ).order_by(RetrievedDocument.rank).all()

        for doc in docs:
            chunk = db.query(DocumentChunk).filter(
                DocumentChunk.id == doc.chunk_id
            ).first()

            if chunk:
                retrieved_docs.append({
                    "id": chunk.embedding_id,
                    "content": chunk.content,
                    "relevance_score": doc.relevance_score,
                    "rank": doc.rank
                })

    result = QueryWithResponse(
        id=query.id,
        query_text=query.query_text,
        session_id=query.session_id,
        created_at=query.created_at,
        response={
            "id": response.id,
            "query_id": query.id,
            "response_text": response.response_text,
            "model_version": response.model_version,
            "confidence_score": response.confidence_score,
            "latency_ms": response.latency_ms,
            "token_count": response.token_count,
            "cost_estimate": response.cost_estimate,
            "created_at": response.created_at
        } if response else None,
        retrieved_documents=retrieved_docs
    )

    return result


@router.post("/search", response_model=list)
def search_knowledge_base(
    search_request: VectorSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search the knowledge base directly (without LLM generation)

    - **query_text**: Search query
    - **top_k**: Number of results to return
    - **similarity_threshold**: Minimum similarity score

    Returns list of relevant document chunks
    """
    try:
        rag_service = RAGService()

        # Generate embedding
        query_embedding = rag_service.llm.generate_embedding(search_request.query_text)

        # Search vector store
        results = rag_service.vector_store.search(
            query_embedding=query_embedding,
            top_k=search_request.top_k,
            similarity_threshold=search_request.similarity_threshold
        )

        return results

    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search knowledge base: {str(e)}"
        )


@router.get("/session/{session_id}")
def get_session_queries(
    session_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get all queries for a session

    - **session_id**: Session identifier
    - **limit**: Maximum number of queries to return
    """
    queries = db.query(Query).filter(
        Query.session_id == session_id
    ).order_by(Query.created_at.desc()).limit(limit).all()

    return {
        "session_id": session_id,
        "count": len(queries),
        "queries": [
            {
                "id": q.id,
                "query_text": q.query_text,
                "created_at": q.created_at
            }
            for q in queries
        ]
    }
