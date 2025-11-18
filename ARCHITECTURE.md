# Solar PV LLM AI System - Architecture Documentation

## Overview

The Solar PV LLM AI System is a comprehensive incremental learning platform designed to provide expert-level knowledge about Solar Photovoltaic systems. It features continuous learning through user feedback, automated model retraining, and zero-downtime updates.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          User Interface                          │
│                     (Web/Mobile/API Clients)                     │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                       │
│  ┌──────────────┬─────────────────┬─────────────────────────┐  │
│  │Query Routes  │Feedback Routes  │Admin Routes             │  │
│  └──────────────┴─────────────────┴─────────────────────────┘  │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Service Layer                             │
│  ┌──────────┬──────────┬──────────┬──────────┬────────────────┐│
│  │   RAG    │ Feedback │  Vector  │   LLM    │   Retraining   ││
│  │ Service  │ Service  │  Store   │ Service  │   Service      ││
│  └──────────┴──────────┴──────────┴──────────┴────────────────┘│
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                          │
│  ┌──────────────┬────────────────┬─────────────────────────┐   │
│  │  PostgreSQL  │ Vector Store   │     Redis (Celery)      │   │
│  │  (Metadata)  │ (Embeddings)   │     (Task Queue)        │   │
│  └──────────────┴────────────────┴─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. RAG (Retrieval Augmented Generation) Service

**Purpose**: Combines document retrieval with LLM generation for accurate, cited responses.

**Key Features**:
- Query embedding generation
- Semantic search in vector store
- Context building from retrieved documents
- LLM-based response generation with citations
- Confidence scoring

**Workflow**:
1. User submits query
2. Query is embedded using embedding model
3. Top-K relevant documents retrieved from vector store
4. Context built from retrieved documents
5. LLM generates response with context
6. Citations extracted and returned

### 2. Feedback Collection System

**Purpose**: Collect and analyze user feedback for continuous improvement.

**Database Schema**:
- `user_feedbacks`: Core feedback data (rating, helpfulness, accuracy)
- `feedback_comments`: Detailed user comments
- `feedback_tags`: Categorization tags
- Review status tracking (pending, approved, rejected)

**Features**:
- Multi-dimensional feedback (rating, helpfulness, accuracy, completeness)
- Comment collection for detailed insights
- Tag-based categorization
- Review workflow for feedback quality control

**Analysis Capabilities**:
- Low-confidence response detection
- Negative feedback identification
- Feedback trend analysis
- Statistics and metrics

### 3. Vector Store Service

**Purpose**: Efficient storage and retrieval of document embeddings.

**Supported Backends**:
- **Pinecone**: Managed vector database (recommended for production)
- **ChromaDB**: Local/self-hosted option
- **Weaviate**: Self-hosted with advanced features
- **Qdrant**: Modern vector database
- **FAISS**: Facebook's similarity search library

**Zero-Downtime Update Strategy**:
1. Add new documents with version tag
2. Verify new documents are searchable
3. Switch active version atomically
4. Keep old version for rollback
5. Clean up old versions after grace period

### 4. LLM Service with LoRA Fine-Tuning

**Purpose**: Manage LLM interactions and model fine-tuning.

**Supported Providers**:
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude models
- **Azure OpenAI**: Enterprise deployment
- **Local Models**: HuggingFace transformers

**LoRA Fine-Tuning**:
- Low-Rank Adaptation for efficient fine-tuning
- Configurable parameters (r, alpha, dropout)
- Training data preparation from feedback
- Model versioning and deployment
- Checkpoint management

**Confidence Scoring**:
- Heuristic-based confidence calculation
- Response length analysis
- Completion status verification
- Token usage patterns

### 5. Retraining Service

**Purpose**: Automated model retraining based on feedback signals.

**Trigger Conditions**:
- Sufficient feedback collected (configurable threshold)
- Low average rating below threshold
- Low positive feedback rate
- Scheduled retraining (weekly, monthly)

**Retraining Pipeline**:
1. **Data Preparation**:
   - Collect approved high-quality feedbacks
   - Extract query-response pairs
   - Format for training
   - Split positive/negative examples

2. **Training Execution**:
   - Load base model
   - Configure LoRA parameters
   - Train adapters on feedback data
   - Save checkpoints

3. **Evaluation**:
   - Validate on held-out set
   - Calculate metrics
   - Compare with baseline

4. **Deployment**:
   - Blue-green deployment strategy
   - Zero-downtime model swap
   - Rollback capability

### 6. Celery Task Queue

**Purpose**: Asynchronous task execution and scheduling.

**Tasks**:
- **Scheduled Tasks**:
  - `check_retraining_trigger`: Weekly check for retraining needs
  - `collect_system_metrics`: Hourly metrics collection

- **Async Tasks**:
  - `execute_retraining`: Model training pipeline
  - `deploy_trained_model`: Model deployment
  - `update_vector_store`: Knowledge base updates

**Monitoring**: Flower dashboard for task monitoring

## Database Schema

### Core Tables

#### Users and Authentication
- `users`: User accounts and roles

#### Queries and Responses
- `queries`: User queries
- `query_responses`: AI-generated responses
- `retrieved_documents`: Links queries to retrieved documents

#### Feedback System
- `user_feedbacks`: Feedback ratings and status
- `feedback_comments`: Detailed feedback comments
- `feedback_tags`: Categorization tags

#### Knowledge Base
- `documents`: Source documents
- `document_chunks`: Chunked document segments
- Metadata for vector store synchronization

#### Training and Deployment
- `training_runs`: Model training executions
- `retraining_feedbacks`: Links feedback to training runs
- `model_deployments`: Production model deployments
- `deployment_metrics`: Performance tracking

#### Monitoring
- `system_metrics`: System-wide metrics
- `audit_logs`: Action audit trail

## API Endpoints

### Query API (`/api/v1/query`)
- `POST /`: Submit query and get response
- `GET /{query_id}`: Get query details
- `POST /search`: Search knowledge base directly
- `GET /session/{session_id}`: Get session history

### Feedback API (`/api/v1/feedback`)
- `POST /`: Create feedback
- `GET /{feedback_id}`: Get feedback details
- `PUT /{feedback_id}`: Update review status
- `POST /{feedback_id}/comments`: Add comment
- `POST /{feedback_id}/tags`: Add tag
- `GET /stats/summary`: Get feedback statistics
- `GET /review/pending`: Get feedbacks pending review
- `POST /review/bulk-update`: Bulk update review status
- `GET /analysis/low-confidence`: Get low confidence responses
- `GET /analysis/negative`: Get negative feedbacks
- `GET /analysis/trends`: Get feedback trends
- `GET /training/candidates`: Get training data candidates

### Admin API (`/api/v1/admin`)

#### Dashboard & Monitoring
- `GET /dashboard/metrics`: Comprehensive dashboard metrics
- `GET /health`: System health check

#### Retraining Management
- `GET /retraining/recommendation`: Get retraining recommendation
- `POST /retraining/trigger`: Manually trigger retraining
- `GET /retraining/runs`: List training runs
- `GET /retraining/runs/{run_id}`: Get training run details
- `GET /retraining/tasks/{task_id}`: Get task status
- `POST /retraining/tasks/{task_id}/cancel`: Cancel task

#### Model Deployment
- `POST /deployments/deploy`: Deploy trained model
- `GET /deployments/active`: Get active deployment
- `POST /deployments/{deployment_id}/rollback`: Rollback deployment

#### Knowledge Base
- `POST /knowledge-base/update`: Update knowledge base
- `GET /knowledge-base/stats`: Get KB statistics

#### System Management
- `GET /config`: Get system configuration
- `GET /audit-logs`: Get audit logs

## Configuration

### Environment Variables

See `.env.example` for comprehensive configuration options.

**Critical Settings**:
- `DATABASE_URL`: PostgreSQL connection string
- `VECTOR_STORE_TYPE`: Vector store backend
- `VECTOR_STORE_API_KEY`: Vector store credentials
- `LLM_PROVIDER`: LLM provider (openai, anthropic)
- `LLM_API_KEY`: LLM API credentials
- `CELERY_BROKER_URL`: Redis connection for Celery

**Fine-Tuning Settings**:
- `LORA_R`: LoRA rank
- `LORA_ALPHA`: LoRA alpha
- `LORA_DROPOUT`: Dropout rate
- `TRAINING_BATCH_SIZE`: Training batch size
- `TRAINING_EPOCHS`: Number of epochs
- `TRAINING_LEARNING_RATE`: Learning rate

## Deployment

### Docker Compose Deployment

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Services:
- **api**: Main FastAPI application (port 8000)
- **postgres**: PostgreSQL database (port 5432)
- **redis**: Redis for Celery (port 6379)
- **celery-worker**: Background task worker
- **celery-beat**: Task scheduler
- **flower**: Celery monitoring (port 5555)

### Manual Deployment

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Set up database
python -m backend.database.setup

# Run migrations
alembic upgrade head

# Start API server
uvicorn backend.app:app --host 0.0.0.0 --port 8000

# Start Celery worker
celery -A backend.services.celery_tasks worker --loglevel=info

# Start Celery beat
celery -A backend.services.celery_tasks beat --loglevel=info
```

## Monitoring and Observability

### Metrics Collection
- System-wide metrics collected hourly
- Per-deployment metrics tracking
- Request/response metrics
- Feedback metrics
- Training metrics

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking with stack traces
- Audit trail for admin actions

### Health Checks
- Database connectivity
- Vector store health
- LLM service availability
- Celery task queue status

### Prometheus Integration
- HTTP request metrics
- Response time histograms
- Custom business metrics
- Available at `/metrics` endpoint

## Security Considerations

### Authentication & Authorization
- JWT-based authentication (to be implemented)
- Role-based access control (RBAC)
- Admin-only endpoints protection

### Data Privacy
- User data encryption at rest
- Secure credential management
- Audit logging for data access

### API Security
- Rate limiting (to be implemented)
- Input validation
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection

## Performance Optimization

### Caching Strategies
- Vector store query caching
- LLM response caching for identical queries
- Database query optimization

### Async Operations
- Background task processing with Celery
- Non-blocking API endpoints
- Batch processing for embeddings

### Scaling Considerations
- Horizontal scaling of API servers
- Multiple Celery workers
- Database connection pooling
- Vector store sharding

## Continuous Learning Workflow

```
User Query → RAG Response → User Feedback → Feedback Analysis
                                                    │
                                                    ▼
                                            Retraining Decision
                                                    │
                                                    ▼
                                         Data Preparation
                                                    │
                                                    ▼
                                         LoRA Fine-Tuning
                                                    │
                                                    ▼
                                         Model Evaluation
                                                    │
                                                    ▼
                                         Deployment (Blue-Green)
                                                    │
                                                    ▼
                                         Performance Monitoring
                                                    │
                                                    ▼
                                         Rollback if needed
```

## Future Enhancements

### Planned Features
1. **A/B Testing Framework**: Compare model versions
2. **Advanced Analytics Dashboard**: Real-time insights
3. **Multi-language Support**: Internationalization
4. **Conversation Context**: Multi-turn dialogue
5. **Active Learning**: Strategic example selection
6. **Explainable AI**: Model decision explanations
7. **Advanced Security**: OAuth2, API keys, rate limiting
8. **Performance Dashboard**: Real-time monitoring UI

### Research Directions
1. **Reinforcement Learning**: RLHF integration
2. **Few-Shot Learning**: Better adaptation with less data
3. **Meta-Learning**: Faster learning for new domains
4. **Federated Learning**: Privacy-preserving training
5. **Knowledge Distillation**: Model compression

## Troubleshooting

### Common Issues

**Database Connection Errors**:
- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Check network connectivity

**Vector Store Errors**:
- Verify API credentials
- Check vector store service status
- Validate dimension compatibility

**LLM API Errors**:
- Check API key validity
- Monitor rate limits
- Verify model availability

**Celery Task Failures**:
- Check Redis connectivity
- Review worker logs
- Verify task dependencies

## Contributing

Contributions are welcome! Please follow:
1. Code style: Black formatter, PEP 8
2. Tests: Pytest with >80% coverage
3. Documentation: Update relevant docs
4. Security: Report vulnerabilities privately

## License

[To be determined]

## Contact

[To be determined]
