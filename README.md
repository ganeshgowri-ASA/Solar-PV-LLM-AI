# Solar-PV-LLM-AI

AI-powered Solar PV Assistant with FastAPI backend and Streamlit frontend. Built for broad audiences from beginners to experts with RAG-based responses and citations.

## Features

- **AI Chat Assistant**: Ask questions about solar PV systems with expertise-level tailored responses
- **Standards Search**: Search through solar PV standards (IEC, NEC, IEEE, UL)
- **Solar Calculator**: Calculate system size, energy output, ROI, payback period, and more
- **Image Analysis**: Analyze solar panel images for defects, shading, and layout issues
- **Real-time Streaming**: WebSocket support for streaming chat responses
- **Citations**: RAG-based responses with source citations

## Architecture

```
Solar-PV-LLM-AI/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Main application entry
│   ├── routers/               # API route handlers
│   │   ├── chat.py           # Chat endpoints + WebSocket
│   │   ├── search.py         # Standards search
│   │   ├── calculator.py     # Solar calculations
│   │   └── image.py          # Image analysis
│   ├── models/               # Pydantic schemas
│   │   └── schemas.py        # Request/Response models
│   └── services/             # Business logic
│       ├── llm_service.py    # LLM integration
│       └── rag_service.py    # RAG for standards search
├── frontend/                  # Streamlit Frontend
│   ├── streamlit_app.py      # Main Streamlit app
│   ├── api_client.py         # API client with retries
│   └── pages/                # Multi-page app pages
│       ├── 1_Chat_Assistant.py
│       ├── 2_Standards_Search.py
│       ├── 3_Calculator.py
│       └── 4_Image_Analysis.py
└── requirements.txt          # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Backend

```bash
# From project root
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Start Frontend

```bash
# From project root
cd frontend
streamlit run streamlit_app.py
```

The frontend will be available at http://localhost:8501

## API Endpoints

### Chat
- `POST /chat/query` - Send a chat query
- `POST /chat/query/stream` - Stream chat response
- `WebSocket /chat/ws/{conversation_id}` - Real-time chat

### Search
- `POST /search/standards` - Search solar PV standards
- `GET /search/categories` - Get available categories

### Calculator
- `POST /calculate` - Perform solar calculations
- `GET /calculate/types` - Get calculation types

### Image Analysis
- `POST /analyze/image` - Analyze solar panel image
- `GET /analyze/types` - Get analysis types

### Health
- `GET /health` - System health check

## API Client Features

The frontend API client (`frontend/api_client.py`) includes:

- **Automatic Retries**: Exponential backoff for failed requests
- **Connection Pooling**: Efficient HTTP connection management
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **WebSocket Support**: Real-time streaming for chat
- **Type Safety**: Full type hints and dataclasses

### Usage Example

```python
from api_client import get_client, ExpertiseLevel, CalculationType

client = get_client()

# Chat query
response = client.chat_query(
    query="How do I size a solar system?",
    expertise_level=ExpertiseLevel.INTERMEDIATE
)

# Search standards
results = client.search_standards(
    query="safety requirements",
    categories=["Safety"],
    max_results=10
)

# Calculate system size
calc = client.calculate(
    calculation_type=CalculationType.SYSTEM_SIZE,
    parameters={"annual_kwh": 10000, "peak_sun_hours": 5}
)

# Streaming chat
for token in client.chat_stream("Tell me about solar panels"):
    print(token, end="", flush=True)
```

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `OPENAI_API_KEY` | OpenAI API key (for production LLM) | - |
| `LLM_MODEL` | LLM model to use | `gpt-3.5-turbo` |

## Calculator Types

| Type | Description |
|------|-------------|
| `system_size` | Calculate required system size based on energy needs |
| `energy_output` | Calculate expected energy output from a system |
| `roi` | Calculate return on investment over system lifetime |
| `payback_period` | Calculate simple payback period |
| `panel_count` | Calculate number of panels needed |
| `inverter_size` | Calculate recommended inverter size |
| `battery_size` | Calculate battery storage requirements |

## Standards Database

The system includes knowledge of major solar PV standards:

- **IEC 61724**: Performance monitoring
- **IEC 61730**: Module safety
- **IEC 62446**: Testing and documentation
- **NEC Article 690**: US electrical code
- **IEEE 1547**: Grid interconnection
- **UL 1703**: Safety certification

## Development

### Running Tests

```bash
# Backend tests
pytest backend/tests/

# Frontend tests
pytest frontend/tests/
```

### Code Style

```bash
# Format code
black backend/ frontend/

# Type checking
mypy backend/ frontend/
```

## License

MIT License - See LICENSE file for details.
