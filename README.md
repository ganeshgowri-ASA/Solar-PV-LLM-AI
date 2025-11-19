# Solar-PV-LLM-AI

Repository for developing Solar PV AI LLM system with incremental training, RAG, citation, and autonomous delivery. Built for broad audiences from beginners to experts.

## IEC PDF Ingestion Pipeline

A comprehensive pipeline for processing IEC (International Electrotechnical Commission) standard documents with intelligent chunking, metadata extraction, and Q&A generation optimized for RAG systems.

### Features

- **Intelligent PDF Loading**: Preserves section/clause structure from IEC standards
- **Metadata Extraction**: Automatically extracts standard ID, edition, year, clause numbers, and titles
- **Semantic Chunking**: Recursive chunking with clause-aware overlap
- **Q&A Generation**: Creates atomic question-answer pairs for each chunk
- **Structured Storage**: JSON output with comprehensive metadata
- **CLI & Python API**: Easy-to-use interfaces for both command-line and programmatic access

### Quick Start

#### Installation

```bash
# Clone repository
git clone https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI

# Install dependencies
pip install -r requirements.txt

# (Optional) Configure OpenAI API for Q&A generation
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

#### CLI Usage

Process a single IEC PDF:

```bash
./ingest_iec_pdf.py process /path/to/IEC_standard.pdf
```

Process multiple PDFs:

```bash
./ingest_iec_pdf.py batch pdf1.pdf pdf2.pdf pdf3.pdf
```

Validate processed output:

```bash
./ingest_iec_pdf.py validate data/processed/output.json
```

List all processed documents:

```bash
./ingest_iec_pdf.py list-documents
```

#### Python API Usage

```python
from src.pipeline import create_pipeline

# Create pipeline
pipeline = create_pipeline(
    chunk_size=1000,
    chunk_overlap=200,
    enable_qa=True
)

# Process PDF
result = pipeline.process_pdf("IEC_61215-1.pdf")

print(f"Created {result['statistics']['total_chunks']} chunks")
print(f"Generated {result['statistics']['total_qa_pairs']} Q&A pairs")
```

### Pipeline Architecture

```
PDF → Load & Structure → Metadata Extraction → Semantic Chunking → Q&A Generation → JSON Storage
```

**Components:**
1. **PDF Loader**: Extracts text while preserving clause structure
2. **Metadata Extractor**: Identifies standard ID, edition, year, clauses
3. **Semantic Chunker**: Creates intelligent chunks respecting boundaries
4. **Q&A Generator**: Generates question-answer pairs (OpenAI or rule-based)
5. **JSON Storage**: Saves structured output with complete metadata

### Output Format

```json
{
  "document_metadata": {
    "source_file": "IEC_61215-1.pdf",
    "iec_metadata": {
      "standard_id": "IEC 61215-1",
      "edition": "4.0",
      "year": 2021,
      "title": "Terrestrial photovoltaic (PV) modules"
    },
    "total_chunks": 156,
    "total_pages": 48
  },
  "chunks": [
    {
      "text": "...",
      "metadata": {
        "chunk_id": "iec-61215-1_chunk_001",
        "clause": {
          "clause_number": "5.2.3",
          "clause_title": "Thermal cycling test"
        },
        "page_numbers": [15, 16]
      },
      "qa_pairs": [
        {
          "question": "What is the temperature range for thermal cycling?",
          "answer": "-40°C to +85°C",
          "confidence": 0.92,
          "question_type": "factual"
        }
      ]
    }
  ]
}
```

### Configuration

**Chunking:**
- `chunk_size`: Target chunk size (default: 1000 chars)
- `chunk_overlap`: Overlap between chunks (default: 200 chars)
- `respect_clause_boundaries`: Don't split clauses (default: True)

**Q&A Generation:**
- `model`: OpenAI model (default: "gpt-4-turbo-preview")
- `max_questions_per_chunk`: Max Q&A pairs per chunk (default: 3)
- `min_confidence`: Minimum confidence score (default: 0.7)

### Documentation

- [Complete Pipeline Documentation](PIPELINE_DOCUMENTATION.md)
- [Examples](examples/)
  - [Basic Usage](examples/basic_usage.py)
  - [Advanced Usage](examples/advanced_usage.py)

### Testing

Run tests:

```bash
pytest tests/ -v
```

### Project Structure

```
Solar-PV-LLM-AI/
├── src/
│   ├── ingestion/          # PDF loading and structure extraction
│   ├── metadata/           # Metadata schemas and extraction
│   ├── chunking/           # Semantic chunking logic
│   ├── qa_generation/      # Q&A pair generation
│   ├── storage/            # JSON storage and retrieval
│   └── pipeline.py         # Main pipeline orchestrator
├── tests/                  # Test suite
├── examples/               # Usage examples
├── data/
│   ├── raw/               # Input PDFs
│   └── processed/         # Output JSON files
├── ingest_iec_pdf.py      # CLI script
├── requirements.txt
└── README.md
```

### Requirements

- Python 3.8+
- pdfplumber, PyPDF2 (PDF processing)
- OpenAI API key (optional, for Q&A generation)
- See `requirements.txt` for complete list

### Validation

Built-in validation checks:
- Chunk count and completeness
- Metadata extraction accuracy
- Q&A pair coverage
- No empty chunks

```bash
./ingest_iec_pdf.py validate output.json
```

### Performance

Typical processing times:
- Small (20 pages): ~30-60s
- Medium (50 pages): ~1-2min
- Large (100+ pages): ~3-5min

### Contributing

Contributions welcome! Please see issues and pull requests.

### License

[Your License Here]

### Contact

For questions or issues, please open an issue on GitHub.

---

**Note**: This pipeline is specifically designed for IEC standards but can be adapted for other technical documents with similar structure.
