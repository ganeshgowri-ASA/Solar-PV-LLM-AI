# Solar PV LLM AI System

An advanced AI-powered knowledge system for Solar Photovoltaic technology with incremental learning, continuous improvement through user feedback, and zero-downtime model updates.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

## 🌟 Features

### Core Capabilities
- **🤖 RAG-Powered Q&A**: Retrieval Augmented Generation for accurate, cited responses
- **📊 Feedback Collection**: Multi-dimensional user feedback (rating, helpfulness, accuracy)
- **🔄 Incremental Learning**: Continuous model improvement from user interactions
- **🎯 Automated Retraining**: LoRA-based fine-tuning triggered by feedback signals
- **⚡ Zero-Downtime Updates**: Blue-green deployment for knowledge base and models
- **📈 Admin Dashboard**: Comprehensive monitoring and control interface
- **🔍 Citation Support**: Source attribution for all responses
- **🎓 Adaptive Delivery**: Content tailored from beginners to experts

### Technical Highlights
- **Multiple LLM Providers**: OpenAI, Anthropic Claude, Azure OpenAI
- **Flexible Vector Stores**: Pinecone, ChromaDB, Weaviate, Qdrant, FAISS
- **Async Task Processing**: Celery with Redis for background jobs
- **Production-Ready**: Docker Compose, health checks, monitoring
- **Comprehensive Testing**: Pytest with integration tests
- **Observability**: Structured logging, Prometheus metrics, Flower monitoring

## 🏗️ Architecture

```
User → API → RAG Service → Vector Store + LLM
         ↓
    Feedback Collection → Analysis → Retraining → Deployment
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (recommended)
- OpenAI API key or Anthropic API key
- Vector store credentials (Pinecone recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

Required configuration:
- `LLM_API_KEY`: Your OpenAI or Anthropic API key
- `VECTOR_STORE_API_KEY`: Your vector store API key
- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `DATABASE_URL`: PostgreSQL connection string (or use Docker)

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

This starts:
- FastAPI application (port 8000)
- PostgreSQL database
- Redis for task queue
- Celery worker and scheduler
- Flower monitoring dashboard (port 5555)

4. **Initialize database**
```bash
docker-compose exec api alembic upgrade head
```

5. **Verify installation**
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Flower monitoring
open http://localhost:5555
```

## 📖 Usage

### Submit a Query

```bash
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What is the average efficiency of modern solar panels?",
    "session_id": "my-session"
  }'
```

Response:
```json
{
  "id": 1,
  "query_text": "What is the average efficiency of modern solar panels?",
  "response": {
    "response_text": "Modern solar panels typically have an efficiency of 15-20%...",
    "confidence_score": 0.92,
    "model_version": "gpt-4-turbo-preview"
  },
  "retrieved_documents": [
    {
      "title": "Solar Panel Technology",
      "content": "...",
      "relevance_score": 0.89
    }
  ]
}
```

### Submit Feedback

```bash
curl -X POST http://localhost:8000/api/v1/feedback/ \
  -H "Content-Type: application/json" \
  -d '{
    "response_id": 1,
    "rating": 5,
    "is_helpful": true,
    "is_accurate": true,
    "is_complete": true
  }'
```

### Trigger Retraining

```bash
curl -X POST http://localhost:8000/api/v1/admin/retraining/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "solar-pv-model",
    "training_type": "lora",
    "min_feedback_rating": 4
  }'
```

### Add Documents to Knowledge Base

```bash
curl -X POST http://localhost:8000/api/v1/admin/knowledge-base/update \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "title": "Solar Panel Installation Guide",
        "content": "...",
        "source_url": "https://example.com/guide"
      }
    ]
  }'
```

## 📊 Admin Dashboard APIs

### Get Dashboard Metrics
```bash
curl http://localhost:8000/api/v1/admin/dashboard/metrics?days=30
```

### Check System Health
```bash
curl http://localhost:8000/api/v1/admin/health
```

### Get Retraining Recommendation
```bash
curl http://localhost:8000/api/v1/admin/retraining/recommendation
```

### Get Feedback Statistics
```bash
curl http://localhost:8000/api/v1/feedback/stats/summary?days=30
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/solar_pv_ai

# Vector Store
VECTOR_STORE_TYPE=pinecone  # or chromadb, weaviate, qdrant
VECTOR_STORE_API_KEY=your_key
VECTOR_STORE_INDEX_NAME=solar-pv-knowledge

# LLM Provider
LLM_PROVIDER=openai  # or anthropic, azure
LLM_MODEL=gpt-4-turbo-preview
LLM_API_KEY=your_key

# Embedding Model
EMBEDDING_MODEL=text-embedding-ada-002

# RAG Configuration
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7

# Feedback Thresholds
FEEDBACK_CONFIDENCE_THRESHOLD=0.8
FEEDBACK_NEGATIVE_RATING_THRESHOLD=2.0

# Retraining
RETRAINING_ENABLED=true
RETRAINING_MIN_FEEDBACK_COUNT=100
RETRAINING_SCHEDULE_CRON=0 2 * * 0  # Weekly Sunday 2 AM

# LoRA Fine-Tuning
LORA_R=8
LORA_ALPHA=16
LORA_DROPOUT=0.1
TRAINING_BATCH_SIZE=4
TRAINING_EPOCHS=3
TRAINING_LEARNING_RATE=2e-4

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
```

See [`.env.example`](.env.example) for complete configuration options.

## 📁 Project Structure

```
Solar-PV-LLM-AI/
├── backend/
│   ├── api/                    # API routes
│   │   ├── query_routes.py     # Query and RAG endpoints
│   │   ├── feedback_routes.py  # Feedback collection
│   │   └── admin_routes.py     # Admin dashboard
│   ├── models/                 # Data models
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   ├── services/               # Business logic
│   │   ├── rag_service.py      # RAG pipeline
│   │   ├── feedback_service.py # Feedback analysis
│   │   ├── llm_service.py      # LLM integration
│   │   ├── vector_store_service.py  # Vector store
│   │   ├── retraining_service.py    # Model retraining
│   │   └── celery_tasks.py     # Async tasks
│   ├── database/               # Database setup
│   │   ├── connection.py       # DB connection
│   │   └── migrations/         # Alembic migrations
│   ├── utils/                  # Utilities
│   │   └── logger.py           # Logging setup
│   ├── tests/                  # Test suite
│   ├── config.py               # Configuration
│   └── app.py                  # FastAPI app
├── data/                       # Data storage
│   ├── vector_store/           # Vector DB files
│   ├── training_data/          # Training datasets
│   └── feedback_logs/          # Feedback history
├── notebooks/                  # Jupyter notebooks
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Docker image
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── ARCHITECTURE.md             # System architecture
├── DEPLOYMENT.md               # Deployment guide
└── README.md                   # This file
```

## 🧪 Testing

Run tests:
```bash
# All tests
pytest

# With coverage
pytest --cov=backend --cov-report=html

# Specific test file
pytest backend/tests/test_feedback_service.py

# Integration tests only
pytest backend/tests/test_integration.py
```

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed system architecture
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Comprehensive deployment guide
- **API Docs**: http://localhost:8000/docs (interactive Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (alternative API docs)

## 🔍 Monitoring

### Celery Tasks
Monitor background tasks at http://localhost:5555 (Flower dashboard)

### Prometheus Metrics
Metrics available at http://localhost:8000/metrics

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f celery-worker
```

## 🔄 Continuous Learning Workflow

1. **User submits query** → System generates response with RAG
2. **User provides feedback** → Rating, comments, tags collected
3. **System analyzes feedback** → Identifies low-confidence responses
4. **Retraining triggered** → When thresholds met (automatic or manual)
5. **Model fine-tuned** → LoRA adapters trained on feedback data
6. **Model deployed** → Zero-downtime deployment with rollback capability
7. **Performance monitored** → Metrics tracked for continuous improvement

## 🛠️ Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Install development tools
pip install black flake8 mypy pytest pytest-cov

# Set up pre-commit hooks
pip install pre-commit
pre-commit install

# Run in development mode
uvicorn backend.app:app --reload
```

### Code Style

- **Formatter**: Black
- **Linter**: Flake8
- **Type Checker**: MyPy
- **Testing**: Pytest

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🚀 Deployment

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Production configuration
- Docker deployment
- Kubernetes setup
- Database optimization
- Security best practices
- Monitoring and alerting

### Cloud Platforms

Deployment guides for:
- AWS (ECS, RDS, ElastiCache)
- Google Cloud (Cloud Run, Cloud SQL)
- Azure (Container Apps, PostgreSQL)

## 📈 Roadmap

### Current Features (v1.0)
- ✅ RAG-based Q&A system
- ✅ Feedback collection and analysis
- ✅ Automated retraining with LoRA
- ✅ Zero-downtime updates
- ✅ Admin dashboard APIs
- ✅ Comprehensive monitoring

### Planned Features (v2.0)
- 🔜 Web-based admin dashboard UI
- 🔜 A/B testing framework
- 🔜 Multi-language support
- 🔜 Advanced analytics
- 🔜 Active learning strategies
- 🔜 Conversation context tracking
- 🔜 OAuth2 authentication
- 🔜 API rate limiting

## 🤝 Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/discussions)

## 📄 License

[MIT License](LICENSE) - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [OpenAI](https://openai.com/) / [Anthropic](https://www.anthropic.com/)
- Vector search by [Pinecone](https://www.pinecone.io/) / [ChromaDB](https://www.trychroma.com/)
- Task queue by [Celery](https://docs.celeryq.dev/)

## 📞 Contact

For questions, suggestions, or collaborations:
- GitHub: [@ganeshgowri-ASA](https://github.com/ganeshgowri-ASA)
- Repository: [Solar-PV-LLM-AI](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI)

---

**Note**: This is an active research and development project. Contributions, feedback, and suggestions are welcome!
