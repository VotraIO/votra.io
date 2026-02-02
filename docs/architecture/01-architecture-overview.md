aadf# Votra.io System Architecture Overview

**Document ID**: ARCH-001  
**Version**: 1.0.0  
**Last Updated**: 2026-02-01  
**Owner**: Technical Lead / Architect  
**Status**: Approved

---

## Executive Summary

The Votra.io platform is a comprehensive consulting business portal built on a layered FastAPI architecture with clear separation of concerns: a web frontend for user interaction, a REST API backend managing consulting workflows, and database models for consulting entities. The architecture prioritizes security, financial accuracy, auditability, and scalability.

**Key Architectural Decisions**:
- **Layered Architecture** - Clear separation: Routers → Services → Database → Utils
- **Domain-Driven Design** - Consulting-specific entities (SOW, Project, Timesheet, Invoice)
- **API-First Design** - All functionality exposed through RESTful APIs with role-based access
- **Security by Default** - JWT auth, bcrypt passwords, RBAC, audit logging
- **Financial Accuracy** - Input validation to prevent billing errors, audit trails for compliance
- **Observable & Auditable** - Comprehensive logging, financial audit trails, role-based access tracking

---

## System Architecture (30,000 Foot View)

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Layer                                  │
├─────────────────────────────────────────────────────────────────┤
│  Web Dashboard (Vue.js)  │  CLI Tool  │  IDE Extension          │
│  Browser-based UI        │  Command   │  Native editor           │
└──────────────┬────────────────────────┬──────────────────────────┘
               │                        │
               └──────────┬─────────────┘
                          │ HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  Rate Limiting │ Authentication │ Request Routing │ Load Balance│
│  CORS Policy   │ JWT Validation │ Request Logging │ SSL/TLS    │
└──────────────┬────────────────────────┬──────────────────────────┘
               │                        │
               │ Internal APIs          │
┌──────────────────────────────────────────────────────────────────┐
│                Core Services Layer                               │
├──────────────┬─────────────────────┬────────────────────────────┤
│ Auth Service │  Client/SOW Service │  Timesheet/Invoice Service │
│ User mgmt    │  Client & SOW mgmt  │  Time entry & approvals    │
│ Token mgmt   │  Engagement tracking│  Billing & invoicing       │
└──────┬───────┴──────────┬───────────┴──────────────┬────────────┘
       │                  │                          │
       │ Async Events     │                          │
┌──────────────────────────────────────────────────────────────────┐
│            Agent Orchestration Layer (Message Queue)             │
├──────────────────────────────────────────────────────────────────┤
│  Event Bus │ Task Queue │ Agent Coordinator │ Response Handler  │
│  FIFO delivery │ Priority-based processing │ Result aggregation│
└──────────────────────────────────────────────────────────────────┘
       │                  │                          │
       ├──────┬───────────┼─────────────┬───────────┤
       │      │           │             │           │
┌──────────────────────────────────────────────────────────────────┐
│                    Specialized Agents Layer                       │
├──────────────┬────────────────┬────────────────┬────────────────┤
│ Planning     │  Security      │  FastAPI       │  DevOps        │
│ Agent        │  Agent         │  Agent         │  Agent         │
│ Documentation│  Vulnerability │  Code gen      │  Infrastructure│
│ generation   │  scanning      │  scaffolding   │  deployment    │
└──────────────┴────────────────┴────────────────┴────────────────┘
       │              │                 │                 │
       └──────────────────────────────────────────────────┘
                      │ External APIs
       ┌──────────────────────────────────────┐
       │  GitHub  │ GitLab  │ Cloud (AWS/GCP)│
       │  APIs    │  APIs   │ OpenAI APIs    │
       └──────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      Data Layer                                   │
├──────────────────────────────────────────────────────────────────┤
│ PostgreSQL  │ Redis Cache  │  Document Store  │ Object Storage  │
│ Relational  │ Session &    │  Planning docs   │ Generated code  │
│ User data   │  Caching     │  Artifacts       │ Logs & Reports  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                  Infrastructure & Observability                  │
├──────────────────────────────────────────────────────────────────┤
│ Kubernetes │ Prometheus │ ELK Stack  │ Jaeger Tracing           │
│ Orchestration│ Metrics  │ Logging    │ Request tracing          │
│ Auto-scaling │ Alerting │ Searching  │ Performance analysis     │
└──────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend
- **Framework**: Vue.js 3 with TypeScript
- **Build Tool**: Vite
- **Package Manager**: npm/pnpm
- **UI Components**: Headless UI + Tailwind CSS
- **State Management**: Pinia (Vue store)
- **HTTP Client**: axios with interceptors

### Backend & Services
- **Framework**: FastAPI (Python)
- **Python Version**: 3.11+
- **Async Runtime**: asyncio with uvicorn
- **Validation**: Pydantic v2
- **ORM**: SQLAlchemy 2.0+ (async)

### Agent Framework
- **Language**: Python
- **Libraries**: LangChain, semantic-kernel, or custom
- **LLM Integration**: OpenAI API (with provider abstraction)
- **Specialized Libraries**: 
  - Security: bandit, pylint, mypy, safety
  - FastAPI: fastapi, pydantic, sqlalchemy
  - Deployment: boto3, gcloud, azure-sdk

### Data Storage
- **Primary Database**: PostgreSQL 14+
- **Caching**: Redis 7+ (sessions, caching, rate limiting)
- **Document Store**: MongoDB or DynamoDB (planning docs)
- **Object Storage**: AWS S3 or GCS (generated artifacts)

### Infrastructure & DevOps
- **Container Platform**: Kubernetes 1.26+
- **Container Registry**: Docker / GitHub Container Registry
- **Load Balancing**: Nginx or cloud-native load balancer
- **Service Mesh**: Optional (Istio for advanced scenarios)
- **Observability**: Prometheus, Grafana, ELK Stack, Jaeger

### CI/CD & Automation
- **CI/CD Platform**: GitHub Actions
- **Infrastructure as Code**: Terraform
- **Secret Management**: GitHub Secrets (development), HashiCorp Vault (production)
- **Container Orchestration**: Kubernetes manifests or Helm

---

## Core Components

### 1. Web Dashboard (Frontend)
**Purpose**: Primary user interface for managing projects, viewing reports, and configuring agents

**Responsibilities**:
- Display project overview and status
- Manage authentication and sessions
- Submit requests to agents
- Display agent recommendations and results
- Real-time notifications of agent activity

**Tech**: Vue.js 3, Vite, Tailwind CSS, Pinia

**API Endpoints Used**:
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects/{id}/requests` - Submit agent request
- `GET /api/v1/requests/{id}` - Check request status
- `WebSocket /api/v1/ws/notifications` - Real-time updates

---

### 2. API Gateway
**Purpose**: Single entry point managing routing, authentication, rate limiting, and request logging

**Responsibilities**:
- Validate JWT tokens
- Apply rate limiting (10,000 req/min default, configurable)
- Route requests to appropriate backend services
- Add request context (user, organization, trace ID)
- Log all requests for audit trail

**Tech**: FastAPI with custom middleware

**Key Handlers**:
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/refresh` - Token refresh
- All other requests pass through to services

---

### 3. Core Services
**Purpose**: Business logic for projects, users, and platform management

#### 3.1 Auth Service
- User registration and login
- JWT token generation and validation
- Password hashing with bcrypt
- Session management
- Multi-factor authentication (future)

#### 3.2 Project Service
- Project creation and management
- Team membership
- Access control and permissions
- Project settings and configuration
- Integration with GitHub repositories

#### 3.3 Planning Service
- Documentation generation
- Planning document management
- Version control and change tracking
- Collaboration and comments
- Export to PDF/markdown

---

### 4. Agent Orchestration Layer
**Purpose**: Coordinates agent work, manages async task execution, and aggregates results

**Responsibilities**:
- Accept task requests from API
- Route to appropriate agent
- Track task progress
- Handle agent failures and retries
- Aggregate results from multiple agents
- Manage execution priority and queuing

**Tech**: Message queue (RabbitMQ or AWS SQS), async task processor

**Key Patterns**:
- Event-driven: Agents react to events
- Request-response: Caller waits for result (with timeout)
- Async callback: Agents post results to callback URL
- Retry logic: Exponential backoff with max retries

---

### 5. Specialized Agents
Each agent is a containerized service with specific responsibilities:

#### 5.1 Planning Agent
Generates comprehensive strategic planning documentation

**Inputs**: Project requirements, stakeholders, constraints
**Outputs**: Planning markdown documents, risk registers, success criteria
**Performance Target**: <30s for standard project
**Scalability**: Stateless (can run multiple instances)

#### 5.2 Security Agent
Scans code, dependencies, and infrastructure for vulnerabilities

**Inputs**: Code repository, dependency list, infrastructure config
**Outputs**: Vulnerability report, compliance status, recommendations
**Performance Target**: <5min for full analysis
**Scalability**: Resource-intensive (limit to 2-3 concurrent)

#### 5.3 FastAPI Agent
Generates secure REST APIs with best practices

**Inputs**: Data model, endpoints needed, security requirements
**Outputs**: FastAPI scaffolding, models, routers, tests
**Performance Target**: <15s per endpoint
**Scalability**: Stateless (can run multiple instances)

#### 5.4 DevOps Agent
Manages infrastructure and deployment

**Inputs**: Application config, deployment target, scaling requirements
**Outputs**: Terraform/Kubernetes manifests, CI/CD pipeline, monitoring config
**Performance Target**: <2min for infrastructure setup
**Scalability**: Limited to 1-2 concurrent (infrastructure safety)

---

## Data Model (High Level)

### User
- id, username, email, password_hash
- organization_id (multi-tenancy)
- roles (admin, developer, viewer)
- created_at, updated_at

### Project
- id, organization_id, name, description
- github_url, deployment_target
- owner_id, team_members
- settings (agent preferences, integrations)
- created_at, updated_at

### Planning Document
- id, project_id, document_type
- title, content (markdown), version
- created_by, last_modified_by
- created_at, updated_at
- approval_chain (pending approvals)

### Agent Request
- id, project_id, agent_type
- input_data, status, result
- created_at, started_at, completed_at
- error_message (if failed)

### Audit Log
- id, user_id, action, resource_type, resource_id
- changes (before/after)
- ip_address, user_agent
- created_at

---

## API Design Principles

### RESTful Conventions
- Standard HTTP methods: GET (read), POST (create), PUT (update), DELETE (remove)
- Resource-based URLs: `/api/v1/projects/{id}/requests`
- Status codes: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 422 (Validation Error), 500 (Server Error)

### API Versioning
- Version prefix in URL: `/api/v1/`, `/api/v2/`
- Backward compatibility maintained (deprecation period)
- Breaking changes documented in release notes

### Authentication & Authorization
- JWT tokens in `Authorization: Bearer <token>` header
- Role-based access control (RBAC)
- Organization-based isolation (multi-tenancy)
- Audit trail of all actions

### Rate Limiting
- Per-user: 10,000 req/min (configurable per tier)
- Per-IP: 1,000 req/min (bot protection)
- Agent requests: 100 concurrent max (prevent overload)
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### Error Handling
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {"field": "email", "issue": "Invalid email format"}
    ],
    "trace_id": "req-12345" // For support debugging
  }
}
```

---

## Security Architecture

### Defense in Depth
1. **Network Layer**: TLS 1.3 encryption, VPC isolation
2. **API Layer**: Rate limiting, CORS, request validation
3. **Auth Layer**: JWT tokens with expiration, bcrypt hashing
4. **Business Logic**: Input validation, parameterized queries
5. **Data Layer**: Encryption at rest, role-based access
6. **Infrastructure**: Monitoring, intrusion detection, incident response

### Secrets Management
- Environment variables for configuration
- GitHub Secrets for CI/CD
- HashiCorp Vault for production (future)
- Encrypted storage for sensitive data
- Automatic rotation of credentials

### Compliance
- GDPR: Data minimization, right to deletion, consent
- SOC2: Access controls, audit logging, incident response
- HIPAA: PHI handling (if applicable)
- Security testing: OWASP Top 10, dependency scanning

---

## Deployment Architecture

### Development Environment
- Local Docker containers
- SQLite database (fast, no setup)
- Mock LLM responses for testing
- Minimal infrastructure (laptop capable)

### Staging Environment
- Kubernetes cluster on GCP/AWS
- PostgreSQL database
- Real LLM APIs (with usage monitoring)
- Full monitoring and logging
- Load testing capabilities

### Production Environment
- Kubernetes cluster with auto-scaling
- Multi-availability zone deployment
- PostgreSQL with replication
- Redis cluster for caching
- CDN for static assets
- Disaster recovery (backup, failover)

---

## Scalability & Performance

### Horizontal Scaling
- Stateless API servers (add/remove instances as needed)
- Database connection pooling
- Redis cluster for caching
- Message queue with parallel processing

### Expected Load
- **Month 1**: 100 active users, 1,000 API calls/day
- **Month 6**: 10,000 active users, 100,000 API calls/day
- **Year 1**: 100,000 active users, 1M+ API calls/day

### Performance Targets
- API response time: <200ms (p95)
- Agent response time: <30s (p95)
- Page load time: <2s (p95)
- Uptime: 99.9% (≤8.76 hours/year downtime)

---

## Integration Points

### External Systems
1. **GitHub**
   - OAuth authentication
   - Repository access (read code, create PRs)
   - Webhook events (push, PR, release)

2. **Cloud Providers** (AWS, GCP, Azure)
   - Infrastructure provisioning
   - Deployment targets
   - Cost monitoring

3. **LLM APIs** (OpenAI, Anthropic, others)
   - Code generation
   - Analysis and recommendations
   - Cost tracking and rate limiting

4. **Monitoring Services** (Datadog, New Relic, etc.)
   - Performance metrics
   - Error tracking
   - Alerting

---

## Conclusion

The Votra.io architecture is designed to be:
- **Secure** - Defense in depth, cryptography by default
- **Scalable** - Horizontal scaling, efficient caching
- **Maintainable** - Clear separation of concerns, modular design
- **Observable** - Comprehensive logging and monitoring
- **Reliable** - Redundancy, graceful degradation, incident response

This architecture supports the current MVP requirements and scales to enterprise demands as the platform grows.

---

## Approval Chain

- [ ] Technical Lead: _______________  Date: _______
- [ ] Security Lead: _______________  Date: _______
- [ ] DevOps Lead: _______________  Date: _______

---

## Related Documents

- [Project Charter](../planning/01-project-charter.md) - Project context
- [Component Definitions](02-component-definitions.md) - Detailed component specs
- [Data Flows](03-data-flows.md) - How data moves through system
