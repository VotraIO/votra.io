# DevOps Operations Quick Reference

## Local Development

### Start Services

```bash
# Start all services (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

### Common Operations

```bash
# Access PostgreSQL
docker-compose exec db psql -U votraio -d votraio_db

# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "Description"

# Run tests
docker-compose exec api pytest --cov=app

# Access container shell (debugging)
docker-compose exec api bash

# View database contents
docker-compose exec db psql -U votraio -d votraio_db -c "SELECT * FROM users;"

# Clean up (remove volumes)
docker-compose down -v
```

### Performance

```bash
# Monitor container resources
docker stats

# Check database size
docker-compose exec db du -sh /var/lib/postgresql/data

# View Redis memory usage
docker-compose exec redis redis-cli INFO memory
```

---

## Kubernetes (Production)

### Cluster Access

```bash
# Get credentials
gcloud container clusters get-credentials votraio-production \
  --zone us-central1-a \
  --project votraio-prod

# Verify access
kubectl cluster-info
kubectl get nodes
```

### Deployments

```bash
# View deployments
kubectl get deployments -n production
kubectl describe deployment votraio-api -n production

# View pods
kubectl get pods -n production
kubectl describe pod <pod-name> -n production

# View services
kubectl get svc -n production

# View events
kubectl get events -n production --sort-by='.lastTimestamp'
```

### Logs & Debugging

```bash
# View pod logs
kubectl logs <pod-name> -n production
kubectl logs <pod-name> -n production --previous  # Previous crash

# Follow logs (tail)
kubectl logs -f <pod-name> -n production

# All pods for deployment
kubectl logs -l app=votraio-api -n production -f --tail=100

# Get shell access (debugging)
kubectl exec -it <pod-name> -n production -- bash

# Copy file from pod
kubectl cp production/<pod-name>:/app/file.txt ./file.txt
```

### Scaling

```bash
# Scale deployment
kubectl scale deployment votraio-api -n production --replicas=5

# View autoscaling
kubectl get hpa -n production
kubectl describe hpa votraio-api-hpa -n production
```

### Updates & Rollouts

```bash
# Check rollout status
kubectl rollout status deployment/votraio-api -n production

# Watch rollout
kubectl rollout status deployment/votraio-api -n production -w

# View rollout history
kubectl rollout history deployment/votraio-api -n production

# Rollback to previous version
kubectl rollout undo deployment/votraio-api -n production

# Rollback to specific revision
kubectl rollout undo deployment/votraio-api -n production --to-revision=2

# Set new image
kubectl set image deployment/votraio-api \
  app=gcr.io/votraio-prod/votraio-api:new-tag \
  -n production \
  --record
```

### Resource Management

```bash
# View resource usage
kubectl top nodes
kubectl top pods -n production

# View resource quotas
kubectl describe resourcequota -n production

# View resource requests/limits
kubectl describe nodes
```

### Secrets & Config

```bash
# View secrets (names only)
kubectl get secrets -n production

# View secret (decoded)
kubectl get secret db-credentials -n production -o jsonpath='{.data.password}' | base64 -d

# Update secret
kubectl create secret generic db-credentials \
  --from-literal=password=new-password \
  -n production \
  --dry-run=client -o yaml | kubectl apply -f -

# View configmap
kubectl get configmap votraio-config -n production -o yaml
```

---

## Database Operations

### PostgreSQL Access

```bash
# Connect to database
psql postgresql://votraio:password@localhost:5432/votraio_db

# Common commands
\dt                  # List tables
\d tablename         # Describe table
SELECT * FROM users; # Query
\q                   # Exit

# Backup database
pg_dump postgresql://user:pass@host/db > backup.sql

# Restore database
psql postgresql://user:pass@host/db < backup.sql
```

### Migrations

```bash
# Check current version
alembic current

# View migration history
alembic history

# Upgrade to head
alembic upgrade head

# Downgrade one revision
alembic downgrade -1

# Create migration
alembic revision --autogenerate -m "Add user table"
```

---

## GitHub Actions

### Trigger Workflow

```bash
# Push to add/fastapi (auto-deploy to dev)
git push origin add/fastapi

# Push to main (builds, awaits approval for prod)
git push origin main

# Manual workflow trigger
gh workflow run gcloud-deploy.yml -r add/fastapi
```

### Monitor Workflow

```bash
# View workflow runs
gh run list --workflow gcloud-deploy.yml

# View specific run details
gh run view <run-id> --log

# Cancel running workflow
gh run cancel <run-id>

# Re-run failed jobs
gh run rerun <run-id>
```

### Approve Deployment

```bash
# List pending deployments
gh deployment-status --environment production

# Approve via GitHub CLI
gh workflow run gcloud-deploy.yml -r main --ref main
# Then manually approve in GitHub UI
```

---

## Docker Registry (GCR)

### Image Operations

```bash
# List images
gcloud container images list --project votraio-prod

# List image tags
gcloud container images list-tags gcr.io/votraio-prod/votraio-api

# Inspect image
gcloud container images describe gcr.io/votraio-prod/votraio-api:latest

# Delete image
gcloud container images delete gcr.io/votraio-prod/votraio-api:old-tag

# Scan image for vulnerabilities
trivy image gcr.io/votraio-prod/votraio-api:latest
```

### Push Image Manually

```bash
# Build image
docker build -t votraio-api:test .

# Tag for GCR
docker tag votraio-api:test gcr.io/votraio-prod/votraio-api:test

# Authenticate (if needed)
gcloud auth configure-docker

# Push image
docker push gcr.io/votraio-prod/votraio-api:test
```

---

## Monitoring & Alerts

### View Metrics

```bash
# Pod CPU/Memory
kubectl top pods -n production

# Node CPU/Memory
kubectl top nodes

# Deployment status
kubectl get deployment votraio-api -n production -w

# Service endpoints
kubectl get svc votraio-api -n production -o wide
```

### Check Health

```bash
# Health check endpoint
curl http://localhost:8000/api/v1/health

# Database connectivity
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -- \
  psql postgresql://user:pass@db-service:5432/votraio_db -c "SELECT 1"

# API availability
kubectl get endpoints votraio-api -n production
```

### View Logs in GCP

```bash
# Recent logs
gcloud logging read "resource.type=k8s_container" --limit 50

# By namespace
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=production"

# By severity
gcloud logging read "resource.type=k8s_container AND severity=ERROR"

# Stream logs
gcloud logging read --stream
```

---

## Troubleshooting

### Pod Issues

```bash
# Pod stuck in pending
kubectl describe pod <pod-name> -n production
# Check: resource requests, node capacity, PVC availability

# Pod keeps restarting
kubectl logs <pod-name> -n production --previous
# Check logs from previous run for error messages

# Pod not ready
kubectl describe pod <pod-name> -n production
# Check: readiness probe, liveness probe, resource limits
```

### Deployment Issues

```bash
# Stuck rollout
kubectl rollout status deployment/votraio-api -n production

# Immediate rollback
kubectl rollout undo deployment/votraio-api -n production

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'
```

### Database Issues

```bash
# Check connections
psql -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# Kill hanging connections
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='votraio_db';"

# Check locks
psql -c "SELECT * FROM pg_locks WHERE NOT granted;"
```

### Network Issues

```bash
# DNS test
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup votraio-api

# Port connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- http://votraio-api:8000/health

# Check network policies
kubectl get networkpolicies -n production
```

---

## Maintenance Tasks

### Daily

- [ ] Monitor error rates in logs
- [ ] Check pod health status
- [ ] Verify backups completed
- [ ] Review resource usage

### Weekly

- [ ] Check cluster node health
- [ ] Review security alerts
- [ ] Analyze performance metrics
- [ ] Test disaster recovery procedures

### Monthly

- [ ] Update dependencies
- [ ] Review and rotate secrets
- [ ] Security audit of cluster
- [ ] Cost analysis and optimization
- [ ] Test backup restoration

### Quarterly

- [ ] Update OS images
- [ ] Update Kubernetes version
- [ ] Security penetration testing
- [ ] Disaster recovery drill

---

## Cost Optimization

### Current Costs (Estimate)

```bash
# View GCP project costs
gcloud billing accounts list
gcloud billing budgets list

# Check resource usage
kubectl top nodes
kubectl top pods -n production
```

### Reduce Costs

```bash
# Use preemptible nodes (dev only)
gcloud container node-pools create preemptible \
  --cluster votraio-production \
  --preemptible \
  --num-nodes 1

# Use committed use discounts
gcloud compute reservations create votraio-reservation \
  --zone=us-central1-a \
  --machine-type=n1-standard-2 \
  --resource-status=COMMITTED
```

---

## Quick Command Reference

| Task | Command |
|------|---------|
| Deploy locally | `docker-compose up -d` |
| Access API | `curl http://localhost:8000/docs` |
| Check logs | `docker-compose logs -f api` |
| Stop services | `docker-compose down` |
| Get cluster creds | `gcloud container clusters get-credentials votraio-production --zone us-central1-a` |
| View pods | `kubectl get pods -n production` |
| View logs | `kubectl logs -f <pod> -n production` |
| Trigger workflow | `git push origin add/fastapi` (dev) or `main` (prod) |
| Check deployment | `kubectl rollout status deployment/votraio-api -n production` |
| Rollback | `kubectl rollout undo deployment/votraio-api -n production` |
| Scale pods | `kubectl scale deployment votraio-api -n production --replicas=5` |
| Monitor resources | `kubectl top nodes && kubectl top pods -n production` |

---

## Emergency Procedures

### Service Down

1. Check pod status: `kubectl get pods -n production`
2. View logs: `kubectl logs -f deployment/votraio-api -n production`
3. Check events: `kubectl get events -n production`
4. Immediate rollback: `kubectl rollout undo deployment/votraio-api -n production`
5. Notify stakeholders via Slack

### Database Down

1. Check PostgreSQL pod: `kubectl describe pod postgres-0 -n production`
2. Check volume: `kubectl describe pvc postgres-pvc -n production`
3. View database logs: `kubectl logs postgres-0 -n production`
4. Restore from backup if needed

### High Resource Usage

1. Check top pods: `kubectl top pods -n production --sort-by=memory`
2. Check for memory leaks: Monitor over time
3. Scale up: `kubectl scale deployment votraio-api -n production --replicas=5`
4. Kill problematic pods: `kubectl delete pod <pod-name> -n production`

### Unauthorized Access

1. Check audit logs: `gcloud logging read "severity=WARNING"`
2. Review recent changes: `git log --oneline | head -20`
3. Rotate secrets: See "Secrets & Config" section
4. Notify security team
