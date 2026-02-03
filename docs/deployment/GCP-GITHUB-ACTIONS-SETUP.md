# GitHub Actions Google Cloud Deployment Setup

## Overview

This guide walks through setting up the GitHub Actions workflow to deploy VotraIO to Google Cloud.

## Architecture

```
GitHub (Push)
    ↓
GitHub Actions (Workflow)
    ├─ Quality Checks (pytest, linting, security)
    ├─ Build Docker Image (multi-stage build)
    ├─ Push to Google Container Registry
    ├─ Image Vulnerability Scan (Trivy)
    ├─ Deploy to Development (auto on add/fastapi)
    ├─ Deploy to Production (manual approval on main)
    └─ Notify via Slack

Deployments:
    ├─ Development: Automatic
    │  ├─ Blue-green deployment
    │  ├─ Health checks
    │  └─ Auto-rollback on failure
    │
    └─ Production: Manual approval required
       ├─ Blue-green deployment  
       ├─ Health checks
       ├─ Automatic rollback on failure
       └─ Slack notification
```

## Prerequisites

### 1. Google Cloud Setup

#### Create GCP Project

```bash
gcloud projects create votraio-prod --name="VotraIO Production"
export GCP_PROJECT_ID=$(gcloud config get-value project)
echo $GCP_PROJECT_ID
```

#### Enable Required APIs

```bash
gcloud services enable \
  container.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  cloudkms.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com
```

#### Create GKE Cluster

```bash
gcloud container clusters create votraio-production \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10 \
  --enable-stackdriver-kubernetes \
  --enable-network-policy
```

**Cost**: ~$80-150/month for 3x n1-standard-2 nodes (adjust as needed)

### 2. Service Account Setup

#### Create Service Account

```bash
gcloud iam service-accounts create github-deployment \
  --display-name="GitHub Actions Deployment Service Account"

export SERVICE_ACCOUNT_EMAIL=github-deployment@${GCP_PROJECT_ID}.iam.gserviceaccount.com
echo $SERVICE_ACCOUNT_EMAIL
```

#### Grant Permissions

```bash
# Container permissions (deploy to GKE)
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/container.developer"

# Storage permissions (push/pull Docker images)
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/storage.admin"

# Artifact Registry permissions (if using Artifact Registry instead of GCR)
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/artifactregistry.writer"
```

#### Option A: Service Account Key (Not Recommended - Legacy)

⚠️ **Warning**: Service account keys are a security risk. Use Workload Identity (Option B) instead.

If you must use keys:

```bash
gcloud iam service-accounts keys create ~/gh-sa-key.json \
  --iam-account=${SERVICE_ACCOUNT_EMAIL}

# Add to GitHub Secrets as GCP_SA_KEY
cat ~/gh-sa-key.json | base64

# Clean up
rm ~/gh-sa-key.json
```

#### Option B: Workload Identity Federation (Recommended)

This is more secure and doesn't require storing credentials.

##### Create Workload Identity Pool

```bash
gcloud iam workload-identity-pools create github \
  --project=$GCP_PROJECT_ID \
  --location=global \
  --display-name="GitHub Actions"

export WIP_ID=$(gcloud iam workload-identity-pools describe github \
  --project=$GCP_PROJECT_ID \
  --location=global \
  --format='value(name)')

echo $WIP_ID
```

##### Create OIDC Provider

```bash
gcloud iam workload-identity-pools providers create-oidc github \
  --project=$GCP_PROJECT_ID \
  --location=global \
  --workload-identity-pool=github \
  --display-name="GitHub Provider" \
  --attribute-mapping='google.subject=assertion.sub,assertion.aud=assertion.aud' \
  --issuer-uri='https://token.actions.githubusercontent.com' \
  --attribute-condition="assertion.aud == '${GCP_PROJECT_ID}'"
```

##### Allow GitHub to Impersonate Service Account

```bash
# For all repos in VotraIO organization
gcloud iam service-accounts add-iam-policy-binding ${SERVICE_ACCOUNT_EMAIL} \
  --project=$GCP_PROJECT_ID \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/${GCP_PROJECT_ID}/locations/global/workloadIdentityPools/github/attribute.repository_owner/VotraIO"

# Or for specific repo only (more secure)
gcloud iam service-accounts add-iam-policy-binding ${SERVICE_ACCOUNT_EMAIL} \
  --project=$GCP_PROJECT_ID \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/${GCP_PROJECT_ID}/locations/global/workloadIdentityPools/github/attribute.repository/VotraIO/votra.io"
```

##### Get Provider Resource Name

```bash
export PROVIDER_ID=$(gcloud iam workload-identity-pools providers describe github \
  --project=$GCP_PROJECT_ID \
  --location=global \
  --workload-identity-pool=github \
  --format='value(name)')

echo $PROVIDER_ID
```

### 3. Kubernetes Setup

#### Create Namespaces

```bash
gcloud container clusters get-credentials votraio-production \
  --zone us-central1-a \
  --project=$GCP_PROJECT_ID

kubectl create namespace development
kubectl create namespace production

# Label namespaces
kubectl label namespace development environment=dev
kubectl label namespace production environment=prod
```

#### Create Secrets

```bash
# Database credentials (change passwords!)
kubectl create secret generic db-credentials \
  --from-literal=username=votraio \
  --from-literal=password=$(openssl rand -base64 32) \
  --namespace=production

# App secrets
kubectl create secret generic app-secrets \
  --from-literal=secret-key=$(openssl rand -hex 32) \
  --namespace=production

# Repeat for development namespace
kubectl create secret generic db-credentials \
  --from-literal=username=votraio \
  --from-literal=password=$(openssl rand -base64 32) \
  --namespace=development

kubectl create secret generic app-secrets \
  --from-literal=secret-key=$(openssl rand -hex 32) \
  --namespace=development
```

## GitHub Repository Setup

### 1. Add Secrets to Repository

Go to: **Repository Settings → Secrets and variables → Actions**

#### Using Workload Identity (Recommended):

| Secret Name | Value |
|-------------|-------|
| `GCP_PROJECT_ID` | Your project ID (e.g., `votraio-prod`) |
| `WIF_PROVIDER` | Output from `$PROVIDER_ID` above |
| `WIF_SERVICE_ACCOUNT` | Output from `$SERVICE_ACCOUNT_EMAIL` above |

#### Using Service Account Key (Legacy):

| Secret Name | Value |
|-------------|-------|
| `GCP_PROJECT_ID` | Your project ID |
| `GCP_SA_KEY` | Base64-encoded service account key |

### 2. Add Variables (Optional)

Go to: **Repository Settings → Secrets and variables → Variables**

| Variable | Value |
|----------|-------|
| `GKE_CLUSTER` | votraio-production |
| `GKE_ZONE` | us-central1-a |
| `IMAGE_NAME` | votraio-api |

### 3. Add Optional Slack Notifications

| Secret | Value |
|--------|-------|
| `SLACK_WEBHOOK_URL` | Your Slack webhook URL |

To create Slack webhook:
1. Go to https://api.slack.com/apps
2. Create new app → From scratch
3. Name: "VotraIO GitHub"
4. Add "Incoming Webhooks" feature
5. Copy webhook URL to GitHub secrets

## Workflow Verification

### Test the Workflow

1. Make a test commit to `add/fastapi` branch:
   ```bash
   git checkout add/fastapi
   git commit --allow-empty -m "test: trigger workflow"
   git push origin add/fastapi
   ```

2. Go to **Actions** tab in GitHub to watch workflow run

3. Check workflow output for:
   - ✅ Quality checks passed
   - ✅ Docker image built
   - ✅ Image pushed to GCR
   - ✅ Image scanned for vulnerabilities
   - ✅ Deployed to development

### Monitor Deployment

```bash
# Watch deployment status
kubectl rollout status deployment/votraio-api -n development

# Check pod logs
kubectl logs -f deployment/votraio-api -n development

# Get service endpoint
kubectl get service votraio-api -n development
```

### Verify in GCP

```bash
# Check image in registry
gcloud container images list --project=$GCP_PROJECT_ID

# Inspect image
gcloud container images describe gcr.io/${GCP_PROJECT_ID}/votraio-api:latest

# Check GKE deployment
gcloud container clusters describe votraio-production \
  --zone us-central1-a \
  --project=$GCP_PROJECT_ID
```

## Production Deployment

### When Ready for Production

1. Merge to `main` branch on GitHub
2. GitHub Actions automatically:
   - Runs quality checks
   - Builds image
   - Pushes to registry
   - **Waits for manual approval**
3. Go to Actions → Find workflow run → Click "Review deployments"
4. Select "production" → Click "Approve and deploy"
5. Monitor deployment in Actions tab

### Production Safeguards

✅ **Quality Gates**
- Must pass: tests, linting, security checks
- Code coverage minimum: 80%

✅ **Manual Approval**
- Production deployments require human review
- Deployment window: Business hours recommended

✅ **Health Checks**
- 30-second grace period for startup
- 10-second timeout for health endpoint
- Auto-rollback on health check failure

✅ **Resource Limits**
- CPU: 250m (request) / 500m (limit)
- Memory: 256Mi (request) / 512Mi (limit)
- Prevents resource exhaustion

✅ **Pod Disruption Budget**
- Minimum 2 pods always available
- Allows safe cluster updates

## Troubleshooting

### Workflow Fails on Quality Checks

Check output for:
- Test failures: Run locally with `pytest --cov=app`
- Lint errors: Run `ruff check app --fix` and commit
- Type errors: Run `mypy app --ignore-missing-imports`
- Coverage: Add tests to reach 80%

### Docker Build Fails

```bash
# Build locally to debug
docker build -t votraio-test .

# Check Dockerfile
docker inspect votraio-test
```

### Image Scan Vulnerabilities

```bash
# Scan locally
trivy image gcr.io/${GCP_PROJECT_ID}/votraio-api:latest

# Fix vulnerabilities
pip install --upgrade pip
pip list --outdated
pip install -U <package>
```

### Kubernetes Deployment Issues

```bash
# Check pod events
kubectl describe pod <pod-name> -n production

# Check logs
kubectl logs <pod-name> -n production

# Check image pull
kubectl get events -n production | grep "pull"

# Verify image exists
gcloud container images describe gcr.io/${GCP_PROJECT_ID}/votraio-api:latest
```

### Manual Rollback

If deployment fails after approval:

```bash
# Immediate rollback
kubectl rollout undo deployment/votraio-api -n production

# Wait for rollback
kubectl rollout status deployment/votraio-api -n production

# Verify rollback
kubectl get deployment votraio-api -n production -o jsonpath='{.spec.template.spec.containers[0].image}'
```

## Cost Monitoring

### Estimate Monthly Costs

| Service | Estimate |
|---------|----------|
| GKE Cluster (3 nodes) | $80-150 |
| Cloud Storage (images) | $5-10 |
| Network egress | $10-20 |
| Cloud Logging | $10-20 |
| **Total** | **~$100-200** |

### Reduce Costs

1. Use preemptible nodes for development (-60% cost)
2. Set autoscaling min-nodes=1 for dev, min-nodes=2 for prod
3. Use committed use discounts for production
4. Archive old container images

### Monitor Costs

```bash
# View GCP billing
gcloud billing accounts list
gcloud billing budgets list

# Set up cost alerts
gcloud billing budgets create \
  --billing-account=<ACCOUNT> \
  --display-name="VotraIO Monthly Budget" \
  --budget-amount=250 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Security Best Practices

✅ **Use Workload Identity** (not service account keys)
✅ **Enable audit logging** for all deployments
✅ **Scan images** for vulnerabilities (Trivy)
✅ **Use network policies** to restrict traffic
✅ **Set resource quotas** per namespace
✅ **Enable pod security policies**
✅ **Rotate secrets** monthly
✅ **Use separate namespaces** for dev/prod
✅ **Enable cluster logging** to GCP
✅ **Regular security audits** of cluster

## Next Steps

1. ✅ Complete setup above
2. Run initial workflow test
3. Monitor first production deployment
4. Set up uptime monitoring (Google Cloud Monitoring)
5. Create incident response runbook
6. Schedule monthly security audit
7. Plan disaster recovery testing

## Support & Documentation

- [Google Cloud GKE Docs](https://cloud.google.com/kubernetes-engine/docs)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Workload Identity Federation](https://cloud.google.com/docs/authentication/workload-identity-federation)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
