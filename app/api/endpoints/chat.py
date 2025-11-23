"""
Chat endpoint integrating RAG, LLM orchestrator, and citation manager.
"""
import time
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_engine import rag_engine
from app.services.llm_orchestrator import llm_orchestrator
from app.services.citation_manager import citation_manager
from app.core.security import verify_api_key

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Chat endpoint with RAG-enhanced responses.

    This endpoint integrates:
    - RAG engine for context retrieval from knowledge base
    - LLM orchestrator for response generation
    - Citation manager for source attribution

    **Features:**
    - Context-aware responses using retrieved documents
    - Automatic source citation
    - Conversation history support
    - Configurable temperature and max tokens
    - Token usage tracking
    """
    start_time = time.time()

    try:
        logger.info(f"Received chat request: {request.query[:100]}...")

        # Retrieve context if RAG is enabled
        citations = []
        if request.use_rag:
            logger.info("Retrieving context from RAG engine...")
            citations = rag_engine.retrieve_context(
                query=request.query,
                max_results=5
            )

            # Deduplicate and rank citations
            citations = citation_manager.deduplicate_citations(citations)
            citations = citation_manager.rank_citations(citations, request.query)

        # Generate LLM response
        logger.info("Generating LLM response...")
        response_text, tokens_used = llm_orchestrator.generate_response(
            query=request.query,
            citations=citations,
            conversation_history=request.conversation_history,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            use_rag=request.use_rag
        )

        # Calculate processing time
        processing_time = time.time() - start_time

        # Create response
        chat_response = ChatResponse(
            response=response_text,
            citations=citations,
            conversation_id=None,  # Could implement conversation tracking
            tokens_used=tokens_used,
            processing_time=round(processing_time, 3)
        )

        logger.info(
            f"Chat response generated: {tokens_used} tokens, "
            f"{len(citations)} citations, {processing_time:.2f}s"
        )

        return chat_response

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Streaming chat endpoint (future implementation).

    Returns streaming responses for real-time user experience.
    """
    raise HTTPException(
        status_code=501,
        detail="Streaming not yet implemented"
    )
