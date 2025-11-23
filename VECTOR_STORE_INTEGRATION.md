# Pinecone Vector Store Integration - Documentation

## Overview

This implementation provides a complete vector store solution for Solar PV documentation using:
- **Pinecone** vector database (serverless, cosine similarity)
- **OpenAI text-embedding-3-large** (1536 dimensions)
- **FastAPI** REST API with comprehensive endpoints
- **Comprehensive logging and error handling**

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FastAPI API                          │
│  ┌─────────────┬──────────────┬──────────────┬────────────┐ │
│  │   Ingest    │    Search    │   Delete     │   Stats    │ │
│  └─────────────┴──────────────┴──────────────┴────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
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
    │   (OpenAI)  │                    │             │
    └─────────────┘                    └─────────────┘
```

## Features

### ✅ Implemented

1. **Pinecone Index Management**
   - Automatic index creation with 1536 dimensions
   - Cosine similarity metric
   - Serverless deployment (AWS)

2. **Embedding Generation**
   - OpenAI text-embedding-3-large model
   - Batch processing support
   - Automatic retry with exponential backoff

3. **Document Ingestion**
   - Batch upsert functionality
   - Metadata embedding
   - Automatic ID generation
   - Timestamp tracking

4. **Similarity Search**
   - Vector similarity search
   - Metadata filtering support
   - Solar PV specific filters:
     - `standards`: Filter by standard (IEC 61215, IEC 61730, etc.)
     - `clauses`: Filter by specific clauses (MQT 11, MST 09, etc.)
     - `test_type`: Filter by test type (performance, safety, reliability)

5. **Vector Operations**
   - Delete by IDs
   - Delete by filters
   - Fetch vectors by ID
   - Index statistics

6. **API Endpoints**
   - `POST /api/v1/documents/ingest` - Ingest documents
   - `POST /api/v1/search` - Basic similarity search
   - `POST /api/v1/search/filtered` - Filtered search with Solar PV filters
   - `DELETE /api/v1/documents` - Delete vectors
   - `GET /api/v1/stats` - Get index statistics
   - `GET /api/v1/health` - Health check

7. **Logging & Error Handling**
   - Structured logging (JSON or standard format)
   - Custom exception hierarchy
   - Comprehensive error messages
   - Request/response logging

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Pinecone Configuration
PINECONE_API_KEY=your_actual_pinecone_api_key
PINECONE_INDEX_NAME=solar-pv-index
PINECONE_ENVIRONMENT=us-east-1

# OpenAI Configuration
OPENAI_API_KEY=your_actual_openai_api_key
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSION=1536

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=standard
```

### 3. Run the API Server

```bash
python -m src.main
```

Or use uvicorn directly:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage Examples

### 1. Ingest Documents

```bash
curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "text": "IEC 61215 is an international standard for PV module design qualification...",
        "metadata": {
          "standards": "IEC 61215",
          "clauses": ["MQT 01", "MQT 02"],
          "test_type": "performance",
          "category": "module_qualification"
        }
      }
    ],
    "namespace": "production"
  }'
```

### 2. Basic Similarity Search

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "thermal cycling test requirements",
    "top_k": 5,
    "namespace": "production"
  }'
```

### 3. Filtered Search by Standard

```bash
curl -X POST "http://localhost:8000/api/v1/search/filtered" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "environmental testing procedures",
    "top_k": 5,
    "standards": "IEC 61215",
    "test_type": "reliability",
    "namespace": "production"
  }'
```

### 4. Delete Documents

```bash
curl -X DELETE "http://localhost:8000/api/v1/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {"standards": "IEC 62804"},
    "namespace": "production"
  }'
```

### 5. Get Index Statistics

```bash
curl "http://localhost:8000/api/v1/stats?namespace=production"
```

## QA Testing

### Run QA Test Suite

```bash
python tests/test_vector_store.py
```

This will:
1. Load 10 sample Solar PV documents
2. Ingest them into the vector store
3. Run various similarity searches
4. Test filtering by standards, test_type, and multiple criteria
5. Verify deletion and stats endpoints

### Expected Output

```
Starting Vector Store QA Tests
================================================================================
Initializing VectorStoreHandler...
✓ Handler initialized successfully

================================================================================
TEST 1: Document Ingestion
================================================================================
✓ Successfully ingested 10 documents

================================================================================
TEST 2: Basic Similarity Search
================================================================================
✓ Found 3 results
✓ Basic search working correctly

================================================================================
TEST 3: Filtered Search by Standard (IEC 61215)
================================================================================
✓ Found 6 results
✓ All results correctly filtered by standard

... [additional tests]

================================================================================
ALL TESTS PASSED ✓
================================================================================
```

## Code Structure

```
Solar-PV-LLM-AI/
├── src/
│   ├── api/
│   │   ├── models.py          # Pydantic request/response models
│   │   └── routes.py          # FastAPI endpoints
│   ├── config/
│   │   └── settings.py        # Configuration management
│   ├── logging/
│   │   └── logger.py          # Logging configuration
│   ├── utils/
│   │   └── errors.py          # Custom exceptions
│   ├── vector_store/
│   │   ├── embeddings.py      # OpenAI embedding service
│   │   ├── pinecone_client.py # Pinecone client wrapper
│   │   └── handler.py         # Unified vector store handler
│   └── main.py                # Application entry point
├── tests/
│   └── test_vector_store.py   # QA test suite
├── sample_docs/
│   └── solar_pv_documents.json # Sample Solar PV documents
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
└── VECTOR_STORE_INTEGRATION.md # This file
```

## API Reference

### POST /api/v1/documents/ingest

Ingest documents with automatic embedding generation.

**Request:**
```json
{
  "documents": [
    {
      "text": "string",
      "metadata": {
        "standards": "string",
        "clauses": ["string"],
        "test_type": "string"
      }
    }
  ],
  "namespace": "string",
  "batch_size": 100
}
```

**Response:**
```json
{
  "status": "success",
  "documents_ingested": 10,
  "namespace": "production",
  "batches_processed": 1
}
```

### POST /api/v1/search/filtered

Search with Solar PV specific filters.

**Request:**
```json
{
  "query": "string",
  "top_k": 10,
  "standards": "IEC 61215",
  "clauses": ["MQT 11", "MQT 12"],
  "test_type": "reliability",
  "namespace": "production"
}
```

**Response:**
```json
{
  "status": "success",
  "query": "thermal testing",
  "results": [
    {
      "id": "doc_id",
      "score": 0.95,
      "metadata": {
        "standards": "IEC 61215",
        "test_type": "reliability"
      }
    }
  ],
  "count": 5
}
```

## Performance Considerations

1. **Batch Processing**: Use batch_size parameter for large ingestions
2. **Retry Logic**: Automatic retry with exponential backoff for API calls
3. **Namespace Organization**: Use namespaces to separate datasets
4. **Metadata Filtering**: Efficient filtering using Pinecone's built-in capabilities

## Error Handling

All endpoints include comprehensive error handling:

- `400 Bad Request`: Invalid input or embedding errors
- `500 Internal Server Error`: Vector store or unexpected errors
- Custom exceptions with detailed messages
- Full request/error logging

## Monitoring

Check service health:
```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Solar PV LLM AI - Vector Store",
  "version": "0.1.0",
  "pinecone_connected": true,
  "embedding_service_ready": true
}
```

## Security Notes

1. **API Keys**: Never commit `.env` file to version control
2. **CORS**: Configure `allow_origins` appropriately for production
3. **Rate Limiting**: Consider adding rate limiting for production
4. **Authentication**: Add authentication middleware for production use

## Next Steps

1. Add authentication and authorization
2. Implement rate limiting
3. Add monitoring and metrics (Prometheus, Grafana)
4. Implement caching layer
5. Add more Solar PV specific metadata fields
6. Implement RAG (Retrieval-Augmented Generation) pipeline
7. Add LLM integration for question answering

## Support

For issues or questions:
1. Check logs for detailed error messages
2. Review API documentation at `/docs`
3. Run QA tests to verify setup
4. Check environment configuration

## License

See LICENSE file for details.
