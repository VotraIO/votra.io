"""Invoice service for managing invoices and billing."""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Client, Invoice, LineItem, Project, Timesheet
from app.models.invoice import InvoiceResponse
from app.utils.audit import log_audit


class InvoiceService:
    """Service for invoice management operations."""

    async def generate_invoice(
        self,
        session: AsyncSession,
        client_id: int,
        project_id: int,
        created_by: int | None = None,
    ) -> Invoice:
        """Generate invoice from approved timesheets.

        Args:
            session: Database session
            client_id: ID of client to invoice
            project_id: ID of project to invoice for
            created_by: User ID creating the invoice

        Returns:
            Invoice: Created invoice object

        Raises:
            ValueError: If no approved timesheets or validation fails
        """
        # Get approved timesheets for project that haven't been invoiced
        result = await session.execute(
            select(Timesheet).where(
                and_(
                    Timesheet.project_id == project_id,
                    Timesheet.status == "approved",
                    Timesheet.invoice_id.is_(None),
                )
            )
        )
        timesheets = result.scalars().all()

        if not timesheets:
            raise ValueError(f"No approved timesheets found for project {project_id}")

        # Get client and project for validation
        client = await session.get(Client, client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")

        project = await session.get(Project, project_id)
        if not project:
            raise ValueError(f"Project with ID {project_id} not found")

        # Calculate totals
        subtotal = sum(timesheet.billable_amount for timesheet in timesheets)

        # Apply tax (10% for MVP)
        tax_rate = Decimal("0.10")
        tax_amount = (subtotal * tax_rate).quantize(Decimal("0.01"))
        total_amount = (subtotal + tax_amount).quantize(Decimal("0.01"))

        # Generate invoice number (format: INV-YYYYMMDD-NNNN)
        now = datetime.now(timezone.utc)
        invoice_date = now.date()
        invoice_number = await self._generate_invoice_number(session, invoice_date)

        # Create invoice
        invoice = Invoice(
            client_id=client_id,
            project_id=project_id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=None,  # Will be set based on payment terms
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=Decimal("0"),
            total_amount=total_amount,
            status="draft",
        )

        session.add(invoice)
        await session.flush()

        # Create line items from timesheets
        for timesheet in timesheets:
            line_item = LineItem(
                invoice_id=invoice.id,
                description=f"Consulting services - {timesheet.work_date}",
                quantity=timesheet.hours_logged,
                unit_price=timesheet.billing_rate,
                line_total=timesheet.billable_amount,
            )
            session.add(line_item)
            # Mark timesheet as invoiced
            timesheet.invoice_id = invoice.id

        await session.flush()

        # Log audit entry
        await log_audit(
            session,
            user_id=created_by or 1,
            action="create",
            entity_type="invoice",
            entity_id=invoice.id,
            new_values={
                "client_id": client_id,
                "project_id": project_id,
                "subtotal": str(subtotal),
                "tax_amount": str(tax_amount),
                "total_amount": str(total_amount),
            },
            description=f"Invoice {invoice_number} generated for {len(timesheets)} timesheets",
        )

        return invoice

    async def _generate_invoice_number(
        self, session: AsyncSession, invoice_date
    ) -> str:
        """Generate unique invoice number.

        Format: INV-YYYYMMDD-NNNN
        """
        date_str = invoice_date.strftime("%Y%m%d")

        # Count invoices created on this date
        result = await session.execute(
            select(Invoice).where(Invoice.invoice_number.like(f"INV-{date_str}-%"))
        )
        invoices_today = result.scalars().all()
        sequence = len(invoices_today) + 1

        return f"INV-{date_str}-{sequence:04d}"

    async def validate_invoice_totals(
        self, session: AsyncSession, invoice_id: int
    ) -> bool:
        """Validate invoice line items match totals.

        Args:
            session: Database session
            invoice_id: ID of invoice to validate

        Returns:
            bool: True if totals match, raises ValueError if not

        Raises:
            ValueError: If calculations don't match
        """
        invoice = await session.get(Invoice, invoice_id)
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found")

        # Get line items
        result = await session.execute(
            select(LineItem).where(LineItem.invoice_id == invoice_id)
        )
        line_items = result.scalars().all()

        # Calculate totals from line items
        calculated_subtotal = sum(item.line_total for item in line_items)
        calculated_tax = (calculated_subtotal * Decimal("0.10")).quantize(
            Decimal("0.01")
        )
        calculated_total = (calculated_subtotal + calculated_tax).quantize(
            Decimal("0.01")
        )

        # Validate
        if calculated_subtotal != invoice.subtotal:
            raise ValueError(
                f"Subtotal mismatch: expected {calculated_subtotal}, "
                f"got {invoice.subtotal}"
            )
        if calculated_tax != invoice.tax_amount:
            raise ValueError(
                f"Tax mismatch: expected {calculated_tax}, " f"got {invoice.tax_amount}"
            )
        if calculated_total != invoice.total_amount:
            raise ValueError(
                f"Total mismatch: expected {calculated_total}, "
                f"got {invoice.total_amount}"
            )

        return True

    async def get_invoice_detail(
        self, session: AsyncSession, invoice_id: int
    ) -> Invoice:
        """Get invoice with related line items.

        Args:
            session: Database session
            invoice_id: ID of invoice to retrieve

        Returns:
            Invoice: Invoice object with line items

        Raises:
            ValueError: If invoice not found
        """
        invoice = await session.get(Invoice, invoice_id)
        if not invoice:
            raise ValueError(f"Invoice with ID {invoice_id} not found")

        # Eager load line items
        result = await session.execute(
            select(LineItem).where(LineItem.invoice_id == invoice_id)
        )
        invoice.line_items = result.scalars().all()

        return invoice

    async def list_invoices(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        client_id: int | None = None,
        project_id: int | None = None,
        status: str | None = None,
        start_date=None,
        end_date=None,
    ) -> tuple[list[Invoice], int]:
        """List invoices with optional filtering.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Number of records to return
            client_id: Filter by client
            project_id: Filter by project
            status: Filter by status (draft, sent, paid, overdue)
            start_date: Filter by invoice date (start)
            end_date: Filter by invoice date (end)

        Returns:
            Tuple of (invoices, total_count)
        """
        query = select(Invoice)

        # Apply filters
        filters = []
        if client_id:
            filters.append(Invoice.client_id == client_id)
        if project_id:
            filters.append(Invoice.project_id == project_id)
        if status:
            filters.append(Invoice.status == status)
        if start_date:
            filters.append(Invoice.invoice_date >= start_date)
        if end_date:
            filters.append(Invoice.invoice_date <= end_date)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_result = await session.execute(
            select(Invoice).where(and_(*filters) if filters else True)
        )
        total = len(count_result.scalars().all())

        # Get paginated results
        query = query.order_by(Invoice.invoice_date.desc()).offset(skip).limit(limit)
        result = await session.execute(query)
        invoices = result.scalars().all()

        return invoices, total

    def calculate_days_overdue(self, invoice) -> int:
        """Calculate days overdue for an invoice.

        Args:
            invoice: Invoice object

        Returns:
            int: Number of days overdue (0 if not overdue, negative if not yet due)
        """
        if invoice.payment_date:
            return 0  # Already paid

        if not invoice.due_date:
            return 0  # No due date set

        today = datetime.now(timezone.utc).date()
        days_overdue = (today - invoice.due_date).days

        return max(0, days_overdue)  # Return 0 if not overdue
