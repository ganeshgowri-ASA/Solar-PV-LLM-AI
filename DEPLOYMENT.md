# Deployment Guide

Complete deployment guide for Solar-PV-LLM-AI platform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)

---

## Prerequisites

### Required Tools

- **Python 3.9+** (3.11 recommended)
- **Docker** (v24.0+)
- **Docker Compose** (v2.20+)
- **Git**

### For Production

- **Kubernetes** (v1.28+)
- **kubectl**
- **Helm** (optional)
- **Terraform** (v1.6+)

### API Keys

- OpenAI API key (for GPT models)
- Anthropic API key (for Claude models)
- Pinecone API key (for vector store)

---

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/your-org/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

**Required Environment Variables:**

```bash
# LLM Providers
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

### 5. Start the Application

```bash
# Start backend API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start frontend (if applicable)
cd frontend
streamlit run app.py
```

### 6. Access the Application

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:8501

---

## Docker Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| backend | 8000 | FastAPI application |
| frontend | 8501 | Streamlit web UI |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache/queue |
| celery-worker | - | Background tasks |
| celery-beat | - | Task scheduler |
| flower | 5555 | Celery monitoring |
| prometheus | 9090 | Metrics collection |
| grafana | 3001 | Dashboards |

### Stop Services

```bash
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Production Docker Compose

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace solar-pv-llm-ai
```

### 2. Create Secrets

```bash
kubectl create secret generic solar-pv-secrets \
  --from-literal=DATABASE_PASSWORD=your_password \
  --from-literal=REDIS_PASSWORD=your_password \
  --from-literal=SECRET_KEY=your_secret_key \
  --from-literal=OPENAI_API_KEY=your_api_key \
  --from-literal=ANTHROPIC_API_KEY=your_api_key \
  --from-literal=PINECONE_API_KEY=your_api_key \
  --namespace=solar-pv-llm-ai
```

### 3. Deploy Application

```bash
# Apply all manifests
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/postgres/
kubectl apply -f kubernetes/redis/
kubectl apply -f kubernetes/backend/
kubectl apply -f kubernetes/frontend/
kubectl apply -f kubernetes/celery/
kubectl apply -f kubernetes/ingress.yaml

# Check status
kubectl get pods -n solar-pv-llm-ai
kubectl get services -n solar-pv-llm-ai
```

### 4. Configure Ingress & SSL

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Apply ClusterIssuer for Let's Encrypt
kubectl apply -f kubernetes/cluster-issuer.yaml

# Update ingress with your domain
kubectl edit ingress solar-pv-ingress -n solar-pv-llm-ai
```

### 5. Verify Deployment

```bash
# Check pods
kubectl get pods -n solar-pv-llm-ai

# View logs
kubectl logs -f deployment/backend -n solar-pv-llm-ai

# Test endpoint
curl https://api.your-domain.com/health
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment backend --replicas=5 -n solar-pv-llm-ai

# Check HPA (auto-scaling)
kubectl get hpa -n solar-pv-llm-ai
```

---

## Cloud Deployment

### AWS (EKS)

#### 1. Provision with Terraform

```bash
cd terraform/aws

# Initialize
terraform init

# Configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars

# Deploy
terraform plan
terraform apply
```

#### 2. Configure kubectl

```bash
aws eks update-kubeconfig --name solar-pv-llm-ai --region us-east-1
kubectl get nodes
```

#### 3. Deploy Application

Follow Kubernetes deployment steps above.

### GCP (GKE)

```bash
cd terraform/gcp
terraform init
terraform apply

gcloud container clusters get-credentials solar-pv-llm-ai --zone us-central1-a
```

### Azure (AKS)

```bash
cd terraform/azure
terraform init
terraform apply

az aks get-credentials --resource-group solar-pv-rg --name solar-pv-llm-ai
```

---

## Configuration

### Environment Variables

See `.env.example` for all available options.

**Core Settings:**

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes* |
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes* |
| `PINECONE_API_KEY` | Pinecone API key | Yes |
| `DATABASE_URL` | PostgreSQL connection | Yes |
| `SECRET_KEY` | Application secret | Yes |
| `REDIS_URL` | Redis connection | No |

*At least one LLM provider required

**RAG Settings:**

| Variable | Default | Description |
|----------|---------|-------------|
| `TOP_K_RETRIEVAL` | 10 | Documents to retrieve |
| `HYBRID_SEARCH_ENABLED` | true | Use hybrid search |
| `BM25_WEIGHT` | 0.3 | Keyword search weight |
| `RERANKING_ENABLED` | true | Enable reranking |

---

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Prometheus Metrics

```bash
curl http://localhost:8000/metrics
```

### Grafana Dashboards

Access at http://localhost:3001 (default: admin/admin)

Pre-configured dashboards:
- System Overview
- API Metrics
- Query Statistics
- Model Performance

### Logs

```bash
# Docker
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/backend -n solar-pv-llm-ai
```

---

## Troubleshooting

### Common Issues

#### Database Connection

```bash
# Test connection
docker-compose exec backend python -c "from app.core.database import engine; print('OK')"
```

#### LLM API Errors

- Verify API keys in `.env`
- Check rate limits
- Validate model availability

#### Vector Store Issues

- Verify Pinecone API key and environment
- Check index exists and dimensions match

### Getting Help

- **Documentation**: [README.md](README.md)
- **Issues**: https://github.com/your-org/Solar-PV-LLM-AI/issues
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md)

---

## Backup & Recovery

### Database Backup

```bash
# Manual backup
pg_dump -U postgres solar_pv_db > backup.sql

# Docker
docker-compose exec postgres pg_dump -U postgres solar_pv_db > backup.sql
```

### Restore

```bash
psql -U postgres solar_pv_db < backup.sql
```

---

## Security Best Practices

1. **Secrets**: Use Kubernetes Secrets or Vault
2. **Network**: Enable network policies
3. **RBAC**: Principle of least privilege
4. **Images**: Scan for vulnerabilities
5. **SSL**: Always use HTTPS in production
6. **Updates**: Keep dependencies updated

---

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.
