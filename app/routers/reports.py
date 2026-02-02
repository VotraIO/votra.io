"""
Reports and analytics API endpoints.

Provides business intelligence endpoints for revenue tracking,
consultant utilization, and overdue invoice management.
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.dependencies import get_current_active_user, get_db
from app.limiter import limiter
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/v1/reports")


@router.get("/revenue")
@limiter.limit("30/minute")
async def get_revenue_report(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    start_date: date | None = Query(None, description="Start date for report period"),
    end_date: date | None = Query(None, description="End date for report period"),
    client_id: int | None = Query(None, description="Filter by specific client"),
) -> dict:
    """
    Get revenue report with breakdown by client.

    Returns paid invoice data aggregated by client with totals and averages.
    Requires admin or project manager role.

    Args:
        request: HTTP request (for rate limiting)
        db: Database session
        current_user: Authenticated user
        start_date: Optional start date filter
        end_date: Optional end date filter
        client_id: Optional client filter

    Returns:
        Revenue report with summary and breakdown

    Raises:
        HTTPException: 403 if user lacks permission
    """
    # RBAC: Only admin and project managers can view revenue reports
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "project_manager",
        "accountant",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators, project managers, and accountants can view revenue reports",
        )

    # Validate date range
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must be before or equal to end_date",
        )

    report = await ReportService.get_revenue_report(
        db=db,
        start_date=start_date,
        end_date=end_date,
        client_id=client_id,
    )

    return report


@router.get("/utilization")
@limiter.limit("30/minute")
async def get_utilization_report(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    start_date: date | None = Query(None, description="Start date for report period"),
    end_date: date | None = Query(None, description="End date for report period"),
    consultant_id: int | None = Query(
        None, description="Filter by specific consultant"
    ),
) -> dict:
    """
    Get consultant utilization report.

    Returns billable vs non-billable hours with utilization rates.
    Requires admin or project manager role.

    Args:
        request: HTTP request (for rate limiting)
        db: Database session
        current_user: Authenticated user
        start_date: Optional start date filter
        end_date: Optional end date filter
        consultant_id: Optional consultant filter

    Returns:
        Utilization report with summary and breakdown

    Raises:
        HTTPException: 403 if user lacks permission
    """
    # RBAC: Only admin and project managers can view utilization reports
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "project_manager",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and project managers can view utilization reports",
        )

    # Validate date range
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must be before or equal to end_date",
        )

    report = await ReportService.get_utilization_report(
        db=db,
        start_date=start_date,
        end_date=end_date,
        consultant_id=consultant_id,
    )

    return report


@router.get("/overdue-invoices")
@limiter.limit("30/minute")
async def get_overdue_invoices(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    days_overdue: int = Query(
        0, ge=0, description="Minimum days overdue (0 = all overdue)"
    ),
) -> dict:
    """
    Get overdue invoices report.

    Lists all invoices past their due date with details.
    Requires admin, project manager, or accountant role.

    Args:
        request: HTTP request (for rate limiting)
        db: Database session
        current_user: Authenticated user
        days_overdue: Minimum days overdue filter (default 0 = all)

    Returns:
        Overdue invoices with summary metrics

    Raises:
        HTTPException: 403 if user lacks permission
    """
    # RBAC: Admin, PM, and accountants can view overdue invoices
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "project_manager",
        "accountant",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators, project managers, and accountants can view overdue invoices",
        )

    report = await ReportService.get_overdue_invoices(db=db, days_overdue=days_overdue)

    return report
