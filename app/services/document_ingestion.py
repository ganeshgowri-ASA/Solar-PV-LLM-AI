"""
Document Ingestion Service for processing and indexing documents.
Handles PDF, DOCX, and TXT files with chunking and vector storage.
"""
import io
import base64
import hashlib
import uuid
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
import asyncio

from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from loguru import logger

from app.core.config import settings
from app.services.rag_engine import rag_engine
from app.models.schemas import DocumentFormat, DocumentMetadata, IngestionStatus


class DocumentProcessor:
    """Document processing and ingestion service."""

    def __init__(self):
        """Initialize document processor."""
        self.upload_dir = Path(settings.DOCUMENT_UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.ingestion_tasks: Dict[str, IngestionStatus] = {}
        logger.info("Document Processor initialized")

    def generate_document_id(self, content: bytes) -> str:
        """
        Generate unique document ID from content hash.

        Args:
            content: Document content bytes

        Returns:
            Unique document ID
        """
        content_hash = hashlib.sha256(content).hexdigest()[:16]
        return f"doc_{content_hash}_{uuid.uuid4().hex[:8]}"

    def decode_document(self, document_base64: str) -> bytes:
        """
        Decode base64 document.

        Args:
            document_base64: Base64 encoded document

        Returns:
            Document bytes
        """
        try:
            # Remove data URL prefix if present
            if ',' in document_base64:
                document_base64 = document_base64.split(',')[1]

            document_bytes = base64.b64decode(document_base64)
            return document_bytes

        except Exception as e:
            logger.error(f"Error decoding document: {e}")
            raise ValueError(f"Invalid document data: {e}")

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """
        Extract text from PDF file.

        Args:
            file_bytes: PDF file bytes

        Returns:
            Extracted text
        """
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)

            text_parts = []
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                text_parts.append(f"[Page {page_num}]\n{text}\n")

            full_text = "\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from PDF ({len(reader.pages)} pages)")
            return full_text

        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise ValueError(f"Failed to process PDF: {e}")

    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        """
        Extract text from DOCX file.

        Args:
            file_bytes: DOCX file bytes

        Returns:
            Extracted text
        """
        try:
            docx_file = io.BytesIO(file_bytes)
            doc = DocxDocument(docx_file)

            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)

            full_text = "\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from DOCX")
            return full_text

        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            raise ValueError(f"Failed to process DOCX: {e}")

    def extract_text(self, file_bytes: bytes, format: DocumentFormat) -> str:
        """
        Extract text from document.

        Args:
            file_bytes: Document bytes
            format: Document format

        Returns:
            Extracted text
        """
        if format == DocumentFormat.PDF:
            return self.extract_text_from_pdf(file_bytes)
        elif format == DocumentFormat.DOCX:
            return self.extract_text_from_docx(file_bytes)
        elif format == DocumentFormat.TXT:
            return file_bytes.decode('utf-8', errors='ignore')
        else:
            raise ValueError(f"Unsupported format: {format}")

    def chunk_text(
        self,
        text: str,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Input text
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if chunk_size is None:
            chunk_size = settings.CHUNK_SIZE
        if chunk_overlap is None:
            chunk_overlap = settings.CHUNK_OVERLAP

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)

                if break_point > chunk_size // 2:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - chunk_overlap

        logger.info(f"Created {len(chunks)} chunks from {len(text)} characters")
        return chunks

    async def ingest_document(
        self,
        document_bytes: bytes,
        filename: str,
        format: DocumentFormat,
        metadata: Optional[Dict] = None
    ) -> Tuple[str, int]:
        """
        Ingest document into vector database.

        Args:
            document_bytes: Document content
            filename: Original filename
            format: Document format
            metadata: Additional metadata

        Returns:
            Tuple of (document_id, chunk_count)
        """
        # Generate document ID
        document_id = self.generate_document_id(document_bytes)

        # Initialize ingestion status
        self.ingestion_tasks[document_id] = IngestionStatus(
            document_id=document_id,
            status="processing",
            progress=0,
            chunks_processed=0,
            total_chunks=0
        )

        try:
            # Extract text
            logger.info(f"Processing document: {filename}")
            text = self.extract_text(document_bytes, format)

            # Chunk text
            chunks = self.chunk_text(text)
            total_chunks = len(chunks)

            self.ingestion_tasks[document_id].total_chunks = total_chunks
            self.ingestion_tasks[document_id].progress = 25

            # Prepare for vector storage
            chunk_ids = [f"{document_id}_chunk_{i}" for i in range(total_chunks)]

            chunk_metadata = []
            for i, chunk in enumerate(chunks):
                meta = {
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_id": chunk_ids[i],
                    "chunk_index": i,
                    "total_chunks": total_chunks,
                    "format": format.value,
                    "ingestion_timestamp": datetime.utcnow().isoformat(),
                }
                if metadata:
                    meta.update(metadata)

                # Try to extract page number if available
                if "[Page " in chunk:
                    try:
                        page_num = int(chunk.split("[Page ")[1].split("]")[0])
                        meta["page"] = page_num
                        meta["source"] = f"{filename} (Page {page_num})"
                    except:
                        meta["source"] = filename
                else:
                    meta["source"] = filename

                chunk_metadata.append(meta)

            self.ingestion_tasks[document_id].progress = 50

            # Add to vector database
            success = rag_engine.add_documents(
                documents=chunks,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )

            if success:
                self.ingestion_tasks[document_id].status = "completed"
                self.ingestion_tasks[document_id].progress = 100
                self.ingestion_tasks[document_id].chunks_processed = total_chunks
                logger.info(f"Successfully ingested document {document_id} ({total_chunks} chunks)")
            else:
                raise Exception("Failed to add documents to vector database")

            return document_id, total_chunks

        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            self.ingestion_tasks[document_id].status = "failed"
            self.ingestion_tasks[document_id].error_message = str(e)
            raise

    def get_ingestion_status(self, document_id: str) -> Optional[IngestionStatus]:
        """
        Get ingestion status for document.

        Args:
            document_id: Document identifier

        Returns:
            Ingestion status or None
        """
        return self.ingestion_tasks.get(document_id)

    async def stop_ingestion(self, document_id: str) -> bool:
        """
        Stop ongoing document ingestion.

        Args:
            document_id: Document identifier

        Returns:
            Success status
        """
        if document_id in self.ingestion_tasks:
            status = self.ingestion_tasks[document_id]
            if status.status == "processing":
                status.status = "stopped"
                logger.info(f"Stopped ingestion for document {document_id}")
                return True
        return False

    def get_all_statuses(self) -> List[IngestionStatus]:
        """
        Get all ingestion statuses.

        Returns:
            List of all ingestion statuses
        """
        return list(self.ingestion_tasks.values())


# Global document processor instance
document_processor = DocumentProcessor()
