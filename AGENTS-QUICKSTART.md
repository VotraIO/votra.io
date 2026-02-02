# How to Use Custom Agents - Quick Start Guide

The Votra.io consulting portal has 7 custom AI agents available to accelerate development. This guide shows you how to invoke them.

---

## Quick Reference

| Agent | Invoke | Use For |
|-------|--------|---------|
| Consulting Developer | `@consulting-dev` | Consulting domain features |
| Security & Compliance | `@security-compliance` | Security and compliance |
| FastAPI Security Dev | `@fastapi-security-dev` | API endpoints and testing |
| DevOps & Infrastructure | `@devops-infra` | Infrastructure and deployment |
| Testing & QA | `@testing-qa` | Comprehensive testing |
| Data & Analytics | `@data-analytics` | Analytics and reporting |
| Advanced Planning | `@advanced-planning-agent` | Planning and architecture |

---

## Common Requests by Use Case

### Building a New Consulting Workflow

**Step 1: Plan Architecture**
```
@advanced-planning-agent Create a plan for implementing [feature].
Include architecture, risk assessment, timeline, and success criteria.
```

**Step 2: Implement Core Feature**
```
@consulting-dev Implement [feature] based on the plan:
- [Key requirement 1]
- [Key requirement 2]
- Include Pydantic validation
- Include comprehensive tests
```

**Step 3: Secure Implementation**
```
@security-compliance Review [feature] for security:
- Ensure proper RBAC
- Add audit logging
- Validate financial calculations
- Add encryption for sensitive data
```

**Step 4: Comprehensive Testing**
```
@testing-qa Create complete test suite for [feature]:
- Unit tests (90%+ coverage)
- Integration tests
- API endpoint tests
- Performance tests
- Security tests
```

**Step 5: Deploy Infrastructure**
```
@devops-infra Set up infrastructure for [feature]:
- Database migrations
- Environment configuration
- Monitoring and alerting
- Deployment procedures
```

**Step 6: Analytics & Monitoring**
```
@data-analytics Add analytics for [feature]:
- Key metrics to track
- Dashboard visualization
- Reporting endpoints
- Performance monitoring
```

### Creating API Endpoints

```
@fastapi-security-dev Create REST API endpoint for [feature]:

Endpoint: [METHOD] /api/v1/[resource]

Request/Response:
- [Field]: [Type] - [Description]

Validation:
- [Validation rule 1]
- [Validation rule 2]

Tests:
- Unit tests for validation
- Integration tests for database
- API tests with different roles
- Error condition tests

Target coverage: 95%+
```

### Setting Up Infrastructure

```
@devops-infra Set up production infrastructure:

Components:
- PostgreSQL database with backups
- Redis caching layer
- Application server
- Load balancer
- Monitoring and alerting

Requirements:
- Automated backups
- Point-in-time recovery
- High availability setup
- Cost optimization
- Security hardening

CI/CD:
- Automated testing on push
- Automated deployment to staging
- Manual approval for production
- Health checks after deployment
- Automatic rollback capability
```

### Creating Test Suite

```
@testing-qa Create comprehensive test suite for [feature]:

Test Coverage:
- Scenario 1: [Description]
- Scenario 2: [Description]
- Scenario 3: [Description]

Edge Cases:
- [Edge case 1]
- [Edge case 2]

Performance:
- Target: [Requirement]

Security:
- [Security test 1]
- [Security test 2]

Target Coverage: 95%+
```

### Building Analytics

```
@data-analytics Create analytics for [metric]:

Metrics:
- Metric 1: Definition and calculation
- Metric 2: Definition and calculation

Data Sources:
- [Table 1]
- [Table 2]

Dashboard:
- Visualization type
- Update frequency
- Access permissions

Reports:
- Executive summary
- Detailed reports
- Export format (CSV, PDF)

ETL:
- Daily update at [time]
- Real-time for critical metrics
```

---

## Feature Examples

### Example 1: Implement Timesheet Submission

```
@consulting-dev Implement timesheet submission feature:

Requirements:
- Consultant submits hours for completed work
- Timesheet entry: work_date, hours (0-24), billable (true/false)
- Validation: work_date must be within project dates
- Each entry creates timesheet record
- Submit endpoint: POST /api/v1/timesheets
- List endpoint: GET /api/v1/timesheets
- RBAC: Consultants can submit their own, PMs can view all

Validation Rules:
- hours must be between 0 and 24
- hours must not exceed available hours for consultant
- work_date must be within project date range
- Cannot submit future-dated timesheets
- Billing rate calculated from project rate

Testing:
- Unit tests for validation (90%+ coverage)
- Integration tests for database
- API tests for endpoints
- Permission tests (consultant vs PM)
- Edge case tests
```

### Example 2: Implement Invoice Generation

```
@consulting-dev Implement invoice generation from approved timesheets:

Requirements:
- Generate invoice from timesheets
- Calculate total accurately (DECIMAL, no rounding errors)
- Apply taxes per client contract
- Prevent double-billing
- Invoice states: draft → sent → paid
- API endpoint: POST /api/v1/invoices

Calculations:
- Subtotal = SUM(timesheet.hours × timesheet.billing_rate)
- Tax = subtotal × tax_rate
- Total = subtotal + tax - discounts

Validation:
- All timesheets must be approved
- No timesheet can be used twice
- Rates must be positive
- Invoice total >= 0

Testing:
- Financial calculation accuracy
- Double-billing prevention
- Approval workflow
- Tax calculation
- Edge cases (discounts, special rates)
```

### Example 3: Setup Production Infrastructure

```
@devops-infra Set up Votra.io production infrastructure:

Components:
- PostgreSQL 15 database
- Redis 7 caching layer
- FastAPI application servers (2x t3.medium)
- AWS NLB load balancer
- CloudWatch monitoring
- SNS for alerting

Database:
- 100GB storage
- Multi-AZ deployment
- Daily backups (30-day retention)
- Point-in-time recovery
- Read replicas for reporting

Security:
- VPC with private database
- Security groups (minimal permissions)
- Secrets Manager for credentials
- SSL/TLS with ACM
- WAF for API protection

Backups:
- Daily full backup
- Hourly incremental
- Off-site storage
- Monthly restore testing

Monitoring:
- Application metrics
- Database performance
- Error rate alerting (> 1%)
- Response time alerting (p95 > 1s)
- Disk space alerts (< 20%)

CI/CD:
- GitHub Actions workflows
- Automated testing
- Automated deployment to staging
- Manual approval for production
- Blue-green deployment
- Automatic rollback
```

### Example 4: Testing Suite for Invoice

```
@testing-qa Create comprehensive test suite for invoice generation:

Unit Tests (30 tests):
- Calculation accuracy (no rounding errors)
- Tax calculation correctness
- Discount application
- Negative validation (no negative amounts)
- Edge cases (empty timesheets, zero amounts)

Integration Tests (20 tests):
- Invoice creation from timesheets
- Status transitions (draft → sent → paid)
- Financial data persistence
- Cascade effects (closing project)

API Tests (15 tests):
- Create invoice endpoint
- List invoices endpoint
- Update invoice endpoint
- Permission tests (who can generate)
- Error responses (missing data, invalid IDs)

Security Tests (10 tests):
- Rate limiting
- Authentication required
- Authorization by role
- Input validation
- SQL injection prevention
- XSS prevention

Performance Tests (5 tests):
- Invoice generation < 5 seconds
- List invoices returns in < 1 second
- Calculation accuracy under load
- Memory usage during generation

Edge Cases (10 tests):
- Very large invoices ($1M+)
- Complex tax calculations
- Multiple discounts
- Zero amount invoices
- Duplicate timesheet prevention

Total: 90 tests, 95%+ coverage
```

---

## Agent Interaction Workflow

### Single Feature Implementation

```
1. Request Agent → Get Output → Review Code
                   ↓
            Does it look good?
            ↙           ↘
          YES            NO
           ↓              ↓
        MERGE      Request Changes
                      ↓
                (Back to Agent)
```

### Complex Feature Implementation

```
1. @advanced-planning-agent: Create plan
           ↓
2. @consulting-dev: Implement core
           ↓
3. @fastapi-security-dev: Create endpoints
           ↓
4. @security-compliance: Add security
           ↓
5. @testing-qa: Create tests
           ↓
6. @devops-infra: Set up infrastructure
           ↓
7. @data-analytics: Add analytics
           ↓
8. MERGE TO MAIN
```

---

## Tips for Best Results

### 1. Be Specific
❌ "Add authentication"
✅ "Implement JWT authentication with 30-minute expiration and 7-day refresh tokens"

### 2. Provide Context
```
✅ "Implement timesheet approval workflow:
   - Consultant submits timesheet for PM approval
   - PM can approve or reject with comment
   - Once approved, cannot modify
   - Include audit log of all changes"
```

### 3. Request Tests
```
✅ "Include unit tests (90%+ coverage), integration tests, 
   API tests, and security tests"
```

### 4. Specify Requirements
```
✅ "Financial calculation must use DECIMAL type (no floats),
   no rounding errors, passes audit verification"
```

### 5. Mention Compliance
```
✅ "SOX compliance: implement audit trail, immutable logs,
   prevent unauthorized modifications"
```

---

## Troubleshooting

### Agent Response Too Generic
**Solution**: Provide more specific context
```
Instead of: "Create a new API endpoint"
Use: "Create POST endpoint for SOW creation with fields:
     title (required), client_id (required), rate (100-500),
     duration_days (1-365), include validation and tests"
```

### Missing Tests
**Solution**: Explicitly request test details
```
@testing-qa Create test suite for [feature]:
- Unit tests: validation, edge cases
- Integration tests: database operations
- API tests: all endpoints and error codes
- Security tests: auth, permissions
- Performance: [specific requirement]
- Target coverage: 95%+
```

### Unclear Output
**Solution**: Ask for clarification with examples
```
@agent-name The previous output didn't [describe issue].
Here's an example of what I need:
[Show example or pattern]
```

### Performance Issues
**Solution**: Request profiling and optimization
```
@devops-infra The invoice generation is taking 10 seconds.
Please profile and optimize. Target: < 5 seconds.
```

---

## Success Indicators

Agent work is successful when:
- ✅ Code follows existing patterns
- ✅ Tests achieve target coverage (80-95%)
- ✅ Security requirements are met
- ✅ Performance meets SLAs
- ✅ Consulting workflows work end-to-end
- ✅ Financial calculations are accurate
- ✅ Linters and formatters pass
- ✅ Security scans pass
- ✅ Documentation is complete
- ✅ Ready for production

---

## Getting Help

For detailed agent documentation, see:
- [Agent Registry](.github/agents/README.md) - All agents and capabilities
- [Consulting Developer](.github/agents/consulting-dev.md) - Domain expertise
- [Security & Compliance](.github/agents/security-compliance.md) - Security patterns
- [Testing & QA](.github/agents/testing-qa.md) - Testing strategies
- [DevOps & Infrastructure](.github/agents/devops-infra.md) - Infrastructure setup
- [Data & Analytics](.github/agents/data-analytics.md) - Analytics patterns
- [Consulting Workflow](docs/CONSULTING-WORKFLOW.md) - Business workflows
