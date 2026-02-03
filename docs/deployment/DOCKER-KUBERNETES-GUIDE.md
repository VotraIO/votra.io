# Docker & Kubernetes Deployment Guide

## Overview

This guide covers deploying VotraIO to production using Docker, Kubernetes, and Google Cloud. The setup follows industry best practices for security, scalability, and observability.

## Table of Contents

1. [Docker Best Practices](#docker-best-practices)
2. [Local Development with Docker Compose](#local-development-with-docker-compose)
3. [Google Cloud Setup](#google-cloud-setup)
4. [GitHub Actions Workflow](#github-actions-workflow)
5. [Troubleshooting](#troubleshooting)
6. [Security Considerations](#security-considerations)

---

## Docker Best Practices

### Why Multi-Stage Builds?

The `Dockerfile` uses a multi-stage build pattern:

**Stage 1: Builder**
- Includes all build tools (gcc, pip, setuptools)
- Compiles Python dependencies
- Creates isolated virtual environment
- Discarded after build

**Stage 2: Runtime**
- Minimal Python image (11-slim = 124MB)
- Only runtime dependencies (curl, postgresql-client)
- Copies pre-built virtual environment
- Final image size: ~250MB (vs ~500MB+ without multi-stage)

### Security Features

✅ **Non-Root User**
```bash
# Application runs as 'appuser' (UID 1000)
# Prevents privilege escalation attacks
USER appuser
```

✅ **Health Checks**
```bash
# Container automatically restarts if unhealthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3
```

✅ **Signal Handling**
```bash
# FastAPI with Uvicorn handles SIGTERM for graceful shutdown
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

✅ **Minimal Attack Surface**
- No shell (CMD format avoids /bin/sh)
- No SSH/debugging tools in image
- Read-only root filesystem support

### .dockerignore Optimization

Excludes 70+ file patterns:
- Source control (.git, .gitignore)
- Python caches (__pycache__, .pytest_cache)
- Virtual environments (venv/, .venv)
- Test files and coverage reports
- IDE configurations (.vscode, .idea)
- CI/CD files (.github, .gitlab-ci.yml)

**Impact**: Reduces build context from ~150MB to ~5MB

---

## Local Development with Docker Compose

### Quick Start

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# View logs
docker-compose logs -f api

# Access services
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Services Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐   │
│  │   FastAPI    │───→│ PostgreSQL   │    │   Redis    │   │
│  │   (8000)     │    │   (5432)     │    │  (6379)    │   │
│  └──────────────┘    └──────────────┘    └────────────┘   │
│       │                    │ (volumes)        │             │
│       └────────────────────┴──────────────────┘             │
│       localhost:8000, 5432, 6379                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Environment Variables

Create `.env` file:

```bash
# Database Configuration
DB_USER=votraio
DB_PASSWORD=votraio_dev_password  # Change in production!
DB_NAME=votraio_db

# Application
SECRET_KEY=your-secret-key-here-32-characters-minimum
ENVIRONMENT=development
LOG_LEVEL=INFO

# Redis
REDIS_URL=redis://redis:6379/0
```

### Common Tasks

**Run database migrations:**
```bash
docker-compose exec api alembic upgrade head
```

**Create migration:**
```bash
docker-compose exec api alembic revision --autogenerate -m "Add new field"
```

**Run tests:**
```bash
docker-compose exec api pytest --cov=app
```

**Access PostgreSQL:**
```bash
docker-compose exec db psql -U votraio -d votraio_db
```

**View API logs:**
```bash
docker-compose logs -f api --tail=100
```

**Restart services:**
```bash
docker-compose restart

# Or specific service
docker-compose restart db
```

**Clean up:**
```bash
# Stop containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove all
docker-compose down -v --remove-orphans
```

---

## Google Cloud Setup

### Prerequisites

1. **GCP Project**
   ```bash
   gcloud projects create votraio-prod --name="VotraIO Production"
   gcloud config set project votraio-prod
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable \
     container.googleapis.com \
     containerregistry.googleapis.com \
     artifactregistry.googleapis.com \
     cloudkms.googleapis.com \
     cloudbuild.googleapis.com
   ```

3. **Create GKE Cluster**
   ```bash
   gcloud container clusters create votraio-production \
     --zone us-central1-a \
     --num-nodes 3 \
     --machine-type n1-standard-2 \
     --enable-autoscaling \
     --min-nodes 2 \
     --max-nodes 10 \
     --enable-ip-alias \
     --enable-stackdriver-kubernetes \
     --enable-network-policy \
     --network "default"
   ```

4. **Create Service Account for Deployment**
   ```bash
   # Create service account
   gcloud iam service-accounts create github-deployment \
     --display-name="GitHub Deployment Service Account"
   
   # Grant permissions
   gcloud projects add-iam-policy-binding votraio-prod \
     --member="serviceAccount:github-deployment@votraio-prod.iam.gserviceaccount.com" \
     --role="roles/container.developer"
   
   gcloud projects add-iam-policy-binding votraio-prod \
     --member="serviceAccount:github-deployment@votraio-prod.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   ```

5. **Set Up Workload Identity (Recommended)**
   ```bash
   # Create workload identity pool
   gcloud iam workload-identity-pools create github \
     --project="votraio-prod" \
     --location="global" \
     --display-name="GitHub Actions"
   
   # Create provider
   gcloud iam workload-identity-pools providers create-oidc github \
     --project="votraio-prod" \
     --location="global" \
     --workload-identity-pool="github" \
     --display-name="GitHub Actions" \
     --attribute-mapping="google.subject=assertion.sub,assertion.aud=assertion.aud" \
     --issuer-uri="https://token.actions.githubusercontent.com"
   
   # Allow GitHub to impersonate service account
   gcloud iam service-accounts add-iam-policy-binding \
     github-deployment@votraio-prod.iam.gserviceaccount.com \
     --project="votraio-prod" \
     --role="roles/iam.workloadIdentityUser" \
     --member="principalSet://iam.googleapis.com/projects/votraio-prod/locations/global/workloadIdentityPools/github/attribute.repository/VotraIO/votra.io"
   ```

### Create Namespaces

```bash
# Get credentials
gcloud container clusters get-credentials votraio-production \
  --zone us-central1-a \
  --project votraio-prod

# Create namespaces
kubectl create namespace development
kubectl create namespace production

# Label namespaces
kubectl label namespace development environment=dev
kubectl label namespace production environment=prod
```

### Create Kubernetes Secrets

```bash
# Database credentials
kubectl create secret generic db-credentials \
  --from-literal=username=votraio \
  --from-literal=password=your-secure-password \
  --namespace=production

# API secret key
kubectl create secret generic app-secrets \
  --from-literal=secret-key=$(openssl rand -hex 32) \
  --namespace=production

# Docker credentials (if using private registry)
kubectl create secret docker-registry gcr-json-key \
  --docker-server=gcr.io \
  --docker-username=_json_key \
  --docker-password="$(cat ~/key.json)" \
  --namespace=production
```

---

## GitHub Actions Workflow

### Setup GitHub Secrets

In repository settings, add these secrets:

| Secret | Value | Purpose |
|--------|-------|---------|
| `GCP_PROJECT_ID` | votraio-prod | GCP project ID |
| `WIF_PROVIDER` | Workload Identity Provider URL | Authentication |
| `WIF_SERVICE_ACCOUNT` | Service account email | Deployment permissions |
| `SLACK_WEBHOOK_URL` | Slack webhook (optional) | Deployment notifications |

### Workflow Triggers

The workflow automatically runs on:

1. **Push to `main` branch**
   - Runs quality checks
   - Builds Docker image
   - **Manual approval required** for production deployment

2. **Push to `add/fastapi` branch**
   - Runs quality checks
   - Builds Docker image
   - Automatically deploys to development

3. **Pull Requests to `main` or `add/fastapi`**
   - Runs quality checks only
   - Requires checks to pass before merge

### Workflow Stages

#### 1. Quality Checks
- ✅ Run pytest with 80% coverage requirement
- ✅ Lint with ruff
- ✅ Type check with mypy
- ✅ Format check with black
- ✅ Security scan with bandit
- ✅ Dependency check with safety

#### 2. Build Docker Image
- Builds multi-stage Docker image
- Pushes to Google Container Registry
- Scans image with Trivy for vulnerabilities
- Tags with commit hash and timestamp

#### 3. Deploy to Development
- Automatic on `add/fastapi` push
- Blue-green deployment to dev namespace
- Runs health checks
- Automatic rollback on failure

#### 4. Deploy to Production
- **Manual approval required** on `main` push
- Blue-green deployment to prod namespace
- 10-minute timeout for rollout
- Automatic rollback on failure

#### 5. Notifications
- Sends Slack notification on completion
- Includes deployment status, commit info, links

### Manual Deployment Approval

1. Go to GitHub Actions workflow run
2. Click "Review deployments"
3. Select "production" environment
4. Click "Approve and deploy"
5. Monitor deployment logs

---

## Troubleshooting

### Docker Issues

**Container won't start:**
```bash
# Check logs
docker logs <container-id>

# Inspect image
docker inspect <image-id>

# Rebuild without cache
docker-compose build --no-cache
```

**Permission denied:**
```bash
# Check user
docker exec <container> id

# Verify .dockerignore doesn't exclude necessary files
cat .dockerignore
```

**Port already in use:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <pid>

# Or use different port
docker-compose up -p <different-port>:8000
```

### Kubernetes Issues

**Pod won't start:**
```bash
# Check pod status
kubectl describe pod <pod-name> -n production

# Check logs
kubectl logs <pod-name> -n production

# Check events
kubectl get events -n production
```

**Deployment stuck:**
```bash
# Check rollout status
kubectl rollout status deployment/votraio-api -n production

# Force rollback
kubectl rollout undo deployment/votraio-api -n production
```

**Database connection issues:**
```bash
# Test connection
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -- \
  psql postgresql://user:password@db-service:5432/dbname
```

### Workflow Issues

**Workflow won't run:**
- Check branch name matches trigger (main/add/fastapi)
- Check commit message doesn't contain [skip ci]
- Verify secrets are set correctly

**Build failures:**
```bash
# Re-run workflow with debug logs
# Click "Re-run job" and select "Re-run jobs with debug logging"
```

**Deployment failures:**
- Check Pod events: `kubectl describe pod <pod>`
- Check resource limits: `kubectl top nodes`
- Check image pull errors: `kubectl get events`

---

## Security Considerations

### Image Security

✅ **Scan images for vulnerabilities**
```bash
# Local scan
trivy image <image-name>

# Automated via GitHub Actions (included in workflow)
```

✅ **Sign images** (optional)
```bash
# Enable image signing in GCP
gcloud beta container binauthz policy import policy.yaml
```

### Runtime Security

✅ **Network policies**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

✅ **Pod security policies**
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: votraio-api
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: votraio-api
```

### Secret Management

✅ **Use Google Secret Manager**
```bash
# Store secrets securely
echo -n "password" | gcloud secrets create db-password --data-file=-

# Reference in deployments
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-password
      key: password
```

✅ **Rotate secrets regularly**
```bash
# Set expiration
gcloud secrets versions destroy 0 --secret db-password
```

### Compliance

✅ **Audit logging**
- All deployments logged in GKE audit logs
- Database audit table tracks all changes
- GitHub Actions logs track all deployment decisions

✅ **HIPAA/SOC2 (if applicable)**
- Encryption at rest (Google KMS)
- Encryption in transit (TLS 1.3)
- Immutable audit logs
- Regular security scans

---

## Performance Tuning

### Database Performance

```yaml
# In docker-compose.yml
command:
  - "postgres"
  - "-c"
  - "shared_buffers=256MB"  # 25% of available RAM
  - "-c"
  - "effective_cache_size=1GB"  # 50-75% of available RAM
  - "-c"
  - "work_mem=4MB"  # shared_buffers / max_connections
  - "-c"
  - "maintenance_work_mem=64MB"  # 10% of available RAM
```

### Container Resources

```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 512M
    reservations:
      cpus: '0.5'
      memory: 256M
```

### Health Check Optimization

Adjust intervals based on workload:
```yaml
healthcheck:
  interval: 10s      # Check every 10s
  timeout: 5s        # Wait 5s for response
  retries: 3         # Fail after 3 consecutive failures
  start_period: 30s  # Grace period for startup
```

---

## Monitoring & Logging

### Enable Google Cloud Logging

```bash
# Create log sink
gcloud logging sinks create kubernetes-logs \
  logging.googleapis.com/projects/votraio-prod/logs/kubernetes \
  --log-filter='resource.type="k8s_container"'
```

### View Logs

```bash
# Pod logs
kubectl logs <pod-name> -n production -f

# All logs in namespace
kubectl logs -l app=votraio-api -n production -f --tail=100

# GCP logs
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=production"
```

### Health Monitoring

```bash
# Check cluster health
gcloud container clusters describe votraio-production --zone us-central1-a

# Check node health
kubectl get nodes
kubectl top nodes

# Check pod health
kubectl get pods -n production
kubectl top pods -n production
```

---

## Cost Optimization

### Cluster Cost

| Component | Recommendation | Impact |
|-----------|-----------------|---------|
| Node size | n1-standard-2 | Balanced CPU/memory |
| Autoscaling | 2-10 nodes | Scales with demand |
| Preemptible VMs | For non-critical workloads | 60-80% cost savings |
| Reserved Instances | For baseline capacity | 25-40% discounts |

### Storage Cost

- Use SSD for databases (faster, only 2-3x cost)
- Archive old logs after 30 days
- Use Coldline Storage for backups

### Bandwidth Cost

- Use private clusters (VPC-only)
- Use Google Cloud CDN for static assets
- Monitor egress bandwidth

---

## Next Steps

1. **Set up monitoring dashboard** in GCP
2. **Configure backup automation** for databases
3. **Set up disaster recovery** procedures
4. **Create runbooks** for common operations
5. **Schedule security audit** of cluster
6. **Test disaster recovery** procedures

---

## References

- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
- [Google Cloud GKE](https://cloud.google.com/kubernetes-engine/docs)
- [GitHub Actions](https://docs.github.com/en/actions)
