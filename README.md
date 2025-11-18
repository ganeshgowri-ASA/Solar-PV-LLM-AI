# Solar-PV-LLM-AI

Repository for developing Solar PV AI LLM system with incremental training, RAG, citation, and autonomous delivery. Built for broad audiences from beginners to experts.

## 🚀 Features

- **Vector Store Integration**: Pinecone-based vector database with OpenAI embeddings
- **Intelligent Search**: Semantic similarity search with Solar PV specific filtering
- **Document Ingestion**: Batch processing of Solar PV technical documents
- **RESTful API**: FastAPI-based endpoints for all vector operations
- **Comprehensive Logging**: Structured logging with detailed error tracking
- **QA Testing**: Complete test suite for validation

## 📋 Quick Start

### Prerequisites

- Python 3.8+
- Pinecone API key
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
```

2. Create and configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the server:
```bash
chmod +x run_server.sh
./run_server.sh
```

The API will be available at http://localhost:8000 with interactive docs at http://localhost:8000/docs

### Quick Test

Run the QA test suite:
```bash
python tests/test_vector_store.py
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI REST API                       │
│         /ingest  |  /search  |  /delete  |  /stats          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                   ┌───────▼────────┐
                   │ Vector Store   │
                   │    Handler     │
                   └────┬──────┬────┘
                        │      │
          ┌─────────────┘      └─────────────┐
          │                                   │
   ┌──────▼──────┐                    ┌──────▼──────┐
   │  Embedding  │                    │  Pinecone   │
   │   Service   │                    │   Client    │
   │  (OpenAI)   │                    │  (Vectors)  │
   └─────────────┘                    └─────────────┘
```

## 📚 Documentation

- [Vector Store Integration Guide](VECTOR_STORE_INTEGRATION.md) - Comprehensive documentation
- [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI (when server is running)

## 🔑 Key Technologies

- **Pinecone**: Serverless vector database with cosine similarity
- **OpenAI**: text-embedding-3-large (1536 dimensions)
- **FastAPI**: Modern, fast web framework for APIs
- **Pydantic**: Data validation using Python type annotations

## 📊 Supported Filters

The system supports Solar PV specific metadata filtering:

- `standards`: IEC 61215, IEC 61730, IEC 62804, etc.
- `clauses`: MQT 11, MST 09, etc.
- `test_type`: performance, safety, reliability
- `category`: Custom categorization

## 🧪 Example Usage

### Python Client Example

```python
from src.vector_store.handler import VectorStoreHandler

# Initialize handler
handler = VectorStoreHandler()

# Ingest documents
documents = [
    {
        "text": "IEC 61215 thermal cycling test...",
        "metadata": {
            "standards": "IEC 61215",
            "test_type": "reliability"
        }
    }
]
handler.ingest_documents(documents)

# Search with filters
results = handler.search_with_filters(
    query="thermal testing requirements",
    standards="IEC 61215",
    test_type="reliability"
)
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/v1/search/filtered" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "thermal cycling test",
    "top_k": 5,
    "standards": "IEC 61215",
    "test_type": "reliability"
  }'
```

## 🔧 Development

### Project Structure

```
Solar-PV-LLM-AI/
├── src/
│   ├── api/              # API routes and models
│   ├── config/           # Configuration management
│   ├── logging/          # Logging setup
│   ├── utils/            # Utilities and errors
│   ├── vector_store/     # Vector store implementation
│   └── main.py           # Application entry point
├── tests/                # Test suite
├── sample_docs/          # Sample Solar PV documents
└── requirements.txt      # Python dependencies
```

### Running Tests

```bash
# Run QA test suite
python tests/test_vector_store.py

# Expected: All tests pass with verification of:
# - Document ingestion
# - Similarity search
# - Filter correctness
# - Deletion operations
# - Index statistics
```

## 🎯 Roadmap

- [x] Vector store integration with Pinecone
- [x] OpenAI embedding generation
- [x] Batch document ingestion
- [x] Similarity search with filtering
- [x] RESTful API endpoints
- [ ] RAG pipeline integration
- [ ] LLM-based question answering
- [ ] Citation tracking
- [ ] Multi-modal support
- [ ] Authentication and authorization
- [ ] Production monitoring

## 📖 Use Cases

1. **Solar PV Standards Search**: Query across IEC standards with semantic understanding
2. **Test Procedure Discovery**: Find relevant test procedures by description
3. **Compliance Checking**: Filter by standards and test types
4. **Knowledge Management**: Centralized Solar PV technical knowledge base
5. **RAG Applications**: Foundation for question-answering systems

## 🤝 Contributing

Contributions are welcome! Please see our contributing guidelines.

## 📝 License

See LICENSE file for details.

## 🔗 Links

- [Pinecone Documentation](https://docs.pinecone.io/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 📧 Support

For issues or questions, please open an issue on GitHub.
