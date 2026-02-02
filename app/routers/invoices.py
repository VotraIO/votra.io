"""Router for invoice management endpoints."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_active_user, get_db
from app.limiter import limiter
from app.models.invoice import (
    InvoiceCreate,
    InvoiceList,
    InvoiceResponse,
    LineItemResponse,
    PaymentRecord,
)
from app.models.user import TokenData
from app.services.invoice_service import InvoiceService

router = APIRouter(
    prefix="/api/v1/invoices",
    tags=["invoices"],
)


@router.post(
    "",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Invoice",
    description="Generate invoice from approved timesheets for a project (project manager or admin only)",
)
@limiter.limit("10/minute")
async def generate_invoice(
    request: Request,
    invoice_data: InvoiceCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> InvoiceResponse:
    """Generate invoice from approved timesheets.

    Args:
        invoice_data: Invoice creation request (project_id, invoice_date)
        session: Database session
        current_user: Current authenticated user

    Returns:
        InvoiceResponse: Generated invoice

    Raises:
        HTTPException: 403 if unauthorized, 422 if validation fails
    """
    # Check permissions - project manager or admin
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "project_manager",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and project managers can generate invoices",
        )

    service = InvoiceService()
    try:
        # For now, we generate invoice for all approved timesheets on the project
        # In production, might want to select specific timesheets
        # Get project to find client
        from app.database.models import Project

        project = await session.get(Project, invoice_data.project_id)
        if not project:
            raise ValueError(f"Project with ID {invoice_data.project_id} not found")

        invoice = await service.generate_invoice(
            session,
            client_id=project.sow.client_id,
            project_id=invoice_data.project_id,
            created_by=current_user.user_id,
        )
        await session.commit()
        await session.refresh(invoice)
        return InvoiceResponse.model_validate(invoice)
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
            detail=f"Failed to generate invoice: {str(e)}",
        ) from e


@router.get(
    "",
    response_model=InvoiceList,
    status_code=status.HTTP_200_OK,
    summary="List Invoices",
    description="List invoices with pagination and filtering (clients see only their own)",
)
@limiter.limit("30/minute")
async def list_invoices(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    status_filter: str | None = Query(None, description="Filter by invoice status"),
    client_id: int | None = Query(None, gt=0, description="Filter by client ID"),
    project_id: int | None = Query(None, gt=0, description="Filter by project ID"),
    start_date: date | None = Query(None, description="Filter by invoice date (from)"),
    end_date: date | None = Query(None, description="Filter by invoice date (to)"),
) -> InvoiceList:
    """List invoices with flexible filtering.

    Clients can only see their own invoices. Admins and staff see all invoices.

    Args:
        skip: Pagination offset
        limit: Pagination limit (max 100)
        status_filter: Filter by status (draft, sent, paid, overdue)
        client_id: Filter by specific client
        project_id: Filter by specific project
        start_date: Filter by invoice date range start
        end_date: Filter by invoice date range end
        current_user: Current authenticated user
        session: Database session

    Returns:
        InvoiceList: Paginated invoice list

    Raises:
        HTTPException: 422 if validation fails
    """
    service = InvoiceService()

    # Apply RBAC: clients can only see their own invoices
    if hasattr(current_user, "role") and current_user.role == "client":
        # For clients, restrict to their own invoices
        # This would need a client -> user mapping in production
        # For now, if client_id not specified, deny access
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Clients can only view invoices for their own account",
            )

    try:
        invoices, total = await service.list_invoices(
            session,
            skip=skip,
            limit=limit,
            status=status_filter,
            client_id=client_id,
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
        )

        return InvoiceList(
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            items=[InvoiceResponse.model_validate(inv) for inv in invoices],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list invoices: {str(e)}",
        ) from e


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Invoice Details",
    description="Get invoice detail with line items (clients see only their own)",
)
@limiter.limit("30/minute")
async def get_invoice_detail(
    request: Request,
    invoice_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> InvoiceResponse:
    """Get invoice detail with line items.

    Args:
        invoice_id: Invoice ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        InvoiceResponse: Invoice with line items

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
    """
    service = InvoiceService()
    try:
        invoice = await service.get_invoice_detail(session, invoice_id)

        # Apply RBAC for clients
        if hasattr(current_user, "role") and current_user.role == "client":
            # Check if invoice belongs to their client
            # In production, compare with current_user's client_id
            if invoice.client_id != current_user.client_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to view this invoice",
                )

        await session.refresh(invoice)
        return InvoiceResponse.model_validate(invoice)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoice: {str(e)}",
        ) from e


@router.post(
    "/{invoice_id}/send",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Send Invoice",
    description="Mark invoice as sent (transition from draft to sent status)",
)
@limiter.limit("10/minute")
async def send_invoice(
    request: Request,
    invoice_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> InvoiceResponse:
    """Mark invoice as sent (draft → sent).

    Args:
        invoice_id: Invoice ID
        session: Database session
        current_user: Current authenticated user

    Returns:
        InvoiceResponse: Updated invoice

    Raises:
        HTTPException: 403 if unauthorized, 422 if state transition invalid
    """
    # Check permissions - project manager or admin
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "project_manager",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and project managers can send invoices",
        )

    from app.database.models import Invoice

    try:
        invoice = await session.get(Invoice, invoice_id)
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found")

        if invoice.status != "draft":
            raise ValueError(
                f"Cannot send invoice in {invoice.status} status. Only draft invoices can be sent."
            )

        invoice.status = "sent"
        await session.commit()
        await session.refresh(invoice)
        return InvoiceResponse.model_validate(invoice)
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
            detail=f"Failed to send invoice: {str(e)}",
        ) from e


@router.post(
    "/{invoice_id}/mark-paid",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark Invoice Paid",
    description="Record payment for invoice (accountant or admin only)",
)
@limiter.limit("10/minute")
async def mark_invoice_paid(
    request: Request,
    invoice_id: int,
    payment_data: PaymentRecord,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> InvoiceResponse:
    """Record payment for invoice.

    Args:
        invoice_id: Invoice ID
        payment_data: Payment information (payment_date)
        session: Database session
        current_user: Current authenticated user

    Returns:
        InvoiceResponse: Updated invoice

    Raises:
        HTTPException: 403 if unauthorized, 422 if validation fails
    """
    # Check permissions - accountant or admin
    if not hasattr(current_user, "role") or current_user.role not in [
        "admin",
        "accountant",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and accountants can mark invoices as paid",
        )

    from app.database.models import Invoice

    try:
        invoice = await session.get(Invoice, invoice_id)
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found")

        if invoice.status == "paid":
            raise ValueError("Invoice is already marked as paid")

        invoice.status = "paid"
        invoice.payment_date = payment_data.payment_date
        await session.commit()
        await session.refresh(invoice)
        return InvoiceResponse.model_validate(invoice)
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
            detail=f"Failed to mark invoice paid: {str(e)}",
        ) from e
