# IEC PDF Ingestion Pipeline

Intelligent ingestion pipeline for IEC standards PDF documents with structure-preserving extraction, semantic chunking, and Q&A pair generation.

## Features

✅ **Structure-Preserving PDF Loading**
- Extracts text while maintaining document structure
- Preserves clause/section hierarchy
- Extracts tables and preserves layout

✅ **Intelligent Metadata Extraction**
- Standard ID (e.g., IEC 61730-1)
- Edition and publication year
- Clause numbers and titles
- Document hierarchy

✅ **Clause-Aware Semantic Chunking**
- Recursive character-based splitting
- Respects clause boundaries
- Configurable chunk size and overlap
- Maintains context at boundaries

✅ **Atomic Q&A Pair Generation**
- LLM-powered question generation (Anthropic/OpenAI)
- Factual, conceptual, and application questions
- Self-contained Q&A pairs for retrieval
- Keyword extraction

✅ **Structured JSON Storage**
- Complete metadata preservation
- Multiple export formats (JSON, JSONL)
- Chunk-only and Q&A-only exports
- Vector database ready

✅ **Comprehensive Validation**
- Chunk count and size validation
- Metadata completeness checks
- Parsing accuracy verification
- Quality metrics

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Solar-PV-LLM-AI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or for development:

```bash
pip install -e ".[dev]"
```

### 3. Set up API keys (for Q&A generation)

```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required environment variables:
- `ANTHROPIC_API_KEY` - For Claude-based Q&A generation
- `OPENAI_API_KEY` - For GPT-based Q&A generation (alternative)

## Quick Start

### Command Line Interface

#### Process a single PDF

```bash
python -m src.ingestion.cli ingest path/to/iec_standard.pdf
```

#### Process with custom configuration

```bash
python -m src.ingestion.cli ingest \
  path/to/iec_standard.pdf \
  --config config/ingestion_config.yaml \
  --chunk-size 1500 \
  --chunk-overlap 300
```

#### Process multiple PDFs

```bash
python -m src.ingestion.cli batch \
  path/to/pdf1.pdf \
  path/to/pdf2.pdf \
  path/to/pdf3.pdf
```

#### Validate processed document

```bash
python -m src.ingestion.cli validate data/output/IEC_61730-1_processed.json
```

#### View storage statistics

```bash
python -m src.ingestion.cli stats
```

### Python API

#### Simple usage

```python
from src.ingestion.api import quick_ingest

# Quick ingestion with defaults
document = quick_ingest("path/to/iec_standard.pdf")

print(f"Processed {len(document.chunks)} chunks")
print(f"Generated {document.get_total_qa_pairs()} Q&A pairs")
```

#### Advanced usage

```python
from src.ingestion.api import IECIngestionAPI
from src.ingestion.models import IngestionConfig

# Custom configuration
config = IngestionConfig(
    chunk_size=1500,
    chunk_overlap=300,
    clause_aware=True,
    qa_enabled=True,
    qa_provider="anthropic",
    qa_model="claude-3-haiku-20240307",
)

# Initialize API
api = IECIngestionAPI(config=config)

# Process document
document = api.ingest("path/to/iec_standard.pdf")

# Access data
for chunk in document.chunks:
    print(f"\nChunk {chunk.chunk_index}:")
    print(f"Clause: {chunk.clause_info.clause_number if chunk.clause_info else 'N/A'}")
    print(f"Content: {chunk.content[:100]}...")

    for qa in chunk.qa_pairs:
        print(f"  Q: {qa.question}")
        print(f"  A: {qa.answer}")

# Validate
validation = api.validate(document)
print(f"Valid: {validation['valid']}")

# Export formats
api.export_chunks(document, "chunks_for_vectordb.jsonl")
api.export_qa_pairs(document, "qa_training_data.jsonl")
```

#### Batch processing

```python
from src.ingestion.api import IECIngestionAPI

api = IECIngestionAPI()

pdf_files = [
    "iec_61730-1.pdf",
    "iec_61730-2.pdf",
    "iec_61215.pdf",
]

documents = api.ingest_batch(pdf_files)

for doc in documents:
    print(f"Processed: {doc.metadata.standard_id}")
    print(f"  Chunks: {len(doc.chunks)}")
    print(f"  Q&A pairs: {doc.get_total_qa_pairs()}")
```

#### Search and query

```python
from src.ingestion.api import IECIngestionAPI, load_document

# Load previously processed document
document = load_document("data/output/IEC_61730-1_processed.json")

api = IECIngestionAPI()

# Search for relevant chunks
chunks = api.search_chunks(document, "temperature testing requirements", top_k=5)

for chunk in chunks:
    print(chunk.content)

# Get all chunks for a specific clause
clause_chunks = api.get_chunks_by_clause(document, "4.2.1")

# Get document hierarchy
hierarchy = api.get_clause_hierarchy(document)
```

## Configuration

Configuration is managed through `config/ingestion_config.yaml`:

```yaml
# PDF Processing
pdf:
  extract_images: false
  extract_tables: true
  preserve_layout: true

# Chunking Strategy
chunking:
  strategy: 'recursive'
  chunk_size: 1000
  chunk_overlap: 200
  clause_aware: true
  min_chunk_size: 100
  max_chunk_size: 2000

# Q&A Generation
qa_generation:
  enabled: true
  provider: 'anthropic'
  model: 'claude-3-haiku-20240307'
  temperature: 0.7
  max_questions_per_chunk: 3

# Output
output:
  format: 'json'
  include_metadata: true
  include_source: true
  include_qa: true
  pretty_print: true
  output_dir: 'data/output'
```

## Output Schema

### Processed Document Structure

```json
{
  "document_id": "uuid",
  "metadata": {
    "standard_id": "IEC 61730-1",
    "standard_type": "IEC",
    "edition": "2.0",
    "year": 2023,
    "title": "Photovoltaic module safety qualification",
    "total_pages": 150,
    "file_path": "path/to/pdf"
  },
  "chunks": [
    {
      "chunk_id": "uuid",
      "content": "Full text content...",
      "clause_info": {
        "clause_number": "4.2.1",
        "title": "Temperature Testing",
        "level": 3,
        "parent_clause": "4.2"
      },
      "page_numbers": [45, 46],
      "char_count": 1250,
      "word_count": 187,
      "chunk_index": 42,
      "qa_pairs": [
        {
          "question": "What temperature range is specified for testing?",
          "answer": "The testing shall be conducted at -40°C to +85°C",
          "question_type": "factual",
          "keywords": ["temperature", "testing", "range"]
        }
      ]
    }
  ],
  "clauses": [...],
  "processing_stats": {
    "processing_time_seconds": 45.2,
    "total_chunks": 150,
    "total_clauses": 45,
    "qa_pairs_generated": 420
  }
}
```

## Architecture

```
src/ingestion/
├── models.py              # Pydantic data models
├── pdf_loader.py          # PDF extraction with structure preservation
├── metadata_extractor.py  # IEC metadata extraction
├── chunker.py            # Clause-aware semantic chunking
├── qa_generator.py       # LLM-based Q&A generation
├── storage.py            # JSON serialization and storage
├── pipeline.py           # Main orchestration pipeline
├── api.py                # Python API wrapper
├── cli.py                # Command-line interface
└── validation.py         # Validation utilities
```

## Validation

The pipeline includes comprehensive validation:

```python
from src.ingestion.api import IECIngestionAPI
from src.ingestion.validation import print_validation_report

api = IECIngestionAPI()
document = api.ingest("iec_standard.pdf")

# Validate
validation = api.validate(document)

# Print detailed report
print_validation_report(validation)
```

Validation checks:
- ✅ Chunk count and sizes
- ✅ Metadata completeness
- ✅ Clause coverage
- ✅ Q&A pair quality
- ✅ Content quality metrics
- ✅ Internal consistency

## Advanced Usage

### Custom Chunking Strategy

```python
from src.ingestion.chunker import ClauseAwareChunker
from src.ingestion.pdf_loader import IECPDFLoader

# Load PDF
loader = IECPDFLoader()
text, clauses, metadata = loader.load("iec_standard.pdf")

# Custom chunking
chunker = ClauseAwareChunker(
    chunk_size=2000,
    chunk_overlap=400,
    clause_aware=True,
)

chunks = chunker.chunk_document(text, clauses, metadata)
```

### Custom Q&A Generation

```python
from src.ingestion.qa_generator import QAGenerator

generator = QAGenerator(
    provider="anthropic",
    model="claude-3-sonnet-20240229",  # More powerful model
    temperature=0.5,
    max_questions_per_chunk=5,
)

qa_pairs = generator.generate_qa_pairs(chunk, metadata)
```

### Export for Vector Databases

```python
from src.ingestion.api import IECIngestionAPI

api = IECIngestionAPI()
document = api.ingest("iec_standard.pdf")

# Export chunks in vector DB friendly format
chunks_file = api.export_chunks(document)

# Each line is a JSON object with:
# - chunk_id
# - content
# - metadata (standard_id, clause_number, page_numbers, etc.)
# - qa_pairs
```

## Testing

Run tests:

```bash
pytest tests/
```

With coverage:

```bash
pytest --cov=src --cov-report=html
```

## Performance

Typical processing times (on standard hardware):

- **PDF Loading**: 5-15 seconds
- **Chunking**: 2-5 seconds
- **Q&A Generation**: 30-120 seconds (depends on document size and LLM)
- **Total**: ~1-2 minutes per document

## Troubleshooting

### Q&A Generation Not Working

1. Check API keys are set:
   ```bash
   echo $ANTHROPIC_API_KEY
   ```

2. Disable Q&A temporarily:
   ```bash
   python -m src.ingestion.cli ingest document.pdf --skip-qa
   ```

### Poor Clause Detection

- Check if document follows standard IEC formatting
- Adjust regex patterns in `config/ingestion_config.yaml`
- Set `clause_aware: false` to use pure semantic chunking

### Memory Issues with Large PDFs

- Process in batch with smaller documents
- Reduce chunk size
- Disable Q&A generation during initial processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review example code in `/examples`
