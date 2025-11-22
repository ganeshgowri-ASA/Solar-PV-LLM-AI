# Solar-PV-LLM-AI

Repository for developing Solar PV AI LLM system with incremental training, RAG, citation, and autonomous delivery. Built for broad audiences from beginners to experts.

## Project Structure

```
Solar-PV-LLM-AI/
├── backend/              # FastAPI backend with LLM capabilities
│   ├── main.py          # Main application entry point
│   └── requirements.txt # Python dependencies
├── frontend/            # Next.js React frontend
│   ├── app/            # App router pages and API routes
│   ├── package.json    # Node dependencies
│   └── next.config.js  # Next.js configuration
├── docker/             # Docker deployment configuration
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── docker-compose.yml
│   └── .env.example
└── k8s/               # Kubernetes deployment manifests
    ├── backend-deployment.yaml
    ├── frontend-deployment.yaml
    ├── service.yaml
    └── ingress.yaml
```

## Quick Start with Docker

### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+

### Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/Solar-PV-LLM-AI.git
   cd Solar-PV-LLM-AI
   ```

2. Copy environment configuration:
   ```bash
   cp docker/.env.example docker/.env
   # Edit docker/.env with your configuration
   ```

3. Start the services:
   ```bash
   cd docker
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs (debug mode only)

### Running with Database (Full Profile)

```bash
cd docker
docker-compose --profile full up -d
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster 1.25+
- kubectl configured
- nginx-ingress controller
- cert-manager (for TLS)

### Deployment Steps

1. Create the namespace and apply configurations:
   ```bash
   kubectl apply -f k8s/service.yaml
   ```

2. Update secrets in `k8s/service.yaml` with production values

3. Deploy backend and frontend:
   ```bash
   kubectl apply -f k8s/backend-deployment.yaml
   kubectl apply -f k8s/frontend-deployment.yaml
   ```

4. Configure ingress:
   ```bash
   kubectl apply -f k8s/ingress.yaml
   ```

5. Verify deployment:
   ```bash
   kubectl get pods -n solar-pv
   kubectl get services -n solar-pv
   ```

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Environment (production/development) | production |
| `DEBUG` | Enable debug mode | false |
| `LOG_LEVEL` | Logging level | info |
| `DATABASE_URL` | PostgreSQL connection URL | - |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379/0 |
| `SECRET_KEY` | Application secret key | - |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:3000 |
| `OPENAI_API_KEY` | OpenAI API key (optional) | - |
| `ANTHROPIC_API_KEY` | Anthropic API key (optional) | - |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Node environment | production |
| `NEXT_PUBLIC_API_URL` | Backend API URL | http://localhost:8000 |
| `NEXT_PUBLIC_APP_NAME` | Application name | Solar PV LLM AI |

## API Endpoints

### Health Checks

- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check with dependencies
- `GET /health/live` - Kubernetes liveness probe

### API

- `POST /api/v1/query` - Query the LLM system
- `GET /api/v1/models` - List available models

## Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## License

MIT License
