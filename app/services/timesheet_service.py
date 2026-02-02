"""Timesheet service for managing time entries and billing."""

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Project, Timesheet
from app.models.timesheet import TimesheetResponse
from app.utils.audit import log_audit


class TimesheetService:
    """Service for timesheet management operations."""

    async def create_timesheet(
        self,
        session: AsyncSession,
        project_id: int,
        consultant_id: int,
        work_date: date,
        hours_logged: Decimal,
        billing_rate: Decimal,
        is_billable: bool = True,
        notes: str | None = None,
        created_by: int | None = None,
    ) -> Timesheet:
        """Create a new timesheet entry.

        Args:
            session: Database session
            project_id: ID of project
            consultant_id: ID of consultant/user
            work_date: Date of work
            hours_logged: Hours worked (0-24)
            billing_rate: Billing rate per hour
            is_billable: Whether billable to client
            notes: Optional notes
            created_by: User ID creating the timesheet

        Returns:
            Timesheet: Created timesheet object

        Raises:
            ValueError: If validation fails
        """
        # Validate project exists and is active
        result = await session.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Validate work_date is within project dates
        if work_date < project.start_date or work_date > project.end_date:
            raise ValueError(
                f"work_date must be between {project.start_date} and {project.end_date}"
            )

        # Validate hours
        if hours_logged <= 0 or hours_logged > 24:
            raise ValueError("hours_logged must be between 0 and 24")

        # Calculate billable amount
        billable_amount = hours_logged * billing_rate if is_billable else Decimal("0")

        # Create timesheet in draft status
        timesheet = Timesheet(
            project_id=project_id,
            consultant_id=consultant_id,
            work_date=work_date,
            hours_logged=hours_logged,
            billing_rate=billing_rate,
            billable_amount=billable_amount,
            is_billable=is_billable,
            notes=notes,
            status="draft",
        )

        session.add(timesheet)
        await session.flush()

        # Log audit entry
        await log_audit(
            session,
            user_id=created_by or consultant_id,
            action="create",
            entity_type="timesheet",
            entity_id=timesheet.id,
            new_values={
                "project_id": project_id,
                "work_date": str(work_date),
                "hours_logged": str(hours_logged),
                "billing_rate": str(billing_rate),
                "is_billable": is_billable,
            },
            description=f"Timesheet entry created for {work_date}: {hours_logged} hours",
        )

        return timesheet

    async def get_timesheet(
        self, session: AsyncSession, timesheet_id: int
    ) -> Timesheet:
        """Get a timesheet by ID.

        Args:
            session: Database session
            timesheet_id: ID of timesheet

        Returns:
            Timesheet: The timesheet object

        Raises:
            ValueError: If timesheet not found
        """
        result = await session.execute(
            select(Timesheet).where(Timesheet.id == timesheet_id)
        )
        timesheet = result.scalar_one_or_none()

        if not timesheet:
            raise ValueError(f"Timesheet with ID {timesheet_id} not found")

        return timesheet

    async def list_timesheets(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        project_id: int | None = None,
        consultant_id: int | None = None,
        status: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[list[Timesheet], int]:
        """List timesheets with filtering and pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Number of records to return
            project_id: Filter by project
            consultant_id: Filter by consultant
            status: Filter by status
            start_date: Filter by work date range start
            end_date: Filter by work date range end

        Returns:
            tuple: (list of timesheets, total count)
        """
        query = select(Timesheet)

        if project_id:
            query = query.where(Timesheet.project_id == project_id)
        if consultant_id:
            query = query.where(Timesheet.consultant_id == consultant_id)
        if status:
            query = query.where(Timesheet.status == status)
        if start_date:
            query = query.where(Timesheet.work_date >= start_date)
        if end_date:
            query = query.where(Timesheet.work_date <= end_date)

        # Get total count
        count_result = await session.execute(
            select(Timesheet) if not any([project_id, consultant_id, status, start_date, end_date])
            else query
        )
        total = len(count_result.fetchall())

        # Get paginated results
        result = await session.execute(query.offset(skip).limit(limit))
        timesheets = result.scalars().all()

        return list(timesheets), total

    async def update_timesheet(
        self,
        session: AsyncSession,
        timesheet_id: int,
        work_date: date | None = None,
        hours_logged: Decimal | None = None,
        billing_rate: Decimal | None = None,
        is_billable: bool | None = None,
        notes: str | None = None,
        updated_by: int | None = None,
    ) -> Timesheet:
        """Update a timesheet entry (draft only).

        Args:
            session: Database session
            timesheet_id: ID of timesheet
            work_date: Updated work date
            hours_logged: Updated hours
            billing_rate: Updated billing rate
            is_billable: Updated billable status
            notes: Updated notes
            updated_by: User ID performing update

        Returns:
            Timesheet: Updated timesheet object

        Raises:
            ValueError: If timesheet not found, not draft, or validation fails
        """
        timesheet = await self.get_timesheet(session, timesheet_id)

        # Only allow updates to draft timesheets
        if timesheet.status != "draft":
            raise ValueError(
                f"Cannot update timesheet with status '{timesheet.status}' (only draft can be updated)"
            )

        # Store old values for audit
        old_values = {
            "work_date": str(timesheet.work_date),
            "hours_logged": str(timesheet.hours_logged),
            "billing_rate": str(timesheet.billing_rate),
            "is_billable": timesheet.is_billable,
            "notes": timesheet.notes,
        }

        # Update fields
        if work_date:
            timesheet.work_date = work_date
        if hours_logged is not None:
            timesheet.hours_logged = hours_logged
        if billing_rate is not None:
            timesheet.billing_rate = billing_rate
        if is_billable is not None:
            timesheet.is_billable = is_billable
        if notes is not None:
            timesheet.notes = notes

        # Recalculate billable amount
        timesheet.billable_amount = (
            timesheet.hours_logged * timesheet.billing_rate
            if timesheet.is_billable
            else Decimal("0")
        )

        timesheet.updated_at = datetime.now(timezone.utc)
        await session.flush()

        # Log audit entry
        await log_audit(
            session,
            user_id=updated_by or 0,
            action="update",
            entity_type="timesheet",
            entity_id=timesheet.id,
            old_values=old_values,
            new_values={
                "work_date": str(timesheet.work_date),
                "hours_logged": str(timesheet.hours_logged),
                "billing_rate": str(timesheet.billing_rate),
                "is_billable": timesheet.is_billable,
                "notes": timesheet.notes,
            },
            description=f"Timesheet entry updated: {timesheet.hours_logged} hours at ${timesheet.billing_rate}/hr",
        )

        return timesheet

    async def submit_timesheet(
        self, session: AsyncSession, timesheet_id: int, submitted_by: int | None = None
    ) -> Timesheet:
        """Submit a timesheet for approval (draft → submitted).

        Args:
            session: Database session
            timesheet_id: ID of timesheet
            submitted_by: User ID submitting

        Returns:
            Timesheet: Updated timesheet object

        Raises:
            ValueError: If timesheet not found or not draft
        """
        timesheet = await self.get_timesheet(session, timesheet_id)

        if timesheet.status != "draft":
            raise ValueError(f"Can only submit draft timesheets (current: {timesheet.status})")

        timesheet.status = "submitted"
        timesheet.submitted_at = datetime.now(timezone.utc)
        timesheet.updated_at = datetime.now(timezone.utc)
        await session.flush()

        # Log audit entry
        await log_audit(
            session,
            user_id=submitted_by or timesheet.consultant_id,
            action="submit",
            entity_type="timesheet",
            entity_id=timesheet.id,
            new_values={"status": "submitted", "submitted_at": str(datetime.now(timezone.utc))},
            description=f"Timesheet {timesheet_id} submitted for approval",
        )

        return timesheet

    async def approve_timesheet(
        self,
        session: AsyncSession,
        timesheet_id: int,
        approved_by: int | None = None,
    ) -> Timesheet:
        """Approve a timesheet (submitted → approved).

        Args:
            session: Database session
            timesheet_id: ID of timesheet
            approved_by: User ID (PM) approving

        Returns:
            Timesheet: Updated timesheet object

        Raises:
            ValueError: If timesheet not found or not submitted
        """
        timesheet = await self.get_timesheet(session, timesheet_id)

        if timesheet.status != "submitted":
            raise ValueError(
                f"Can only approve submitted timesheets (current: {timesheet.status})"
            )

        timesheet.status = "approved"
        timesheet.approved_by = approved_by
        timesheet.approved_at = datetime.now(timezone.utc)
        timesheet.updated_at = datetime.now(timezone.utc)
        await session.flush()

        # Log audit entry
        await log_audit(
            session,
            user_id=approved_by or 0,
            action="approve",
            entity_type="timesheet",
            entity_id=timesheet.id,
            new_values={"status": "approved", "approved_at": str(datetime.now(timezone.utc))},
            description=f"Timesheet {timesheet_id} approved for billing",
        )

        return timesheet

    async def reject_timesheet(
        self,
        session: AsyncSession,
        timesheet_id: int,
        rejection_reason: str | None = None,
        rejected_by: int | None = None,
    ) -> Timesheet:
        """Reject a timesheet (submitted → rejected).

        Args:
            session: Database session
            timesheet_id: ID of timesheet
            rejection_reason: Reason for rejection
            rejected_by: User ID (PM) rejecting

        Returns:
            Timesheet: Updated timesheet object

        Raises:
            ValueError: If timesheet not found or not submitted
        """
        timesheet = await self.get_timesheet(session, timesheet_id)

        if timesheet.status != "submitted":
            raise ValueError(
                f"Can only reject submitted timesheets (current: {timesheet.status})"
            )

        timesheet.status = "rejected"
        if rejection_reason:
            timesheet.notes = f"[REJECTED] {rejection_reason}"
        timesheet.updated_at = datetime.now(timezone.utc)
        await session.flush()

        # Log audit entry
        await log_audit(
            session,
            user_id=rejected_by or 0,
            action="reject",
            entity_type="timesheet",
            entity_id=timesheet.id,
            new_values={"status": "rejected", "reason": rejection_reason or "No reason provided"},
            description=f"Timesheet {timesheet_id} rejected: {rejection_reason}",
        )

        return timesheet

    async def get_timesheet_summary(
        self,
        session: AsyncSession,
        project_id: int | None = None,
        consultant_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status: str | None = None,
    ) -> dict:
        """Get summary of timesheet entries (total hours, billable amount).

        Args:
            session: Database session
            project_id: Filter by project
            consultant_id: Filter by consultant
            start_date: Filter by start date
            end_date: Filter by end date
            status: Filter by status

        Returns:
            dict: Summary with total_hours, total_billable, entry_count
        """
        query = select(Timesheet)

        if project_id:
            query = query.where(Timesheet.project_id == project_id)
        if consultant_id:
            query = query.where(Timesheet.consultant_id == consultant_id)
        if start_date:
            query = query.where(Timesheet.work_date >= start_date)
        if end_date:
            query = query.where(Timesheet.work_date <= end_date)
        if status:
            query = query.where(Timesheet.status == status)

        result = await session.execute(query)
        timesheets = result.scalars().all()

        total_hours = sum(t.hours_logged for t in timesheets) if timesheets else Decimal("0")
        total_billable = (
            sum(t.billable_amount for t in timesheets) if timesheets else Decimal("0")
        )
        approved_hours = sum(
            t.hours_logged for t in timesheets if t.status == "approved"
        )
        approved_billable = sum(
            t.billable_amount for t in timesheets if t.status == "approved"
        )

        return {
            "total_hours": str(total_hours),
            "total_billable": str(total_billable),
            "approved_hours": str(approved_hours),
            "approved_billable": str(approved_billable),
            "entry_count": len(timesheets),
            "approved_count": sum(1 for t in timesheets if t.status == "approved"),
            "pending_count": sum(1 for t in timesheets if t.status == "submitted"),
        }
