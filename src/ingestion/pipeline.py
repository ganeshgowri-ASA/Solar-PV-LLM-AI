"""Main ingestion pipeline orchestrating all components."""

import logging
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .models import ProcessedDocument, IngestionConfig
from .pdf_loader import IECPDFLoader
from .metadata_extractor import MetadataExtractor
from .chunker import ClauseAwareChunker
from .qa_generator import QAGenerator
from .storage import DocumentStorage

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """End-to-end pipeline for IEC PDF ingestion."""

    def __init__(self, config: Optional[IngestionConfig] = None):
        """Initialize the ingestion pipeline.

        Args:
            config: Optional configuration object
        """
        self.config = config or IngestionConfig()

        # Initialize components
        self.pdf_loader = IECPDFLoader(
            preserve_layout=self.config.pdf_preserve_layout,
            extract_tables=self.config.pdf_extract_tables,
        )

        self.metadata_extractor = MetadataExtractor()

        self.chunker = ClauseAwareChunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            min_chunk_size=self.config.min_chunk_size,
            max_chunk_size=self.config.max_chunk_size,
            clause_aware=self.config.clause_aware,
        )

        self.qa_generator = None
        if self.config.qa_enabled:
            try:
                self.qa_generator = QAGenerator(
                    provider=self.config.qa_provider,
                    model=self.config.qa_model,
                    temperature=self.config.qa_temperature,
                    max_questions_per_chunk=self.config.max_questions_per_chunk,
                )
            except Exception as e:
                logger.warning(f"Could not initialize Q&A generator: {e}")

        self.storage = DocumentStorage(
            output_dir=self.config.output_dir,
            pretty_print=self.config.pretty_print,
        )

        logger.info("Ingestion pipeline initialized")

    def process(
        self,
        pdf_path: str,
        output_filename: Optional[str] = None,
        skip_qa: bool = False,
    ) -> ProcessedDocument:
        """Process a single PDF document.

        Args:
            pdf_path: Path to PDF file
            output_filename: Optional custom output filename
            skip_qa: Skip Q&A generation even if enabled

        Returns:
            ProcessedDocument object
        """
        start_time = datetime.utcnow()
        logger.info(f"Starting ingestion of {pdf_path}")

        # Step 1: Load PDF
        logger.info("Step 1/5: Loading PDF...")
        full_text, clauses, basic_metadata = self.pdf_loader.load(pdf_path)

        # Step 2: Extract metadata
        logger.info("Step 2/5: Extracting metadata...")
        metadata = self.metadata_extractor.extract(full_text, basic_metadata)

        # Also try to extract from filename
        filename_metadata = self.metadata_extractor.extract_from_filename(pdf_path)
        if not metadata.standard_id and filename_metadata.standard_id:
            metadata.standard_id = filename_metadata.standard_id
        if not metadata.year and filename_metadata.year:
            metadata.year = filename_metadata.year
        if not metadata.edition and filename_metadata.edition:
            metadata.edition = filename_metadata.edition

        # Step 3: Chunk document
        logger.info("Step 3/5: Chunking document...")
        chunks = self.chunker.chunk_document(text=full_text, clauses=clauses, metadata=metadata)

        # Step 4: Generate Q&A pairs
        if self.qa_generator and not skip_qa and self.config.qa_enabled:
            logger.info("Step 4/5: Generating Q&A pairs...")
            try:
                self.qa_generator.generate_batch(chunks, metadata)
            except Exception as e:
                logger.error(f"Error generating Q&A pairs: {e}")
        else:
            logger.info("Step 4/5: Skipping Q&A generation")

        # Step 5: Create ProcessedDocument
        logger.info("Step 5/5: Creating processed document...")
        document_id = str(uuid.uuid4())

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        processed_doc = ProcessedDocument(
            document_id=document_id,
            metadata=metadata,
            chunks=chunks,
            clauses=clauses,
            processing_stats={
                "processing_time_seconds": processing_time,
                "total_chunks": len(chunks),
                "total_clauses": len(clauses),
                "total_characters": len(full_text),
                "total_words": len(full_text.split()),
                "qa_pairs_generated": sum(len(chunk.qa_pairs) for chunk in chunks),
                "config": self.config.dict(),
            },
        )

        logger.info(
            f"Ingestion complete: {len(chunks)} chunks, "
            f"{len(clauses)} clauses, "
            f"{processed_doc.get_total_qa_pairs()} Q&A pairs, "
            f"{processing_time:.2f}s"
        )

        return processed_doc

    def process_and_save(
        self,
        pdf_path: str,
        output_filename: Optional[str] = None,
        skip_qa: bool = False,
    ) -> tuple[ProcessedDocument, Path]:
        """Process PDF and save results.

        Args:
            pdf_path: Path to PDF file
            output_filename: Optional custom output filename
            skip_qa: Skip Q&A generation

        Returns:
            Tuple of (ProcessedDocument, output_path)
        """
        # Process document
        processed_doc = self.process(pdf_path, output_filename, skip_qa)

        # Save to disk
        output_path = self.storage.save(
            processed_doc,
            filename=output_filename,
            format=self.config.output_format,
        )

        # Export additional formats if requested
        if self.config.include_qa and processed_doc.get_total_qa_pairs() > 0:
            self.storage.export_qa_pairs(processed_doc)

        logger.info(f"Results saved to {output_path}")

        return processed_doc, output_path

    def validate(self, document: ProcessedDocument) -> Dict[str, Any]:
        """Validate processed document.

        Args:
            document: Document to validate

        Returns:
            Validation results dictionary
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "stats": {},
        }

        # Check chunk count
        if len(document.chunks) == 0:
            results["valid"] = False
            results["errors"].append("No chunks generated")
        else:
            results["stats"]["chunk_count"] = len(document.chunks)

        # Check metadata completeness
        metadata_valid, metadata_issues = self.metadata_extractor.validate_metadata(
            document.metadata
        )
        if not metadata_valid:
            results["warnings"].extend(metadata_issues)

        # Check chunk sizes
        small_chunks = [c for c in document.chunks if c.char_count < self.config.min_chunk_size]
        if small_chunks:
            results["warnings"].append(
                f"{len(small_chunks)} chunks smaller than minimum size"
            )

        large_chunks = [c for c in document.chunks if c.char_count > self.config.max_chunk_size]
        if large_chunks:
            results["warnings"].append(
                f"{len(large_chunks)} chunks larger than maximum size"
            )

        # Check clause coverage
        chunks_with_clauses = [c for c in document.chunks if c.clause_info]
        clause_coverage = (
            len(chunks_with_clauses) / len(document.chunks) * 100 if document.chunks else 0
        )
        results["stats"]["clause_coverage_percent"] = round(clause_coverage, 2)

        if clause_coverage < 50 and document.clauses:
            results["warnings"].append(
                f"Low clause coverage: {clause_coverage:.1f}% of chunks have clause info"
            )

        # Check Q&A generation
        if self.config.qa_enabled:
            chunks_with_qa = [c for c in document.chunks if c.qa_pairs]
            qa_coverage = (
                len(chunks_with_qa) / len(document.chunks) * 100 if document.chunks else 0
            )
            results["stats"]["qa_coverage_percent"] = round(qa_coverage, 2)
            results["stats"]["total_qa_pairs"] = document.get_total_qa_pairs()

            if qa_coverage < 30:
                results["warnings"].append(
                    f"Low Q&A coverage: {qa_coverage:.1f}% of chunks have Q&A pairs"
                )

        # Add summary stats
        results["stats"].update(document.get_statistics())

        if results["errors"]:
            results["valid"] = False

        return results

    def process_batch(
        self, pdf_paths: list[str], skip_qa: bool = False
    ) -> list[tuple[str, ProcessedDocument, Path]]:
        """Process multiple PDFs.

        Args:
            pdf_paths: List of PDF file paths
            skip_qa: Skip Q&A generation

        Returns:
            List of tuples (pdf_path, document, output_path)
        """
        results = []

        for i, pdf_path in enumerate(pdf_paths):
            logger.info(f"Processing {i+1}/{len(pdf_paths)}: {pdf_path}")

            try:
                processed_doc, output_path = self.process_and_save(pdf_path, skip_qa=skip_qa)
                results.append((pdf_path, processed_doc, output_path))
                logger.info(f"Successfully processed {pdf_path}")

            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}", exc_info=True)
                results.append((pdf_path, None, None))

        success_count = sum(1 for _, doc, _ in results if doc is not None)
        logger.info(f"Batch complete: {success_count}/{len(pdf_paths)} successful")

        return results

    def get_config(self) -> IngestionConfig:
        """Get current configuration.

        Returns:
            IngestionConfig object
        """
        return self.config

    def update_config(self, **kwargs) -> None:
        """Update configuration parameters.

        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated config: {key} = {value}")
            else:
                logger.warning(f"Unknown config parameter: {key}")
