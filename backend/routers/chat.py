"""Chat router for Solar PV AI assistant."""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import json
import asyncio

from ..models.schemas import ChatRequest, ChatResponse, ExpertiseLevel
from ..services.llm_service import llm_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """
    Send a query to the Solar PV AI assistant.

    Args:
        request: Chat request with query and options

    Returns:
        AI-generated response with citations
    """
    try:
        response, citations, conv_id, confidence, follow_ups = await llm_service.generate_response(
            query=request.query,
            expertise_level=request.expertise_level,
            conversation_id=request.conversation_id,
            include_citations=request.include_citations
        )

        return ChatResponse(
            response=response,
            citations=citations,
            conversation_id=conv_id,
            expertise_level=request.expertise_level,
            confidence_score=confidence,
            follow_up_questions=follow_ups
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/query/stream")
async def chat_query_stream(request: ChatRequest):
    """
    Stream a response from the Solar PV AI assistant.

    Args:
        request: Chat request with query and options

    Returns:
        Streaming response with tokens
    """
    async def generate():
        try:
            async for token in llm_service.stream_response(
                query=request.query,
                expertise_level=request.expertise_level,
                conversation_id=request.conversation_id
            ):
                yield f"data: {json.dumps({'token': token})}\n\n"
                await asyncio.sleep(0.02)  # Simulate streaming delay
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.websocket("/ws/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint for real-time chat.

    Args:
        websocket: WebSocket connection
        conversation_id: Unique conversation ID
    """
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            query = data.get("query", "")
            expertise_level = ExpertiseLevel(data.get("expertise_level", "intermediate"))

            if not query:
                await websocket.send_json({"error": "Query is required"})
                continue

            # Send acknowledgment
            await websocket.send_json({
                "type": "start",
                "conversation_id": conversation_id
            })

            # Stream response
            full_response = ""
            async for token in llm_service.stream_response(
                query=query,
                expertise_level=expertise_level,
                conversation_id=conversation_id
            ):
                full_response += token
                await websocket.send_json({
                    "type": "token",
                    "token": token
                })
                await asyncio.sleep(0.02)

            # Send completion with full response
            await websocket.send_json({
                "type": "complete",
                "response": full_response,
                "conversation_id": conversation_id
            })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass


@router.get("/health")
async def chat_health():
    """Health check for chat service."""
    return {"status": "healthy", "service": "chat"}
