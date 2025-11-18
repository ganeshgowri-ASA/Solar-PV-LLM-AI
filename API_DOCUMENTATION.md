# Solar PV LLM AI - API Documentation

## Overview

Comprehensive REST API for Solar PV analysis, defect detection, and AI-powered assistance using RAG (Retrieval Augmented Generation).

**Base URL:** `http://localhost:8000`
**API Documentation:** `http://localhost:8000/docs` (Swagger UI)
**Alternative Docs:** `http://localhost:8000/redoc` (ReDoc)

---

## Authentication

All endpoints (except `/health` and `/docs`) require API key authentication.

### API Key Header
```http
X-API-Key: your-api-key-here
```

### Environment Setup
Configure in `.env` file:
```env
API_KEY=your-api-key-here
SECRET_KEY=your-secret-jwt-key
```

---

## Endpoints

### 1. Health & Monitoring

#### `GET /health`
Health check for all services.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "services": {
    "vector_db": "healthy",
    "llm": "healthy",
    "image_analyzer": "healthy",
    "pv_calculator": "healthy"
  }
}
```

#### `GET /metrics`
Prometheus metrics endpoint for monitoring.

#### `GET /ping`
Simple ping test.

---

### 2. Chat (RAG-Enhanced)

#### `POST /chat/`
AI-powered chat with RAG context retrieval.

**Request:**
```json
{
  "query": "What is the optimal tilt angle for solar panels in California?",
  "use_rag": true,
  "max_tokens": 1000,
  "temperature": 0.7,
  "conversation_history": [
    {
      "role": "user",
      "content": "Tell me about solar panels"
    }
  ]
}
```

**Response:**
```json
{
  "response": "For California (latitude ~37°), the optimal annual tilt angle is approximately 37°...",
  "citations": [
    {
      "source": "Solar Engineering Handbook",
      "page": 42,
      "relevance_score": 0.95,
      "text_snippet": "The optimal tilt angle for fixed solar panels..."
    }
  ],
  "tokens_used": 523,
  "processing_time": 2.34
}
```

---

### 3. PV Calculations

#### `POST /pv/estimate-output`
Estimate solar system energy output.

**Request:**
```json
{
  "panel_capacity_kw": 5.0,
  "panel_efficiency": 0.2,
  "system_losses": 0.14,
  "tilt_angle": 30.0,
  "azimuth_angle": 180.0,
  "location_lat": 37.7749,
  "location_lon": -122.4194
}
```

**Response:**
```json
{
  "daily_energy_kwh": 22.5,
  "monthly_energy_kwh": 685.5,
  "annual_energy_kwh": 8215.6,
  "capacity_factor": 0.187,
  "peak_sun_hours": 5.2
}
```

#### `POST /pv/performance-ratio`
Calculate system performance ratio.

**Query Parameters:**
- `actual_output_kwh` (required)
- `expected_output_kwh` (required)

**Response:**
```json
{
  "actual_output_kwh": 8500.0,
  "expected_output_kwh": 10000.0,
  "performance_ratio": 0.85,
  "efficiency_loss": 15.0
}
```

#### `GET /pv/optimal-tilt/{latitude}`
Get optimal panel tilt angles.

#### `GET /pv/payback-period`
Calculate financial payback period.

**Query Parameters:**
- `system_cost` (required)
- `annual_savings` (required)
- `annual_degradation` (default: 0.005)

#### `GET /pv/peak-sun-hours`
Calculate peak sun hours for location.

---

### 4. Image Analysis

#### `POST /image-analysis/analyze`
Analyze solar panel images for defects.

**Request:**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAA...",
  "analysis_type": "defect_detection"
}
```

**Response:**
```json
{
  "defects": [
    {
      "defect_type": "hotspot",
      "confidence": 0.87,
      "bounding_box": [100, 100, 200, 200],
      "severity": "high",
      "description": "Hotspot detected - potential bypass diode failure"
    }
  ],
  "overall_health_score": 72.5,
  "processing_time": 1.23,
  "image_dimensions": {"width": 1920, "height": 1080},
  "recommendations": [
    "⚠️ HOTSPOT DETECTED: Immediate inspection recommended",
    "Check for shading or cell mismatch"
  ]
}
```

#### `POST /image-analysis/upload-and-analyze`
Upload image file and analyze.

**Form Data:**
- `file`: Image file (JPEG, PNG, TIFF)

#### `GET /image-analysis/supported-defects`
List all detectable defect types.

**Defect Types:**
- Hotspot
- Crack/Micro-crack
- Delamination
- Discoloration
- Soiling
- Snail Trail
- PID (Potential Induced Degradation)
- Bypass Diode Failure

---

### 5. Document Ingestion

#### `POST /documents/ingest`
Ingest document into knowledge base.

**Request:**
```json
{
  "document_base64": "JVBERi0xLjQKJcOkw7zDtsOf...",
  "metadata": {
    "filename": "solar_handbook.pdf",
    "category": "technical"
  }
}
```

**Response:**
```json
{
  "document_id": "doc_a1b2c3d4_e5f6g7h8",
  "status": "completed",
  "chunks_created": 156,
  "processing_time": 8.45
}
```

#### `POST /documents/upload`
Upload document file for ingestion.

**Form Data:**
- `file`: Document file (PDF, DOCX, TXT)

**Supported Formats:**
- PDF (.pdf)
- Word Documents (.docx)
- Plain Text (.txt)

#### `GET /documents/status/{document_id}`
Get document processing status.

**Response:**
```json
{
  "document_id": "doc_a1b2c3d4_e5f6g7h8",
  "status": "processing",
  "progress": 65.0,
  "chunks_processed": 101,
  "total_chunks": 156
}
```

**Status Values:**
- `pending`: Queued for processing
- `processing`: Currently being processed
- `completed`: Successfully ingested
- `failed`: Processing error
- `stopped`: Manually stopped

#### `POST /documents/stop/{document_id}`
Stop ongoing document ingestion.

#### `GET /documents/status`
Get all document ingestion statuses.

#### `GET /documents/collection-stats`
Get vector database statistics.

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `401`: Unauthorized (invalid token)
- `403`: Forbidden (missing/invalid API key)
- `404`: Not Found
- `500`: Internal Server Error
- `501`: Not Implemented

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. For production deployments, consider implementing:
- Per-IP rate limiting
- Per-API-key quotas
- Request throttling for expensive operations

---

## Streaming (Future)

The following endpoints will support streaming in future versions:
- `POST /chat/stream` - Real-time streaming chat responses

---

## Examples

### Python Client Example

```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "your-api-key"

headers = {"X-API-Key": API_KEY}

# Chat example
chat_response = requests.post(
    f"{API_URL}/chat/",
    headers=headers,
    json={
        "query": "How do I calculate solar panel efficiency?",
        "use_rag": True
    }
)
print(chat_response.json()["response"])

# PV calculation example
pv_response = requests.post(
    f"{API_URL}/pv/estimate-output",
    headers=headers,
    json={
        "panel_capacity_kw": 5.0,
        "panel_efficiency": 0.2,
        "system_losses": 0.14,
        "tilt_angle": 37.0,
        "azimuth_angle": 180.0,
        "location_lat": 37.7749,
        "location_lon": -122.4194
    }
)
print(f"Annual Output: {pv_response.json()['annual_energy_kwh']} kWh")
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Chat with RAG
curl -X POST http://localhost:8000/chat/ \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "What causes solar panel hotspots?", "use_rag": true}'

# PV calculation
curl -X POST http://localhost:8000/pv/estimate-output \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "panel_capacity_kw": 5.0,
    "panel_efficiency": 0.2,
    "system_losses": 0.14,
    "tilt_angle": 30.0,
    "azimuth_angle": 180.0,
    "location_lat": 37.7749,
    "location_lon": -122.4194
  }'

# Upload document
curl -X POST http://localhost:8000/documents/upload \
  -H "X-API-Key: your-api-key" \
  -F "file=@solar_manual.pdf"
```

---

## Support & Feedback

For issues, questions, or feature requests, please contact the development team or open an issue in the project repository.
