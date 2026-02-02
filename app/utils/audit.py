"""Audit logging utilities."""

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AuditLog


async def log_audit(
    session: AsyncSession,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
    description: str | None = None,
) -> AuditLog:
    """Create an audit log entry.

    Args:
        session: Database session
        user_id: ID of user performing the action
        action: Action being performed (e.g., 'create', 'update', 'delete', 'approve', 'reject')
        entity_type: Type of entity (e.g., 'sow', 'client', 'project', 'invoice')
        entity_id: ID of the entity
        old_values: Previous state of the entity (for updates)
        new_values: New state of the entity (for updates/creates)
        description: Optional human-readable description

    Returns:
        AuditLog: Created audit log entry

    Example:
        >>> await log_audit(
        ...     session=session,
        ...     user_id=1,
        ...     action="approve",
        ...     entity_type="sow",
        ...     entity_id=123,
        ...     old_values={"status": "pending"},
        ...     new_values={"status": "approved", "approved_by": 1},
        ...     description="SOW approved by admin"
        ... )
    """
    # Serialize values to JSON strings
    old_values_json = json.dumps(old_values) if old_values else None
    new_values_json = json.dumps(new_values) if new_values else None

    # Create audit log entry
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values_json,
        new_values=new_values_json,
        description=description,
    )

    session.add(audit_log)
    await session.flush()
    await session.refresh(audit_log)

    return audit_log


async def get_audit_logs(
    session: AsyncSession,
    entity_type: str | None = None,
    entity_id: int | None = None,
    user_id: int | None = None,
    action: str | None = None,
    limit: int = 100,
    skip: int = 0,
) -> list[AuditLog]:
    """Retrieve audit logs with optional filtering.

    Args:
        session: Database session
        entity_type: Filter by entity type
        entity_id: Filter by entity ID
        user_id: Filter by user ID
        action: Filter by action
        limit: Maximum number of records to return
        skip: Number of records to skip

    Returns:
        list[AuditLog]: List of audit log entries
    """
    from sqlalchemy import select

    query = select(AuditLog).order_by(AuditLog.created_at.desc())

    # Apply filters
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.where(AuditLog.entity_id == entity_id)
    if user_id is not None:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()


def parse_audit_values(values_json: str | None) -> dict[str, Any] | None:
    """Parse JSON string to dictionary.

    Args:
        values_json: JSON string of values

    Returns:
        dict[str, Any] | None: Parsed dictionary or None
    """
    if not values_json:
        return None

    try:
        return json.loads(values_json)
    except json.JSONDecodeError:
        return None
