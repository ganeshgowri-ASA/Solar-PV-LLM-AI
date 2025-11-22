# API Reference

Complete API reference for Solar-PV-LLM-AI platform.

## Base URL

```
Production: https://api.your-domain.com
Development: http://localhost:8000
```

## Authentication

All API endpoints (except `/health`, `/ping`, `/docs`, `/redoc`) require authentication via API key.

### API Key Authentication

Include the API key in the request header:

```http
X-API-Key: your-api-key-here
```

### Example Request

```bash
curl -X GET http://localhost:8000/api/v1/query/stats \
  -H "X-API-Key: your-api-key-here"
```

---

## Endpoints Overview

| Category | Base Path | Description |
|----------|-----------|-------------|
| Health | `/health`, `/ping` | System health monitoring |
| Query | `/api/v1/query` | RAG-powered Q&A |
| Feedback | `/api/v1/feedback` | User feedback collection |
| PV Calculations | `/api/v1/pv` | Solar PV calculations |
| Image Analysis | `/api/v1/image-analysis` | Panel defect detection |
| Documents | `/api/v1/documents` | Document ingestion |
| Admin | `/api/v1/admin` | Administration endpoints |

---

## Health & Monitoring

### GET /health

Check system health status.

**Authentication:** Not required

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "services": {
    "database": "healthy",
    "vector_store": "healthy",
    "llm": "healthy",
    "redis": "healthy"
  }
}
```

### GET /ping

Simple ping endpoint.

**Response:**

```json
{
  "message": "pong",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### GET /metrics

Prometheus metrics endpoint.

**Response:** Prometheus text format

---

## Query API

### POST /api/v1/query/

Submit a query and get an AI-generated response with RAG context.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | The user's question |
| `use_rag` | boolean | No | Enable RAG retrieval (default: true) |
| `max_tokens` | integer | No | Maximum response tokens (default: 1000) |
| `temperature` | float | No | LLM temperature 0-1 (default: 0.7) |
| `conversation_history` | array | No | Previous conversation messages |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/v1/query/ \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the optimal tilt angle for solar panels at 40° latitude?",
    "use_rag": true,
    "max_tokens": 1000,
    "temperature": 0.7
  }'
```

**Response:**

```json
{
  "id": "query_abc123",
  "response": "For a location at 40° latitude, the optimal annual tilt angle for fixed solar panels is approximately 35-40°. This angle maximizes year-round energy production by balancing summer and winter sun positions...",
  "citations": [
    {
      "source": "IEC 62446-1:2016",
      "section": "Clause 7.2",
      "page": 42,
      "relevance_score": 0.95,
      "text_snippet": "The optimal tilt angle for fixed-mount solar panels..."
    }
  ],
  "confidence_score": 0.89,
  "tokens_used": 523,
  "processing_time_ms": 2340,
  "llm_provider": "anthropic",
  "model": "claude-3-sonnet"
}
```

### GET /api/v1/query/{query_id}

Retrieve details of a specific query.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query_id` | string | Query identifier |

**Response:**

```json
{
  "id": "query_abc123",
  "query_text": "What is the optimal tilt angle?",
  "response_text": "For a location at 40° latitude...",
  "created_at": "2025-01-15T10:30:00Z",
  "user_id": "user_xyz",
  "session_id": "session_789"
}
```

### POST /api/v1/query/search

Search the knowledge base directly without LLM generation.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `top_k` | integer | No | Number of results (default: 10) |
| `filters` | object | No | Metadata filters |

**Response:**

```json
{
  "results": [
    {
      "document_id": "doc_abc123",
      "chunk_id": "chunk_456",
      "text": "The optimal tilt angle for solar panels...",
      "score": 0.95,
      "metadata": {
        "source": "IEC 62446-1",
        "page": 42
      }
    }
  ],
  "total_results": 156,
  "processing_time_ms": 45
}
```

### GET /api/v1/query/session/{session_id}

Get conversation history for a session.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | string | Session identifier |

---

## Feedback API

### POST /api/v1/feedback/

Create feedback for a query response.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query_id` | string | Yes | Associated query ID |
| `rating` | integer | Yes | Rating 1-5 |
| `helpfulness` | integer | No | Helpfulness 1-5 |
| `accuracy` | integer | No | Accuracy 1-5 |
| `completeness` | integer | No | Completeness 1-5 |
| `comment` | string | No | Optional comment |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/v1/feedback/ \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "query_abc123",
    "rating": 4,
    "helpfulness": 5,
    "accuracy": 4,
    "completeness": 4,
    "comment": "Very helpful response with good citations"
  }'
```

**Response:**

```json
{
  "id": "feedback_xyz789",
  "query_id": "query_abc123",
  "rating": 4,
  "created_at": "2025-01-15T10:35:00Z"
}
```

### GET /api/v1/feedback/{feedback_id}

Get feedback details.

### PUT /api/v1/feedback/{feedback_id}

Update feedback review status.

**Request Body:**

```json
{
  "review_status": "approved"
}
```

### GET /api/v1/feedback/stats/summary

Get feedback statistics.

**Response:**

```json
{
  "total_feedbacks": 1523,
  "average_rating": 4.2,
  "rating_distribution": {
    "1": 23,
    "2": 45,
    "3": 156,
    "4": 678,
    "5": 621
  },
  "average_helpfulness": 4.1,
  "average_accuracy": 4.3,
  "positive_feedback_rate": 0.85
}
```

### GET /api/v1/feedback/analysis/trends

Get feedback trend analysis.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `days` | integer | Number of days to analyze (default: 30) |

---

## PV Calculations API

### POST /api/v1/pv/estimate-output

Estimate solar system energy output.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `panel_capacity_kw` | float | Yes | System capacity in kW |
| `panel_efficiency` | float | Yes | Panel efficiency (0-1) |
| `system_losses` | float | No | System losses (default: 0.14) |
| `tilt_angle` | float | Yes | Panel tilt angle in degrees |
| `azimuth_angle` | float | Yes | Azimuth angle (180 = south) |
| `location_lat` | float | Yes | Latitude |
| `location_lon` | float | Yes | Longitude |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/v1/pv/estimate-output \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "panel_capacity_kw": 5.0,
    "panel_efficiency": 0.20,
    "system_losses": 0.14,
    "tilt_angle": 35.0,
    "azimuth_angle": 180.0,
    "location_lat": 37.7749,
    "location_lon": -122.4194
  }'
```

**Response:**

```json
{
  "daily_energy_kwh": 22.5,
  "monthly_energy_kwh": 685.5,
  "annual_energy_kwh": 8215.6,
  "capacity_factor": 0.187,
  "peak_sun_hours": 5.2,
  "specific_yield_kwh_kwp": 1643.1
}
```

### GET /api/v1/pv/optimal-tilt/{latitude}

Get optimal tilt angles for a latitude.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `latitude` | float | Location latitude |

**Response:**

```json
{
  "latitude": 37.77,
  "optimal_annual_tilt": 35.0,
  "optimal_summer_tilt": 20.0,
  "optimal_winter_tilt": 55.0,
  "seasonal_adjustment_recommended": true
}
```

### GET /api/v1/pv/payback-period

Calculate financial payback period.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `system_cost` | float | Yes | Total system cost ($) |
| `annual_savings` | float | Yes | Annual electricity savings ($) |
| `annual_degradation` | float | No | Annual degradation rate (default: 0.005) |
| `electricity_rate_increase` | float | No | Annual rate increase (default: 0.03) |

**Response:**

```json
{
  "simple_payback_years": 7.5,
  "discounted_payback_years": 8.2,
  "roi_25_years": 2.45,
  "net_present_value": 15420.50,
  "internal_rate_of_return": 0.12
}
```

### GET /api/v1/pv/peak-sun-hours

Get peak sun hours for a location.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `latitude` | float | Yes | Location latitude |
| `longitude` | float | Yes | Location longitude |
| `tilt_angle` | float | No | Panel tilt angle |

---

## Image Analysis API

### POST /api/v1/image-analysis/analyze

Analyze a solar panel image for defects.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image_base64` | string | Yes | Base64-encoded image |
| `analysis_type` | string | No | Analysis type (default: defect_detection) |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/v1/image-analysis/analyze \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAA...",
    "analysis_type": "defect_detection"
  }'
```

**Response:**

```json
{
  "analysis_id": "analysis_abc123",
  "defects": [
    {
      "defect_type": "hotspot",
      "confidence": 0.87,
      "bounding_box": [100, 100, 200, 200],
      "severity": "high",
      "description": "Hotspot detected in upper-left quadrant"
    },
    {
      "defect_type": "soiling",
      "confidence": 0.72,
      "bounding_box": [300, 400, 500, 600],
      "severity": "low",
      "description": "Light dust accumulation detected"
    }
  ],
  "overall_health_score": 72.5,
  "recommendations": [
    "URGENT: Inspect hotspot area for bypass diode failure",
    "Schedule cleaning to address soiling"
  ],
  "processing_time_ms": 1230,
  "image_dimensions": {
    "width": 1920,
    "height": 1080
  }
}
```

### POST /api/v1/image-analysis/upload-and-analyze

Upload an image file and analyze it.

**Form Data:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | Image file (JPEG, PNG, TIFF) |

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/v1/image-analysis/upload-and-analyze \
  -H "X-API-Key: your-api-key" \
  -F "file=@solar_panel.jpg"
```

### GET /api/v1/image-analysis/supported-defects

List all supported defect types.

**Response:**

```json
{
  "defect_types": [
    {
      "type": "hotspot",
      "description": "Localized high-temperature area",
      "severity_levels": ["low", "medium", "high"]
    },
    {
      "type": "crack",
      "description": "Visible crack or micro-crack in cell",
      "severity_levels": ["low", "medium", "high"]
    },
    {
      "type": "delamination",
      "description": "Separation of encapsulant layers",
      "severity_levels": ["low", "medium", "high"]
    },
    {
      "type": "discoloration",
      "description": "Yellowing or browning of cells/encapsulant",
      "severity_levels": ["low", "medium", "high"]
    },
    {
      "type": "soiling",
      "description": "Dust, dirt, or debris accumulation",
      "severity_levels": ["low", "medium", "high"]
    },
    {
      "type": "snail_trail",
      "description": "Discoloration pattern from silver migration",
      "severity_levels": ["low", "medium", "high"]
    },
    {
      "type": "pid",
      "description": "Potential Induced Degradation",
      "severity_levels": ["low", "medium", "high"]
    },
    {
      "type": "bypass_diode_failure",
      "description": "Failed bypass diode causing hotspot",
      "severity_levels": ["high"]
    }
  ]
}
```

---

## Documents API

### POST /api/v1/documents/ingest

Ingest a document into the knowledge base.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_base64` | string | Yes | Base64-encoded document |
| `filename` | string | Yes | Original filename |
| `metadata` | object | No | Additional metadata |

**Response:**

```json
{
  "document_id": "doc_abc123",
  "status": "processing",
  "message": "Document queued for processing"
}
```

### POST /api/v1/documents/upload

Upload a document file for ingestion.

**Form Data:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | Document file (PDF, DOCX, TXT) |

### GET /api/v1/documents/status/{document_id}

Get document processing status.

**Response:**

```json
{
  "document_id": "doc_abc123",
  "status": "processing",
  "progress": 65.0,
  "chunks_processed": 101,
  "total_chunks": 156,
  "started_at": "2025-01-15T10:30:00Z"
}
```

**Status Values:**

| Status | Description |
|--------|-------------|
| `pending` | Queued for processing |
| `processing` | Currently being processed |
| `completed` | Successfully ingested |
| `failed` | Processing error |
| `stopped` | Manually stopped |

### GET /api/v1/documents/collection-stats

Get vector store collection statistics.

**Response:**

```json
{
  "total_documents": 156,
  "total_chunks": 12453,
  "total_tokens": 2456789,
  "storage_size_mb": 125.5,
  "last_updated": "2025-01-15T10:30:00Z"
}
```

---

## Admin API

### GET /api/v1/admin/dashboard/metrics

Get comprehensive dashboard metrics.

**Response:**

```json
{
  "queries": {
    "total": 15234,
    "today": 234,
    "this_week": 1523
  },
  "feedback": {
    "total": 8234,
    "average_rating": 4.2,
    "pending_review": 156
  },
  "system": {
    "uptime_hours": 720,
    "cpu_usage": 45.2,
    "memory_usage": 62.5
  },
  "models": {
    "active_deployment": "deployment_v1.2.3",
    "last_training": "2025-01-10T08:00:00Z"
  }
}
```

### GET /api/v1/admin/retraining/recommendation

Get retraining recommendation based on feedback.

**Response:**

```json
{
  "recommendation": "retraining_recommended",
  "reasons": [
    "Average rating below threshold (3.8 < 4.0)",
    "156 negative feedback items since last training"
  ],
  "metrics": {
    "feedback_count": 523,
    "average_rating": 3.8,
    "negative_feedback_rate": 0.18
  }
}
```

### POST /api/v1/admin/retraining/trigger

Manually trigger model retraining.

**Request Body:**

```json
{
  "reason": "Manual trigger for quality improvement"
}
```

---

## Error Responses

All endpoints return standard HTTP status codes with error details.

### Error Format

```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request - Invalid parameters |
| `401` | Unauthorized - Invalid or missing token |
| `403` | Forbidden - Invalid API key |
| `404` | Not Found |
| `422` | Validation Error |
| `429` | Too Many Requests |
| `500` | Internal Server Error |
| `503` | Service Unavailable |

---

## Rate Limiting

| Endpoint Category | Rate Limit |
|-------------------|------------|
| Health endpoints | Unlimited |
| Query endpoints | 60 requests/minute |
| Image analysis | 10 requests/minute |
| Document ingestion | 5 requests/minute |
| Admin endpoints | 30 requests/minute |

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705315800
```

---

## SDKs & Client Libraries

### Python SDK

```python
from solar_pv_client import SolarPVClient

client = SolarPVClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Query
response = client.query("What causes hotspots in solar panels?")
print(response.text)
print(response.citations)

# Image analysis
result = client.analyze_image("panel.jpg")
print(result.health_score)
print(result.defects)

# PV calculation
output = client.estimate_output(
    capacity_kw=5.0,
    efficiency=0.20,
    latitude=37.77,
    longitude=-122.41
)
print(f"Annual output: {output.annual_energy_kwh} kWh")
```

### JavaScript/TypeScript SDK

```typescript
import { SolarPVClient } from 'solar-pv-client';

const client = new SolarPVClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Query
const response = await client.query({
  query: 'What causes hotspots?',
  useRag: true
});

// Image analysis
const analysis = await client.analyzeImage(imageFile);
console.log(analysis.healthScore);
```

---

## Webhooks (Coming Soon)

Configure webhooks to receive notifications for:

- Document processing completion
- Model training completion
- System alerts

---

## OpenAPI Specification

The full OpenAPI 3.0 specification is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **JSON**: `http://localhost:8000/openapi.json`

---

## Support

For API support:

- **Documentation**: https://docs.solar-pv-llm-ai.com
- **Issues**: https://github.com/your-org/Solar-PV-LLM-AI/issues
- **Email**: api-support@your-domain.com
