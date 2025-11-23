"""Citation Manager - Automated citation extraction and formatting for Solar PV LLM.

This package provides comprehensive citation management functionality including:
- Citation tracking with sequential numbering
- Extraction of clause references and standard IDs
- Citation injection into LLM responses
- Formatting in multiple citation styles (IEC, IEEE, ISO, APA)
- Reference management and tracking

Main classes:
    CitationManager: Main interface for all citation operations
    CitationTracker: Tracks citation numbers
    CitationExtractor: Extracts citations from text
    CitationFormatter: Formats citations in various styles
    ReferenceTracker: Manages document metadata

Example usage:
    >>> from citation_manager import CitationManager, CitationStyle
    >>> from citation_manager import create_standard_metadata
    >>>
    >>> # Initialize manager
    >>> manager = CitationManager(style=CitationStyle.IEC)
    >>>
    >>> # Add source document
    >>> doc = create_standard_metadata(
    ...     standard_id="IEC 61730-1:2016",
    ...     title="Photovoltaic (PV) module safety qualification - Part 1",
    ...     organization="IEC"
    ... )
    >>> manager.add_document(doc)
    >>>
    >>> # Process response
    >>> result = manager.process_response(
    ...     response_text="The module must meet IEC 61730 requirements.",
    ...     retrieved_documents=[{
    ...         'document_id': 'IEC 61730-1:2016',
    ...         'content': 'Requirements for construction...',
    ...         'score': 0.95
    ...     }]
    ... )
    >>>
    >>> print(result.text_with_citations)
    >>> print(result.reference_section)
"""

from .citation_models import (
    Citation,
    CitationExtractionResult,
    CitationStyle,
    ClauseReference,
    DocumentMetadata,
    DocumentType,
    FormattedCitation,
    ResponseCitations,
    StandardMetadata,
)

from .citation_tracker import CitationTracker
from .citation_extractor import CitationExtractor
from .citation_formatter import CitationFormatter
from .reference_tracker import ReferenceTracker, create_standard_metadata
from .citation_manager import CitationManager

__version__ = "0.1.0"

__all__ = [
    # Main class
    "CitationManager",

    # Core components
    "CitationTracker",
    "CitationExtractor",
    "CitationFormatter",
    "ReferenceTracker",

    # Data models
    "Citation",
    "CitationExtractionResult",
    "CitationStyle",
    "ClauseReference",
    "DocumentMetadata",
    "DocumentType",
    "FormattedCitation",
    "ResponseCitations",
    "StandardMetadata",

    # Helper functions
    "create_standard_metadata",

    # Version
    "__version__",
]
