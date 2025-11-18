# Solar-PV-LLM-AI

Repository for developing Solar PV AI LLM system with incremental training, RAG, citation, and autonomous delivery. Built for broad audiences from beginners to experts.

## 🚀 RAG Engine Core

A comprehensive **Retrieval Augmented Generation (RAG)** engine featuring:

- ✅ **Hybrid Retrieval**: Combines semantic vector search + BM25 keyword search
- ✅ **Advanced Re-ranking**: Cohere API and Cross-Encoder support
- ✅ **HyDE (Hypothetical Document Embeddings)**: Query enhancement technique
- ✅ **Multiple Vector Stores**: ChromaDB and FAISS backends
- ✅ **Flexible Configuration**: Environment-based or programmatic setup
- ✅ **Production Ready**: Comprehensive testing and examples

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Testing](#testing)
- [API Reference](#api-reference)

## 🎯 Features

### Retrieval Methods

1. **Vector Similarity Search**
   - Semantic search using sentence-transformers
   - ChromaDB or FAISS backends
   - Cosine similarity scoring

2. **BM25 Keyword Search**
   - Statistical keyword ranking
   - Fast and efficient
   - Complementary to semantic search

3. **Hybrid Retrieval**
   - Reciprocal Rank Fusion (RRF)
   - Weighted score fusion
   - Configurable alpha weighting

### Re-ranking

1. **Cohere Re-ranker**
   - State-of-the-art relevance scoring
   - API-based (requires key)
   - Model: `rerank-english-v3.0`

2. **Cross-Encoder Re-ranker**
   - Local model execution
   - No API required
   - Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`

### Query Enhancement

- **HyDE (Hypothetical Document Embeddings)**
  - Generates hypothetical answers using LLM
  - Bridges semantic gap between queries and documents
  - Improves retrieval for complex queries

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI

# Install dependencies
pip install -r requirements.txt
```

### Optional Dependencies

```bash
# For GPU acceleration (FAISS)
pip install faiss-gpu

# For development
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

## 🚀 Quick Start

### Basic Usage

```python
from src.rag_engine.pipeline.rag_pipeline import RAGPipeline
from src.rag_engine.utils.data_models import Document

# Initialize pipeline
pipeline = RAGPipeline()

# Add documents
documents = [
    Document(
        id="doc1",
        content="Solar panels convert sunlight into electricity using photovoltaic cells.",
        metadata={"source": "solar_guide.pdf", "page": 1}
    ),
    Document(
        id="doc2",
        content="Solar panel efficiency typically ranges from 15% to 22%.",
        metadata={"source": "efficiency.pdf", "page": 3}
    ),
]
pipeline.add_documents(documents)

# Query the system
result = pipeline.query(
    query="How efficient are solar panels?",
    top_k=3,
    retrieval_method="hybrid",
    use_reranker=True
)

# Access results
print(f"Query: {result['query']}")
print(f"Context: {result['formatted_context']}")
for doc in result['retrieved_docs']:
    print(f"  - {doc.document.content[:100]}... (score: {doc.score:.4f})")
```

### Run Examples

```bash
# Basic usage example
python examples/basic_usage.py

# Advanced features (HyDE, re-ranking, comparisons)
python examples/advanced_usage.py
```

## 🏗️ Architecture

```
RAG Pipeline
├── Retrieval
│   ├── Vector Retriever (ChromaDB/FAISS)
│   ├── BM25 Retriever
│   └── Hybrid Retriever (RRF/Weighted Fusion)
├── Re-ranking
│   ├── Cohere Re-ranker
│   └── Cross-Encoder Re-ranker
├── Enhancement
│   └── HyDE (Hypothetical Document Embeddings)
└── Context Creation
    └── Formatted RAG Context
```

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 💡 Usage Examples

### Example 1: Vector-Only Retrieval

```python
from src.rag_engine.pipeline.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()
pipeline.add_documents(documents)

results = pipeline.retrieve(
    query="How do solar panels work?",
    top_k=5,
    retrieval_method="vector",
    use_reranker=False
)
```

### Example 2: Hybrid Retrieval with Re-ranking

```python
from src.rag_engine.reranking.reranker import CrossEncoderReranker

# Initialize with cross-encoder reranker
reranker = CrossEncoderReranker(
    model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
)
pipeline = RAGPipeline(reranker=reranker)

results = pipeline.retrieve(
    query="What is the best solar panel efficiency?",
    top_k=10,
    retrieval_method="hybrid",
    use_reranker=True  # Apply cross-encoder re-ranking
)
```

### Example 3: Using HyDE

```python
from src.rag_engine.embeddings.hyde import HyDE
import os

# Initialize HyDE
hyde = HyDE(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo"
)
pipeline = RAGPipeline(hyde=hyde)

results = pipeline.retrieve(
    query="solar energy benefits",
    top_k=5,
    retrieval_method="hybrid",
    use_hyde=True  # Apply HyDE query enhancement
)
```

### Example 4: Creating RAG Context

```python
# Get formatted context for LLM
context = pipeline.create_context(
    query="How to install solar panels?",
    top_k=3,
    retrieval_method="hybrid",
    use_reranker=True
)

# Use context with LLM
prompt = f"""
Answer the question based on the context below.

Context:
{context.context_text}

Question: {context.query}

Answer:
"""
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (see `.env.example`):

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
COHERE_API_KEY=your_cohere_api_key

# RAG Configuration
TOP_K_RETRIEVAL=10
TOP_K_RERANK=5
HYBRID_ALPHA=0.5
USE_HYDE=false

# Vector Store
VECTOR_STORE_TYPE=chromadb
VECTOR_STORE_PATH=./data/vector_store
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Re-ranker
RERANKER_TYPE=cross-encoder
CROSS_ENCODER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
```

### Programmatic Configuration

```python
from config.rag_config import RAGConfig, RetrievalConfig, VectorStoreConfig

config = RAGConfig(
    retrieval=RetrievalConfig(
        top_k=10,
        top_k_rerank=5,
        hybrid_alpha=0.5,
        use_hyde=False
    ),
    vector_store=VectorStoreConfig(
        store_type="chromadb",
        store_path="./data/vector_store",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2"
    )
)

pipeline = RAGPipeline(config=config)
```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Suites

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_bm25_retriever.py

# With coverage
pytest --cov=src/rag_engine --cov-report=html
```

### Test Coverage

Current test coverage includes:
- ✅ Data models (Document, RetrievalResult, RAGContext)
- ✅ BM25 retriever
- ✅ Vector retriever (ChromaDB/FAISS)
- ✅ Hybrid retriever (RRF and weighted fusion)
- ✅ Re-ranking (Cohere and Cross-Encoder)
- ✅ Full RAG pipeline integration

## 📚 API Reference

### RAGPipeline

Main class for RAG operations.

```python
pipeline = RAGPipeline(
    config=None,              # Optional RAGConfig
    vector_retriever=None,    # Optional pre-initialized retriever
    bm25_retriever=None,      # Optional pre-initialized retriever
    reranker=None,            # Optional pre-initialized reranker
    hyde=None                 # Optional pre-initialized HyDE
)
```

**Key Methods**:

- `add_documents(documents: List[Document])`: Add documents to the system
- `retrieve(query, top_k, retrieval_method, use_hyde, use_reranker)`: Retrieve documents
- `create_context(query, ...)`: Create formatted RAG context
- `query(query, ...)`: Complete RAG query pipeline
- `get_stats()`: Get pipeline statistics

### Document

```python
Document(
    id: str,                    # Unique identifier
    content: str,               # Document text
    metadata: Dict[str, Any],   # Optional metadata
    embedding: List[float]      # Optional pre-computed embedding
)
```

### RetrievalResult

```python
RetrievalResult(
    document: Document,        # Retrieved document
    score: float,             # Relevance score
    rank: int,                # Rank position
    retrieval_method: str     # Method used
)
```

### RAGContext

```python
RAGContext(
    query: str,                        # Original query
    retrieved_docs: List[RetrievalResult],  # Retrieved documents
    context_text: str,                 # Formatted context
    metadata: Dict[str, Any],          # Context metadata
    timestamp: datetime                # Creation time
)
```

## 🔧 Advanced Features

### Reciprocal Rank Fusion (RRF)

Combines rankings from multiple retrieval methods:

```python
pipeline.hybrid_retriever.retrieve(
    query="...",
    top_k=10,
    fusion_method="rrf"  # Reciprocal Rank Fusion
)
```

### Weighted Fusion

Combines normalized scores:

```python
pipeline.hybrid_retriever.retrieve(
    query="...",
    top_k=10,
    fusion_method="weighted"  # Weighted score fusion
)
```

### Custom Alpha Weighting

Control semantic vs keyword balance:

```python
# Favor semantic search (alpha=0.7)
pipeline.hybrid_retriever.alpha = 0.7

# Favor keyword search (alpha=0.3)
pipeline.hybrid_retriever.alpha = 0.3

# Equal balance (alpha=0.5)
pipeline.hybrid_retriever.alpha = 0.5
```

## 📊 Performance

| Configuration | Speed | Quality | Cost |
|--------------|-------|---------|------|
| Vector only | ⚡⚡⚡ | ⭐⭐⭐ | Free |
| BM25 only | ⚡⚡⚡ | ⭐⭐⭐ | Free |
| Hybrid | ⚡⚡⚡ | ⭐⭐⭐⭐ | Free |
| + Cross-Encoder | ⚡⚡ | ⭐⭐⭐⭐⭐ | Free |
| + Cohere | ⚡⚡ | ⭐⭐⭐⭐⭐ | $ |
| + HyDE | ⚡ | ⭐⭐⭐⭐⭐ | $ |

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Sentence Transformers** for embedding models
- **ChromaDB** and **FAISS** for vector storage
- **Cohere** for re-ranking API
- **rank-bm25** for BM25 implementation
- **HyDE paper**: "Precise Zero-Shot Dense Retrieval without Relevance Labels" (Gao et al., 2022)

## 📞 Contact

For questions or support, please open an issue on GitHub.

---

**Built for Solar PV AI LLM System** | Incremental Training | RAG | Citation | Autonomous Delivery
