# MVP Implementation Checklist - Step by Step

**Project**: Votra.io Consulting Portal - MVP Launch
**Status**: Ready to Begin
**Total Tasks**: 40+
**Estimated Duration**: 8 weeks

---

## Phase 1: Core Infrastructure ✅ READY

### Week 1: Database & ORM

**[ ] Task 1.1: Initialize Alembic Migrations**
- [x] Install alembic: `pip install alembic`
- [x] Initialize: `alembic init alembic`
- [x] Create `alembic.ini` with database URL
- [ ] Create initial migration with User model
- [ ] Test migration: `alembic upgrade head`
- **Files**: `alembic/`, `alembic.ini`, `alembic/env.py`
- **Validation**: Migration creates users table in database

**[x] Task 1.2: Define SQLAlchemy ORM Models**
- [x] Create `app/database/models.py`
- [x] Implement User model with fields: id, email, username, hashed_password, full_name, role, is_active, created_at
- [x] Implement Client model with fields: id, name, email, phone, company, billing_address, payment_terms, is_active, created_at
- [x] Implement SOW model with fields: id, client_id, title, description, start_date, end_date, rate, total_budget, status, created_by, approved_by, approved_at, created_at, updated_at
- [x] Implement Project model with fields: id, sow_id, name, description, status, start_date, end_date, budget, created_by, created_at, updated_at
- [x] Implement Timesheet model with fields: id, project_id, consultant_id, work_date, hours_logged, billing_rate, billable_amount, is_billable, notes, status, submitted_at, approved_by, approved_at, created_at, updated_at
- [x] Implement Invoice model with fields: id, client_id, project_id, invoice_number, invoice_date, due_date, subtotal, tax_amount, discount_amount, total_amount, status, payment_date, created_at, updated_at
- [x] Implement LineItem model with fields: id, invoice_id, description, quantity, unit_price, line_total
- [x] Implement AuditLog model with fields: id, user_id, action, entity_type, entity_id, old_values, new_values, description, created_at
- [x] Add relationships between models
- [x] Add constraints (foreign keys, unique constraints)
- [x] Add indexes for performance
- **Files**: `app/database/models.py`
- **Validation**: `python -c "from app.database.models import *; print('All models imported successfully')"`

**[ ] Task 1.3: Create Database Migrations**
- [ ] Create migration script for initial schema
- [ ] Create migration for User table
- [ ] Create migration for Client table
- [ ] Create migration for SOW table
- [ ] Create migration for Project table
- [ ] Create migration for Timesheet table
- [ ] Create migration for Invoice table
- [ ] Create migration for LineItem table
- [ ] Create migration for AuditLog table
- [ ] Test all migrations on clean database
- **Command**: `alembic revision --autogenerate -m "Initial schema"`
- **Validation**: `alembic upgrade head` completes successfully

**[ ] Task 1.4: Set up Database Connection**
- [ ] Update `app/database/base.py` with async engine configuration
- [ ] Add database URL to `app/config.py`
- [ ] Create async session factory
- [ ] Add `get_db()` dependency function to `app/dependencies.py`
- [ ] Test connection on startup
- **Files**: `app/database/base.py`, `app/config.py`, `app/dependencies.py`
- **Validation**: Server starts without database connection errors

### Week 2: Pydantic Models & Authentication

**[ ] Task 2.1: Create Pydantic Request/Response Models**
- [ ] `app/models/user.py`: UserCreate, UserUpdate, UserResponse
- [ ] `app/models/client.py`: ClientCreate, ClientUpdate, ClientResponse, ClientList
- [ ] `app/models/sow.py`: SOWBase, SOWCreate, SOWUpdate, SOWResponse, SOWList, SOWApprove
- [ ] `app/models/project.py`: ProjectCreate, ProjectUpdate, ProjectResponse, ProjectList
- [ ] `app/models/timesheet.py`: TimesheetCreate, TimesheetUpdate, TimesheetResponse, TimesheetList
- [ ] `app/models/invoice.py`: InvoiceCreate, InvoiceResponse, InvoiceList, PaymentRecord
- [ ] Add field validators for all models
- [ ] Add password strength validation (8+ chars, uppercase, lowercase, number)
- [ ] Add email validation
- [ ] Add date range validation (end_date > start_date)
- [ ] Add financial field validation (positive amounts)
- **Files**: `app/models/*.py`
- **Validation**: `pytest tests/test_models.py -v`

**[ ] Task 2.2: Implement Password Security**
- [ ] Update `app/utils/security.py`:
  - [ ] Add `verify_password()` function using bcrypt
  - [ ] Add `get_password_hash()` function using bcrypt
  - [ ] Test password hashing works correctly
- [ ] Update User model to hash passwords on creation
- **Files**: `app/utils/security.py`
- **Validation**: Passwords hash correctly and verify works

**[ ] Task 2.3: Implement JWT Token Management**
- [ ] Update `app/utils/security.py`:
  - [ ] Add `create_access_token()` function
  - [ ] Add `verify_token()` function
  - [ ] Add token expiration handling
  - [ ] Add refresh token support
- [ ] Add token configuration to `app/config.py`:
  - [ ] `access_token_expire_minutes` (default 30)
  - [ ] `refresh_token_expire_days` (default 7)
  - [ ] `algorithm` (HS256)
- [ ] Test token creation and validation
- **Files**: `app/utils/security.py`, `app/config.py`
- **Validation**: Tokens are created, validated, and expire correctly

**[ ] Task 2.4: Add Authentication Dependencies**
- [ ] Update `app/dependencies.py`:
  - [ ] Add `oauth2_scheme` OAuth2PasswordBearer
  - [ ] Add `get_current_user()` function
  - [ ] Add `get_current_active_user()` function
  - [ ] Add `require_role()` factory function for RBAC
- [ ] Test dependency injection works
- **Files**: `app/dependencies.py`
- **Validation**: Auth dependencies can be injected into routers

**[ ] Task 2.5: Create Authentication Router**
- [ ] Create `app/routers/auth.py`:
  - [ ] POST `/api/v1/auth/register` - User registration
  - [ ] POST `/api/v1/auth/login` - User login with JWT token
  - [ ] POST `/api/v1/auth/refresh` - Refresh access token
  - [ ] GET `/api/v1/auth/me` - Get current user info
  - [ ] POST `/api/v1/auth/logout` - Token invalidation (blacklist or DB)
- [ ] Add proper error handling (409 conflict if user exists, 401 unauthorized)
- [ ] Add input validation with Pydantic
- [ ] Test all endpoints with valid and invalid inputs
- **Files**: `app/routers/auth.py`
- **Validation**: `pytest tests/test_auth.py -v` passes with 100% coverage

**[ ] Task 2.6: Integration Tests for Auth**
- [ ] Create `tests/test_auth.py`:
  - [ ] Test user registration (success, duplicate email, validation errors)
  - [ ] Test user login (success, wrong credentials, inactive user)
  - [ ] Test token refresh
  - [ ] Test current user endpoint
  - [ ] Test logout / token invalidation
  - [ ] Test protected endpoints without token (401)
  - [ ] Test protected endpoints with invalid token (401)
  - [ ] Test role-based access control (403 for wrong role)
- [ ] Run tests: `pytest tests/test_auth.py -v --cov=app.routers.auth`
- **Files**: `tests/test_auth.py`
- **Validation**: All auth tests pass, coverage ≥ 95%

---

## Phase 2: Consulting Workflow ✅ READY

### Week 3: Client & SOW Management

**[ ] Task 3.1: Create Client Router**
- [ ] Create `app/routers/clients.py`:
  - [ ] POST `/api/v1/clients` - Create client (admin, pm only)
  - [ ] GET `/api/v1/clients` - List clients (paginated)
  - [ ] GET `/api/v1/clients/{id}` - Get client detail
  - [ ] PUT `/api/v1/clients/{id}` - Update client (admin, pm only)
  - [ ] DELETE `/api/v1/clients/{id}` - Deactivate client (admin only)
- [ ] Add RBAC enforcement
- [ ] Add 404 handling
- **Files**: `app/routers/clients.py`
- **Validation**: `pytest tests/test_clients.py -v`

**[ ] Task 3.2: Create SOW Router & Service**
- [ ] Create `app/services/sow_service.py` with business logic:
  - [ ] `create_sow()` - Create SOW with validation
  - [ ] `approve_sow()` - Approve SOW, trigger project creation
  - [ ] `reject_sow()` - Reject SOW with reason
  - [ ] `submit_sow()` - Submit for approval
  - [ ] Calculate SOW total hours from timesheets (for reporting)
- [ ] Create `app/routers/sows.py`:
  - [ ] POST `/api/v1/sows` - Create SOW (status: draft)
  - [ ] GET `/api/v1/sows` - List SOWs with filtering (status, client_id)
  - [ ] GET `/api/v1/sows/{id}` - Get SOW detail
  - [ ] PUT `/api/v1/sows/{id}` - Update SOW (only if draft)
  - [ ] POST `/api/v1/sows/{id}/submit` - Submit for approval
  - [ ] POST `/api/v1/sows/{id}/approve` - Approve or reject
- [ ] Add workflow state validation (can only edit draft, can only approve pending)
- [ ] Add audit logging for state changes
- **Files**: `app/services/sow_service.py`, `app/routers/sows.py`
- **Validation**: `pytest tests/test_sows.py -v`

**[ ] Task 3.3: Add Audit Logging**
- [ ] Create `app/utils/audit.py`:
  - [ ] `log_audit()` function to create AuditLog entries
  - [ ] Track user, action, entity_type, entity_id, timestamp
  - [ ] Store old/new values for updates
- [ ] Add audit logging to SOW state changes
- [ ] Add audit logging to all financial operations
- **Files**: `app/utils/audit.py`
- **Validation**: Audit logs created for all state transitions

### Week 3-4: Project & Timesheet Management

**[ ] Task 4.1: Create Project Router**
- [ ] Create `app/routers/projects.py`:
  - [ ] POST `/api/v1/projects` - Create project from approved SOW
  - [ ] GET `/api/v1/projects` - List projects with filtering
  - [ ] GET `/api/v1/projects/{id}` - Get project detail
  - [ ] PUT `/api/v1/projects/{id}` - Update project (limited fields)
  - [ ] POST `/api/v1/projects/{id}/close` - Close project
- [ ] Create `app/services/project_service.py`:
  - [ ] `create_project_from_sow()` - Validate SOW approved, create project
  - [ ] `get_project_summary()` - Total hours, billable amount, status
- [ ] RBAC: pm only can create/modify
- **Files**: `app/routers/projects.py`, `app/services/project_service.py`
- **Validation**: `pytest tests/test_projects.py -v`

**[ ] Task 4.2: Create Timesheet Router & Service**
- [ ] Create `app/services/timesheet_service.py`:
  - [ ] `validate_timesheet_entry()` - Check dates, hours, rates
  - [ ] `calculate_billable_amount()` - hours × rate
  - [ ] `get_timesheet_summary()` - Total hours/amount for period
  - [ ] `approve_timesheet()` - PM approval workflow
- [ ] Create `app/routers/timesheets.py`:
  - [ ] POST `/api/v1/timesheets` - Submit timesheet (consultant only)
  - [ ] GET `/api/v1/timesheets` - List with filtering (date range, project, consultant)
  - [ ] GET `/api/v1/timesheets/{id}` - Get timesheet detail
  - [ ] PUT `/api/v1/timesheets/{id}` - Update (draft only, consultant)
  - [ ] POST `/api/v1/timesheets/{id}/approve` - Approve (pm only)
  - [ ] POST `/api/v1/timesheets/{id}/reject` - Reject (pm only)
- [ ] Validation:
  - [ ] Hours must be 0-24
  - [ ] work_date must be within project dates
  - [ ] consultant_id must be team member
  - [ ] billing_rate must match project rate
- **Files**: `app/services/timesheet_service.py`, `app/routers/timesheets.py`
- **Validation**: `pytest tests/test_timesheets.py -v`

### Week 4: Invoice Management

**[ ] Task 5.1: Create Invoice Service**
- [ ] Create `app/services/invoice_service.py`:
  - [ ] `generate_invoice()` - Create from approved timesheets
    - [ ] Calculate subtotal from timesheets
    - [ ] Apply tax (10% for MVP)
    - [ ] Create line items
    - [ ] Mark timesheets as invoiced
  - [ ] `validate_invoice_totals()` - Check calculations
  - [ ] `get_invoice_detail()` - With line items
  - [ ] `calculate_days_overdue()` - For reporting
- [ ] Use Decimal for all financial calculations (accuracy)
- **Files**: `app/services/invoice_service.py`
- **Validation**: Invoice calculations are accurate (unit tested)

**[ ] Task 5.2: Create Invoice Router**
- [ ] Create `app/routers/invoices.py`:
  - [ ] POST `/api/v1/invoices` - Generate from timesheets
  - [ ] GET `/api/v1/invoices` - List with filtering (status, client, date range)
  - [ ] GET `/api/v1/invoices/{id}` - Get invoice detail with line items
  - [ ] POST `/api/v1/invoices/{id}/send` - Mark sent (draft → sent)
  - [ ] POST `/api/v1/invoices/{id}/mark-paid` - Record payment (admin/accountant)
  - [ ] GET `/api/v1/invoices/{id}/pdf` - Generate PDF (future: nice-to-have)
- [ ] RBAC:
  - [ ] Clients can only view their own invoices
  - [ ] PMs can create/send
  - [ ] Accountants can mark paid
- [ ] Error handling:
  - [ ] Cannot create invoice without approved timesheets
  - [ ] Cannot mark paid if already paid
  - [ ] Cannot send if not draft
- **Files**: `app/routers/invoices.py`
- **Validation**: `pytest tests/test_invoices.py -v`

**[ ] Task 5.3: Create Report/Analytics Router (Optional for MVP)**
- [ ] GET `/api/v1/reports/revenue` - Revenue by client/period
- [ ] GET `/api/v1/reports/utilization` - Consultant utilization
- [ ] GET `/api/v1/reports/overdue-invoices` - Overdue payment tracking
- **Files**: `app/routers/reports.py`
- **Validation**: Reports return correct aggregated data

---

## Phase 3: Frontend Integration ✅ READY

### Week 5: Frontend Setup & Serving

**[ ] Task 6.1: Setup Static File Serving**
- [ ] Update `app/main.py`:
  - [ ] Import StaticFiles and FileResponse
  - [ ] Add middleware to serve static files from `/static` directory
  - [ ] Add catch-all route for SPA routing (serve index.html)
- [ ] Create `static/` directory structure
- [ ] Create `static/index.html` template
- **Files**: `app/main.py`, `static/`
- **Validation**: Access `http://localhost:8000/` returns index.html

**[ ] Task 6.2: Initialize React Frontend Project**
- [ ] In `static/` directory: `npx create-react-app .`
- [ ] Or use Vite: `npm create vite@latest . -- --template react-ts`
- [ ] Install dependencies: react-router-dom, axios, zustand/redux (state)
- [ ] Remove default CSS and replace with modern framework (Tailwind/Material-UI)
- [ ] Create folder structure: components/, pages/, services/, hooks/
- [ ] Build: `npm run build` → outputs to `build/` (will be served from FastAPI)
- **Files**: `static/package.json`, `static/src/`, `static/public/`
- **Validation**: Frontend builds successfully: `npm run build`

**[ ] Task 6.3: Create API Client Service**
- [ ] Create `static/src/services/api.ts`:
  - [ ] Axios instance with base URL
  - [ ] Request interceptor (add JWT token)
  - [ ] Response interceptor (handle 401, refresh token)
  - [ ] Auth methods: login(), register(), getMe()
  - [ ] Client methods: list, create, update, delete
  - [ ] SOW methods: list, create, submit, approve
  - [ ] Project methods: list, create, update
  - [ ] Timesheet methods: list, create, approve
  - [ ] Invoice methods: list, view, send, markPaid
- **Files**: `static/src/services/api.ts`
- **Validation**: API client calls work in browser console

**[ ] Task 6.4: Create Authentication UI & Flows**
- [ ] Create `static/src/pages/Login.tsx`:
  - [ ] Email and password inputs
  - [ ] Submit button
  - [ ] Error messages
  - [ ] Link to register
  - [ ] Store JWT token in localStorage on success
  - [ ] Redirect to dashboard
- [ ] Create `static/src/pages/Register.tsx`:
  - [ ] Email, username, password, confirm password inputs
  - [ ] Password strength indicator
  - [ ] Submit and error handling
  - [ ] Redirect to login on success
- [ ] Create auth context/store:
  - [ ] Track authenticated user
  - [ ] Track token
  - [ ] Provide logout function
  - [ ] Auto-redirect to login if not authenticated
- [ ] Create ProtectedRoute component:
  - [ ] Check if user is authenticated
  - [ ] Redirect to login if not
  - [ ] Show component if authenticated
- **Files**: `static/src/pages/Login.tsx`, `static/src/pages/Register.tsx`, `static/src/context/AuthContext.tsx`
- **Validation**: Login flow works end-to-end

### Week 5-6: Core Feature UIs

**[ ] Task 7.1: Create Dashboard Page**
- [ ] Display welcome message with user name
- [ ] Show metrics:
  - [ ] Active SOWs count
  - [ ] Active Projects count
  - [ ] Pending Timesheets count
  - [ ] Outstanding Invoices count
- [ ] Display recent activity (last 5 SOWs, Projects, Timesheets)
- [ ] Quick action buttons (Create SOW, Submit Timesheet, etc.)
- [ ] Role-based content (show/hide based on user role)
- **Files**: `static/src/pages/Dashboard.tsx`
- **Validation**: Dashboard loads and displays data

**[ ] Task 7.2: Create SOW Management UI**
- [ ] SOW List Page:
  - [ ] Table with columns: title, client, status, created_date, actions
  - [ ] Filtering by status and client
  - [ ] Pagination
  - [ ] "Create New SOW" button
  - [ ] View/Edit/Delete actions
- [ ] SOW Detail Page:
  - [ ] Display all SOW fields (read-only for approved)
  - [ ] Show approval status and history
  - [ ] Submit/Approve buttons (role-based)
- [ ] SOW Create/Edit Form:
  - [ ] Client selector (dropdown)
  - [ ] Title, description inputs
  - [ ] Date range picker
  - [ ] Rate and budget inputs
  - [ ] Submit button
  - [ ] Validation messages
- **Files**: `static/src/pages/SOWs/SOWList.tsx`, `static/src/pages/SOWs/SOWDetail.tsx`, `static/src/components/SOW/SOWForm.tsx`
- **Validation**: SOW CRUD operations work in UI

**[ ] Task 7.3: Create Project Management UI**
- [ ] Project List Page:
  - [ ] Table: name, client, SOW, status, dates
  - [ ] Filtering by status and client
  - [ ] Create New button (from approved SOW)
- [ ] Project Detail Page:
  - [ ] Display project info
  - [ ] List timesheets for project
  - [ ] Show project summary (total hours, billable amount)
- **Files**: `static/src/pages/Projects/*.tsx`
- **Validation**: Project CRUD works

**[ ] Task 7.4: Create Timesheet Entry UI**
- [ ] Timesheet List Page:
  - [ ] Table: date, project, hours, rate, total, status
  - [ ] Filtering by date range and project
  - [ ] Create New button
  - [ ] Approve button (PM only)
- [ ] Timesheet Form:
  - [ ] Project selector
  - [ ] Date picker
  - [ ] Hours input (0-24)
  - [ ] Auto-calculate billing rate from project
  - [ ] Auto-calculate total (hours × rate)
  - [ ] Notes field
  - [ ] Submit button
  - [ ] Validation
- **Files**: `static/src/pages/Timesheets/*.tsx`, `static/src/components/Timesheet/TimesheetForm.tsx`
- **Validation**: Timesheet entry works end-to-end

**[ ] Task 7.5: Create Invoice Management UI**
- [ ] Invoice List Page:
  - [ ] Table: invoice_number, client, total, status, due_date
  - [ ] Filtering by status and date range
  - [ ] Create New button
  - [ ] View/Send/MarkPaid actions
- [ ] Invoice Detail Page:
  - [ ] Display invoice header (number, date, due, client)
  - [ ] Line items table (description, quantity, unit_price, total)
  - [ ] Summary (subtotal, tax, total)
  - [ ] Status and actions
- **Files**: `static/src/pages/Invoices/*.tsx`
- **Validation**: Invoice list and detail work

**[ ] Task 7.6: Create Layout Components**
- [ ] Navbar component:
  - [ ] User menu (profile, logout)
  - [ ] Logo/brand
  - [ ] Role badge
- [ ] Sidebar component:
  - [ ] Navigation menu (Dashboard, Clients, SOWs, Projects, Timesheets, Invoices)
  - [ ] Role-based menu items
  - [ ] Collapse/expand toggle
- [ ] Main Layout:
  - [ ] Combine Navbar and Sidebar
  - [ ] Main content area
  - [ ] Responsive design
- **Files**: `static/src/components/Layout/*.tsx`
- **Validation**: Navigation works across pages

---

## Phase 4: Quality & Launch ✅ READY

### Week 7: Testing & Code Quality

**[ ] Task 8.1: Comprehensive Unit Tests**
- [ ] `tests/test_models.py`:
  - [ ] Validate all model fields and constraints
  - [ ] Test relationships
  - [ ] Test __repr__ methods
- [ ] `tests/test_services.py`:
  - [ ] Test business logic in service layer
  - [ ] Test validations
  - [ ] Test error cases
- [ ] Test coverage: `pytest tests/ --cov=app --cov-report=html`
- [ ] Target: ≥80% coverage
- **Files**: `tests/`
- **Validation**: `pytest` passes with coverage report

**[ ] Task 8.2: Integration Tests**
- [ ] `tests/test_workflows.py`:
  - [ ] Test end-to-end: Create Client → SOW → Project → Timesheet → Invoice
  - [ ] Test state transitions
  - [ ] Test role-based access throughout workflow
  - [ ] Test error handling
- [ ] **Command**: `pytest tests/test_workflows.py -v`
- **Files**: `tests/test_workflows.py`
- **Validation**: All workflows pass

**[ ] Task 8.3: API Endpoint Tests**
- [ ] Each router has corresponding test file
- [ ] Test all CRUD operations
- [ ] Test authentication required endpoints
- [ ] Test role-based access control
- [ ] Test error responses (400, 401, 403, 404, 409)
- [ ] **Command**: `pytest tests/test_*.py -v --cov=app`
- **Files**: `tests/test_*.py`
- **Validation**: All endpoints tested, ≥95% coverage for routes

**[ ] Task 8.4: Code Quality Checks**
- [ ] **Formatting**: `black app/ tests/` ✓
- [ ] **Import sorting**: `isort app/ tests/` ✓
- [ ] **Linting**: `ruff check app/ tests/` ✓
- [ ] **Type checking**: `mypy app/` ✓
- [ ] **Security**: `bandit -r app/` ✓
- [ ] **Dependencies**: `safety check` ✓
- [ ] Run GitHub Actions locally (act) or via push
- **Validation**: All checks pass

**[ ] Task 8.5: Performance Optimization**
- [ ] Database query optimization:
  - [ ] Add indexes to frequently queried columns
  - [ ] Use eager loading for relationships where needed
  - [ ] Avoid N+1 queries
- [ ] API performance:
  - [ ] Measure response times
  - [ ] Target: <200ms p95 for most endpoints
- [ ] Frontend optimization:
  - [ ] Minify and bundle JavaScript/CSS
  - [ ] Lazy load routes
  - [ ] Optimize images
- **Validation**: Load testing shows good performance

### Week 8: Documentation & Deployment

**[ ] Task 9.1: Documentation**
- [ ] README.md updates:
  - [ ] MVP feature overview
  - [ ] Setup instructions
  - [ ] Running locally
  - [ ] Environment variables required
  - [ ] API documentation links
- [ ] API Documentation:
  - [ ] FastAPI auto-generates Swagger at `/docs`
  - [ ] Verify all endpoints documented
  - [ ] Add descriptions to all endpoints
- [ ] Database Schema Documentation:
  - [ ] Create ER diagram
  - [ ] Document relationships
  - [ ] Document constraints
- [ ] Deployment Guide:
  - [ ] Docker setup
  - [ ] Environment configuration
  - [ ] Database setup on production
- **Files**: `README.md`, docs/
- **Validation**: Documentation is complete and accurate

**[ ] Task 9.2: Docker Setup**
- [ ] Create `Dockerfile`:
  - [ ] Use Python 3.11 slim image
  - [ ] Install dependencies
  - [ ] Copy app and static files
  - [ ] Expose port 8000
  - [ ] Run uvicorn
- [ ] Create `docker-compose.yml`:
  - [ ] FastAPI service
  - [ ] PostgreSQL service
  - [ ] Volume for database persistence
  - [ ] Environment variables
- [ ] Test locally:
  - [ ] `docker-compose build`
  - [ ] `docker-compose up`
  - [ ] Verify API works at localhost:8000
- **Files**: `Dockerfile`, `docker-compose.yml`
- **Validation**: Application runs in Docker

**[ ] Task 9.3: Environment Configuration**
- [ ] Create `.env.example`:
  - [ ] DATABASE_URL
  - [ ] SECRET_KEY (generate with `openssl rand -hex 32`)
  - [ ] CORS_ORIGINS
  - [ ] DEBUG (false in production)
  - [ ] All other config options
- [ ] Document all required env variables
- [ ] Setup process:
  - [ ] Copy .env.example to .env
  - [ ] Fill in values
  - [ ] Never commit .env
- **Files**: `.env.example`, `.gitignore`
- **Validation**: Application starts with proper env vars

**[ ] Task 9.4: GitHub Secrets Setup**
- [ ] Set up GitHub secrets for CI/CD:
  - [ ] DATABASE_URL (test database)
  - [ ] SECRET_KEY
  - [ ] CODECOV_TOKEN (optional, for coverage reports)
- [ ] Update GitHub Actions workflows to use secrets
- [ ] Test: Push code → verify CI passes
- **Files**: `.github/workflows/`
- **Validation**: CI/CD workflows pass

**[ ] Task 9.5: Pre-Launch Checklist**
- [ ] [ ] All tests passing (≥80% coverage)
- [ ] [ ] All linting checks passing
- [ ] [ ] Security scans passing (bandit, safety)
- [ ] [ ] Type checking passes (mypy)
- [ ] [ ] Documentation complete
- [ ] [ ] Docker image builds successfully
- [ ] [ ] Environment configuration documented
- [ ] [ ] GitHub secrets configured
- [ ] [ ] Database migrations work on fresh database
- [ ] [ ] Frontend builds successfully
- [ ] [ ] End-to-end workflows tested
- [ ] [ ] Performance baseline established
- [ ] [ ] Error handling tested
- [ ] [ ] RBAC enforcement verified
- [ ] [ ] Audit logging works
- [ ] [ ] Financial calculations verified
- **Files**: All
- **Validation**: MVP ready for launch

---

## Key Metrics & Success Criteria

### Code Quality
- [ ] Test Coverage: ≥80% (target 85%+)
- [ ] Linting: 0 errors from ruff, pylint, mypy
- [ ] Security: 0 high/critical findings from bandit, safety
- [ ] Type Safety: 100% of functions have type hints

### Functionality
- [ ] All CRUD operations working
- [ ] All workflows end-to-end functional
- [ ] All role-based access controls enforced
- [ ] All validations working correctly
- [ ] All error messages clear and helpful

### Performance
- [ ] API response time <200ms (p95)
- [ ] Frontend page load <3 seconds
- [ ] Database queries optimized (no N+1)
- [ ] No memory leaks

### Stability
- [ ] Zero crashes in testing
- [ ] Proper error handling everywhere
- [ ] Clean shutdown on signals
- [ ] Database connections properly pooled

### Security
- [ ] JWT tokens secure (HS256, expiration)
- [ ] Passwords hashed with bcrypt
- [ ] CORS configured correctly
- [ ] HTTPS ready for production
- [ ] No secrets in code or logs
- [ ] SQL injection protected
- [ ] XSS protection in frontend

### Operations
- [ ] Dockerized and deployable
- [ ] Environment configuration managed
- [ ] Logging implemented
- [ ] Health check endpoint working
- [ ] Graceful shutdown implemented

---

## Testing Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::test_login -v

# Run tests matching pattern
pytest tests/ -k "workflow" -v

# Code quality checks
black app/ tests/
isort app/ tests/
ruff check app/ tests/
mypy app/

# Security checks
bandit -r app/
safety check

# Run with GitHub Actions locally
act push
```

---

## Timeline Summary

```
Week 1: Database & ORM (7 tasks)
Week 2: Auth & Security (6 tasks)
Week 3: Client & SOW (3 tasks)
Week 3-4: Projects & Timesheets (2 tasks)
Week 4: Invoices (3 tasks)
Week 5: Frontend Setup (4 tasks)
Week 5-6: Frontend UIs (6 tasks)
Week 7: Testing & Quality (5 tasks)
Week 8: Documentation & Deployment (5 tasks)

Total: 40+ tasks across 8 weeks
Daily: ~5-7 tasks per week
```

---

**Status**: Ready to implement
**Next**: Assign developers to phases and begin Week 1 tasks
