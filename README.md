# Solar PV LLM AI

![CI/CD Pipeline](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/workflows/CI/CD%20Pipeline/badge.svg)

AI-powered Solar PV analysis system with incremental training, RAG (Retrieval Augmented Generation), citation tracking, and autonomous delivery. Built to serve audiences from beginners to experts in solar photovoltaic technology.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

Solar PV LLM AI is an intelligent system that combines large language models (LLMs) with domain-specific knowledge about solar photovoltaic systems. The platform uses:

- **RAG (Retrieval Augmented Generation)** for accurate, context-aware responses
- **Multiple LLM providers** (OpenAI GPT-4, Anthropic Claude) for robust AI capabilities
- **Vector database (Pinecone)** for efficient semantic search
- **NREL API integration** for authoritative solar energy data
- **Citation tracking** to ensure transparency and verifiability

## Features

- 🤖 **Multi-LLM Support**: Integrate with OpenAI GPT-4 and Anthropic Claude
- 📚 **RAG Pipeline**: Advanced retrieval-augmented generation for accurate responses
- 🔍 **Vector Search**: Pinecone-powered semantic search for relevant information
- 📊 **NREL Integration**: Direct access to National Renewable Energy Laboratory data
- 🎯 **Citation Tracking**: Transparent source attribution for all generated content
- 🔄 **Incremental Learning**: Continuous improvement through data updates
- 🐳 **Docker Support**: Containerized deployment for consistency
- 🚀 **CI/CD Pipeline**: Automated testing and deployment via GitHub Actions
- 📈 **Scalable Architecture**: Microservices-based design for growth

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│  Pinecone   │
│  (React)    │      │  (FastAPI)   │      │  (Vector DB)│
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├─────▶ OpenAI GPT-4
                            ├─────▶ Anthropic Claude
                            ├─────▶ NREL API
                            │
                     ┌──────┴──────┐
                     │             │
                ┌────▼────┐   ┌────▼────┐
                │PostgreSQL│   │  Redis  │
                └──────────┘   └─────────┘
```

## Prerequisites

### Required

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git** (2.30+)

### For Local Development (Without Docker)

- **Python** 3.11+
- **Node.js** 20+
- **PostgreSQL** 16+
- **Redis** 7+

### API Keys

You will need API keys from the following services:

1. **OpenAI**: https://platform.openai.com/api-keys
2. **Anthropic**: https://console.anthropic.com/
3. **Pinecone**: https://app.pinecone.io/
4. **NREL**: https://developer.nrel.gov/signup/

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI.git
   cd Solar-PV-LLM-AI
   ```

2. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   nano .env  # or use your preferred editor
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PgAdmin (optional): http://localhost:5050

5. **View logs**
   ```bash
   docker-compose logs -f
   ```

6. **Stop services**
   ```bash
   docker-compose down
   ```

## Environment Setup

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Configure Required Variables

Edit `.env` and set the following **required** variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Anthropic Claude Configuration
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key-here

# Pinecone Configuration
PINECONE_API_KEY=your-actual-pinecone-key-here
PINECONE_ENVIRONMENT=your-pinecone-environment  # e.g., us-east1-gcp

# NREL API Configuration
NREL_API_KEY=your-actual-nrel-key-here

# Database (for production - defaults work for Docker)
POSTGRES_PASSWORD=change-this-to-secure-password
REDIS_PASSWORD=change-this-to-secure-password

# Security
JWT_SECRET=generate-a-random-secure-secret-here
```

### 3. Optional Configuration

See [ENVIRONMENT.md](./docs/ENVIRONMENT.md) for complete documentation on all environment variables.

## Development

### Backend Development

#### Using Docker
```bash
# Backend runs with hot-reload enabled
docker-compose up backend
```

#### Without Docker
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend Development

#### Using Docker
```bash
# Frontend runs with Vite HMR enabled
docker-compose up frontend
```

#### Without Docker
```bash
cd frontend
npm install
npm run dev
```

### Code Quality

#### Backend
```bash
cd backend

# Format code
black .

# Lint
flake8 .

# Type checking
mypy app/

# Run tests
pytest
```

#### Frontend
```bash
cd frontend

# Lint
npm run lint

# Format
npm run format

# Run tests
npm run test
```

## Testing

### Run All Tests
```bash
# Backend tests
docker-compose run backend pytest

# Frontend tests
docker-compose run frontend npm run test

# Integration tests
docker-compose up -d
# Run your integration tests here
docker-compose down
```

### Coverage Reports
```bash
# Backend coverage
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend coverage
cd frontend
npm run test:coverage
open coverage/index.html
```

## Deployment

### Production Deployment

1. **Build production images**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

2. **Deploy to your infrastructure**
   - AWS ECS/EKS
   - Google Cloud Run
   - Azure Container Instances
   - Kubernetes cluster

3. **Set production environment variables**
   - Never commit production `.env` files
   - Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)

### CI/CD Pipeline

The project includes GitHub Actions workflows that automatically:

- ✅ Lint code (Python with Black/Flake8, JavaScript with ESLint)
- ✅ Run tests (pytest for backend, Vitest for frontend)
- ✅ Build Docker images
- ✅ Run security scans (Trivy)
- ✅ Deploy to staging/production (configure in workflow)

## API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

```
GET  /               - Health check
GET  /health         - Detailed health status
POST /api/query      - Submit a query to the LLM
GET  /api/sources    - Retrieve data sources
POST /api/feedback   - Submit user feedback
```

## Project Structure

```
Solar-PV-LLM-AI/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── main.py         # Application entry point
│   │   ├── config.py       # Configuration management
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── tests/              # Backend tests
│   ├── Dockerfile          # Backend container definition
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client services
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   ├── Dockerfile          # Frontend container definition
│   ├── nginx.conf          # Nginx configuration
│   └── package.json        # Node dependencies
│
├── data/                   # Data storage
│   ├── raw/               # Raw data files
│   ├── processed/         # Processed datasets
│   └── models/            # Trained model artifacts
│
├── scripts/               # Utility scripts
│   ├── setup.sh          # Environment setup
│   ├── seed_data.py      # Database seeding
│   └── backup.sh         # Backup utilities
│
├── tests/                 # Integration tests
│   ├── integration/      # End-to-end tests
│   └── unit/            # Unit tests
│
├── .github/
│   └── workflows/        # GitHub Actions CI/CD
│       └── ci-cd.yml    # Main pipeline
│
├── docker-compose.yml    # Development environment
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript/TypeScript
- Write tests for new features
- Update documentation as needed
- Ensure CI/CD pipeline passes

## Troubleshooting

### Common Issues

1. **Docker containers won't start**
   ```bash
   docker-compose down -v  # Remove all containers and volumes
   docker-compose up --build  # Rebuild and start
   ```

2. **Port already in use**
   ```bash
   # Change ports in .env file
   APP_PORT=8001
   FRONTEND_PORT=3001
   ```

3. **API keys not working**
   - Verify keys are correctly set in `.env`
   - Restart containers: `docker-compose restart`
   - Check logs: `docker-compose logs backend`

4. **Database connection issues**
   ```bash
   # Reset database
   docker-compose down postgres -v
   docker-compose up -d postgres
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- NREL for solar energy data
- Pinecone for vector database capabilities

## Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for the solar energy community**
