# Architecture Documentation

This document provides a comprehensive overview of the Solar-PV-LLM-AI system architecture.

## System Overview

Solar-PV-LLM-AI is a multi-tier application with the following architectural principles:

- **Modularity**: Independent components for development and deployment
- **Scalability**: Horizontal scaling through containerization
- **Extensibility**: Plugin architecture for LLM providers and vector stores
- **Observability**: Built-in monitoring and logging

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                   │
├─────────────────┬──────────────────────┬────────────────────────────────────┤
│   Streamlit     │      REST API        │      CLI / Python SDK              │
│   Web App       │      Clients         │      Direct Integration            │
└─────────────────┴──────────────────────┴────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                        FastAPI Application                                  │
│  • Request validation    • Authentication    • Rate limiting                │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SERVICE LAYER                                      │
├───────────────┬───────────────┬───────────────┬─────────────────────────────┤
│  RAG Engine   │  Orchestrator │ Image Analysis│     PV Calculators          │
│  (Retrieval)  │  (LLM Router) │ (Defects)     │     (Domain Logic)          │
└───────────────┴───────────────┴───────────────┴─────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                         │
├───────────────────┬───────────────────┬─────────────────────────────────────┤
│    PostgreSQL     │  Pinecone Vector  │          Redis Cache                │
│    (Metadata)     │  Store            │          (Queue)                    │
└───────────────────┴───────────────────┴─────────────────────────────────────┘
```

## Core Components

### 1. RAG Engine

The Retrieval-Augmented Generation engine combines document retrieval with LLM generation.

**Key Features:**
- Hybrid retrieval (BM25 + Vector similarity)
- HyDE (Hypothetical Document Embeddings)
- Cross-encoder reranking
- Context building with metadata

**Workflow:**
1. Query embedding generation
2. Hybrid document retrieval
3. Reranking for relevance
4. Context formatting
5. LLM response generation

### 2. Multi-LLM Orchestrator

Intelligent routing between LLM providers based on query classification.

**Supported Providers:**
- OpenAI (GPT-4, GPT-4o)
- Anthropic (Claude 3.5 Sonnet)
- Local models (HuggingFace)

**Query Types:**
| Type | Best Provider | Use Case |
|------|---------------|----------|
| Interpretation | Claude | Conceptual questions |
| Calculation | GPT-4o | Numerical computations |
| Compliance | Claude | Standards questions |
| Troubleshooting | GPT-4o | Problem diagnosis |
| Design | Claude | System recommendations |

### 3. Image Analysis

Multi-stage pipeline for solar panel defect detection.

**Components:**
- **CLIP Classifier**: Zero-shot defect classification
- **Vision LLM**: Detailed image analysis
- **Report Generator**: Structured output

**Detectable Defects:**
- Hotspots, Cracks, Delamination
- Discoloration, Soiling, PID
- Snail trails, Bypass diode failures

### 4. Citation Manager

Automated citation extraction and formatting.

**Supported Formats:**
- IEEE, APA, Chicago, MLA

**Features:**
- Inline citation injection
- Reference tracking
- Bibliography generation

### 5. Ingestion Pipeline

IEC/IEEE standards document processing.

**Stages:**
1. PDF text extraction
2. Metadata extraction
3. Semantic chunking
4. Q&A generation
5. Vector store upload

## Data Flows

### Query Processing

```
User Query → API → RAG Engine → Vector Store
                        ↓
                   Reranker
                        ↓
              LLM Orchestrator → Response
                        ↓
              Citation Manager
                        ↓
                   User Response
```

### Image Analysis

```
Image Upload → Preprocessor → CLIP → Vision LLM
                                ↓
                         Report Generator
                                ↓
                          Analysis Report
```

## Database Schema

### Core Tables

- `users`: User accounts
- `queries`: Query history
- `query_responses`: AI responses
- `user_feedbacks`: Feedback data
- `documents`: Source documents
- `training_runs`: Model training

## Technology Stack

| Layer | Technologies |
|-------|--------------|
| API | FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy |
| Vector Store | Pinecone, ChromaDB |
| Cache | Redis |
| Queue | Celery |
| LLMs | OpenAI, Anthropic |
| ML | PyTorch, CLIP |
| Monitoring | Prometheus, Grafana |

## Security

- API key authentication
- JWT tokens for sessions
- Input validation (Pydantic)
- SQL injection prevention
- Rate limiting

## Monitoring

- Prometheus metrics at `/metrics`
- Structured JSON logging
- Health checks at `/health`
- Sentry error tracking (optional)

---

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.
See [API_REFERENCE.md](API_REFERENCE.md) for API documentation.
