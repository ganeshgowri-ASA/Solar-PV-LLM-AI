# RAG Engine Architecture

## Overview

The RAG (Retrieval Augmented Generation) Engine is a comprehensive system for retrieving relevant documents and creating context for LLM-based question answering. It combines multiple retrieval strategies, re-ranking techniques, and query enhancement methods.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        RAG Pipeline                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐                                            │
│  │   Query      │                                            │
│  └──────┬───────┘                                            │
│         │                                                     │
│         ├──────────┐  (Optional)                             │
│         │  HyDE    │  Generate hypothetical document         │
│         └──────────┘                                         │
│         │                                                     │
│         ├─────────────────┬─────────────────┐                │
│         ▼                 ▼                 ▼                │
│  ┌────────────┐    ┌───────────┐    ┌──────────────┐        │
│  │   Vector   │    │   BM25    │    │   Hybrid     │        │
│  │ Retriever  │    │ Retriever │    │  Retriever   │        │
│  └────────────┘    └───────────┘    └──────────────┘        │
│         │                 │                 │                │
│         └─────────────────┴─────────────────┘                │
│                           │                                  │
│                           ▼                                  │
│                  ┌─────────────────┐                         │
│                  │   Re-ranker     │  (Optional)             │
│                  │  - Cohere       │                         │
│                  │  - Cross-Enc    │                         │
│                  └─────────────────┘                         │
│                           │                                  │
│                           ▼                                  │
│                  ┌─────────────────┐                         │
│                  │  RAG Context    │                         │
│                  └─────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Vector Retriever

**Purpose**: Semantic similarity search using dense embeddings

**Implementation**:
- Supports ChromaDB and FAISS backends
- Uses sentence-transformers for embedding generation
- Cosine similarity for relevance scoring

**Key Features**:
- Persistent storage
- Configurable embedding models
- Metadata filtering (ChromaDB)

**File**: `src/rag_engine/retrieval/vector_retriever.py`

### 2. BM25 Retriever

**Purpose**: Keyword-based retrieval using statistical ranking

**Implementation**:
- BM25Okapi algorithm from rank-bm25 library
- Tokenization and term frequency analysis
- Configurable BM25 parameters (k1, b, epsilon)

**Key Features**:
- Fast keyword matching
- No need for embeddings
- Complementary to semantic search

**File**: `src/rag_engine/retrieval/bm25_retriever.py`

### 3. Hybrid Retriever

**Purpose**: Combine vector and BM25 retrieval for best results

**Implementation**:
- Two fusion methods:
  1. **Reciprocal Rank Fusion (RRF)**: `score = Σ(1/(k + rank))`
  2. **Weighted Score Fusion**: `score = α·vector_score + (1-α)·bm25_score`

**Key Features**:
- Configurable weighting (alpha parameter)
- Leverages strengths of both methods
- Robust to individual method weaknesses

**File**: `src/rag_engine/retrieval/hybrid_retriever.py`

**RRF Formula**:
```
For each document d:
  RRF_score(d) = α / (k + rank_vector(d)) + (1-α) / (k + rank_bm25(d))

where:
  - α: weight for vector search (0-1)
  - k: constant (typically 60)
  - rank: position in results (1, 2, 3, ...)
```

### 4. Re-ranker

**Purpose**: Improve relevance by re-scoring retrieved documents

**Implementations**:

#### A. Cohere Re-ranker
- Uses Cohere's rerank API
- State-of-the-art relevance scoring
- Requires API key
- Model: `rerank-english-v3.0`

#### B. Cross-Encoder Re-ranker
- Local cross-encoder models
- Jointly encodes query + document
- No API required
- Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`

**File**: `src/rag_engine/reranking/reranker.py`

### 5. HyDE (Hypothetical Document Embeddings)

**Purpose**: Bridge semantic gap between queries and documents

**Implementation**:
- Uses LLM (GPT-3.5/4) to generate hypothetical answer
- Searches with generated answer instead of query
- Can generate multiple diverse hypotheses

**Algorithm**:
```
1. Input: user query Q
2. Generate: hypothetical document H using LLM
   Prompt: "Write a passage to answer: {Q}"
3. Search: use H instead of Q for retrieval
4. Return: documents similar to H
```

**Benefits**:
- Better matches document style/vocabulary
- Improved recall for complex queries
- Bridges vocabulary mismatch

**File**: `src/rag_engine/embeddings/hyde.py`

### 6. RAG Pipeline

**Purpose**: Orchestrate all components into unified workflow

**Capabilities**:
- Document ingestion
- Multi-strategy retrieval
- Optional HyDE enhancement
- Optional re-ranking
- Context formatting

**Usage Modes**:
1. **Vector only**: Fast, semantic search
2. **BM25 only**: Fast, keyword search
3. **Hybrid**: Best quality, combines both
4. **With re-ranking**: Highest quality
5. **With HyDE**: Best for complex queries

**File**: `src/rag_engine/pipeline/rag_pipeline.py`

## Data Models

### Document
```python
{
  "id": str,           # Unique identifier
  "content": str,      # Document text
  "metadata": dict,    # Arbitrary metadata
  "embedding": list    # Optional pre-computed embedding
}
```

### RetrievalResult
```python
{
  "document": Document,      # Retrieved document
  "score": float,           # Relevance score
  "rank": int,              # Position in results
  "retrieval_method": str   # Method used
}
```

### RAGContext
```python
{
  "query": str,                      # Original query
  "retrieved_docs": [RetrievalResult],  # Retrieved documents
  "context_text": str,               # Formatted context
  "metadata": dict,                  # Context metadata
  "timestamp": datetime              # Creation time
}
```

## Configuration

Configuration is managed through Pydantic models in `config/rag_config.py`:

- **RetrievalConfig**: top_k, alpha, HyDE settings
- **VectorStoreConfig**: store type, path, embedding model
- **RerankerConfig**: reranker type, API keys, models
- **HyDEConfig**: LLM settings, prompt template

Configuration can be loaded from:
1. Environment variables (`.env` file)
2. Code (direct instantiation)
3. Config file (future)

## Performance Characteristics

| Component | Speed | Quality | Memory | API Cost |
|-----------|-------|---------|--------|----------|
| Vector    | Fast  | Good    | High   | None     |
| BM25      | Fast  | Good    | Low    | None     |
| Hybrid    | Fast  | Better  | High   | None     |
| Cohere RR | Medium| Best    | Low    | $$       |
| Cross-Enc | Slow  | Best    | Medium | None     |
| HyDE      | Slow  | Better  | Low    | $        |

**Recommended Configurations**:

1. **Development/Testing**: Vector only, no re-ranking
2. **Production (Fast)**: Hybrid, no re-ranking
3. **Production (Quality)**: Hybrid + Cross-Encoder
4. **Production (Best)**: Hybrid + HyDE + Cohere

## Extensibility

The architecture supports easy extension:

1. **New Vector Stores**: Implement in `VectorRetriever`
   - Already supports: ChromaDB, FAISS
   - Easy to add: Pinecone, Weaviate, Milvus

2. **New Re-rankers**: Inherit from `Reranker` base class
   - Already supports: Cohere, Cross-Encoder
   - Easy to add: Custom models, APIs

3. **New Retrievers**: Implement retrieval interface
   - Already supports: Vector, BM25, Hybrid
   - Easy to add: TF-IDF, Elasticsearch, custom

4. **New Fusion Methods**: Add to `HybridRetriever`
   - Already supports: RRF, Weighted
   - Easy to add: Rank fusion, Score normalization

## Testing Strategy

1. **Unit Tests**: Individual components (`tests/unit/`)
2. **Integration Tests**: Full pipeline (`tests/integration/`)
3. **QA Validation**: Retrieval quality metrics

Run tests:
```bash
pytest tests/unit/          # Fast unit tests
pytest tests/integration/   # Full integration tests
pytest                      # All tests
```
