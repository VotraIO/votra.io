"""Invoice-related Pydantic models."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InvoiceBase(BaseModel):
    """Base invoice model with common fields."""

    client_id: int = Field(..., gt=0)
    project_id: int | None = Field(None, gt=0)
    invoice_number: str = Field(..., min_length=1, max_length=50)
    invoice_date: date
    due_date: date
    subtotal: Decimal = Field(..., ge=0, decimal_places=2)
    tax_amount: Decimal = Field(default=0, ge=0, decimal_places=2)
    discount_amount: Decimal = Field(default=0, ge=0, decimal_places=2)
    total_amount: Decimal = Field(..., ge=0, decimal_places=2)
    status: str = Field(..., min_length=1, max_length=50)
    payment_date: date | None = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: date, info) -> date:
        """Ensure due_date is not before invoice_date."""
        invoice_date = info.data.get("invoice_date")
        if invoice_date and v < invoice_date:
            raise ValueError("due_date must be on or after invoice_date")
        return v


class InvoiceCreate(BaseModel):
    """Invoice creation request model."""

    project_id: int = Field(..., gt=0)
    invoice_date: date


class InvoiceResponse(InvoiceBase):
    """Invoice response model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class InvoiceList(BaseModel):
    """Invoice list response model."""

    total: int
    page: int
    per_page: int
    items: list[InvoiceResponse]


class LineItemBase(BaseModel):
    """Invoice line item base model."""

    description: str = Field(..., min_length=1, max_length=255)
    quantity: Decimal = Field(..., gt=0, decimal_places=2)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)
    line_total: Decimal = Field(..., ge=0, decimal_places=2)


class LineItemResponse(LineItemBase):
    """Invoice line item response model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int


class PaymentRecord(BaseModel):
    """Invoice payment record request model."""

    payment_date: date
