# Citation Manager

Automated citation extraction, formatting, and insertion for Solar PV LLM AI responses.

## Overview

The Citation Manager is a comprehensive Python module that automates the process of:
- Extracting standard IDs (IEC, IEEE, ISO, etc.) and clause references from documents
- Tracking citation numbers incrementally per response
- Injecting inline citations into LLM-generated answers
- Formatting reference sections in multiple citation styles (IEC, IEEE, ISO, APA)
- Managing document metadata and usage tracking

## Features

✅ **Citation Tracking**: Automatic sequential numbering of citations per response
✅ **Smart Extraction**: Identifies standard IDs, clause references, and section numbers
✅ **Multiple Styles**: Support for IEC, IEEE, ISO, and APA citation formats
✅ **Document Management**: Track and manage source document metadata
✅ **RAG Integration**: Seamlessly integrates with Retrieval-Augmented Generation pipelines
✅ **Export/Import**: Save and load citation data in JSON format
✅ **Comprehensive Testing**: Full unit test coverage with QA verification

## Installation

```bash
# Clone the repository
cd Solar-PV-LLM-AI

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from src.citation_manager import (
    CitationManager,
    CitationStyle,
    create_standard_metadata
)

# 1. Initialize the citation manager
manager = CitationManager(style=CitationStyle.IEC)

# 2. Add source documents
doc = create_standard_metadata(
    standard_id="IEC 61730-1:2016",
    title="Photovoltaic (PV) module safety qualification - Part 1",
    organization="IEC",
    year=2016
)
manager.add_document(doc)

# 3. Process an LLM response
response_text = "Modules must meet IEC 61730 safety requirements."

retrieved_docs = [
    {
        'document_id': 'IEC 61730-1:2016',
        'content': 'Safety requirements for PV modules...',
        'score': 0.95,
        'metadata': {}
    }
]

result = manager.process_response(
    response_text=response_text,
    retrieved_documents=retrieved_docs
)

# 4. Get the cited response
print(result.text_with_citations)
print(result.reference_section)
```

### Output Example

```
Modules must meet IEC 61730 safety requirements[1].

References
==================================================

[1] IEC 61730-1:2016, Photovoltaic (PV) module safety qualification - Part 1
```

## Architecture

### Core Components

```
citation_manager/
├── citation_models.py      # Data models (Citation, DocumentMetadata, etc.)
├── citation_tracker.py     # Tracks citation numbers
├── citation_extractor.py   # Extracts citations from text
├── citation_formatter.py   # Formats citations in various styles
├── reference_tracker.py    # Manages document metadata
└── citation_manager.py     # Main orchestrator
```

### Data Flow

```
1. Documents → Reference Tracker (metadata storage)
2. LLM Response + Retrieved Docs → Citation Extractor
3. Extracted Citations → Citation Tracker (numbering)
4. Citations → Citation Formatter (style formatting)
5. Final Output: Response with inline citations + reference section
```

## Detailed Usage

### 1. Document Management

```python
from src.citation_manager import CitationManager, create_standard_metadata

manager = CitationManager()

# Add a single document
doc = create_standard_metadata(
    standard_id="IEC 61730-1:2016",
    title="PV module safety qualification",
    organization="IEC",
    year=2016,
    url="https://webstore.iec.ch/publication/26210"
)
manager.add_document(doc)

# Add multiple documents
docs = [
    create_standard_metadata("IEC 61730-1:2016", "PV safety - Part 1", "IEC"),
    create_standard_metadata("IEC 61730-2:2016", "PV safety - Part 2", "IEC"),
    create_standard_metadata("IEEE 1547-2018", "Grid interconnection", "IEEE")
]
manager.add_documents(docs)

# Retrieve a document
doc = manager.get_document("IEC 61730-1:2016")
print(doc.title)
```

### 2. Processing Responses

```python
# Simple response processing
response = "The module meets IEC 61730 requirements."

retrieved = [
    {
        'document_id': 'IEC 61730-1:2016',
        'content': 'Module construction requirements...',
        'score': 0.95,
        'metadata': {'page': 10}
    }
]

result = manager.process_response(response, retrieved)

print(result.text_with_citations)
print(result.reference_section)
```

### 3. Citation Styles

The Citation Manager supports multiple citation styles:

#### IEC Style (Default)
```
[1] IEC 61730-1:2016, Photovoltaic (PV) module safety qualification - Part 1
```

#### IEEE Style
```
[1] IEC 61730-1:2016, "Photovoltaic (PV) module safety qualification - Part 1."
```

#### ISO Style
```
[1] IEC 61730-1:2016, Photovoltaic (PV) module safety qualification - Part 1
```

#### APA Style
```
1. (2016). Photovoltaic (PV) module safety qualification - Part 1. IEC.
```

```python
from src.citation_manager import CitationStyle

# Change citation style
manager.set_citation_style(CitationStyle.IEEE)
result = manager.process_response(response, retrieved)
```

### 4. Extracting Standard IDs and Clauses

The Citation Extractor automatically identifies:

**Standard IDs:**
- IEC standards: `IEC 61730-1:2016`, `IEC 61215`
- IEEE standards: `IEEE 1547-2018`, `IEEE 802.3`
- ISO standards: `ISO 9001:2015`
- UL standards: `UL 1741`
- NEC standards: `NEC 690.7`

**Clause References:**
- Clauses: `Clause 5.2.1`, `Section 10.3`
- Annexes: `Annex A`, `Appendix B`
- Tables/Figures: `Table 3`, `Figure 5.2`

```python
from src.citation_manager import CitationExtractor

extractor = CitationExtractor()

text = "According to IEC 61730, Clause 10.2, modules must withstand mechanical loads."

# Extract standard IDs
standards = extractor.extract_standard_ids(text)
# Returns: [('IEC', 'IEC 61730')]

# Extract clause references
clauses = extractor.extract_clause_references(text)
# Returns: ['Clause 10.2']
```

### 5. Statistics and Tracking

```python
# Get usage statistics
stats = manager.get_statistics()

print(f"Total documents: {stats['total_documents']}")
print(f"Total citations: {stats['total_citations']}")
print(f"Responses processed: {stats['responses_processed']}")
print(f"Avg citations per doc: {stats['average_citations_per_document']}")
```

### 6. Export and Import

```python
# Export references to JSON
manager.export_references('references.json')

# Import references
new_manager = CitationManager()
new_manager.import_references('references.json')
```

## Advanced Features

### Custom Citation Formatting

```python
from src.citation_manager.citation_formatter import CitationFormatter
from src.citation_manager import CitationStyle

formatter = CitationFormatter(style=CitationStyle.IEC)

# Format inline citation
inline = formatter.format_inline_citation(citation)  # Returns: "[1]"

# Format reference entry
ref = formatter.format_reference_entry(citation, metadata)
```

### Manual Citation Creation

```python
from src.citation_manager import CitationTracker

tracker = CitationTracker()

# Create citations manually
citation1 = tracker.create_citation(
    document_id="IEC 61730-1:2016",
    matched_text="safety requirements",
    confidence=0.95
)

print(citation1.citation_number)  # 1
```

### Clause Reference Management

```python
from src.citation_manager.citation_models import ClauseReference

clause_ref = ClauseReference(
    document_id="IEC 61730-1:2016",
    clause_number="10.2.1",
    clause_title="Mechanical load testing",
    page_number=25,
    excerpt="The module shall withstand..."
)
```

## Integration with RAG Pipeline

The Citation Manager is designed to integrate seamlessly with RAG systems:

```python
# In your RAG pipeline:

def generate_response_with_citations(query: str, manager: CitationManager):
    # 1. Retrieve relevant documents
    retrieved_docs = vector_db.search(query, top_k=5)

    # 2. Generate LLM response
    context = "\n".join([doc['content'] for doc in retrieved_docs])
    llm_response = llm.generate(query, context)

    # 3. Process with citation manager
    result = manager.process_response(
        response_text=llm_response,
        retrieved_documents=retrieved_docs
    )

    # 4. Return cited response
    return {
        'answer': result.text_with_citations,
        'references': result.reference_section,
        'citations': result.citations_found
    }
```

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_citation_manager.py

# Run with coverage
pytest --cov=src/citation_manager tests/
```

### Run QA Demo

```bash
# Run the QA verification script
python tests/test_qa_demo.py
```

This will run comprehensive tests including:
- ✅ Basic safety requirements
- ✅ Multi-standard responses with clause references
- ✅ Citation style comparison
- ✅ Statistics and tracking
- ✅ Export/import functionality

## API Reference

### CitationManager

Main interface for all citation operations.

**Constructor:**
```python
CitationManager(
    style: CitationStyle = CitationStyle.IEC,
    auto_inject_citations: bool = True
)
```

**Key Methods:**
- `add_document(metadata: DocumentMetadata) -> str`
- `add_documents(documents: List[DocumentMetadata]) -> List[str]`
- `process_response(response_text, retrieved_documents, response_id=None) -> CitationExtractionResult`
- `set_citation_style(style: CitationStyle)`
- `get_statistics() -> Dict`
- `export_references(file_path: str)`
- `import_references(file_path: str)`

### CitationStyle Enum

Supported citation styles:
- `CitationStyle.IEC`
- `CitationStyle.IEEE`
- `CitationStyle.ISO`
- `CitationStyle.APA`

### Helper Functions

**create_standard_metadata()**
```python
create_standard_metadata(
    standard_id: str,
    title: str,
    organization: str = "IEC",
    year: Optional[int] = None,
    edition: Optional[str] = None,
    url: Optional[str] = None
) -> DocumentMetadata
```

## Examples

See the `tests/test_qa_demo.py` file for comprehensive examples including:
- Solar PV safety requirements
- Multi-standard responses
- Clause reference extraction
- Different citation styles
- Statistics tracking

## Limitations

- Citation matching uses keyword-based similarity (can be enhanced with embeddings)
- Assumes structured standard IDs (IEC, IEEE, ISO formats)
- Clause reference extraction uses regex patterns (may miss non-standard formats)

## Future Enhancements

- [ ] Semantic similarity matching for better citation accuracy
- [ ] Support for additional citation styles (Harvard, Chicago, etc.)
- [ ] Citation validation against source documents
- [ ] Automatic clause title extraction
- [ ] Multi-language support
- [ ] Citation impact tracking

## Contributing

Contributions are welcome! Please ensure:
1. All tests pass: `pytest tests/`
2. Code follows PEP 8 style guidelines
3. New features include unit tests
4. Documentation is updated

## License

This project is part of the Solar PV LLM AI system.

## Contact

For questions or issues, please open an issue on the project repository.
