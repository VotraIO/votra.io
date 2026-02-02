# Consulting Portal Application Structure

This directory contains the FastAPI application code for the Votra.io consulting business portal. The application follows security best practices and clean architecture principles, with a focus on managing the complete consulting lifecycle: client engagement, SOW creation, project tracking, timesheet management, and invoice generation.

## Directory Structure

```
app/
├── __init__.py              # Package initialization with version
├── main.py                  # FastAPI app instance and middleware
├── config.py                # Application settings (Pydantic Settings)
├── dependencies.py          # Dependency injection functions
│
├── models/                  # Pydantic models (request/response)
│   ├── __init__.py
│   ├── client.py           # Client models
│   ├── sow.py              # Statement of Work models
│   ├── project.py          # Project models
│   ├── timesheet.py        # Timesheet and time entry models
│   ├── invoice.py          # Invoice and line item models
│   └── common.py           # Common response models
│
├── routers/                 # API route handlers
│   ├── __init__.py
│   ├── health.py           # Health check endpoints
│   ├── auth.py             # Authentication endpoints
│   ├── clients.py          # Client management endpoints
│   ├── sows.py             # SOW CRUD and workflow endpoints
│   ├── projects.py         # Project management endpoints
│   ├── timesheets.py       # Timesheet entry and tracking endpoints
│   ├── invoices.py         # Invoice generation and management endpoints
│   └── reports.py          # Consulting metrics and analytics endpoints
│
├── services/                # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py     # Authentication logic
│   ├── client_service.py   # Client management logic
│   ├── sow_service.py      # SOW creation, approval, state transitions
│   ├── project_service.py  # Project tracking and resource allocation
│   ├── timesheet_service.py # Time entry validation and tracking
│   └── invoice_service.py  # Invoice generation and calculation logic
│
├── database/                # Database configuration and models
│   ├── __init__.py
│   ├── base.py             # Database connection and session
│   └── models.py           # SQLAlchemy ORM models
│
└── utils/                   # Utility functions
    ├── __init__.py
    └── security.py          # Security utilities (hashing, JWT)
```

## Key Components

### Main Application (`main.py`)
- FastAPI app initialization
- CORS middleware configuration
- Security headers middleware
- Rate limiting setup
- Global exception handling
- Router inclusion

### Configuration (`config.py`)
- Environment-based settings using Pydantic
- Secure defaults for production
- Validates configuration on startup
- Centralized settings access with `get_settings()`

### Models (`models/`)
- **Pydantic models** for request/response validation
- Input sanitization and type checking
- **Consulting-specific validation**:
  - Client and company information validation
  - SOW scope, rate, and term validation
  - Project milestone and deliverable tracking
  - Timesheet hours validation against project dates and billable rates
  - Invoice calculation and payment term handling

### Routers (`routers/`)
- **Health Check**: `/health` - API health status
- **Authentication**: `/api/v1/auth/*` - Login, token refresh
- **Clients**: `/api/v1/clients/*` - Client profiles, contact information, engagement history
- **SOWs**: `/api/v1/sows/*` - Create, retrieve, approve, and manage statements of work
- **Projects**: `/api/v1/projects/*` - Project tracking, resource allocation, milestones
- **Timesheets**: `/api/v1/timesheets/*` - Time entry, tracking, and billing validation
- **Invoices**: `/api/v1/invoices/*` - Invoice generation, management, and payment tracking
- **Reports**: `/api/v1/reports/*` - Consulting metrics, project analytics, utilization reports

### Services (`services/`)
- Business logic separated from routes
- **Consulting workflow logic**:
  - Client management and contact tracking
  - SOW creation, approval workflows, and state transitions
  - Project resource allocation and milestone tracking
  - Timesheet validation (hours, rates, project dates, no double-billing)
  - Invoice generation with automatic calculations from timesheets
- Reusable across different endpoints
- Easy to test in isolation
- Database integration for persistent storage

### Database (`database/`)
- Async SQLAlchemy configuration
- **Consulting schema ORM models**:
  - `Client` - Client company and contact information
  - `User` - System users with role-based access (Admin, PM, Consultant, Client, Accountant)
  - `SOW` - Statement of Work with scope, rates, terms, and approval status
  - `Project` - Projects derived from SOWs with milestones and deliverables
  - `Resource` - Consultant/staff resource allocation to projects
  - `Timesheet` - Time entries linked to projects with billing rates
  - `Invoice` - Invoices generated from timesheets with payment terms
  - `LineItem` - Individual line items in SOWs and invoices
- Session management and transaction handling
- Migration support (Alembic) for schema evolution

### Security (`utils/security.py`)
- Password hashing with bcrypt
- JWT token creation and validation
- Secure token expiration handling
- **Role-based access control**: Enforce permissions for Admin, Project Manager, Consultant, Client, Accountant roles
- **Audit trail**: Track user actions for compliance and financial audits

## Security Features

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC):
  - **Admin**: Full system access, user management
  - **Project Manager**: SOW and project management, team oversight
  - **Consultant**: Time entry, project work, deliverable submission
  - **Client**: View SOWs, projects, timesheets, invoices (read-only where applicable)
  - **Accountant**: Invoice generation, payment processing, financial reporting
- Secure password hashing (bcrypt)
- Token expiration handling
- Audit logging for compliance

### Input Validation
- Pydantic model validation for all endpoints
- **Consulting-specific validation**:
  - Rate and pricing validation (no negative or zero rates)
  - Date range validation for projects and timesheets
  - Timesheet hours must fall within project active dates
  - Invoice calculations must match timesheet entries
  - SOW approval workflow enforced
  - No double-billing prevention (timesheets to same project checked)
- SQL injection prevention (parameterized queries via SQLAlchemy)
- XSS protection via JSON responses

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HSTS)
- `Content-Security-Policy`

### Rate Limiting
- Per-endpoint rate limits
- IP-based rate limiting
- Configurable limits

### CORS
- Configurable allowed origins
- Credential support
- Proper headers configuration

## API Endpoints

### Health Check
- `GET /health` - Health check with version info
- `GET /` - Root endpoint with API info

### Authentication
- `POST /api/v1/auth/token` - Login (OAuth2 form)
- `POST /api/v1/auth/login` - Login (JSON)
- `POST /api/v1/auth/refresh` - Refresh access token

### Clients
- `GET /api/v1/clients/` - List all clients (with pagination)
- `POST /api/v1/clients/` - Create new client
- `GET /api/v1/clients/{client_id}` - Get client details
- `PUT /api/v1/clients/{client_id}` - Update client information
- `DELETE /api/v1/clients/{client_id}` - Delete/archive client

### SOWs (Statement of Work)
- `GET /api/v1/sows/` - List SOWs (with filtering by status, client)
- `POST /api/v1/sows/` - Create new SOW
- `GET /api/v1/sows/{sow_id}` - Get SOW details
- `PUT /api/v1/sows/{sow_id}` - Update SOW
- `POST /api/v1/sows/{sow_id}/approve` - Approve SOW (PM/Admin only)
- `POST /api/v1/sows/{sow_id}/reject` - Reject SOW (PM/Admin only)
- `GET /api/v1/sows/{sow_id}/projects` - Get projects under SOW

### Projects
- `GET /api/v1/projects/` - List projects
- `POST /api/v1/projects/` - Create project (from SOW)
- `GET /api/v1/projects/{project_id}` - Get project details
- `PUT /api/v1/projects/{project_id}` - Update project
- `POST /api/v1/projects/{project_id}/assign-resource` - Allocate consultant to project
- `GET /api/v1/projects/{project_id}/timesheets` - Get all timesheets for project

### Timesheets
- `GET /api/v1/timesheets/` - List timesheets (by consultant, project, date range)
- `POST /api/v1/timesheets/` - Submit time entry
- `GET /api/v1/timesheets/{timesheet_id}` - Get timesheet details
- `PUT /api/v1/timesheets/{timesheet_id}` - Update timesheet entry
- `POST /api/v1/timesheets/{timesheet_id}/approve` - Approve timesheet (PM/Admin only)
- `DELETE /api/v1/timesheets/{timesheet_id}` - Delete time entry

### Invoices
- `GET /api/v1/invoices/` - List invoices (by client, date range, status)
- `POST /api/v1/invoices/` - Generate invoice from timesheets
- `GET /api/v1/invoices/{invoice_id}` - Get invoice details
- `PUT /api/v1/invoices/{invoice_id}` - Update invoice (before sending)
- `POST /api/v1/invoices/{invoice_id}/send` - Mark invoice as sent
- `POST /api/v1/invoices/{invoice_id}/pay` - Record payment received
- `GET /api/v1/invoices/{invoice_id}/pdf` - Download invoice as PDF

### Reports
- `GET /api/v1/reports/project-hours` - Project hours and costs
- `GET /api/v1/reports/consultant-utilization` - Consultant utilization rates
- `GET /api/v1/reports/profitability` - Project profitability analysis
- `GET /api/v1/reports/revenue` - Revenue tracking and forecasting
- `GET /api/v1/reports/outstanding-invoices` - Outstanding payment tracking

## Running the Application

### Development Mode
```bash
# Using the startup script (recommended)
./start.sh

# Or manually
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
- `SECRET_KEY` - JWT secret (generate with `openssl rand -hex 32`)
- `DATABASE_URL` - Database connection string
- `CORS_ORIGINS` - Allowed CORS origins
- See `.env.example` for all options

## Testing

Run tests with coverage:
```bash
pytest --cov=app --cov-report=term-missing
```

Run specific test files:
```bash
pytest tests/test_auth.py -v
```

## Next Steps (TODOs)

### Core Consulting Workflow Features
1. **SOW Management** - Complete approval workflow, version control, amendment tracking
2. **Project Tracking** - Milestone management, deliverable tracking, status updates
3. **Timesheet Validation** - Prevent double billing, validate against project dates and rates
4. **Invoice Generation** - Automatic invoice creation from approved timesheets
5. **Payment Processing** - Track payments, handle partial payments, late payment tracking
6. **Reporting** - Profitability, utilization, revenue forecasting, client reports

### Database Integration
1. Configure Alembic for migrations
2. Implement full consulting entity models (Client, SOW, Project, Timesheet, Invoice)
3. Add database initialization in lifespan events
4. Set up proper transaction handling for financial operations
5. Add database constraints for data integrity

### Audit & Compliance
1. Implement audit logging for all state changes (SOW approval, invoice generation, etc.)
2. Add change tracking (who made changes, when, what changed)
3. Ensure compliance with financial regulations
4. Archive historical data appropriately
5. Support audit trail queries for financial audits

### Security Enhancements
1. Implement token blacklisting for logout
2. Add two-factor authentication (2FA) for sensitive operations
3. Implement account lockout after failed attempts
4. Add security audit logging
5. Implement role-based endpoint access control validation

## Code Quality Standards

- **Format**: Black (88 char line length)
- **Linting**: Ruff, Pylint
- **Type Checking**: MyPy with strict mode
- **Security Scanning**: Bandit, Safety
- **Test Coverage**: 80% minimum target

## Contributing

1. Follow the established directory structure
2. Write tests for all new features
3. Ensure all security checks pass
4. Update documentation
5. Follow conventional commits format
