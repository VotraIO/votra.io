"""Router for timesheet management endpoints."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.dependencies import get_current_active_user
from app.limiter import limiter
from app.models.timesheet import (
    TimesheetCreate,
    TimesheetList,
    TimesheetResponse,
    TimesheetUpdate,
)
from app.models.user import TokenData
from app.services.timesheet_service import TimesheetService

router = APIRouter(prefix="/api/v1/timesheets")


@router.post(
    "/",
    response_model=TimesheetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Timesheet",
    description="Submit a new timesheet entry (consultant or admin only)",
)
@limiter.limit("20/minute")
async def create_timesheet(
    request: Request,
    timesheet_data: TimesheetCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> TimesheetResponse:
    """Create a new timesheet entry.

    Args:
        timesheet_data: Timesheet creation data
        session: Database session
        current_user: Current authenticated user

    Returns:
        TimesheetResponse: Created timesheet

    Raises:
        HTTPException: 403 if unauthorized, 422 if validation fails, 500 if creation fails
    """
    # Only consultant, project_manager, or admin can create timesheets
    if current_user.role not in ["consultant", "project_manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants, project managers, and admins can create timesheets",
        )

    service = TimesheetService()
    try:
        timesheet = await service.create_timesheet(
            session,
            project_id=timesheet_data.project_id,
            consultant_id=current_user.user_id,
            work_date=timesheet_data.work_date,
            hours_logged=timesheet_data.hours_logged,
            billing_rate=timesheet_data.billing_rate,
            is_billable=timesheet_data.is_billable,
            notes=timesheet_data.notes,
            created_by=current_user.user_id,
        )
        await session.commit()
        return TimesheetResponse.model_validate(timesheet)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create timesheet: {str(e)}",
        )


@router.get(
    "/",
    response_model=TimesheetList,
    status_code=status.HTTP_200_OK,
    summary="List Timesheets",
    description="List timesheets with filtering and pagination",
)
@limiter.limit("30/minute")
async def list_timesheets(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 10,
    project_id: int | None = None,
    consultant_id: int | None = None,
    status_filter: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> TimesheetList:
    """List timesheets with optional filtering.

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        project_id: Filter by project
        consultant_id: Filter by consultant
        status_filter: Filter by status (draft, submitted, approved, rejected)
        start_date: Filter by work date range start
        end_date: Filter by work date range end
        session: Database session
        current_user: Current authenticated user

    Returns:
        TimesheetList: Paginated timesheet list
    """
    # Consultants can only see their own timesheets
    if current_user.role == "consultant":
        consultant_id = current_user.user_id

    service = TimesheetService()
    try:
        timesheets, total = await service.list_timesheets(
            session,
            skip=skip,
            limit=limit,
            project_id=project_id,
            consultant_id=consultant_id,
            status=status_filter,
            start_date=start_date,
            end_date=end_date,
        )

        return TimesheetList(
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            items=[TimesheetResponse.model_validate(t) for t in timesheets],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list timesheets: {str(e)}",
        )


@router.get(
    "/{timesheet_id}",
    response_model=TimesheetResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Timesheet Detail",
    description="Get a specific timesheet's details",
)
@limiter.limit("30/minute")
async def get_timesheet(
    request: Request,
    timesheet_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> TimesheetResponse:
    """Get a specific timesheet by ID.

    Args:
        timesheet_id: ID of timesheet to retrieve
        session: Database session
        current_user: Current authenticated user

    Returns:
        TimesheetResponse: Timesheet details

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
    """
    service = TimesheetService()
    try:
        timesheet = await service.get_timesheet(session, timesheet_id)

        # Consultants can only view their own timesheets
        if current_user.role == "consultant" and timesheet.consultant_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own timesheets",
            )

        return TimesheetResponse.model_validate(timesheet)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Timesheet not found"
        )


@router.put(
    "/{timesheet_id}",
    response_model=TimesheetResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Timesheet",
    description="Update a timesheet entry (draft only, consultant only)",
)
@limiter.limit("10/minute")
async def update_timesheet(
    request: Request,
    timesheet_id: int,
    timesheet_data: TimesheetUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> TimesheetResponse:
    """Update a timesheet entry.

    Args:
        timesheet_id: ID of timesheet to update
        timesheet_data: Updated timesheet data
        session: Database session
        current_user: Current authenticated user

    Returns:
        TimesheetResponse: Updated timesheet

    Raises:
        HTTPException: 403 if unauthorized, 404 if not found, 422 if validation fails
    """
    service = TimesheetService()
    try:
        timesheet = await service.get_timesheet(session, timesheet_id)

        # Only consultant who created it or admin can update
        if (
            current_user.role not in ["admin", "project_manager"]
            and timesheet.consultant_id != current_user.user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own timesheets",
            )

        updated = await service.update_timesheet(
            session,
            timesheet_id,
            work_date=timesheet_data.work_date,
            hours_logged=timesheet_data.hours_logged,
            billing_rate=timesheet_data.billing_rate,
            is_billable=timesheet_data.is_billable,
            notes=timesheet_data.notes,
            updated_by=current_user.user_id,
        )
        await session.commit()
        return TimesheetResponse.model_validate(updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@router.post(
    "/{timesheet_id}/submit",
    response_model=TimesheetResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Timesheet",
    description="Submit a timesheet for approval (draft → submitted)",
)
@limiter.limit("10/minute")
async def submit_timesheet(
    request: Request,
    timesheet_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> TimesheetResponse:
    """Submit a timesheet for approval.

    Args:
        timesheet_id: ID of timesheet to submit
        session: Database session
        current_user: Current authenticated user

    Returns:
        TimesheetResponse: Updated timesheet

    Raises:
        HTTPException: 403 if unauthorized, 404 if not found, 422 if invalid state
    """
    service = TimesheetService()
    try:
        timesheet = await service.get_timesheet(session, timesheet_id)

        # Only consultant who created it or admin can submit
        if (
            current_user.role not in ["admin", "project_manager"]
            and timesheet.consultant_id != current_user.user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only submit your own timesheets",
            )

        submitted = await service.submit_timesheet(
            session, timesheet_id, submitted_by=current_user.user_id
        )
        await session.commit()
        return TimesheetResponse.model_validate(submitted)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@router.post(
    "/{timesheet_id}/approve",
    response_model=TimesheetResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve Timesheet",
    description="Approve a timesheet for billing (project manager or admin only)",
)
@limiter.limit("10/minute")
async def approve_timesheet(
    request: Request,
    timesheet_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> TimesheetResponse:
    """Approve a timesheet.

    Args:
        timesheet_id: ID of timesheet to approve
        session: Database session
        current_user: Current authenticated user

    Returns:
        TimesheetResponse: Updated timesheet

    Raises:
        HTTPException: 403 if unauthorized, 404 if not found, 422 if invalid state
    """
    # Only PM and admin can approve
    if current_user.role not in ["project_manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project managers and admins can approve timesheets",
        )

    service = TimesheetService()
    try:
        approved = await service.approve_timesheet(
            session, timesheet_id, approved_by=current_user.user_id
        )
        await session.commit()
        return TimesheetResponse.model_validate(approved)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@router.post(
    "/{timesheet_id}/reject",
    response_model=TimesheetResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject Timesheet",
    description="Reject a timesheet (project manager or admin only)",
)
@limiter.limit("10/minute")
async def reject_timesheet(
    request: Request,
    timesheet_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
    reason: str | None = None,
) -> TimesheetResponse:
    """Reject a timesheet.

    Args:
        timesheet_id: ID of timesheet to reject
        session: Database session
        current_user: Current authenticated user
        reason: Reason for rejection

    Returns:
        TimesheetResponse: Updated timesheet

    Raises:
        HTTPException: 403 if unauthorized, 404 if not found, 422 if invalid state
    """
    # Only PM and admin can reject
    if current_user.role not in ["project_manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project managers and admins can reject timesheets",
        )

    service = TimesheetService()
    try:
        rejected = await service.reject_timesheet(
            session, timesheet_id, rejection_reason=reason, rejected_by=current_user.user_id
        )
        await session.commit()
        return TimesheetResponse.model_validate(rejected)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@router.get(
    "/{timesheet_id}/summary",
    status_code=status.HTTP_200_OK,
    summary="Get Timesheet Summary",
    description="Get summary information for timesheet entries",
)
@limiter.limit("30/minute")
async def get_timesheet_summary(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
    project_id: int | None = None,
    consultant_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    status_filter: str | None = None,
) -> dict:
    """Get summary of timesheet entries.

    Args:
        project_id: Filter by project
        consultant_id: Filter by consultant
        start_date: Filter by work date start
        end_date: Filter by work date end
        status_filter: Filter by status
        session: Database session
        current_user: Current authenticated user

    Returns:
        dict: Summary with total hours and billable amounts
    """
    # Consultants can only see their own summaries
    if current_user.role == "consultant":
        consultant_id = current_user.user_id

    service = TimesheetService()
    try:
        summary = await service.get_timesheet_summary(
            session,
            project_id=project_id,
            consultant_id=consultant_id,
            start_date=start_date,
            end_date=end_date,
            status=status_filter,
        )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}",
        )
