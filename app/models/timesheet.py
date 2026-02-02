"""Timesheet-related Pydantic models."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TimesheetBase(BaseModel):
    """Base timesheet model with common fields."""

    project_id: int = Field(..., gt=0)
    work_date: date
    hours_logged: Decimal = Field(..., gt=0, le=24, decimal_places=2)
    billing_rate: Decimal = Field(..., gt=0, decimal_places=2)
    billable_amount: Decimal = Field(..., ge=0, decimal_places=2)
    is_billable: bool = Field(default=True)
    notes: Optional[str] = Field(None, max_length=2000)
    status: str = Field(..., min_length=1, max_length=50)

    @field_validator("billable_amount")
    @classmethod
    def validate_billable_amount(cls, v: Decimal) -> Decimal:
        """Ensure billable amount is not negative."""
        if v < 0:
            raise ValueError("billable_amount must be >= 0")
        return v


class TimesheetCreate(TimesheetBase):
    """Timesheet creation request model."""


class TimesheetUpdate(BaseModel):
    """Timesheet update request model."""

    work_date: Optional[date] = None
    hours_logged: Optional[Decimal] = Field(None, gt=0, le=24, decimal_places=2)
    billing_rate: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    billable_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    is_billable: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field(None, min_length=1, max_length=50)


class TimesheetResponse(TimesheetBase):
    """Timesheet response model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    consultant_id: int
    invoice_id: Optional[int] = None
    submitted_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TimesheetList(BaseModel):
    """Timesheet list response model."""

    total: int
    page: int
    per_page: int
    items: list[TimesheetResponse]
