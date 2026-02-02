"""Project-related Pydantic models."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreateFromSOW(BaseModel):
    """Request model for creating a project from an approved SOW."""

    sow_id: int = Field(..., gt=0, description="ID of the approved SOW")


class ProjectUpdate(BaseModel):
    """Project update request model - only description can be updated."""

    description: str | None = Field(
        None, max_length=1000, description="Updated description"
    )


class ProjectClose(BaseModel):
    """Request model for closing a project."""

    notes: str | None = Field(None, max_length=500, description="Closing notes")


class ProjectResponse(BaseModel):
    """Project response model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sow_id: int
    name: str
    description: str | None
    status: str
    start_date: date
    end_date: date
    budget: Decimal
    created_by: int
    created_at: datetime
    updated_at: datetime


class ProjectSummary(BaseModel):
    """Response model for project summary with billing information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sow_id: int
    name: str
    status: str
    start_date: date
    end_date: date
    budget: Decimal
    total_hours: Decimal = Field(
        default=Decimal("0"), description="Total hours from timesheets"
    )
    billable_amount: Decimal = Field(
        default=Decimal("0"),
        description="Total billable amount from approved timesheets",
    )
    hours_percentage: float = Field(
        default=0.0, description="Percentage of allocated hours used"
    )
    budget_percentage: float = Field(
        default=0.0, description="Percentage of budget utilized"
    )


class ProjectList(BaseModel):
    """Project list response model."""

    total: int
    skip: int
    limit: int
    items: list[ProjectResponse]
