"""Command-line interface for IEC PDF ingestion."""

import sys
import logging
from pathlib import Path
from typing import Optional
import yaml
import click
from dotenv import load_dotenv

from .models import IngestionConfig
from .pipeline import IngestionPipeline

# Load environment variables
load_dotenv()


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup logging configuration.

    Args:
        log_level: Logging level
        log_file: Optional log file path
    """
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_file_path = Path(log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def load_config(config_path: Optional[str]) -> IngestionConfig:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        IngestionConfig object
    """
    if not config_path:
        return IngestionConfig()

    config_file = Path(config_path)
    if not config_file.exists():
        click.echo(f"Warning: Config file not found: {config_path}", err=True)
        return IngestionConfig()

    try:
        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f)

        # Flatten nested config structure
        flat_config = {}

        if "pdf" in config_data:
            flat_config.update(
                {
                    f"pdf_{k}": v
                    for k, v in config_data["pdf"].items()
                }
            )

        if "chunking" in config_data:
            flat_config.update(config_data["chunking"])

        if "qa_generation" in config_data:
            flat_config.update(
                {
                    f"qa_{k}" if not k.startswith("qa_") else k: v
                    for k, v in config_data["qa_generation"].items()
                    if k != "question_types" and k != "system_prompt"
                }
            )

        if "output" in config_data:
            flat_config.update(config_data["output"])

        return IngestionConfig(**flat_config)

    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        return IngestionConfig()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """IEC PDF Ingestion Pipeline - Process IEC standards with intelligent chunking."""
    pass


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    default="config/ingestion_config.yaml",
    help="Path to configuration file",
)
@click.option("--output", "-o", type=str, help="Output filename (without extension)")
@click.option("--skip-qa", is_flag=True, help="Skip Q&A pair generation")
@click.option(
    "--chunk-size", type=int, help="Override chunk size from config"
)
@click.option(
    "--chunk-overlap", type=int, help="Override chunk overlap from config"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Logging level",
)
@click.option("--log-file", type=str, help="Log file path")
def ingest(
    pdf_path: str,
    config: str,
    output: Optional[str],
    skip_qa: bool,
    chunk_size: Optional[int],
    chunk_overlap: Optional[int],
    log_level: str,
    log_file: Optional[str],
):
    """Ingest a single IEC PDF document.

    PDF_PATH: Path to the PDF file to process
    """
    # Setup logging
    setup_logging(log_level, log_file)

    logger = logging.getLogger(__name__)
    logger.info(f"Starting ingestion of {pdf_path}")

    try:
        # Load configuration
        ingestion_config = load_config(config)

        # Apply CLI overrides
        if chunk_size:
            ingestion_config.chunk_size = chunk_size
        if chunk_overlap:
            ingestion_config.chunk_overlap = chunk_overlap

        # Initialize pipeline
        pipeline = IngestionPipeline(config=ingestion_config)

        # Process document
        processed_doc, output_path = pipeline.process_and_save(
            pdf_path=pdf_path,
            output_filename=output,
            skip_qa=skip_qa,
        )

        # Validate results
        validation = pipeline.validate(processed_doc)

        # Display results
        click.echo("\n" + "="*60)
        click.echo("INGESTION COMPLETE")
        click.echo("="*60)
        click.echo(f"Document ID: {processed_doc.document_id}")
        click.echo(f"Standard: {processed_doc.metadata.standard_id or 'Unknown'}")
        click.echo(f"Edition: {processed_doc.metadata.edition or 'Unknown'}")
        click.echo(f"Year: {processed_doc.metadata.year or 'Unknown'}")
        click.echo(f"\nOutput: {output_path}")
        click.echo(f"\nStatistics:")
        click.echo(f"  - Total chunks: {len(processed_doc.chunks)}")
        click.echo(f"  - Total clauses: {len(processed_doc.clauses)}")
        click.echo(f"  - Total Q&A pairs: {processed_doc.get_total_qa_pairs()}")
        click.echo(f"  - Processing time: {processed_doc.processing_stats.get('processing_time_seconds', 0):.2f}s")

        # Display validation results
        if validation["warnings"]:
            click.echo(f"\nWarnings:")
            for warning in validation["warnings"]:
                click.echo(f"  - {warning}")

        if validation["errors"]:
            click.echo(f"\nErrors:", err=True)
            for error in validation["errors"]:
                click.echo(f"  - {error}", err=True)
            sys.exit(1)

        click.echo("\n✓ Ingestion successful!")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("pdf_paths", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    default="config/ingestion_config.yaml",
    help="Path to configuration file",
)
@click.option("--skip-qa", is_flag=True, help="Skip Q&A pair generation")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Logging level",
)
@click.option("--log-file", type=str, help="Log file path")
def batch(
    pdf_paths: tuple,
    config: str,
    skip_qa: bool,
    log_level: str,
    log_file: Optional[str],
):
    """Ingest multiple IEC PDF documents.

    PDF_PATHS: Paths to PDF files to process
    """
    # Setup logging
    setup_logging(log_level, log_file)

    logger = logging.getLogger(__name__)
    logger.info(f"Starting batch ingestion of {len(pdf_paths)} documents")

    try:
        # Load configuration
        ingestion_config = load_config(config)

        # Initialize pipeline
        pipeline = IngestionPipeline(config=ingestion_config)

        # Process batch
        results = pipeline.process_batch(list(pdf_paths), skip_qa=skip_qa)

        # Display results
        click.echo("\n" + "="*60)
        click.echo("BATCH INGESTION COMPLETE")
        click.echo("="*60)

        successful = [r for r in results if r[1] is not None]
        failed = [r for r in results if r[1] is None]

        click.echo(f"\nSuccessful: {len(successful)}/{len(pdf_paths)}")

        if successful:
            click.echo("\nProcessed documents:")
            for pdf_path, doc, output_path in successful:
                click.echo(f"  ✓ {Path(pdf_path).name}")
                click.echo(f"    - Output: {output_path}")
                click.echo(f"    - Chunks: {len(doc.chunks)}")
                click.echo(f"    - Q&A pairs: {doc.get_total_qa_pairs()}")

        if failed:
            click.echo(f"\nFailed documents:", err=True)
            for pdf_path, _, _ in failed:
                click.echo(f"  ✗ {Path(pdf_path).name}", err=True)

        if failed:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Batch ingestion failed: {e}", exc_info=True)
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("document_path", type=click.Path(exists=True))
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    default="config/ingestion_config.yaml",
    help="Path to configuration file",
)
def validate(document_path: str, config: str):
    """Validate a processed document.

    DOCUMENT_PATH: Path to the processed document JSON file
    """
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        ingestion_config = load_config(config)

        # Initialize pipeline and storage
        pipeline = IngestionPipeline(config=ingestion_config)

        # Load document
        click.echo(f"Loading document: {document_path}")
        processed_doc = pipeline.storage.load(document_path)

        # Validate
        validation = pipeline.validate(processed_doc)

        # Display results
        click.echo("\n" + "="*60)
        click.echo("VALIDATION RESULTS")
        click.echo("="*60)
        click.echo(f"Valid: {'✓ Yes' if validation['valid'] else '✗ No'}")

        if validation["stats"]:
            click.echo(f"\nStatistics:")
            for key, value in validation["stats"].items():
                if isinstance(value, dict):
                    continue
                click.echo(f"  - {key}: {value}")

        if validation["warnings"]:
            click.echo(f"\nWarnings:")
            for warning in validation["warnings"]:
                click.echo(f"  - {warning}")

        if validation["errors"]:
            click.echo(f"\nErrors:", err=True)
            for error in validation["errors"]:
                click.echo(f"  - {error}", err=True)

        if not validation["valid"]:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--output-dir",
    "-o",
    type=str,
    default="data/output",
    help="Output directory to check",
)
def stats(output_dir: str):
    """Show statistics about stored documents."""
    from .storage import DocumentStorage

    try:
        storage = DocumentStorage(output_dir=output_dir)
        statistics = storage.get_statistics()

        click.echo("\n" + "="*60)
        click.echo("STORAGE STATISTICS")
        click.echo("="*60)
        click.echo(f"Output directory: {statistics['output_dir']}")
        click.echo(f"JSON documents: {statistics['json_documents']}")
        click.echo(f"JSONL documents: {statistics['jsonl_documents']}")
        click.echo(f"Total size: {statistics['total_size_mb']} MB")

    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
