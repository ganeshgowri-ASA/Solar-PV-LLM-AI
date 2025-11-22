# Solar PV LLM AI - Agent Guidelines

This file provides guidelines for AI assistants working on this Solar PV knowledge base project with Pinecone vector database integration.

## Project Overview

This repository develops a Solar PV AI LLM system with:
- Incremental training capabilities
- RAG (Retrieval-Augmented Generation) with Pinecone
- Citation support
- Autonomous delivery
- Support for audiences from beginners to experts

---

# Pinecone Vector Database Guidelines

> **Official docs**: [https://docs.pinecone.io/](https://docs.pinecone.io/)

If you need to help with Pinecone, vector databases, embeddings, semantic search, RAG, or recommendations, follow these guidelines.

## MANDATORY RULES - Read First

**These rules MUST be followed. Violations will cause runtime errors or data issues.**

1. **MUST use namespaces** - Every upsert, search, fetch, delete operation MUST specify a namespace
2. **MUST wait 10+ seconds** - After upserting records, MUST wait 10+ seconds before searching
3. **MUST match field_map** - Record field names MUST match the right side of `--field_map` used when creating index
4. **MUST respect batch limits** - Text records: MAX 96 per batch, Vector records: MAX 1000 per batch
5. **MUST use flat metadata** - No nested objects allowed, only flat key-value pairs
6. **MUST use `pinecone` package** - NOT `pinecone-client` (deprecated, causes errors)
7. **MUST verify before installing** - Check if SDK/CLI already installed before prompting installation

## Installation & Setup

### Python SDK (Current API 2025)

```python
from pinecone import Pinecone
```

**Install:**
```bash
pip install pinecone
```

**CRITICAL**: Always use `pinecone` (NOT `pinecone-client` - deprecated).

### Environment Configuration

**Use `.env` files for security:**

```bash
pip install python-dotenv
```

```python
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()  # Loads .env file
api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    raise ValueError("PINECONE_API_KEY required")
pc = Pinecone(api_key=api_key)
```

### Production Client Class

```python
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

class PineconeClient:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY required")
        self.pc = Pinecone(api_key=self.api_key)
        self.index_name = os.getenv("PINECONE_INDEX", "solar-pv-knowledge")

    def get_index(self):
        return self.pc.Index(self.index_name)
```

## CLI vs SDK: When to Use Which

**Use the Pinecone CLI for administrative tasks:**
- Creating indexes - `pc index create`
- Deleting indexes - `pc index delete`
- Configuring indexes - `pc index configure`
- Listing indexes - `pc index list`
- Creating API keys - `pc api-key create`

**Use the SDK for application code:**
- Vector operations - upsert, query, search, delete vectors
- Records operations - upsert, query, search, delete RECORDS
- Embeddings generation, reranking
- Unit and integration tests

## Index Creation

### Using CLI (Recommended for setup)

```bash
pc index create -n solar-pv-knowledge -m cosine -c aws -r us-east-1 --model llama-text-embed-v2 --field_map text=content
```

### Available Embedding Models

- `llama-text-embed-v2`: High-performance, configurable dimensions (recommended)
- `multilingual-e5-large`: For multilingual content, 1024 dimensions
- `pinecone-sparse-english-v0`: For keyword/hybrid search

## Data Operations

### Upserting Records

**Before upserting, verify:**
1. Namespace is specified (MANDATORY)
2. Field names match `--field_map` (MANDATORY)
3. Batch size ≤ 96 records for text (MANDATORY)
4. Metadata is flat (no nested objects) (MANDATORY)

```python
# For Solar PV knowledge base
records = [
    {
        "_id": "solar_basics_001",
        "content": "Solar photovoltaic cells convert sunlight directly into electricity using semiconductor materials.",
        "category": "fundamentals",
        "difficulty": "beginner",
        "topic": "pv_cells"
    },
    {
        "_id": "solar_efficiency_001",
        "content": "Monocrystalline solar panels typically achieve 15-22% efficiency under standard test conditions.",
        "category": "technology",
        "difficulty": "intermediate",
        "topic": "efficiency"
    }
]

# Always use namespaces
namespace = "solar_pv_docs"  # or "user_123", "session_456"
index.upsert_records(namespace, records)
```

### Batch Processing

```python
def batch_upsert(index, namespace, records, batch_size=96):
    """Batch upsert with rate limiting"""
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        index.upsert_records(namespace, batch)
        time.sleep(0.1)  # Rate limiting
```

## Search Operations

### Semantic Search with Reranking (Best Practice)

```python
import time

# IMPORTANT: Wait after upserting
time.sleep(10)

def search_solar_knowledge(index, query_text, category_filter=None, top_k=5):
    """Search Solar PV knowledge base with reranking"""
    query_dict = {
        "top_k": top_k * 2,  # Get more candidates for reranking
        "inputs": {"text": query_text}
    }

    if category_filter:
        query_dict["filter"] = {"category": {"$eq": category_filter}}

    results = index.search(
        namespace="solar_pv_docs",
        query=query_dict,
        rerank={
            "model": "bge-reranker-v2-m3",
            "top_n": top_k,
            "rank_fields": ["content"]
        }
    )
    return results
```

### Metadata Filtering

**Supported filter operators:**
- `$eq`: equals
- `$ne`: not equals
- `$gt`, `$gte`: greater than, greater than or equal
- `$lt`, `$lte`: less than, less than or equal
- `$in`: in list
- `$nin`: not in list
- `$exists`: field exists
- `$and`, `$or`: logical operators

```python
# Filter by difficulty level
filter_criteria = {
    "$and": [
        {"category": {"$in": ["fundamentals", "technology"]}},
        {"difficulty": {"$eq": "beginner"}}
    ]
}

results = index.search(
    namespace="solar_pv_docs",
    query={
        "top_k": 10,
        "inputs": {"text": "how do solar panels work"},
        "filter": filter_criteria
    }
)
```

## RAG System for Solar PV

```python
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("solar-pv-knowledge")

def rag_query(query, difficulty_level=None, top_k=5):
    """RAG query for Solar PV knowledge base"""
    query_dict = {
        "top_k": top_k * 2,
        "inputs": {"text": query}
    }

    if difficulty_level:
        query_dict["filter"] = {"difficulty": {"$eq": difficulty_level}}

    results = index.search(
        namespace="solar_pv_docs",
        query=query_dict,
        rerank={
            "model": "bge-reranker-v2-m3",
            "top_n": top_k,
            "rank_fields": ["content"]
        }
    )

    # Construct context for LLM with citations
    context_parts = []
    citations = []
    for i, hit in enumerate(results.result.hits):
        doc_id = hit["_id"]
        content = hit.fields["content"]
        context_parts.append(f"[{i+1}] {content}")
        citations.append({
            "ref": i+1,
            "id": doc_id,
            "category": hit.fields.get("category", ""),
            "topic": hit.fields.get("topic", "")
        })

    return {
        "context": "\n\n".join(context_parts),
        "citations": citations
    }
```

## Namespace Strategy for Solar PV Project

```python
# Content-based namespaces
NAMESPACES = {
    "docs": "solar_pv_docs",           # Main documentation
    "research": "solar_pv_research",    # Research papers
    "faq": "solar_pv_faq",              # Frequently asked questions
    "tutorials": "solar_pv_tutorials",  # Step-by-step guides
}

# User session namespaces (for personalization)
def get_user_namespace(user_id):
    return f"user_{user_id}"
```

## Common Mistakes to Avoid

### 1. Nested Metadata (API error)
```python
# BAD - nested objects not allowed
{"metadata": {"nested": {"value": 1}}}

# GOOD - flat structure only
{"metadata_nested_value": 1}
```

### 2. Batch Size Limits (API error)
- Text records: MAX 96 per batch, 2MB total
- Vector records: MAX 1000 per batch, 2MB total

### 3. Missing Namespaces (data isolation issues)
```python
# BAD
index.upsert_records(records)

# GOOD
index.upsert_records("solar_pv_docs", records)
```

### 4. Searching Too Soon After Upsert
```python
# BAD
index.upsert_records(namespace, records)
results = index.search(...)  # May return incomplete results

# GOOD
index.upsert_records(namespace, records)
time.sleep(10)  # Wait for indexing
results = index.search(...)
```

## Error Handling

```python
import time
from pinecone.exceptions import PineconeException

def exponential_backoff_retry(func, max_retries=5):
    """Retry with exponential backoff for transient errors"""
    for attempt in range(max_retries):
        try:
            return func()
        except PineconeException as e:
            status_code = getattr(e, 'status', None)

            # Only retry transient errors (5xx or 429)
            if status_code and (status_code >= 500 or status_code == 429):
                if attempt < max_retries - 1:
                    delay = min(2 ** attempt, 60)
                    time.sleep(delay)
                else:
                    raise
            else:
                raise  # Don't retry client errors

# Usage
exponential_backoff_retry(lambda: index.upsert_records(namespace, records))
```

## Key Constraints Reference

| Constraint | Limit | Notes |
|------------|-------|-------|
| Metadata per record | 40KB | Flat JSON only |
| Text batch size | 96 records | 2MB total per batch |
| Vector batch size | 1000 records | 2MB total per batch |
| Query response size | 4MB | Per query response |
| Metadata types | strings, ints, floats, bools, string lists | No nested structures |
| Consistency | Eventually consistent | Wait ~10s after upsert |

## Quick Reference

### Index Operations
```bash
# Create index
pc index create -n solar-pv-knowledge -m cosine -c aws -r us-east-1 --model llama-text-embed-v2 --field_map text=content

# List indexes
pc index list

# Describe index
pc index describe --name solar-pv-knowledge

# Delete index
pc index delete --name solar-pv-knowledge
```

### Python SDK Quick Start
```python
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("solar-pv-knowledge")

# Upsert
index.upsert_records("solar_pv_docs", records)

# Search
results = index.search(
    namespace="solar_pv_docs",
    query={"top_k": 5, "inputs": {"text": "solar panel efficiency"}}
)

# Fetch
result = index.fetch(namespace="solar_pv_docs", ids=["doc1"])

# Delete
index.delete(namespace="solar_pv_docs", ids=["doc1"])
```

## Official Documentation

- **API Reference**: https://docs.pinecone.io/reference/api/introduction
- **Python SDK**: https://docs.pinecone.io/reference/python-sdk
- **Error Handling**: https://docs.pinecone.io/guides/production/error-handling
- **Database Limits**: https://docs.pinecone.io/reference/api/database-limits
