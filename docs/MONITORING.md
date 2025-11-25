# Solar PV LLM AI - Monitoring, Logging, and Alerting

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Components](#components)
5. [Metrics](#metrics)
6. [Dashboards](#dashboards)
7. [Alerts](#alerts)
8. [LangSmith Integration](#langsmith-integration)
9. [Monitoring Scripts](#monitoring-scripts)
10. [Runbooks](#runbooks)
11. [Testing](#testing)
12. [Troubleshooting](#troubleshooting)

## Overview

This monitoring infrastructure provides comprehensive observability for the Solar PV LLM AI system, including:

- **Real-time Metrics:** Prometheus-based metrics collection
- **Visualization:** Grafana dashboards for system health
- **Alerting:** Automated alerts for anomalies and issues
- **LLM Tracing:** LangSmith integration for query tracking
- **Hallucination Detection:** Automated quality monitoring
- **Operational Tools:** Scripts and runbooks for on-call engineers

## Architecture

```
┌─────────────┐
│   Users     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│   Solar PV LLM AI Application   │
│   - FastAPI                     │
│   - LLM Integration             │
│   - RAG System                  │
│   - Prometheus Exporter         │
└────┬──────────────────┬─────────┘
     │                  │
     │                  ▼
     │         ┌─────────────────┐
     │         │   LangSmith     │
     │         │   (LLM Traces)  │
     │         └─────────────────┘
     │
     ▼
┌─────────────────┐
│   Prometheus    │
│  (Metrics DB)   │
└────┬──────┬─────┘
     │      │
     │      └──────────────┐
     │                     │
     ▼                     ▼
┌──────────┐      ┌────────────────┐
│ Grafana  │      │ AlertManager   │
│(Dashboards)│      │(Notifications) │
└──────────┘      └────────┬───────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Notifications  │
                  │  - Email        │
                  │  - Slack        │
                  │  - PagerDuty    │
                  └─────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- API keys (OpenAI, LangSmith)

### 1. Setup Environment

```bash
# Clone the repository
cd Solar-PV-LLM-AI

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Required environment variables:
```bash
# LLM Configuration
OPENAI_API_KEY=sk-your-key-here

# LangSmith (for tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=solar-pv-llm-ai

# Alert Configuration
SMTP_HOST=smtp.gmail.com
SMTP_FROM=alerts@yourdomain.com
SMTP_TO=oncall@yourdomain.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Verify Installation

```bash
# Run health check
./scripts/monitoring/health_check.sh

# Check metrics
python3 scripts/monitoring/query_metrics.py
```

### 4. Access Dashboards

- **Application API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin123)
- **AlertManager:** http://localhost:9093

## Components

### Application (Port 8000)

The main FastAPI application with:
- LLM query endpoints
- Prometheus metrics exporter (`/metrics`)
- Health check endpoint (`/health`)
- LangSmith tracing integration

### Prometheus (Port 9090)

Metrics collection and storage:
- Scrapes application metrics every 15 seconds
- Evaluates alerting rules
- 30-day retention period
- Configuration: `monitoring/prometheus/prometheus.yml`

### Grafana (Port 3000)

Visualization and dashboards:
- Pre-configured dashboards
- Real-time metric visualization
- Alert visualization
- Configuration: `monitoring/grafana/`

### AlertManager (Port 9093)

Alert routing and notifications:
- Email notifications
- Slack integration
- PagerDuty integration
- Alert grouping and deduplication
- Configuration: `monitoring/alertmanager/alertmanager.yml`

### Node Exporter (Port 9100)

System-level metrics:
- CPU usage
- Memory usage
- Disk I/O
- Network statistics

## Metrics

### HTTP Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method and endpoint |
| `http_request_duration_seconds` | Histogram | Request latency in seconds |
| `errors_total` | Counter | Total errors by type and endpoint |

### LLM Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `llm_queries_total` | Counter | Total LLM queries processed |
| `llm_query_duration_seconds` | Histogram | LLM query latency |
| `llm_tokens_total` | Counter | Total tokens consumed |
| `llm_hallucination_score` | Gauge | Current hallucination risk (0-1) |
| `llm_hallucinations_detected_total` | Counter | Detected hallucinations |
| `llm_response_confidence` | Histogram | Response confidence scores |

### RAG Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `rag_retrievals_total` | Counter | Total document retrievals |
| `rag_retrieval_duration_seconds` | Histogram | Retrieval latency |
| `rag_documents_retrieved` | Histogram | Documents per query |
| `citations_generated_total` | Counter | Total citations generated |

### Querying Metrics

Using Prometheus Query Language (PromQL):

```bash
# Request rate
rate(http_requests_total[5m])

# Error percentage
rate(errors_total[5m]) / rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Hallucination rate
rate(llm_hallucinations_detected_total[10m])
```

## Dashboards

### Main Dashboard: "Solar PV LLM AI - System Overview"

Located at: http://localhost:3000/d/solar-pv-llm-overview

Panels:
1. **Service Status** - Application health
2. **Request Rate** - Requests per second by method
3. **Error Rate** - Current error percentage
4. **API P95 Latency** - 95th percentile API response time
5. **API Latency Percentiles** - P50, P95, P99 trends
6. **LLM Query Latency** - LLM-specific latency metrics
7. **Hallucination Score** - Current hallucination risk
8. **LLM Quality Metrics** - Confidence and hallucination trends
9. **Error Distribution** - Breakdown by error type
10. **LLM Operations Rate** - Query, RAG, and citation rates
11. **Token Usage** - LLM token consumption
12. **System Resources** - CPU and memory usage
13. **Active Alerts** - Currently firing alerts

### Creating Custom Dashboards

1. Access Grafana: http://localhost:3000
2. Login with admin/admin123
3. Click "+" → "Dashboard"
4. Add panels with PromQL queries
5. Save dashboard to `/var/lib/grafana/dashboards/`

## Alerts

### Alert Severities

- **Critical:** Immediate action required, service impact
- **Warning:** Attention needed, potential issues
- **Info:** Informational, monitoring trends

### Configured Alerts

#### Service Health

| Alert | Severity | Threshold | Description |
|-------|----------|-----------|-------------|
| ServiceDown | Critical | Service unavailable for 1min | Application not responding |
| HighMemoryUsage | Warning | >85% for 5min | Memory pressure |
| HighCPUUsage | Warning | >80% for 5min | CPU saturation |

#### LLM Performance

| Alert | Severity | Threshold | Description |
|-------|----------|-----------|-------------|
| HighLLMLatency | Warning | P95 >5s for 3min | Slow LLM responses |
| CriticalLLMLatency | Critical | P95 >10s for 2min | Very slow LLM responses |
| HighTokenUsage | Warning | >10K tokens/sec for 5min | Excessive token consumption |

#### LLM Quality

| Alert | Severity | Threshold | Description |
|-------|----------|-----------|-------------|
| HighHallucinationScore | Warning | Score >0.5 for 2min | High hallucination risk |
| FrequentHallucinations | Critical | >0.1/sec for 5min | Repeated hallucinations |
| LowConfidenceResponses | Warning | P50 confidence <0.3 for 5min | Low confidence answers |

#### Error Rates

| Alert | Severity | Threshold | Description |
|-------|----------|-----------|-------------|
| HighErrorRate | Warning | >0.05/sec for 3min | Elevated error rate |
| CriticalErrorRate | Critical | >0.2/sec for 1min | Very high error rate |

### Alert Configuration

Alerts are defined in: `monitoring/prometheus/alerts.yml`

Example alert:
```yaml
- alert: HighHallucinationScore
  expr: llm_hallucination_score > 0.5
  for: 2m
  labels:
    severity: warning
    component: llm_quality
  annotations:
    summary: "High hallucination risk detected"
    description: "Hallucination score is {{ $value }}"
    runbook_url: "https://docs.company.com/runbooks/high-hallucination"
```

### Alert Routing

AlertManager routes alerts based on:
- **Severity:** Critical alerts go to all channels
- **Component:** Alerts routed to appropriate teams
- **Time:** Different routing for business hours vs. off-hours

Configuration: `monitoring/alertmanager/alertmanager.yml`

### Notification Channels

1. **Email:**
   - Configured via SMTP
   - HTML formatted alerts
   - Includes runbook links

2. **Slack:**
   - Real-time notifications
   - Separate channels by severity
   - Rich formatting

3. **PagerDuty:**
   - For critical alerts
   - Incident creation
   - On-call escalation

## LangSmith Integration

LangSmith provides LLM-specific tracing and monitoring.

### Setup

1. Sign up at: https://smith.langchain.com
2. Create project: "solar-pv-llm-ai"
3. Get API key
4. Configure in `.env`:
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-key-here
LANGCHAIN_PROJECT=solar-pv-llm-ai
```

### Features

- **Trace Visualization:** See complete LLM call chains
- **Performance Metrics:** Track latency per component
- **Cost Tracking:** Monitor token usage and costs
- **Debugging:** Inspect inputs, outputs, and errors
- **Feedback Collection:** User ratings and comments

### Accessing Traces

1. Go to: https://smith.langchain.com
2. Select project: "solar-pv-llm-ai"
3. View traces, filter, and analyze

Each API response includes a `trace_url` field linking to the LangSmith trace.

## Monitoring Scripts

### Health Check Script

```bash
./scripts/monitoring/health_check.sh
```

Checks:
- Application health
- Prometheus status
- Grafana availability
- AlertManager status
- Active alerts
- Key metrics (error rate, hallucination score, latency)

Exit codes:
- 0: All healthy
- 1: Issues found

### Metrics Query Script

```bash
python3 scripts/monitoring/query_metrics.py
```

Displays:
- System health
- Request metrics
- Latency percentiles
- LLM quality metrics
- System resources
- Active alerts

### Alert Simulation Script

```bash
# Simulate high error rate
python3 scripts/monitoring/simulate_alerts.py --scenario error-rate --duration 180

# Simulate high latency
python3 scripts/monitoring/simulate_alerts.py --scenario latency --duration 180

# Simulate hallucinations
python3 scripts/monitoring/simulate_alerts.py --scenario hallucination --duration 180

# Check current alerts
python3 scripts/monitoring/simulate_alerts.py --scenario check
```

## Runbooks

Detailed runbooks for on-call engineers:

- [Service Down](./runbooks/service-down.md) - Application not responding
- [High Hallucination Score](./runbooks/high-hallucination.md) - LLM quality issues
- [High Error Rate](./runbooks/high-error-rate.md) - Elevated errors
- [High Latency](./runbooks/high-latency.md) - Performance degradation

Each runbook includes:
- Alert description and impact
- Triage steps
- Common causes and solutions
- Verification procedures
- Escalation paths
- Prevention strategies

## Testing

### 1. Test Application

```bash
# Health check
curl http://localhost:8000/health

# Test query endpoint
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the efficiency of solar panels?",
    "include_citations": true
  }'
```

### 2. Verify Metrics

```bash
# Check metrics endpoint
curl http://localhost:8000/metrics | grep llm_queries_total

# Query Prometheus
curl "http://localhost:9090/api/v1/query?query=up"
```

### 3. Test Alerts

```bash
# Simulate alerts
python3 scripts/monitoring/simulate_alerts.py --scenario error-rate --duration 180

# Check AlertManager
curl http://localhost:9093/api/v1/alerts

# View in Prometheus
# Go to: http://localhost:9090/alerts
```

### 4. Verify Dashboards

1. Access Grafana: http://localhost:3000
2. Login: admin/admin123
3. Open "Solar PV LLM AI - System Overview"
4. Verify all panels are displaying data
5. Check for any errors

### 5. Test Notifications

1. Trigger an alert (using simulation script)
2. Wait for alert to fire (check thresholds)
3. Verify notification received via:
   - Email inbox
   - Slack channel
   - PagerDuty incident

## Troubleshooting

### No Metrics in Grafana

```bash
# Check Prometheus is scraping
curl http://localhost:9090/api/v1/targets

# Check application metrics endpoint
curl http://localhost:8000/metrics

# Verify Grafana datasource
# Grafana → Configuration → Data Sources → Prometheus
# Click "Test" button
```

### Alerts Not Firing

```bash
# Check alert rules are loaded
curl http://localhost:9090/api/v1/rules

# Check alert evaluation
curl http://localhost:9090/api/v1/alerts

# Verify AlertManager config
docker logs solar-pv-alertmanager

# Test alert manually
curl -X POST http://localhost:9093/api/v1/alerts \
  -d '[{"labels":{"alertname":"test"}}]'
```

### LangSmith Not Working

```bash
# Check API key
docker exec solar-pv-llm-app env | grep LANGCHAIN

# Test connectivity
curl -H "x-api-key: $LANGCHAIN_API_KEY" \
  https://api.smith.langchain.com/api/v1/projects

# Check application logs
docker logs solar-pv-llm-app | grep langsmith
```

### High Resource Usage

```bash
# Check container stats
docker stats

# Check Prometheus storage
du -sh monitoring/prometheus/data/

# Reduce retention if needed
# Edit monitoring/prometheus/prometheus.yml
# Change --storage.tsdb.retention.time=30d to 7d
```

### Docker Issues

```bash
# Restart all services
docker-compose restart

# Rebuild if needed
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Best Practices

1. **Regular Monitoring:**
   - Check dashboards daily
   - Review metrics trends weekly
   - Update alerts based on patterns

2. **Alert Tuning:**
   - Adjust thresholds to reduce false positives
   - Add context to alert descriptions
   - Keep runbooks updated

3. **Performance:**
   - Set up performance baselines
   - Monitor trends over time
   - Plan capacity proactively

4. **Security:**
   - Rotate API keys regularly
   - Use secrets management
   - Restrict dashboard access
   - Enable TLS for production

5. **Documentation:**
   - Keep runbooks current
   - Document changes
   - Share knowledge with team
   - Conduct post-mortems

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [FastAPI Monitoring](https://fastapi.tiangolo.com/advanced/monitoring/)

## Support

For issues or questions:
- **Email:** support@yourdomain.com
- **Slack:** #monitoring-support
- **On-call:** Use PagerDuty escalation

---

Last Updated: 2025-11-18
Version: 1.0.0
