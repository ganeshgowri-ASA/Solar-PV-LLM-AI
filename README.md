# Solar-PV-LLM-AI

Repository for developing Solar PV AI LLM system with incremental training, RAG, citation, and autonomous delivery. Built for broad audiences from beginners to experts.

## Features

🚀 **IEC PDF Ingestion Pipeline** - Now Available!
- Structure-preserving PDF extraction
- Intelligent clause-aware chunking
- Metadata extraction (standard ID, edition, year, clauses)
- Atomic Q&A pair generation for retrieval
- Comprehensive validation and QA

📚 **Coming Soon**
- RAG (Retrieval Augmented Generation) system
- Incremental model training
- Citation and attribution system
- Autonomous delivery mechanisms

## Quick Start

### IEC PDF Ingestion

Process IEC standards PDFs with intelligent chunking and Q&A generation:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys (for Q&A generation)
cp .env.example .env
# Edit .env with your API keys

# Process a PDF
python -m src.ingestion.cli ingest path/to/iec_standard.pdf

# Or use Python API
python
>>> from src.ingestion.api import quick_ingest
>>> document = quick_ingest("path/to/iec_standard.pdf")
>>> print(f"Created {len(document.chunks)} chunks")
```

See [INGESTION_README.md](INGESTION_README.md) for complete documentation.

## Project Structure

```
Solar-PV-LLM-AI/
├── src/
│   └── ingestion/         # IEC PDF ingestion pipeline
│       ├── models.py      # Data models
│       ├── pdf_loader.py  # PDF extraction
│       ├── chunker.py     # Semantic chunking
│       ├── qa_generator.py # Q&A generation
│       ├── cli.py         # Command-line interface
│       └── api.py         # Python API
├── config/                # Configuration files
├── data/                  # Data storage
│   ├── raw/              # Input PDFs
│   ├── processed/        # Intermediate data
│   └── output/           # Final outputs
├── examples/             # Usage examples
└── tests/                # Test suite

## Documentation

- [Ingestion Pipeline Documentation](INGESTION_README.md)
- [Configuration Guide](config/ingestion_config.yaml)
- [Python API Examples](examples/)

## Development Status

- ✅ **Phase 1**: IEC PDF Ingestion Pipeline - **COMPLETE**
- 🔄 **Phase 2**: RAG System - In Planning
- 📋 **Phase 3**: Incremental Training - Planned
- 📋 **Phase 4**: Citation System - Planned
- 📋 **Phase 5**: Autonomous Delivery - Planned

## Requirements

- Python 3.9+
- See [requirements.txt](requirements.txt) for dependencies

## Contributing

Contributions welcome! Please see our contributing guidelines.

## License

MIT License - See LICENSE file for details.
