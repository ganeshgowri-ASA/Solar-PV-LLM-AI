# Quick Start Guide

Get up and running with the Solar PV Multi-Agent System in minutes!

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- OpenAI API key (or Anthropic API key)

## Step 1: Installation

### Clone the Repository

```bash
git clone https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI.git
cd Solar-PV-LLM-AI
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configuration

### Set Up Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API key:
```bash
# Required: Add your API key
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional: Configure other settings
DEFAULT_MODEL=gpt-4-turbo-preview
AGENT_TEMPERATURE=0.7
LOG_LEVEL=INFO
```

### Verify Installation

Create a test script `test_setup.py`:

```python
import asyncio
from src.api import SolarPVMultiAgent

async def test():
    system = SolarPVMultiAgent(log_level="INFO")
    info = system.get_system_info()
    print(f"✓ System initialized with {info['total_agents']} agents")
    print(f"✓ Using model: {info['model']}")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test())
        print("\n✓ Setup successful!")
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
```

Run it:
```bash
python test_setup.py
```

## Step 3: First Query

Create `first_query.py`:

```python
import asyncio
from src.api import SolarPVMultiAgent

async def main():
    # Initialize the system
    agent_system = SolarPVMultiAgent()

    # Ask a question
    result = await agent_system.query(
        "What is IEC 61215 and why is it important for solar panels?"
    )

    # Display results
    print("Question: What is IEC 61215?")
    print("\nAnswer:")
    print(result['response'])
    print(f"\nAgents involved: {', '.join(result['agents_used'])}")
    print(f"Time taken: {result['execution_time']:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python first_query.py
```

## Step 4: Explore Examples

The repository includes comprehensive examples:

### Basic Usage

```bash
python examples/basic_usage.py
```

This demonstrates:
- IEC standards queries
- Testing procedures
- Performance analysis
- Multi-agent collaboration
- Agent capabilities

### Advanced Usage

```bash
python examples/advanced_usage.py
```

This shows:
- Custom configuration
- Detailed response analysis
- Error handling
- Batch processing
- Agent comparison

## Common Use Cases

### 1. IEC Standards Inquiry

```python
result = await agent_system.query(
    "What are the testing requirements in IEC 61215 for crystalline silicon modules?"
)
```

**Expected routing**: IEC Standards Expert

### 2. Testing Procedures

```python
result = await agent_system.query(
    "How do I perform flash testing on PV modules?"
)
```

**Expected routing**: Testing Specialist

### 3. Performance Analysis

```python
result = await agent_system.query(
    "What is a good performance ratio for a residential solar installation?"
)
```

**Expected routing**: Performance Analyst

### 4. Multi-Agent Collaboration

```python
result = await agent_system.query(
    "What IEC standards apply to performance testing, "
    "and what specific procedures should I follow?"
)
```

**Expected routing**: IEC Standards Expert + Testing Specialist (collaborative)

## Understanding Results

The `query()` method returns a comprehensive result dictionary:

```python
{
    "response": "The synthesized answer...",
    "agents_used": ["iec_standards_001"],
    "agent_details": [
        {
            "agent_id": "iec_standards_001",
            "agent_type": "iec_standards_expert",
            "confidence": 0.9,
            "reasoning": "Query explicitly about IEC standards..."
        }
    ],
    "routing_info": {
        "primary_agents": ["iec_standards_001"],
        "requires_collaboration": False,
        "confidence": 0.9,
        "task_type": "iec_standards"
    },
    "execution_time": 2.5,
    "timestamp": "2025-11-18T..."
}
```

## Configuration Options

### Using Custom Configuration

```python
from src.api import SolarPVMultiAgent
from src.core.config import SystemConfig

# Create custom config
config = SystemConfig(
    default_model="gpt-4-turbo-preview",
    agent_temperature=0.5,  # Lower = more consistent
    max_iterations=3
)

# Initialize with custom config
agent_system = SolarPVMultiAgent(
    system_config=config,
    log_level="DEBUG"  # More verbose logging
)
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `default_model` | `gpt-4-turbo-preview` | LLM model for agents |
| `supervisor_model` | `gpt-4-turbo-preview` | LLM for routing/orchestration |
| `agent_temperature` | `0.7` | Response creativity (0.0-2.0) |
| `max_iterations` | `5` | Maximum execution rounds |
| `log_level` | `INFO` | Logging verbosity |

## Querying Specific Agents

Bypass routing and query a specific agent:

```python
# Query IEC Standards Expert directly
result = await agent_system.query_specific_agent(
    agent_type="iec_standards_expert",
    question="What is IEC 61730?"
)

print(result['response'])
print(f"Confidence: {result['confidence']}")
```

Available agent types:
- `iec_standards_expert`
- `testing_specialist`
- `performance_analyst`

## Getting System Information

### Agent Capabilities

```python
capabilities = await agent_system.get_capabilities()

for agent_id, cap in capabilities.items():
    print(f"{agent_id}:")
    print(f"  Type: {cap['agent_type']}")
    print(f"  Description: {cap['description']}")
    print(f"  Keywords: {', '.join(cap['keywords'][:5])}...")
```

### System Info

```python
info = agent_system.get_system_info()

print(f"Total Agents: {info['total_agents']}")
print(f"Agent Types: {', '.join(info['agent_types'])}")
print(f"Model: {info['model']}")
```

## Troubleshooting

### Issue: ImportError

**Problem**: Module not found errors

**Solution**: Ensure you're in the project root and dependencies are installed:
```bash
cd Solar-PV-LLM-AI
pip install -r requirements.txt
```

### Issue: API Key Error

**Problem**: "API key not found" or authentication errors

**Solution**:
1. Check `.env` file exists
2. Verify API key is correct
3. Ensure no extra spaces in `.env`

### Issue: Slow Responses

**Problem**: Queries take too long

**Solutions**:
- Use a faster model in config
- Reduce `max_iterations`
- Query specific agents directly for simple questions

### Issue: Low Quality Responses

**Problem**: Responses don't meet expectations

**Solutions**:
- Increase `agent_temperature` for more creative responses
- Use `gpt-4` instead of `gpt-3.5-turbo` for better quality
- Provide more context in your queries

## Next Steps

1. **Read the Documentation**:
   - [Architecture Guide](ARCHITECTURE.md)
   - [API Reference](API_REFERENCE.md)

2. **Explore Examples**:
   - Check `examples/basic_usage.py`
   - Review `examples/advanced_usage.py`

3. **Run Tests**:
   ```bash
   pytest tests/
   ```

4. **Extend the System**:
   - Add new specialized agents
   - Customize routing logic
   - Integrate with your application

## Getting Help

- Check the [API Reference](API_REFERENCE.md) for detailed documentation
- Review [examples/](../examples/) for code samples
- Open an issue on GitHub for bugs or questions

## Best Practices

1. **Be Specific**: More specific queries get better results
2. **Use Metadata**: Add context via the metadata parameter
3. **Monitor Execution**: Check execution_time and agent_details
4. **Handle Errors**: Always wrap queries in try-except blocks
5. **Cache Results**: Store responses for repeated queries (if applicable)

Example with error handling:

```python
try:
    result = await agent_system.query("Your question")
    print(result['response'])
except Exception as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

## Sample Integration

Example of integrating into a web application:

```python
from fastapi import FastAPI
from src.api import SolarPVMultiAgent

app = FastAPI()
agent_system = SolarPVMultiAgent()

@app.post("/query")
async def query_endpoint(question: str):
    result = await agent_system.query(question)
    return {
        "answer": result['response'],
        "agents": result['agents_used'],
        "time": result['execution_time']
    }
```

Happy querying! 🌞
