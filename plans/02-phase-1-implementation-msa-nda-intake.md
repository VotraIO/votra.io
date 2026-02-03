# Phase 1 Implementation Guide: Client Onboarding & Legal Foundation

**Duration**: 4 weeks  
**Goal**: Establish MSA, NDA, and Client Intake workflows  
**Complexity**: Medium  
**Team Size**: 1-2 developers

---

## Table of Contents

1. [Week 1: MSA Management System](#week-1-msa-management-system)
2. [Week 2: NDA Management System](#week-2-nda-management-system)
3. [Week 3: Client Intake Forms](#week-3-client-intake-forms)
4. [Week 4: Integration & Testing](#week-4-integration--testing)

---

## Week 1: MSA Management System

### Overview

MSA (Master Service Agreement) is the legal framework that governs all client engagements. By end of week 1, consultants will be able to:
- Create MSA from templates
- Collect client signatures
- Track MSA expiration
- Prevent contracts work without signed MSA

### Tasks

#### 1.1.1 Create Database Models & Migration

**File**: `app/database/models.py`

Add these models to the existing models.py file:

```python
class MSATemplate(Base):
    """MSA template for reuse across clients"""
    __tablename__ = "msa_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)  # Template with {{placeholders}}
    version = Column(String(20), nullable=False, default="1.0")
    default_terms_days = Column(Integer, default=30)
    default_renewal_days = Column(Integer, default=365)
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    msas = relationship(
        "MSA", back_populates="template", cascade="all, delete-orphan"
    )
    created_by_user = relationship("User")

    def __repr__(self) -> str:
        """String representation"""
        return f"<MSATemplate(id={self.id}, name='{self.name}', version='{self.version}')>"


class MSA(Base):
    """Master Service Agreement for a client"""
    __tablename__ = "msas"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    template_id = Column(
        Integer, ForeignKey("msa_templates.id"), nullable=False, index=True
    )
    status = Column(
        String(50),
        nullable=False,
        default="draft",
        index=True,
    )  # draft, signed, active, expired, renewed
    current_version = Column(Integer, default=1, nullable=False)
    customizations = Column(Text, nullable=True)  # Additional custom terms
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    renewal_date = Column(Date, nullable=True)
    signed_date = Column(Date, nullable=True)
    signed_by = Column(String(255), nullable=True)  # Name of signer
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    client = relationship("Client", back_populates="msas")
    template = relationship("MSATemplate", back_populates="msas")
    signatures = relationship(
        "MSASignature", back_populates="msa", cascade="all, delete-orphan"
    )
    versions = relationship(
        "MSAVersion", back_populates="msa", cascade="all, delete-orphan"
    )
    created_by_user = relationship("User")

    def __repr__(self) -> str:
        """String representation"""
        return f"<MSA(id={self.id}, client_id={self.client_id}, status='{self.status}')>"


class MSASignature(Base):
    """Signature record on MSA - tracks who signed and when"""
    __tablename__ = "msa_signatures"

    id = Column(Integer, primary_key=True, index=True)
    msa_id = Column(Integer, ForeignKey("msas.id"), nullable=False, index=True)
    signer_name = Column(String(255), nullable=False)
    signer_email = Column(String(255), nullable=False)
    signer_title = Column(String(255), nullable=True)
    signer_company = Column(String(255), nullable=True)
    signature_date = Column(Date, nullable=False)
    signature_method = Column(String(50), nullable=False)  # electronic, manual, esign
    signed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    msa = relationship("MSA", back_populates="signatures")
    signed_by_user = relationship("User")

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<MSASignature(id={self.id}, msa_id={self.msa_id}, "
            f"signer='{self.signer_name}')>"
        )


class MSAVersion(Base):
    """Version history of MSA changes - for audit trail"""
    __tablename__ = "msa_versions"

    id = Column(Integer, primary_key=True, index=True)
    msa_id = Column(Integer, ForeignKey("msas.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    change_summary = Column(Text, nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    msa = relationship("MSA", back_populates="versions")
    changed_by_user = relationship("User")

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"<MSAVersion(id={self.id}, msa_id={self.msa_id}, "
            f"version={self.version_number})>"
        )
```

Also update the `Client` model to add MSA relationship:
```python
# In Client class, add:
msas = relationship("MSA", back_populates="client", cascade="all, delete-orphan")
```

**Migration File**: `alembic/versions/20260203_0001_add_msa_tables.py`

```python
"""Add MSA tables for legal agreements"""

from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "20260203_0001"
down_revision = "a0779863e19c"
branch_labels = None
depends_on = None


def upgrade():
    """Create MSA tables"""
    # MSA Templates table
    op.create_table(
        "msa_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("version", sa.String(20), nullable=False, server_default="1.0"),
        sa.Column("default_terms_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("default_renewal_days", sa.Integer(), nullable=False, server_default="365"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_msa_templates_name", "msa_templates", ["name"])
    op.create_index("ix_msa_templates_is_active", "msa_templates", ["is_active"])

    # MSAs table
    op.create_table(
        "msas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("customizations", sa.Text(), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("expiration_date", sa.Date(), nullable=False),
        sa.Column("renewal_date", sa.Date(), nullable=True),
        sa.Column("signed_date", sa.Date(), nullable=True),
        sa.Column("signed_by", sa.String(255), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["template_id"], ["msa_templates.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_msas_client_id", "msas", ["client_id"])
    op.create_index("ix_msas_template_id", "msas", ["template_id"])
    op.create_index("ix_msas_status", "msas", ["status"])

    # MSA Signatures table
    op.create_table(
        "msa_signatures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("msa_id", sa.Integer(), nullable=False),
        sa.Column("signer_name", sa.String(255), nullable=False),
        sa.Column("signer_email", sa.String(255), nullable=False),
        sa.Column("signer_title", sa.String(255), nullable=True),
        sa.Column("signer_company", sa.String(255), nullable=True),
        sa.Column("signature_date", sa.Date(), nullable=False),
        sa.Column("signature_method", sa.String(50), nullable=False),
        sa.Column("signed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["msa_id"], ["msas.id"]),
        sa.ForeignKeyConstraint(["signed_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_msa_signatures_msa_id", "msa_signatures", ["msa_id"])

    # MSA Versions table
    op.create_table(
        "msa_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("msa_id", sa.Integer(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["msa_id"], ["msas.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_msa_versions_msa_id", "msa_versions", ["msa_id"])


def downgrade():
    """Drop MSA tables"""
    op.drop_index("ix_msa_versions_msa_id", "msa_versions")
    op.drop_table("msa_versions")

    op.drop_index("ix_msa_signatures_msa_id", "msa_signatures")
    op.drop_table("msa_signatures")

    op.drop_index("ix_msas_status", "msas")
    op.drop_index("ix_msas_template_id", "msas")
    op.drop_index("ix_msas_client_id", "msas")
    op.drop_table("msas")

    op.drop_index("ix_msa_templates_is_active", "msa_templates")
    op.drop_index("ix_msa_templates_name", "msa_templates")
    op.drop_table("msa_templates")
```

**Run Migration**:
```bash
cd /Users/jasonmiller/GitHub/votraio/votra.io
alembic upgrade head
```

#### 1.1.2 Create Pydantic Models

**File**: `app/models/msa.py` (NEW)

```python
"""MSA (Master Service Agreement) Pydantic models."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MSATemplateBase(BaseModel):
    """Base MSA template model"""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    content: str = Field(..., min_length=100)  # Template content
    version: str = Field(default="1.0")
    default_terms_days: int = Field(default=30, ge=1, le=365)
    default_renewal_days: int = Field(default=365, ge=30, le=3650)
    is_active: bool = Field(default=True)


class MSATemplateCreate(MSATemplateBase):
    """Create MSA template"""

    pass


class MSATemplateResponse(MSATemplateBase):
    """MSA template response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime


class MSABase(BaseModel):
    """Base MSA model"""

    client_id: int = Field(..., gt=0)
    template_id: int = Field(..., gt=0)
    customizations: str | None = Field(None, max_length=5000)
    effective_date: date
    expiration_date: date

    @field_validator("expiration_date")
    @classmethod
    def validate_expiration(cls, v: date, info) -> date:
        """Ensure expiration is after effective date"""
        effective_date = info.data.get("effective_date")
        if effective_date and v <= effective_date:
            raise ValueError("expiration_date must be after effective_date")
        return v


class MSACreate(MSABase):
    """Create new MSA"""

    pass


class MSAUpdate(BaseModel):
    """Update MSA (only before signing)"""

    customizations: str | None = Field(None, max_length=5000)
    expiration_date: date | None = None


class MSASignatureRequest(BaseModel):
    """Request to sign MSA"""

    signer_name: str = Field(..., min_length=1, max_length=255)
    signer_email: str = Field(..., max_length=255)
    signer_title: str | None = Field(None, max_length=255)
    signer_company: str | None = Field(None, max_length=255)
    signature_date: date
    signature_method: str = Field(default="electronic")  # electronic, manual, esign
    notes: str | None = Field(None, max_length=1000)


class MSASignatureResponse(MSASignatureRequest):
    """MSA signature response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    msa_id: int
    created_at: datetime


class MSAResponse(MSABase):
    """MSA response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str  # draft, signed, active, expired, renewed
    current_version: int
    signed_date: date | None = None
    signed_by: str | None = None
    renewal_date: date | None = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    signatures: list[MSASignatureResponse] = []


class MSAList(BaseModel):
    """MSA list response"""

    total: int
    page: int
    per_page: int
    items: list[MSAResponse]


class MSARenewRequest(BaseModel):
    """Request to renew MSA"""

    new_expiration_date: date = Field(..., description="New expiration date")
    notes: str | None = Field(None, max_length=1000)
```

#### 1.1.3 Create Service Layer

**File**: `app/services/msa_service.py` (NEW)

```python
"""MSA (Master Service Agreement) business logic service."""

from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    AuditLog,
    MSA,
    MSASignature,
    MSATemplate,
    MSAVersion,
)
from app.models.msa import (
    MSACreate,
    MSAResponse,
    MSASignatureRequest,
    MSAUpdate,
)


class MSAService:
    """Service for managing MSAs"""

    async def create_msa_template(
        self,
        session: AsyncSession,
        template_data: dict,
        created_by: int,
    ) -> MSATemplate:
        """Create new MSA template"""
        template = MSATemplate(
            name=template_data["name"],
            description=template_data.get("description"),
            content=template_data["content"],
            version=template_data.get("version", "1.0"),
            default_terms_days=template_data.get("default_terms_days", 30),
            default_renewal_days=template_data.get("default_renewal_days", 365),
            is_active=True,
            created_by=created_by,
        )
        session.add(template)
        await session.flush()
        
        # Audit log
        await self._create_audit_log(
            session,
            user_id=created_by,
            action="CREATE",
            entity_type="MSATemplate",
            entity_id=template.id,
            description=f"Created MSA template: {template.name}",
        )
        
        return template

    async def create_msa(
        self,
        session: AsyncSession,
        msa_data: MSACreate,
        created_by: int,
    ) -> MSA:
        """Create new MSA for client"""
        # Get template
        template = await session.get(MSATemplate, msa_data.template_id)
        if not template:
            raise ValueError(f"Template {msa_data.template_id} not found")

        msa = MSA(
            client_id=msa_data.client_id,
            template_id=msa_data.template_id,
            status="draft",
            current_version=1,
            customizations=msa_data.customizations,
            effective_date=msa_data.effective_date,
            expiration_date=msa_data.expiration_date,
            created_by=created_by,
        )
        session.add(msa)
        await session.flush()

        # Audit log
        await self._create_audit_log(
            session,
            user_id=created_by,
            action="CREATE",
            entity_type="MSA",
            entity_id=msa.id,
            new_values=f"Client: {msa.client_id}, Status: {msa.status}",
            description=f"Created MSA for client {msa.client_id}",
        )

        return msa

    async def sign_msa(
        self,
        session: AsyncSession,
        msa_id: int,
        signature_data: MSASignatureRequest,
        signed_by_user_id: int | None = None,
    ) -> MSA:
        """Record signature on MSA"""
        msa = await session.get(MSA, msa_id)
        if not msa:
            raise ValueError(f"MSA {msa_id} not found")

        # Add signature
        signature = MSASignature(
            msa_id=msa.id,
            signer_name=signature_data.signer_name,
            signer_email=signature_data.signer_email,
            signer_title=signature_data.signer_title,
            signer_company=signature_data.signer_company,
            signature_date=signature_data.signature_date,
            signature_method=signature_data.signature_method,
            signed_by_user_id=signed_by_user_id,
            notes=signature_data.notes,
        )
        session.add(signature)

        # Update MSA status
        msa.status = "signed"
        msa.signed_date = signature_data.signature_date
        msa.signed_by = signature_data.signer_name

        await session.flush()

        # Audit log
        await self._create_audit_log(
            session,
            user_id=signed_by_user_id or msa.created_by,
            action="SIGN",
            entity_type="MSA",
            entity_id=msa.id,
            new_values=f"Status: signed, Signer: {signature_data.signer_name}",
            description=f"MSA signed by {signature_data.signer_name}",
        )

        return msa

    async def renew_msa(
        self,
        session: AsyncSession,
        msa_id: int,
        new_expiration_date: date,
        notes: str | None = None,
        renewed_by: int = None,
    ) -> MSA:
        """Renew expiring MSA"""
        msa = await session.get(MSA, msa_id)
        if not msa:
            raise ValueError(f"MSA {msa_id} not found")

        # Update renewal info
        msa.renewal_date = datetime.now(timezone.utc).date()
        msa.expiration_date = new_expiration_date
        msa.status = "renewed"
        msa.current_version += 1

        await session.flush()

        # Create version record
        version = MSAVersion(
            msa_id=msa.id,
            version_number=msa.current_version,
            change_summary=f"Renewed MSA: {notes or 'No notes'}",
            changed_by=renewed_by or msa.created_by,
        )
        session.add(version)

        # Audit log
        await self._create_audit_log(
            session,
            user_id=renewed_by or msa.created_by,
            action="RENEW",
            entity_type="MSA",
            entity_id=msa.id,
            new_values=f"Expiration: {new_expiration_date}, Version: {msa.current_version}",
            description=f"Renewed MSA through {new_expiration_date}",
        )

        return msa

    async def check_msa_required(
        self, session: AsyncSession, client_id: int
    ) -> bool:
        """Check if client has signed MSA"""
        stmt = select(MSA).where(
            and_(
                MSA.client_id == client_id,
                MSA.status.in_(["signed", "active", "renewed"]),
            )
        )
        result = await session.execute(stmt)
        return result.scalars().first() is not None

    async def get_active_msa(
        self, session: AsyncSession, client_id: int
    ) -> Optional[MSA]:
        """Get client's active MSA"""
        stmt = (
            select(MSA)
            .where(
                and_(
                    MSA.client_id == client_id,
                    MSA.status.in_(["signed", "active", "renewed"]),
                )
            )
            .order_by(desc(MSA.expiration_date))
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def list_expiring_msas(
        self, session: AsyncSession, days_ahead: int = 30
    ) -> list[MSA]:
        """List MSAs expiring within N days"""
        today = datetime.now(timezone.utc).date()
        expiration_threshold = today + timedelta(days=days_ahead)
        
        stmt = select(MSA).where(
            and_(
                MSA.status.in_(["signed", "active", "renewed"]),
                MSA.expiration_date <= expiration_threshold,
                MSA.expiration_date > today,
            )
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def _create_audit_log(
        self,
        session: AsyncSession,
        user_id: int,
        action: str,
        entity_type: str,
        entity_id: int,
        old_values: Optional[str] = None,
        new_values: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Create audit log entry"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            description=description,
        )
        session.add(audit_log)
```

#### 1.1.4 Create Router/Endpoints

**File**: `app/routers/msa.py` (NEW)

```python
"""MSA (Master Service Agreement) router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.database.models import MSA, MSATemplate
from app.dependencies import get_current_active_user
from app.limiter import limiter
from app.models.msa import (
    MSACreate,
    MSAList,
    MSARenewRequest,
    MSAResponse,
    MSASignatureRequest,
    MSASignatureResponse,
    MSATemplateCreate,
    MSATemplateResponse,
    MSAUpdate,
)
from app.models.user import TokenData
from app.services.msa_service import MSAService

router = APIRouter(prefix="/api/v1/msas", tags=["msas"])


# ============================================================================
# MSA TEMPLATE ENDPOINTS (Admin only)
# ============================================================================


@router.post(
    "/templates",
    response_model=MSATemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create MSA Template",
)
@limiter.limit("5/minute")
async def create_msa_template(
    request: Request,
    template_data: MSATemplateCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> MSATemplateResponse:
    """Create new MSA template (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create MSA templates",
        )

    service = MSAService()
    try:
        template = await service.create_msa_template(
            session,
            template_data.model_dump(),
            current_user.user_id,
        )
        await session.commit()
        return MSATemplateResponse.model_validate(template)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}",
        )


@router.get(
    "/templates",
    response_model=list[MSATemplateResponse],
    summary="List MSA Templates",
)
@limiter.limit("30/minute")
async def list_msa_templates(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: bool | None = None,
    session: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[TokenData, Depends(get_current_active_user)] = None,
) -> list[MSATemplateResponse]:
    """List available MSA templates"""
    stmt = select(MSATemplate)
    if is_active is not None:
        stmt = stmt.where(MSATemplate.is_active == is_active)
    stmt = stmt.offset(skip).limit(limit)
    
    result = await session.execute(stmt)
    templates = result.scalars().all()
    
    return [MSATemplateResponse.model_validate(t) for t in templates]


@router.get(
    "/templates/{template_id}",
    response_model=MSATemplateResponse,
    summary="Get MSA Template",
)
async def get_msa_template(
    template_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> MSATemplateResponse:
    """Get specific MSA template"""
    template = await session.get(MSATemplate, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return MSATemplateResponse.model_validate(template)


# ============================================================================
# MSA ENDPOINTS
# ============================================================================


@router.post(
    "",
    response_model=MSAResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create MSA",
)
@limiter.limit("10/minute")
async def create_msa(
    request: Request,
    msa_data: MSACreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> MSAResponse:
    """Create new MSA for client (PM/Admin only)"""
    if current_user.role not in ["admin", "project_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only PMs and admins can create MSAs",
        )

    service = MSAService()
    try:
        msa = await service.create_msa(session, msa_data, current_user.user_id)
        await session.commit()
        
        # Refresh to get relationships
        await session.refresh(msa)
        return MSAResponse.model_validate(msa)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create MSA: {str(e)}",
        )


@router.get(
    "",
    response_model=MSAList,
    summary="List MSAs",
)
@limiter.limit("30/minute")
async def list_msas(
    request: Request,
    client_id: int | None = None,
    status_filter: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[TokenData, Depends(get_current_active_user)] = None,
) -> MSAList:
    """List MSAs with optional filtering"""
    stmt = select(MSA)
    
    if client_id:
        stmt = stmt.where(MSA.client_id == client_id)
    if status_filter:
        stmt = stmt.where(MSA.status == status_filter)
    
    # Get total count
    count_result = await session.execute(
        select(MSA.__table__.count()).select_from(MSA)
    )
    total = count_result.scalar()
    
    # Get paginated results
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    msas = result.scalars().all()
    
    return MSAList(
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        items=[MSAResponse.model_validate(m) for m in msas],
    )


@router.get("/{msa_id}", response_model=MSAResponse, summary="Get MSA")
async def get_msa(
    msa_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> MSAResponse:
    """Get MSA details"""
    msa = await session.get(MSA, msa_id)
    if not msa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MSA not found",
        )
    return MSAResponse.model_validate(msa)


@router.put("/{msa_id}", response_model=MSAResponse, summary="Update MSA")
@limiter.limit("10/minute")
async def update_msa(
    request: Request,
    msa_id: int,
    msa_data: MSAUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> MSAResponse:
    """Update MSA (only before signing)"""
    msa = await session.get(MSA, msa_id)
    if not msa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MSA not found",
        )
    
    if msa.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Can only update MSAs in draft status",
        )
    
    if msa_data.customizations is not None:
        msa.customizations = msa_data.customizations
    if msa_data.expiration_date is not None:
        msa.expiration_date = msa_data.expiration_date
    
    await session.commit()
    await session.refresh(msa)
    
    return MSAResponse.model_validate(msa)


@router.post(
    "/{msa_id}/sign",
    response_model=MSAResponse,
    summary="Sign MSA",
)
@limiter.limit("20/minute")
async def sign_msa(
    request: Request,
    msa_id: int,
    signature_data: MSASignatureRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> MSAResponse:
    """Record signature on MSA"""
    service = MSAService()
    try:
        msa = await service.sign_msa(
            session,
            msa_id,
            signature_data,
            current_user.user_id,
        )
        await session.commit()
        await session.refresh(msa)
        
        return MSAResponse.model_validate(msa)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sign MSA: {str(e)}",
        )


@router.post(
    "/{msa_id}/renew",
    response_model=MSAResponse,
    summary="Renew MSA",
)
@limiter.limit("10/minute")
async def renew_msa(
    request: Request,
    msa_id: int,
    renew_data: MSARenewRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> MSAResponse:
    """Renew expiring MSA"""
    if current_user.role not in ["admin", "project_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only PMs and admins can renew MSAs",
        )
    
    service = MSAService()
    try:
        msa = await service.renew_msa(
            session,
            msa_id,
            renew_data.new_expiration_date,
            renew_data.notes,
            current_user.user_id,
        )
        await session.commit()
        await session.refresh(msa)
        
        return MSAResponse.model_validate(msa)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to renew MSA: {str(e)}",
        )
```

#### 1.1.5 Update Main Router

**File**: `app/main.py`

Add MSA router to imports and app:

```python
# In imports section, add:
from app.routers import auth, clients, health, invoices, msa, projects, reports, sows, timesheets, users

# In app.include_router() section, add:
app.include_router(msa.router)
```

#### 1.1.6 Create Tests

**File**: `tests/test_msa.py` (NEW)

```python
"""Tests for MSA management endpoints"""

import pytest
from datetime import date, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import MSATemplate
from app.models.msa import MSACreate, MSATemplateCreate


@pytest.mark.asyncio
async def test_create_msa_template(
    client: AsyncClient,
    admin_token: str,
    db_session: AsyncSession,
):
    """Test MSA template creation"""
    template_data = {
        "name": "Standard Services MSA",
        "description": "Standard MSA for professional services",
        "content": "This is a template with {{client_name}} placeholder",
        "version": "1.0",
        "default_terms_days": 30,
        "default_renewal_days": 365,
        "is_active": True,
    }
    
    response = await client.post(
        "/api/v1/msas/templates",
        json=template_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == template_data["name"]
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_msa_template_non_admin_forbidden(
    client: AsyncClient,
    consultant_token: str,
):
    """Test that non-admin users can't create templates"""
    template_data = {
        "name": "Standard Services MSA",
        "content": "Template content",
    }
    
    response = await client.post(
        "/api/v1/msas/templates",
        json=template_data,
        headers={"Authorization": f"Bearer {consultant_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_msa_templates(
    client: AsyncClient,
    admin_token: str,
    db_session: AsyncSession,
):
    """Test listing MSA templates"""
    response = await client.get(
        "/api/v1/msas/templates",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_msa(
    client: AsyncClient,
    pm_token: str,
    db_session: AsyncSession,
    test_client_id: int,
    test_msa_template_id: int,
):
    """Test MSA creation"""
    effective_date = date.today()
    expiration_date = effective_date + timedelta(days=365)
    
    msa_data = {
        "client_id": test_client_id,
        "template_id": test_msa_template_id,
        "effective_date": effective_date.isoformat(),
        "expiration_date": expiration_date.isoformat(),
    }
    
    response = await client.post(
        "/api/v1/msas",
        json=msa_data,
        headers={"Authorization": f"Bearer {pm_token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["client_id"] == test_client_id
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_sign_msa(
    client: AsyncClient,
    pm_token: str,
    test_msa_id: int,
):
    """Test MSA signing"""
    signature_data = {
        "signer_name": "John Client",
        "signer_email": "john@client.com",
        "signer_title": "CEO",
        "signature_date": date.today().isoformat(),
        "signature_method": "electronic",
    }
    
    response = await client.post(
        f"/api/v1/msas/{test_msa_id}/sign",
        json=signature_data,
        headers={"Authorization": f"Bearer {pm_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "signed"
    assert len(data["signatures"]) == 1


@pytest.mark.asyncio
async def test_msa_prevents_update_after_signing(
    client: AsyncClient,
    pm_token: str,
    test_signed_msa_id: int,
):
    """Test that signed MSAs can't be updated"""
    msa_update = {
        "customizations": "New custom terms"
    }
    
    response = await client.put(
        f"/api/v1/msas/{test_signed_msa_id}",
        json=msa_update,
        headers={"Authorization": f"Bearer {pm_token}"},
    )
    
    assert response.status_code == 422
    assert "draft status" in response.json()["detail"]
```

**Run tests**:
```bash
cd /Users/jasonmiller/GitHub/votraio/votra.io
pytest tests/test_msa.py -v --cov=app/services/msa_service.py --cov=app/routers/msa.py
```

---

**Week 1 Summary**: By end of week, you should have:
- ✅ MSA database models created and migrated
- ✅ Pydantic models for requests/responses
- ✅ Service layer with business logic
- ✅ API endpoints for CRUD operations
- ✅ Signature tracking
- ✅ Version control
- ✅ 85%+ test coverage
- ✅ Integration with audit logging

---

## Week 2: NDA Management System

Similar structure to MSA but simpler (single-signer, shorter duration).

[Implementation details follow...]

---

## Week 3: Client Intake Forms

Comprehensive client onboarding with document uploads.

[Implementation details follow...]

---

## Week 4: Integration & Testing

- Integrate MSA requirement into SOW creation
- Integrate NDA requirement into project start
- Add audit logging to all workflows
- Run full test suite (target 85%+ coverage)
- Manual testing of workflows
- Deploy to staging environment

---

## Success Criteria for Phase 1

✅ MSA Management System
- MSA templates created and reusable
- Client can view and sign MSA
- Expiration tracking with alerts
- Multi-signature support
- Version history maintained
- All state changes logged
- 85%+ test coverage

✅ NDA Management System
- Similar capabilities as MSA
- Separate templates for mutual/unidirectional
- Signature tracking
- Expiration alerts
- 85%+ test coverage

✅ Client Intake Forms
- Comprehensive intake form
- Document upload support
- Compliance requirement tracking
- Form validation
- Audit trail
- 85%+ test coverage

✅ Integration
- SOW creation requires signed MSA
- Project creation requires signed NDA (if configured)
- Compliance checklist auto-generated from intake
- All workflows have audit trails
- Email notifications for required actions
- Dashboard shows completion status

✅ Quality
- All endpoints tested
- All validations tested
- RBAC tested
- Error cases handled
- Performance acceptable
- Documentation complete

---

## Frontend Implementation Notes for Phase 1

Frontend components to create:

**MSA UI**:
1. MSATemplateManager - Admin template creation
2. MSACreationForm - Create MSA for client
3. MSASignatureForm - Multi-step signature collection
4. MSAList - View all MSAs with status
5. MSADetail - Full MSA view with action buttons
6. MSARenewalModal - Renew expiring MSA
7. MSAExpirationAlert - Show expiring MSAs in dashboard

**NDA UI**:
- Similar structure to MSA components

**Client Intake UI**:
1. ClientIntakeForm - Multi-section form
2. DocumentUpload - Upload supporting documents
3. IntakeReview - Review and submit
4. IntakeStatus - Show intake status per client

---

**Document Version**: 1.0  
**Created**: February 3, 2026  
**Status**: Ready for Implementation
