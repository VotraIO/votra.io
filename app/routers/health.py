"""Health check router."""

from datetime import datetime, timezone

from fastapi import APIRouter, Request, status

from app.limiter import limiter
from app.models.common import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the API is running and healthy",
)
@limiter.limit("10/minute")
async def health_check(request: Request) -> HealthResponse:
    """Health check endpoint.

    Returns:
        HealthResponse: API health status
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get(
    "/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Root Endpoint",
    description="API root information",
)
async def root() -> dict:
    """Root endpoint with API information.

    Returns:
        dict: API information
    """
    return {
        "name": "Votra.io API",
        "version": "0.1.0",
        "documentation": "/docs",
        "health": "/health",
    }
