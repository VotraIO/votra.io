"""Client-related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientBase(BaseModel):
    """Base client model with common fields."""

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(..., description="Client email address")
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)
    billing_address: Optional[str] = Field(None, max_length=2000)
    payment_terms: int = Field(default=30, ge=0, le=365)
    is_active: bool = Field(default=True)


class ClientCreate(ClientBase):
    """Client creation request model."""


class ClientUpdate(BaseModel):
    """Client update request model."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)
    billing_address: Optional[str] = Field(None, max_length=2000)
    payment_terms: Optional[int] = Field(None, ge=0, le=365)
    is_active: Optional[bool] = None


class ClientResponse(ClientBase):
    """Client response model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ClientList(BaseModel):
    """Client list response model."""

    total: int
    page: int
    per_page: int
    items: list[ClientResponse]
