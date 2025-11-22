# Solar PV LLM AI - Deployment Guide

Complete deployment guide for containerized production deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Monitoring & Observability](#monitoring--observability)
5. [Backup & Disaster Recovery](#backup--disaster-recovery)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Docker** (v24.0+): Container runtime
- **Docker Compose** (v2.20+): Local orchestration
- **Kubernetes** (v1.28+): Production orchestration
- **kubectl** (v1.28+): Kubernetes CLI
- **Helm** (v3.12+): Kubernetes package manager (optional)
- **Terraform** (v1.6+): Infrastructure as Code
- **Git**: Version control

### Cloud Accounts (for production)

- AWS Account with appropriate permissions
- Or GCP/Azure account (modify Terraform accordingly)
- Container Registry (GitHub Container Registry, ECR, GCR, or ACR)

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Important**: Update these critical values in `.env`:

- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `DATABASE_PASSWORD`: Strong password
- `REDIS_PASSWORD`: Strong password
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`: Your LLM API keys

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Access Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Flower (Celery Monitor)**: http://localhost:5555
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

### 5. Run Migrations

```bash
# Backend migrations (if using Alembic)
docker-compose exec backend alembic upgrade head
```

### 6. Stop Services

```bash
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v
```

---

## Production Deployment

### Option 1: Kubernetes with Terraform (Recommended)

#### Step 1: Provision Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars

# Plan infrastructure changes
terraform plan

# Apply infrastructure
terraform apply
```

#### Step 2: Configure kubectl

```bash
# AWS EKS
aws eks update-kubeconfig --name solar-pv-llm-ai --region us-east-1

# Verify connection
kubectl get nodes
```

#### Step 3: Create Secrets

```bash
# Create namespace
kubectl apply -f kubernetes/namespace.yaml

# Create secrets (NEVER commit actual secrets!)
kubectl create secret generic solar-pv-secrets \
  --from-literal=DATABASE_PASSWORD=your_password \
  --from-literal=REDIS_PASSWORD=your_password \
  --from-literal=SECRET_KEY=your_secret_key \
  --from-literal=OPENAI_API_KEY=your_api_key \
  --namespace=solar-pv-llm-ai

# Or use sealed-secrets for GitOps
# kubeseal --format=yaml < secrets.yaml > sealed-secrets.yaml
```

#### Step 4: Deploy Application

```bash
# Update image registry in deployment files
export REGISTRY="ghcr.io/your-org"
find kubernetes -name "*.yaml" -exec sed -i "s|REPLACE_WITH_YOUR_REGISTRY|$REGISTRY|g" {} \;

# Apply all Kubernetes manifests
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/postgres/
kubectl apply -f kubernetes/redis/
kubectl apply -f kubernetes/backend/
kubectl apply -f kubernetes/frontend/
kubectl apply -f kubernetes/celery/
kubectl apply -f kubernetes/ingress.yaml

# Check deployment status
kubectl get pods -n solar-pv-llm-ai
kubectl get deployments -n solar-pv-llm-ai
```

#### Step 5: Configure DNS & SSL

```bash
# Install cert-manager for SSL certificates
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Update Ingress with your domain
kubectl edit ingress solar-pv-ingress -n solar-pv-llm-ai
```

#### Step 6: Verify Deployment

```bash
# Check pod status
kubectl get pods -n solar-pv-llm-ai

# Check services
kubectl get svc -n solar-pv-llm-ai

# Check ingress
kubectl get ingress -n solar-pv-llm-ai

# View logs
kubectl logs -f deployment/backend -n solar-pv-llm-ai

# Test endpoints
curl https://api.your-domain.com/health
```

### Option 2: Docker Compose (Production)

```bash
# Use production override
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## CI/CD Pipeline

### GitHub Actions Setup

The repository includes a complete CI/CD pipeline in `.github/workflows/ci-cd.yml`.

#### Required Secrets

Configure these in GitHub repository settings:

- `KUBE_CONFIG_STAGING`: Base64-encoded kubeconfig for staging
- `KUBE_CONFIG_PRODUCTION`: Base64-encoded kubeconfig for production

```bash
# Encode kubeconfig
cat ~/.kube/config | base64 | pbcopy
```

#### Workflow Triggers

- **Push to `main`**: Deploys to production
- **Push to `develop`**: Deploys to staging
- **Pull Requests**: Runs tests only

#### Manual Deployment

```bash
# Trigger workflow manually
gh workflow run ci-cd.yml
```

---

## Monitoring & Observability

### Prometheus & Grafana

```bash
# Access Prometheus
kubectl port-forward -n solar-pv-llm-ai svc/prometheus 9090:9090

# Access Grafana
kubectl port-forward -n solar-pv-llm-ai svc/grafana 3000:3000

# Default credentials: admin/admin
```

### View Metrics

```bash
# Backend metrics
curl http://localhost:8000/metrics

# Kubernetes metrics
kubectl top nodes
kubectl top pods -n solar-pv-llm-ai
```

### Logs

```bash
# View logs
kubectl logs -f deployment/backend -n solar-pv-llm-ai

# Stream logs from all pods
kubectl logs -f -l app=backend -n solar-pv-llm-ai

# Previous pod logs (after crash)
kubectl logs --previous deployment/backend -n solar-pv-llm-ai
```

---

## Backup & Disaster Recovery

### Manual Backup

```bash
# Run backup script
./scripts/backup.sh

# Backups are saved to S3: s3://solar-pv-backups/
```

### Automated Backups

Backups run automatically via CronJob (configure in Kubernetes).

### Restore from Backup

```bash
# Download backup from S3
aws s3 cp s3://solar-pv-backups/database/postgres_backup_20240101_120000.sql.gz .

# Restore to database
gunzip < postgres_backup_20240101_120000.sql.gz | \
  kubectl exec -i -n solar-pv-llm-ai postgres-pod -- \
  psql -U solar_pv_user -d solar_pv_db
```

---

## Rollback

### Quick Rollback

```bash
# Rollback to previous version
./scripts/rollback.sh

# Rollback specific deployment
./scripts/rollback.sh 0 backend

# Rollback to specific revision
./scripts/rollback.sh 3 backend
```

### Manual Rollback

```bash
# View rollout history
kubectl rollout history deployment/backend -n solar-pv-llm-ai

# Rollback to previous version
kubectl rollout undo deployment/backend -n solar-pv-llm-ai

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n solar-pv-llm-ai
```

---

## Load Testing

### Run Load Tests

```bash
# Simple load test
./scripts/load-test.sh

# Advanced load test with Locust
cd load-testing
locust -f locustfile.py --host=https://api.your-domain.com \
  --users=100 --spawn-rate=10 --run-time=10m
```

---

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

- **Backend**: Min 2, Max 10 (70% CPU target)
- **Workers**: Min 2, Max 10 (70% CPU target)

```bash
# Check HPA status
kubectl get hpa -n solar-pv-llm-ai
```

---

## Troubleshooting

### Common Issues

#### Pods Not Starting

```bash
# Describe pod
kubectl describe pod <pod-name> -n solar-pv-llm-ai

# Check events
kubectl get events -n solar-pv-llm-ai --sort-by='.lastTimestamp'
```

#### Database Connection Issues

```bash
# Test database connection
kubectl exec -it -n solar-pv-llm-ai postgres-pod -- psql -U solar_pv_user -d solar_pv_db

# Check database logs
kubectl logs -f deployment/postgres -n solar-pv-llm-ai
```

#### Image Pull Errors

```bash
# Check image pull secrets
kubectl get secrets -n solar-pv-llm-ai

# Create image pull secret
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=your-username \
  --docker-password=your-token \
  -n solar-pv-llm-ai
```

### Health Checks

```bash
# Backend health
curl https://api.your-domain.com/health

# Database connectivity
kubectl exec -n solar-pv-llm-ai deployment/backend -- \
  python -c "from app.core.database import engine; print('OK')"
```

---

## Security Best Practices

1. **Secrets Management**
   - Use Kubernetes Secrets or external secret managers (Vault, AWS Secrets Manager)
   - Never commit secrets to Git
   - Rotate secrets regularly

2. **Network Policies**
   - Implement Kubernetes Network Policies
   - Restrict pod-to-pod communication

3. **RBAC**
   - Use Role-Based Access Control
   - Principle of least privilege

4. **Image Security**
   - Scan images for vulnerabilities
   - Use minimal base images
   - Run containers as non-root

5. **SSL/TLS**
   - Always use HTTPS in production
   - Use cert-manager for automated certificate management

---

## Support

For issues and questions:

- GitHub Issues: https://github.com/your-org/Solar-PV-LLM-AI/issues
- Documentation: https://docs.your-domain.com
- Email: support@your-domain.com

---

## License

[Your License Here]
