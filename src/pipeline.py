"""
IEC PDF Ingestion Pipeline - Orchestrates the complete processing workflow.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .ingestion import IECPDFLoader, StructuredSection
from .metadata import IECMetadataExtractor, ChunkMetadata, DocumentMetadata, ClauseMetadata, ProcessedChunk
from .chunking import SemanticChunker, ChunkConfig
from .qa_generation import QAGenerator, QAConfig
from .storage import JSONStorage

logger = logging.getLogger(__name__)


class IECIngestionPipeline:
    """
    Complete pipeline for ingesting IEC PDF documents.
    """

    def __init__(
        self,
        chunk_config: Optional[ChunkConfig] = None,
        qa_config: Optional[QAConfig] = None,
        output_dir: str = "data/processed",
        enable_qa_generation: bool = True
    ):
        """
        Initialize the ingestion pipeline.

        Args:
            chunk_config: Configuration for chunking
            qa_config: Configuration for Q&A generation
            output_dir: Output directory for processed data
            enable_qa_generation: Whether to generate Q&A pairs
        """
        self.pdf_loader = IECPDFLoader()
        self.metadata_extractor = IECMetadataExtractor()
        self.chunker = SemanticChunker(chunk_config)
        self.qa_generator = QAGenerator(qa_config) if enable_qa_generation else None
        self.storage = JSONStorage(output_dir)

        self.enable_qa_generation = enable_qa_generation

        logger.info("IEC Ingestion Pipeline initialized")

    def process_pdf(
        self,
        pdf_path: str,
        output_filename: Optional[str] = None,
        save_intermediate: bool = False
    ) -> Dict[str, Any]:
        """
        Process a single IEC PDF through the complete pipeline.

        Args:
            pdf_path: Path to PDF file
            output_filename: Optional custom output filename
            save_intermediate: Whether to save intermediate results

        Returns:
            Dictionary with processing results and statistics
        """
        logger.info(f"Starting pipeline for: {pdf_path}")
        start_time = datetime.utcnow()

        # Step 1: Load PDF and extract structure
        logger.info("Step 1: Loading PDF and extracting structure...")
        pdf_data, sections = self.pdf_loader.load_and_structure(pdf_path)

        # Step 2: Extract document-level metadata
        logger.info("Step 2: Extracting document metadata...")
        doc_metadata = self.metadata_extractor.extract_document_metadata(pdf_data['text'])

        # Extract scope if available
        scope = self.metadata_extractor.extract_scope(pdf_data['text'])
        if scope:
            doc_metadata.scope = scope

        # Step 3: Process each section - chunk and generate metadata
        logger.info(f"Step 3: Processing {len(sections)} sections...")
        all_chunks = []
        chunk_index = 0

        for section in sections:
            # Create chunks for this section
            section_chunks = self.chunker.chunk_section(
                section.content,
                section.clause_number,
                section.clause_title
            )

            # Process each chunk
            for chunk_data in section_chunks:
                chunk_id = f"{doc_metadata.standard_id.replace(' ', '-')}_chunk_{chunk_index:04d}"

                # Create clause metadata
                clause_metadata = ClauseMetadata(
                    clause_number=section.clause_number,
                    clause_title=section.clause_title,
                    parent_clause=section.parent_clause,
                    level=section.level,
                    section_type=section.section_type
                )

                # Create chunk metadata
                chunk_metadata = ChunkMetadata(
                    document=doc_metadata,
                    clause=clause_metadata,
                    chunk_id=chunk_id,
                    chunk_index=chunk_index,
                    page_numbers=section.page_numbers,
                    char_count=len(chunk_data['text']),
                    word_count=len(chunk_data['text'].split()),
                    previous_chunk_id=f"{doc_metadata.standard_id.replace(' ', '-')}_chunk_{chunk_index-1:04d}" if chunk_index > 0 else None,
                    next_chunk_id=None,  # Will be updated later
                    related_clauses=self.pdf_loader.extract_references(chunk_data['text'])
                )

                # Update previous chunk's next_chunk_id
                if all_chunks:
                    all_chunks[-1].metadata.next_chunk_id = chunk_id

                # Step 4: Generate Q&A pairs
                qa_pairs = []
                if self.enable_qa_generation and self.qa_generator:
                    qa_pairs = self.qa_generator.generate_qa_pairs(
                        text=chunk_data['text'],
                        chunk_id=chunk_id,
                        clause_number=section.clause_number,
                        clause_title=section.clause_title,
                        standard_id=doc_metadata.standard_id
                    )

                # Create ProcessedChunk
                processed_chunk = ProcessedChunk(
                    text=chunk_data['text'],
                    metadata=chunk_metadata,
                    qa_pairs=qa_pairs
                )

                all_chunks.append(processed_chunk)
                chunk_index += 1

        # Calculate chunk statistics
        chunk_stats = self.chunker.get_chunk_statistics(
            [{'text': c.text} for c in all_chunks]
        )

        # Create document metadata
        document_metadata = DocumentMetadata(
            source_file=Path(pdf_path).name,
            iec_metadata=doc_metadata,
            total_chunks=len(all_chunks),
            total_pages=pdf_data['metadata']['page_count'],
            total_characters=sum(c.metadata.char_count for c in all_chunks),
            chunk_statistics=chunk_stats
        )

        # Step 5: Save to JSON
        logger.info("Step 5: Saving processed data...")
        output_path = self.storage.save_processed_document(
            chunks=all_chunks,
            document_metadata=document_metadata,
            output_filename=output_filename
        )

        # Save additional formats if requested
        if save_intermediate:
            # Export for retrieval
            retrieval_path = output_path.replace('.json', '_retrieval.json')
            self.storage.export_for_retrieval(all_chunks, Path(retrieval_path).name)

            # Export Q&A pairs
            if self.enable_qa_generation:
                qa_path = output_path.replace('.json', '_qa_pairs.json')
                self.storage.export_qa_pairs(all_chunks, Path(qa_path).name)

        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()

        # Generate results
        results = {
            'success': True,
            'output_path': output_path,
            'document_metadata': document_metadata.model_dump(mode='json'),
            'statistics': {
                'total_chunks': len(all_chunks),
                'total_qa_pairs': sum(len(c.qa_pairs) for c in all_chunks),
                'total_sections': len(sections),
                'processing_time_seconds': processing_time,
                **chunk_stats
            }
        }

        logger.info(f"Pipeline completed in {processing_time:.2f}s")
        logger.info(f"Generated {len(all_chunks)} chunks with {results['statistics']['total_qa_pairs']} Q&A pairs")

        return results

    def process_batch(
        self,
        pdf_paths: List[str],
        output_dir: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple PDFs in batch.

        Args:
            pdf_paths: List of PDF file paths
            output_dir: Optional output directory override

        Returns:
            List of processing results
        """
        if output_dir:
            self.storage = JSONStorage(output_dir)

        results = []
        for i, pdf_path in enumerate(pdf_paths, 1):
            logger.info(f"Processing {i}/{len(pdf_paths)}: {pdf_path}")
            try:
                result = self.process_pdf(pdf_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {e}")
                results.append({
                    'success': False,
                    'pdf_path': pdf_path,
                    'error': str(e)
                })

        return results

    def validate_processing(self, output_path: str) -> Dict[str, Any]:
        """
        Validate processed document.

        Args:
            output_path: Path to processed JSON file

        Returns:
            Validation results
        """
        logger.info(f"Validating: {output_path}")

        # Load processed data
        data = self.storage.load_processed_document(output_path)
        chunks = data['chunks']
        doc_metadata = data['document_metadata']

        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }

        # Check chunk count
        if len(chunks) == 0:
            validation['errors'].append("No chunks found")
            validation['valid'] = False

        # Check metadata completeness
        if not doc_metadata:
            validation['errors'].append("Missing document metadata")
            validation['valid'] = False
        else:
            if not doc_metadata.iec_metadata.standard_id:
                validation['warnings'].append("Missing standard ID")
            if not doc_metadata.iec_metadata.year:
                validation['warnings'].append("Missing publication year")

        # Check each chunk
        empty_chunks = 0
        missing_metadata = 0
        missing_qa = 0

        for chunk in chunks:
            if not chunk.text or len(chunk.text.strip()) < 10:
                empty_chunks += 1

            if not chunk.metadata:
                missing_metadata += 1

            if self.enable_qa_generation and len(chunk.qa_pairs) == 0:
                missing_qa += 1

        if empty_chunks > 0:
            validation['warnings'].append(f"{empty_chunks} chunks are empty or too short")

        if missing_metadata > 0:
            validation['errors'].append(f"{missing_metadata} chunks missing metadata")
            validation['valid'] = False

        if missing_qa > len(chunks) * 0.5:  # More than 50% missing Q&A
            validation['warnings'].append(f"{missing_qa}/{len(chunks)} chunks missing Q&A pairs")

        # Get statistics
        validation['statistics'] = self.storage.get_statistics(output_path)

        return validation


def create_pipeline(
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    enable_qa: bool = True,
    output_dir: str = "data/processed"
) -> IECIngestionPipeline:
    """
    Factory function to create a configured pipeline.

    Args:
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        enable_qa: Enable Q&A generation
        output_dir: Output directory

    Returns:
        Configured IECIngestionPipeline
    """
    chunk_config = ChunkConfig(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    qa_config = QAConfig() if enable_qa else None

    return IECIngestionPipeline(
        chunk_config=chunk_config,
        qa_config=qa_config,
        output_dir=output_dir,
        enable_qa_generation=enable_qa
    )
