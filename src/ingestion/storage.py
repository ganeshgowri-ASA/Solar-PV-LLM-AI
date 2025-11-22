"""Storage utilities for processed documents."""

import json
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from .models import ProcessedDocument, Chunk

logger = logging.getLogger(__name__)


class DocumentStorage:
    """Handles storage and retrieval of processed documents."""

    def __init__(self, output_dir: str = "data/output", pretty_print: bool = True):
        """Initialize document storage.

        Args:
            output_dir: Output directory for saved documents
            pretty_print: Whether to pretty-print JSON output
        """
        self.output_dir = Path(output_dir)
        self.pretty_print = pretty_print

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        document: ProcessedDocument,
        filename: Optional[str] = None,
        format: str = "json",
    ) -> Path:
        """Save processed document to disk.

        Args:
            document: ProcessedDocument to save
            filename: Optional custom filename (without extension)
            format: Output format ('json' or 'jsonl')

        Returns:
            Path to saved file
        """
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            doc_id = document.document_id[:8]
            standard_id = document.metadata.standard_id or "unknown"
            standard_id = standard_id.replace(" ", "_").replace("/", "-")
            filename = f"{standard_id}_{doc_id}_{timestamp}"

        if format == "json":
            filepath = self.output_dir / f"{filename}.json"
            self._save_json(document, filepath)
        elif format == "jsonl":
            filepath = self.output_dir / f"{filename}.jsonl"
            self._save_jsonl(document, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Saved document to {filepath}")
        return filepath

    def _save_json(self, document: ProcessedDocument, filepath: Path) -> None:
        """Save document as single JSON file.

        Args:
            document: Document to save
            filepath: Output file path
        """
        # Convert to dict
        doc_dict = document.dict()

        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            if self.pretty_print:
                json.dump(doc_dict, f, indent=2, ensure_ascii=False, default=str)
            else:
                json.dump(doc_dict, f, ensure_ascii=False, default=str)

    def _save_jsonl(self, document: ProcessedDocument, filepath: Path) -> None:
        """Save document as JSONL (one chunk per line).

        Args:
            document: Document to save
            filepath: Output file path
        """
        with open(filepath, "w", encoding="utf-8") as f:
            # Write metadata line
            metadata_line = {
                "type": "metadata",
                "document_id": document.document_id,
                "metadata": document.metadata.dict(),
                "processing_stats": document.processing_stats,
                "processed_at": str(document.processed_at),
            }
            f.write(json.dumps(metadata_line, ensure_ascii=False, default=str) + "\n")

            # Write chunk lines
            for chunk in document.chunks:
                chunk_line = {
                    "type": "chunk",
                    "document_id": document.document_id,
                    **chunk.dict(),
                }
                f.write(json.dumps(chunk_line, ensure_ascii=False, default=str) + "\n")

    def load(self, filepath: str) -> ProcessedDocument:
        """Load processed document from disk.

        Args:
            filepath: Path to saved document

        Returns:
            ProcessedDocument object
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Document not found: {filepath}")

        if filepath.suffix == ".json":
            return self._load_json(filepath)
        elif filepath.suffix == ".jsonl":
            return self._load_jsonl(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

    def _load_json(self, filepath: Path) -> ProcessedDocument:
        """Load document from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            ProcessedDocument object
        """
        with open(filepath, "r", encoding="utf-8") as f:
            doc_dict = json.load(f)

        return ProcessedDocument(**doc_dict)

    def _load_jsonl(self, filepath: Path) -> ProcessedDocument:
        """Load document from JSONL file.

        Args:
            filepath: Path to JSONL file

        Returns:
            ProcessedDocument object
        """
        metadata_dict = None
        chunks = []

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line_data = json.loads(line)

                if line_data.get("type") == "metadata":
                    metadata_dict = line_data
                elif line_data.get("type") == "chunk":
                    # Remove type and document_id fields
                    line_data.pop("type")
                    line_data.pop("document_id", None)
                    chunks.append(Chunk(**line_data))

        if not metadata_dict:
            raise ValueError("No metadata found in JSONL file")

        # Reconstruct ProcessedDocument
        return ProcessedDocument(
            document_id=metadata_dict["document_id"],
            metadata=metadata_dict["metadata"],
            chunks=chunks,
            processing_stats=metadata_dict.get("processing_stats", {}),
            processed_at=metadata_dict.get("processed_at"),
        )

    def list_documents(self, pattern: str = "*.json") -> List[Path]:
        """List all saved documents.

        Args:
            pattern: Glob pattern for files

        Returns:
            List of file paths
        """
        return sorted(self.output_dir.glob(pattern))

    def export_chunks_only(
        self, document: ProcessedDocument, filename: Optional[str] = None
    ) -> Path:
        """Export only chunks (useful for vector databases).

        Args:
            document: Document to export
            filename: Optional custom filename

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"chunks_{document.document_id[:8]}_{timestamp}.jsonl"

        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            for chunk in document.chunks:
                # Create simplified chunk record
                chunk_record = {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "metadata": {
                        "document_id": document.document_id,
                        "standard_id": document.metadata.standard_id,
                        "chunk_index": chunk.chunk_index,
                        "clause_number": (
                            chunk.clause_info.clause_number if chunk.clause_info else None
                        ),
                        "clause_title": (
                            chunk.clause_info.title if chunk.clause_info else None
                        ),
                        "page_numbers": chunk.page_numbers,
                    },
                    "qa_pairs": [qa.dict() for qa in chunk.qa_pairs],
                }

                f.write(json.dumps(chunk_record, ensure_ascii=False, default=str) + "\n")

        logger.info(f"Exported {len(document.chunks)} chunks to {filepath}")
        return filepath

    def export_qa_pairs(
        self, document: ProcessedDocument, filename: Optional[str] = None
    ) -> Path:
        """Export only Q&A pairs (useful for training data).

        Args:
            document: Document to export
            filename: Optional custom filename

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"qa_pairs_{document.document_id[:8]}_{timestamp}.jsonl"

        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            for chunk in document.chunks:
                for qa in chunk.qa_pairs:
                    qa_record = {
                        "question": qa.question,
                        "answer": qa.answer,
                        "question_type": qa.question_type,
                        "keywords": qa.keywords,
                        "source": {
                            "document_id": document.document_id,
                            "standard_id": document.metadata.standard_id,
                            "chunk_id": chunk.chunk_id,
                            "clause_number": (
                                chunk.clause_info.clause_number if chunk.clause_info else None
                            ),
                        },
                    }

                    f.write(json.dumps(qa_record, ensure_ascii=False, default=str) + "\n")

        total_qa = sum(len(chunk.qa_pairs) for chunk in document.chunks)
        logger.info(f"Exported {total_qa} Q&A pairs to {filepath}")
        return filepath

    def get_statistics(self) -> dict:
        """Get statistics about stored documents.

        Returns:
            Dictionary with storage statistics
        """
        json_files = list(self.output_dir.glob("*.json"))
        jsonl_files = list(self.output_dir.glob("*.jsonl"))

        total_size = sum(f.stat().st_size for f in json_files + jsonl_files)

        return {
            "output_dir": str(self.output_dir),
            "json_documents": len(json_files),
            "jsonl_documents": len(jsonl_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
