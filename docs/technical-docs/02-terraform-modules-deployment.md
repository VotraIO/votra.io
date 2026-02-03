# Terraform Module Reference and Deployment Automation

**Document Version:** 1.0.0  
**Last Updated:** February 2026  
**Target Audience:** DevOps Engineers, Infrastructure Architects  
**Related Document:** [Infrastructure-as-Code for Votra.io](./01-infrastructure-as-code.md)

---

## Table of Contents

1. [Module Structure](#module-structure)
2. [Reusable Terraform Modules](#reusable-terraform-modules)
3. [Environment-Specific Configurations](#environment-specific-configurations)
4. [Deployment Automation](#deployment-automation)
5. [Pre-Commit Validation](#pre-commit-validation)
6. [CI/CD Integration](#cicd-integration)

---

## Module Structure

### Directory Organization

```
terraform/
├── modules/
│   ├── gcp/
│   │   ├── vpc/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   └── locals.tf
│   │   ├── kubernetes/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   ├── node_pools.tf
│   │   │   └── workload_identity.tf
│   │   ├── database/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   ├── backups.tf
│   │   │   └── iam.tf
│   │   ├── cache/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── monitoring/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── alerts.tf
│   │   │   └── dashboards.tf
│   │   └── security/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── policies.tf
│   │
│   ├── aws/
│   │   ├── vpc/
│   │   ├── eks/
│   │   ├── rds/
│   │   ├── elasticache/
│   │   ├── monitoring/
│   │   └── security/
│   │
│   └── azure/
│       ├── vnet/
│       ├── aks/
│       ├── psql/
│       ├── redis/
│       ├── monitoring/
│       └── security/
│
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   ├── backend.tf
│   │   └── provider_overrides.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   ├── backend.tf
│   │   └── provider_overrides.tf
│   └── prod/
│       ├── main.tf
│       ├── terraform.tfvars
│       ├── backend.tf
│       └── provider_overrides.tf
│
├── scripts/
│   ├── validate.sh
│   ├── fmt.sh
│   ├── init.sh
│   ├── plan.sh
│   ├── apply.sh
│   ├── destroy.sh
│   └── rollback.sh
│
├── policies/
│   ├── cost_controls.sentinel
│   ├── security_policies.sentinel
│   ├── compliance_rules.sentinel
│   └── naming_conventions.sentinel
│
├── .terraformignore
├── .gitignore
├── .pre-commit-config.yaml
├── main.tf
├── variables.tf
├── outputs.tf
└── README.md
```

---

## Reusable Terraform Modules

### 1. GCP VPC Module

```hcl
# modules/gcp/vpc/main.tf

resource "google_compute_network" "main" {
  name                    = var.network_name
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"

  description = "VPC for ${var.environment}"
}

resource "google_compute_subnetwork" "kubernetes" {
  name          = "${var.network_name}-k8s"
  ip_cidr_range = var.kubernetes_subnet_cidr
  region        = var.region
  network       = google_compute_network.main.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_secondary_range
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_secondary_range
  }

  private_ip_google_access = true

  flow_logs_config {
    enable        = true
    sampling_rate = 0.5

    metadata = "INCLUDE_ALL_METADATA"
  }

  depends_on = [google_compute_network.main]
}

resource "google_compute_subnetwork" "databases" {
  name          = "${var.network_name}-db"
  ip_cidr_range = var.database_subnet_cidr
  region        = var.region
  network       = google_compute_network.main.id

  private_ip_google_access = true

  flow_logs_config {
    enable = true
  }

  depends_on = [google_compute_network.main]
}

resource "google_compute_firewall" "allow_internal" {
  name    = "${var.network_name}-allow-internal"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = [
    var.kubernetes_subnet_cidr,
    var.pods_secondary_range,
    var.services_secondary_range,
    var.database_subnet_cidr
  ]

  target_tags = ["kubernetes", "internal"]
}

resource "google_compute_firewall" "allow_ingress" {
  name    = "${var.network_name}-allow-ingress"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ingress"]
}

resource "google_compute_firewall" "allow_health_checks" {
  name    = "${var.network_name}-allow-health-checks"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
  }

  source_ranges = [
    "35.191.0.0/16",
    "130.211.0.0/22"
  ]
}

resource "google_compute_router" "main" {
  name    = "${var.network_name}-router"
  network = google_compute_network.main.id
  region  = var.region

  bgp {
    asn = 64514
  }
}

resource "google_compute_router_nat" "main" {
  name                               = "${var.network_name}-nat"
  router                             = google_compute_router.main.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# outputs.tf
output "network_id" {
  value       = google_compute_network.main.id
  description = "VPC network ID"
}

output "kubernetes_subnet_id" {
  value       = google_compute_subnetwork.kubernetes.id
  description = "Kubernetes subnet ID"
}

output "database_subnet_id" {
  value       = google_compute_subnetwork.databases.id
  description = "Database subnet ID"
}

# variables.tf
variable "network_name" {
  type        = string
  description = "Name of the VPC network"
}

variable "region" {
  type        = string
  description = "GCP region"
}

variable "kubernetes_subnet_cidr" {
  type        = string
  description = "CIDR range for Kubernetes subnet"
  default     = "10.1.0.0/20"
}

variable "pods_secondary_range" {
  type        = string
  description = "Secondary CIDR for pod IPs"
  default     = "10.4.0.0/14"
}

variable "services_secondary_range" {
  type        = string
  description = "Secondary CIDR for service IPs"
  default     = "10.0.0.0/16"
}

variable "database_subnet_cidr" {
  type        = string
  description = "CIDR range for database subnet"
  default     = "10.2.0.0/20"
}

variable "environment" {
  type        = string
  description = "Environment name"
}
```

### 2. GKE Cluster Module

```hcl
# modules/gcp/kubernetes/main.tf

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region

  # Disable default node pool
  remove_default_node_pool = true
  initial_node_count       = 1

  # Networking
  network    = var.vpc_network_id
  subnetwork = var.subnet_id

  # Version management
  min_master_version = var.kubernetes_version
  release_channel {
    channel = "REGULAR"
  }

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Security
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = var.authorized_networks_cidr
      display_name = "Admin Network"
    }
  }

  # IP allocation
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Network policy
  network_policy {
    enabled = true
  }

  addons_config {
    network_policy_config {
      disabled = false
    }
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
  }

  # Logging and monitoring
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS", "API_SERVER"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS", "POD_MONITORING", "DEPLOYMENT_MONITORING"]
    managed_prometheus {
      enabled = true
    }
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = var.maintenance_window_start
    }
  }

  # Cluster resource labels
  resource_labels = merge(
    var.labels,
    {
      cluster-name = var.cluster_name
    }
  )

  # Deletion protection
  deletion_protection = var.deletion_protection
}

resource "google_container_node_pool" "primary_nodes" {
  name           = "${var.cluster_name}-pool"
  cluster        = google_container_cluster.primary.id
  node_count     = var.node_pool_initial_size
  location       = var.region

  autoscaling {
    min_node_count = var.node_pool_min_size
    max_node_count = var.node_pool_max_size
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    preemptible  = var.enable_preemptible_nodes
    machine_type = var.machine_type
    disk_size_gb = var.disk_size_gb
    disk_type    = "pd-ssd"

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = merge(
      var.labels,
      {
        pool = "primary"
      }
    )

    tags = ["gke-node", var.cluster_name]

    metadata = {
      disable-legacy-endpoints = "true"
    }

    reservation_affinity {
      consume_reservation_type = "NO_RESERVATION"
    }
  }

  lifecycle {
    ignore_changes = [
      node_config[0].machine_type
    ]
  }
}

# Service Account for Kubernetes workloads
resource "google_service_account" "kubernetes" {
  account_id   = "${var.cluster_name}-ksa"
  display_name = "Kubernetes service account"
}

# Workload Identity binding
resource "google_service_account_iam_binding" "kubernetes_workload_identity" {
  service_account_id = google_service_account.kubernetes.name
  role               = "roles/iam.workloadIdentityUser"
  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[default/default]"
  ]
}
```

### 3. PostgreSQL Database Module

```hcl
# modules/gcp/database/main.tf

resource "google_sql_database_instance" "postgres" {
  name             = var.instance_name
  database_version = "POSTGRES_${var.postgres_version}"
  region           = var.region
  
  # Deletion protection
  deletion_protection = var.deletion_protection

  settings {
    tier              = var.instance_tier
    availability_type = "REGIONAL"
    disk_type         = "PD_SSD"
    disk_size         = var.disk_size

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      
      backup_retention_settings {
        retained_backups = var.backup_retained_count
        retention_unit   = "COUNT"
      }
    }

    ip_configuration {
      ipv4_enabled                                  = var.enable_public_ip
      private_network                               = var.private_network_id
      enable_private_path_for_cloudsql_cloud_sql    = true
      require_ssl                                   = true
      
      authorized_networks {
        name  = "kubernetes"
        value = var.kubernetes_network_cidr
      }
    }

    database_flags {
      name  = "cloudsql_iam_authentication"
      value = "on"
    }

    database_flags {
      name  = "max_connections"
      value = var.max_connections
    }

    database_flags {
      name  = "log_statement"
      value = "DDL"
    }

    database_flags {
      name  = "log_min_duration_statement"
      value = var.log_min_duration
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
      query_plans_per_minute  = 5
    }

    user_labels = var.labels
  }
}

resource "google_sql_database" "main" {
  name     = var.database_name
  instance = google_sql_database_instance.postgres.name
  charset  = "UTF8"
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "google_sql_user" "app" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result

  deletion_protection = true
}

# Store password in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${var.instance_name}-password"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# Grant Kubernetes service account access to secret
resource "google_secret_manager_iam_binding" "db_password" {
  secret_id = google_secret_manager_secret.db_password.id
  role      = "roles/secretmanager.secretAccessor"
  members = [
    "serviceAccount:${var.kubernetes_sa_email}"
  ]
}

# Connection string secret
resource "google_secret_manager_secret" "db_connection_string" {
  secret_id = "${var.instance_name}-connection-string"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "db_connection_string" {
  secret      = google_secret_manager_secret.db_connection_string.id
  secret_data = "postgresql://${var.db_user}:${random_password.db_password.result}@${google_sql_database_instance.postgres.private_ip_address}:5432/${var.database_name}"
}
```

---

## Environment-Specific Configurations

### Development Environment

```hcl
# environments/dev/terraform.tfvars

# Project/Global Settings
environment         = "development"
project_name        = "votraio"
gcp_project_id      = "votraio-dev"
gcp_region          = "us-central1"
aws_region          = "us-east-1"
azure_subscription_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Network
kubernetes_subnet_cidr  = "10.1.0.0/20"
pods_secondary_range    = "10.4.0.0/14"
services_secondary_range = "10.0.0.0/16"
database_subnet_cidr    = "10.2.0.0/20"

# Kubernetes
cluster_name              = "votraio-dev"
kubernetes_version        = "1.28"
node_pool_initial_size    = 1
node_pool_min_size        = 1
node_pool_max_size        = 3
machine_type              = "n1-standard-2"
enable_preemptible_nodes  = true

# Database
database_version     = "15"
instance_tier        = "db-custom-2-8192"
disk_size            = 50
max_connections      = 100
backup_retained_count = 7

# Cache
redis_memory_gb = 2
redis_tier      = "basic"

# Flags
deploy_gcp   = true
deploy_aws   = false
deploy_azure = false
enable_public_ip = true
deletion_protection = false

common_labels = {
  environment = "development"
  managed_by  = "terraform"
  team        = "platform"
}
```

### Production Environment

```hcl
# environments/prod/terraform.tfvars

environment           = "production"
project_name          = "votraio"
gcp_project_id        = "votraio-prod"
gcp_region            = "us-central1"
aws_region            = "us-east-1"
azure_subscription_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Network
kubernetes_subnet_cidr   = "10.1.0.0/20"
pods_secondary_range     = "10.4.0.0/14"
services_secondary_range = "10.0.0.0/16"
database_subnet_cidr     = "10.2.0.0/20"

# Kubernetes
cluster_name               = "votraio-prod"
kubernetes_version         = "1.28"
node_pool_initial_size     = 3
node_pool_min_size         = 3
node_pool_max_size         = 10
machine_type               = "n2-standard-4"
enable_preemptible_nodes   = false

# Database
database_version      = "15"
instance_tier         = "db-custom-8-32768"
disk_size             = 200
max_connections       = 500
backup_retained_count = 30

# Cache
redis_memory_gb = 16
redis_tier      = "premium"

# Flags
deploy_gcp   = true
deploy_aws   = true
deploy_azure = true
enable_public_ip = true
deletion_protection = true

common_labels = {
  environment = "production"
  managed_by  = "terraform"
  team        = "platform"
  criticality = "high"
}
```

---

## Deployment Automation

### Initialization Script

```bash
#!/bin/bash
# scripts/init.sh

set -euo pipefail

ENVIRONMENT="${1:-dev}"
WORKSPACE="${2:-$ENVIRONMENT}"

echo "🔧 Initializing Terraform for $ENVIRONMENT environment..."

# Validate environment
if [[ ! -f "environments/$ENVIRONMENT/terraform.tfvars" ]]; then
  echo "❌ Environment file not found: environments/$ENVIRONMENT/terraform.tfvars"
  exit 1
fi

# Initialize Terraform backend
echo "📦 Initializing Terraform backend..."
cd "environments/$ENVIRONMENT"
terraform init -backend=true -upgrade

# Create/select workspace
echo "🔄 Setting up workspace: $WORKSPACE"
terraform workspace select "$WORKSPACE" || terraform workspace new "$WORKSPACE"

cd - > /dev/null

echo "✅ Initialization complete!"
```

### Planning Script

```bash
#!/bin/bash
# scripts/plan.sh

set -euo pipefail

ENVIRONMENT="${1:-dev}"
PLAN_FILE="terraform_${ENVIRONMENT}_$(date +%Y%m%d_%H%M%S).tfplan"

echo "📋 Creating Terraform plan for $ENVIRONMENT environment..."

cd "environments/$ENVIRONMENT"

# Format check
echo "🎨 Checking Terraform formatting..."
terraform fmt -recursive -check=true || {
  echo "❌ Terraform formatting issues detected. Run 'terraform fmt -recursive' to fix."
  exit 1
}

# Validation
echo "✅ Validating Terraform configuration..."
terraform validate

# Planning
echo "📐 Generating Terraform plan..."
terraform plan -out="$PLAN_FILE" -var-file=terraform.tfvars

# Save summary
terraform show "$PLAN_FILE" > "plan_${ENVIRONMENT}_$(date +%Y%m%d_%H%M%S).txt"

echo "✅ Plan complete: $PLAN_FILE"
```

### Apply Script

```bash
#!/bin/bash
# scripts/apply.sh

set -euo pipefail

ENVIRONMENT="${1:-dev}"
PLAN_FILE="${2:-}"

if [[ -z "$PLAN_FILE" ]]; then
  echo "❌ Usage: apply.sh <environment> <plan_file>"
  exit 1
fi

if [[ ! -f "$PLAN_FILE" ]]; then
  echo "❌ Plan file not found: $PLAN_FILE"
  exit 1
fi

echo "🚀 Applying Terraform plan: $PLAN_FILE"

cd "environments/$ENVIRONMENT"

# Apply with approval
read -p "Are you sure you want to apply these changes? (yes/no) " -n 3 -r
echo
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
  terraform apply "$PLAN_FILE"
  
  # Save state backup
  echo "💾 Backing up state..."
  aws s3 cp terraform.tfstate "s3://votraio-terraform-state/${ENVIRONMENT}/backup_$(date +%Y%m%d_%H%M%S).tfstate" || true
  
  echo "✅ Apply complete!"
else
  echo "❌ Apply cancelled."
  exit 1
fi

cd - > /dev/null
```

### Rollback Script

```bash
#!/bin/bash
# scripts/rollback.sh

set -euo pipefail

ENVIRONMENT="${1:-dev}"

echo "⚠️ Rolling back Terraform state for $ENVIRONMENT environment..."

cd "environments/$ENVIRONMENT"

# Show current state
echo "📊 Current state version:"
terraform show

# List state backups
echo "📋 Available backups:"
aws s3 ls "s3://votraio-terraform-state/${ENVIRONMENT}/" || true

# Get backup to restore
read -p "Enter backup filename to restore: " BACKUP_FILE

# Restore state
echo "♻️ Restoring state from backup..."
aws s3 cp "s3://votraio-terraform-state/${ENVIRONMENT}/$BACKUP_FILE" terraform.tfstate

# Verify
echo "✅ State restored. Verifying..."
terraform show

cd - > /dev/null
```

---

## Pre-Commit Validation

### Pre-Commit Configuration

```yaml
# .pre-commit-config.yaml

repos:
  # Terraform formatting
  - repo: https://github.com/hashicorp/pre-commit-terraform
    rev: v1.80.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint
        args:
          - --args=--config=.tflint.hcl
      - id: terraform_docs
        args:
          - --hook-config=--path-to-file=README.md
          - --hook-config=--add-to-existing-file=true

  # Security scanning
  - repo: https://github.com/aquasecurity/tfsec
    rev: v1.27.0
    hooks:
      - id: tfsec

  # Cost analysis
  - repo: https://github.com/bridgecrewio/checkov
    rev: 1.1280.0
    hooks:
      - id: checkov
        args:
          - --framework=terraform
          - --check=CKV_GCP_1,CKV_AWS_1

  # General lint checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
```

### TFLint Configuration

```hcl
# .tflint.hcl

config {
  module = true
  force  = false
}

plugin "terraform" {
  enabled = true
  version = "0.4.0"
  source  = "github.com/terraform-linters/tflint-ruleset-terraform"
}

plugin "aws" {
  enabled = true
  version = "0.18.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

plugin "google" {
  enabled = true
  version = "0.20.0"
  source  = "github.com/terraform-linters/tflint-ruleset-google"
}

rule "terraform_comment_syntax" {
  enabled = true
}

rule "terraform_deprecated_index" {
  enabled = true
}

rule "terraform_deprecated_interpolation" {
  enabled = true
}

rule "terraform_documented_outputs" {
  enabled = true
}

rule "terraform_documented_variables" {
  enabled = true
}

rule "terraform_empty_list_equality" {
  enabled = true
}

rule "terraform_module_pinned_source" {
  enabled = true
}

rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}

rule "terraform_required_providers" {
  enabled = true
}

rule "terraform_required_version" {
  enabled = true
}

rule "terraform_standard_module_structure" {
  enabled = true
}

rule "terraform_unused_declarations" {
  enabled = true
}

rule "terraform_unused_required_providers" {
  enabled = true
}

rule "terraform_workspace_remote" {
  enabled = true
}
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/terraform-deploy.yml

name: Terraform Deployment

on:
  push:
    branches:
      - main
    paths:
      - 'terraform/**'
      - '.github/workflows/terraform-deploy.yml'
  pull_request:
    branches:
      - main
    paths:
      - 'terraform/**'

env:
  TF_VERSION: 1.5.0
  TF_WORKSPACE: ${{ github.ref_name }}

jobs:
  validate:
    name: Validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}
      
      - name: Terraform Format Check
        run: terraform fmt -recursive -check
      
      - name: Terraform Validate
        run: terraform validate
  
  plan:
    name: Plan
    runs-on: ubuntu-latest
    needs: validate
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}
          cli_config_credentials_token: ${{ secrets.TF_API_TOKEN }}
      
      - name: Configure Cloud Credentials
        run: |
          echo "${{ secrets.GCP_SA_KEY }}" > gcp-key.json
          export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/gcp-key.json
      
      - name: Terraform Init
        working-directory: terraform/environments/${{ github.ref_name }}
        run: terraform init
      
      - name: Terraform Plan
        working-directory: terraform/environments/${{ github.ref_name }}
        run: terraform plan -out=tfplan
      
      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: terraform-plan
          path: terraform/environments/${{ github.ref_name }}/tfplan
  
  apply:
    name: Apply
    runs-on: ubuntu-latest
    needs: plan
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Download Plan
        uses: actions/download-artifact@v3
        with:
          name: terraform-plan
          path: terraform/environments/prod
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}
          cli_config_credentials_token: ${{ secrets.TF_API_TOKEN }}
      
      - name: Configure Cloud Credentials
        run: |
          echo "${{ secrets.GCP_SA_KEY }}" > gcp-key.json
          export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/gcp-key.json
      
      - name: Terraform Apply
        working-directory: terraform/environments/prod
        run: terraform apply -auto-approve tfplan
      
      - name: Notify Slack
        if: always()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "Terraform deployment completed",
              "status": "${{ job.status }}"
            }
```

---

**Document Author:** Infrastructure Engineering Team  
**Last Reviewed:** February 2026  
**Version:** 1.0.0

