# Usage Guide: Solar PV Multi-LLM Orchestrator

This guide provides detailed instructions for using the Multi-LLM Orchestrator for Solar PV queries.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Query Classification](#query-classification)
3. [LLM Routing Strategy](#llm-routing-strategy)
4. [Advanced Features](#advanced-features)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- API keys for:
  - OpenAI (GPT-4o)
  - Anthropic (Claude 3.5 Sonnet)

### Initial Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Start the service:
```bash
python main.py
```

## Query Classification

The orchestrator automatically classifies queries into five types:

### 1. Standard Interpretation

**Best for:** General questions about Solar PV concepts, components, and systems.

**Triggers:**
- General "what is" questions
- Broad explanations
- Overview requests

**Examples:**
```json
{
  "query": "What is a solar inverter?"
}
```

**Primary LLM:** Claude 3.5 (better for comprehensive explanations)

### 2. Calculation

**Best for:** Numerical calculations, system sizing, performance analysis.

**Triggers:**
- "calculate", "compute", "size"
- Numerical values with units (kW, kWh, MW)
- ROI, payback, LCOE calculations

**Examples:**
```json
{
  "query": "Calculate energy yield for a 10kW system with 5 sun hours per day"
}
```

**Primary LLM:** GPT-4o (better for structured calculations)

### 3. Image Analysis

**Best for:** Visual inspection, thermal imaging, defect detection.

**Triggers:**
- Image data provided
- Keywords: "image", "thermal", "inspect", "photo"

**Examples:**
```json
{
  "query": "Analyze defects in this solar panel array",
  "image_data": "base64_encoded_image_data"
}
```

**Primary LLM:** GPT-4o (strong vision capabilities)

### 4. Technical Explanation

**Best for:** Deep technical concepts, physics, engineering principles.

**Triggers:**
- "how does", "explain", "why"
- Technical terms: MPPT, inverter topology, physics
- Comparison requests

**Examples:**
```json
{
  "query": "How does MPPT tracking work in solar inverters?"
}
```

**Primary LLM:** Claude 3.5 (excels at detailed explanations)

### 5. Code Generation

**Best for:** Python code, simulations, data analysis scripts.

**Triggers:**
- "write code", "script", "implement"
- Mentions of: pvlib, pandas, Python
- "simulate", "model", "automate"

**Examples:**
```json
{
  "query": "Write Python code to calculate shading losses using pvlib"
}
```

**Primary LLM:** GPT-4o (strong code generation)

## LLM Routing Strategy

### Automatic Routing

The orchestrator uses intelligent routing based on:

1. **Query Type**: Each type has a preferred primary LLM
2. **Confidence Score**: Low confidence triggers hybrid mode
3. **User Preference**: Can override automatic selection

### Routing Table

| Query Type | Primary LLM | Fallback LLM | Reasoning |
|------------|-------------|--------------|-----------|
| Calculation | GPT-4o | Claude 3.5 | Better structured output |
| Image Analysis | GPT-4o | Claude 3.5 | Strong vision capabilities |
| Code Generation | GPT-4o | Claude 3.5 | Excellent code quality |
| Technical Explanation | Claude 3.5 | GPT-4o | Nuanced explanations |
| Standard Interpretation | Claude 3.5 | GPT-4o | Comprehensive responses |

### Confidence Thresholds

- **High Confidence (≥ 0.7)**: Use primary LLM only
- **Medium Confidence (0.5-0.7)**: Consider hybrid
- **Low Confidence (< 0.5)**: Use hybrid mode

## Advanced Features

### Hybrid Responses

Hybrid mode queries both LLMs and synthesizes their responses:

```json
{
  "query": "Compare monocrystalline vs polycrystalline solar panels",
  "preferred_llm": "hybrid"
}
```

**When to use:**
- Complex, multi-faceted questions
- When you want diverse perspectives
- For critical decisions requiring validation

### Explicit LLM Selection

Override automatic routing:

```json
{
  "query": "Your question here",
  "preferred_llm": "claude"  // or "gpt"
}
```

**Use cases:**
- You know which LLM performs better for your use case
- Consistency in multi-query workflows
- Cost optimization

### Custom Temperature

Control response creativity:

```json
{
  "query": "Calculate system size",
  "temperature": 0.2  // More deterministic (good for calculations)
}
```

```json
{
  "query": "Explain solar technology trends",
  "temperature": 0.9  // More creative (good for brainstorming)
}
```

**Recommended settings:**
- Calculations: 0.2-0.4
- Technical explanations: 0.5-0.7
- Creative/comparative: 0.7-0.9

### Token Limits

Adjust response length:

```json
{
  "query": "Brief overview of solar panels",
  "max_tokens": 500  // Shorter response
}
```

```json
{
  "query": "Comprehensive guide to PV system design",
  "max_tokens": 4000  // Longer, detailed response
}
```

## Best Practices

### 1. Query Formulation

**Good:**
- "Calculate the ROI for a 50kW commercial system with $40,000 installation cost and $6,000 annual savings"
- "Explain how bifacial solar panels increase energy yield compared to monofacial panels"

**Less Effective:**
- "Tell me about solar"
- "How much money?"

### 2. Query Type Hints

When automatic classification might be unclear, provide explicit type:

```json
{
  "query": "What's the formula for performance ratio?",
  "query_type": "calculation"  // Ensures calculation-focused response
}
```

### 3. Context Provision

Include relevant context:

```json
{
  "query": "Size the inverter for this system",
  "context": {
    "location": "Arizona",
    "panel_count": 20,
    "panel_wattage": 400,
    "system_type": "grid-tied"
  }
}
```

### 4. Iterative Refinement

Start broad, then narrow:

1. "What are the main types of solar inverters?"
2. "Compare string inverters vs microinverters for residential use"
3. "Calculate optimal inverter size for 15x 350W panels with microinverters"

### 5. Leveraging Hybrid Mode

Use for:
- Complex comparisons
- Decision-making scenarios
- Validation of calculations
- Multi-perspective analysis

## Troubleshooting

### Issue: Low Classification Confidence

**Symptom:** Responses marked as hybrid when you expected single LLM

**Solutions:**
- Make query more specific
- Include explicit query_type
- Add more context
- Use domain-specific terminology

### Issue: Unexpected LLM Selection

**Symptom:** GPT used when Claude expected (or vice versa)

**Solutions:**
- Check automatic classification result
- Use preferred_llm parameter
- Review query wording
- Provide explicit query_type

### Issue: Response Quality

**Symptom:** Response not meeting expectations

**Solutions:**
- Adjust temperature (lower for factual, higher for creative)
- Increase max_tokens for more detail
- Try hybrid mode for comparison
- Rephrase query with more specifics

### Issue: Slow Response Times

**Symptom:** High latency

**Causes & Solutions:**
- Large max_tokens → Reduce if possible
- Hybrid mode → Use single LLM if acceptable
- Image analysis → Compress images
- Network issues → Check connectivity

### Issue: Fallback Triggered

**Symptom:** fallback_used: true in response

**Common Causes:**
- Primary LLM API issues
- Rate limiting
- Invalid API key
- Network problems

**Resolution:**
- Check API key validity
- Review rate limits
- Check service health endpoint
- Review logs for errors

## Performance Optimization

### 1. Caching Strategy

For repeated queries, consider implementing client-side caching:

```python
cache = {}

async def cached_query(query):
    if query in cache:
        return cache[query]

    result = await orchestrator_query(query)
    cache[query] = result
    return result
```

### 2. Batch Processing

For multiple related queries:

```python
queries = [
    "Calculate yield for 10kW",
    "Calculate yield for 20kW",
    "Calculate yield for 30kW"
]

# Process concurrently
results = await asyncio.gather(*[
    orchestrator_query(q) for q in queries
])
```

### 3. Cost Management

Monitor token usage:

```python
response = await orchestrator_query(query)
tokens_used = sum(r.tokens_used for r in response.responses)
print(f"Total tokens: {tokens_used}")
```

## Monitoring

### Health Checks

Regular health monitoring:

```python
import httpx

async def check_health():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/health")
        return response.json()
```

### Metrics to Track

- Average latency per query type
- Classification accuracy
- Fallback frequency
- Token consumption
- Error rates

## Support

For additional help:
- Check API documentation: `/docs`
- Review examples: `examples/example_usage.py`
- GitHub Issues: [Report issues](https://github.com/ganeshgowri-ASA/Solar-PV-LLM-AI/issues)
