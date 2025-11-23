# Quick Start Guide - IEC PDF Ingestion Pipeline

## 5-Minute Quick Start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. (Optional) Add OpenAI API Key

```bash
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...
```

### 3. Process Your First PDF

```bash
./ingest_iec_pdf.py process /path/to/your/IEC_standard.pdf
```

That's it! Your processed document will be in `data/processed/`

---

## CLI Commands Cheat Sheet

### Process Single PDF
```bash
./ingest_iec_pdf.py process document.pdf
```

### Process with Custom Settings
```bash
./ingest_iec_pdf.py process document.pdf \
  --chunk-size 800 \
  --chunk-overlap 150 \
  --output-dir ./my_output
```

### Batch Process
```bash
./ingest_iec_pdf.py batch pdf1.pdf pdf2.pdf pdf3.pdf
```

### Validate Output
```bash
./ingest_iec_pdf.py validate data/processed/output.json
```

### List Processed Documents
```bash
./ingest_iec_pdf.py list-documents
```

### View Statistics
```bash
./ingest_iec_pdf.py stats data/processed/output.json
```

---

## Python API Quick Examples

### Basic Usage
```python
from src.pipeline import create_pipeline

pipeline = create_pipeline()
result = pipeline.process_pdf("document.pdf")
```

### Custom Configuration
```python
pipeline = create_pipeline(
    chunk_size=800,
    chunk_overlap=150,
    enable_qa=True
)
result = pipeline.process_pdf("document.pdf")
```

### Access Results
```python
print(f"Chunks: {result['statistics']['total_chunks']}")
print(f"Q&A pairs: {result['statistics']['total_qa_pairs']}")
print(f"Output: {result['output_path']}")
```

---

## Common Options

| Option | Default | Description |
|--------|---------|-------------|
| `--chunk-size` | 1000 | Target chunk size in characters |
| `--chunk-overlap` | 200 | Overlap between chunks |
| `--output-dir` | data/processed | Output directory |
| `--no-qa` | False | Disable Q&A generation |
| `--save-intermediate` | False | Save additional formats |

---

## Output Structure

Your processed document will be saved as JSON:

```
data/processed/
└── IEC-61215-1_20250119_120000.json
```

Contains:
- Document metadata (standard ID, edition, year)
- Chunks with text and metadata
- Q&A pairs for each chunk
- Page references
- Clause information

---

## Next Steps

1. **Read full documentation**: [PIPELINE_DOCUMENTATION.md](PIPELINE_DOCUMENTATION.md)
2. **Explore examples**: [examples/](examples/)
3. **Run tests**: `pytest tests/ -v`
4. **Customize for your needs**: Modify chunking and Q&A settings

---

## Troubleshooting

**No Q&A pairs?**
- Add OpenAI API key to `.env` or use `--no-qa` for rule-based generation

**PDF not loading?**
- Ensure PDF is not encrypted
- Check file exists and has read permissions

**Chunks too large/small?**
- Adjust `--chunk-size` parameter

---

## Support

- Documentation: [PIPELINE_DOCUMENTATION.md](PIPELINE_DOCUMENTATION.md)
- Examples: [examples/](examples/)
- Issues: GitHub Issues
