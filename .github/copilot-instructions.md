# Copilot Instructions for Votra.io

## Project Overview

**Votra.io** is a comprehensive consulting and IT business portal designed to streamline the consulting workflow from initial client engagement through project completion and invoicing. The platform manages the complete consulting lifecycle including SOW creation, project tracking, resource allocation, time tracking, and automated invoice generation. The project prioritizes:
- OWASP-compliant secure development
- 80%+ test coverage with pytest
- Code quality (black, ruff, mypy, pylint)
- CI/CD automation via GitHub Actions
- Industry-standard consulting workflows

**Tech Stack**: FastAPI (Python 3.10+), SQLAlchemy, Pydantic v2, JWT authentication, bcrypt, SQLite/PostgreSQL

---

## Architecture Essentials

### Layered Architecture (see [app/README.md](app/README.md))
```
Routers (consulting endpoints) → Services (workflow logic) → Database (ORM/models) → Utils (security, helpers)
```
- **Routers** ([app/routers/](app/routers/)): HTTP endpoints for clients, SOWs, projects, timesheets, invoices
- **Services** ([app/services/](app/services/)): Consulting workflow logic, invoice generation, project management
- **Database** ([app/database/](app/database/)): SQLAlchemy ORM models for consulting entities
- **Models** ([app/models/](app/models/)): Pydantic schemas for SOWs, projects, timesheets, invoices

### Application Setup ([app/main.py](app/main.py))
- FastAPI initialization with lifespan context manager
- CORS configured for development/production
- Rate limiting via `slowapi` (60 req/min by default, configurable)
- Security headers middleware (CSP, X-Frame-Options, HSTS, etc.)
- Exception handlers for rate limiting

### Configuration ([app/config.py](app/config.py))
- `Settings` class using `pydantic_settings.BaseSettings`
- Loads from `.env` file, validates with `field_validator`
- **Key settings**: `SECRET_KEY` (32+ chars, required), `algorithm` (HS256), JWT expiration, CORS origins, rate limits
- Use `get_settings()` for singleton access

---

## Critical Developer Workflows

### Testing (80% coverage target)
```bash
# Run all tests with coverage report
pytest --cov=app --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run with markers
pytest -m "not slow" --cov=app
```
**Test Configuration**: [tests/conftest.py](tests/conftest.py) sets up `TestClient`, disables rate limiting, uses in-memory SQLite for tests. Tests inherit from isolated fixtures.

### Code Quality
```bash
# Format
black .
isort .

# Lint & type check
ruff check . --fix
mypy app/
pylint app/

# Pre-commit hooks (auto-run on commit)
pre-commit install
```

### Security & CI/CD
```bash
# Manual security scans
bandit -r app/
safety check

# GitHub Actions workflows (auto on push/PR)
# - .github/workflows/test.yml (Python 3.10, 3.11, 3.12)
# - .github/workflows/lint.yml (black, ruff, mypy, pylint)
# - .github/workflows/security.yml (bandit, safety, CodeQL)
```

### Running Locally
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt requirements-dev.txt

# Generate SECRET_KEY
openssl rand -hex 32  # Copy to .env

# Start server
uvicorn app.main:app --reload  # http://localhost:8000

# Or use startup script
./start.sh
```

---

## Project-Specific Patterns & Conventions

### API Structure - Consulting Workflow Endpoints
- **Versioned endpoints**: `/api/v1/*` with domain-specific grouping
- **Core resources**:
  - `/api/v1/clients/*` - Client management and profiles
  - `/api/v1/sows/*` - Statement of Work creation, management, and approval
  - `/api/v1/projects/*` - Project tracking and resource allocation
  - `/api/v1/timesheets/*` - Time entry and billing tracking
  - `/api/v1/invoices/*` - Invoice generation and management
  - `/api/v1/reports/*` - Consulting metrics and analytics
- **Pattern**: Each resource follows standard CRUD operations with workflow-specific states

### Authentication & Security
- **JWT with bcrypt**: `utils/security.py` handles token creation, password hashing
- **Role-based access**: Admin, Project Manager, Consultant, Client, Accountant roles
- **Password requirements**: 8+ chars, uppercase, lowercase, number (enforced in Pydantic models)
- **Token expiration**: Access tokens (30 min), refresh tokens (7 days) - configurable in `.env`
- **Pattern**: Use `Depends(get_current_user)` with role validation for endpoint access

### Input Validation - Consulting Domain
- **All** request bodies must use Pydantic models (in `models/` directory)
- **Consulting models**: `Client`, `SOW`, `Project`, `Timesheet`, `Invoice`, `LineItem`
- **Pattern**: Define separate request/response models (e.g., `SOWCreate` vs `SOWResponse`)
- **Field validators**: Use `@field_validator` for business logic (e.g., SOW rate validation, timesheet hours)
- **Example**: Validate that project billing rate ≥ minimum consulting rate, timesheet entries fall within project dates

### Database Integration - Consulting Schema (Async SQLAlchemy)
- **Session management**: [app/database/base.py](app/database/base.py) configures async engine & session maker
- **Core models**: Client, SOW, Project, Resource, Timesheet, Invoice, LineItem, PaymentTerm
- **Relationships**: Projects belong to SOWs, Timesheets reference Projects, Invoices aggregate Timesheets
- **Pattern**: Inject `Session` dependency via `Depends(get_db)` for all consulting operations
- **Migrations**: Alembic handles schema versioning (critical for workflow state changes)

### Error Handling
- FastAPI automatically converts Pydantic validation errors to 422 responses
- Raise `HTTPException` for custom error codes with proper status codes
- All exceptions include proper logging (to be added in production)

### Rate Limiting
- **Configured**: 60 req/min per IP for anonymous, 300 req/min for authenticated (`rate_limit_per_minute` in config)
- **Pattern**: Apply decorator `@limiter.limit("60/minute")` to public routes, higher for internal APIs
- **Per-route override**: Critical operations (invoicing, SOW approval) may have tighter limits

---

## Key Files Reference

| File | Purpose |
|------|---------|
| [app/main.py](app/main.py) | FastAPI app initialization, middleware, router inclusion |
| [app/config.py](app/config.py) | Settings management (Pydantic BaseSettings) |
| [app/dependencies.py](app/dependencies.py) | Dependency injection functions (get_settings, get_db, etc.) |
| [app/routers/](app/routers/) | API endpoint handlers (health, auth, users) |
| [app/services/](app/services/) | Business logic (auth_service, user_service) |
| [app/models/](app/models/) | Pydantic request/response schemas |
| [app/database/](app/database/) | SQLAlchemy ORM setup and models |
| [app/utils/security.py](app/utils/security.py) | JWT, password hashing utilities |
| [tests/conftest.py](tests/conftest.py) | Pytest fixtures and test configuration |
| [.github/workflows/](../.github/workflows/) | GitHub Actions CI/CD pipelines |

---

## When to Reach Out - Consulting Workflow Context

- **New consulting endpoints**: Consider workflow state transitions, audit trails for compliance, Pydantic validation
- **SOW/Invoice logic**: Ensure calculations are auditable, handle edge cases (scope changes, rate changes, corrections)
- **Timesheet features**: Validate against project dates/rates, prevent double billing, flag discrepancies
- **Workflow transitions**: Document state changes (e.g., SOW pending → approved → in-progress → completed)
- **Security & audit**: Track who made changes, when, for financial compliance and audit trails
- **Database schemas**: Use strong foreign keys, constraints for data integrity in financial records

---

## Reference Documentation

- **FastAPI Docs**: [python-fastapi.org](https://fastapi.tiangolo.com)
- **Pydantic v2**: [docs.pydantic.dev](https://docs.pydantic.dev)
- **SQLAlchemy Async**: [docs.sqlalchemy.org/orm/extensions/asyncio](https://docs.sqlalchemy.org/orm/extensions/asyncio)
- **Project Architecture**: [docs/architecture/01-architecture-overview.md](docs/architecture/01-architecture-overview.md)
- **Custom Agent**: [@fastapi-security-dev](../agents/fastapi-security-dev.md) - Use for complex security/testing tasks
