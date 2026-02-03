# Infrastructure-as-Code for Votra.io: Multi-Cloud Deployment Guide

**Document Version:** 1.0.0  
**Last Updated:** February 2026  
**Target Audience:** DevOps Engineers, Infrastructure Engineers, Cloud Architects  
**Compliance Framework:** OWASP, CIS Benchmarks, SOC 2 Type II  

---

## Table of Contents

1. [Executive Overview](#executive-overview)
2. [Architecture and Design](#architecture-and-design)
3. [Compliance and Security Requirements](#compliance-and-security-requirements)
4. [Terraform Implementation](#terraform-implementation)
5. [Policy as Code with Sentinel](#policy-as-code-with-sentinel)
6. [Cloud Provider Setup](#cloud-provider-setup)
7. [Deployment Procedures](#deployment-procedures)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [Disaster Recovery](#disaster-recovery)
10. [References and Sources](#references-and-sources)

---

## Executive Overview

### Purpose

This document provides Infrastructure Engineers with a comprehensive guide to deploying the Votra.io consulting portal across multiple cloud providers using Infrastructure-as-Code (IaC) principles. The implementation prioritizes security, compliance, and operational excellence.

### Scope

- **Deployment Target:** Kubernetes clusters on GCP, AWS, or Azure
- **Infrastructure Components:** Compute, networking, storage, databases, caching, and observability
- **Tooling:** Terraform, Helm, kubectl, and cloud provider CLIs
- **Environments:** Development, staging, and production

### Key Principles

1. **Infrastructure as Code:** All infrastructure defined in version-controlled Terraform
2. **Policy as Code:** Sentinel policies enforce compliance and best practices
3. **Cloud Agnostic:** Multi-cloud support with provider-specific modules
4. **Security First:** Defense-in-depth with least-privilege access
5. **Compliance Ready:** Audit trails, encryption, and compliance reporting

---

## Architecture and Design

### Multi-Cloud Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VotraIO Application Layer                 │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Kubernetes Cluster (GKE/EKS/AKS)                       │ │
│  │ ├── FastAPI Application (3+ replicas)                  │ │
│  │ ├── PostgreSQL (managed service)                       │ │
│  │ ├── Redis (managed service)                            │ │
│  │ └── Ingress/Load Balancer                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
           │
     ┌─────┴─────────────────────────────────────────┐
     │                                               │
┌────▼───────┐  ┌──────────────┐  ┌──────────────┐ │
│     GCP    │  │     AWS      │  │     Azure    │ │
│ ┌────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │ │
│ │GKE     │ │  │ │EKS       │ │  │ │AKS       │ │ │
│ │Cloud   │ │  │ │RDS       │ │  │ │Postgres  │ │ │
│ │Storage │ │  │ │ElastiC   │ │  │ │Managed   │ │ │
│ │Cloud   │ │  │ │ache      │ │  │ │Redis     │ │ │
│ │CDN     │ │  │ │S3        │ │  │ │Blob      │ │ │
│ └────────┘ │  │ └──────────┘ │  │ └──────────┘ │ │
└────────────┘  └──────────────┘  └──────────────┘ │
                                                    │
└────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│              Infrastructure as Code                  │
│ ┌────────────────────────────────────────────────┐  │
│ │ Terraform Root Module                          │  │
│ │ ├── Provider: GCP, AWS, Azure                  │  │
│ │ ├── Module: VPC/Networking                     │  │
│ │ ├── Module: Kubernetes Cluster                 │  │
│ │ ├── Module: Database Services                  │  │
│ │ ├── Module: Monitoring & Logging               │  │
│ │ └── Module: Security & IAM                     │  │
│ └────────────────────────────────────────────────┘  │
│ ┌────────────────────────────────────────────────┐  │
│ │ Policy as Code (Sentinel)                      │  │
│ │ ├── Cost Controls                              │  │
│ │ ├── Security Policies                          │  │
│ │ └── Compliance Rules                           │  │
│ └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Component Overview

| Component | Purpose | Service Type |
|-----------|---------|--------------|
| **Kubernetes Cluster** | Container orchestration | GKE/EKS/AKS (managed) |
| **PostgreSQL** | Transactional database | Cloud SQL/RDS/Database for PostgreSQL |
| **Redis** | Session/cache storage | Cloud Memorystore/ElastiCache/Azure Cache |
| **VPC/Network** | Network isolation | Cloud VPC/AWS VPC/Azure vNET |
| **Load Balancer** | Traffic distribution | Cloud LB/ALB/NLB/Azure LB |
| **Object Storage** | File/backup storage | Cloud Storage/S3/Blob Storage |
| **DNS** | Domain resolution | Cloud DNS/Route 53/Azure DNS |
| **Monitoring** | Observability | Cloud Monitoring/CloudWatch/Monitor |
| **Logging** | Log aggregation | Cloud Logging/CloudWatch Logs/Log Analytics |

---

## Compliance and Security Requirements

### Applicable Compliance Frameworks

#### 1. OWASP Top 10

**Implementation Controls:**

| Threat | Control | Implementation |
|--------|---------|-----------------|
| A01: Broken Access Control | RBAC + Network policies | Terraform IAM modules + K8s RBAC |
| A02: Cryptographic Failures | Encryption at rest/transit | Terraform KMS + TLS enforcement |
| A03: Injection | Input validation | FastAPI Pydantic + WAF rules |
| A04: Insecure Design | Secure defaults | Terraform policy as code |
| A05: Security Misconfiguration | IaC + scanning | Terraform + Checkov validation |
| A06: Vulnerable Components | SCA + SBOM | Trivy + supply chain scanning |
| A07: Authentication Failures | JWT + MFA | App implementation + IAM MFA |
| A08: Unauthorized Data Access | Encryption + access logs | Cloud KMS + audit logging |
| A09: Logging Failures | Centralized logging | Cloud Logging integration |
| A10: SSRF | Network isolation | Security groups + network policies |

#### 2. CIS Kubernetes Benchmarks

**Kubernetes Security Controls:**

```hcl
# Pod Security Policy (PSP) or Pod Security Standards (PSS)
resource "kubernetes_namespace" "production" {
  metadata {
    name = "production"
    labels = {
      "pod-security.kubernetes.io/enforce" = "restricted"
      "pod-security.kubernetes.io/audit"   = "restricted"
      "pod-security.kubernetes.io/warn"    = "restricted"
    }
  }
}

# Network Policy - Default Deny
resource "kubernetes_network_policy" "default_deny" {
  metadata {
    name      = "default-deny-ingress"
    namespace = kubernetes_namespace.production.metadata[0].name
  }
  spec {
    pod_selector {}
    policy_types = ["Ingress"]
  }
}

# RBAC - Least Privilege
resource "kubernetes_service_account" "app" {
  metadata {
    name      = "votraio-app"
    namespace = kubernetes_namespace.production.metadata[0].name
  }
}

resource "kubernetes_role" "app" {
  metadata {
    name      = "votraio-app-role"
    namespace = kubernetes_namespace.production.metadata[0].name
  }
  rule {
    api_groups = [""]
    resources  = ["pods", "services"]
    verbs      = ["get", "list"]
  }
}
```

#### 3. SOC 2 Type II Compliance

**Required Controls:**

- **CC6.1:** Logical Access Controls
  - Implementation: IAM with MFA, encryption keys, audit logging
  
- **CC7.2:** System Monitoring
  - Implementation: CloudWatch/Cloud Monitoring/Azure Monitor alerts
  
- **CC8.1:** Change Management
  - Implementation: Git-based IaC, Terraform state locking
  
- **A1.2:** Availability
  - Implementation: Multi-region setup, auto-scaling, backup/recovery

### Encryption Requirements

#### Data at Rest

```hcl
# GCP: Cloud SQL with CMK
resource "google_kms_key_ring" "database" {
  name     = "votraio-db-keys"
  location = "us-central1"
}

resource "google_kms_crypto_key" "database_key" {
  name            = "votraio-db-key"
  key_ring        = google_kms_key_ring.database.id
  rotation_period = "7776000s"  # 90 days
}

resource "google_sql_database_instance" "postgres" {
  name             = "votraio-db"
  database_version = "POSTGRES_15"
  
  settings {
    backup_configuration {
      enabled = true
      location = "us"
    }
    
    ip_configuration {
      require_ssl = true
      authorized_networks {
        name  = "gke-cluster"
        value = google_container_cluster.primary.master_ipv4_cidr_block
      }
    }
    
    database_flags {
      name  = "cloudsql_iam_authentication"
      value = "on"
    }
  }
  
  deletion_protection = true
}

# AWS: RDS with KMS encryption
resource "aws_kms_key" "rds_key" {
  description             = "RDS encryption key"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = {
    Name = "votraio-rds-key"
  }
}

resource "aws_rds_cluster" "postgres" {
  cluster_identifier          = "votraio-db"
  engine                      = "aurora-postgresql"
  engine_version              = "15.2"
  database_name               = "votraio_db"
  master_username             = "votraio"
  master_password             = random_password.db_password.result
  db_subnet_group_name        = aws_db_subnet_group.main.name
  storage_encrypted           = true
  kms_key_id                  = aws_kms_key.rds_key.arn
  backup_retention_period     = 30
  skip_final_snapshot         = false
  final_snapshot_identifier   = "votraio-db-final-snapshot"
  enable_iam_database_authentication = true
  
  tags = {
    Name = "votraio-postgres"
  }
}

# Azure: Managed Database with CMK
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "votraio-db"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  administrator_login    = "votraio"
  administrator_password = random_password.db_password.result
  
  cmk_enabled = true
  
  backup_retention_days             = 30
  geo_redundant_backup_enabled      = true
  
  ssl_enabled = true
  ssl_minimum_tls_version_enforced  = "TLSEnforcementEnabled"
}
```

#### Data in Transit

```hcl
# TLS/HTTPS Everywhere

# GCP: Cloud Armor for DDoS + WAF
resource "google_compute_security_policy" "policy" {
  name = "votraio-policy"

  # Default rule
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SOC_V2"
      src_ip_ranges  = ["*"]
    }
    description = "Default rule"
  }

  # Block known malicious traffic
  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      versioned_expr = "SOC_V2"
      src_ip_ranges  = ["203.0.113.0/24"]  # Example blacklist
    }
    description = "Block malicious IP range"
  }

  # Rate limiting
  rule {
    action   = "rate_based_ban"
    priority = "100"
    match {
      versioned_expr = "SOC_V2"
      src_ip_ranges  = ["*"]
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
    }
    description = "Rate limit requests"
  }
}

# AWS: WAF for API protection
resource "aws_wafv2_web_acl" "api" {
  name  = "votraio-api-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "RateLimitRule"
    priority = 0

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "votraio-api-waf"
    sampled_requests_enabled   = true
  }

  tags = {
    Name = "votraio-api-waf"
  }
}

# Enforce TLS 1.2+ everywhere
resource "google_compute_backend_service" "api" {
  name = "votraio-api-backend"

  protocol = "HTTPS"
  port_name = "https"
  
  security_policy = google_compute_security_policy.policy.id
  
  session_affinity = "NONE"
  timeout_sec     = 30

  enable_cdn = true
  
  cdn_policy {
    cache_mode        = "CACHE_ALL_STATIC"
    default_ttl       = 3600
    max_ttl           = 86400
    negative_caching  = true
    signed_url_cache_max_age_sec = 7200
    client_ttl        = 3600
  }
}
```

### Audit Logging and Compliance Reporting

```hcl
# Enable comprehensive audit logging

# GCP: Cloud Audit Logs
resource "google_project_iam_audit_config" "project" {
  project = var.gcp_project
  service = "allServices"
  
  audit_log_config {
    log_type = "ADMIN_WRITE"
    exempted_members = []
  }
  
  audit_log_config {
    log_type = "DATA_ACCESS"
  }
  
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}

# AWS: CloudTrail for API audit logs
resource "aws_cloudtrail" "main" {
  name                          = "votraio-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  depends_on                    = [aws_s3_bucket_policy.cloudtrail]

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::*/"]
    }

    data_resource {
      type   = "AWS::Lambda::Function"
      values = ["arn:aws:lambda:*:*:function/*"]
    }
  }

  tags = {
    Name = "votraio-trail"
  }
}

resource "aws_s3_bucket" "cloudtrail" {
  bucket = "votraio-cloudtrail-logs"
  
  tags = {
    Name = "CloudTrail Logs"
  }
}

resource "aws_s3_bucket_policy" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# Azure: Activity Log Diagnostics
resource "azurerm_monitor_diagnostic_setting" "audit" {
  name               = "votraio-audit"
  target_resource_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}"

  log {
    category = "Administrative"
    enabled  = true

    retention_policy {
      enabled = true
      days    = 90
    }
  }

  log {
    category = "Security"
    enabled  = true

    retention_policy {
      enabled = true
      days    = 365
    }
  }

  metric {
    category = "AllMetrics"
    enabled  = false
  }

  storage_account_id = azurerm_storage_account.audit.id
}
```

---

## Terraform Implementation

### Project Structure

```
terraform/
├── README.md
├── main.tf                      # Root module
├── providers.tf                 # Provider configuration
├── variables.tf                 # Input variables
├── outputs.tf                   # Module outputs
├── terraform.tfvars            # Variable values
├── terraform.tfvars.example    # Example values template
├── backends.tf                 # Remote state configuration
├── .terraformignore            # Files to ignore
├── .gitignore                  # Git ignore rules
├── .pre-commit-config.yaml     # Pre-commit hooks
│
├── modules/                    # Reusable modules
│   ├── vpc/                    # VPC networking
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── locals.tf
│   │
│   ├── kubernetes/             # Kubernetes cluster
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── node_pools.tf
│   │
│   ├── database/               # PostgreSQL database
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── backups.tf
│   │
│   ├── cache/                  # Redis cache
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── monitoring/             # Observability stack
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── alerts.tf
│   │
│   └── security/               # IAM and security
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── policies.tf
│
├── environments/               # Environment configs
│   ├── dev/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── terraform.tfvars
│       └── backend.tf
│
├── policies/                   # Sentinel policies
│   ├── cost_controls.sentinel
│   ├── security_policies.sentinel
│   ├── compliance_rules.sentinel
│   └── README.md
│
└── scripts/                    # Helper scripts
    ├── validate.sh
    ├── fmt.sh
    ├── init.sh
    └── deploy.sh
```

### Root Module Configuration

```hcl
# main.tf - Root module entry point

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }

  cloud {
    organization = "votraio"
    
    workspaces {
      name = terraform.workspace
    }
  }
}

# GCP Module
module "gcp_infrastructure" {
  count = var.deploy_gcp ? 1 : 0
  
  source = "./modules/gcp"
  
  project_id = var.gcp_project_id
  region     = var.gcp_region
  
  # VPC Configuration
  vpc_name           = var.gcp_vpc_name
  subnet_cidr        = var.gcp_subnet_cidr
  secondary_cidr     = var.gcp_secondary_cidr
  
  # Kubernetes Configuration
  cluster_name       = var.gcp_cluster_name
  kubernetes_version = var.kubernetes_version
  
  # Database Configuration
  database_version   = var.database_version
  database_size      = var.database_size
  
  # Backup Configuration
  backup_location    = var.backup_location
  
  # Labels
  labels = merge(
    var.common_labels,
    {
      environment = var.environment
      provider    = "gcp"
    }
  )
}

# AWS Module
module "aws_infrastructure" {
  count = var.deploy_aws ? 1 : 0
  
  source = "./modules/aws"
  
  aws_region = var.aws_region
  aws_account_id = var.aws_account_id
  
  # VPC Configuration
  vpc_cidr           = var.aws_vpc_cidr
  vpc_name           = var.aws_vpc_name
  
  # Kubernetes Configuration
  cluster_name       = var.aws_cluster_name
  kubernetes_version = var.kubernetes_version
  
  # Database Configuration
  engine_version     = var.database_version
  instance_class     = var.database_size
  
  # Tags
  tags = merge(
    var.common_tags,
    {
      Environment = var.environment
      Provider    = "aws"
    }
  )
}

# Azure Module
module "azure_infrastructure" {
  count = var.deploy_azure ? 1 : 0
  
  source = "./modules/azure"
  
  azure_subscription_id = var.azure_subscription_id
  resource_group_name   = var.resource_group_name
  location              = var.azure_region
  
  # VPC Configuration
  vnet_cidr            = var.azure_vnet_cidr
  vnet_name            = var.azure_vnet_name
  
  # Kubernetes Configuration
  cluster_name         = var.azure_cluster_name
  kubernetes_version   = var.kubernetes_version
  
  # Database Configuration
  server_version       = var.database_version
  sku_name             = var.database_size
  
  # Tags
  tags = merge(
    var.common_tags,
    {
      Environment = var.environment
      Provider    = "azure"
    }
  )
}

# Helm Provider for Kubernetes deployments
provider "helm" {
  kubernetes {
    host  = var.kubernetes_host
    token = var.kubernetes_token
    cluster_ca_certificate = base64decode(
      var.kubernetes_ca_certificate
    )
  }
}

# Deploy Votra.io Helm chart
resource "helm_release" "votraio" {
  name  = "votraio"
  chart = "./helm/votra-io"
  
  namespace        = kubernetes_namespace.production.metadata[0].name
  create_namespace = false
  
  values = [
    file("${path.module}/helm/votra-io/values-${var.environment}.yaml")
  ]
  
  set {
    name  = "image.tag"
    value = var.app_version
  }
  
  set {
    name  = "domain"
    value = var.domain
  }
  
  depends_on = [
    module.gcp_infrastructure,
    module.aws_infrastructure,
    module.azure_infrastructure,
    kubernetes_namespace.production
  ]
}
```

### Provider Configuration

```hcl
# providers.tf - Provider setup

terraform {
  required_providers {
    google = "~> 5.0"
    aws    = "~> 5.0"
    azurerm = "~> 3.0"
  }
}

# GCP Provider
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  
  scopes = [
    "https://www.googleapis.com/auth/cloud-platform",
  ]
}

provider "google-beta" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# AWS Provider
provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      ManagedBy   = "Terraform"
      Project     = "VotraIO"
      Environment = var.environment
      CreatedAt   = timestamp()
    }
  }
}

# Azure Provider
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
  }

  subscription_id = var.azure_subscription_id
  tenant_id       = var.azure_tenant_id
  
  skip_provider_registration = false
}

# Kubernetes Provider
provider "kubernetes" {
  host  = var.kubernetes_host
  token = var.kubernetes_token
  
  cluster_ca_certificate = base64decode(
    var.kubernetes_ca_certificate
  )
}

# Helm Provider (configured in root module)
```

### Core Modules

#### VPC Module

```hcl
# modules/vpc/main.tf

resource "google_compute_network" "main" {
  name                    = var.vpc_name
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"

  depends_on = [
    google_compute_global_address.private_ip_address
  ]
}

resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.vpc_name}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

resource "google_compute_subnetwork" "kubernetes" {
  name          = "${var.vpc_name}-k8s"
  ip_cidr_range = var.kubernetes_subnet_cidr
  region        = var.region
  network       = google_compute_network.main.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr
  }

  private_ip_google_access = true
  flow_logs_config {
    enable = true
  }
}

resource "google_compute_firewall" "allow_internal" {
  name    = "${var.vpc_name}-allow-internal"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  source_ranges = [
    var.kubernetes_subnet_cidr,
    var.pods_cidr,
    var.services_cidr
  ]
}

resource "google_compute_firewall" "allow_ingress" {
  name    = "${var.vpc_name}-allow-ingress"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ingress"]
}
```

#### Kubernetes Module

```hcl
# modules/kubernetes/main.tf

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1
  
  network    = var.vpc_id
  subnetwork = var.subnet_id

  # Kubernetes version
  min_master_version = var.kubernetes_version
  
  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Network Policy
  network_policy {
    enabled = true
  }

  # IP allocation
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Logging and Monitoring
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
    managed_prometheus {
      enabled = true
    }
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

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  # Resource labels
  labels = var.labels

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    network_policy_config {
      disabled = false
    }
  }

  depends_on = [
    var.network_id
  ]
}

# Node pool for application workloads
resource "google_container_node_pool" "primary_nodes" {
  name           = "${var.cluster_name}-node-pool"
  cluster        = google_container_cluster.primary.id
  node_count     = var.node_pool_initial_size
  
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
  }
}

# Service account for pods
resource "google_service_account" "kubernetes_default" {
  account_id   = "${var.cluster_name}-sa"
  display_name = "Service account for ${var.cluster_name}"
}

# Workload Identity binding
resource "google_service_account_iam_binding" "kubernetes_workload_identity" {
  service_account_id = google_service_account.kubernetes_default.name
  role               = "roles/iam.workloadIdentityUser"
  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[default/default]"
  ]
}
```

#### Database Module

```hcl
# modules/database/main.tf

resource "google_sql_database_instance" "postgres" {
  name             = var.instance_name
  database_version = "POSTGRES_${var.postgres_version}"
  region           = var.region
  
  deletion_protection = var.deletion_protection

  settings {
    tier = var.instance_tier
    
    availability_type = "REGIONAL"
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.private_network_id
      require_ssl     = true
      
      authorized_networks {
        name  = "kubernetes-cluster"
        value = var.cluster_network_cidr
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

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
    }

    user_labels = var.labels
  }
}

resource "google_sql_database" "main" {
  name     = var.database_name
  instance = google_sql_database_instance.postgres.name
  charset  = "UTF8"
}

resource "google_sql_user" "app" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result

  deletion_protection = true
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

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

output "instance_connection_name" {
  value = google_sql_database_instance.postgres.connection_name
}

output "database_password_secret" {
  value = google_secret_manager_secret.db_password.id
}
```

---

## Policy as Code with Sentinel

### Overview

Sentinel is HashiCorp's policy-as-code framework for Terraform Cloud/Enterprise. It enforces rules and best practices across all infrastructure deployments.

### Setup and Configuration

```hcl
# terraform/policies/README.md

# Sentinel Policies for VotraIO

This directory contains Sentinel policies that enforce compliance, security,
and cost controls across all Terraform deployments.

## Policy Levels

- **Advisory:** Warning only (non-blocking)
- **Soft Mandatory:** Can be overridden with approval
- **Hard Mandatory:** Cannot be overridden

## Policies Included

1. cost_controls.sentinel - Cost and resource limits
2. security_policies.sentinel - Security best practices
3. compliance_rules.sentinel - Compliance requirements
```

### Cost Control Policies

```hcl
# terraform/policies/cost_controls.sentinel

# Cost Constraints Policy
# Enforces resource quotas and prevents expensive configurations

import "tfplan/v2" as tfplan
import "tfplan/v2" as tfstate

# Allowed instance types and their monthly costs (USD)
instance_costs = {
  "n1-standard-1": 24.45,
  "n1-standard-2": 48.90,
  "n1-standard-4": 97.80,
  "e2-standard-2": 34.13,
  "e2-standard-4": 68.26,
}

# Check GCP instance types
check_gcp_instances = func() {
  violations = []
  
  for resource in tfplan.resource_changes {
    if resource.type is "google_container_node_pool" {
      for instance in resource.change.after.node_config {
        machine_type = instance.machine_type
        
        if machine_type not in instance_costs {
          append(violations, {
            resource: resource.address,
            message: "Instance type not in approved list"
          })
        }
      }
    }
  }
  
  return violations
}

# Check resource deletion protection
check_deletion_protection = func() {
  violations = []
  
  for resource in tfplan.resource_changes {
    if resource.type is "google_sql_database_instance" {
      if resource.change.after.deletion_protection is not true {
        append(violations, {
          resource: resource.address,
          message: "Database must have deletion protection enabled"
        })
      }
    }
  }
  
  return violations
}

# Check for unused resources
check_unused_resources = func() {
  violations = []
  
  for resource in tfplan.resource_changes {
    if resource.type is "google_compute_instance" {
      # Check if instance has scheduling enabled
      if resource.change.after.scheduling is null {
        append(violations, {
          resource: resource.address,
          message: "Compute instance should have scheduling configuration"
        })
      }
    }
  }
  
  return violations
}

# Main policy evaluation
vpc_deletion = check_deletion_protection()
instance_types = check_gcp_instances()
unused = check_unused_resources()

main = rule {
  length(vpc_deletion) == 0 and
  length(instance_types) == 0 and
  length(unused) == 0
}
```

### Security Policies

```hcl
# terraform/policies/security_policies.sentinel

# Security Best Practices Policy
# Enforces encryption, network isolation, and access controls

import "tfplan/v2" as tfplan

# Check encryption at rest
check_encryption = func() {
  violations = []
  
  for resource in tfplan.resource_changes {
    if resource.type is "google_sql_database_instance" {
      settings = resource.change.after.settings
      if settings and settings[0] {
        if settings[0].backup_configuration[0].backup_retention_settings is null {
          append(violations, {
            resource: resource.address,
            message: "Backup retention must be configured"
          })
        }
      }
    }
    
    if resource.type is "aws_rds_cluster" {
      if resource.change.after.storage_encrypted is not true {
        append(violations, {
          resource: resource.address,
          message: "RDS cluster must have encryption at rest enabled"
        })
      }
      
      if resource.change.after.backup_retention_period < 30 {
        append(violations, {
          resource: resource.address,
          message: "RDS backup retention must be at least 30 days"
        })
      }
    }
  }
  
  return violations
}

# Check network security
check_network_security = func() {
  violations = []
  
  for resource in tfplan.resource_changes {
    # Check for public databases
    if resource.type is "aws_rds_cluster" {
      if resource.change.after.publicly_accessible is true {
        append(violations, {
          resource: resource.address,
          message: "RDS cluster must not be publicly accessible"
        })
      }
    }
    
    # Check for open security groups
    if resource.type is "aws_security_group_rule" {
      if resource.change.after.from_port is 0 and
         resource.change.after.to_port is 65535 and
         resource.change.after.cidr_blocks contains "0.0.0.0/0" {
        append(violations, {
          resource: resource.address,
          message: "Security group rule allows unrestricted access"
        })
      }
    }
  }
  
  return violations
}

# Check IAM permissions
check_iam_security = func() {
  violations = []
  
  for resource in tfplan.resource_changes {
    if resource.type is "aws_iam_policy" {
      policy = resource.change.after.policy
      
      # Check for wildcard permissions
      if policy contains "*" {
        append(violations, {
          resource: resource.address,
          message: "IAM policy contains overly broad permissions"
        })
      }
    }
  }
  
  return violations
}

# Main policy evaluation
encryption_check = check_encryption()
network_check = check_network_security()
iam_check = check_iam_security()

main = rule {
  length(encryption_check) == 0 and
  length(network_check) == 0 and
  length(iam_check) == 0
}
```

### Compliance Policies

```hcl
# terraform/policies/compliance_rules.sentinel

# Compliance Rules Policy
# Enforces SOC 2, HIPAA, and other compliance requirements

import "tfplan/v2" as tfplan

# Check logging compliance
check_logging = func() {
  violations = []
  
  for resource in tfplan.resource_changes {
    if resource.type is "google_container_cluster" {
      logging = resource.change.after.logging_config
      if logging is null or length(logging) == 0 {
        append(violations, {
          resource: resource.address,
          message: "Kubernetes cluster must have logging enabled"
        })
      }
    }
    
    if resource.type is "aws_cloudtrail" {
      if resource.change.after.enable_log_file_validation is not true {
        append(violations, {
          resource: resource.address,
          message: "CloudTrail must have log file validation enabled"
        })
      }
    }
  }
  
  return violations
}

# Check audit controls
check_audit = func() {
  violations = []
  
  for resource in tfplan.resource_changes {
    if resource.type is "google_sql_database_instance" {
      settings = resource.change.after.settings
      if settings and settings[0] and settings[0].database_flags {
        flags = settings[0].database_flags
        
        # Check for audit logging
        audit_enabled = false
        for flag in flags {
          if flag.name == "log_statement" {
            audit_enabled = true
          }
        }
        
        if not audit_enabled {
          append(violations, {
            resource: resource.address,
            message: "Database must have audit logging enabled"
          })
        }
      }
    }
  }
  
  return violations
}

# Check tagging compliance
check_tagging = func() {
  violations = []
  
  required_tags = ["Environment", "CostCenter", "Owner", "Project"]
  
  for resource in tfplan.resource_changes {
    if resource.type is "aws_instance" or
       resource.type is "aws_rds_instance" or
       resource.type is "aws_s3_bucket" {
      
      tags = resource.change.after.tags or {}
      
      for required_tag in required_tags {
        if required_tag not in tags {
          append(violations, {
            resource: resource.address,
            message: "Resource missing required tag: " + required_tag
          })
        }
      }
    }
  }
  
  return violations
}

# Check backup compliance
check_backups = func() {
  violations = []
  
  for resource in tfplan.resource_changes {
    if resource.type is "aws_db_instance" {
      if resource.change.after.backup_retention_period < 7 {
        append(violations, {
          resource: resource.address,
          message: "Database backup retention must be at least 7 days"
        })
      }
      
      if resource.change.after.copy_tags_to_snapshot is not true {
        append(violations, {
          resource: resource.address,
          message: "Database snapshots must include resource tags"
        })
      }
    }
  }
  
  return violations
}

# Main policy evaluation
logging_check = check_logging()
audit_check = check_audit()
tagging_check = check_tagging()
backup_check = check_backups()

main = rule {
  length(logging_check) == 0 and
  length(audit_check) == 0 and
  length(tagging_check) == 0 and
  length(backup_check) == 0
}
```

---

## Cloud Provider Setup

### GCP Setup Commands

#### Initial Configuration

```bash
# 1. Set project
export GCP_PROJECT="votraio-prod"
gcloud config set project ${GCP_PROJECT}

# 2. Enable required APIs
gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  servicenetworking.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudsql.googleapis.com \
  redis.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com \
  secretmanager.googleapis.com \
  dns.googleapis.com

# 3. Create service account for Terraform
gcloud iam service-accounts create terraform \
  --display-name="Terraform Service Account"

# 4. Grant necessary IAM roles
gcloud projects add-iam-policy-binding ${GCP_PROJECT} \
  --member="serviceAccount:terraform@${GCP_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/compute.admin"

gcloud projects add-iam-policy-binding ${GCP_PROJECT} \
  --member="serviceAccount:terraform@${GCP_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/container.admin"

gcloud projects add-iam-policy-binding ${GCP_PROJECT} \
  --member="serviceAccount:terraform@${GCP_PROJECT}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.admin"

# 5. Create and export service account key
gcloud iam service-accounts keys create ~/terraform-sa-key.json \
  --iam-account=terraform@${GCP_PROJECT}.iam.gserviceaccount.com

export GOOGLE_APPLICATION_CREDENTIALS=~/terraform-sa-key.json
```

#### Network Setup

```bash
# Create VPC with secondary ranges for Kubernetes
gcloud compute networks create votraio-vpc \
  --subnet-mode=custom \
  --bgp-routing-mode=regional

gcloud compute networks subnets create votraio-k8s \
  --network=votraio-vpc \
  --range=10.1.0.0/20 \
  --secondary-range pods=10.4.0.0/14 \
  --secondary-range services=10.0.0.0/16 \
  --region=us-central1 \
  --private-ip-google-access

# Create Cloud NAT for outbound traffic
gcloud compute routers create votraio-nat-router \
  --network=votraio-vpc \
  --region=us-central1

gcloud compute routers nats create votraio-nat \
  --router=votraio-nat-router \
  --region=us-central1 \
  --nat-all-subnet-ip-ranges \
  --auto-allocate-nat-external-ips
```

#### GKE Cluster Setup

```bash
# Create GKE cluster with security best practices
gcloud container clusters create votraio-gke \
  --region=us-central1 \
  --num-nodes=3 \
  --machine-type=n2-standard-4 \
  --network=votraio-vpc \
  --subnetwork=votraio-k8s \
  --cluster-secondary-range-name=pods \
  --services-secondary-range-name=services \
  --enable-ip-alias \
  --enable-network-policy \
  --enable-vertical-pod-autoscaling \
  --enable-workload-identity \
  --workload-pool=${GCP_PROJECT}.svc.id.goog \
  --enable-logging=SYSTEM,WORKLOAD \
  --enable-monitoring=SYSTEM,WORKLOAD \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=10 \
  --enable-shielded-nodes \
  --enable-ip-masq-agent \
  --addons=HttpLoadBalancing,HorizontalPodAutoscaling,NetworkPolicy

# Get cluster credentials
gcloud container clusters get-credentials votraio-gke \
  --region=us-central1
```

#### CloudSQL Setup

```bash
# Create Cloud SQL instance with replication
gcloud sql instances create votraio-db-primary \
  --database-version=POSTGRES_15 \
  --tier=db-custom-4-16384 \
  --region=us-central1 \
  --availability-type=REGIONAL \
  --backup-start-time=03:00 \
  --retained-backups-count=30 \
  --retained-transaction-log-days=7 \
  --transaction-log-retention-days=7 \
  --database-flags=cloudsql_iam_authentication=on,log_statement=DDL \
  --insights-enabled \
  --storage-auto-increase \
  --storage-auto-increase-limit=200

# Create database
gcloud sql databases create votraio_db \
  --instance=votraio-db-primary

# Create application user
gcloud sql users create votraio \
  --instance=votraio-db-primary \
  --type=BUILT_IN \
  --password

# Create replica for backups
gcloud sql instances clone votraio-db-primary votraio-db-replica \
  --region=us-east1
```

#### Cloud Memorystore (Redis) Setup

```bash
# Create Redis instance
gcloud redis instances create votraio-cache \
  --size=4 \
  --region=us-central1 \
  --redis-version=7.0 \
  --tier=standard \
  --reserved-ip-range=10.1.64.0/24 \
  --enable-auth \
  --auth-string=$(openssl rand -base64 32)

# Configure persistence
gcloud redis instances update votraio-cache \
  --persistence-mode=rdb \
  --rdb-snapshot-period=24h
```

### AWS Setup Commands

#### Initial Configuration

```bash
# 1. Configure AWS CLI
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="123456789012"

aws configure set region ${AWS_REGION}

# 2. Create IAM user for Terraform
aws iam create-user --user-name terraform

# 3. Create access key
aws iam create-access-key --user-name terraform

# 4. Attach policies
aws iam attach-user-policy \
  --user-name terraform \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Alternative: Least privilege policy
cat > terraform-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "eks:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "rds:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "elasticache:*",
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-user-policy \
  --user-name terraform \
  --policy-name TerraformPolicy \
  --policy-document file://terraform-policy.json
```

#### VPC and Network Setup

```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

VPC_ID=$(aws ec2 describe-vpcs --filters "Name=cidr,Values=10.0.0.0/16" \
  --query 'Vpcs[0].VpcId' --output text)

# Create public subnets
aws ec2 create-subnet \
  --vpc-id ${VPC_ID} \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a

aws ec2 create-subnet \
  --vpc-id ${VPC_ID} \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b

# Create private subnets
aws ec2 create-subnet \
  --vpc-id ${VPC_ID} \
  --cidr-block 10.0.10.0/24 \
  --availability-zone us-east-1a

aws ec2 create-subnet \
  --vpc-id ${VPC_ID} \
  --cidr-block 10.0.11.0/24 \
  --availability-zone us-east-1b

# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
  --query 'InternetGateway.InternetGatewayId' --output text)

aws ec2 attach-internet-gateway \
  --vpc-id ${VPC_ID} \
  --internet-gateway-id ${IGW_ID}

# Create route table
RT_ID=$(aws ec2 create-route-table \
  --vpc-id ${VPC_ID} \
  --query 'RouteTable.RouteTableId' --output text)

aws ec2 create-route \
  --route-table-id ${RT_ID} \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id ${IGW_ID}
```

#### EKS Cluster Setup

```bash
# Create EKS cluster
aws eks create-cluster \
  --name votraio-eks \
  --version 1.28 \
  --role-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/eks-service-role \
  --resources-vpc-config subnetIds=subnet-xxxxx,subnet-yyyyy \
  --logging '{"clusterLogging":[{"enabled":true,"types":["api","audit","authenticator","controllerManager","scheduler"]}]}'

# Get cluster endpoint
aws eks describe-cluster \
  --name votraio-eks \
  --query 'cluster.endpoint' \
  --output text

# Update kubeconfig
aws eks update-kubeconfig \
  --region ${AWS_REGION} \
  --name votraio-eks

# Create node group
aws eks create-nodegroup \
  --cluster-name votraio-eks \
  --nodegroup-name votraio-nodes \
  --scaling-config minSize=3,maxSize=10,desiredSize=3 \
  --subnets subnet-xxxxx subnet-yyyyy \
  --node-role arn:aws:iam::${AWS_ACCOUNT_ID}:role/NodeInstanceRole
```

#### RDS Setup

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier votraio-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.2 \
  --master-username votraio \
  --master-user-password $(openssl rand -base64 32) \
  --allocated-storage 100 \
  --storage-type gp3 \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:us-east-1:${AWS_ACCOUNT_ID}:key/xxxxx \
  --db-subnet-group-name votraio-db-subnet \
  --vpc-security-group-ids sg-xxxxx \
  --enable-iam-database-authentication \
  --backup-retention-period 30 \
  --multi-az \
  --enable-cloudwatch-logs-exports postgresql

# Create database
aws rds create-db-instance --db-instance-identifier votraio_db
```

#### ElastiCache Setup

```bash
# Create Redis cluster
aws elasticache create-replication-group \
  --replication-group-description "Votra.io Redis Cache" \
  --replication-group-id votraio-cache \
  --engine redis \
  --cache-node-type cache.t3.medium \
  --num-cache-clusters 3 \
  --automatic-failover-enabled \
  --multi-az \
  --engine-version 7.0 \
  --cache-subnet-group-name votraio-cache-subnet \
  --security-group-ids sg-xxxxx \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled \
  --auth-token $(openssl rand -base64 32)
```

### Azure Setup Commands

#### Initial Configuration

```bash
# 1. Login to Azure
az login

# 2. Set subscription
az account set --subscription="subscription-id"

# 3. Create resource group
az group create \
  --name votraio-rg \
  --location eastus

# 4. Create service principal for Terraform
az ad sp create-for-rbac \
  --name terraform \
  --role Contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv)

# Set environment variables for Terraform
export ARM_CLIENT_ID="<appId>"
export ARM_CLIENT_SECRET="<password>"
export ARM_SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
export ARM_TENANT_ID="<tenant>"
```

#### Networking Setup

```bash
# Create virtual network
az network vnet create \
  --resource-group votraio-rg \
  --name votraio-vnet \
  --address-prefix 10.0.0.0/16

# Create subnets for AKS
az network vnet subnet create \
  --resource-group votraio-rg \
  --vnet-name votraio-vnet \
  --name aks-subnet \
  --address-prefixes 10.0.1.0/24

# Create subnet for databases
az network vnet subnet create \
  --resource-group votraio-rg \
  --vnet-name votraio-vnet \
  --name db-subnet \
  --address-prefixes 10.0.2.0/24
```

#### AKS Cluster Setup

```bash
# Create AKS cluster
az aks create \
  --resource-group votraio-rg \
  --name votraio-aks \
  --kubernetes-version 1.28.0 \
  --node-count 3 \
  --vm-set-type VirtualMachineScaleSets \
  --zones 1 2 3 \
  --node-vm-size Standard_D4s_v3 \
  --network-plugin azure \
  --network-policy azure \
  --vnet-subnet-id /subscriptions/$(az account show --query id -o tsv)/resourceGroups/votraio-rg/providers/Microsoft.Network/virtualNetworks/votraio-vnet/subnets/aks-subnet \
  --docker-bridge-address 172.17.0.1/16 \
  --service-cidr 10.0.0.0/16 \
  --dns-service-ip 10.0.0.10 \
  --enable-managed-identity \
  --enable-addon monitoring \
  --workspace-resource-id /subscriptions/$(az account show --query id -o tsv)/resourcegroups/votraio-rg/providers/microsoft.operationalinsights/workspaces/votraio-workspace \
  --enable-aad \
  --aad-admin-group-object-ids "group-object-id"

# Get credentials
az aks get-credentials \
  --resource-group votraio-rg \
  --name votraio-aks
```

#### Database Setup

```bash
# Create Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group votraio-rg \
  --name votraio-db \
  --location eastus \
  --admin-user votraio \
  --admin-password $(openssl rand -base64 32) \
  --sku-name Standard_D4s_v3 \
  --tier GeneralPurpose \
  --storage-size 131072 \
  --version 15 \
  --high-availability Enabled \
  --backup-retention 30 \
  --geo-redundant-backup Enabled

# Create database
az postgres flexible-server db create \
  --resource-group votraio-rg \
  --server-name votraio-db \
  --database-name votraio_db

# Create Azure Cache for Redis
az redis create \
  --resource-group votraio-rg \
  --name votraio-cache \
  --location eastus \
  --sku Premium \
  --vm-size p1 \
  --enable-non-ssl-port false \
  --minimum-tls-version 1.2
```

---

## Deployment Procedures

### Terraform Workflow

#### Initialization

```bash
# 1. Clone repository
git clone https://github.com/VotraIO/votra-infrastructure.git
cd votra-infrastructure/terraform

# 2. Initialize Terraform
terraform init

# 3. Select workspace
terraform workspace select prod
# or create new workspace
terraform workspace new prod

# 4. Validate configuration
terraform validate

# 5. Format code
terraform fmt -recursive
```

#### Planning

```bash
# Generate execution plan
terraform plan -out=tfplan

# View detailed changes
terraform show tfplan

# Save plan for review
terraform plan -out=tfplan > plan.txt
```

#### Applying

```bash
# Apply Terraform changes
terraform apply tfplan

# Save outputs
terraform output > outputs.json

# Export kubeconfig
terraform output kubernetes_config > ~/.kube/config
chmod 600 ~/.kube/config
```

#### Validation

```bash
# Verify cluster connectivity
kubectl cluster-info

# Check nodes
kubectl get nodes

# Verify Helm deployments
helm list

# Check pod status
kubectl get pods -A
```

---

## Monitoring and Observability

### Cloud Provider Monitoring Setup

#### GCP Monitoring

```bash
# Create alert policy for high CPU
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High CPU Usage" \
  --condition-display-name="CPU > 80%" \
  --condition-threshold-value=0.8 \
  --condition-threshold-duration=300s \
  --condition-threshold-filter='resource.type="gce_instance"'
```

#### AWS CloudWatch

```bash
# Create alarm for database connections
aws cloudwatch put-metric-alarm \
  --alarm-name rds-high-connections \
  --alarm-description "Alert on high database connections" \
  --metric-name DatabaseConnections \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:votraio-alerts
```

#### Azure Monitor

```bash
# Create metric alert
az monitor metrics alert create \
  --name "High Memory Usage" \
  --resource-group votraio-rg \
  --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/votraio-rg/providers/Microsoft.Compute/virtualMachines/vm-name \
  --condition "avg Percentage Memory > 80" \
  --window-size 5m \
  --evaluation-frequency 1m
```

---

## Disaster Recovery

### Backup Strategy

```hcl
# Backup retention policy
backup_retention_days = 30
backup_frequency = "daily"
backup_time = "03:00 UTC"

# Cross-region replication
backup_replication_enabled = true
backup_replication_region = "alternate-region"

# Point-in-time recovery
point_in_time_recovery_days = 7
```

### Restore Procedures

```bash
# List available backups
gcloud sql backups list --instance=votraio-db-primary

# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=votraio-db-primary \
  --backup-configuration=automated
```

---

## References and Sources

### Terraform Documentation
- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Terraform Best Practices](https://www.terraform.io/language)

### Kubernetes and Container Security
- [CIS Kubernetes Benchmarks](https://www.cisecurity.org/benchmark/kubernetes)
- [Kubernetes Security Documentation](https://kubernetes.io/docs/concepts/security/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)

### Cloud Provider Security
- [GCP Security Best Practices](https://cloud.google.com/security/best-practices)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [Azure Security Best Practices](https://docs.microsoft.com/en-us/azure/security/fundamentals/best-practices-and-patterns)

### Compliance Frameworks
- [OWASP Top 10](https://owasp.org/Top10/)
- [SOC 2 Type II Compliance](https://www.aicpa.org/interestareas/informationmanagement/sodp-system-and-organization-controls.html)
- [CIS Controls](https://www.cisecurity.org/controls)

### Policy as Code
- [Sentinel Documentation](https://www.terraform.io/cloud-docs/policy-enforcement/policy-as-code)
- [Terraform Cloud Policy Set](https://www.terraform.io/cloud-docs/policy-enforcement/manage-policy-sets)
- [HashiCorp Sentinel Examples](https://github.com/hashicorp/terraform-sentinel-policies)

### Additional Resources
- [FastAPI Security](https://fastapi.tiangolo.com/advanced/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/sql-syntax.html)
- [Redis Security](https://redis.io/topics/security)

---

**Document Author:** Infrastructure Engineering Team  
**Last Reviewed:** February 2026  
**Next Review Date:** August 2026  
**Version:** 1.0.0

