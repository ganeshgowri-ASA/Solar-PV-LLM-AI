#!/usr/bin/env python3
"""
Basic usage example for IEC PDF ingestion pipeline.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import create_pipeline


def main():
    """Basic pipeline usage example."""

    # Example 1: Process a single PDF with default settings
    print("Example 1: Basic processing")
    print("=" * 60)

    pipeline = create_pipeline()

    # Note: Replace with actual PDF path
    pdf_path = "data/raw/sample_iec_standard.pdf"

    if not Path(pdf_path).exists():
        print(f"⚠ PDF not found: {pdf_path}")
        print("Please provide a valid IEC standard PDF path")
        return

    result = pipeline.process_pdf(pdf_path)

    if result['success']:
        print(f"✓ Processing successful!")
        print(f"  Output: {result['output_path']}")
        print(f"  Chunks: {result['statistics']['total_chunks']}")
        print(f"  Q&A pairs: {result['statistics']['total_qa_pairs']}")
        print(f"  Time: {result['statistics']['processing_time_seconds']:.2f}s")

    print("\n")

    # Example 2: Custom chunk size
    print("Example 2: Custom configuration")
    print("=" * 60)

    custom_pipeline = create_pipeline(
        chunk_size=800,
        chunk_overlap=150,
        enable_qa=True
    )

    print("Pipeline configured with:")
    print("  - Chunk size: 800 characters")
    print("  - Overlap: 150 characters")
    print("  - Q&A generation: Enabled")

    print("\n")

    # Example 3: Validation
    print("Example 3: Validation")
    print("=" * 60)

    if result['success']:
        validation = pipeline.validate_processing(result['output_path'])

        if validation['valid']:
            print("✓ Validation passed!")
        else:
            print("✗ Validation issues found:")
            for error in validation['errors']:
                print(f"  Error: {error}")
            for warning in validation['warnings']:
                print(f"  Warning: {warning}")

        print("\nStatistics:")
        stats = validation['statistics']
        print(f"  Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  Total Q&A pairs: {stats.get('total_qa_pairs', 0)}")
        print(f"  Unique clauses: {stats.get('unique_clauses', 0)}")


if __name__ == '__main__':
    main()
