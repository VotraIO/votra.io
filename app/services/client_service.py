"""Client service for managing client records."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Client
from app.models.client import ClientCreate, ClientUpdate


class ClientService:
    """Service for client management operations."""

    async def create_client(
        self, session: AsyncSession, client_data: ClientCreate
    ) -> Client:
        """Create a new client.

        Args:
            session: Database session
            client_data: Client creation data

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
        return client

    async def get_client(
        self, session: AsyncSession, client_id: int
    ) -> Optional[Client]:
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
    ) -> Optional[Client]:
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
        is_active: Optional[bool] = None,
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
        self, session: AsyncSession, client_id: int, client_data: ClientUpdate
    ) -> Optional[Client]:
        """Update a client.

        Args:
            session: Database session
            client_id: Client ID
            client_data: Client update data

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

        # Update only provided fields
        update_data = client_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(client, key, value)

        await session.flush()
        return client

    async def delete_client(
        self, session: AsyncSession, client_id: int
    ) -> Optional[Client]:
        """Delete (deactivate) a client.

        Args:
            session: Database session
            client_id: Client ID

        Returns:
            Optional[Client]: Deleted client object if found, None otherwise
        """
        client = await self.get_client(session, client_id)
        if not client:
            return None

        client.is_active = False
        await session.flush()
        return client
