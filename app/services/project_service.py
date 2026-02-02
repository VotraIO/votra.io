"""Project service for managing project records and workflow."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import SOW, Project
from app.models.project import ProjectSummary
from app.utils.audit import log_audit


class ProjectService:
    """Service for project management operations."""

    async def create_project_from_sow(
        self, session: AsyncSession, sow_id: int, created_by: int
    ) -> Project:
        """Create a new project from an approved SOW.

        Args:
            session: Database session
            sow_id: ID of the SOW to create project from
            created_by: User ID creating the project

        Returns:
            Project: Created project object

        Raises:
            ValueError: If SOW not found, not approved, or project already exists
        """
        # Get SOW
        result = await session.execute(select(SOW).where(SOW.id == sow_id))
        sow = result.scalar_one_or_none()

        if not sow:
            raise ValueError(f"SOW with ID {sow_id} not found")

        if sow.status != "approved":
            raise ValueError(
                f"SOW must be approved to create a project (current status: {sow.status})"
            )

        # Check if project already exists for this SOW
        existing = await session.execute(
            select(Project).where(Project.sow_id == sow_id)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Project already exists for SOW {sow_id}")

        # Create project from SOW
        project = Project(
            sow_id=sow_id,
            name=sow.title,
            description=sow.description,
            status="in_progress",
            start_date=sow.start_date,
            end_date=sow.end_date,
            budget=sow.total_budget,
            created_by=created_by,
        )

        session.add(project)
        await session.flush()
        await session.refresh(project)

        # Log audit entry
        await log_audit(
            session=session,
            user_id=created_by,
            action="create",
            entity_type="project",
            entity_id=project.id,
            new_values={
                "status": project.status,
                "sow_id": sow_id,
                "name": project.name,
                "budget": str(project.budget),
            },
            description=f"Project '{project.name}' created from approved SOW {sow_id}",
        )

        return project

    async def get_project(
        self, session: AsyncSession, project_id: int
    ) -> Project | None:
        """Get a project by ID.

        Args:
            session: Database session
            project_id: Project ID

        Returns:
            Optional[Project]: Project object if found, None otherwise
        """
        result = await session.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    async def list_projects(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> tuple[list[Project], int]:
        """List projects with optional filtering.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by project status (in_progress, closed, on_hold)

        Returns:
            Tuple of (list of projects, total count)
        """
        query = select(Project)

        if status:
            query = query.where(Project.status == status)

        # Get total count
        count_result = await session.execute(select(Project))
        if status:
            count_result = await session.execute(
                select(Project).where(Project.status == status)
            )
        total = len(count_result.all())

        # Get paginated results
        result = await session.execute(
            query.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def update_project(
        self,
        session: AsyncSession,
        project_id: int,
        description: str | None,
        updated_by: int,
    ) -> Project | None:
        """Update project description only.

        Args:
            session: Database session
            project_id: Project ID
            description: Updated description
            updated_by: User ID performing the update

        Returns:
            Optional[Project]: Updated project if found, None otherwise

        Raises:
            ValueError: If trying to update closed project
        """
        project = await self.get_project(session, project_id)
        if not project:
            return None

        if project.status == "closed":
            raise ValueError("Cannot update a closed project")

        old_description = project.description
        if description is not None:
            project.description = description
            await session.flush()
            await session.refresh(project)

            # Log audit entry
            await log_audit(
                session=session,
                user_id=updated_by,
                action="update",
                entity_type="project",
                entity_id=project.id,
                old_values={"description": old_description},
                new_values={"description": description},
                description=f"Project '{project.name}' description updated",
            )

        return project

    async def close_project(
        self,
        session: AsyncSession,
        project_id: int,
        closed_by: int,
        notes: str | None = None,
    ) -> Project | None:
        """Close a project.

        Args:
            session: Database session
            project_id: Project ID
            closed_by: User ID closing the project
            notes: Optional closing notes

        Returns:
            Optional[Project]: Closed project if found, None otherwise

        Raises:
            ValueError: If project already closed
        """
        project = await self.get_project(session, project_id)
        if not project:
            return None

        if project.status == "closed":
            raise ValueError("Project is already closed")

        old_status = project.status
        project.status = "closed"
        await session.flush()
        await session.refresh(project)

        # Log audit entry
        await log_audit(
            session=session,
            user_id=closed_by,
            action="close",
            entity_type="project",
            entity_id=project.id,
            old_values={"status": old_status},
            new_values={"status": "closed"},
            description=f"Project '{project.name}' closed by user {closed_by}"
            + (f" with notes: {notes}" if notes else ""),
        )

        return project

    async def get_project_summary(
        self, session: AsyncSession, project_id: int
    ) -> ProjectSummary | None:
        """Get project summary with billing information.

        Args:
            session: Database session
            project_id: Project ID

        Returns:
            Optional[ProjectSummary]: Project summary if found, None otherwise
        """
        project = await self.get_project(session, project_id)
        if not project:
            return None

        # TODO: Calculate hours and billable amount from timesheets
        # For now, return zeros (will be implemented in timesheet task)
        total_hours = Decimal("0")
        billable_amount = Decimal("0")

        # Calculate percentages
        hours_percentage = 0.0
        budget_percentage = (
            float(billable_amount / project.budget * 100) if project.budget > 0 else 0.0
        )

        return ProjectSummary(
            id=project.id,
            sow_id=project.sow_id,
            name=project.name,
            status=project.status,
            start_date=project.start_date,
            end_date=project.end_date,
            budget=project.budget,
            total_hours=total_hours,
            billable_amount=billable_amount,
            hours_percentage=hours_percentage,
            budget_percentage=budget_percentage,
        )
