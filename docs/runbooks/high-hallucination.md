# Runbook: High Hallucination Score

**Alert Name:** `HighHallucinationScore` / `FrequentHallucinations`
**Severity:** Warning / Critical
**Component:** LLM Quality

## Description

The LLM is generating responses with a high hallucination risk score, meaning it may be generating information that is not grounded in the provided context or factual data.

## Impact

- **Users:** May receive inaccurate or fabricated information
- **Business:** Risk to credibility and trust
- **Compliance:** Potential liability for providing incorrect information

## Understanding Hallucination Scores

- **Score Range:** 0.0 (low risk) to 1.0 (high risk)
- **Warning Threshold:** > 0.5
- **Critical Threshold:** Frequent occurrences (> 0.1 per second)

## Triage Steps

### 1. Verify the Alert

```bash
# Check current hallucination metrics
python3 scripts/monitoring/query_metrics.py | grep -A 5 "LLM Quality"

# Query Prometheus directly
curl "http://localhost:9090/api/v1/query?query=llm_hallucination_score"
```

### 2. Check Recent Queries

Access LangSmith to review recent queries:
- Go to: https://smith.langchain.com
- Project: solar-pv-llm-ai
- Filter by: Last 1 hour
- Sort by: Lowest confidence score

Look for patterns:
- Are certain types of queries triggering hallucinations?
- Are queries asking about topics outside the RAG knowledge base?
- Are there issues with document retrieval?

### 3. Review RAG System

```bash
# Check if RAG retrieval is working
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the efficiency of solar panels?",
    "include_citations": true
  }' | jq '.citations'

# Should return citations from retrieved documents
```

## Resolution Steps

### Option 1: Adjust LLM Temperature

If hallucination score is consistently high:

```python
# Lower the temperature in src/api/main.py
# Current default: 0.7
# Reduce to: 0.3-0.5 for more conservative responses

# This requires a code change and redeployment
```

### Option 2: Improve RAG Document Quality

```bash
# Check if knowledge base needs updating
# Review document quality and coverage

# Add more authoritative sources
# Update ChromaDB with better documents

# Verify document retrieval count
python3 scripts/monitoring/query_metrics.py | grep "RAG"
```

### Option 3: Implement Response Validation

```python
# Add additional validation in src/models/solar_llm.py
# Enhance the _calculate_hallucination_score method
# Consider implementing:
# - Semantic similarity checks
# - Fact verification against source documents
# - Citation requirement for factual claims
```

### Option 4: Update System Prompt

```python
# In src/models/solar_llm.py, strengthen the system prompt:
# - Emphasize staying grounded in provided context
# - Require explicit acknowledgment of uncertainty
# - Mandate citations for all factual claims
```

### Option 5: Enable Guardrails

```python
# Implement response guardrails:
# - Reject responses with no document support
# - Flag uncertain responses for human review
# - Add confidence thresholds for automatic responses
```

## Immediate Mitigation

While investigating:

```bash
# 1. Enable stricter validation (if available)
# Set environment variable:
export STRICT_VALIDATION=true

# 2. Increase hallucination threshold alerts temporarily
# Edit monitoring/prometheus/alerts.yml
# Change threshold from 0.5 to 0.7 temporarily

# 3. Restart application
docker-compose restart app
```

## Verification

After implementing fixes:

```bash
# 1. Test with known queries
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is photovoltaic effect?",
    "include_citations": true
  }' | jq '{
    hallucination_score: .hallucination_score,
    confidence: .confidence,
    citations_count: (.citations | length)
  }'

# 2. Monitor hallucination metrics
watch -n 30 'python3 scripts/monitoring/query_metrics.py | grep -A 5 "LLM Quality"'

# 3. Check LangSmith traces
# Verify that recent queries have better scores
```

## Investigation Checklist

- [ ] Review recent query patterns in LangSmith
- [ ] Check RAG document retrieval quality
- [ ] Verify knowledge base is up to date
- [ ] Examine queries with highest hallucination scores
- [ ] Check if specific topics trigger hallucinations
- [ ] Review LLM model version and settings
- [ ] Verify citation generation is working
- [ ] Check response confidence scores

## Prevention

1. **Continuous Monitoring:**
   - Set up daily reviews of hallucination metrics
   - Monitor LangSmith traces regularly
   - Track hallucination patterns over time

2. **Knowledge Base Maintenance:**
   - Regular updates to RAG documents
   - Quarterly review of document quality
   - Add documents for frequently asked topics

3. **Model Configuration:**
   - Use lower temperature for factual queries
   - Implement strict citation requirements
   - Add automated fact-checking where possible

4. **User Feedback:**
   - Collect user ratings on responses
   - Track and investigate low-rated responses
   - Use feedback to improve system

## Escalation

If hallucination rate remains high after 1 hour:

1. **Escalate to:** ML/AI Team Lead
2. **Contact:** ml-team@company.com
3. **Slack:** #ml-incidents
4. **Severity:** May need to temporarily disable LLM features

## Related Runbooks

- [Low Confidence Responses](./low-confidence.md)
- [RAG System Issues](./rag-issues.md)
- [LLM API Failures](./llm-api-failures.md)

## Additional Resources

- LangSmith Dashboard: https://smith.langchain.com
- LLM Best Practices: Internal Wiki
- Hallucination Detection Papers: Research folder

## Post-Incident

After resolution:

1. Analyze root cause of hallucinations
2. Document problematic query patterns
3. Update knowledge base if gaps found
4. Improve hallucination detection algorithm
5. Consider retraining or fine-tuning model
