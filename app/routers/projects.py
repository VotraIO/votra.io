"""Router for project management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db
from app.limiter import limiter
from app.models.project import (
    ProjectClose,
    ProjectCreateFromSOW,
    ProjectList,
    ProjectResponse,
    ProjectSummary,
    ProjectUpdate,
)
from app.models.user import TokenData
from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/api/v1/projects",
    tags=["projects"],
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Project",
    description="Create a new project from an approved SOW (project managers only)",
)
@limiter.limit("10/minute")
async def create_project(
    request: Request,
    project_data: ProjectCreateFromSOW,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> ProjectResponse:
    """Create a new project from an approved SOW.

    Args:
        project_data: SOW ID to create project from
        session: Database session
        current_user: Current authenticated user

    Returns:
        ProjectResponse: Created project

    Raises:
        HTTPException: 403 if unauthorized, 422 if validation fails
    """
    # Check permissions - project manager only
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "project_manager",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and project managers can create projects",
        )

    service = ProjectService()
    try:
        project = await service.create_project_from_sow(
            session, project_data.sow_id, created_by=current_user.user_id
        )
        await session.commit()
        await session.refresh(project)
        return ProjectResponse.model_validate(project)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}",
        ) from e


@router.get(
    "",
    response_model=ProjectList,
    status_code=status.HTTP_200_OK,
    summary="List Projects",
    description="List all projects with pagination and filtering",
)
@limiter.limit("30/minute")
async def list_projects(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    status: str | None = Query(None, description="Filter by project status"),
) -> ProjectList:
    """List all projects.

    Args:
        session: Database session
        current_user: Current authenticated user
        skip: Number of records to skip
        limit: Maximum records to return
        status: Filter by project status (in_progress, closed, on_hold)

    Returns:
        ProjectList: Paginated list of projects
    """
    service = ProjectService()
    projects, total = await service.list_projects(
        session, skip=skip, limit=limit, status=status
    )

    return ProjectList(
        total=total,
        skip=skip,
        limit=limit,
        items=[ProjectResponse.model_validate(p) for p in projects],
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Project",
    description="Get project details by ID",
)
@limiter.limit("30/minute")
async def get_project(
    request: Request,
    project_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> ProjectResponse:
    """Get a specific project.

    Args:
        project_id: Project ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        ProjectResponse: Project details

    Raises:
        HTTPException: 404 if project not found
    """
    service = ProjectService()
    project = await service.get_project(session, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    return ProjectResponse.model_validate(project)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Project",
    description="Update project description (project managers only)",
)
@limiter.limit("10/minute")
async def update_project(
    request: Request,
    project_id: int,
    project_data: ProjectUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> ProjectResponse:
    """Update a project.

    Args:
        project_id: Project ID
        project_data: Project update data
        session: Database session
        current_user: Current authenticated user

    Returns:
        ProjectResponse: Updated project

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
    """
    # Check permissions
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "project_manager",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and project managers can update projects",
        )

    service = ProjectService()
    try:
        project = await service.update_project(
            session,
            project_id,
            project_data.description,
            updated_by=current_user.user_id,
        )

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found",
            )

        await session.commit()
        await session.refresh(project)
        return ProjectResponse.model_validate(project)
    except HTTPException:
        await session.rollback()
        raise
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}",
        ) from e


@router.post(
    "/{project_id}/close",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Close Project",
    description="Close a project (project managers only)",
)
@limiter.limit("10/minute")
async def close_project(
    request: Request,
    project_id: int,
    close_data: ProjectClose,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> ProjectResponse:
    """Close a project.

    Args:
        project_id: Project ID
        close_data: Project closing data
        session: Database session
        current_user: Current authenticated user

    Returns:
        ProjectResponse: Closed project

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
    """
    # Check permissions - admin only for project closure
    if not hasattr(current_user, "role") or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can close projects",
        )

    service = ProjectService()
    try:
        project = await service.close_project(
            session, project_id, closed_by=current_user.user_id, notes=close_data.notes
        )

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found",
            )

        await session.commit()
        await session.refresh(project)
        return ProjectResponse.model_validate(project)
    except HTTPException:
        await session.rollback()
        raise
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close project: {str(e)}",
        ) from e


@router.get(
    "/{project_id}/summary",
    response_model=ProjectSummary,
    status_code=status.HTTP_200_OK,
    summary="Get Project Summary",
    description="Get project summary with billing information",
)
@limiter.limit("30/minute")
async def get_project_summary(
    request: Request,
    project_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> ProjectSummary:
    """Get project summary with billing information.

    Args:
        project_id: Project ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        ProjectSummary: Project summary with hours and billing info

    Raises:
        HTTPException: 404 if project not found
    """
    service = ProjectService()
    summary = await service.get_project_summary(session, project_id)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    return summary
