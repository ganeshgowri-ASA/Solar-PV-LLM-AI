# Runbook: Service Down

**Alert Name:** `ServiceDown`
**Severity:** Critical
**Component:** Application

## Description

The Solar PV LLM AI application is not responding to health checks. This is a critical issue that requires immediate attention as users cannot access the service.

## Impact

- **Users:** Cannot access the application
- **Business:** Complete service outage
- **SLA:** Critical - Immediate response required

## Triage Steps

### 1. Verify the Alert

```bash
# Check if the service is actually down
curl -f http://localhost:8000/health

# Check Docker container status
docker ps | grep solar-pv-llm-app

# Check service logs
docker logs solar-pv-llm-app --tail 100
```

### 2. Check Recent Changes

- Review recent deployments
- Check if there were any configuration changes
- Review git history: `git log --oneline -10`

### 3. Check System Resources

```bash
# Check system resources
./scripts/monitoring/health_check.sh

# Check disk space
df -h

# Check memory
free -h

# Check CPU
top -bn1 | head -20
```

## Resolution Steps

### Option 1: Restart the Service

```bash
# Restart the Docker container
docker-compose restart app

# Wait 30 seconds and verify
sleep 30
curl -f http://localhost:8000/health
```

### Option 2: Full Stack Restart

```bash
# If restart doesn't work, try full restart
docker-compose down
docker-compose up -d

# Monitor logs
docker-compose logs -f app
```

### Option 3: Check for Application Errors

```bash
# Check application logs for errors
docker logs solar-pv-llm-app --tail 500 | grep -i error

# Common issues to look for:
# - Database connection failures
# - Missing environment variables
# - LLM API key issues
# - Port conflicts
```

### Option 4: Rebuild and Deploy

```bash
# If the application is corrupted, rebuild
docker-compose down
docker-compose build --no-cache app
docker-compose up -d app

# Monitor startup
docker-compose logs -f app
```

## Verification

After resolution, verify:

```bash
# 1. Health check passes
curl -f http://localhost:8000/health

# 2. API is responding
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# 3. Metrics are being collected
curl http://localhost:8000/metrics | head -20

# 4. Alert has cleared in Prometheus
# Check: http://localhost:9090/alerts
```

## Escalation

If the issue persists after 15 minutes:

1. **Escalate to:** Infrastructure Team Lead
2. **Contact:** infrastructure-oncall@company.com
3. **Slack:** #incident-response
4. **Create incident:** Use incident management system

## Prevention

- Enable automated health checks with auto-restart
- Set up redundancy with multiple instances
- Implement circuit breakers
- Review and test disaster recovery procedures

## Related Runbooks

- [High Memory Usage](./high-memory.md)
- [High Error Rate](./high-error-rate.md)
- [Database Connection Issues](./database-issues.md)

## Post-Incident

After resolution:

1. Document root cause
2. Update this runbook if needed
3. Schedule post-mortem meeting
4. Implement preventive measures
