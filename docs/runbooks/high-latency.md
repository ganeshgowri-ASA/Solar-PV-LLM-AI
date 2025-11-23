# Runbook: High Latency

**Alert Names:** `HighAPILatency` / `CriticalLLMLatency` / `HighLLMLatency`
**Severity:** Warning / Critical
**Component:** API / LLM

## Description

The application or LLM is experiencing high response latency, causing slow user experience.

## Impact

- **Users:** Slow or timing out requests
- **Business:** Poor user experience, potential abandonment
- **SLA:** May breach response time SLAs

## Alert Thresholds

### API Latency
- **Warning:** P95 > 2 seconds for 3 minutes
- **Critical:** P95 > 5 seconds for 2 minutes

### LLM Latency
- **Warning:** P95 > 5 seconds for 3 minutes
- **Critical:** P95 > 10 seconds for 2 minutes

## Triage Steps

### 1. Check Current Latency

```bash
# Get latency metrics
python3 scripts/monitoring/query_metrics.py | grep -A 10 "Latency"

# Check Prometheus
curl "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[5m]))"

curl "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(llm_query_duration_seconds_bucket[5m]))"
```

### 2. Identify Latency Source

```bash
# Test API directly
time curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is solar energy?"}'

# Check if it's network latency
ping localhost

# Check system load
uptime
top -bn1 | head -20
```

### 3. Check Resource Utilization

```bash
# CPU usage
docker stats solar-pv-llm-app --no-stream

# Memory usage
free -h

# Disk I/O
iostat -x 1 5

# Network
netstat -s | grep -i retrans
```

## Common Causes and Solutions

### Cause 1: LLM API Slowdown

**Symptoms:**
- High LLM latency but normal API latency
- Timeouts to LLM provider
- Specific to query endpoint

**Resolution:**
```bash
# Check LLM provider status
# OpenAI status: https://status.openai.com
# Anthropic status: https://status.anthropic.com

# Check LangSmith traces for slow queries
# Go to: https://smith.langchain.com
# Filter by: Duration > 5s

# Reduce LLM timeout if needed
# Edit src/models/solar_llm.py
# Add: timeout=30  # or lower

# Consider implementing caching for common queries
```

**Temporary Mitigation:**
```python
# Add response caching (requires code change)
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_query(query_hash):
    # Cache common queries
    pass
```

### Cause 2: RAG Retrieval Slowdown

**Symptoms:**
- Slow document retrieval
- ChromaDB timeouts
- High disk I/O

**Resolution:**
```bash
# Check RAG retrieval time
curl "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(rag_retrieval_duration_seconds_bucket[5m]))"

# Check ChromaDB size
du -sh ./data/chroma/

# Optimize ChromaDB if large
# Consider:
# - Reducing document chunk size
# - Limiting retrieval count
# - Adding indexes
# - Moving to faster storage (SSD)

# Restart ChromaDB
docker-compose restart app
```

### Cause 3: High Request Volume

**Symptoms:**
- Latency correlates with request rate
- System resources maxed out
- Queue buildup

**Resolution:**
```bash
# Check request rate
curl "http://localhost:9090/api/v1/query?query=rate(http_requests_total[5m])"

# Scale horizontally
docker-compose up -d --scale app=3

# Add load balancer (nginx) if not present
# See: docs/deployment/load-balancing.md

# Implement rate limiting
# Add to src/api/main.py:
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### Cause 4: Database Locks/Contention

**Symptoms:**
- Slow database queries
- Lock timeouts
- Increasing latency over time

**Resolution:**
```bash
# Check for database locks
# (If using PostgreSQL for metadata)
docker exec -it postgres psql -U user -c \
  "SELECT * FROM pg_stat_activity WHERE wait_event IS NOT NULL;"

# Clear stale connections
# Restart database container
docker-compose restart db

# Optimize queries
# Add indexes for frequently queried fields
```

### Cause 5: Memory Pressure/Swapping

**Symptoms:**
- High memory usage
- System swapping to disk
- Gradual latency increase

**Resolution:**
```bash
# Check swap usage
free -h
vmstat 1 5

# Check for memory leaks
docker exec solar-pv-llm-app ps aux --sort=-%mem

# Increase memory limits
# Edit docker-compose.yml:
services:
  app:
    mem_limit: 8g
    mem_reservation: 4g

# Restart with new limits
docker-compose up -d --force-recreate app

# Add memory monitoring
docker stats solar-pv-llm-app
```

### Cause 6: Network Issues

**Symptoms:**
- High network latency
- Packet loss
- Intermittent timeouts

**Resolution:**
```bash
# Check network latency
ping -c 10 8.8.8.8

# Check packet loss
mtr -c 100 api.openai.com

# Check DNS resolution
dig api.openai.com

# Check for network errors
netstat -i | grep -v "^Kernel"

# Restart networking if issues found
sudo systemctl restart docker
```

## Immediate Mitigation

If latency is critical:

```bash
# 1. Restart application (quickest fix for transient issues)
docker-compose restart app

# 2. Clear caches if available
docker exec solar-pv-llm-app rm -rf /tmp/cache/*

# 3. Scale horizontally
docker-compose up -d --scale app=2

# 4. Enable emergency mode (if implemented)
# Set timeout limits lower to fail fast
curl -X POST http://localhost:8000/admin/emergency-mode \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"enabled": true, "timeout_seconds": 10}'

# 5. Consider temporarily disabling non-critical features
# - Disable detailed logging
# - Reduce RAG document retrieval count
# - Lower LLM temperature for faster responses
```

## Performance Optimization

For sustained improvements:

### Application Level
```python
# 1. Add query caching
from aiocache import cached

@cached(ttl=3600)
async def query_llm(query: str):
    pass

# 2. Implement connection pooling
# 3. Use async/await properly
# 4. Batch RAG retrievals
# 5. Optimize serialization
```

### Infrastructure Level
```bash
# 1. Use faster storage (SSD)
# 2. Add more RAM
# 3. Upgrade CPU
# 4. Implement CDN for static assets
# 5. Add read replicas for database
```

### Configuration Level
```yaml
# docker-compose.yml optimizations
services:
  app:
    cpus: '4'
    mem_limit: 8g
    environment:
      - WORKERS=4
      - TIMEOUT=30
```

## Verification

After implementing fixes:

```bash
# 1. Test latency directly
for i in {1..10}; do
  time curl -X POST http://localhost:8000/api/v1/query \
    -H "Content-Type: application/json" \
    -d '{"query": "test"}' &
done
wait

# 2. Check metrics
python3 scripts/monitoring/query_metrics.py

# 3. Monitor Grafana dashboard
# Check: http://localhost:3000/d/solar-pv-llm-overview

# 4. Watch latency trend
watch -n 10 'curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[1m]))" | jq ".data.result[0].value[1]"'
```

## Investigation Checklist

- [ ] Measure current latency (API and LLM)
- [ ] Check system resources (CPU, memory, disk)
- [ ] Review request rate and patterns
- [ ] Check LLM provider status
- [ ] Test RAG retrieval speed
- [ ] Review application logs for slow operations
- [ ] Check network connectivity
- [ ] Verify database performance
- [ ] Review recent code changes
- [ ] Check for memory leaks

## Prevention

1. **Performance Testing:**
   - Regular load testing
   - Stress testing before releases
   - Performance regression tests
   - Benchmark critical paths

2. **Optimization:**
   - Query result caching
   - Connection pooling
   - Async processing where possible
   - Efficient data structures

3. **Monitoring:**
   - Track latency percentiles (P50, P95, P99)
   - Monitor resource utilization trends
   - Set up latency budgets
   - Regular performance reviews

4. **Capacity Planning:**
   - Monitor growth trends
   - Plan for peak usage
   - Auto-scaling rules
   - Resource headroom (25-30%)

## Escalation

If latency remains high after 20 minutes:

1. **Escalate to:** Performance Engineering Team
2. **Contact:** performance@company.com
3. **Slack:** #performance-incidents
4. **Consider:** Emergency maintenance window

## Related Runbooks

- [High Error Rate](./high-error-rate.md)
- [Memory Issues](./high-memory.md)
- [LLM API Failures](./llm-api-failures.md)
- [RAG System Issues](./rag-issues.md)

## Post-Incident

After resolution:

1. Conduct performance profiling
2. Identify bottlenecks
3. Implement long-term optimizations
4. Update capacity planning
5. Add performance tests
6. Document optimizations
