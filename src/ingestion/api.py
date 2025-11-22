"""Python API wrapper for programmatic access to ingestion pipeline."""

import logging
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

from .models import (
    ProcessedDocument,
    IngestionConfig,
    DocumentMetadata,
    Chunk,
    ClauseInfo,
)
from .pipeline import IngestionPipeline
from .storage import DocumentStorage

logger = logging.getLogger(__name__)


class IECIngestionAPI:
    """High-level Python API for IEC PDF ingestion.

    Example usage:
        >>> from src.ingestion.api import IECIngestionAPI
        >>>
        >>> # Initialize API
        >>> api = IECIngestionAPI()
        >>>
        >>> # Process a single document
        >>> result = api.ingest("path/to/iec_standard.pdf")
        >>> print(f"Created {result.chunk_count} chunks")
        >>>
        >>> # Access processed data
        >>> for chunk in result.chunks:
        >>>     print(chunk.content)
        >>>     for qa in chunk.qa_pairs:
        >>>         print(f"Q: {qa.question}")
        >>>         print(f"A: {qa.answer}")
    """

    def __init__(
        self,
        config: Optional[Union[IngestionConfig, dict, str]] = None,
        log_level: str = "INFO",
    ):
        """Initialize the API.

        Args:
            config: Configuration (IngestionConfig object, dict, or path to YAML file)
            log_level: Logging level
        """
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Load configuration
        if config is None:
            self.config = IngestionConfig()
        elif isinstance(config, IngestionConfig):
            self.config = config
        elif isinstance(config, dict):
            self.config = IngestionConfig(**config)
        elif isinstance(config, str):
            self.config = self._load_config_from_file(config)
        else:
            raise ValueError(f"Unsupported config type: {type(config)}")

        # Initialize pipeline
        self.pipeline = IngestionPipeline(config=self.config)
        self.storage = self.pipeline.storage

        logger.info("IEC Ingestion API initialized")

    def _load_config_from_file(self, config_path: str) -> IngestionConfig:
        """Load config from YAML file.

        Args:
            config_path: Path to config file

        Returns:
            IngestionConfig object
        """
        import yaml

        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        # Flatten nested structure (similar to CLI)
        flat_config = {}

        if "pdf" in config_data:
            flat_config.update({f"pdf_{k}": v for k, v in config_data["pdf"].items()})

        if "chunking" in config_data:
            flat_config.update(config_data["chunking"])

        if "qa_generation" in config_data:
            flat_config.update(
                {
                    f"qa_{k}" if not k.startswith("qa_") else k: v
                    for k, v in config_data["qa_generation"].items()
                    if k not in ["question_types", "system_prompt"]
                }
            )

        if "output" in config_data:
            flat_config.update(config_data["output"])

        return IngestionConfig(**flat_config)

    def ingest(
        self,
        pdf_path: str,
        save: bool = True,
        output_filename: Optional[str] = None,
        skip_qa: bool = False,
    ) -> ProcessedDocument:
        """Ingest a single PDF document.

        Args:
            pdf_path: Path to PDF file
            save: Whether to save results to disk
            output_filename: Optional custom output filename
            skip_qa: Skip Q&A generation

        Returns:
            ProcessedDocument object
        """
        if save:
            doc, _ = self.pipeline.process_and_save(
                pdf_path=pdf_path,
                output_filename=output_filename,
                skip_qa=skip_qa,
            )
        else:
            doc = self.pipeline.process(
                pdf_path=pdf_path,
                output_filename=output_filename,
                skip_qa=skip_qa,
            )

        return doc

    def ingest_batch(
        self,
        pdf_paths: List[str],
        skip_qa: bool = False,
    ) -> List[ProcessedDocument]:
        """Ingest multiple PDF documents.

        Args:
            pdf_paths: List of PDF file paths
            skip_qa: Skip Q&A generation

        Returns:
            List of ProcessedDocument objects
        """
        results = self.pipeline.process_batch(pdf_paths, skip_qa=skip_qa)
        return [doc for _, doc, _ in results if doc is not None]

    def load(self, filepath: str) -> ProcessedDocument:
        """Load a previously processed document.

        Args:
            filepath: Path to saved document

        Returns:
            ProcessedDocument object
        """
        return self.storage.load(filepath)

    def save(
        self,
        document: ProcessedDocument,
        filename: Optional[str] = None,
        format: str = "json",
    ) -> Path:
        """Save a processed document.

        Args:
            document: Document to save
            filename: Optional custom filename
            format: Output format ('json' or 'jsonl')

        Returns:
            Path to saved file
        """
        return self.storage.save(document, filename=filename, format=format)

    def validate(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Validate a processed document.

        Args:
            document: Document to validate

        Returns:
            Validation results dictionary
        """
        return self.pipeline.validate(document)

    def export_chunks(
        self,
        document: ProcessedDocument,
        filename: Optional[str] = None,
    ) -> Path:
        """Export only chunks (useful for vector databases).

        Args:
            document: Document to export
            filename: Optional custom filename

        Returns:
            Path to exported file
        """
        return self.storage.export_chunks_only(document, filename=filename)

    def export_qa_pairs(
        self,
        document: ProcessedDocument,
        filename: Optional[str] = None,
    ) -> Path:
        """Export only Q&A pairs (useful for training data).

        Args:
            document: Document to export
            filename: Optional custom filename

        Returns:
            Path to exported file
        """
        return self.storage.export_qa_pairs(document, filename=filename)

    def list_documents(self, pattern: str = "*.json") -> List[Path]:
        """List all saved documents.

        Args:
            pattern: Glob pattern for files

        Returns:
            List of file paths
        """
        return self.storage.list_documents(pattern=pattern)

    def get_statistics(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Get comprehensive document statistics.

        Args:
            document: Document to analyze

        Returns:
            Statistics dictionary
        """
        return document.get_statistics()

    def search_chunks(
        self,
        document: ProcessedDocument,
        query: str,
        top_k: int = 5,
    ) -> List[Chunk]:
        """Search for relevant chunks (simple text matching).

        Args:
            document: Document to search
            query: Search query
            top_k: Number of results to return

        Returns:
            List of matching chunks
        """
        query_lower = query.lower()
        scored_chunks = []

        for chunk in document.chunks:
            content_lower = chunk.content.lower()
            # Simple scoring based on query term frequency
            score = sum(content_lower.count(term) for term in query_lower.split())

            if score > 0:
                scored_chunks.append((score, chunk))

        # Sort by score and return top k
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[:top_k]]

    def get_chunks_by_clause(
        self,
        document: ProcessedDocument,
        clause_number: str,
    ) -> List[Chunk]:
        """Get all chunks for a specific clause.

        Args:
            document: Document to search
            clause_number: Clause number (e.g., '4.2.1')

        Returns:
            List of chunks in the clause
        """
        return document.get_chunks_by_clause(clause_number)

    def get_clause_hierarchy(
        self,
        document: ProcessedDocument,
    ) -> Dict[str, Any]:
        """Get hierarchical structure of clauses.

        Args:
            document: Document to analyze

        Returns:
            Nested dictionary representing clause hierarchy
        """
        hierarchy = {}

        for clause in document.clauses:
            # Build path to this clause
            parts = clause.clause_number.split(".")
            current = hierarchy

            for i, part in enumerate(parts):
                clause_num = ".".join(parts[: i + 1])

                if clause_num not in current:
                    current[clause_num] = {
                        "title": clause.title if clause_num == clause.clause_number else None,
                        "level": i + 1,
                        "children": {},
                    }

                if i < len(parts) - 1:
                    current = current[clause_num]["children"]

        return hierarchy

    def update_config(self, **kwargs) -> None:
        """Update configuration parameters.

        Args:
            **kwargs: Configuration parameters to update
        """
        self.pipeline.update_config(**kwargs)
        self.config = self.pipeline.get_config()

    def get_config(self) -> IngestionConfig:
        """Get current configuration.

        Returns:
            IngestionConfig object
        """
        return self.config


# Convenience functions for quick access
def quick_ingest(
    pdf_path: str,
    chunk_size: int = 1000,
    skip_qa: bool = False,
) -> ProcessedDocument:
    """Quick ingestion with default settings.

    Args:
        pdf_path: Path to PDF file
        chunk_size: Chunk size in characters
        skip_qa: Skip Q&A generation

    Returns:
        ProcessedDocument object
    """
    config = IngestionConfig(chunk_size=chunk_size, qa_enabled=not skip_qa)
    api = IECIngestionAPI(config=config)
    return api.ingest(pdf_path, save=True, skip_qa=skip_qa)


def load_document(filepath: str) -> ProcessedDocument:
    """Load a processed document.

    Args:
        filepath: Path to saved document

    Returns:
        ProcessedDocument object
    """
    api = IECIngestionAPI()
    return api.load(filepath)
