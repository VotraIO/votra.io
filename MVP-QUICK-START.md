# MVP Quick Start Guide

**Goal**: Get the Votra.io MVP up and running in 8 weeks

---

## 🚀 Quick Navigation

| Document | Purpose |
|----------|---------|
| [MVP-IMPLEMENTATION-PLAN.md](MVP-IMPLEMENTATION-PLAN.md) | Complete phase-by-phase breakdown with code examples |
| [MVP-IMPLEMENTATION-CHECKLIST.md](MVP-IMPLEMENTATION-CHECKLIST.md) | Task-by-task checklist with validation steps |
| [FASTAPI-FRONTEND-SERVING-GUIDE.md](FASTAPI-FRONTEND-SERVING-GUIDE.md) | How to serve React/Vue from FastAPI (no separate infra) |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | Development patterns and best practices |
| [.github/agents/README.md](.github/agents/README.md) | Custom AI agents for different development tasks |

---

## 📋 Phase Overview

### Phase 1: Core Infrastructure (Week 1-2)
**What**: Database, ORM models, authentication, static file serving
**Result**: FastAPI can serve API + static files, users can authenticate
**Key Files**: 
- `app/database/models.py` - SQLAlchemy ORM
- `app/routers/auth.py` - JWT authentication
- `app/main.py` - SPA serving setup

### Phase 2: Consulting Workflow (Week 3-4)
**What**: Client management, SOW workflow, projects, timesheets, invoices
**Result**: Complete consulting workflow from Client → Invoice
**Key Files**:
- `app/routers/clients.py` - Client management
- `app/routers/sows.py` - SOW workflow
- `app/routers/projects.py` - Project management
- `app/routers/timesheets.py` - Timesheet tracking
- `app/routers/invoices.py` - Invoice generation

### Phase 3: Frontend (Week 5-6)
**What**: React/Vue SPA served from FastAPI
**Result**: Complete user interface for all workflows
**Key Files**:
- `static/src/` - React components and pages
- `static/src/services/api.ts` - API client
- `static/package.json` - Frontend dependencies

### Phase 4: Polish & Launch (Week 7-8)
**What**: Testing, security, documentation, deployment
**Result**: Production-ready MVP
**Key Files**:
- `tests/` - Comprehensive test suite
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Full stack deployment

---

## 🎯 Success Criteria

**Code Quality**
- ✅ 80%+ test coverage
- ✅ All linting checks passing (black, ruff, mypy)
- ✅ Security scanning clean (bandit, safety)

**Functionality**
- ✅ All consulting workflows working end-to-end
- ✅ Authentication secure with JWT + bcrypt
- ✅ Role-based access control enforced
- ✅ Frontend fully integrated in FastAPI

**Infrastructure**
- ✅ Single FastAPI instance (no separate web server)
- ✅ Dockerized and deployable
- ✅ Environment configuration managed
- ✅ Database migrations working

---

## 🔧 Development Setup

### Prerequisites
```bash
# Python 3.10+
python --version

# Node.js 18+
node --version

# Git
git --version
```

### Initial Setup
```bash
# Clone repo (already done)
cd votra.io

# Create Python venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Generate SECRET_KEY
openssl rand -hex 32  # Copy this value to .env

# Create .env file
cp .env.example .env
# Edit .env with:
# - DATABASE_URL=sqlite:///./votra.db (for local dev)
# - SECRET_KEY=<generated value>
# - DEBUG=True

# Setup frontend
cd static
npm install
cd ..
```

### Running Locally

**Backend Only**:
```bash
# Terminal 1
source venv/bin/activate
uvicorn app.main:app --reload
# API: http://localhost:8000/docs
# API: http://localhost:8000/api/v1/health
```

**Backend + Frontend (Development)**:
```bash
# Terminal 1: Backend
source venv/bin/activate
uvicorn app.main:app --reload
# http://localhost:8000

# Terminal 2: Frontend dev server
cd static
npm run dev
# http://localhost:5173 (hot reload)
# Auto-proxies /api/* to localhost:8000
```

**Backend + Frontend (Build & Serve)**:
```bash
# Build frontend
cd static
npm run build
cd ..

# Start backend (serves both API and built frontend)
uvicorn app.main:app --reload
# http://localhost:8000 (fully integrated)
```

---

## 📝 Week-by-Week Tasks

### Week 1-2: Core Infrastructure
```
Day 1-2: Database & ORM Models (Task 1.1-1.4)
  - Alembic migrations setup
  - SQLAlchemy models (User, Client, SOW, Project, Timesheet, Invoice)
  - Database connections working
  
Day 3-4: Authentication (Task 2.1-2.3)
  - Pydantic models for requests/responses
  - JWT token generation and validation
  - Password hashing with bcrypt
  
Day 5: Auth Router (Task 2.4-2.5)
  - register, login, refresh endpoints
  - Role-based access control
  
Day 6-7: Static File Serving & Testing (Task 2.6)
  - FastAPI configured to serve static files
  - SPA routing catch-all implemented
  - Tests passing with 80%+ coverage
```

**Validation**: 
```bash
pytest tests/test_auth.py -v --cov=app
# Coverage ≥95%, all tests pass
```

### Week 3-4: Consulting Workflow
```
Day 8-9: Client Management (Task 3.1)
  - Client CRUD endpoints
  - RBAC enforcement
  
Day 10-12: SOW Workflow (Task 3.2)
  - Create, submit, approve workflow
  - State validation
  - Audit logging
  
Day 13-14: Projects & Timesheets (Task 4.1-4.2)
  - Project creation from approved SOW
  - Timesheet entry with validation
  - Approval workflows
  
Day 15: Invoice Generation (Task 5.1-5.2)
  - Generate from approved timesheets
  - Financial calculations (DECIMAL precision)
  - Invoice state transitions
```

**Validation**:
```bash
pytest tests/test_workflows.py -v --cov=app
# End-to-end workflows pass
```

### Week 5-6: Frontend
```
Day 16-17: Frontend Setup (Task 6.1-6.3)
  - React/Vite project initialized
  - API client configured
  - Development server working with hot reload
  
Day 18: Auth UI (Task 6.4)
  - Login and register pages
  - JWT token management
  - Auth context/store
  
Day 19-24: Core UI Components
  - Dashboard
  - SOW management (list, detail, form)
  - Project management
  - Timesheet entry
  - Invoice management
  - Layout and navigation
```

**Validation**:
```bash
cd static
npm run build
# Build succeeds, no errors

# Access http://localhost:8000
# Frontend loads and works
```

### Week 7-8: Quality & Deployment
```
Day 25-26: Testing
  - Unit tests for services
  - Integration tests for workflows
  - Coverage ≥80%
  
Day 27: Code Quality
  - black, isort formatting
  - ruff linting
  - mypy type checking
  - bandit security scanning
  
Day 28-29: Documentation & Deployment
  - README documentation
  - Docker setup
  - Environment configuration
  - GitHub Actions CI/CD
  
Day 30: Launch Prep
  - Final validation
  - Pre-launch checklist
  - Ready for production
```

**Validation**:
```bash
# All checks pass
pytest tests/ --cov=app --cov-fail-under=80
black --check app/
ruff check app/
mypy app/
bandit -r app/

# Docker works
docker build -t votra-io:latest .
docker run -p 8000:8000 votra-io:latest
```

---

## 🏗️ Architecture Decisions

### 1. Single FastAPI Instance (No Separate Web Server)
✅ **Why**: Simpler deployment, lower cost, easier development
✅ **How**: StaticFiles mount + SPA catch-all route (see FASTAPI-FRONTEND-SERVING-GUIDE.md)

### 2. SQLAlchemy ORM with Async
✅ **Why**: Type-safe, async support, relationship handling
✅ **How**: async_sessionmaker, async_create_engine

### 3. JWT Authentication
✅ **Why**: Stateless, scalable, industry standard
✅ **How**: HS256 algorithm, 30-min access token, 7-day refresh token

### 4. Pydantic v2 for Validation
✅ **Why**: Type hints, validation, auto-docs
✅ **How**: Request/response models with field_validators

### 5. pytest for Testing
✅ **Why**: Industry standard, good coverage tools
✅ **How**: Fixtures, parametrize, coverage reports

---

## 📚 Key Resources

### Development Guidance
- **Copilot Instructions**: [.github/copilot-instructions.md](.github/copilot-instructions.md) - Patterns and best practices
- **Consulting Workflow Docs**: [docs/](docs/) - Business requirements

### Custom AI Agents
Use these agents to help with specific tasks:

```bash
# For architecture and security questions
@consulting-dev agent

# For testing and CI/CD questions  
@testing-qa agent

# For DevOps and deployment questions
@devops-infra agent

# For code review and security scanning
@security-compliance agent
```

See [.github/agents/README.md](.github/agents/README.md) for usage guide.

---

## 🐛 Common Issues & Solutions

### Issue: `ModuleNotFoundError: No module named 'app'`
```bash
# Solution: Make sure you're in the votra.io root directory
pwd  # Should end with /votra.io
python -c "from app import main"  # Should work
```

### Issue: `DATABASE_URL not set`
```bash
# Solution: Create .env file with DATABASE_URL
echo "DATABASE_URL=sqlite:///./votra.db" >> .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

### Issue: Frontend not loading (404 on /)
```bash
# Solution: Build frontend first
cd static
npm run build
cd ..

# Then restart FastAPI
# or check static_dir path in app/main.py
```

### Issue: CORS errors between frontend and backend
```bash
# Solution: Frontend should be served BY FastAPI, not separately
# If using separate dev servers:
# - Frontend: http://localhost:5173
# - Backend: http://localhost:8000
# - vite.config.ts should proxy /api/* to localhost:8000
```

### Issue: Tests failing with database errors
```bash
# Solution: Ensure test database is set up
pytest tests/conftest.py -v
# conftest.py should create in-memory SQLite for tests
```

---

## ✅ Milestone Checklist

### Milestone 1: Infrastructure Ready (End of Week 2)
- [ ] Database models defined and migrations working
- [ ] Authentication endpoints working (register, login)
- [ ] Static files serving from FastAPI
- [ ] Initial tests passing (80%+ coverage for auth)
- [ ] Can access http://localhost:8000/docs

### Milestone 2: Core Workflows (End of Week 4)
- [ ] Client management CRUD working
- [ ] SOW workflow complete (create, submit, approve)
- [ ] Project management working
- [ ] Timesheet validation and approval working
- [ ] Invoice generation working
- [ ] Audit logging for all state changes
- [ ] End-to-end workflow tests passing

### Milestone 3: Frontend Functional (End of Week 6)
- [ ] React/Vue project initialized and building
- [ ] Login/register UI working
- [ ] SOW management UI complete
- [ ] Project, timesheet, invoice UIs complete
- [ ] API client correctly handling authentication
- [ ] Frontend integrated with FastAPI serving
- [ ] All pages accessible and functional

### Milestone 4: MVP Ready (End of Week 8)
- [ ] 80%+ test coverage
- [ ] All linting/type checking passing
- [ ] Security scans passing
- [ ] Docker image building successfully
- [ ] Documentation complete
- [ ] Ready for production deployment

---

## 🚀 Deployment

### Docker Deployment
```bash
# 1. Build frontend
cd static && npm run build && cd ..

# 2. Build Docker image
docker build -t votra-io:latest .

# 3. Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/votraio" \
  -e SECRET_KEY="<your-secret-key>" \
  votra-io:latest
```

### Using docker-compose
```bash
# Copy .env.example to .env and fill in values
cp .env.example .env

# Start full stack (API + PostgreSQL)
docker-compose up -d

# Access: http://localhost:8000
```

---

## 📞 Getting Help

### Use Custom Agents
See [.github/agents/README.md](.github/agents/README.md) for agent usage

**Examples**:
```
"@consulting-dev help me implement the SOW approval workflow"
"@testing-qa how do I test role-based access control?"
"@devops-infra help me set up GitHub Actions CI/CD"
"@security-compliance audit the authentication implementation"
```

### Use Copilot Instructions
All developers should reference:
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Development patterns
- [docs/architecture/01-architecture-overview.md](docs/architecture/01-architecture-overview.md) - System architecture

### Troubleshooting
1. Check implementation plan for phase requirements
2. Check checklist for specific task steps  
3. Check example code in implementation plan
4. Ask custom agents for help with specific tasks
5. Run tests to validate: `pytest tests/ -v --cov=app`

---

## 📊 Project Status

**Current State**: Architecture and agents complete, ready for implementation

**Next Steps**:
1. ✅ Review this MVP plan with team
2. ✅ Assign developers to phases
3. ✅ Create GitHub issues from checklist
4. ✅ Set up development environment
5. ⏳ Begin Phase 1 Week 1 tasks

---

## 🎓 Key Learnings for Team

### Python/FastAPI
- Type hints and Pydantic validation
- Async/await with SQLAlchemy
- JWT authentication patterns
- RBAC with dependency injection

### Frontend Integration
- Serving SPA from FastAPI (no separate server needed)
- React Router with SPA catch-all routes
- API client with axios interceptors

### Testing
- pytest with fixtures and coverage
- Integration testing for workflows
- Security testing (OWASP Top 10)

### DevOps
- Docker containerization
- GitHub Actions CI/CD
- Environment configuration management

---

## 🎉 Ready to Build!

This MVP plan provides everything needed to launch Votra.io in 8 weeks:
- ✅ Complete architecture documented
- ✅ Phase-by-phase breakdown with code examples
- ✅ Task-by-task checklist with validation
- ✅ Testing requirements and patterns
- ✅ Deployment configuration
- ✅ Custom AI agents for guidance

**Next**: Assign teams and start Week 1!

---

**Last Updated**: February 2026
**Status**: Ready for Implementation
**Estimated Duration**: 8 weeks with 1 team of 2-3 developers
