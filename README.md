# Solar PV Multi-Agent AI System

An intelligent multi-agent system for Solar Photovoltaic (PV) expertise, powered by Large Language Models (LLMs). The system provides specialized knowledge through collaborative agents, intelligent routing, and task-based query handling.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Specialized Agents**: Domain experts in IEC standards, testing, and performance analysis
- **Intelligent Routing**: Automatic query classification and agent selection
- **Multi-Agent Collaboration**: Agents work together on complex queries
- **Task Decomposition**: Complex queries broken into manageable subtasks
- **Fallback Mechanisms**: Robust error handling and graceful degradation
- **Flexible Configuration**: Customizable models, parameters, and behavior
- **Comprehensive Testing**: Unit, integration, and end-to-end tests
- **Production Ready**: Async support, logging, monitoring, and error handling

## Architecture

The system uses a hierarchical multi-agent architecture:

```
User Query → Supervisor → Router → Orchestrator → Specialized Agents
                    ↓
              Synthesizer → Final Response
```

### Specialized Agents

1. **IEC Standards Expert**: IEC 61215, 61730, 62446, 61727, 60364-7-712
2. **Testing Specialist**: Module testing, commissioning, diagnostics, quality assurance
3. **Performance Analyst**: Performance metrics, optimization, loss analysis, degradation

## Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key or Anthropic API key

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

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Basic Usage

```python
import asyncio
from src.api import SolarPVMultiAgent

async def main():
    # Initialize the system
    agent_system = SolarPVMultiAgent()

    # Query the system
    result = await agent_system.query(
        "What are the IEC 61215 requirements for PV module testing?"
    )

    print(result['response'])
    print(f"Agents used: {result['agents_used']}")
    print(f"Execution time: {result['execution_time']:.2f}s")

asyncio.run(main())
```

See `examples/` for more usage examples.

## Project Structure

```
Solar-PV-LLM-AI/
├── src/
│   ├── core/               # Core protocols and base classes
│   │   ├── protocols.py    # Agent protocols and message formats
│   │   ├── base_agent.py   # Base agent implementation
│   │   └── config.py       # Configuration classes
│   ├── agents/             # Specialized agents
│   │   ├── iec_standards_agent.py
│   │   ├── testing_specialist_agent.py
│   │   └── performance_analyst_agent.py
│   ├── supervisor/         # Supervisor and orchestration
│   │   ├── supervisor_agent.py
│   │   ├── router.py       # Intelligent routing
│   │   └── orchestrator.py # Multi-agent coordination
│   ├── utils/              # Utilities
│   └── api.py              # Main API
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── examples/               # Usage examples
├── docs/                   # Documentation
└── requirements.txt        # Dependencies
```

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - System design and components
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Examples](examples/) - Usage examples and tutorials

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
```

## Configuration

Configure the system via environment variables in `.env`:

```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Model Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo-preview
SUPERVISOR_MODEL=gpt-4-turbo-preview
AGENT_TEMPERATURE=0.7

# System Configuration
MAX_ITERATIONS=5
LOG_LEVEL=INFO
```

## Advanced Features

### Task Decomposition

The system automatically decomposes complex queries:

```python
result = await agent_system.query(
    "What IEC standards apply to performance testing, "
    "and what are the specific test procedures?"
)
# Automatically routes to both IEC and Testing agents
```

### Direct Agent Access

Query specific agents directly:

```python
result = await agent_system.query_specific_agent(
    agent_type="iec_standards_expert",
    question="What is IEC 61730?"
)
```

### Custom Configuration

```python
from src.core.config import SystemConfig

config = SystemConfig(
    default_model="gpt-4-turbo-preview",
    agent_temperature=0.5,
    max_iterations=3
)

agent_system = SolarPVMultiAgent(system_config=config)
```

## Extending the System

### Adding New Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement required methods and properties
3. Define capabilities and keywords
4. Register in `SupervisorAgent`

Example:

```python
from src.core.base_agent import BaseAgent
from src.core.protocols import AgentCapability, TaskType

class MyCustomAgent(BaseAgent):
    @property
    def capabilities(self) -> AgentCapability:
        return AgentCapability(
            task_types=[TaskType.GENERAL],
            keywords=["custom", "specific"],
            description="My custom agent",
            priority=1
        )

    def _get_system_prompt(self) -> str:
        return "You are an expert in..."
```

## Roadmap

- [x] Multi-agent system architecture
- [x] Specialized agents (IEC, Testing, Performance)
- [x] Intelligent routing and orchestration
- [x] Task decomposition
- [x] Comprehensive testing
- [ ] RAG integration for knowledge retrieval
- [ ] Citation and source tracking
- [ ] Incremental learning capabilities
- [ ] Web interface
- [ ] Deployment automation

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

Built for broad audiences from beginners to experts in Solar PV systems.

## Contact

For questions or support, please open an issue on GitHub.
