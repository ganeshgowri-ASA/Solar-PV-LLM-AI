#!/usr/bin/env python3
"""
IEC PDF Ingestion CLI
Command-line interface for processing IEC standard PDFs.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import create_pipeline
from src.chunking import ChunkConfig
from src.qa_generation import QAConfig

# Load environment variables
load_dotenv()


def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO

    # Create formatters
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)

    handlers = [console_handler]

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--log-file', type=click.Path(), help='Log to file')
@click.pass_context
def cli(ctx, verbose, log_file):
    """IEC PDF Ingestion Pipeline CLI"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    setup_logging(verbose, log_file)


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='data/processed', help='Output directory')
@click.option('--chunk-size', '-s', default=1000, help='Target chunk size in characters')
@click.option('--chunk-overlap', default=200, help='Overlap between chunks')
@click.option('--no-qa', is_flag=True, help='Disable Q&A generation')
@click.option('--save-intermediate', is_flag=True, help='Save intermediate results')
@click.option('--output-filename', help='Custom output filename')
@click.pass_context
def process(ctx, pdf_path, output_dir, chunk_size, chunk_overlap, no_qa, save_intermediate, output_filename):
    """
    Process a single IEC PDF document.

    Example:
        ingest_iec_pdf.py process /path/to/IEC_61215-1.pdf
    """
    click.echo(f"Processing: {pdf_path}")
    click.echo(f"Output directory: {output_dir}")

    # Create pipeline
    pipeline = create_pipeline(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        enable_qa=not no_qa,
        output_dir=output_dir
    )

    # Process PDF
    try:
        with click.progressbar(length=100, label='Processing PDF') as bar:
            result = pipeline.process_pdf(
                pdf_path=pdf_path,
                output_filename=output_filename,
                save_intermediate=save_intermediate
            )
            bar.update(100)

        # Display results
        if result['success']:
            click.echo(click.style("\n✓ Processing successful!", fg='green', bold=True))
            click.echo(f"\nOutput: {result['output_path']}")

            stats = result['statistics']
            click.echo("\nStatistics:")
            click.echo(f"  Chunks: {stats['total_chunks']}")
            click.echo(f"  Q&A pairs: {stats['total_qa_pairs']}")
            click.echo(f"  Sections: {stats['total_sections']}")
            click.echo(f"  Avg chunk size: {stats['avg_chunk_size']:.0f} chars")
            click.echo(f"  Processing time: {stats['processing_time_seconds']:.2f}s")

            # Document info
            doc_meta = result['document_metadata']['iec_metadata']
            click.echo("\nDocument:")
            click.echo(f"  Standard: {doc_meta['standard_id']}")
            click.echo(f"  Title: {doc_meta['title']}")
            if doc_meta.get('year'):
                click.echo(f"  Year: {doc_meta['year']}")
            if doc_meta.get('edition'):
                click.echo(f"  Edition: {doc_meta['edition']}")

        else:
            click.echo(click.style("\n✗ Processing failed!", fg='red', bold=True))
            click.echo(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"\n✗ Error: {e}", fg='red', bold=True))
        if ctx.obj.get('verbose'):
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('pdf_paths', nargs=-1, type=click.Path(exists=True), required=True)
@click.option('--output-dir', '-o', default='data/processed', help='Output directory')
@click.option('--chunk-size', '-s', default=1000, help='Target chunk size in characters')
@click.option('--chunk-overlap', default=200, help='Overlap between chunks')
@click.option('--no-qa', is_flag=True, help='Disable Q&A generation')
@click.pass_context
def batch(ctx, pdf_paths, output_dir, chunk_size, chunk_overlap, no_qa):
    """
    Process multiple IEC PDFs in batch.

    Example:
        ingest_iec_pdf.py batch /path/to/pdf1.pdf /path/to/pdf2.pdf
    """
    click.echo(f"Batch processing {len(pdf_paths)} PDFs")

    # Create pipeline
    pipeline = create_pipeline(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        enable_qa=not no_qa,
        output_dir=output_dir
    )

    # Process batch
    results = pipeline.process_batch(list(pdf_paths))

    # Display summary
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    click.echo(f"\n{'='*60}")
    click.echo(f"Batch processing complete:")
    click.echo(f"  Successful: {successful}/{len(results)}")
    click.echo(f"  Failed: {failed}/{len(results)}")

    if failed > 0:
        click.echo("\nFailed files:")
        for r in results:
            if not r['success']:
                click.echo(f"  - {r['pdf_path']}: {r.get('error', 'Unknown error')}")


@cli.command()
@click.argument('json_path', type=click.Path(exists=True))
@click.pass_context
def validate(ctx, json_path):
    """
    Validate a processed JSON file.

    Example:
        ingest_iec_pdf.py validate data/processed/IEC_61215-1.json
    """
    click.echo(f"Validating: {json_path}")

    # Create pipeline
    pipeline = create_pipeline()

    # Validate
    try:
        validation = pipeline.validate_processing(json_path)

        if validation['valid']:
            click.echo(click.style("\n✓ Validation passed!", fg='green', bold=True))
        else:
            click.echo(click.style("\n✗ Validation failed!", fg='red', bold=True))

        # Display errors
        if validation['errors']:
            click.echo("\nErrors:")
            for error in validation['errors']:
                click.echo(click.style(f"  ✗ {error}", fg='red'))

        # Display warnings
        if validation['warnings']:
            click.echo("\nWarnings:")
            for warning in validation['warnings']:
                click.echo(click.style(f"  ! {warning}", fg='yellow'))

        # Display statistics
        if validation['statistics']:
            stats = validation['statistics']
            click.echo("\nStatistics:")
            click.echo(f"  Total chunks: {stats.get('total_chunks', 0)}")
            click.echo(f"  Total Q&A pairs: {stats.get('total_qa_pairs', 0)}")
            click.echo(f"  Unique clauses: {stats.get('unique_clauses', 0)}")
            click.echo(f"  Avg chunk size: {stats.get('avg_chunk_size', 0):.0f} chars")

        sys.exit(0 if validation['valid'] else 1)

    except Exception as e:
        click.echo(click.style(f"\n✗ Error: {e}", fg='red', bold=True))
        if ctx.obj.get('verbose'):
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--output-dir', '-o', default='data/processed', help='Output directory to list')
def list_documents(output_dir):
    """
    List all processed documents.

    Example:
        ingest_iec_pdf.py list-documents
    """
    from src.storage import JSONStorage

    storage = JSONStorage(output_dir)
    documents = storage.list_processed_documents()

    if not documents:
        click.echo("No processed documents found.")
        return

    click.echo(f"\nFound {len(documents)} processed documents:\n")
    click.echo(f"{'Filename':<40} {'Standard ID':<20} {'Chunks':<10} {'Date':<20}")
    click.echo("=" * 90)

    for doc in documents:
        click.echo(
            f"{doc['filename']:<40} "
            f"{doc.get('standard_id', 'N/A'):<20} "
            f"{doc['chunk_count']:<10} "
            f"{doc.get('export_timestamp', 'N/A'):<20}"
        )


@cli.command()
@click.argument('json_path', type=click.Path(exists=True))
def stats(json_path):
    """
    Display statistics for a processed document.

    Example:
        ingest_iec_pdf.py stats data/processed/IEC_61215-1.json
    """
    from src.storage import JSONStorage

    storage = JSONStorage()
    statistics = storage.get_statistics(json_path)

    click.echo(f"\nStatistics for: {Path(json_path).name}\n")
    click.echo(f"Total chunks: {statistics.get('total_chunks', 0)}")
    click.echo(f"Total Q&A pairs: {statistics.get('total_qa_pairs', 0)}")
    click.echo(f"Avg Q&A per chunk: {statistics.get('avg_qa_per_chunk', 0):.2f}")
    click.echo(f"Unique clauses: {statistics.get('unique_clauses', 0)}")
    click.echo(f"Total characters: {statistics.get('total_characters', 0):,}")
    click.echo(f"Avg chunk size: {statistics.get('avg_chunk_size', 0):.0f} chars")
    click.echo(f"Min chunk size: {statistics.get('min_chunk_size', 0)} chars")
    click.echo(f"Max chunk size: {statistics.get('max_chunk_size', 0)} chars")


if __name__ == '__main__':
    cli(obj={})
