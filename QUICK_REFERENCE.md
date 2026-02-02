# Consulting Portal Quick Reference

## Quick Start Commands

### Invoke the Agent for Consulting Features
```
@fastapi-security-dev [your consulting workflow request]
```

## Common Use Cases

### 1. Client Management
```
@fastapi-security-dev Create client management endpoints with company info, 
contact details, billing address, and engagement history tracking.
```

### 2. SOW Management
```
@fastapi-security-dev Implement SOW creation and approval workflow with scope, 
deliverables, timeline, rates, and approval status tracking.
```

### 3. Project Tracking
```
@fastapi-security-dev Build project management from SOWs with resource 
allocation, milestone tracking, and deliverable management.
```

### 4. Timesheet Management
```
@fastapi-security-dev Create timesheet endpoints with hour entry, validation 
against project dates/rates, and prevention of double-billing.
```

### 5. Invoice Generation
```
@fastapi-security-dev Implement automated invoice generation from timesheets 
with calculation, payment term tracking, and payment status.
```

### 6. Reporting
```
@fastapi-security-dev Build consulting reports for project profitability, 
consultant utilization, revenue tracking, and outstanding payments.
```

### 7. Audit & Compliance
```
@fastapi-security-dev Add audit logging for all state changes (SOW approval, 
invoice generation) and financial compliance tracking.
```

### 8. Role-Based Access
```
@fastapi-security-dev Implement role-based access control for Admin, PM, 
Consultant, Client, and Accountant roles with appropriate permissions.
```

## Agent Capabilities Checklist

When the agent completes a consulting task, it will ensure:

- [x] FastAPI best practices for consulting workflows
- [x] Security best practices (OWASP, bcrypt, JWT)
- [x] Role-based access control implementation
- [x] Consulting domain validation (rates, dates, billing)
- [x] Type hints on all functions
- [x] Pydantic models for all data validation
- [x] Unit tests written and passing (85%+ coverage)
- [x] Security tests included
- [x] Code formatted (black, isort)
- [x] Linting passed (ruff, pylint, mypy)
- [x] Security scans passed (bandit, safety)
- [x] No secrets in code
- [x] Environment variables documented
- [x] Error handling implemented
- [x] Docstrings added
- [x] Audit logging for state changes (consulting-specific)
- [x] Financial validation rules enforced
- [x] Compliance requirements met

## Local Development Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Setup environment
cp .env.example .env
# Edit .env with your values

# 4. Install pre-commit hooks
pre-commit install

# 5. Run tests
pytest --cov=app --cov-report=html

# 6. Run linting
black .
isort .
ruff check .
mypy app/

# 7. Run security scans
bandit -r app/
safety check
```

## GitHub Secrets Setup

```bash
# Authenticate with GitHub
gh auth login

# Set application secrets
gh secret set SECRET_KEY --body "$(openssl rand -hex 32)"
gh secret set DATABASE_URL --body "postgresql://user:pass@host/db"

# Set CI/CD secrets (optional)
gh secret set CODECOV_TOKEN --body "your-codecov-token"

# List all secrets
gh secret list
```

## Testing Commands

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=term-missing

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Code Quality Commands

```bash
# Format all code
black .
isort .

# Check formatting without changes
black --check .
isort --check-only .

# Lint with ruff
ruff check .

# Auto-fix ruff issues
ruff check . --fix

# Type check with mypy
mypy app/

# Lint with pylint
pylint app/
```

## Security Scanning Commands

```bash
# Scan code for security issues
bandit -r app/

# Generate JSON report
bandit -r app/ -f json -o bandit-report.json

# Check dependencies for vulnerabilities
safety check

# Update safety database
safety check --update
```

## CI/CD Workflows

The following workflows run automatically:

### On Push/PR to main or develop:
- **test.yml**: Runs tests on Python 3.10, 3.11, 3.12
- **lint.yml**: Checks formatting and linting
- **security.yml**: Scans for vulnerabilities

### Weekly (Sundays at midnight):
- **security.yml**: Scheduled security scan

### Required Checks for Merging:
All workflows must pass before merging to main/develop.

## Troubleshooting

### Tests Failing
```bash
# Run with verbose output to see details
pytest -v

# Run single test for debugging
pytest tests/test_auth.py::test_login -v

# Check coverage gaps
pytest --cov=app --cov-report=term-missing
```

### Coverage Too Low
```bash
# Generate HTML report to see gaps
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Focus on missing lines
pytest --cov=app --cov-report=term-missing
```

### Linting Errors
```bash
# Auto-fix what's possible
black .
isort .
ruff check . --fix

# Check remaining issues
mypy app/
pylint app/
```

### Security Scan Failures
```bash
# View detailed report
bandit -r app/ -v

# Check specific file
bandit app/routers/auth.py

# Update vulnerable dependencies
pip list --outdated
pip install --upgrade [package]
```

## Best Practices Reminders

### Security
- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all user inputs with Pydantic
- Hash passwords with bcrypt
- Use parameterized queries
- Implement rate limiting
- Add security headers

### Testing
- Write tests before or with code
- Aim for 80%+ coverage
- Test happy path and edge cases
- Mock external dependencies
- Test security scenarios
- Keep tests isolated

### Code Quality
- Use type hints everywhere
- Write descriptive docstrings
- Keep functions small and focused
- Follow DRY principle
- Use meaningful names
- Format code consistently

### Documentation
- Update README with new features
- Document environment variables
- Add API documentation
- Include examples
- Document security requirements

## Resources

- [Custom Agent Details](.github/agents/fastapi-security-dev.md)
- [Agent Usage Guide](.github/agents/README.md)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Pytest Docs](https://docs.pytest.org/)
