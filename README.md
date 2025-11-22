# Solar PV LLM AI

AI-powered Solar Photovoltaic analysis platform with incremental training, Retrieval-Augmented Generation (RAG), citation tracking, and autonomous delivery system. Built for broad audiences from beginners to experts.

[![CI/CD](https://github.com/your-org/Solar-PV-LLM-AI/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/your-org/Solar-PV-LLM-AI/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18.2-blue.svg)](https://reactjs.org/)

## Features

- **Incremental Training**: Continuously improve ML models with new data
- **RAG (Retrieval-Augmented Generation)**: AI-powered question answering with source citations
- **Multi-Audience Support**: Adaptive responses for beginners to experts
- **Real-time Analytics**: Monitor solar PV system performance
- **Autonomous Delivery**: Automated ML model deployment and monitoring
- **Production-Ready**: Fully containerized with Kubernetes orchestration
- **Scalable Architecture**: Auto-scaling based on load
- **Comprehensive Monitoring**: Prometheus + Grafana observability

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴─────────┬────────────┬─────────────┐
        │                  │            │             │
   ┌────▼────┐      ┌─────▼──────┐  ┌──▼──────┐  ┌──▼────────┐
   │Frontend │      │  Backend   │  │ Celery  │  │ Flower    │
   │(React)  │      │  (FastAPI) │  │ Workers │  │(Monitor)  │
   └─────────┘      └─────┬──────┘  └────┬────┘  └───────────┘
                          │              │
                 ┌────────┴──────────────┴────────┐
                 │                                 │
           ┌─────▼──────┐                   ┌─────▼──────┐
           │ PostgreSQL │                   │   Redis    │
           │  Database  │                   │   Cache    │
           └────────────┘                   └────────────┘
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Celery**: Distributed task queue
- **PyTorch**: Machine learning framework
- **LangChain**: RAG implementation
- **Pydantic**: Data validation

### Frontend
- **React**: UI framework
- **TailwindCSS**: Utility-first CSS
- **React Query**: Data fetching and caching
- **Recharts**: Data visualization

### Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **Terraform**: Infrastructure as Code
- **GitHub Actions**: CI/CD
- **Prometheus**: Metrics
- **Grafana**: Visualization

### Databases
- **PostgreSQL**: Primary database
- **Redis**: Caching and message broker
- **Vector Database**: RAG embeddings (pgvector/Pinecone/Weaviate)

## Quick Start

### Prerequisites

- Docker (v24.0+)
- Docker Compose (v2.20+)
- Git

### Local Development

```bash
# Clone repository
git clone https://github.com/your-org/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access services
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
# Flower: http://localhost:5555
```

### Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive deployment instructions.

```bash
# Quick production deployment to Kubernetes
cd terraform
terraform init
terraform apply

# Deploy application
kubectl apply -f kubernetes/
```

## API Documentation

Once the backend is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Example API Calls

```bash
# Health check
curl http://localhost:8000/health

# List solar PV systems
curl http://localhost:8000/api/v1/solar-pv/systems

# Make prediction
curl -X POST http://localhost:8000/api/v1/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "temperature": 25,
      "irradiance": 800,
      "humidity": 60
    },
    "model_name": "solar_efficiency_predictor"
  }'

# RAG query
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the optimal angle for solar panels?",
    "audience_level": "beginner"
  }'
```

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run linters
black .
flake8 .
mypy app/

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

### Workers Development

```bash
cd workers

# Start Celery worker
celery -A celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A celery_app beat --loglevel=info

# Monitor with Flower
celery -A celery_app flower
```

## Testing

### Unit Tests

```bash
# Backend
cd backend
pytest --cov=app tests/

# Frontend
cd frontend
npm test -- --coverage
```

### Integration Tests

```bash
# Run all integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Load Testing

```bash
# Simple load test
./scripts/load-test.sh

# Advanced load test with Locust
cd load-testing
locust -f locustfile.py --host=http://localhost:8000
```

## Monitoring

### Metrics

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Flower**: http://localhost:5555

### Key Metrics

- API request rate and latency
- Error rates
- Database connection pool usage
- Celery task queue length
- ML model inference time
- System resource utilization

## Deployment Strategies

### Rolling Update (Default)

```bash
kubectl set image deployment/backend backend=new-image:v1.2.3 -n solar-pv-llm-ai
```

### Canary Deployment

```bash
# Deploy canary with 10% traffic
kubectl apply -f kubernetes/canary/
```

### Blue-Green Deployment

```bash
# Switch traffic to green deployment
kubectl patch service backend -p '{"spec":{"selector":{"version":"green"}}}'
```

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n solar-pv-llm-ai

# Scale workers
kubectl scale deployment celery-worker --replicas=3 -n solar-pv-llm-ai
```

### Auto-scaling

Horizontal Pod Autoscaler (HPA) is configured automatically:

```bash
# View autoscaling status
kubectl get hpa -n solar-pv-llm-ai
```

## Backup & Recovery

### Automated Backups

Backups run daily at 2 AM UTC and are stored in S3:

```bash
# Manual backup
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh
```

### Disaster Recovery

See [RUNBOOK.md](./RUNBOOK.md) for detailed disaster recovery procedures.

## Rollback

```bash
# Quick rollback to previous version
./scripts/rollback.sh

# Rollback specific deployment
./scripts/rollback.sh 0 backend
```

## Security

- **Secrets Management**: Kubernetes Secrets / Sealed Secrets
- **Network Policies**: Pod-to-pod communication restrictions
- **RBAC**: Role-based access control
- **SSL/TLS**: Automated certificate management with cert-manager
- **Image Scanning**: Vulnerability scanning in CI/CD
- **Non-root Containers**: All containers run as non-root users

## Performance

- **Response Time**: P95 < 200ms
- **Throughput**: 1000+ requests/second
- **Availability**: 99.9% uptime SLA
- **Scalability**: Auto-scales from 2 to 10 pods

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

- [Deployment Guide](./DEPLOYMENT.md) - Complete deployment instructions
- [Operations Runbook](./RUNBOOK.md) - Incident response and operations
- [API Documentation](http://localhost:8000/api/docs) - Interactive API docs
- [Architecture Decisions](./docs/architecture.md) - Design decisions (TODO)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: https://docs.your-domain.com
- **Issues**: https://github.com/your-org/Solar-PV-LLM-AI/issues
- **Email**: support@your-domain.com
- **Slack**: #solar-pv-llm-ai

## Roadmap

- [ ] Multi-model support (OpenAI, Anthropic, local models)
- [ ] Real-time streaming predictions
- [ ] Mobile app (React Native)
- [ ] Advanced visualization dashboards
- [ ] Multi-tenancy support
- [ ] GraphQL API
- [ ] Internationalization (i18n)
- [ ] Advanced ML model versioning

## Acknowledgments

- FastAPI for the excellent web framework
- React community for frontend tools
- Kubernetes for orchestration
- OpenAI/Anthropic for LLM APIs

## Project Status

🚀 **Active Development** - Version 1.0.0

---

Made with ❤️ by the Solar PV LLM AI Team
