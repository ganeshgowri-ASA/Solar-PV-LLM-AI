# Solar PV LLM AI - Operations Runbook

Operational procedures for incident response and maintenance.

## Table of Contents

1. [Emergency Contacts](#emergency-contacts)
2. [System Architecture](#system-architecture)
3. [Incident Response](#incident-response)
4. [Common Operations](#common-operations)
5. [Monitoring & Alerts](#monitoring--alerts)
6. [Disaster Recovery](#disaster-recovery)

---

## Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| On-Call Engineer | oncall@your-domain.com | 24/7 |
| DevOps Lead | devops-lead@your-domain.com | Mon-Fri 9-5 |
| Database Admin | dba@your-domain.com | 24/7 |
| Security Team | security@your-domain.com | 24/7 |

**Escalation Path**: On-Call → DevOps Lead → CTO

---

## System Architecture

### Components

```
┌─────────────┐
│   Users     │
└──────┬──────┘
       │
┌──────▼──────────────────┐
│   Load Balancer/Ingress │
└──────┬──────────────────┘
       │
   ┌───┴───┬─────────────┬─────────────┐
   │       │             │             │
┌──▼───┐ ┌─▼──────┐  ┌──▼──────┐  ┌──▼────────┐
│Frontend│Backend │  │ Celery  │  │ Flower    │
│  (2)  ││  (3)   │  │ Worker  │  │ (Monitor) │
└───────┘ │        │  │  (2)    │  └───────────┘
          └────┬───┘  └────┬────┘
               │           │
       ┌───────┴───────────┴────────┐
       │                            │
   ┌───▼────┐                  ┌───▼────┐
   │Postgres│                  │ Redis  │
   └────────┘                  └────────┘
```

### Resource Allocation

| Component | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-----------|-------------|----------------|-----------|--------------|
| Backend | 500m | 512Mi | 2000m | 2Gi |
| Frontend | 100m | 128Mi | 200m | 256Mi |
| Worker | 1000m | 1Gi | 2000m | 4Gi |
| Postgres | 250m | 256Mi | 1000m | 1Gi |
| Redis | 250m | 256Mi | 500m | 512Mi |

---

## Incident Response

### Severity Levels

- **P0 (Critical)**: System down, data loss, security breach
- **P1 (High)**: Major feature broken, performance degradation
- **P2 (Medium)**: Minor feature broken, workaround available
- **P3 (Low)**: Cosmetic issues, minor bugs

### Response Times

| Severity | Response Time | Resolution Time |
|----------|---------------|-----------------|
| P0 | 15 minutes | 1 hour |
| P1 | 1 hour | 4 hours |
| P2 | 4 hours | 1 day |
| P3 | 1 day | 1 week |

### P0 Incident Response Checklist

1. **Acknowledge**
   - [ ] Acknowledge alert in monitoring system
   - [ ] Post in #incidents Slack channel
   - [ ] Start incident Zoom call

2. **Assess**
   - [ ] Check system status dashboard
   - [ ] Review recent deployments
   - [ ] Check error logs
   - [ ] Identify affected users

3. **Mitigate**
   - [ ] Implement immediate fix or rollback
   - [ ] Enable maintenance mode if needed
   - [ ] Update status page

4. **Resolve**
   - [ ] Apply permanent fix
   - [ ] Verify system stability
   - [ ] Disable maintenance mode

5. **Post-Mortem**
   - [ ] Document incident timeline
   - [ ] Identify root cause
   - [ ] Create action items
   - [ ] Schedule post-mortem meeting

---

## Common Operations

### 1. Application Deployment

```bash
# Check current version
kubectl get deployment backend -n solar-pv-llm-ai -o jsonpath='{.spec.template.spec.containers[0].image}'

# Deploy new version (via CI/CD)
git tag v1.2.3
git push origin v1.2.3

# Manual deployment
kubectl set image deployment/backend backend=ghcr.io/org/solar-pv-backend:v1.2.3 -n solar-pv-llm-ai

# Monitor rollout
kubectl rollout status deployment/backend -n solar-pv-llm-ai
```

### 2. Scaling Services

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n solar-pv-llm-ai

# Scale workers during high load
kubectl scale deployment celery-worker --replicas=5 -n solar-pv-llm-ai

# Check autoscaling
kubectl get hpa -n solar-pv-llm-ai
```

### 3. Database Operations

```bash
# Access database
kubectl exec -it deployment/postgres -n solar-pv-llm-ai -- psql -U solar_pv_user -d solar_pv_db

# Run migrations
kubectl exec deployment/backend -n solar-pv-llm-ai -- alembic upgrade head

# Backup database
./scripts/backup.sh

# Check database size
kubectl exec deployment/postgres -n solar-pv-llm-ai -- \
  psql -U solar_pv_user -d solar_pv_db -c "SELECT pg_size_pretty(pg_database_size('solar_pv_db'));"
```

### 4. Clear Redis Cache

```bash
# Clear all caches
kubectl exec deployment/redis -n solar-pv-llm-ai -- redis-cli FLUSHALL

# Clear specific pattern
kubectl exec deployment/redis -n solar-pv-llm-ai -- redis-cli KEYS "cache:*" | xargs redis-cli DEL
```

### 5. Restart Services

```bash
# Restart backend (rolling restart)
kubectl rollout restart deployment/backend -n solar-pv-llm-ai

# Restart all workers
kubectl rollout restart deployment/celery-worker -n solar-pv-llm-ai

# Force pod restart
kubectl delete pod -l app=backend -n solar-pv-llm-ai
```

### 6. View Logs

```bash
# Backend logs (last 100 lines)
kubectl logs --tail=100 deployment/backend -n solar-pv-llm-ai

# Stream logs
kubectl logs -f deployment/backend -n solar-pv-llm-ai

# Logs from all backend pods
kubectl logs -f -l app=backend -n solar-pv-llm-ai

# Filter logs
kubectl logs deployment/backend -n solar-pv-llm-ai | grep ERROR

# Export logs to file
kubectl logs deployment/backend -n solar-pv-llm-ai > backend.log
```

### 7. Execute Commands in Pods

```bash
# Shell access
kubectl exec -it deployment/backend -n solar-pv-llm-ai -- /bin/bash

# Run management command
kubectl exec deployment/backend -n solar-pv-llm-ai -- python manage.py createsuperuser

# Check environment variables
kubectl exec deployment/backend -n solar-pv-llm-ai -- env | grep DATABASE
```

---

## Monitoring & Alerts

### Key Metrics

| Metric | Threshold | Action |
|--------|-----------|--------|
| Pod CPU Usage | >80% | Scale up |
| Pod Memory Usage | >85% | Scale up |
| API Response Time | >2s | Investigate |
| Error Rate | >5% | Alert |
| Database Connections | >80 of 100 | Scale database |
| Disk Usage | >85% | Clean up or expand |

### Check System Health

```bash
# Overall cluster health
kubectl get nodes
kubectl top nodes

# Pod status
kubectl get pods -n solar-pv-llm-ai
kubectl top pods -n solar-pv-llm-ai

# Service endpoints
kubectl get endpoints -n solar-pv-llm-ai

# Ingress status
kubectl get ingress -n solar-pv-llm-ai
```

### Prometheus Queries

```promql
# API request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Pod CPU usage
sum(rate(container_cpu_usage_seconds_total{namespace="solar-pv-llm-ai"}[5m])) by (pod)
```

---

## Disaster Recovery

### Database Restore

```bash
# 1. Stop application
kubectl scale deployment backend --replicas=0 -n solar-pv-llm-ai
kubectl scale deployment celery-worker --replicas=0 -n solar-pv-llm-ai

# 2. Download backup
aws s3 cp s3://solar-pv-backups/database/latest.sql.gz /tmp/

# 3. Restore
gunzip < /tmp/latest.sql.gz | kubectl exec -i deployment/postgres -n solar-pv-llm-ai -- \
  psql -U solar_pv_user -d solar_pv_db

# 4. Restart application
kubectl scale deployment backend --replicas=3 -n solar-pv-llm-ai
kubectl scale deployment celery-worker --replicas=2 -n solar-pv-llm-ai
```

### Complete System Restore

```bash
# 1. Provision infrastructure
cd terraform
terraform apply

# 2. Deploy application
kubectl apply -f kubernetes/

# 3. Restore database
./scripts/restore.sh

# 4. Verify
curl https://api.your-domain.com/health
```

---

## Troubleshooting Playbooks

### Backend Not Responding

1. Check pod status:
   ```bash
   kubectl get pods -n solar-pv-llm-ai | grep backend
   ```

2. Check logs:
   ```bash
   kubectl logs deployment/backend -n solar-pv-llm-ai --tail=100
   ```

3. Check database connectivity:
   ```bash
   kubectl exec deployment/backend -n solar-pv-llm-ai -- \
     python -c "from app.core.database import engine; print('OK')"
   ```

4. Restart if needed:
   ```bash
   kubectl rollout restart deployment/backend -n solar-pv-llm-ai
   ```

### High CPU Usage

1. Identify pod:
   ```bash
   kubectl top pods -n solar-pv-llm-ai --sort-by=cpu
   ```

2. Check metrics:
   ```bash
   kubectl describe pod <pod-name> -n solar-pv-llm-ai
   ```

3. Scale if needed:
   ```bash
   kubectl scale deployment backend --replicas=5 -n solar-pv-llm-ai
   ```

### Database Connection Pool Exhausted

1. Check connections:
   ```bash
   kubectl exec deployment/postgres -n solar-pv-llm-ai -- \
     psql -U solar_pv_user -d solar_pv_db -c "SELECT count(*) FROM pg_stat_activity;"
   ```

2. Kill idle connections:
   ```bash
   kubectl exec deployment/postgres -n solar-pv-llm-ai -- \
     psql -U solar_pv_user -d solar_pv_db -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';"
   ```

3. Increase pool size (if needed):
   - Update `DATABASE_POOL_SIZE` in ConfigMap
   - Restart backend

---

## Maintenance Windows

### Scheduled Maintenance

- **When**: Every Sunday 2:00-4:00 AM UTC
- **Duration**: Max 2 hours
- **Notification**: 1 week advance notice

### Maintenance Checklist

- [ ] Post maintenance notice
- [ ] Create backup
- [ ] Enable maintenance mode
- [ ] Perform maintenance tasks
- [ ] Verify system health
- [ ] Disable maintenance mode
- [ ] Post completion notice

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2024-01-01 | Initial runbook | DevOps Team |

---

## Additional Resources

- [Deployment Guide](./DEPLOYMENT.md)
- [Architecture Documentation](./docs/architecture.md)
- [API Documentation](https://api.your-domain.com/docs)
- [Grafana Dashboards](https://grafana.your-domain.com)
