#!/usr/bin/env python3
"""
Advanced usage examples for IEC PDF ingestion pipeline.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import IECPDFLoader
from src.metadata import IECMetadataExtractor
from src.chunking import SemanticChunker, ChunkConfig
from src.qa_generation import QAGenerator, QAConfig
from src.storage import JSONStorage


def example_1_component_usage():
    """Example: Using individual components."""
    print("Example 1: Using Individual Components")
    print("=" * 60)

    # Load PDF
    loader = IECPDFLoader()
    pdf_path = "data/raw/sample.pdf"

    if not Path(pdf_path).exists():
        print(f"⚠ PDF not found: {pdf_path}")
        return

    pdf_data, sections = loader.load_and_structure(pdf_path)
    print(f"Loaded {len(sections)} sections from PDF")

    # Extract metadata
    extractor = IECMetadataExtractor()
    metadata = extractor.extract_document_metadata(pdf_data['text'])
    print(f"Standard ID: {metadata.standard_id}")
    print(f"Title: {metadata.title}")

    # Chunk first section
    if sections:
        chunker = SemanticChunker(ChunkConfig(chunk_size=500))
        chunks = chunker.chunk_section(
            sections[0].content,
            sections[0].clause_number,
            sections[0].clause_title
        )
        print(f"Created {len(chunks)} chunks from first section")

    print()


def example_2_custom_qa_generation():
    """Example: Custom Q&A generation."""
    print("Example 2: Custom Q&A Generation")
    print("=" * 60)

    # Configure Q&A generator
    qa_config = QAConfig(
        model="gpt-4-turbo-preview",
        max_questions_per_chunk=5,
        min_confidence=0.8,
        temperature=0.2
    )

    qa_generator = QAGenerator(qa_config)

    sample_text = """
    The thermal cycling test shall subject the module to 200 cycles
    between -40°C and +85°C. The temperature transition rate shall
    not exceed 100°C per hour. This test evaluates the module's
    ability to withstand thermal stress.
    """

    qa_pairs = qa_generator.generate_qa_pairs(
        text=sample_text,
        chunk_id="example_001",
        clause_number="5.2.3",
        clause_title="Thermal cycling test",
        standard_id="IEC 61215-1"
    )

    print(f"Generated {len(qa_pairs)} Q&A pairs:")
    for i, qa in enumerate(qa_pairs, 1):
        print(f"\n  Q{i}: {qa.question}")
        print(f"  A{i}: {qa.answer}")
        print(f"  Confidence: {qa.confidence:.2f}")
        print(f"  Type: {qa.question_type}")

    print()


def example_3_batch_processing():
    """Example: Batch processing multiple PDFs."""
    print("Example 3: Batch Processing")
    print("=" * 60)

    from src.pipeline import create_pipeline

    pipeline = create_pipeline()

    # List of PDFs to process
    pdf_paths = [
        "data/raw/IEC_61215-1.pdf",
        "data/raw/IEC_61215-2.pdf",
        "data/raw/IEC_62804-1.pdf"
    ]

    # Filter to existing files
    existing_pdfs = [p for p in pdf_paths if Path(p).exists()]

    if not existing_pdfs:
        print("⚠ No PDFs found. Please add PDF files to data/raw/")
        return

    print(f"Processing {len(existing_pdfs)} PDFs...")

    results = pipeline.process_batch(existing_pdfs)

    successful = sum(1 for r in results if r['success'])
    print(f"\nCompleted: {successful}/{len(results)} successful")

    print()


def example_4_custom_storage():
    """Example: Custom storage and export."""
    print("Example 4: Custom Storage and Export")
    print("=" * 60)

    storage = JSONStorage("data/processed")

    # List all processed documents
    documents = storage.list_processed_documents()

    if not documents:
        print("No processed documents found.")
        return

    print(f"Found {len(documents)} processed documents:")
    for doc in documents[:5]:  # Show first 5
        print(f"  - {doc['filename']} ({doc['chunk_count']} chunks)")

    # Get statistics for first document
    if documents:
        first_doc = documents[0]
        stats = storage.get_statistics(first_doc['path'])

        print(f"\nStatistics for {first_doc['filename']}:")
        print(f"  Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  Total Q&A pairs: {stats.get('total_qa_pairs', 0)}")
        print(f"  Avg chunk size: {stats.get('avg_chunk_size', 0):.0f} chars")

    print()


def example_5_metadata_extraction():
    """Example: Detailed metadata extraction."""
    print("Example 5: Detailed Metadata Extraction")
    print("=" * 60)

    extractor = IECMetadataExtractor()

    # Sample IEC standard text
    sample_text = """
    IEC 61215-1:2021

    Terrestrial photovoltaic (PV) modules –
    Design qualification and type approval –
    Part 1: Test requirements

    Edition 4.0

    © IEC 2021

    1 Scope

    This part of IEC 61215 lays down requirements for the design
    qualification and type approval of terrestrial photovoltaic modules
    suitable for long-term operation in general open-air climates.
    """

    metadata = extractor.extract_document_metadata(sample_text)

    print(f"Standard ID: {metadata.standard_id}")
    print(f"Edition: {metadata.edition}")
    print(f"Year: {metadata.year}")
    print(f"Title: {metadata.title}")
    print(f"Keywords: {', '.join(metadata.keywords[:5])}")

    # Extract scope
    scope = extractor.extract_scope(sample_text)
    if scope:
        print(f"\nScope: {scope[:100]}...")

    print()


if __name__ == '__main__':
    print("IEC PDF Pipeline - Advanced Usage Examples\n")

    examples = [
        example_1_component_usage,
        example_2_custom_qa_generation,
        example_3_batch_processing,
        example_4_custom_storage,
        example_5_metadata_extraction
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"⚠ Example failed: {e}\n")
