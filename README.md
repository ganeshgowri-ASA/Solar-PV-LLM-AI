# Solar-PV-LLM-AI

<div align="center">

![Solar PV AI](https://img.shields.io/badge/Solar%20PV-AI%20Platform-orange?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTEyLDdBNSw1LDAsMCwxLDE3LDEyQTUsNSwwLDAsMSwxMiwxN0E1LDUsMCwwLDEsNywxMkE1LDUsMCwwLDEsMTIsN00xMiwyTDEyLDRNMTIsMjBMMTIsMjJNNCwxMkwyLDEyTTYuMjIsNi4yMkw0LjgsNC44TTYuMjIsMTcuNzhMNC44LDE5LjJNMTIsMjBMMTIsMjJNMjAsMTJMMjIsMTJNMTcuNzgsNi4yMkwxOS4yLDQuOE0xNy43OCwxNy43OEwxOS4yLDE5LjIiLz48L3N2Zz4=)
![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Enterprise-Grade AI Platform for Solar Photovoltaic Systems**

*Intelligent Q&A | Image Analysis | PV Calculations | Incremental Learning*

[Quick Start](#-quick-start) | [Features](#-features) | [Architecture](#-architecture) | [API Docs](#-api-documentation) | [Contributing](#-contributing)

</div>

---

## Overview

**Solar-PV-LLM-AI** is a comprehensive AI-powered platform designed to provide expert-level knowledge and autonomous assistance for Solar Photovoltaic (PV) systems. It combines Retrieval-Augmented Generation (RAG), multi-LLM orchestration, incremental learning from user feedback, and specialized domain calculators into a unified system.

### Key Capabilities

- **Intelligent Q&A** - RAG-powered responses with automatic citations
- **Image Analysis** - Detect solar panel defects using AI vision models
- **PV Calculations** - Energy yield, payback period, optimal angles
- **Multi-LLM Support** - Route queries to optimal LLM (GPT-4, Claude)
- **Incremental Learning** - Continuously improve from user feedback
- **IEC Standards** - Process and query IEC/IEEE standards documents

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACES                               │
├─────────────────┬─────────────────────┬─────────────────────────────────┤
│   Streamlit     │    FastAPI REST     │      CLI / Python SDK           │
│   Web App       │    (Port 8000)      │      Direct Integration         │
│  (Port 8501)    │                     │                                 │
└────────┬────────┴──────────┬──────────┴───────────────┬─────────────────┘
         │                   │                          │
         └───────────────────┼──────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FASTAPI APPLICATION SERVER                           │
├─────────────────────────────────────────────────────────────────────────┤
│  /api/v1/query    │  /api/v1/feedback   │  /api/v1/pv    │  /health    │
│  /api/v1/documents│  /api/v1/admin      │  /api/v1/image │  /metrics   │
└────────┬──────────┴─────────┬───────────┴───────┬───────┴──────────────┘
         │                    │                   │
         ▼                    ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                                   │
├───────────────┬───────────────┬───────────────┬─────────────────────────┤
│  RAG Engine   │  Orchestrator │ Image Analysis│  PV Calculators         │
│  ┌─────────┐  │  ┌──────────┐ │ ┌───────────┐ │  ┌───────────────────┐  │
│  │Embedding│  │  │Classifier│ │ │   CLIP    │ │  │  Energy Yield     │  │
│  │ Service │  │  │          │ │ │ Classifier│ │  │  Payback Period   │  │
│  └────┬────┘  │  └────┬─────┘ │ └─────┬─────┘ │  │  Optimal Tilt     │  │
│       │       │       │       │       │       │  │  Degradation      │  │
│  ┌────▼────┐  │  ┌────▼─────┐ │ ┌─────▼─────┐ │  └───────────────────┘  │
│  │ Hybrid  │  │  │  Router  │ │ │  Vision   │ │                         │
│  │Retrieval│  │  │(GPT/Claude)│ │   LLM     │ │                         │
│  └────┬────┘  │  └────┬─────┘ │ └─────┬─────┘ │                         │
│       │       │       │       │       │       │                         │
│  ┌────▼────┐  │  ┌────▼─────┐ │ ┌─────▼─────┐ │                         │
│  │Reranker │  │  │Synthesizer│ │   Report   │ │                         │
│  └─────────┘  │  └──────────┘ │ │ Generator │ │                         │
│               │               │ └───────────┘ │                         │
└───────┬───────┴───────┬───────┴───────┬───────┴─────────────────────────┘
        │               │               │
        ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATA & STORAGE LAYER                               │
├───────────────────┬───────────────────┬─────────────────────────────────┤
│    PostgreSQL     │  Pinecone Vector  │       Redis Cache               │
│    (Metadata)     │  Store (Embeddings)│      (Celery Queue)            │
└───────────────────┴───────────────────┴─────────────────────────────────┘
```

---

## Features

### Core AI Features

| Feature | Description | Status |
|---------|-------------|--------|
| **RAG Engine** | Hybrid retrieval (BM25 + Vector) with HyDE embeddings | ✅ Complete |
| **Multi-LLM Orchestrator** | Intelligent routing to GPT-4/Claude based on query type | ✅ Complete |
| **Citation Manager** | Automatic citation extraction and formatting (IEEE, APA) | ✅ Complete |
| **Image Analysis** | CLIP + Vision LLM for solar panel defect detection | ✅ Complete |
| **PV Calculators** | Energy yield, payback, optimal tilt calculations | ✅ Complete |
| **Incremental Learning** | LoRA fine-tuning from user feedback | ✅ Complete |
| **IEC Ingestion** | Process IEC/IEEE standards with semantic chunking | ✅ Complete |

### Detected Defects (Image Analysis)

- Hotspot Detection
- Crack / Micro-crack
- Delamination
- Discoloration
- Soiling / Dust
- Snail Trail
- PID (Potential Induced Degradation)
- Bypass Diode Failure

### Supported LLM Providers

| Provider | Models | Best For |
|----------|--------|----------|
| **OpenAI** | GPT-4, GPT-4o, GPT-3.5-turbo | Calculations, Troubleshooting |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Haiku | Interpretation, Design |
| **Local** | HuggingFace Transformers | Privacy-sensitive deployments |

---

## Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (recommended)
- API Keys: OpenAI, Anthropic (optional), Pinecone

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI

# Configure environment
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY, PINECONE_API_KEY, etc.)

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Clone and setup
git clone https://github.com/your-org/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start the backend
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, start the frontend
cd frontend
streamlit run app.py
```

### Quick Usage Examples

#### Python SDK

```python
from src.rag_engine.pipeline import RAGPipeline
from src.pv_image_analysis import ImageAnalyzer

# Initialize RAG pipeline
rag = RAGPipeline()

# Query the knowledge base
result = rag.query("What causes hotspots in solar panels?")
print(result['response'])
for citation in result['citations']:
    print(f"  - {citation['source']}: {citation['text']}")

# Analyze a solar panel image
analyzer = ImageAnalyzer()
report = analyzer.analyze("panel_image.jpg")
print(f"Health Score: {report['health_score']}%")
for defect in report['defects']:
    print(f"  - {defect['type']}: {defect['confidence']}%")
```

#### REST API

```bash
# Health check
curl http://localhost:8000/health

# Submit a query
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "What is the optimal tilt angle for solar panels at 40° latitude?",
    "use_rag": true
  }'

# Analyze an image
curl -X POST http://localhost:8000/api/v1/image-analysis/upload-and-analyze \
  -H "X-API-Key: your-api-key" \
  -F "file=@solar_panel.jpg"

# Calculate energy yield
curl -X POST http://localhost:8000/api/v1/pv/estimate-output \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "panel_capacity_kw": 5.0,
    "panel_efficiency": 0.20,
    "location_lat": 37.7749,
    "location_lon": -122.4194
  }'
```

#### CLI

```bash
# Process an IEC standards PDF
python -m src.ingestion.cli ingest /path/to/IEC_62446.pdf

# Batch process multiple documents
python -m src.ingestion.cli batch docs/*.pdf

# Validate processed output
python -m src.ingestion.cli validate data/processed/output.json
```

---

## Project Structure

```
Solar-PV-LLM-AI/
├── src/                          # Core business logic
│   ├── agents/                   # Multi-agent task routing
│   ├── chunking/                 # Document chunking strategies
│   ├── citation_manager/         # Citation extraction & formatting
│   ├── ingestion/                # IEC PDF processing pipeline
│   ├── orchestrator/             # Multi-LLM orchestration
│   ├── pv_image_analysis/        # Image defect detection
│   ├── rag_engine/               # RAG with hybrid retrieval
│   ├── storage/                  # Data persistence
│   └── vector_store/             # Vector database clients
│
├── backend/                      # Backend services
│   ├── api/                      # FastAPI routes
│   ├── calculators/              # PV domain calculators
│   ├── models/                   # Pydantic & SQLAlchemy models
│   └── services/                 # Business logic services
│
├── frontend/                     # Streamlit web interface
│   ├── pages/                    # UI pages
│   └── utils/                    # Frontend utilities
│
├── database/                     # DB initialization scripts
├── kubernetes/                   # K8s deployment manifests
├── terraform/                    # Infrastructure as Code
├── monitoring/                   # Prometheus, Grafana configs
├── workers/                      # Celery task workers
├── tests/                        # Test suites
│
├── docker-compose.yml            # Local orchestration
├── Dockerfile                    # Container image
├── requirements.txt              # Python dependencies
└── .env.example                  # Environment template
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, components, data flows |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Local, Docker, Kubernetes, Cloud setup |
| [API_REFERENCE.md](API_REFERENCE.md) | Complete API documentation with examples |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development setup, code style, guidelines |
| [INGESTION_README.md](INGESTION_README.md) | IEC PDF ingestion pipeline |

---

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/query/` | POST | Submit a query, get RAG response |
| `/api/v1/feedback/` | POST | Submit user feedback |
| `/api/v1/pv/estimate-output` | POST | Calculate energy yield |
| `/api/v1/pv/optimal-tilt/{lat}` | GET | Get optimal tilt angle |
| `/api/v1/image-analysis/analyze` | POST | Analyze solar panel image |
| `/api/v1/documents/ingest` | POST | Ingest a document |
| `/health` | GET | System health check |

See [API_REFERENCE.md](API_REFERENCE.md) for complete documentation.

---

## Configuration

### Required Environment Variables

```bash
# LLM Providers (at least one required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Vector Store
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=solar-pv-docs

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/solar_pv_db

# Application
SECRET_KEY=your-secret-key
ENVIRONMENT=development
```

### Optional Configuration

```bash
# Redis (for caching & Celery)
REDIS_URL=redis://localhost:6379/0

# NREL API (for PV calculations)
NREL_API_KEY=...

# Monitoring
PROMETHEUS_ENABLED=true
SENTRY_DSN=...

# RAG Settings
TOP_K_RETRIEVAL=10
HYBRID_SEARCH_ENABLED=true
BM25_WEIGHT=0.3
```

See [.env.example](.env.example) for all configuration options.

---

## Technology Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | FastAPI, Uvicorn, SQLAlchemy, PostgreSQL |
| **Frontend** | Streamlit |
| **LLMs** | OpenAI GPT-4, Anthropic Claude, LangChain |
| **Embeddings** | Sentence-Transformers, OpenAI |
| **Vector Store** | Pinecone, ChromaDB, FAISS |
| **Cache/Queue** | Redis, Celery |
| **ML/AI** | PyTorch, Transformers, CLIP |
| **Monitoring** | Prometheus, Grafana, Sentry |
| **Infrastructure** | Docker, Kubernetes, Terraform |

---

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) guide for:

- Development environment setup
- Code style guidelines
- Testing requirements
- Pull request process

```bash
# Quick development setup
git clone https://github.com/your-org/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
pytest tests/
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [OpenAI](https://openai.com) for GPT models
- [Anthropic](https://anthropic.com) for Claude models
- [Pinecone](https://pinecone.io) for vector database
- [NREL](https://www.nrel.gov) for solar resource data
- [Streamlit](https://streamlit.io) for the frontend framework

---

<div align="center">

**[Documentation](ARCHITECTURE.md)** | **[API Reference](API_REFERENCE.md)** | **[Report Issues](https://github.com/your-org/Solar-PV-LLM-AI/issues)**

Made with ❤️ for the Solar PV community

</div>
