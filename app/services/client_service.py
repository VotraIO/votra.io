"""Client service for managing client records."""


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Client
from app.models.client import ClientCreate, ClientUpdate
from app.utils.audit import log_audit


class ClientService:
    """Service for client management operations."""

    async def create_client(
        self, session: AsyncSession, client_data: ClientCreate, created_by: int
    ) -> Client:
        """Create a new client.

        Args:
            session: Database session
            client_data: Client creation data
            created_by: ID of user creating the client

        Returns:
            Client: Created client object

        Raises:
            ValueError: If client with same email already exists
        """
        # Check if client with email already exists
        existing = await session.execute(
            select(Client).where(Client.email == client_data.email)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Client with email {client_data.email} already exists")

        client = Client(**client_data.model_dump())
        session.add(client)
        await session.flush()
        await session.refresh(client)

        # Log audit entry
        await log_audit(
            session=session,
            user_id=created_by,
            action="create",
            entity_type="client",
            entity_id=client.id,
            new_values={
                "name": client.name,
                "email": client.email,
                "company": client.company,
            },
            description=f"Client '{client.name}' created",
        )

        return client

    async def get_client(
        self, session: AsyncSession, client_id: int
    ) -> Client | None:
        """Get a client by ID.

        Args:
            session: Database session
            client_id: Client ID

        Returns:
            Optional[Client]: Client object if found, None otherwise
        """
        result = await session.execute(select(Client).where(Client.id == client_id))
        return result.scalar_one_or_none()

    async def get_client_by_email(
        self, session: AsyncSession, email: str
    ) -> Client | None:
        """Get a client by email address.

        Args:
            session: Database session
            email: Email address

        Returns:
            Optional[Client]: Client object if found, None otherwise
        """
        result = await session.execute(select(Client).where(Client.email == email))
        return result.scalar_one_or_none()

    async def list_clients(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None,
    ) -> tuple[list[Client], int]:
        """List all clients with optional filtering.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status (None = all)

        Returns:
            Tuple of (list of clients, total count)
        """
        query = select(Client)

        if is_active is not None:
            query = query.where(Client.is_active == is_active)

        # Get total count
        count_result = await session.execute(select(Client))
        if is_active is not None:
            count_result = await session.execute(
                select(Client).where(Client.is_active == is_active)
            )
        total = len(count_result.all())

        # Get paginated results
        result = await session.execute(query.offset(skip).limit(limit))
        return result.scalars().all(), total

    async def update_client(
        self, session: AsyncSession, client_id: int, client_data: ClientUpdate, updated_by: int
    ) -> Client | None:
        """Update a client.

        Args:
            session: Database session
            client_id: Client ID
            client_data: Client update data
            updated_by: ID of user updating the client

        Returns:
            Optional[Client]: Updated client object if found, None otherwise

        Raises:
            ValueError: If updating email to one that already exists
        """
        client = await self.get_client(session, client_id)
        if not client:
            return None

        # Check if updating email to one that already exists
        if client_data.email and client_data.email != client.email:
            existing = await self.get_client_by_email(session, client_data.email)
            if existing:
                raise ValueError(
                    f"Client with email {client_data.email} already exists"
                )

        # Capture old values before update
        update_data = client_data.model_dump(exclude_unset=True)
        old_values = {key: getattr(client, key, None) for key in update_data.keys()}

        # Update only provided fields
        for key, value in update_data.items():
            setattr(client, key, value)

        await session.flush()
        await session.refresh(client)

        # Log audit entry
        await log_audit(
            session=session,
            user_id=updated_by,
            action="update",
            entity_type="client",
            entity_id=client.id,
            old_values=old_values,
            new_values=update_data,
            description=f"Client '{client.name}' updated",
        )

        return client

    async def delete_client(
        self, session: AsyncSession, client_id: int, deleted_by: int
    ) -> Client | None:
        """Delete (deactivate) a client.

        Args:
            session: Database session
            client_id: Client ID
            deleted_by: ID of user deleting the client

        Returns:
            Optional[Client]: Deleted client object if found, None otherwise
        """
        client = await self.get_client(session, client_id)
        if not client:
            return None

        client.is_active = False
        await session.flush()
        await session.refresh(client)

        # Log audit entry
        await log_audit(
            session=session,
            user_id=deleted_by,
            action="delete",
            entity_type="client",
            entity_id=client.id,
            old_values={"is_active": True},
            new_values={"is_active": False},
            description=f"Client '{client.name}' deactivated",
        )

        return client
