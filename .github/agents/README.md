# Custom Agents for Votra.io Consulting Portal

This directory contains custom AI agent definitions for specialized development tasks in the Votra.io consulting business portal. These agents provide domain expertise, enforce best practices, and ensure quality across all development work.

## Available Agents

### 1. Consulting Developer (`consulting-dev.md`)

**Classification**: Development | Consulting Domain

**Purpose**: Expert developer specializing in consulting business workflows, data models, API development, and business logic implementation.

**Key Capabilities**:
- ✅ Consulting domain expertise (SOW, projects, timesheets, invoices)
- ✅ Complex workflow implementation (5-phase consulting lifecycle)
- ✅ Data model design and validation
- ✅ API endpoint development (CRUD + workflow operations)
- ✅ Business logic implementation with audit trails
- ✅ Role-based access control (Admin, PM, Consultant, Client, Accountant)
- ✅ Comprehensive testing (unit, integration, API tests)

**When to Use**:
- Implementing SOW management features
- Creating project tracking functionality
- Building timesheet submission workflows
- Implementing invoice generation
- Adding new consulting-domain features
- Designing data models for consulting entities
- Implementing approval workflows

**Example Usage**:
```
@consulting-dev I need to implement SOW (Statement of Work) management with approval workflow.
The SOW should track client, scope, rate, duration, and require PM approval before
creating a project. Include Pydantic validation and comprehensive tests.
```

### 2. Security & Compliance (`security-compliance.md`)

**Classification**: Security | Compliance

**Purpose**: Security and compliance specialist ensuring financial data protection, regulatory compliance, and audit trails for consulting platforms.

**Key Capabilities**:
- ✅ Role-based access control (RBAC) architecture
- ✅ Financial data encryption and protection
- ✅ Compliance frameworks (GDPR, SOX, HIPAA)
- ✅ Audit logging and immutable records
- ✅ Financial data validation
- ✅ API security (rate limiting, validation, CORS)
- ✅ Secrets management
- ✅ Vulnerability management
- ✅ Security monitoring and alerting

**When to Use**:
- Implementing access control for consulting roles
- Setting up financial data encryption
- Implementing compliance requirements
- Adding audit logging for financial transactions
- Implementing security headers and rate limiting
- Managing secrets and credentials
- Setting up security monitoring

**Example Usage**:
```
@security-compliance I need to ensure consulting portal compliance with SOX for 
financial controls. Implement audit logging for all financial transactions, 
role-based access control, and validation of financial calculations.
```

### 3. FastAPI Security Developer (`fastapi-security-dev.md`)

**Classification**: Development | Security | Infrastructure

**Purpose**: Expert FastAPI Python developer specializing in secure, well-tested, production-ready code.

**Key Capabilities**:
- ✅ Secure FastAPI development following OWASP guidelines
- ✅ Automated unit test generation with 80% coverage target
- ✅ Security scanning (bandit, safety, CodeQL)
- ✅ Code quality enforcement (black, ruff, mypy, pylint)
- ✅ GitHub Actions CI/CD setup
- ✅ GitHub secrets management
- ✅ Dependency vulnerability scanning
- ✅ Pre-commit hooks and linting

**When to Use**:
- Creating or modifying FastAPI endpoints
- Implementing authentication/authorization
- Setting up new API routes or services
- Adding security features
- Creating or updating tests
- Setting up CI/CD pipelines
- Managing application secrets

**Example Usage**:
```
@fastapi-security-dev Implement JWT-based authentication for consulting portal with 
refresh tokens, password hashing with bcrypt, and comprehensive security tests covering 
token validation, expiration, and refresh scenarios.
```

### 4. DevOps & Infrastructure (`devops-infra.md`)

**Classification**: Infrastructure | DevOps

**Purpose**: DevOps engineer specializing in CI/CD automation, containerization, database management, monitoring, and deployment strategies.

**Key Capabilities**:
- ✅ GitHub Actions CI/CD pipeline design
- ✅ Docker containerization and multi-stage builds
- ✅ Database setup (PostgreSQL) and migrations
- ✅ Monitoring and observability (logging, metrics, alerting)
- ✅ Backup and disaster recovery
- ✅ Security infrastructure (VPC, secrets management, SSL/TLS)
- ✅ Infrastructure as Code (Terraform)
- ✅ Load balancing and auto-scaling
- ✅ Zero-downtime deployments
- ✅ Cost optimization

**When to Use**:
- Setting up CI/CD pipelines
- Configuring Docker containers
- Managing database setup and migrations
- Implementing monitoring and alerting
- Disaster recovery planning
- Infrastructure provisioning
- Deployment strategy design
- Performance optimization

**Example Usage**:
```
@devops-infra Set up production infrastructure for consulting portal:
- PostgreSQL database with backups and point-in-time recovery
- Redis caching layer
- CI/CD pipeline with automated testing and deployment
- Monitoring and alerting for errors, performance, and financial transactions
- Zero-downtime deployment strategy with rollback capability
```

### 5. Testing & QA (`testing-qa.md`)

**Classification**: Quality Assurance | Testing

**Purpose**: Testing engineer specializing in comprehensive test strategy, automation, coverage analysis, and quality assurance.

**Key Capabilities**:
- ✅ Test strategy design (pyramid: unit, service, integration)
- ✅ Unit testing with pytest
- ✅ Service layer testing
- ✅ API integration testing
- ✅ Database integrity testing
- ✅ Performance testing and benchmarking
- ✅ Security testing (OWASP Top 10)
- ✅ Regression testing
- ✅ Test data management and fixtures
- ✅ CI/CD integration
- ✅ Consulting-specific test scenarios

**When to Use**:
- Designing test strategy
- Writing comprehensive test suites
- Testing business logic and workflows
- API endpoint testing
- Performance and load testing
- Security testing
- Database testing
- Test coverage analysis

**Example Usage**:
```
@testing-qa Create comprehensive test suite for invoice generation feature:
- Unit tests for financial calculations (no rounding errors)
- Integration tests for workflow (timesheet → invoice)
- API endpoint tests for invoice CRUD operations
- Security tests for permission validation
- Performance tests (generate invoice < 5 seconds)
- Target: 95%+ coverage for critical paths
```

### 6. Data & Analytics (`data-analytics.md`)

**Classification**: Data Engineering | Analytics

**Purpose**: Data engineer specializing in data warehouse design, ETL pipelines, analytics, and business intelligence.

**Key Capabilities**:
- ✅ Data warehouse design (star schema for consulting metrics)
- ✅ ETL pipeline design and implementation
- ✅ Real-time analytics and streaming data
- ✅ Data quality checks and validation
- ✅ Financial reconciliation
- ✅ KPI dashboard design
- ✅ Executive reporting
- ✅ Self-service analytics APIs
- ✅ Consulting-specific metrics (utilization, profitability, DSO)
- ✅ Data governance and lineage

**When to Use**:
- Setting up data warehouse
- Designing ETL pipelines
- Creating analytics dashboards
- Building reporting features
- Implementing KPI tracking
- Financial reconciliation
- Performance analysis
- Business intelligence

**Example Usage**:
```
@data-analytics Set up analytics infrastructure for consulting portal KPIs:
- Consultant utilization tracking (target 75%+)
- Revenue by client, project, service type
- Invoice aging and collection rate
- Project profitability analysis
- Real-time dashboard for executives
- Daily ETL from operational database
- Financial reconciliation checks
```

### 7. Advanced Planning Agent (`advanced-planning-agent.md`)

**Classification**: Meta-Agent | Planning | Architecture

**Purpose**: Strategic planning and architecture specialist for decomposing complex requirements into actionable plans.

**Key Capabilities**:
- ✅ Strategic planning and decomposition
- ✅ Architecture design and ADRs
- ✅ Risk assessment and mitigation
- ✅ Project charter definition
- ✅ Stakeholder analysis
- ✅ Scope definition
- ✅ Success criteria definition
- ✅ Timeline planning
- ✅ ROI and cost analysis

## How Custom Agents Work

Custom agents are specialized AI assistants with deep expertise in specific domains. Each agent is designed with:

1. **Domain Expertise**: Pre-configured with best practices, architectural patterns, and guidelines specific to their area
2. **Quality Standards**: Enforce coding standards, security practices, testing requirements, and compliance rules
3. **Iterative Approach**: Work through problems systematically, validating output after each step
4. **Quality Assurance**: Automatically run linters, formatters, security scans, tests, and other quality checks
5. **Consulting Domain Knowledge**: Understanding of consulting workflows, financial compliance, and business patterns

## Agent Interaction Patterns

### Single Agent Request
Request a specific agent for a focused task:

```
@consulting-dev Implement SOW approval workflow with status transitions and audit logging
```

### Multi-Agent Workflow
Agents can work together for complex features:

1. **Planning**: @advanced-planning-agent defines architecture
2. **Development**: @consulting-dev implements features
3. **Security**: @security-compliance reviews access control
4. **Testing**: @testing-qa creates comprehensive tests
5. **Infrastructure**: @devops-infra sets up deployment
6. **Analytics**: @data-analytics enables reporting

### Cross-Agent Communication
Agents reference each other's outputs:
- Development agent follows architecture decisions from planning agent
- Security agent validates implementation from development agent
- Testing agent ensures quality of development
- DevOps agent deploys tested code

## Using Agents Effectively

### 1. Be Specific and Detailed

❌ Poor: "Add authentication"
✅ Good: "Implement JWT-based authentication with refresh tokens, password hashing using bcrypt, and token expiration of 30 minutes. Include comprehensive security tests for token validation, expiration, and refresh scenarios."

### 2. Provide Context

Include relevant information:
- Existing code structure and patterns
- Integration points with other systems
- Specific requirements and constraints
- Related tasks or dependencies
- Performance/security requirements

```
@consulting-dev Implement timesheet validation. Timesheets are for projects that 
have start_date and end_date. A timesheet entry must have:
- work_date between project dates
- hours between 0 and 24
- billable_amount calculated as hours × billing_rate
- Include validation tests and API endpoint at POST /api/v1/timesheets
```

### 3. Request Tests and Documentation

Agents are configured to write tests, but be explicit:
```
@consulting-dev Implement SOW creation endpoint with:
- Unit tests for validation (90%+ coverage)
- Integration tests for workflow
- API tests for endpoint (POST /api/v1/sows)
- Documentation of endpoint and business rules
```

### 4. Security and Compliance Considerations

For security-related work, mention:
- Data sensitivity
- Compliance requirements (GDPR, SOX, HIPAA)
- Authentication/authorization needs
- External service integrations

```
@security-compliance Implement audit logging for SOW approval workflow:
- Log all status changes with timestamp, user, action
- Immutable audit trail (never delete/modify logs)
- Include in financial compliance audit reports
- Accessible only to admin and compliance team
```

### 5. Review Agent Output

While agents are expert-level, always:
1. **Review the generated code** for correctness
2. **Understand security implications** of changes
3. **Verify tests cover edge cases** thoroughly
4. **Check that secrets** are properly managed
5. **Validate performance** meets requirements

### 6. Progressive Enhancement

Use agents iteratively to enhance features:

1. First request: Core functionality
2. Second request: Error handling and edge cases
3. Third request: Performance optimization
4. Fourth request: Security hardening
5. Fifth request: Analytics and monitoring

Example:

```
# First - Core feature
@consulting-dev Create invoice generation from approved timesheets

# Second - Validation
@consulting-dev Add comprehensive validation to invoice generation:
- Prevent double-billing
- Validate rates and calculations
- Check for required fields

# Third - Performance
@devops-infra Optimize invoice generation:
- Add caching for frequently generated invoices
- Profile performance and optimize queries

# Fourth - Security
@security-compliance Harden invoice generation:
- Encrypt sensitive invoice data
- Add role-based access control
- Implement audit logging

# Fifth - Analytics
@data-analytics Add invoice analytics:
- Dashboard for invoice metrics
- Collection rate tracking
- Payment aging analysis
```

## Best Practices by Agent

### Consulting Developer
- Include consulting domain models in requests
- Reference the consulting workflow phases
- Be specific about API endpoints needed
- Specify validation rules for business logic

### Security & Compliance
- Mention regulatory requirements
- Specify who should have access
- Request audit trails for sensitive operations
- Include security testing

### FastAPI Security Developer
- Reference existing code patterns
- Specify test coverage requirements
- Mention security concerns
- Request pre-commit hook setup

### DevOps & Infrastructure
- Specify environment requirements
- Request monitoring and alerting setup
- Include disaster recovery in requests
- Request cost optimization recommendations

### Testing & QA
- Request specific test types (unit, integration, etc.)
- Specify coverage requirements
- Include edge cases and error scenarios
- Request performance benchmarks

### Data & Analytics
- Specify KPIs and metrics needed
- Request ETL pipeline details
- Include data quality requirements
- Request reconciliation checks

### Advanced Planning Agent
- Request architecture decisions documented
- Ask for risk assessment
- Request timeline and milestones
- Ask for stakeholder analysis

## Common Workflows

### Implementing a New Consulting Feature

1. **Plan** with @advanced-planning-agent
2. **Develop** API with @consulting-dev
3. **Secure** with @security-compliance
4. **Test** with @testing-qa
5. **Deploy** with @devops-infra
6. **Monitor** with @data-analytics

### Financial Compliance Update

1. **Review** requirements with @advanced-planning-agent
2. **Implement** audit trails with @consulting-dev
3. **Harden security** with @security-compliance
4. **Test thoroughly** with @testing-qa
5. **Add monitoring** with @data-analytics

### Performance Optimization

1. **Profile** with @devops-infra
2. **Optimize** code with @consulting-dev or @fastapi-security-dev
3. **Test** improvements with @testing-qa
4. **Analyze** metrics with @data-analytics

## Agent Conventions

### Naming
- Prefix requests with agent name: `@agent-name`
- Use clear, specific task descriptions
- Include context and requirements

### Output Format
Agents provide:
- Clear, documented code
- Comprehensive tests
- Security considerations
- Performance implications
- Deployment instructions

### Quality Assurance
All agent work includes:
- Passing linter/formatter checks
- Security scans completed
- Test coverage verified
- Performance validated
- Documentation provided

## Support & Troubleshooting

### If an agent fails:
1. Review the error message carefully
2. Check that requirements are clear and specific
3. Provide additional context if needed
4. Break large tasks into smaller steps
5. Verify related infrastructure is in place

### If output seems incomplete:
1. Request additional specific details
2. Ask for edge cases and error handling
3. Request more comprehensive tests
4. Ask for documentation and examples

### If performance is an issue:
1. Request profiling with @devops-infra
2. Ask @testing-qa for performance tests
3. Request optimization from development agent
4. Ask @data-analytics for metrics

## Agent Dependencies

Some agents depend on others' work:

```
Advanced Planning Agent (strategic decisions)
    ├─→ Consulting Developer (implements per plan)
    ├─→ FastAPI Security Developer (implements per plan)
    └─→ Data & Analytics (defines metrics per plan)

Security & Compliance (defines requirements)
    ├─→ Consulting Developer (implements controls)
    ├─→ FastAPI Security Developer (implements in code)
    └─→ Testing & QA (validates compliance)

Testing & QA (validates all work)
    ├─ Consulting Developer output
    ├─ FastAPI Security Developer output
    ├─ DevOps Infrastructure setup
    └─ Data & Analytics queries

DevOps & Infrastructure (enables deployment)
    ├─ Consulting Developer code
    ├─ FastAPI Security Developer code
    └─ Testing & QA validation
```

## Consulting Portal Agent Specializations

### Consulting Workflows
- @consulting-dev: Core implementation
- @security-compliance: Access control for roles
- @testing-qa: Workflow validation tests
- @data-analytics: Workflow metrics and KPIs

### Financial Management
- @consulting-dev: Invoice/payment logic
- @security-compliance: Financial controls and compliance
- @testing-qa: Financial accuracy tests
- @data-analytics: Financial reporting

### Resource Management
- @consulting-dev: Resource allocation features
- @security-compliance: Resource access control
- @testing-qa: Allocation logic tests
- @data-analytics: Resource utilization analytics

## Success Metrics

Agents are working effectively when:
- ✅ Code is production-ready on first output
- ✅ Tests achieve 80%+ coverage
- ✅ Security requirements are met
- ✅ Performance meets SLAs
- ✅ Consulting workflows work end-to-end
- ✅ Financial calculations are accurate
- ✅ Compliance requirements are satisfied
- ✅ Deployment is smooth and safe

- **Responsibilities**: Core tasks and duties
- **Best Practices**: Domain-specific guidelines
- **Tools**: Required dependencies and utilities
- **Workflows**: Step-by-step processes
- **Examples**: Common patterns and code samples
- **Checklists**: Quality gates and verification steps

## Adding New Agents

To create a new custom agent:

1. Create a new `.md` file in this directory
2. Define the agent's expertise and responsibilities
3. Include relevant best practices and examples
4. Add quality checklists and verification steps
5. Document when and how to use the agent

See `fastapi-security-dev.md` as a reference template.

## Environment Setup

Before using the FastAPI agent, ensure you have:

### Required Tools
```bash
# Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install GitHub CLI
# macOS: brew install gh
# Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md
# Windows: https://github.com/cli/cli/releases
```

### GitHub CLI Setup
```bash
# Authenticate
gh auth login

# Verify access
gh auth status

# Set secrets
gh secret set DATABASE_URL --body "postgresql://user:pass@localhost/db"
gh secret set SECRET_KEY --body "your-secret-key-here"
```

### Local Development
```bash
# Run tests with coverage
pytest --cov=app --cov-report=term-missing --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Run linting
ruff check .
mypy app/
pylint app/

# Format code
black .
isort .

# Security scan
bandit -r app/
safety check
```

## Troubleshooting

### Agent Not Following Guidelines
- Check that the agent file is in `.github/agents/`
- Ensure the file is properly formatted Markdown
- Be more explicit in your request

### Tests Failing
- Review the test output carefully
- Check that dependencies are installed
- Verify database/service connections
- Ensure environment variables are set

### Coverage Below 80%
- Ask the agent to add more test cases
- Focus on untested branches and edge cases
- Use `--cov-report=html` to see what's missing

### Security Scan Failures
- Review the bandit/safety output
- Ask the agent to fix specific vulnerabilities
- Update dependencies if needed
- Use `# nosec` sparingly and document why

## Resources

### FastAPI
- [Official Documentation](https://fastapi.tiangolo.com/)
- [Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)

### Security
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

### Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)
- [Bandit Security Scanner](https://bandit.readthedocs.io/)

## Contributing

To improve or extend the custom agents:

1. Test changes thoroughly
2. Update documentation
3. Add examples if introducing new capabilities
4. Submit a pull request with clear description

## Support

For questions or issues with custom agents:
1. Review this README and the agent definition
2. Check the troubleshooting section
3. Open an issue with details about the problem
