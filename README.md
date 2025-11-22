# ☀️ Solar PV LLM AI - Intelligent Chatbot

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.31.0-red)

An intelligent RAG-powered chatbot for Solar PV professionals, combining advanced AI technologies with comprehensive IEC standards knowledge.

## 🌟 Features

### 🤖 AI-Powered Chat Assistant
- **RAG Technology**: Retrieval-Augmented Generation with IEC standards database
- **Multi-LLM Support**: Intelligent routing between Claude, GPT-4, and Gemini
- **Context-Aware**: Maintains conversation history and context
- **Citation Management**: Automatic extraction and formatting of technical references

### 🔍 Smart Search
- **Semantic Search**: Vector-based search through IEC standards
- **Advanced Filtering**: Filter by standard series, type, and year
- **Relevance Scoring**: AI-powered ranking of search results
- **Quick Access**: Fast retrieval from Pinecone vector database

### 🧮 PV Calculators
- **System Sizing**: Calculate array and battery requirements
- **Energy Yield**: Annual production estimates using NREL APIs
- **Performance Ratio**: System efficiency calculations
- **String Configuration**: Optimal string design
- **Tilt Optimization**: Location-specific angle optimization

### 📷 Image Analysis
- **Defect Detection**: AI-powered analysis of solar panel images
- **EL Image Analysis**: Detect cell cracks, hotspots, and defects
- **Thermal Imaging**: IR image processing for thermal issues
- **Visual Inspection**: Automated quality control

### 📚 Document Library
- **IEC Standards**: Comprehensive collection of PV standards
- **Metadata Extraction**: Automatic parsing of document properties
- **Full-Text Search**: Search within document contents
- **Version Control**: Track document revisions

### 📊 Analytics Dashboard
- **Usage Metrics**: Query volume and response times
- **User Analytics**: Satisfaction scores and feedback
- **Popular Topics**: Most searched standards and topics
- **Performance Monitoring**: System health and uptime

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                      │
│  • Interactive UI    • Real-time Chat    • Visualizations   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  • API Endpoints    • Business Logic    • Orchestration     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                    AI/ML Services                            │
│  • RAG Engine      • Vector DB (Pinecone)                   │
│  • Multi-LLM       • Image Analysis                         │
│  • Citations       • NREL APIs                              │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip or conda
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the Streamlit app
streamlit run streamlit_app.py
```

### Environment Variables

Create a `.env` file with the following:

```env
# AI/LLM APIs
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_gemini_api_key

# Vector Database
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env
PINECONE_INDEX_NAME=solar-pv-standards

# NREL APIs
NREL_API_KEY=your_nrel_api_key

# Application Settings
APP_NAME=Solar PV AI Assistant
APP_VERSION=1.0.0
DEBUG=False
```

## 🚀 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy from repository
4. Add secrets in Streamlit dashboard

### Docker

```bash
# Build image
docker build -t solar-pv-ai .

# Run container
docker run -p 8501:8501 --env-file .env solar-pv-ai
```

### Railway / Heroku

Follow platform-specific deployment guides.

## 📋 Features by Branch

This repository consolidates work from multiple feature branches:

| Branch | Feature | Status |
|--------|---------|--------|
| `claude/setup-project-structure` | Project foundation | ✅ Merged |
| `claude/iec-pdf-ingestion-pipeline` | Document processing | ✅ Merged |
| `claude/pinecone-vector-integration` | Vector database | ✅ Merged |
| `claude/build-rag-engine` | RAG implementation | ✅ Merged |
| `claude/multi-llm-orchestrator` | Multi-LLM routing | ✅ Merged |
| `claude/citation-extraction-automation` | Citation management | ✅ Merged |
| `claude/pv-calculators-nrel` | NREL calculators | ✅ Merged |
| `claude/pv-image-analysis-module` | Image analysis | ✅ Merged |
| `claude/fastapi-backend-endpoints` | Backend APIs | ✅ Merged |
| `claude/streamlit-frontend-complete` | UI/UX | ✅ Merged |
| `claude/multi-agent-task-routing` | Agent system | ✅ Merged |
| `claude/incremental-learning-feedback` | Learning system | ✅ Merged |
| `claude/setup-monitoring-logging-alerts` | Observability | ✅ Merged |
| `claude/containerize-production-deployment` | Deployment | ✅ Merged |

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_rag_engine.py
```

## 📖 Documentation

- **Architecture**: `/docs/architecture.md`
- **API Reference**: `/docs/api_reference.md`
- **User Guide**: `/docs/user_guide.md`
- **Development Guide**: `/docs/development.md`

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 👤 Author

**Ganesh Gowri**
- GitHub: [@ganeshgowri-ASA](https://github.com/ganeshgowri-ASA)

## 🙏 Acknowledgments

- IEC for technical standards
- NREL for solar calculation APIs
- Anthropic, OpenAI, Google for LLM APIs
- Pinecone for vector database
- Streamlit community

## 📞 Support

For support and questions:
- Open an [issue](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/issues)
- Email: support@example.com

---

**Built with ❤️ for the Solar PV community**
