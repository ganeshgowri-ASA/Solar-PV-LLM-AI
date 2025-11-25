"""
Document ingestion control endpoints.
"""
import time
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List
from loguru import logger

from app.models.schemas import (
    DocumentIngestionRequest,
    DocumentIngestionResponse,
    IngestionStatus,
    DocumentFormat
)
from app.services.document_ingestion import document_processor
from app.core.security import verify_api_key

router = APIRouter(prefix="/documents", tags=["Document Ingestion"])


@router.post("/ingest", response_model=DocumentIngestionResponse)
async def ingest_document(
    request: DocumentIngestionRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Ingest document into knowledge base.

    Process and index documents for RAG retrieval.

    **Supported formats:**
    - PDF
    - DOCX (Word)
    - TXT (Plain text)

    **Process:**
    1. Extract text from document
    2. Split into overlapping chunks
    3. Generate embeddings
    4. Store in vector database

    **Input:**
    - document_base64: Base64 encoded document
    - OR document_url: URL to document
    - metadata: Additional metadata (optional)

    **Returns:**
    - document_id: Unique identifier
    - chunks_created: Number of text chunks
    - processing_time: Time taken
    """
    start_time = time.time()

    try:
        if not request.document_base64 and not request.document_url:
            raise HTTPException(
                status_code=400,
                detail="Either document_base64 or document_url must be provided"
            )

        logger.info("Starting document ingestion...")

        # Decode document
        document_bytes = document_processor.decode_document(request.document_base64)

        # Detect format (simplified - in production, use magic bytes)
        # For now, assume PDF
        format = DocumentFormat.PDF
        filename = request.metadata.get("filename", "uploaded_document.pdf")

        # Ingest document
        document_id, chunk_count = await document_processor.ingest_document(
            document_bytes=document_bytes,
            filename=filename,
            format=format,
            metadata=request.metadata
        )

        processing_time = time.time() - start_time

        response = DocumentIngestionResponse(
            document_id=document_id,
            status="completed",
            chunks_created=chunk_count,
            processing_time=round(processing_time, 3)
        )

        logger.info(
            f"Document ingested: {document_id} "
            f"({chunk_count} chunks, {processing_time:.2f}s)"
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=DocumentIngestionResponse)
async def upload_document(
    file: UploadFile = File(...),
    authenticated: bool = Depends(verify_api_key)
):
    """
    Upload and ingest document file.

    Alternative endpoint that accepts file upload.

    **Supported file extensions:**
    - .pdf
    - .docx
    - .txt

    **Returns:**
    - Same as /ingest endpoint
    """
    start_time = time.time()

    try:
        # Get file extension
        filename = file.filename
        extension = filename.split('.')[-1].lower()

        # Map to DocumentFormat
        format_map = {
            'pdf': DocumentFormat.PDF,
            'docx': DocumentFormat.DOCX,
            'txt': DocumentFormat.TXT
        }

        if extension not in format_map:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {extension}"
            )

        format = format_map[extension]

        logger.info(f"Uploading document: {filename} ({format.value})")

        # Read file
        contents = await file.read()

        # Ingest
        document_id, chunk_count = await document_processor.ingest_document(
            document_bytes=contents,
            filename=filename,
            format=format,
            metadata={"original_filename": filename}
        )

        processing_time = time.time() - start_time

        response = DocumentIngestionResponse(
            document_id=document_id,
            status="completed",
            chunks_created=chunk_count,
            processing_time=round(processing_time, 3)
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{document_id}", response_model=IngestionStatus)
async def get_ingestion_status(
    document_id: str,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Get ingestion status for document.

    Check the processing status of an ingested document.

    **Parameters:**
    - document_id: Unique document identifier

    **Returns:**
    - status: pending, processing, completed, failed, stopped
    - progress: Processing progress (0-100)
    - chunks_processed: Number of chunks processed
    - total_chunks: Total number of chunks
    - error_message: Error details if failed
    """
    try:
        status = document_processor.get_ingestion_status(document_id)

        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )

        return status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop/{document_id}")
async def stop_ingestion(
    document_id: str,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Stop ongoing document ingestion.

    Cancel a document processing task in progress.

    **Parameters:**
    - document_id: Document identifier

    **Returns:**
    - success: Boolean indicating if stopped
    """
    try:
        success = await document_processor.stop_ingestion(document_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found or not processing"
            )

        return {
            "document_id": document_id,
            "stopped": True,
            "message": "Ingestion stopped successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=List[IngestionStatus])
async def get_all_statuses(
    authenticated: bool = Depends(verify_api_key)
):
    """
    Get all document ingestion statuses.

    Returns status for all documents that have been processed
    or are currently being processed.

    **Returns:**
    - List of ingestion statuses
    """
    try:
        statuses = document_processor.get_all_statuses()
        return statuses

    except Exception as e:
        logger.error(f"Error getting statuses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collection-stats")
async def get_collection_stats(
    authenticated: bool = Depends(verify_api_key)
):
    """
    Get vector database collection statistics.

    **Returns:**
    - collection_name: Name of the collection
    - document_count: Number of document chunks stored
    - status: Collection health status
    """
    try:
        from app.services.rag_engine import rag_engine

        stats = rag_engine.get_collection_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
