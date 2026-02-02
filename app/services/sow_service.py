"""SOW (Statement of Work) service with business logic."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import SOW
from app.models.sow import SOWApprove, SOWCreate, SOWUpdate
from app.utils.audit import log_audit


class SOWService:
    """Service class for SOW operations."""

    async def create_sow(
        self, session: AsyncSession, sow_data: SOWCreate, created_by: int
    ) -> SOW:
        """Create a new SOW with draft status.

        Args:
            session: Database session
            sow_data: SOW creation data
            created_by: User ID of creator

        Returns:
            SOW: Created SOW object

        Raises:
            ValueError: If validation fails
        """
        # Validate that client exists
        from app.database.models import Client

        client_result = await session.execute(
            select(Client).where(Client.id == sow_data.client_id)
        )
        client = client_result.scalar_one_or_none()
        if not client:
            raise ValueError(f"Client with ID {sow_data.client_id} not found")

        # Create SOW with draft status
        sow = SOW(
            **sow_data.model_dump(),
            status="draft",
            created_by=created_by,
        )

        session.add(sow)
        await session.flush()
        await session.refresh(sow)

        # Log audit entry
        await log_audit(
            session=session,
            user_id=created_by,
            action="create",
            entity_type="sow",
            entity_id=sow.id,
            new_values={
                "status": sow.status,
                "client_id": sow.client_id,
                "title": sow.title,
                "total_budget": str(sow.total_budget),
            },
            description=f"SOW '{sow.title}' created in draft status",
        )

        return sow

    async def get_sow(self, session: AsyncSession, sow_id: int) -> SOW | None:
        """Get a SOW by ID.

        Args:
            session: Database session
            sow_id: SOW ID

        Returns:
            Optional[SOW]: SOW object if found, None otherwise
        """
        result = await session.execute(select(SOW).where(SOW.id == sow_id))
        return result.scalar_one_or_none()

    async def list_sows(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        client_id: int | None = None,
    ) -> tuple[list[SOW], int]:
        """List SOWs with pagination and filtering.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            client_id: Filter by client ID

        Returns:
            tuple[list[SOW], int]: List of SOWs and total count
        """
        query = select(SOW)

        # Apply filters
        if status:
            query = query.where(SOW.status == status)
        if client_id:
            query = query.where(SOW.client_id == client_id)

        # Get total count
        count_query = select(SOW)
        if status:
            count_query = count_query.where(SOW.status == status)
        if client_id:
            count_query = count_query.where(SOW.client_id == client_id)

        count_result = await session.execute(count_query)
        total = len(count_result.all())

        # Get paginated results
        result = await session.execute(query.offset(skip).limit(limit))
        return result.scalars().all(), total

    async def update_sow(
        self, session: AsyncSession, sow_id: int, sow_data: SOWUpdate
    ) -> SOW | None:
        """Update a SOW (only if in draft status).

        Args:
            session: Database session
            sow_id: SOW ID
            sow_data: SOW update data

        Returns:
            Optional[SOW]: Updated SOW object if found, None otherwise

        Raises:
            ValueError: If SOW is not in draft status
        """
        sow = await self.get_sow(session, sow_id)
        if not sow:
            return None

        # Only allow updates if SOW is in draft status
        if sow.status != "draft":
            raise ValueError(
                f"Cannot update SOW with status '{sow.status}'. Only draft SOWs can be updated."
            )

        # Update only provided fields
        update_data = sow_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(sow, key, value)

        await session.flush()
        await session.refresh(sow)
        return sow

    async def submit_sow(self, session: AsyncSession, sow_id: int) -> SOW | None:
        """Submit SOW for approval (draft → pending).

        Args:
            session: Database session
            sow_id: SOW ID

        Returns:
            Optional[SOW]: Updated SOW object if found, None otherwise

        Raises:
            ValueError: If SOW is not in draft status
        """
        sow = await self.get_sow(session, sow_id)
        if not sow:
            return None

        if sow.status != "draft":
            raise ValueError(
                f"Cannot submit SOW with status '{sow.status}'. Only draft SOWs can be submitted."
            )

        old_status = sow.status
        sow.status = "pending"
        await session.flush()
        await session.refresh(sow)

        # Log audit entry
        await log_audit(
            session=session,
            user_id=sow.created_by,  # Assuming creator submits
            action="submit",
            entity_type="sow",
            entity_id=sow.id,
            old_values={"status": old_status},
            new_values={"status": "pending"},
            description=f"SOW '{sow.title}' submitted for approval",
        )

        return sow

    async def approve_sow(
        self,
        session: AsyncSession,
        sow_id: int,
        approval_data: SOWApprove,
        approved_by: int,
    ) -> SOW | None:
        """Approve or reject a SOW (pending → approved/rejected).

        Args:
            session: Database session
            sow_id: SOW ID
            approval_data: Approval decision and notes
            approved_by: User ID of approver

        Returns:
            Optional[SOW]: Updated SOW object if found, None otherwise

        Raises:
            ValueError: If SOW is not in pending status
        """
        sow = await self.get_sow(session, sow_id)
        if not sow:
            return None

        if sow.status != "pending":
            raise ValueError(
                f"Cannot approve/reject SOW with status '{sow.status}'. Only pending SOWs can be approved/rejected."
            )

        # Update status based on approval decision
        old_status = sow.status
        new_status = "approved" if approval_data.approved else "rejected"
        sow.status = new_status
        sow.approved_by = approved_by
        sow.approved_at = datetime.now(timezone.utc)

        await session.flush()
        await session.refresh(sow)

        # Log audit entry
        action = "approve" if approval_data.approved else "reject"
        await log_audit(
            session=session,
            user_id=approved_by,
            action=action,
            entity_type="sow",
            entity_id=sow.id,
            old_values={"status": old_status},
            new_values={
                "status": new_status,
                "approved_by": approved_by,
                "approved_at": sow.approved_at.isoformat(),
            },
            description=f"SOW '{sow.title}' {new_status} by user {approved_by}",
        )

        return sow

    async def reject_sow(
        self, session: AsyncSession, sow_id: int, approved_by: int, notes: str
    ) -> SOW | None:
        """Reject a SOW (pending → rejected).

        Args:
            session: Database session
            sow_id: SOW ID
            approved_by: User ID of approver
            notes: Rejection reason

        Returns:
            Optional[SOW]: Updated SOW object if found, None otherwise

        Raises:
            ValueError: If SOW is not in pending status
        """
        approval_data = SOWApprove(approved=False, notes=notes)
        return await self.approve_sow(session, sow_id, approval_data, approved_by)
