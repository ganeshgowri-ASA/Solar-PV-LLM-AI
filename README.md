# Solar PV LLM AI

> **Advanced Solar PV AI System** with RAG, LLM orchestration, defect detection, and performance analytics.

A comprehensive FastAPI-based backend system for solar photovoltaic analysis, combining AI-powered chat assistance, computer vision for defect detection, performance calculations, and document-based knowledge retrieval.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🌟 Features

### 🤖 AI-Powered Chat with RAG
- **Retrieval Augmented Generation (RAG)** for context-aware responses
- Integration with **OpenAI GPT-4** and **Anthropic Claude**
- Automatic source citation and bibliography generation
- Conversation history support
- Token usage tracking

### 📊 PV Performance Calculations
- Energy output estimation (daily, monthly, annual)
- Performance ratio calculation
- Optimal tilt angle determination
- Financial payback analysis
- Peak sun hours calculation
- System capacity factor analysis

### 🔍 Defect Detection & Image Analysis
- **8 defect types** detection:
  - Hotspots (thermal anomalies)
  - Cracks and micro-cracks
  - Delamination
  - Discoloration
  - Soiling
  - Snail trails
  - PID (Potential Induced Degradation)
  - Bypass diode failures
- Overall health scoring
- Automated maintenance recommendations

### 📚 Document Ingestion & Knowledge Base
- Support for **PDF, DOCX, TXT** formats
- Automatic text extraction and chunking
- Vector embeddings with **ChromaDB**
- Real-time processing status tracking
- Semantic search capabilities

### 🛡️ Production-Ready Features
- **Token-based authentication** (API Key + JWT)
- **CORS** middleware configuration
- **Prometheus metrics** integration
- Structured **logging** with Loguru
- Comprehensive **API documentation** (Swagger UI)
- **Health checks** for all services
- Request/response validation with Pydantic

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager
- (Optional) OpenAI API key
- (Optional) Anthropic API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/Solar-PV-LLM-AI.git
   cd Solar-PV-LLM-AI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the API**
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health

---

## 📁 Project Structure

```
Solar-PV-LLM-AI/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── chat.py              # RAG-enhanced chat endpoint
│   │       ├── pv_calculations.py   # PV performance calculations
│   │       ├── image_analysis.py    # Defect detection
│   │       ├── documents.py         # Document ingestion
│   │       └── health.py            # Health & metrics
│   ├── core/
│   │   ├── config.py                # Configuration management
│   │   └── security.py              # Authentication & JWT
│   ├── middleware/
│   │   ├── logging.py               # Logging middleware
│   │   └── metrics.py               # Prometheus metrics
│   ├── models/
│   │   └── schemas.py               # Pydantic models
│   ├── services/
│   │   ├── rag_engine.py            # RAG implementation
│   │   ├── llm_orchestrator.py      # LLM integration
│   │   ├── citation_manager.py      # Citation handling
│   │   ├── pv_calculator.py         # PV calculations
│   │   ├── image_analyzer.py        # Image analysis
│   │   └── document_ingestion.py    # Document processing
│   └── main.py                      # FastAPI application
├── tests/
│   ├── api/
│   │   ├── test_chat.py
│   │   ├── test_pv_calculations.py
│   │   ├── test_image_analysis.py
│   │   └── test_health.py
│   └── conftest.py
├── config/                          # Configuration files
├── data/                            # Data storage
│   ├── chroma/                      # Vector database
│   └── uploads/                     # Uploaded files
├── logs/                            # Application logs
├── .env.example                     # Environment template
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Test configuration
├── run.py                          # Application runner
├── API_DOCUMENTATION.md            # Detailed API docs
└── README.md                       # This file
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Application
APP_NAME=Solar PV LLM AI
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-change-in-production
API_KEY=your-api-key

# OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key

# Vector Database
CHROMA_PERSIST_DIRECTORY=./data/chroma
CHROMA_COLLECTION_NAME=solar_pv_documents

# RAG
MAX_RETRIEVAL_RESULTS=5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

See `.env.example` for all available configuration options.

---

## 📖 API Usage

### Authentication

All API endpoints require authentication via API key:

```python
import requests

headers = {"X-API-Key": "your-api-key"}
response = requests.post(
    "http://localhost:8000/chat/",
    headers=headers,
    json={"query": "What is solar panel efficiency?"}
)
```

### Example: Chat with RAG

```python
import requests

response = requests.post(
    "http://localhost:8000/chat/",
    headers={"X-API-Key": "your-api-key"},
    json={
        "query": "How do I optimize solar panel tilt angle?",
        "use_rag": True,
        "max_tokens": 500
    }
)

data = response.json()
print(f"Response: {data['response']}")
print(f"Citations: {len(data['citations'])}")
```

### Example: PV Output Estimation

```python
response = requests.post(
    "http://localhost:8000/pv/estimate-output",
    headers={"X-API-Key": "your-api-key"},
    json={
        "panel_capacity_kw": 5.0,
        "panel_efficiency": 0.2,
        "system_losses": 0.14,
        "tilt_angle": 37.0,
        "azimuth_angle": 180.0,
        "location_lat": 37.7749,
        "location_lon": -122.4194
    }
)

print(f"Annual Output: {response.json()['annual_energy_kwh']} kWh")
```

### Example: Image Analysis

```python
import base64

with open("panel_image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

response = requests.post(
    "http://localhost:8000/image-analysis/analyze",
    headers={"X-API-Key": "your-api-key"},
    json={"image_base64": image_base64}
)

data = response.json()
print(f"Health Score: {data['overall_health_score']}")
print(f"Defects Found: {len(data['defects'])}")
```

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_chat.py

# Run with verbose output
pytest -v
```

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Prometheus Metrics

```bash
curl http://localhost:8000/metrics
```

Metrics include:
- HTTP request counts and durations
- Active request gauge
- Custom application metrics

---

## 🛠️ Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the run script
python run.py
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint
flake8 app/ tests/

# Type checking
mypy app/
```

---

## 📚 Architecture

### Services Overview

1. **RAG Engine** (`rag_engine.py`)
   - ChromaDB vector database
   - Sentence transformers for embeddings
   - Semantic search and retrieval

2. **LLM Orchestrator** (`llm_orchestrator.py`)
   - OpenAI/Anthropic integration
   - Prompt engineering
   - Token counting and management

3. **Citation Manager** (`citation_manager.py`)
   - Multiple citation formats (APA, MLA, Chicago, IEEE)
   - Deduplication and ranking
   - Bibliography generation

4. **PV Calculator** (`pv_calculator.py`)
   - Energy output estimation
   - Performance ratio calculation
   - Financial analysis

5. **Image Analyzer** (`image_analyzer.py`)
   - Computer vision preprocessing
   - Defect detection (mock - ready for model integration)
   - Health scoring

6. **Document Processor** (`document_ingestion.py`)
   - Multi-format support (PDF, DOCX, TXT)
   - Text extraction and chunking
   - Async processing

---

## 🚀 Deployment

### Docker (Coming Soon)

```bash
docker build -t solar-pv-ai .
docker run -p 8000:8000 --env-file .env solar-pv-ai
```

### Production Considerations

- Use a production ASGI server (Gunicorn + Uvicorn workers)
- Configure proper API keys and secrets
- Set up SSL/TLS certificates
- Implement rate limiting
- Configure monitoring and alerting
- Use a production-grade vector database
- Deploy actual ML models for defect detection

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Vector storage with [ChromaDB](https://www.trychroma.com/)
- LLM integration via [OpenAI](https://openai.com/) and [Anthropic](https://www.anthropic.com/)
- Image processing with [OpenCV](https://opencv.org/) and [Pillow](https://python-pillow.org/)

---

## 📧 Support

For questions, issues, or feature requests, please open an issue on GitHub or contact the development team.

---

**Happy Coding! ☀️⚡**
