# Citation Manager Module

Comprehensive citation management system for the Solar PV LLM AI project. Automatically extracts, tracks, formats, and injects citations into LLM-generated responses.

## Features

### Core Capabilities

1. **Citation Tracking** - Sequential citation numbering with optional persistence
2. **Metadata Extraction** - Automatically extracts standard IDs, clause references, and metadata
3. **Inline Citation Injection** - Intelligently injects citation markers into responses
4. **Multiple Format Support** - IEC, IEEE, and APA citation styles
5. **Reference Management** - Validates and manages citation references

### Supported Standards

The citation extractor recognizes and extracts:
- IEC standards (e.g., IEC 61215, IEC 61730-1)
- ISO standards (e.g., ISO 9001, ISO/IEC 17025)
- IEEE standards (e.g., IEEE 1547, IEEE 802.11)
- ASTM standards (e.g., ASTM E1036)
- EN standards (e.g., EN 50530)
- UL standards (e.g., UL 1741)

### Citation Elements Extracted

- Standard IDs (e.g., "IEC 61215-1")
- Clause references (e.g., "Clause 5.2.1")
- Section references (e.g., "Section 4.3")
- Annex references (e.g., "Annex A")
- Publication years
- Page numbers
- Titles and URLs

## Usage

### Basic Usage

```python
from citations import CitationManager, RetrievedDocument

# Initialize citation manager
manager = CitationManager()

# Prepare LLM response and retrieved documents
llm_response = "Solar modules must meet IEC 61215 testing standards."

retrieved_docs = [
    RetrievedDocument(
        content="IEC 61215 defines testing requirements...",
        metadata={
            'standard_id': 'IEC 61215',
            'title': 'PV Module Testing',
            'year': '2021',
            'clause': 'Clause 5.2'
        },
        doc_id="doc_1",
        score=0.9
    )
]

# Process response with citation injection
processed_response, citations = manager.process_response(
    llm_response,
    retrieved_docs,
    inject_citations=True
)

# Format references
references = manager.format_references(style='iec')

print(processed_response)  # Response with [1] citation markers
print(references)          # Formatted reference list
```

### Advanced Usage

#### Custom Citation Persistence

```python
# Reset citations for each response (default)
manager = CitationManager(reset_per_response=True)

# Or persist citations across responses
manager = CitationManager(reset_per_response=False)
```

#### Different Citation Formats

```python
# IEC format (default)
references_iec = manager.format_references(style='iec')

# IEEE format
references_ieee = manager.format_references(style='ieee')

# APA format
references_apa = manager.format_references(style='apa')
```

#### Manual Citation Extraction

```python
from citations import CitationExtractor

extractor = CitationExtractor()

# Extract from text
standard_id = extractor.extract_standard_id("According to IEC 61215...")
# Returns: "IEC 61215"

clause_ref = extractor.extract_clause_reference("See Clause 5.2.1...")
# Returns: "Clause 5.2.1"

# Extract all metadata
metadata = extractor.extract_metadata(
    metadata={'title': 'PV Testing'},
    content="IEC 61215:2021 Clause 5.2 describes..."
)
# Returns: {'standard_id': 'IEC 61215', 'year': '2021', 'clause_ref': 'Clause 5.2', ...}
```

#### Reference Validation

```python
from citations import ReferenceManager

ref_manager = ReferenceManager()
ref_manager.add_citations(citations)

# Validate citations in text
is_valid, errors = ref_manager.validate_citations(text_with_citations)

# Validate citation sequence
is_valid, errors = ref_manager.validate_citation_sequence()

# Get statistics
stats = ref_manager.get_citation_statistics()
print(f"Total citations: {stats['total_citations']}")
print(f"Unique standards: {stats['unique_standards']}")
```

## Citation Formats

### IEC Style

```
[1] IEC 61215-1, "Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 1", 2021, Clause 5.2.
```

### IEEE Style

```
[1] "Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 1," IEC 61215-1, 2021, sec. 5.2.
```

### APA Style

```
[1] International Electrotechnical Commission. (2021). Terrestrial photovoltaic (PV) modules - Design qualification and type approval - Part 1. (IEC 61215-1).
```

## Module Structure

```
citations/
├── __init__.py                 # Module exports
├── citation_manager.py         # Main orchestration class
├── citation_extractor.py       # Metadata extraction
├── citation_injector.py        # Inline citation injection
├── citation_formatter.py       # Format citations (IEC, IEEE, APA)
├── reference_manager.py        # Reference validation and management
└── README.md                   # This file
```

## Data Classes

### Citation

```python
@dataclass
class Citation:
    citation_id: int
    standard_id: Optional[str] = None
    clause_ref: Optional[str] = None
    title: Optional[str] = None
    year: Optional[str] = None
    url: Optional[str] = None
    page: Optional[str] = None
    source_doc_id: str = ""
    match_text: str = ""
```

### RetrievedDocument

```python
@dataclass
class RetrievedDocument:
    content: str
    metadata: Dict[str, Any]
    doc_id: str
    score: float = 0.0
```

## Testing

Run unit tests:

```bash
# Run all citation tests
pytest tests/test_citations/ -v

# Run specific test file
pytest tests/test_citations/test_citation_manager.py -v

# Run with coverage
pytest tests/test_citations/ --cov=src/citations --cov-report=html
```

Run QA verification:

```bash
python tests/qa_verification.py
```

## Configuration

### CitationInjector Parameters

- `similarity_threshold` (float, default: 0.6) - Minimum similarity for content matching
- `min_match_length` (int, default: 30) - Minimum character length for matching
- `citation_format` (str, default: "[{id}]") - Format for citation markers

### CitationTracker Parameters

- `start_index` (int, default: 1) - Starting citation number

## Best Practices

1. **Always provide metadata** - Include standard_id, title, year, and clause in document metadata
2. **Use reset_per_response=True** - For independent responses (default behavior)
3. **Validate citations** - Use ReferenceManager to validate before finalizing
4. **Choose appropriate format** - IEC for technical standards, IEEE for academic, APA for general
5. **Test thoroughly** - Run QA verification after any changes

## Future Enhancements

- Support for additional citation styles (Chicago, MLA)
- Multi-language citation support
- DOI and ISBN extraction
- Citation deduplication improvements
- Integration with reference management tools (Zotero, Mendeley)
- Machine learning-based citation relevance scoring

## Contributing

When contributing to the citation module:

1. Add tests for new features
2. Update this README
3. Run QA verification script
4. Ensure all tests pass
5. Follow existing code style

## License

Part of the Solar PV LLM AI System project.
