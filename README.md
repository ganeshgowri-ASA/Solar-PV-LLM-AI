# Solar PV LLM AI System

Repository for developing a comprehensive Solar PV AI LLM system with incremental training, RAG (Retrieval-Augmented Generation), citation management, and autonomous delivery. Built for broad audiences from beginners to experts.

## Overview

The Solar PV LLM AI System is designed to provide accurate, citation-backed answers to questions about solar photovoltaic systems, standards, and best practices. The system combines:

- **RAG Architecture** - Retrieval-augmented generation for accurate, source-based responses
- **Citation Management** - Automatic extraction, tracking, and formatting of citations
- **Multi-Standard Support** - IEC, IEEE, ISO, ASTM, and other industry standards
- **Flexible Citation Styles** - IEC, IEEE, and APA formatting

## Features

### Current Release (v0.1.0)

#### ✅ Citation Management System
- **Citation Tracker** - Sequential citation numbering with persistence options
- **Metadata Extraction** - Automatic extraction of standard IDs, clause references, years, and titles
- **Inline Citation Injection** - Smart injection of citation markers into LLM responses
- **Multi-Format Support** - IEC, IEEE, and APA citation styles
- **Reference Validation** - Validate citations and check for consistency
- **Comprehensive Testing** - Full unit test coverage and QA verification

### Supported Standards

The system recognizes and extracts citations from:
- **IEC** (International Electrotechnical Commission) - e.g., IEC 61215, IEC 61730
- **ISO** (International Organization for Standardization) - e.g., ISO 9001
- **IEEE** (Institute of Electrical and Electronics Engineers) - e.g., IEEE 1547
- **ASTM** (American Society for Testing and Materials) - e.g., ASTM E1036
- **EN** (European Standards) - e.g., EN 50530
- **UL** (Underwriters Laboratories) - e.g., UL 1741

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Basic Usage

```python
from citations import CitationManager, RetrievedDocument

# Initialize citation manager
manager = CitationManager()

# Sample LLM response
llm_response = "Solar modules must meet IEC 61215 testing standards."

# Sample retrieved documents from RAG
retrieved_docs = [
    RetrievedDocument(
        content="IEC 61215 defines testing requirements for PV modules.",
        metadata={
            'standard_id': 'IEC 61215',
            'title': 'Terrestrial PV modules - Design qualification',
            'year': '2021',
            'clause': 'Clause 5.2'
        },
        doc_id="doc_1",
        score=0.9
    )
]

# Process response with citations
processed_response, citations = manager.process_response(
    llm_response,
    retrieved_docs,
    inject_citations=True
)

# Format references in IEC style
references = manager.format_references(style='iec')

print(processed_response)  # "Solar modules must meet IEC 61215[1] testing standards."
print(references)
# References
# ==================================================
# [1] IEC 61215, "Terrestrial PV modules - Design qualification", 2021, Clause 5.2.
```

## Running Tests

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run citation tests only
pytest tests/test_citations/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### QA Verification

```bash
# Run comprehensive QA verification
python tests/qa_verification.py
```

This will verify:
- Citation extraction accuracy
- Multiple citation format support
- Clause reference extraction
- Citation number persistence
- Real-world scenario handling

## Project Structure

```
Solar-PV-LLM-AI/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── setup.py                     # Package configuration
├── pytest.ini                   # Pytest configuration
├── .gitignore                   # Git ignore rules
│
├── src/                         # Source code
│   ├── __init__.py
│   ├── citations/               # Citation management module
│   │   ├── __init__.py
│   │   ├── README.md           # Citation module documentation
│   │   ├── citation_manager.py  # Main orchestration
│   │   ├── citation_extractor.py # Metadata extraction
│   │   ├── citation_injector.py  # Inline citation injection
│   │   ├── citation_formatter.py # Multi-format support
│   │   └── reference_manager.py  # Reference validation
│   │
│   ├── retrieval/               # RAG components (planned)
│   ├── llm/                     # LLM integration (planned)
│   └── utils/                   # Utility functions
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── qa_verification.py      # QA verification script
│   └── test_citations/         # Citation tests
│       ├── __init__.py
│       ├── test_citation_manager.py
│       ├── test_citation_extractor.py
│       ├── test_citation_injector.py
│       ├── test_citation_formatter.py
│       └── test_reference_manager.py
│
├── data/                        # Data storage
│   ├── raw/                    # Original documents
│   ├── processed/              # Processed documents
│   └── vector_db/              # Vector database
│
├── config/                      # Configuration files
└── notebooks/                   # Jupyter notebooks
```

## Citation Formats

### IEC Style (Default)
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

## Documentation

- [Citation Manager Documentation](src/citations/README.md) - Comprehensive guide to the citation system
- [Testing Guide](tests/test_citations/) - Unit test documentation
- [QA Verification](tests/qa_verification.py) - QA test scenarios

## Development Roadmap

### Phase 1: Citation Management ✅ (Current)
- [x] Citation tracker with sequential numbering
- [x] Metadata extraction (standards, clauses, years)
- [x] Inline citation injection
- [x] Multiple citation formats (IEC, IEEE, APA)
- [x] Reference validation
- [x] Comprehensive unit tests
- [x] QA verification

### Phase 2: Document Processing (Planned)
- [ ] PDF parsing and extraction
- [ ] Text chunking for RAG
- [ ] Metadata extraction from documents
- [ ] Document preprocessing pipeline

### Phase 3: RAG Implementation (Planned)
- [ ] Vector database integration
- [ ] Embedding generation
- [ ] Semantic search
- [ ] Relevance ranking
- [ ] Context window management

### Phase 4: LLM Integration (Planned)
- [ ] OpenAI integration
- [ ] Anthropic integration
- [ ] Prompt engineering
- [ ] Response generation
- [ ] Context-aware responses

### Phase 5: Advanced Features (Planned)
- [ ] Multi-language support
- [ ] Incremental learning
- [ ] User feedback integration
- [ ] Web interface
- [ ] API endpoints

## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest tests/ -v`)
6. Run QA verification (`python tests/qa_verification.py`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Write unit tests for new features
- Update documentation as needed

## Testing Philosophy

All code must include:
1. **Unit tests** - Test individual components
2. **Integration tests** - Test component interactions
3. **QA verification** - Test real-world scenarios
4. **Documentation** - Clear usage examples

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- International Electrotechnical Commission (IEC) for standardization
- Solar PV industry standards organizations
- Open-source AI and ML communities

## Contact

For questions, issues, or contributions:
- GitHub Issues: [Solar-PV-LLM-AI/issues](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/issues)
- Repository: [Solar-PV-LLM-AI](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI)

## Version History

### v0.1.0 (Current)
- Initial release
- Citation management system
- Support for IEC, IEEE, ISO, ASTM, EN, and UL standards
- IEC, IEEE, and APA citation formatting
- Comprehensive test suite
- QA verification script

---

**Built for the Solar PV community** - From beginners to experts, this system aims to provide accurate, citation-backed information about solar photovoltaic technologies.
