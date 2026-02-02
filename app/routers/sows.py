"""SOW (Statement of Work) router with endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.dependencies import get_current_active_user
from app.limiter import limiter
from app.models.sow import SOWApprove, SOWCreate, SOWList, SOWResponse, SOWUpdate
from app.models.user import TokenData
from app.services.sow_service import SOWService

router = APIRouter(prefix="/api/v1/sows")


@router.post(
    "/",
    response_model=SOWResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create SOW",
    description="Create a new Statement of Work in draft status (admin and project managers only)",
)
@limiter.limit("10/minute")
async def create_sow(
    request: Request,
    sow_data: SOWCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> SOWResponse:
    """Create a new SOW.

    Args:
        sow_data: SOW creation data
        session: Database session
        current_user: Current authenticated user

    Returns:
        SOWResponse: Created SOW

    Raises:
        HTTPException: 403 if unauthorized, 422 if validation fails, 500 if creation fails
    """
    # Check permissions - only admin and project_manager can create SOWs
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "project_manager",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and project managers can create SOWs",
        )

    service = SOWService()
    try:
        sow = await service.create_sow(
            session, sow_data, created_by=current_user.user_id
        )
        await session.commit()
        await session.refresh(sow)
        return SOWResponse.model_validate(sow)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create SOW: {str(e)}",
        )


@router.get(
    "/",
    response_model=SOWList,
    status_code=status.HTTP_200_OK,
    summary="List SOWs",
    description="List all SOWs with optional filtering by status and client",
)
@limiter.limit("30/minute")
async def list_sows(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = None,
    client_id: int | None = None,
) -> SOWList:
    """List SOWs with pagination and filtering.

    Args:
        session: Database session
        current_user: Current authenticated user
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Filter by status (draft, pending, approved, rejected)
        client_id: Filter by client ID

    Returns:
        SOWList: Paginated list of SOWs
    """
    service = SOWService()
    sows, total = await service.list_sows(
        session, skip=skip, limit=limit, status=status_filter, client_id=client_id
    )

    return SOWList(
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        per_page=limit,
        items=[SOWResponse.model_validate(sow) for sow in sows],
    )


@router.get(
    "/{sow_id}",
    response_model=SOWResponse,
    status_code=status.HTTP_200_OK,
    summary="Get SOW",
    description="Get a specific SOW by ID",
)
@limiter.limit("30/minute")
async def get_sow(
    request: Request,
    sow_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> SOWResponse:
    """Get a SOW by ID.

    Args:
        sow_id: SOW ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        SOWResponse: SOW details

    Raises:
        HTTPException: 404 if not found
    """
    service = SOWService()
    sow = await service.get_sow(session, sow_id)

    if not sow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SOW with ID {sow_id} not found",
        )

    return SOWResponse.model_validate(sow)


@router.put(
    "/{sow_id}",
    response_model=SOWResponse,
    status_code=status.HTTP_200_OK,
    summary="Update SOW",
    description="Update a SOW (only if in draft status)",
)
@limiter.limit("10/minute")
async def update_sow(
    request: Request,
    sow_id: int,
    sow_data: SOWUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> SOWResponse:
    """Update a SOW.

    Args:
        sow_id: SOW ID
        sow_data: SOW update data
        session: Database session
        current_user: Current authenticated user

    Returns:
        SOWResponse: Updated SOW

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 422 if not in draft status
    """
    # Check permissions
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "project_manager",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and project managers can update SOWs",
        )

    service = SOWService()
    try:
        sow = await service.update_sow(session, sow_id, sow_data)

        if not sow:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SOW with ID {sow_id} not found",
            )

        await session.commit()
        await session.refresh(sow)
        return SOWResponse.model_validate(sow)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update SOW: {str(e)}",
        )


@router.post(
    "/{sow_id}/submit",
    response_model=SOWResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit SOW",
    description="Submit a SOW for approval (draft → pending)",
)
@limiter.limit("10/minute")
async def submit_sow(
    request: Request,
    sow_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> SOWResponse:
    """Submit a SOW for approval.

    Args:
        sow_id: SOW ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        SOWResponse: Updated SOW

    Raises:
        HTTPException: 404 if not found, 422 if not in draft status
    """
    service = SOWService()
    try:
        sow = await service.submit_sow(session, sow_id)

        if not sow:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SOW with ID {sow_id} not found",
            )

        await session.commit()
        await session.refresh(sow)
        return SOWResponse.model_validate(sow)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit SOW: {str(e)}",
        )


@router.post(
    "/{sow_id}/approve",
    response_model=SOWResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve/Reject SOW",
    description="Approve or reject a SOW (admin only, pending → approved/rejected)",
)
@limiter.limit("10/minute")
async def approve_sow(
    request: Request,
    sow_id: int,
    approval_data: SOWApprove,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> SOWResponse:
    """Approve or reject a SOW.

    Args:
        sow_id: SOW ID
        approval_data: Approval decision and notes
        session: Database session
        current_user: Current authenticated user

    Returns:
        SOWResponse: Updated SOW

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 422 if not in pending status
    """
    # Check permissions - only admin can approve/reject
    if not hasattr(current_user, "role") or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can approve or reject SOWs",
        )

    service = SOWService()
    try:
        sow = await service.approve_sow(
            session, sow_id, approval_data, approved_by=current_user.user_id
        )

        if not sow:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SOW with ID {sow_id} not found",
            )

        await session.commit()
        await session.refresh(sow)
        return SOWResponse.model_validate(sow)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve/reject SOW: {str(e)}",
        )
