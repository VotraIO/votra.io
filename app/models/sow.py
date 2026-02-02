"""SOW (Statement of Work) Pydantic models."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SOWBase(BaseModel):
    """Base SOW model with common fields."""

    client_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    start_date: date
    end_date: date
    rate: Decimal = Field(..., gt=0, decimal_places=2)
    total_budget: Decimal = Field(..., gt=0, decimal_places=2)

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: date, info) -> date:
        """Ensure end_date is after start_date."""
        start_date = info.data.get("start_date")
        if start_date and v <= start_date:
            raise ValueError("end_date must be after start_date")
        return v


class SOWCreate(SOWBase):
    """SOW creation request model."""


class SOWUpdate(BaseModel):
    """SOW update request model."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    rate: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    total_budget: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


class SOWResponse(SOWBase):
    """SOW response model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class SOWApprove(BaseModel):
    """SOW approval request model."""

    approved: bool = Field(..., description="Whether the SOW is approved")
    notes: Optional[str] = Field(None, max_length=2000)


class SOWList(BaseModel):
    """SOW list response model."""

    total: int
    page: int
    per_page: int
    items: list[SOWResponse]
