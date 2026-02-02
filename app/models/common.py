"""Common Pydantic models."""


from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str = Field(..., description="Error message")
    error_code: str | None = Field(None, description="Error code")


class SuccessResponse(BaseModel):
    """Standard success response model."""

    message: str = Field(..., description="Success message")
    data: dict | None = Field(None, description="Response data")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(default="healthy", description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
