"""Timesheet-related Pydantic models."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TimesheetBase(BaseModel):
    """Base timesheet model with common fields."""

    project_id: int = Field(..., gt=0)
    work_date: date
    hours_logged: Decimal = Field(..., gt=0, le=24, decimal_places=2)
    billing_rate: Decimal = Field(..., gt=0, decimal_places=2)
    is_billable: bool = Field(default=True)
    notes: str | None = Field(None, max_length=2000)


class TimesheetCreate(TimesheetBase):
    """Timesheet creation request model."""


class TimesheetUpdate(BaseModel):
    """Timesheet update request model."""

    work_date: date | None = None
    hours_logged: Decimal | None = Field(None, gt=0, le=24, decimal_places=2)
    billing_rate: Decimal | None = Field(None, gt=0, decimal_places=2)
    is_billable: bool | None = None
    notes: str | None = Field(None, max_length=2000)


class TimesheetResponse(BaseModel):
    """Timesheet response model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    consultant_id: int
    work_date: date
    hours_logged: Decimal
    billing_rate: Decimal
    billable_amount: Decimal
    is_billable: bool
    notes: str | None = None
    status: str
    invoice_id: int | None = None
    submitted_at: datetime | None = None
    approved_by: int | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TimesheetList(BaseModel):
    """Timesheet list response model."""

    total: int
    page: int
    per_page: int
    items: list[TimesheetResponse]
