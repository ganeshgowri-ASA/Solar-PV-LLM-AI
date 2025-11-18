# Solar PV Multi-LLM Orchestrator

An intelligent multi-LLM orchestration system for Solar PV queries that intelligently routes questions between GPT-4o and Claude 3.5 Sonnet based on query type and complexity.

## Features

- **Intelligent Query Classification**: Automatically classifies queries into 5 types:
  - Standard Interpretation
  - Calculation
  - Image Analysis
  - Technical Explanation
  - Code Generation

- **Smart LLM Routing**: Routes queries to the most appropriate LLM based on:
  - Query type and complexity
  - Classification confidence
  - User preferences

- **Fallback & Hybrid Responses**:
  - Automatic fallback to alternative LLM on failure
  - Hybrid responses combining insights from multiple LLMs
  - Intelligent response synthesis

- **Production-Ready API**: FastAPI-based REST API with:
  - Comprehensive documentation (OpenAPI/Swagger)
  - Health checks and monitoring
  - CORS support
  - Structured logging

## Architecture

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Classifier     │ ──► Determines query type
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Router         │ ──► Selects appropriate LLM(s)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Clients    │ ──► GPT-4o / Claude 3.5
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Synthesizer    │ ──► Combines responses
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Final Response │
└─────────────────┘
```

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Configuration

Edit `.env` file:
```env
# API Keys (required)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Model Configuration
GPT_MODEL=gpt-4o
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Orchestrator Configuration
DEFAULT_LLM=auto                    # auto, gpt, or claude
ENABLE_FALLBACK=true               # Enable automatic fallback
ENABLE_HYBRID_SYNTHESIS=true       # Enable hybrid responses
CLASSIFICATION_THRESHOLD=0.7       # Confidence threshold

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### Running the Service

Start the orchestrator service:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

Access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage

### API Endpoints

#### POST `/api/v1/query`
Process a query through the orchestrator.

**Request:**
```json
{
  "query": "Calculate the energy yield for a 10kW solar system in California",
  "query_type": "calculation",
  "max_tokens": 2000,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "response": "Detailed calculation response...",
  "primary_llm": "gpt",
  "query_type": "calculation",
  "classification_confidence": 0.92,
  "is_hybrid": false,
  "fallback_used": false,
  "total_latency_ms": 1234.56
}
```

#### GET `/api/v1/health`
Check service health status.

#### GET `/api/v1/models`
List available models and configuration.

#### GET `/api/v1/query-types`
List supported query types with examples.

### Python Client Example

```python
import httpx
import asyncio

async def query_orchestrator(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/query",
            json={
                "query": query,
                "max_tokens": 2000,
                "temperature": 0.7
            }
        )
        return response.json()

# Example usage
result = asyncio.run(query_orchestrator(
    "How does MPPT tracking work in solar inverters?"
))
print(result["response"])
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Calculate ROI for a 20kW commercial solar installation",
    "query_type": "calculation"
  }'
```

## Query Types

### 1. Standard Interpretation
General questions about solar PV systems.

**Examples:**
- "What is a solar inverter?"
- "Explain how solar panels work"

### 2. Calculation
Numerical calculations and system sizing.

**Examples:**
- "Calculate energy yield for a 10kW system"
- "Size inverter for 20 panels of 400W each"

### 3. Image Analysis
Visual inspection and analysis (requires image data).

**Examples:**
- "Analyze this thermal image of solar panels"
- "Inspect this PV array layout"

### 4. Technical Explanation
Detailed technical explanations.

**Examples:**
- "How does MPPT tracking work?"
- "Explain the physics of the photovoltaic effect"

### 5. Code Generation
Generate code for PV simulations and analysis.

**Examples:**
- "Write Python code to calculate shading losses"
- "Generate a PV system simulation script"

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/orchestrator --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## Project Structure

```
Solar-PV-LLM-AI/
├── src/
│   └── orchestrator/
│       ├── __init__.py
│       ├── config.py              # Configuration management
│       ├── models.py              # Data models
│       ├── service.py             # Main orchestrator service
│       ├── clients/               # LLM API clients
│       │   ├── base.py
│       │   ├── gpt_client.py
│       │   └── claude_client.py
│       ├── classifier/            # Query classification
│       │   └── semantic_classifier.py
│       ├── router/                # LLM routing logic
│       │   └── llm_router.py
│       ├── synthesizer/           # Response synthesis
│       │   └── response_synthesizer.py
│       ├── prompts/               # Prompt templates
│       │   └── templates.py
│       └── api/                   # REST API
│           └── app.py
├── tests/
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── README.md                      # This file
```

## Advanced Features

### Hybrid Responses

Enable hybrid mode to get responses from both LLMs for complex queries:

```json
{
  "query": "Comprehensive analysis of monocrystalline vs polycrystalline panels",
  "preferred_llm": "hybrid"
}
```

### Explicit LLM Selection

Override automatic routing:

```json
{
  "query": "Your question here",
  "preferred_llm": "claude"  // or "gpt"
}
```

### Image Analysis

Include base64-encoded images:

```json
{
  "query": "Analyze defects in this thermal image",
  "image_data": "base64_encoded_image_data_here"
}
```

## Monitoring & Logging

The service uses structured logging with different levels:
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Errors and failures

Logs include:
- Request/response timing
- Classification results
- Routing decisions
- LLM interactions
- Error traces

## Performance

Typical response times:
- Simple queries: 1-3 seconds
- Complex calculations: 2-5 seconds
- Image analysis: 3-7 seconds
- Hybrid responses: 4-8 seconds

## Roadmap

- [ ] RAG integration for Solar PV knowledge base
- [ ] Citation tracking and source attribution
- [ ] Streaming responses
- [ ] Multi-language support
- [ ] Enhanced metrics and analytics
- [ ] Cost optimization and caching

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/issues
- Documentation: See `/docs` endpoint

## Acknowledgments

Built for the Solar PV AI project to provide intelligent, context-aware responses for users ranging from beginners to experts.
