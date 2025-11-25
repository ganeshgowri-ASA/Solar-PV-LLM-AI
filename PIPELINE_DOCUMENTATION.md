# IEC PDF Ingestion Pipeline Documentation

## Overview

The IEC PDF Ingestion Pipeline is a comprehensive system for processing IEC (International Electrotechnical Commission) standard documents, specifically designed for Solar PV standards. It extracts structured information, creates intelligent chunks, generates Q&A pairs, and stores everything in a structured JSON format optimized for RAG (Retrieval-Augmented Generation) systems.

## Features

- **PDF Loading**: Preserves section/clause structure from IEC standards
- **Metadata Extraction**: Automatically extracts standard ID, edition, year, clause numbers, and titles
- **Intelligent Chunking**: Recursive semantic chunking with clause-aware overlap
- **Q&A Generation**: Creates atomic question-answer pairs for each chunk (using OpenAI or rule-based fallback)
- **Structured Storage**: Saves processed data in JSON with comprehensive metadata
- **CLI Interface**: Easy-to-use command-line interface
- **Python API**: Programmatic access for integration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IEC PDF Document                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              1. PDF Loader (pdfplumber)                      │
│  - Extract text with structure                               │
│  - Identify clause headers                                   │
│  - Preserve page information                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         2. Metadata Extraction                               │
│  - Standard ID (IEC 61215-1)                                 │
│  - Edition, Year                                             │
│  - Clause structure                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         3. Semantic Chunking                                 │
│  - Respect clause boundaries                                 │
│  - Recursive splitting (paragraphs → sentences → words)      │
│  - Configurable overlap                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         4. Q&A Generation                                    │
│  - OpenAI GPT-4 (if API key provided)                        │
│  - Rule-based fallback                                       │
│  - Multiple question types                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         5. JSON Storage                                      │
│  - Complete metadata                                         │
│  - Chunk text + Q&A pairs                                    │
│  - Retrieval-optimized format                                │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Solar-PV-LLM-AI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Configure OpenAI API key for Q&A generation:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## CLI Usage

### Process a Single PDF

```bash
./ingest_iec_pdf.py process /path/to/IEC_61215-1.pdf
```

**Options:**
- `--output-dir, -o`: Output directory (default: `data/processed`)
- `--chunk-size, -s`: Target chunk size in characters (default: 1000)
- `--chunk-overlap`: Overlap between chunks (default: 200)
- `--no-qa`: Disable Q&A generation
- `--save-intermediate`: Save additional formats (retrieval, Q&A-only)
- `--output-filename`: Custom output filename

**Example with options:**
```bash
./ingest_iec_pdf.py process IEC_61215-1.pdf \
  --output-dir ./output \
  --chunk-size 800 \
  --chunk-overlap 150 \
  --save-intermediate
```

### Batch Processing

Process multiple PDFs:

```bash
./ingest_iec_pdf.py batch pdf1.pdf pdf2.pdf pdf3.pdf
```

### Validate Processed Document

```bash
./ingest_iec_pdf.py validate data/processed/IEC_61215-1.json
```

### List Processed Documents

```bash
./ingest_iec_pdf.py list-documents
```

### View Statistics

```bash
./ingest_iec_pdf.py stats data/processed/IEC_61215-1.json
```

## Python API Usage

### Basic Pipeline

```python
from src.pipeline import create_pipeline

# Create pipeline with default settings
pipeline = create_pipeline()

# Process a PDF
result = pipeline.process_pdf("path/to/IEC_61215-1.pdf")

print(f"Created {result['statistics']['total_chunks']} chunks")
print(f"Generated {result['statistics']['total_qa_pairs']} Q&A pairs")
```

### Custom Configuration

```python
from src.pipeline import create_pipeline

# Create pipeline with custom settings
pipeline = create_pipeline(
    chunk_size=800,
    chunk_overlap=150,
    enable_qa=True,
    output_dir="./my_output"
)

# Process with intermediate files
result = pipeline.process_pdf(
    pdf_path="IEC_61215-1.pdf",
    save_intermediate=True
)
```

### Using Individual Components

```python
from src.ingestion import IECPDFLoader
from src.metadata import IECMetadataExtractor
from src.chunking import SemanticChunker, ChunkConfig

# Load PDF
loader = IECPDFLoader()
pdf_data, sections = loader.load_and_structure("document.pdf")

# Extract metadata
extractor = IECMetadataExtractor()
doc_metadata = extractor.extract_document_metadata(pdf_data['text'])

# Chunk text
config = ChunkConfig(chunk_size=1000, chunk_overlap=200)
chunker = SemanticChunker(config)
chunks = chunker.chunk_section(
    sections[0].content,
    sections[0].clause_number,
    sections[0].clause_title
)
```

## Output Format

### Main JSON Structure

```json
{
  "document_metadata": {
    "source_file": "IEC_61215-1_2021.pdf",
    "iec_metadata": {
      "standard_id": "IEC 61215-1",
      "edition": "4.0",
      "year": 2021,
      "title": "Terrestrial photovoltaic (PV) modules",
      "keywords": ["photovoltaic", "PV", "modules"]
    },
    "total_chunks": 156,
    "total_pages": 48,
    "total_characters": 89234,
    "chunk_statistics": {
      "avg_chunk_size": 572,
      "min_chunk_size": 100,
      "max_chunk_size": 1200
    }
  },
  "chunks": [
    {
      "text": "The thermal cycling test subjects the module to...",
      "metadata": {
        "document": { ... },
        "clause": {
          "clause_number": "5.2.3",
          "clause_title": "Thermal cycling test",
          "parent_clause": "5.2",
          "level": 3,
          "section_type": "clause"
        },
        "chunk_id": "iec-61215-1_chunk_042",
        "chunk_index": 42,
        "page_numbers": [15, 16],
        "char_count": 856,
        "word_count": 142
      },
      "qa_pairs": [
        {
          "question": "What temperature range is used in the thermal cycling test?",
          "answer": "The test uses temperatures from -40°C to +85°C",
          "chunk_id": "iec-61215-1_chunk_042",
          "confidence": 0.92,
          "question_type": "factual"
        }
      ]
    }
  ]
}
```

## Configuration

### Chunking Configuration

- `chunk_size`: Target size in characters (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)
- `min_chunk_size`: Minimum chunk size (default: 100)
- `max_chunk_size`: Maximum chunk size (default: 2000)
- `respect_clause_boundaries`: Don't split clauses (default: True)
- `respect_sentence_boundaries`: Split on sentences (default: True)
- `respect_paragraph_boundaries`: Prefer paragraph splits (default: True)

### Q&A Generation Configuration

- `model`: OpenAI model to use (default: "gpt-4-turbo-preview")
- `max_questions_per_chunk`: Maximum Q&A pairs per chunk (default: 3)
- `min_confidence`: Minimum confidence score (default: 0.7)
- `temperature`: Generation temperature (default: 0.3)
- `generate_diverse_types`: Generate varied question types (default: True)

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run specific tests:

```bash
pytest tests/test_metadata.py -v
pytest tests/test_pipeline.py -v
```

## Validation

The pipeline includes built-in validation:

```python
# Programmatically
validation = pipeline.validate_processing("output.json")

if validation['valid']:
    print("✓ All checks passed")
else:
    print("Errors:", validation['errors'])
    print("Warnings:", validation['warnings'])
```

**Validation checks:**
- Chunk count > 0
- Metadata completeness
- Standard ID present
- Q&A pair coverage
- No empty chunks

## Performance

**Typical processing times:**
- Small document (20 pages): ~30-60 seconds
- Medium document (50 pages): ~1-2 minutes
- Large document (100+ pages): ~3-5 minutes

*Note: Time varies based on Q&A generation (OpenAI API calls add latency)*

## Troubleshooting

### No Q&A pairs generated

- Check OpenAI API key in `.env`
- Ensure `openai` package is installed
- Pipeline will use rule-based fallback if API unavailable

### PDF not loading

- Ensure PDF is not encrypted
- Check file permissions
- Try with a different PDF reader if extraction fails

### Low chunk count

- Adjust `chunk_size` parameter
- Check if PDF has extractable text (not scanned image)

## Examples

See `examples/` directory for:
- Sample processing scripts
- Custom pipeline configurations
- Integration examples

## License

[Your License Here]

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.
