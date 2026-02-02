"""Database models (SQLAlchemy ORM)."""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class User(Base):
    """User database model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="consultant", nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    created_sows = relationship(
        "SOW",
        back_populates="creator",
        foreign_keys="SOW.created_by",
        cascade="all, delete-orphan",
    )
    approved_sows = relationship(
        "SOW",
        back_populates="approver",
        foreign_keys="SOW.approved_by",
    )
    created_projects = relationship(
        "Project",
        back_populates="creator",
        foreign_keys="Project.created_by",
        cascade="all, delete-orphan",
    )
    timesheets = relationship(
        "Timesheet",
        back_populates="consultant",
        foreign_keys="Timesheet.consultant_id",
        cascade="all, delete-orphan",
    )
    approved_timesheets = relationship(
        "Timesheet",
        back_populates="approver",
        foreign_keys="Timesheet.approved_by",
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        foreign_keys="AuditLog.user_id",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Client(Base):
    """Client database model."""

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True)
    billing_address = Column(Text, nullable=True)
    payment_terms = Column(Integer, default=30, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sows = relationship("SOW", back_populates="client", cascade="all, delete-orphan")
    invoices = relationship(
        "Invoice", back_populates="client", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Client."""
        return f"<Client(id={self.id}, name='{self.name}')>"


class SOW(Base):
    """Statement of Work (SOW) database model."""

    __tablename__ = "sows"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    rate = Column(Numeric(10, 2), nullable=False)
    total_budget = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    client = relationship("Client", back_populates="sows")
    creator = relationship(
        "User", back_populates="created_sows", foreign_keys=[created_by]
    )
    approver = relationship(
        "User", back_populates="approved_sows", foreign_keys=[approved_by]
    )
    projects = relationship(
        "Project", back_populates="sow", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of SOW."""
        return f"<SOW(id={self.id}, title='{self.title}', status='{self.status}')>"


class Project(Base):
    """Project database model."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    sow_id = Column(Integer, ForeignKey("sows.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Numeric(12, 2), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sow = relationship("SOW", back_populates="projects")
    creator = relationship(
        "User", back_populates="created_projects", foreign_keys=[created_by]
    )
    timesheets = relationship(
        "Timesheet", back_populates="project", cascade="all, delete-orphan"
    )
    invoices = relationship("Invoice", back_populates="project")

    def __repr__(self) -> str:
        """String representation of Project."""
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"


class Timesheet(Base):
    """Timesheet entry database model."""

    __tablename__ = "timesheets"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    consultant_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True)
    work_date = Column(Date, nullable=False, index=True)
    hours_logged = Column(Numeric(5, 2), nullable=False)
    billing_rate = Column(Numeric(10, 2), nullable=False)
    billable_amount = Column(Numeric(12, 2), nullable=False)
    is_billable = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, index=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    project = relationship("Project", back_populates="timesheets")
    consultant = relationship(
        "User", back_populates="timesheets", foreign_keys=[consultant_id]
    )
    approver = relationship(
        "User", back_populates="approved_timesheets", foreign_keys=[approved_by]
    )
    invoice = relationship("Invoice", back_populates="timesheets")

    def __repr__(self) -> str:
        """String representation of Timesheet."""
        return (
            f"<Timesheet(id={self.id}, project_id={self.project_id}, "
            f"work_date={self.work_date}, status='{self.status}')>"
        )


class Invoice(Base):
    """Invoice database model."""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    subtotal = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(12, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(12, 2), nullable=False, default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    payment_date = Column(Date, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    client = relationship("Client", back_populates="invoices")
    project = relationship("Project", back_populates="invoices")
    line_items = relationship(
        "LineItem", back_populates="invoice", cascade="all, delete-orphan"
    )
    timesheets = relationship("Timesheet", back_populates="invoice")

    def __repr__(self) -> str:
        """String representation of Invoice."""
        return f"<Invoice(id={self.id}, invoice_number='{self.invoice_number}')>"


class LineItem(Base):
    """Invoice line item database model."""

    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(12, 2), nullable=False)

    invoice = relationship("Invoice", back_populates="line_items")

    def __repr__(self) -> str:
        """String representation of LineItem."""
        return f"<LineItem(id={self.id}, invoice_id={self.invoice_id})>"


class AuditLog(Base):
    """Audit log database model."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="audit_logs", foreign_keys=[user_id])

    def __repr__(self) -> str:
        """String representation of AuditLog."""
        return (
            f"<AuditLog(id={self.id}, action='{self.action}', "
            f"entity_type='{self.entity_type}', entity_id={self.entity_id})>"
        )
