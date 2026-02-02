"""Clients router."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db
from app.limiter import limiter
from app.models.client import ClientCreate, ClientList, ClientResponse, ClientUpdate
from app.models.user import TokenData
from app.services.client_service import ClientService

router = APIRouter(prefix="/api/v1/clients", tags=["clients"])


def require_role(*allowed_roles):
    """Factory function to create role-based dependency.

    Args:
        allowed_roles: Tuple of allowed role names

    Returns:
        Callable that checks if user has required role
    """

    async def check_role(current_user: TokenData = Depends(get_current_active_user)):
        """Check if user has required role."""
        if not hasattr(current_user, "role") or current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {allowed_roles}",
            )
        return current_user

    return check_role


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Client",
    description="Create a new client (admin and project managers only)",
)
@limiter.limit("10/minute")
async def create_client(
    request: Request,
    client_data: ClientCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> ClientResponse:
    """Create a new client.

    Args:
        client_data: Client creation data
        session: Database session
        current_user: Current authenticated user

    Returns:
        ClientResponse: Created client

    Raises:
        HTTPException: 409 if email already exists, 403 if unauthorized
    """
    # Check permissions (admin and pm roles)
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "project_manager",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and project managers can create clients",
        )

    service = ClientService()
    try:
        client = await service.create_client(session, client_data, current_user.user_id)
        await session.commit()
        await session.refresh(client)
        return ClientResponse.model_validate(client)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create client: {str(e)}",
        )


@router.get(
    "",
    response_model=ClientList,
    status_code=status.HTTP_200_OK,
    summary="List Clients",
    description="List all clients with pagination and filtering",
)
@limiter.limit("30/minute")
async def list_clients(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    is_active: bool | None = Query(None),
) -> ClientList:
    """List all clients.

    Args:
        session: Database session
        current_user: Current authenticated user
        skip: Number of records to skip
        limit: Maximum records to return
        is_active: Filter by active status

    Returns:
        ClientList: Paginated list of clients
    """
    service = ClientService()
    clients, total = await service.list_clients(
        session, skip=skip, limit=limit, is_active=is_active
    )

    return ClientList(
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        items=[ClientResponse.model_validate(c) for c in clients],
    )


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Client",
    description="Get a specific client by ID",
)
@limiter.limit("30/minute")
async def get_client(
    request: Request,
    client_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> ClientResponse:
    """Get a specific client.

    Args:
        client_id: Client ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        ClientResponse: Client details

    Raises:
        HTTPException: 404 if client not found
    """
    service = ClientService()
    client = await service.get_client(session, client_id)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found",
        )

    return ClientResponse.model_validate(client)


@router.put(
    "/{client_id}",
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Client",
    description="Update a client (admin and project managers only)",
)
@limiter.limit("10/minute")
async def update_client(
    request: Request,
    client_id: int,
    client_data: ClientUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> ClientResponse:
    """Update a client.

    Args:
        client_id: Client ID
        client_data: Client update data
        session: Database session
        current_user: Current authenticated user

    Returns:
        ClientResponse: Updated client

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 409 if email exists
    """
    # Check permissions
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "project_manager",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and project managers can update clients",
        )

    service = ClientService()
    try:
        client = await service.update_client(session, client_id, client_data, current_user.user_id)

        if not client:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found",
            )

        await session.commit()
        await session.refresh(client)
        return ClientResponse.model_validate(client)
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update client: {str(e)}",
        )


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Client",
    description="Deactivate a client (admin only)",
)
@limiter.limit("5/minute")
async def delete_client(
    request: Request,
    client_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> None:
    """Delete (deactivate) a client.

    Args:
        client_id: Client ID
        session: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
    """
    # Check permissions - admin only for deletion
    if not hasattr(current_user, "role") or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete clients",
        )

    service = ClientService()
    try:
        client = await service.delete_client(session, client_id, current_user.user_id)

        if not client:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found",
            )

        await session.commit()
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete client: {str(e)}",
        )
