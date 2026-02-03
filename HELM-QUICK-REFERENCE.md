# Votra.io Helm Chart - Quick Reference Guide

## 📋 One-Liner Deployments

### Development
```bash
helm install votraio helmchart/votra-io/ -f helmchart/votra-io/values-dev.yaml
```

### Staging
```bash
helm install votraio helmchart/votra-io/ -f helmchart/votra-io/values-staging.yaml
```

### Production (GCP with DNS Automation)
```bash
helm install votraio helmchart/votra-io/ -f helmchart/votra-io/values-prod.yaml \
  --set publicIP.gcp.enabled=true \
  --set publicIP.gcp.projectId=YOUR_GCP_PROJECT \
  --set dns.gcp.enabled=true
```

### Production (AWS)
```bash
helm install votraio helmchart/votra-io/ -f helmchart/votra-io/values-prod.yaml \
  --set publicIP.aws.enabled=true \
  --set publicIP.aws.region=us-west-2
```

### Production (Azure)
```bash
helm install votraio helmchart/votra-io/ -f helmchart/votra-io/values-prod.yaml \
  --set publicIP.azure.enabled=true \
  --set publicIP.azure.resourceGroup=my-rg
```

---

## 🔍 Essential Kubectl Commands

### Check Deployment Status
```bash
kubectl get all -l app.kubernetes.io/instance=votraio
kubectl get deployment votraio-api
kubectl get pods -l app.kubernetes.io/name=votra-io
```

### View Logs
```bash
# Real-time API logs
kubectl logs -f deployment/votraio-api

# DNS sync logs (GCP)
kubectl logs -f -l app.kubernetes.io/component=dns-sync

# Previous pod logs
kubectl logs deployment/votraio-api --previous
```

### Access Database
```bash
# PostgreSQL
kubectl exec -it svc/votraio-postgresql -- \
  psql -U votraio -d votraio_db

# Redis
kubectl exec -it svc/votraio-redis-master -- redis-cli
```

### Port Forward
```bash
# Forward to API
kubectl port-forward svc/votraio-api 8000:8000

# Access API docs
open http://localhost:8000/docs
```

---

## 📊 Monitoring Commands

### Pod Metrics
```bash
# CPU and Memory usage
kubectl top pods -l app.kubernetes.io/name=votra-io

# Node resource usage
kubectl top nodes
```

### Check Autoscaling
```bash
# Watch HPA status
kubectl get hpa votraio-api -w

# Get current replicas
kubectl get deployment votraio-api
```

### View Events
```bash
# Recent cluster events
kubectl get events --sort-by='.lastTimestamp'

# Pod-specific events
kubectl describe pod <pod-name>
```

---

## 🔐 Secrets Management

### Create Required Secrets
```bash
# App secrets
kubectl create secret generic votraio-app-secrets \
  --from-literal=SECRET_KEY=$(openssl rand -hex 16) \
  --from-literal=ALGORITHM='HS256' \
  --from-literal=ACCESS_TOKEN_EXPIRE_MINUTES='30' \
  --from-literal=REFRESH_TOKEN_EXPIRE_DAYS='7'

# Database credentials
kubectl create secret generic votraio-db-credentials \
  --from-literal=DATABASE_PASSWORD='secure-password'

# Redis credentials
kubectl create secret generic votraio-redis \
  --from-literal=REDIS_PASSWORD='secure-redis-password'
```

### View Secrets
```bash
kubectl get secrets -o wide
kubectl describe secret votraio-app-secrets
```

---

## 🔄 Helm Operations

### Upgrade Deployment
```bash
helm upgrade votraio helmchart/votra-io/ \
  -f helmchart/votra-io/values-prod.yaml
```

### View Release History
```bash
helm history votraio
helm history votraio --max 10
```

### Rollback to Previous Release
```bash
helm rollback votraio 1
helm rollback votraio 0  # Rollback previous change
```

### Dry-Run (Preview Changes)
```bash
helm install votraio helmchart/votra-io/ \
  -f helmchart/votra-io/values-prod.yaml \
  --dry-run --debug
```

### Get Release Values
```bash
helm get values votraio
helm get manifest votraio
```

### Delete Release
```bash
helm uninstall votraio
```

---

## 🚀 Deployment Scenarios

### Enable GCP Public IP
```bash
helm upgrade votraio helmchart/votra-io/ \
  --set publicIP.enabled=true \
  --set publicIP.gcp.enabled=true
```

### Enable DNS Automation (GCP)
```bash
helm upgrade votraio helmchart/votra-io/ \
  --set dns.gcp.enabled=true \
  --set dns.gcp.projectId=your-project
```

### Scale to 10 Replicas
```bash
helm upgrade votraio helmchart/votra-io/ \
  --set api.replicaCount=10 \
  --set api.autoscaling.enabled=false
```

### Update to New Image
```bash
helm upgrade votraio helmchart/votra-io/ \
  --set api.image.tag=v1.2.0
```

### Increase Resource Limits
```bash
helm upgrade votraio helmchart/votra-io/ \
  --set api.resources.limits.cpu=1000m \
  --set api.resources.limits.memory=1Gi
```

### Enable All Monitoring
```bash
helm upgrade votraio helmchart/votra-io/ \
  --set monitoring.enabled=true \
  --set monitoring.prometheus.enabled=true
```

---

## 🐛 Troubleshooting

### Pod Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name>

# View recent errors
kubectl logs <pod-name> --tail=100

# Check resource constraints
kubectl describe node <node-name>
```

### Database Connection Issues
```bash
# Test PostgreSQL connectivity
kubectl run -it --rm test --image=postgres --restart=Never -- \
  psql -h votraio-postgresql -U votraio -d votraio_db -c "SELECT 1"

# Check database pod logs
kubectl logs sts/votraio-postgresql-0
```

### Ingress Not Working
```bash
# Check ingress status
kubectl get ingress
kubectl describe ingress votraio

# Test DNS resolution
kubectl run -it --rm test --image=busybox --restart=Never -- \
  nslookup api.votra.io

# Test HTTP connectivity
kubectl run -it --rm test --image=curlimages/curl --restart=Never -- \
  curl -v http://votraio-api:8000/health
```

### DNS Sync Not Working (GCP)
```bash
# Check CronJob status
kubectl get cronjob
kubectl get jobs

# View DNS sync pod logs
kubectl logs -f -l app.kubernetes.io/component=dns-sync

# Check GCP service account permissions
gcloud iam service-accounts list
gcloud projects get-iam-policy YOUR_PROJECT
```

---

## 📈 Performance Tuning

### Increase Replicas for Load Testing
```bash
kubectl scale deployment votraio-api --replicas=5
```

### Watch Autoscaling
```bash
watch kubectl get hpa
```

### Monitor Response Times
```bash
kubectl logs -f deployment/votraio-api | grep "response_time"
```

### Check Database Query Performance
```bash
kubectl exec -it svc/votraio-postgresql -- \
  psql -U votraio -d votraio_db \
  -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

---

## 🔒 Security Checks

### Verify Pod Security Context
```bash
kubectl get pod -o jsonpath='{.items[].spec.securityContext}' | jq .
```

### Check RBAC Permissions
```bash
kubectl get rolebindings,clusterrolebindings -o wide
kubectl describe role votraio
```

### Verify Network Policies
```bash
kubectl get networkpolicies
kubectl describe networkpolicy votraio
```

### Audit Secrets Access (GCP)
```bash
gcloud logging read "resource.type=service_account AND protoPayload.resourceName=~secretmanager"
```

---

## 📝 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Pod CrashLoopBackOff | Check logs: `kubectl logs <pod>` |
| Database connection failed | Verify secrets exist: `kubectl get secrets` |
| DNS not updating (GCP) | Check CronJob: `kubectl get cronjob` |
| Out of resources | Add nodes or reduce replicas |
| High memory usage | Increase memory limits or add replicas |
| Slow response times | Check metrics: `kubectl top pods` |
| Ingress IP pending | Wait 2-3 min or check ingress controller |
| Certificate not issued | Check cert-manager: `kubectl describe cert` |

---

## 🔗 Useful Links

- **Kubernetes Docs:** https://kubernetes.io/docs
- **Helm Docs:** https://helm.sh/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **PostgreSQL Docs:** https://www.postgresql.org/docs
- **Redis Docs:** https://redis.io/documentation
- **GCP Cloud DNS:** https://cloud.google.com/dns/docs
- **AWS NLB:** https://docs.aws.amazon.com/elasticloadbalancing
- **Azure Public IP:** https://docs.microsoft.com/en-us/azure/virtual-network/public-ip-addresses

---

## 📞 Emergency Procedures

### Emergency Rollback
```bash
# Immediate rollback to last known good
helm rollback votraio

# Force pod restart
kubectl delete pod -l app.kubernetes.io/name=votra-io

# Scale down during incident
kubectl scale deployment votraio-api --replicas=0
```

### Emergency Scale Up
```bash
# Quickly add replicas
kubectl scale deployment votraio-api --replicas=10

# Force pod rescheduling
kubectl delete pod <pod-name>
```

### Emergency Logs Collection
```bash
# Collect all pod logs
kubectl logs -l app.kubernetes.io/name=votra-io --all-containers=true > logs.txt

# Collect events
kubectl get events --sort-by='.lastTimestamp' > events.txt

# Describe all resources
kubectl describe all > resources.txt
```

---

**Last Updated:** 2024
**Helm Chart Version:** 1.0.0
**Kubernetes Version:** 1.20+
