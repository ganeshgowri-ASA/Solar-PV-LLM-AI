# Deployment Guide - Solar PV LLM AI System

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Production Deployment](#production-deployment)
4. [Configuration](#configuration)
5. [Database Setup](#database-setup)
6. [Vector Store Setup](#vector-store-setup)
7. [LLM Configuration](#llm-configuration)
8. [Monitoring](#monitoring)
9. [Backup and Recovery](#backup-and-recovery)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended) or macOS
- **Python**: 3.11+
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for orchestration)
- **RAM**: Minimum 8GB (16GB+ recommended)
- **Storage**: Minimum 20GB free space

### External Services
- **PostgreSQL**: 15+ (or use Docker)
- **Redis**: 7+ (for Celery task queue)
- **Vector Store**: Pinecone, ChromaDB, or Weaviate
- **LLM Provider**: OpenAI API or Anthropic API

## Quick Start

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/your-org/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
```

2. **Create environment file**
```bash
cp .env.example .env
```

3. **Configure environment variables**
Edit `.env` with your settings:
```bash
# Required: LLM Provider
LLM_API_KEY=your_openai_api_key

# Required: Vector Store
VECTOR_STORE_TYPE=pinecone
VECTOR_STORE_API_KEY=your_pinecone_api_key

# Required: Security
SECRET_KEY=$(openssl rand -hex 32)
ADMIN_PASSWORD_HASH=$(python -c "from passlib.hash import bcrypt; print(bcrypt.hash('your_admin_password'))")
```

4. **Start all services**
```bash
docker-compose up -d
```

5. **Verify deployment**
```bash
# Check service health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# View Celery monitoring
open http://localhost:5555
```

6. **Initialize database**
```bash
docker-compose exec api python -m alembic upgrade head
```

7. **Add initial documents** (optional)
```bash
# Use the admin API to upload documents
curl -X POST http://localhost:8000/api/v1/admin/knowledge-base/update \
  -H "Content-Type: application/json" \
  -d @sample_documents.json
```

### Option 2: Manual Installation

1. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

2. **Set up PostgreSQL**
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE solar_pv_ai;
CREATE USER solar_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE solar_pv_ai TO solar_user;
\q
```

3. **Set up Redis**
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
cd backend
alembic upgrade head
```

6. **Start services**

Terminal 1 - API Server:
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

Terminal 2 - Celery Worker:
```bash
celery -A backend.services.celery_tasks worker --loglevel=info
```

Terminal 3 - Celery Beat:
```bash
celery -A backend.services.celery_tasks beat --loglevel=info
```

Terminal 4 - Flower (optional):
```bash
celery -A backend.services.celery_tasks flower --port=5555
```

## Production Deployment

### 1. Infrastructure Setup

#### Using AWS

**Architecture**:
- EC2/ECS for application servers
- RDS PostgreSQL for database
- ElastiCache Redis for Celery
- S3 for model checkpoints and logs
- CloudWatch for monitoring

**Terraform Configuration** (example):
```hcl
# See infrastructure/terraform/ directory
terraform init
terraform plan
terraform apply
```

#### Using Google Cloud

**Architecture**:
- Cloud Run for API
- Cloud SQL PostgreSQL
- Memorystore Redis
- Cloud Storage for artifacts
- Cloud Monitoring

### 2. Docker Production Build

**Dockerfile.prod**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install production dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copy application
COPY backend/ ./backend/

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Production server
CMD ["gunicorn", "backend.app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 3. Kubernetes Deployment

```yaml
# See kubernetes/ directory for complete manifests

apiVersion: apps/v1
kind: Deployment
metadata:
  name: solar-pv-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: solar-pv-api
  template:
    metadata:
      labels:
        app: solar-pv-api
    spec:
      containers:
      - name: api
        image: solar-pv-llm:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

### 4. Reverse Proxy (Nginx)

```nginx
upstream solar_pv_api {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    location / {
        proxy_pass http://solar_pv_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://solar_pv_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Configuration

### Environment Variables

**Critical Settings**:
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Vector Store
VECTOR_STORE_TYPE=pinecone
VECTOR_STORE_API_KEY=your_key
VECTOR_STORE_INDEX_NAME=solar-pv-prod

# LLM
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_API_KEY=your_key

# Security
SECRET_KEY=your_secret_key_min_32_chars
ADMIN_PASSWORD_HASH=$2b$12$...

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Monitoring
ENABLE_PROMETHEUS=true
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Performance Tuning

**Database**:
```bash
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
DATABASE_ECHO=false
```

**LLM**:
```bash
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048
```

**RAG**:
```bash
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
```

**Retraining**:
```bash
RETRAINING_ENABLED=true
RETRAINING_MIN_FEEDBACK_COUNT=100
TRAINING_BATCH_SIZE=4
TRAINING_EPOCHS=3
```

## Database Setup

### PostgreSQL Optimization

**postgresql.conf**:
```
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Backup Strategy

**Automated Backups**:
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump $DATABASE_URL > $BACKUP_DIR/db_$DATE.sql

# Compress
gzip $BACKUP_DIR/db_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://your-backup-bucket/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

## Vector Store Setup

### Pinecone

```python
# Initialize Pinecone index
import pinecone

pinecone.init(api_key="your_key")

# Create index
pinecone.create_index(
    name="solar-pv-prod",
    dimension=1536,  # OpenAI ada-002
    metric="cosine",
    pods=1,
    pod_type="p1.x1"
)
```

### ChromaDB (Self-hosted)

```bash
# Start ChromaDB server
docker run -d -p 8080:8080 chromadb/chroma:latest
```

## LLM Configuration

### OpenAI

```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
LLM_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-ada-002
```

### Anthropic Claude

```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
LLM_API_KEY=sk-ant-...
# Note: Use OpenAI for embeddings
EMBEDDING_PROVIDER=openai
```

### Azure OpenAI

```bash
LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-12-01-preview
LLM_API_KEY=your_azure_key
```

## Monitoring

### Prometheus + Grafana

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'solar-pv-api'
    static_configs:
      - targets: ['api:9090']
```

### Grafana Dashboard

Import `grafana/dashboard.json` for pre-configured dashboard showing:
- Request rate and latency
- Error rates
- Feedback metrics
- Model performance
- System resource usage

### Alerting

```yaml
# alerts.yml
groups:
  - name: solar_pv_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status="500"}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: LowFeedbackQuality
        expr: avg_feedback_rating < 3.0
        for: 1h
        annotations:
          summary: "Average feedback rating below threshold"
```

## Backup and Recovery

### Disaster Recovery Plan

1. **Regular Backups**:
   - Database: Daily automated backups
   - Model checkpoints: After each training
   - Configuration: Version controlled in Git

2. **Recovery Procedures**:
   ```bash
   # Restore database
   gunzip -c backup.sql.gz | psql $DATABASE_URL

   # Restore vector store
   # (Procedure depends on vector store type)

   # Restore model
   # Copy checkpoint from backup to retraining_checkpoint_dir
   ```

3. **Testing**:
   - Monthly disaster recovery drills
   - Automated backup verification

## Troubleshooting

### Common Issues

**API Not Starting**:
```bash
# Check logs
docker-compose logs api

# Common fixes:
# 1. Database not ready - wait for health check
# 2. Missing environment variables - check .env
# 3. Port already in use - change API_PORT
```

**Celery Tasks Not Running**:
```bash
# Check worker status
docker-compose logs celery-worker

# Check Redis connection
redis-cli ping

# Restart workers
docker-compose restart celery-worker celery-beat
```

**Low Response Quality**:
```bash
# Check feedback metrics
curl http://localhost:8000/api/v1/feedback/stats/summary

# Trigger retraining if needed
curl -X POST http://localhost:8000/api/v1/admin/retraining/trigger \
  -H "Content-Type: application/json" \
  -d '{"model_name": "solar-pv-improved", "training_type": "lora"}'
```

### Performance Issues

**Slow Queries**:
```sql
-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

**High Memory Usage**:
```bash
# Monitor memory
docker stats

# Adjust pool sizes in .env
DATABASE_POOL_SIZE=10  # Reduce if needed
```

### Support

For issues not covered here:
1. Check logs: `docker-compose logs -f`
2. Review [ARCHITECTURE.md](ARCHITECTURE.md)
3. Open an issue on GitHub
4. Contact support: [support email]

## Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS in production
- [ ] Configure firewall rules
- [ ] Set up API rate limiting
- [ ] Regular security updates
- [ ] Audit logs enabled
- [ ] Backup encryption
- [ ] Database encryption at rest
- [ ] Secure API key storage

## Next Steps

After deployment:
1. Add initial documents to knowledge base
2. Test query API with sample questions
3. Configure feedback collection
4. Set up monitoring dashboards
5. Schedule first retraining run
6. Review and optimize performance
