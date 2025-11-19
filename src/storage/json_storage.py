"""
JSON Storage - Store processed chunks with metadata in structured JSON format.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..metadata.schema import ProcessedChunk, DocumentMetadata, ChunkMetadata

logger = logging.getLogger(__name__)


class JSONStorage:
    """
    Store and retrieve processed chunks in JSON format.
    """

    def __init__(self, output_dir: str = "data/processed"):
        """
        Initialize JSON storage.

        Args:
            output_dir: Directory for storing JSON files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_processed_document(
        self,
        chunks: List[ProcessedChunk],
        document_metadata: DocumentMetadata,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Save processed document chunks to JSON.

        Args:
            chunks: List of processed chunks
            document_metadata: Document-level metadata
            output_filename: Optional custom output filename

        Returns:
            Path to saved JSON file
        """
        if not output_filename:
            # Generate filename from document metadata
            safe_name = document_metadata.iec_metadata.standard_id.replace(' ', '_').replace('/', '-')
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{safe_name}_{timestamp}.json"

        output_path = self.output_dir / output_filename

        # Convert to serializable format
        data = {
            "document_metadata": document_metadata.model_dump(mode='json'),
            "chunks": [chunk.model_dump(mode='json') for chunk in chunks],
            "export_timestamp": datetime.utcnow().isoformat(),
            "version": "1.0"
        }

        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(chunks)} chunks to {output_path}")
        return str(output_path)

    def save_chunks_batch(
        self,
        chunks: List[ProcessedChunk],
        batch_name: str
    ) -> str:
        """
        Save a batch of chunks to JSON.

        Args:
            chunks: List of processed chunks
            batch_name: Name for the batch

        Returns:
            Path to saved JSON file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{batch_name}_{timestamp}.json"
        output_path = self.output_dir / output_filename

        data = {
            "batch_name": batch_name,
            "chunks": [chunk.model_dump(mode='json') for chunk in chunks],
            "export_timestamp": datetime.utcnow().isoformat(),
            "chunk_count": len(chunks)
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved batch '{batch_name}' with {len(chunks)} chunks to {output_path}")
        return str(output_path)

    def load_processed_document(self, json_path: str) -> Dict[str, Any]:
        """
        Load processed document from JSON.

        Args:
            json_path: Path to JSON file

        Returns:
            Dictionary with document_metadata and chunks
        """
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert back to Pydantic models
        if 'document_metadata' in data:
            doc_metadata = DocumentMetadata(**data['document_metadata'])
        else:
            doc_metadata = None

        chunks = [ProcessedChunk(**chunk_data) for chunk_data in data['chunks']]

        logger.info(f"Loaded {len(chunks)} chunks from {json_path}")

        return {
            'document_metadata': doc_metadata,
            'chunks': chunks,
            'export_timestamp': data.get('export_timestamp')
        }

    def export_for_retrieval(
        self,
        chunks: List[ProcessedChunk],
        output_filename: str,
        include_embeddings: bool = False
    ) -> str:
        """
        Export chunks in format optimized for retrieval systems.

        Args:
            chunks: List of processed chunks
            output_filename: Output filename
            include_embeddings: Whether to include embeddings

        Returns:
            Path to exported file
        """
        output_path = self.output_dir / output_filename

        # Create retrieval-optimized format
        retrieval_data = []
        for chunk in chunks:
            item = {
                "id": chunk.metadata.chunk_id,
                "text": chunk.text,
                "metadata": {
                    "standard_id": chunk.metadata.document.standard_id,
                    "clause_number": chunk.metadata.clause.clause_number,
                    "clause_title": chunk.metadata.clause.clause_title,
                    "page_numbers": chunk.metadata.page_numbers,
                },
                "qa_pairs": [qa.model_dump(mode='json') for qa in chunk.qa_pairs]
            }

            if include_embeddings and chunk.embeddings:
                item["embeddings"] = chunk.embeddings

            retrieval_data.append(item)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(retrieval_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(retrieval_data)} chunks for retrieval to {output_path}")
        return str(output_path)

    def export_qa_pairs(
        self,
        chunks: List[ProcessedChunk],
        output_filename: str
    ) -> str:
        """
        Export Q&A pairs separately for training or evaluation.

        Args:
            chunks: List of processed chunks
            output_filename: Output filename

        Returns:
            Path to exported file
        """
        output_path = self.output_dir / output_filename

        qa_data = []
        for chunk in chunks:
            for qa in chunk.qa_pairs:
                qa_data.append({
                    **qa.model_dump(mode='json'),
                    "source_metadata": {
                        "standard_id": chunk.metadata.document.standard_id,
                        "clause_number": chunk.metadata.clause.clause_number,
                        "clause_title": chunk.metadata.clause.clause_title,
                    }
                })

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(qa_data)} Q&A pairs to {output_path}")
        return str(output_path)

    def get_statistics(self, json_path: str) -> Dict[str, Any]:
        """
        Get statistics about a processed document.

        Args:
            json_path: Path to JSON file

        Returns:
            Dictionary of statistics
        """
        data = self.load_processed_document(json_path)
        chunks = data['chunks']

        if not chunks:
            return {}

        # Calculate statistics
        total_qa_pairs = sum(len(chunk.qa_pairs) for chunk in chunks)
        chunk_sizes = [len(chunk.text) for chunk in chunks]
        clauses = set(chunk.metadata.clause.clause_number for chunk in chunks)

        return {
            "total_chunks": len(chunks),
            "total_qa_pairs": total_qa_pairs,
            "avg_qa_per_chunk": total_qa_pairs / len(chunks) if chunks else 0,
            "unique_clauses": len(clauses),
            "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "total_characters": sum(chunk_sizes),
        }

    def list_processed_documents(self) -> List[Dict[str, Any]]:
        """
        List all processed documents in storage.

        Returns:
            List of document information
        """
        documents = []

        for json_file in self.output_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                doc_info = {
                    "filename": json_file.name,
                    "path": str(json_file),
                    "chunk_count": len(data.get('chunks', [])),
                    "export_timestamp": data.get('export_timestamp', 'unknown')
                }

                if 'document_metadata' in data:
                    doc_info['standard_id'] = data['document_metadata'].get('iec_metadata', {}).get('standard_id', 'unknown')

                documents.append(doc_info)
            except Exception as e:
                logger.warning(f"Failed to read {json_file}: {e}")
                continue

        return sorted(documents, key=lambda x: x.get('export_timestamp', ''), reverse=True)
