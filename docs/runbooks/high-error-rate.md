# Runbook: High Error Rate

**Alert Name:** `HighErrorRate` / `CriticalErrorRate`
**Severity:** Warning / Critical
**Component:** Application

## Description

The application is experiencing an elevated error rate, indicating that a significant number of requests are failing.

## Impact

- **Users:** Degraded or failed service
- **Business:** Loss of functionality, potential revenue impact
- **SLA:** May breach service level agreements

## Alert Thresholds

- **Warning:** > 0.05 errors/sec (5% error rate) for 3 minutes
- **Critical:** > 0.2 errors/sec (20% error rate) for 1 minute

## Triage Steps

### 1. Verify Current Error Rate

```bash
# Check metrics
python3 scripts/monitoring/query_metrics.py | grep -A 5 "Request Metrics"

# Query Prometheus
curl "http://localhost:9090/api/v1/query?query=rate(errors_total[5m])"

# Check error distribution
curl "http://localhost:9090/api/v1/query?query=sum(rate(errors_total[5m]))by(error_type)"
```

### 2. Identify Error Types

```bash
# Check application logs
docker logs solar-pv-llm-app --tail 200 | grep -i error

# Common error patterns to look for:
# - TimeoutError: LLM or database timeouts
# - ConnectionError: External service failures
# - ValidationError: Invalid input data
# - KeyError/AttributeError: Code bugs
# - 500/503 errors: Server errors
```

### 3. Check Affected Endpoints

```bash
# Query error breakdown by endpoint
curl "http://localhost:9090/api/v1/query?query=sum(rate(errors_total[5m]))by(endpoint)"

# Check if specific endpoint is causing errors
docker logs solar-pv-llm-app --tail 500 | grep "request_failed" | jq .path | sort | uniq -c
```

## Common Causes and Solutions

### Cause 1: LLM API Failures

**Symptoms:**
- Errors mention OpenAI/Anthropic API
- High latency coinciding with errors
- "API key invalid" or "Rate limit exceeded"

**Resolution:**
```bash
# Check API key configuration
docker exec solar-pv-llm-app env | grep -i api_key

# Verify LangSmith connectivity
curl -H "x-api-key: $LANGCHAIN_API_KEY" https://api.smith.langchain.com/api/v1/projects

# Check LLM provider status
# OpenAI: https://status.openai.com
# Anthropic: https://status.anthropic.com

# If rate limited, implement backoff or upgrade API tier
```

### Cause 2: Database/RAG Issues

**Symptoms:**
- ChromaDB connection errors
- "Collection not found" errors
- Slow document retrieval

**Resolution:**
```bash
# Check if ChromaDB data exists
ls -lh ./data/chroma/

# Restart with fresh DB if corrupted
docker-compose down
rm -rf ./data/chroma/*
docker-compose up -d

# Reinitialize knowledge base
# (Run your data ingestion script)
```

### Cause 3: Invalid Input Validation

**Symptoms:**
- ValidationError in logs
- 422 Unprocessable Entity responses
- Malformed request errors

**Resolution:**
```bash
# Check logs for validation errors
docker logs solar-pv-llm-app | grep ValidationError

# Review recent changes to request models
git log --oneline --since="24 hours ago" -- src/api/

# Add additional input validation if needed
# Update src/api/main.py with stricter validation
```

### Cause 4: Memory/Resource Exhaustion

**Symptoms:**
- Out of memory errors
- System getting slower over time
- Docker container restarts

**Resolution:**
```bash
# Check resource usage
docker stats solar-pv-llm-app --no-stream

# Check for memory leaks
docker exec solar-pv-llm-app ps aux --sort=-%mem | head -10

# Increase memory limits in docker-compose.yml
# Add under app service:
#   mem_limit: 4g
#   mem_reservation: 2g

# Restart with new limits
docker-compose up -d --force-recreate app
```

### Cause 5: Code Bugs

**Symptoms:**
- Python exceptions in logs
- Specific endpoint always failing
- Stack traces in logs

**Resolution:**
```bash
# Get detailed stack trace
docker logs solar-pv-llm-app --tail 1000 | grep -A 20 "Traceback"

# Identify the problematic code
# Review recent changes
git diff HEAD~5 -- src/

# If bug identified:
# 1. Fix the code
# 2. Test locally
# 3. Deploy fix
# 4. Monitor error rate
```

## Immediate Mitigation

If errors are critical and cause is unclear:

```bash
# Option 1: Rollback to previous version
docker-compose down
git checkout HEAD~1  # or specific commit
docker-compose build app
docker-compose up -d

# Option 2: Scale horizontally (if using orchestrator)
docker-compose up -d --scale app=3

# Option 3: Enable circuit breaker for failing dependency
# (Requires code change to add circuit breaker logic)
```

## Verification

After implementing fixes:

```bash
# 1. Check error rate has decreased
python3 scripts/monitoring/query_metrics.py

# 2. Test affected endpoints
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}' \
  -w "\nHTTP Code: %{http_code}\n"

# 3. Monitor logs for new errors
docker logs solar-pv-llm-app -f | grep -i error

# 4. Watch error metrics
watch -n 10 'curl -s "http://localhost:9090/api/v1/query?query=rate(errors_total[1m])" | jq'
```

## Investigation Checklist

- [ ] Identify error types and distribution
- [ ] Check affected endpoints
- [ ] Review application logs
- [ ] Verify external service status
- [ ] Check resource utilization
- [ ] Review recent code changes
- [ ] Test individual endpoints
- [ ] Check database/RAG connectivity
- [ ] Verify API keys and credentials
- [ ] Review input validation

## Prevention

1. **Improved Error Handling:**
   - Add retry logic with exponential backoff
   - Implement circuit breakers for external services
   - Add comprehensive input validation
   - Use graceful degradation

2. **Testing:**
   - Comprehensive integration tests
   - Load testing before deployment
   - Error injection testing (chaos engineering)
   - Validate all error paths

3. **Monitoring:**
   - Set up error rate monitoring by endpoint
   - Track error patterns over time
   - Alert on error rate increases
   - Regular log analysis

4. **Documentation:**
   - Document all error codes
   - Maintain troubleshooting guides
   - Keep runbooks updated
   - Document external dependencies

## Escalation

If error rate doesn't decrease within 15 minutes:

1. **Escalate to:** Backend Team Lead
2. **Contact:** backend-team@company.com
3. **Slack:** #backend-incidents
4. **Action:** May need emergency deployment or rollback

## Related Runbooks

- [Service Down](./service-down.md)
- [High Latency](./high-latency.md)
- [LLM API Failures](./llm-api-failures.md)
- [Database Issues](./database-issues.md)

## Post-Incident

After resolution:

1. Root cause analysis
2. Implement permanent fix
3. Add tests to prevent recurrence
4. Update monitoring and alerts
5. Document lessons learned
6. Update this runbook with new insights
