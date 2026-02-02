"""Project-related Pydantic models."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectBase(BaseModel):
    """Base project model with common fields."""

    sow_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    status: str = Field(..., min_length=1, max_length=50)
    start_date: date
    end_date: date
    budget: Decimal = Field(..., gt=0, decimal_places=2)

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: date, info) -> date:
        """Ensure end_date is after start_date."""
        start_date = info.data.get("start_date")
        if start_date and v <= start_date:
            raise ValueError("end_date must be after start_date")
        return v


class ProjectCreate(ProjectBase):
    """Project creation request model."""


class ProjectUpdate(BaseModel):
    """Project update request model."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=5000)
    status: str | None = Field(None, min_length=1, max_length=50)
    end_date: date | None = None
    budget: Decimal | None = Field(None, gt=0, decimal_places=2)


class ProjectResponse(ProjectBase):
    """Project response model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime


class ProjectList(BaseModel):
    """Project list response model."""

    total: int
    page: int
    per_page: int
    items: list[ProjectResponse]
