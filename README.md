# Solar-PV-LLM-AI

AI-powered Solar PV system with RAG (Retrieval-Augmented Generation), citations, and comprehensive monitoring infrastructure. Built for broad audiences from beginners to experts.

## Features

- **🤖 LLM Integration:** OpenAI/Anthropic models for intelligent responses
- **📚 RAG System:** Retrieval-Augmented Generation with ChromaDB
- **📖 Citation Support:** Automatic citation generation from sources
- **🔍 LangSmith Tracing:** Complete LLM query tracing and monitoring
- **📊 Real-time Monitoring:** Prometheus + Grafana dashboards
- **🚨 Intelligent Alerting:** Automated alerts for errors, latency, and hallucinations
- **🎯 Quality Tracking:** Hallucination detection and confidence scoring
- **📋 Operational Tools:** Health checks, runbooks, and simulation scripts

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- OpenAI API key (or other LLM provider)
- LangSmith API key (optional, for tracing)

### Installation

1. **Clone and setup:**
```bash
git clone <repository-url>
cd Solar-PV-LLM-AI

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **Verify installation:**
```bash
./scripts/monitoring/health_check.sh
```

### Access Points

- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Grafana Dashboard:** http://localhost:3000 (admin/admin123)
- **Prometheus:** http://localhost:9090
- **AlertManager:** http://localhost:9093

## Architecture

```
┌─────────────────────────────────────────────┐
│           Solar PV LLM AI System            │
├─────────────────────────────────────────────┤
│  FastAPI Application                        │
│  ├─ LLM Query Endpoints                     │
│  ├─ RAG Document Retrieval                  │
│  ├─ Citation Generation                     │
│  └─ Metrics Export                          │
└──────────┬────────────────────┬─────────────┘
           │                    │
           ▼                    ▼
    ┌─────────────┐      ┌─────────────┐
    │ LangSmith   │      │ Prometheus  │
    │ (Tracing)   │      │ (Metrics)   │
    └─────────────┘      └──────┬──────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
              ┌─────────┐ ┌─────────┐ ┌──────────┐
              │ Grafana │ │ Alerts  │ │   Node   │
              │         │ │ Manager │ │ Exporter │
              └─────────┘ └─────────┘ └──────────┘
```

## Usage

### Making Queries

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the typical efficiency of modern solar panels?",
    "include_citations": true,
    "temperature": 0.7
  }'
```

Response includes:
- AI-generated answer
- Source citations
- Confidence score
- Hallucination risk score
- LangSmith trace URL
- Query latency

### Monitoring

#### Health Checks
```bash
# Automated health check
./scripts/monitoring/health_check.sh

# Query metrics programmatically
python3 scripts/monitoring/query_metrics.py
```

#### Dashboards

Access the Grafana dashboard at http://localhost:3000 to view:
- Request rates and latency
- Error rates and types
- LLM performance metrics
- Hallucination scores
- System resources
- Active alerts

#### Testing Alerts

Simulate various alert conditions:
```bash
# Test error rate alerts
python3 scripts/monitoring/simulate_alerts.py --scenario error-rate --duration 180

# Test latency alerts
python3 scripts/monitoring/simulate_alerts.py --scenario latency --duration 180

# Test hallucination detection
python3 scripts/monitoring/simulate_alerts.py --scenario hallucination --duration 180
```

## Monitoring & Observability

This project includes a comprehensive monitoring stack:

### Metrics Tracked

**System Metrics:**
- CPU and memory usage
- Request rates and latency
- Error rates and types

**LLM Metrics:**
- Query latency and throughput
- Token usage and costs
- Hallucination detection
- Response confidence scores

**RAG Metrics:**
- Document retrieval latency
- Documents retrieved per query
- Citation generation rate

### Alerting

Automated alerts for:
- **Service Health:** Downtime, high resource usage
- **Performance:** High latency, slow responses
- **LLM Quality:** Hallucinations, low confidence
- **Errors:** Elevated error rates

Alerts are sent via:
- Email (SMTP)
- Slack webhooks
- PagerDuty integration

### LangSmith Integration

Every LLM query is traced in LangSmith:
- Complete call chain visualization
- Input/output inspection
- Performance breakdown
- Cost tracking
- User feedback collection

Access traces at: https://smith.langchain.com

## Documentation

- **[Monitoring Guide](docs/MONITORING.md)** - Complete monitoring documentation
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)

### Runbooks for On-Call Engineers

- [Service Down](docs/runbooks/service-down.md)
- [High Hallucination Score](docs/runbooks/high-hallucination.md)
- [High Error Rate](docs/runbooks/high-error-rate.md)
- [High Latency](docs/runbooks/high-latency.md)

## Development

### Project Structure

```
Solar-PV-LLM-AI/
├── src/
│   ├── api/          # FastAPI application
│   ├── models/       # LLM integration
│   └── utils/        # Utilities (metrics, LangSmith)
├── monitoring/
│   ├── prometheus/   # Prometheus config and alerts
│   ├── grafana/      # Dashboards and provisioning
│   └── alertmanager/ # Alert routing config
├── scripts/
│   └── monitoring/   # Operational scripts
├── docs/
│   └── runbooks/     # On-call runbooks
└── tests/            # Test suite
```

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
uvicorn src.api.main:app --reload --port 8000

# Run tests
pytest tests/
```

### Environment Variables

Key configuration in `.env`:

```bash
# LLM
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4-turbo-preview

# LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=solar-pv-llm-ai

# Alerting
SMTP_HOST=smtp.gmail.com
SMTP_FROM=alerts@yourdomain.com
SMTP_TO=oncall@yourdomain.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

## Testing

### Run Tests
```bash
pytest tests/ -v
```

### Simulate Production Scenarios
```bash
# Load testing
./scripts/load_test.sh

# Alert simulation
python3 scripts/monitoring/simulate_alerts.py --scenario all
```

## Deployment

### Docker Compose (Development)
```bash
docker-compose up -d
```

### Production Considerations

1. **Security:**
   - Use secrets management (Vault, AWS Secrets Manager)
   - Enable TLS/SSL
   - Configure authentication for dashboards
   - Restrict network access

2. **Scalability:**
   - Use orchestration (Kubernetes, Docker Swarm)
   - Implement load balancing
   - Add horizontal scaling
   - Use managed services for databases

3. **Reliability:**
   - Set up redundancy
   - Configure auto-restart
   - Implement circuit breakers
   - Use health checks

4. **Monitoring:**
   - Configure alert notifications
   - Set up on-call rotations
   - Establish SLAs
   - Regular runbook updates

## Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Check logs
docker-compose logs app

# Verify environment variables
docker exec solar-pv-llm-app env | grep -E "OPENAI|LANGCHAIN"

# Rebuild
docker-compose build --no-cache app
docker-compose up -d app
```

**No metrics in Grafana:**
```bash
# Test Prometheus scraping
curl http://localhost:9090/api/v1/targets

# Check app metrics endpoint
curl http://localhost:8000/metrics
```

**Alerts not firing:**
```bash
# Check alert rules
curl http://localhost:9090/api/v1/rules

# Verify AlertManager
docker logs solar-pv-alertmanager
```

See [Troubleshooting Guide](docs/MONITORING.md#troubleshooting) for more details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run test suite
6. Submit a pull request

## License

[Add your license here]

## Support

- **Documentation:** [docs/MONITORING.md](docs/MONITORING.md)
- **Issues:** GitHub Issues
- **Email:** support@yourdomain.com
- **On-call:** PagerDuty escalation

---

**Built with:** FastAPI, LangChain, Prometheus, Grafana, LangSmith
**Last Updated:** 2025-11-18
