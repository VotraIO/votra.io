# Votra.io MVP Implementation Plan

**Project**: Votra.io Consulting Business Portal - MVP (Minimum Viable Product)
**Date**: February 2026
**Status**: Ready for Implementation
**Branch**: add/fastapi

---

## Executive Summary

This document provides a **step-by-step implementation plan** for the Votra.io MVP. The MVP focuses on the core consulting workflow: **Client → SOW → Project → Timesheet → Invoice → Payment**.

The implementation covers:
- ✅ **Backend API** (Python/FastAPI) - Complete consulting workflow
- ✅ **Frontend Serving** (FastAPI static files + SPA routing) - No separate infrastructure needed
- ✅ **Database** (SQLAlchemy ORM with PostgreSQL/SQLite)
- ✅ **Authentication** (JWT with role-based access)
- ✅ **Core Features** - Essential consulting operations only
- ✅ **Testing** (80%+ coverage with pytest)

---

## MVP Scope

### Phase 1: Core Infrastructure (Week 1-2)
Focus: **Foundation**
- Authentication & JWT tokens
- Database models (Client, SOW, Project, Timesheet, Invoice)
- Basic CRUD operations
- Static file serving for frontend

### Phase 2: Consulting Workflow (Week 3-4)
Focus: **Workflow Implementation**
- SOW creation and approval
- Project management
- Timesheet validation and submission
- Invoice generation

### Phase 3: Frontend (Week 5-6)
Focus: **User Interface**
- React/Vue SPA (served by FastAPI)
- Authentication UI
- Consulting workflow UI
- Dashboard and reports

### Phase 4: Polish & Launch (Week 7-8)
Focus: **Production Readiness**
- Testing (80%+ coverage)
- Security scanning
- Performance optimization
- Documentation

---

## Architecture Overview

### Frontend-Backend Integration (Key Feature)
```
┌─────────────────────────────────────┐
│     FastAPI Application             │
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │  Static Files (SPA Frontend)    │ │ ← Served from /static
│ │  - index.html                   │ │
│ │  - React/Vue app                │ │
│ │  - CSS, JS, images              │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │  API Routes                     │ │ ← JSON responses
│ │  /api/v1/clients/*              │ │
│ │  /api/v1/sows/*                 │ │
│ │  /api/v1/projects/*             │ │
│ │  /api/v1/timesheets/*           │ │
│ │  /api/v1/invoices/*             │ │
│ │  /api/v1/auth/*                 │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │  Middleware                     │ │
│ │  - CORS, Security Headers       │ │
│ │  - Rate Limiting                │ │
│ │  - JWT Authentication           │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
         ↓
    PostgreSQL/SQLite Database
```

### Technology Stack
```
Frontend:          React 18 (or Vue 3)
Backend:           FastAPI (Python 3.10+)
ORM:               SQLAlchemy 2.0+
Database:          PostgreSQL (prod) / SQLite (dev)
Authentication:    JWT + bcrypt
Validation:        Pydantic v2
Testing:           pytest + pytest-cov
Code Quality:      black, ruff, mypy, pylint
CI/CD:             GitHub Actions
Containerization:  Docker
```

---

## Phase 1: Core Infrastructure (Week 1-2)

### 1.1 Database Setup & ORM Models

**Files to Create/Update**:
- `app/database/models.py` - SQLAlchemy ORM models

**Models to Implement**:

```python
# User Model
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str]
    full_name: Mapped[Optional[str]]
    role: Mapped[str]  # admin, pm, consultant, client, accountant
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    
    # Relationships
    projects: Mapped[List["Project"]] = relationship(back_populates="created_by")
    timesheets: Mapped[List["Timesheet"]] = relationship(back_populates="consultant")

# Client Model
class Client(Base):
    __tablename__ = "clients"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[Optional[str]]
    company: Mapped[Optional[str]]
    billing_address: Mapped[Optional[str]]
    payment_terms: Mapped[int] = mapped_column(default=30)  # days
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    
    # Relationships
    sows: Mapped[List["SOW"]] = relationship(back_populates="client")
    invoices: Mapped[List["Invoice"]] = relationship(back_populates="client")

# SOW Model (Statement of Work)
class SOW(Base):
    __tablename__ = "sows"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]]
    start_date: Mapped[date]
    end_date: Mapped[date]
    rate: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))  # hourly or daily
    total_budget: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    status: Mapped[str]  # draft, pending, approved, in_progress, completed, rejected
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    # Relationships
    client: Mapped["Client"] = relationship(back_populates="sows")
    projects: Mapped[List["Project"]] = relationship(back_populates="sow")

# Project Model
class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sow_id: Mapped[int] = mapped_column(ForeignKey("sows.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]]
    status: Mapped[str]  # active, completed, on_hold, cancelled
    start_date: Mapped[date]
    end_date: Mapped[date]
    budget: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    # Relationships
    sow: Mapped["SOW"] = relationship(back_populates="projects")
    timesheets: Mapped[List["Timesheet"]] = relationship(back_populates="project")

# Timesheet Model
class Timesheet(Base):
    __tablename__ = "timesheets"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    consultant_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    work_date: Mapped[date]
    hours_logged: Mapped[Decimal] = mapped_column(DECIMAL(5, 2))  # 0-24
    billing_rate: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    billable_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    is_billable: Mapped[bool] = mapped_column(default=True)
    notes: Mapped[Optional[str]]
    status: Mapped[str]  # draft, submitted, approved, rejected
    submitted_at: Mapped[Optional[datetime]]
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="timesheets")
    consultant: Mapped["User"] = relationship(back_populates="timesheets")

# Invoice Model
class Invoice(Base):
    __tablename__ = "invoices"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"))
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True)
    invoice_date: Mapped[date]
    due_date: Mapped[date]
    subtotal: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    tax_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    discount_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    total_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    status: Mapped[str]  # draft, sent, paid, overdue, cancelled
    payment_date: Mapped[Optional[date]]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    # Relationships
    client: Mapped["Client"] = relationship(back_populates="invoices")
    line_items: Mapped[List["LineItem"]] = relationship(back_populates="invoice")

# LineItem Model (for invoice items)
class LineItem(Base):
    __tablename__ = "line_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    description: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    line_total: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    
    # Relationships
    invoice: Mapped["Invoice"] = relationship(back_populates="line_items")

# AuditLog Model (for compliance)
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str]  # created, updated, deleted, approved, rejected
    entity_type: Mapped[str]  # sow, project, timesheet, invoice
    entity_id: Mapped[int]
    old_values: Mapped[Optional[str]]  # JSON string
    new_values: Mapped[Optional[str]]  # JSON string
    description: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=func.now())
```

**Test File**:
`tests/test_models.py` - Verify model relationships and constraints

---

### 1.2 Pydantic Models (Request/Response)

**Files to Create**:
- `app/models/client.py`
- `app/models/sow.py`
- `app/models/project.py`
- `app/models/timesheet.py`
- `app/models/invoice.py`

**Example: SOW Models**

```python
# app/models/sow.py
from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class SOWBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    client_id: int = Field(..., gt=0)
    start_date: date
    end_date: date
    rate: Decimal = Field(..., gt=0, decimal_places=2)
    total_budget: Decimal = Field(..., gt=0, decimal_places=2)
    
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        if 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class SOWCreate(SOWBase):
    pass

class SOWUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    rate: Optional[Decimal] = None
    total_budget: Optional[Decimal] = None
    # Cannot update dates, client_id, or status through normal update

class SOWResponse(SOWBase):
    id: int
    status: str
    created_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[str] = None
    created_at: str
    updated_at: str
    
    model_config = ConfigDict(from_attributes=True)

class SOWApprove(BaseModel):
    approved: bool = Field(..., description="Whether to approve SOW")
    notes: Optional[str] = None

class SOWList(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[SOWResponse]
```

**Similar structure for**: Client, Project, Timesheet, Invoice models

---

### 1.3 Authentication & Security

**Files to Update**:
- `app/utils/security.py` - JWT token generation and validation
- `app/dependencies.py` - Dependency injection for current user
- `app/routers/auth.py` - Login, refresh token endpoints

**Key Functions**:

```python
# app/utils/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password for storage."""
    return pwd_context.hash(password)

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    secret_key: str = None,
    algorithm: str = "HS256"
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def verify_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256"
) -> Optional[dict]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except (JWTError, ValidationError):
        return None

# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from token."""
    settings = get_settings()
    
    payload = verify_token(token, settings.secret_key)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Role-based access control
async def require_role(required_roles: list[str]):
    """Factory for role-based access control."""
    async def check_role(user: User = Depends(get_current_active_user)) -> User:
        if user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{user.role}' not authorized for this action"
            )
        return user
    return check_role
```

**Auth Router**:

```python
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register new user."""
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role="consultant"  # Default role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login and return JWT tokens."""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    settings = get_settings()
    
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        secret_key=settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    # Implementation similar to login
    pass
```

**Test File**:
`tests/test_auth.py` - Test registration, login, token validation, role-based access

---

### 1.4 Static File Serving Setup

**Update**: `app/main.py`

```python
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# After creating app and adding routers:

# Serve static files (frontend)
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve frontend index.html for SPA routing
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """
    Serve frontend SPA for all non-API routes.
    This enables browser history-based routing in React/Vue.
    """
    # Don't serve SPA for API routes
    if full_path.startswith("api/"):
        return JSONResponse(
            status_code=404,
            content={"detail": "Not found"}
        )
    
    # Serve index.html for all other routes (SPA routing)
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"}
    )
```

**Directory Structure**:
```
votra.io/
├── static/                 # Frontend (React/Vue) builds here
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── images/
├── app/
│   ├── main.py            # FastAPI app setup
│   ├── config.py
│   ├── dependencies.py
│   ├── database/
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── utils/
└── tests/
```

---

## Phase 2: Consulting Workflow (Week 3-4)

### 2.1 Client Management

**Router**: `app/routers/clients.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/clients", tags=["clients"])

@router.post("/", response_model=ClientResponse, status_code=201)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "pm"]))
):
    """Create new client."""
    db_client = Client(**client_data.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/", response_model=ClientList)
async def list_clients(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all clients."""
    query = db.query(Client).filter(Client.is_active == True)
    
    total = query.count()
    items = query.offset((page-1)*per_page).limit(per_page).all()
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": items
    }

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get client details."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "pm"]))
):
    """Update client details."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    for field, value in client_data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    return client

@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Delete (deactivate) client."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    client.is_active = False
    db.commit()
```

---

### 2.2 SOW Management (Core Workflow)

**Router**: `app/routers/sows.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.sow_service import (
    create_sow,
    approve_sow,
    reject_sow,
    get_sow_detail
)

router = APIRouter(prefix="/api/v1/sows", tags=["sows"])

@router.post("/", response_model=SOWResponse, status_code=201)
async def create_sow_endpoint(
    sow_data: SOWCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "pm"]))
):
    """Create new SOW (draft status)."""
    sow = create_sow(sow_data, current_user.id, db)
    return sow

@router.get("/{sow_id}", response_model=SOWResponse)
async def get_sow(
    sow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SOW details."""
    sow = db.query(SOW).filter(SOW.id == sow_id).first()
    if not sow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SOW not found"
        )
    return sow

@router.put("/{sow_id}", response_model=SOWResponse)
async def update_sow(
    sow_id: int,
    sow_data: SOWUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["pm"]))
):
    """Update SOW (only if in draft status)."""
    sow = db.query(SOW).filter(SOW.id == sow_id).first()
    if not sow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SOW not found"
        )
    
    if sow.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Can only edit SOWs in draft status"
        )
    
    for field, value in sow_data.model_dump(exclude_unset=True).items():
        setattr(sow, field, value)
    sow.updated_at = datetime.now()
    
    db.commit()
    db.refresh(sow)
    return sow

@router.post("/{sow_id}/submit", response_model=SOWResponse)
async def submit_sow(
    sow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["pm"]))
):
    """Submit SOW for approval."""
    sow = db.query(SOW).filter(SOW.id == sow_id).first()
    if not sow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SOW not found"
        )
    
    if sow.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft SOWs can be submitted"
        )
    
    sow.status = "pending"
    db.commit()
    db.refresh(sow)
    
    # Log audit
    log_audit(db, current_user.id, "submitted", "sow", sow.id)
    
    return sow

@router.post("/{sow_id}/approve", response_model=SOWResponse)
async def approve_sow_endpoint(
    sow_id: int,
    approval_data: SOWApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "pm"]))
):
    """Approve SOW."""
    sow = db.query(SOW).filter(SOW.id == sow_id).first()
    if not sow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SOW not found"
        )
    
    if sow.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending SOWs can be approved"
        )
    
    if approval_data.approved:
        sow.status = "approved"
        sow.approved_by = current_user.id
        sow.approved_at = datetime.now()
    else:
        sow.status = "rejected"
    
    db.commit()
    db.refresh(sow)
    
    # Log audit
    action = "approved" if approval_data.approved else "rejected"
    log_audit(db, current_user.id, action, "sow", sow.id)
    
    return sow

@router.get("/", response_model=SOWList)
async def list_sows(
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List SOWs with filtering."""
    query = db.query(SOW)
    
    if status:
        query = query.filter(SOW.status == status)
    if client_id:
        query = query.filter(SOW.client_id == client_id)
    
    total = query.count()
    items = query.order_by(SOW.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": items
    }
```

---

### 2.3 Project Management

**Router**: `app/routers/projects.py`

Similar to SOW router, with endpoints for:
- `POST /` - Create project from approved SOW
- `GET /{id}` - Get project details
- `PUT /{id}` - Update project
- `GET /` - List projects (with filtering)
- `POST /{id}/close` - Close completed project

**Key Logic**:
- Can only create project from approved SOW
- Project dates must match SOW dates
- Automatic timesheet creation from project

---

### 2.4 Timesheet Management

**Router**: `app/routers/timesheets.py`

```python
@router.post("/", response_model=TimesheetResponse, status_code=201)
async def create_timesheet(
    ts_data: TimesheetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["consultant"]))
):
    """Submit timesheet entry."""
    # Validate: work_date is within project dates
    project = db.query(Project).filter(Project.id == ts_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if ts_data.work_date < project.start_date or ts_data.work_date > project.end_date:
        raise HTTPException(
            status_code=400,
            detail="Work date must be within project date range"
        )
    
    # Validate: hours between 0 and 24
    if ts_data.hours_logged <= 0 or ts_data.hours_logged > 24:
        raise HTTPException(
            status_code=400,
            detail="Hours must be between 0 and 24"
        )
    
    # Calculate billable amount
    ts_data.billable_amount = ts_data.hours_logged * ts_data.billing_rate
    
    timesheet = Timesheet(
        **ts_data.model_dump(),
        consultant_id=current_user.id,
        status="submitted",
        submitted_at=datetime.now()
    )
    db.add(timesheet)
    db.commit()
    db.refresh(timesheet)
    
    log_audit(db, current_user.id, "submitted", "timesheet", timesheet.id)
    
    return timesheet

@router.get("/", response_model=TimesheetList)
async def list_timesheets(
    project_id: Optional[int] = None,
    consultant_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List timesheets with filtering."""
    query = db.query(Timesheet)
    
    if project_id:
        query = query.filter(Timesheet.project_id == project_id)
    if consultant_id:
        query = query.filter(Timesheet.consultant_id == consultant_id)
    if date_from:
        query = query.filter(Timesheet.work_date >= date_from)
    if date_to:
        query = query.filter(Timesheet.work_date <= date_to)
    
    total = query.count()
    items = query.order_by(Timesheet.work_date.desc()).offset((page-1)*per_page).limit(per_page).all()
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": items
    }

@router.post("/{timesheet_id}/approve", response_model=TimesheetResponse)
async def approve_timesheet(
    timesheet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["pm"]))
):
    """Approve timesheet (PM only)."""
    timesheet = db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.status != "submitted":
        raise HTTPException(status_code=409, detail="Only submitted timesheets can be approved")
    
    timesheet.status = "approved"
    timesheet.approved_by = current_user.id
    timesheet.approved_at = datetime.now()
    
    db.commit()
    db.refresh(timesheet)
    
    log_audit(db, current_user.id, "approved", "timesheet", timesheet.id)
    
    return timesheet
```

---

### 2.5 Invoice Generation

**Service**: `app/services/invoice_service.py`

```python
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database.models import Invoice, LineItem, Timesheet, Project, Client

def generate_invoice(
    project_id: int,
    invoice_date: date,
    db: Session
) -> Invoice:
    """
    Generate invoice from approved timesheets.
    
    Args:
        project_id: ID of project
        invoice_date: Date for invoice
        db: Database session
    
    Returns:
        Created Invoice object
        
    Raises:
        ValueError: If no approved timesheets or project not found
    """
    # Get project and client
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError(f"Project {project_id} not found")
    
    client = db.query(Client).filter(Client.id == project.sow.client_id).first()
    
    # Get all approved timesheets for project
    timesheets = db.query(Timesheet).filter(
        Timesheet.project_id == project_id,
        Timesheet.status == "approved",
        Timesheet.invoice_id.is_(None)  # Not yet invoiced
    ).all()
    
    if not timesheets:
        raise ValueError(f"No approved timesheets for project {project_id}")
    
    # Calculate totals (use DECIMAL for accuracy)
    subtotal = Decimal(0)
    for ts in timesheets:
        subtotal += ts.billable_amount
    
    # Apply tax (simplified - 10% for MVP)
    tax_rate = Decimal("0.10")
    tax_amount = (subtotal * tax_rate).quantize(Decimal("0.01"))
    total_amount = (subtotal + tax_amount).quantize(Decimal("0.01"))
    
    # Create invoice
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    due_date = invoice_date + timedelta(days=client.payment_terms)
    
    invoice = Invoice(
        client_id=client.id,
        project_id=project_id,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=Decimal(0),
        total_amount=total_amount,
        status="draft"
    )
    
    db.add(invoice)
    db.flush()  # Get invoice ID
    
    # Create line items from timesheets
    for ts in timesheets:
        line_item = LineItem(
            invoice_id=invoice.id,
            description=f"Consulting services - {ts.work_date}",
            quantity=ts.hours_logged,
            unit_price=ts.billing_rate,
            line_total=ts.billable_amount
        )
        db.add(line_item)
        
        # Mark timesheet as invoiced
        ts.invoice_id = invoice.id
    
    db.commit()
    db.refresh(invoice)
    
    return invoice

def validate_invoice_totals(invoice: Invoice) -> bool:
    """Validate invoice calculations are correct."""
    expected_total = invoice.subtotal + invoice.tax_amount - invoice.discount_amount
    return expected_total == invoice.total_amount
```

**Router**: `app/routers/invoices.py`

```python
@router.post("/", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "pm"]))
):
    """Generate invoice from approved timesheets."""
    invoice = generate_invoice(
        invoice_data.project_id,
        invoice_data.invoice_date,
        db
    )
    
    log_audit(db, current_user.id, "created", "invoice", invoice.id)
    
    return invoice

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get invoice details."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Verify access: client can only see their own invoices
    if current_user.role == "client":
        if invoice.client_id != current_user.client_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    return invoice

@router.post("/{invoice_id}/send", response_model=InvoiceResponse)
async def send_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "pm"]))
):
    """Mark invoice as sent to client."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft invoices can be sent")
    
    invoice.status = "sent"
    db.commit()
    db.refresh(invoice)
    
    log_audit(db, current_user.id, "sent", "invoice", invoice.id)
    
    return invoice

@router.post("/{invoice_id}/mark-paid", response_model=InvoiceResponse)
async def mark_invoice_paid(
    invoice_id: int,
    payment_data: PaymentRecord,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "accountant"]))
):
    """Mark invoice as paid."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice.status = "paid"
    invoice.payment_date = payment_data.payment_date
    db.commit()
    db.refresh(invoice)
    
    log_audit(db, current_user.id, "marked_paid", "invoice", invoice.id)
    
    return invoice
```

---

## Phase 3: Frontend (Week 5-6)

### 3.1 Frontend Technology Stack

**Recommended**: React 18 with TypeScript

```
Frontend Structure:
static/
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── Layout/
│   │   │   ├── Navbar.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── SOW/
│   │   │   ├── SOWForm.tsx
│   │   │   ├── SOWList.tsx
│   │   │   └── SOWDetail.tsx
│   │   ├── Project/
│   │   ├── Timesheet/
│   │   └── Invoice/
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── SOWs/
│   │   ├── Projects/
│   │   ├── Timesheets/
│   │   └── Invoices/
│   ├── services/
│   │   ├── api.ts        # API client
│   │   ├── auth.ts       # Auth logic
│   │   └── store.ts      # State management
│   ├── App.tsx
│   └── index.tsx
├── public/
│   └── index.html
├── package.json
└── tsconfig.json
```

### 3.2 Key Frontend Pages

**Login Page**:
- Email/password input
- Register link
- Submit to `/api/v1/auth/login`
- Store JWT token in localStorage
- Redirect to dashboard on success

**Dashboard**:
- Overview metrics (SOWs, Projects, Timesheets, Invoices)
- Recent activity list
- Quick action buttons

**SOW Management**:
- List view with filtering (status, client)
- Create new SOW form
- SOW detail view
- Approval workflow (for PMs)

**Project Management**:
- Create project from approved SOW
- Project status tracking
- Team member allocation

**Timesheet Entry**:
- Daily timesheet form
- Project selection
- Hours and notes
- Approval workflow

**Invoice Management**:
- Invoice list with status
- Invoice detail view (line items, total)
- Send to client
- Payment tracking

### 3.3 API Client Setup

```typescript
// src/services/api.ts
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

class ApiClient {
  private client: AxiosInstance;
  
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // Add JWT token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
    
    // Handle 401 Unauthorized
    this.client.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }
  
  // Auth endpoints
  login = (email: string, password: string) =>
    this.client.post('/auth/login', { email, password });
  
  register = (data: UserRegisterData) =>
    this.client.post('/auth/register', data);
  
  // Client endpoints
  getClients = (page = 1, perPage = 20) =>
    this.client.get('/clients', { params: { page, per_page: perPage } });
  
  getClient = (id: number) =>
    this.client.get(`/clients/${id}`);
  
  createClient = (data: ClientData) =>
    this.client.post('/clients', data);
  
  // SOW endpoints
  getSOWs = (status?: string, clientId?: number, page = 1, perPage = 20) =>
    this.client.get('/sows', { params: { status, client_id: clientId, page, per_page: perPage } });
  
  getSOW = (id: number) =>
    this.client.get(`/sows/${id}`);
  
  createSOW = (data: SOWData) =>
    this.client.post('/sows', data);
  
  updateSOW = (id: number, data: Partial<SOWData>) =>
    this.client.put(`/sows/${id}`, data);
  
  submitSOW = (id: number) =>
    this.client.post(`/sows/${id}/submit`);
  
  approveSOW = (id: number, approved: boolean) =>
    this.client.post(`/sows/${id}/approve`, { approved });
  
  // Similar methods for Projects, Timesheets, Invoices
}

export default new ApiClient();
```

---

## Phase 4: Polish & Launch (Week 7-8)

### 4.1 Testing Requirements

**Unit Tests** (pytest):
- Models and validations
- Service logic
- Utility functions
- Target: 80%+ coverage

```bash
# Run tests
pytest tests/ -v --cov=app --cov-report=html

# Specific test
pytest tests/test_auth.py -v
```

**Integration Tests**:
- API endpoint tests
- Workflow tests (SOW → Project → Timesheet → Invoice)
- Role-based access control
- Error handling

**Test Files**:
```
tests/
├── test_auth.py
├── test_models.py
├── test_clients.py
├── test_sows.py
├── test_projects.py
├── test_timesheets.py
├── test_invoices.py
└── conftest.py
```

### 4.2 Security Validation

```bash
# Run security checks
bandit -r app/
safety check

# Type checking
mypy app/

# Linting
ruff check app/

# Code formatting
black --check app/
```

### 4.3 Deployment Configuration

**Docker**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY static ./static

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/votraio
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: votraio
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

---

## Implementation Timeline

```
Week 1-2 (Core Infrastructure):
  - Database models (1 day)
  - Pydantic models (1 day)
  - Authentication (2 days)
  - Static file serving setup (1 day)
  - Tests for infrastructure (2 days)

Week 3-4 (Consulting Workflow):
  - Client management (1 day)
  - SOW management (2 days)
  - Project management (2 days)
  - Timesheet management (2 days)
  - Invoice generation (2 days)
  - Tests for workflows (2 days)

Week 5-6 (Frontend):
  - Project setup & layout (1 day)
  - Auth UI (1 day)
  - SOW UI (2 days)
  - Project/Timesheet/Invoice UI (2 days)
  - Testing & integration (2 days)

Week 7-8 (Polish):
  - Code quality & security (1 day)
  - Performance optimization (1 day)
  - Documentation (1 day)
  - Testing & QA (2 days)
  - Deployment setup (1 day)
  - Launch preparation (1 day)
```

---

## Milestones

### ✅ Milestone 1: Infrastructure Ready
- Database configured
- Models defined
- Authentication working
- Static files serving
- Initial tests passing

### ✅ Milestone 2: Core Workflows
- Client management complete
- SOW workflow complete
- Project management complete
- Timesheet validation working
- Invoice generation working

### ✅ Milestone 3: Frontend Functional
- Login/register pages working
- SOW management UI complete
- Project management UI complete
- Timesheet entry UI complete
- Invoice view UI complete

### ✅ Milestone 4: MVP Ready
- 80%+ test coverage
- All security checks passing
- Performance optimized
- Documentation complete
- Ready for production

---

## Success Criteria

### Code Quality
- ✅ 80%+ test coverage
- ✅ All linting checks passing
- ✅ Type checking clean (mypy)
- ✅ Security scanning clean (bandit, safety)

### Functionality
- ✅ All consulting workflows working end-to-end
- ✅ Authentication secure
- ✅ Role-based access control enforced
- ✅ Invoice calculations accurate
- ✅ Frontend fully integrated

### Performance
- ✅ API response time < 200ms (p95)
- ✅ Frontend page load < 3 seconds
- ✅ Database queries optimized
- ✅ No memory leaks

### Production Readiness
- ✅ Dockerized and deployable
- ✅ Environment configuration managed
- ✅ Error handling comprehensive
- ✅ Logging implemented
- ✅ Monitoring configured

---

## Next Steps

1. **Review** this MVP plan with team
2. **Assign** developers to each phase
3. **Create** GitHub issues for each milestone
4. **Set up** development environment
5. **Begin** Phase 1 implementation

---

## Resources

- Copilot Instructions: [.github/copilot-instructions.md](.github/copilot-instructions.md)
- Architecture Guide: [docs/architecture/01-architecture-overview.md](docs/architecture/01-architecture-overview.md)
- Consulting Workflow: [docs/CONSULTING-WORKFLOW.md](docs/CONSULTING-WORKFLOW.md)
- Custom Agents: [.github/agents/README.md](.github/agents/README.md)

---

**Status**: Ready for implementation
**Next Action**: Begin Phase 1 with @consulting-dev agent for database models and ORM setup
