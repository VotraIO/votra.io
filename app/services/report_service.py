"""
Report and analytics service for generating business insights.

Provides aggregated data for revenue tracking, consultant utilization,
and overdue invoice management.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Client, Invoice, Project, Timesheet, User


class ReportService:
    """Service for generating business reports and analytics."""

    @staticmethod
    async def get_revenue_report(
        db: AsyncSession,
        start_date: date | None = None,
        end_date: date | None = None,
        client_id: int | None = None,
        group_by: str = "month",
    ) -> dict[str, Any]:
        """
        Generate revenue report with optional filtering.

        Args:
            db: Database session
            start_date: Optional start date filter
            end_date: Optional end date filter
            client_id: Optional client filter
            group_by: Grouping period ("day", "week", "month", "year", "client")

        Returns:
            Dictionary with revenue breakdown and totals
        """
        # Build base query
        query = select(
            Invoice.client_id,
            Client.name.label("client_name"),
            func.count(Invoice.id).label("invoice_count"),
            func.sum(Invoice.total_amount).label("total_revenue"),
            func.sum(Invoice.tax_amount).label("total_tax"),
            func.sum(Invoice.subtotal).label("total_subtotal"),
        ).join(Client, Invoice.client_id == Client.id)

        # Apply filters
        filters = []
        if start_date:
            filters.append(Invoice.invoice_date >= start_date)
        if end_date:
            filters.append(Invoice.invoice_date <= end_date)
        if client_id:
            filters.append(Invoice.client_id == client_id)

        # Only include paid invoices for revenue reporting
        filters.append(Invoice.status == "paid")

        if filters:
            query = query.where(and_(*filters))

        # Group by client
        query = query.group_by(Invoice.client_id, Client.name).order_by(
            func.sum(Invoice.total_amount).desc()
        )

        result = await db.execute(query)
        revenue_data = result.all()

        # Calculate totals
        total_revenue = sum(
            row.total_revenue for row in revenue_data if row.total_revenue
        )
        total_invoices = sum(row.invoice_count for row in revenue_data)
        total_tax = sum(row.total_tax for row in revenue_data if row.total_tax)

        # Format response
        breakdown = [
            {
                "client_id": row.client_id,
                "client_name": row.client_name,
                "invoice_count": row.invoice_count,
                "total_revenue": float(row.total_revenue) if row.total_revenue else 0.0,
                "total_tax": float(row.total_tax) if row.total_tax else 0.0,
                "total_subtotal": (
                    float(row.total_subtotal) if row.total_subtotal else 0.0
                ),
            }
            for row in revenue_data
        ]

        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            "summary": {
                "total_revenue": float(total_revenue) if total_revenue else 0.0,
                "total_invoices": total_invoices,
                "total_tax": float(total_tax) if total_tax else 0.0,
                "average_invoice_value": (
                    float(total_revenue / total_invoices) if total_invoices > 0 else 0.0
                ),
            },
            "breakdown": breakdown,
        }

    @staticmethod
    async def get_utilization_report(
        db: AsyncSession,
        start_date: date | None = None,
        end_date: date | None = None,
        consultant_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate consultant utilization report.

        Calculates billable vs non-billable hours for consultants.

        Args:
            db: Database session
            start_date: Optional start date filter
            end_date: Optional end date filter
            consultant_id: Optional consultant filter

        Returns:
            Dictionary with utilization metrics by consultant
        """
        # Build query
        query = (
            select(
                Timesheet.consultant_id,
                User.full_name.label("consultant_name"),
                func.sum(Timesheet.hours_logged).label("total_hours"),
                func.sum(
                    case(
                        (Timesheet.is_billable == True, Timesheet.hours_logged), else_=0
                    )
                ).label("billable_hours"),
                func.sum(
                    case(
                        (Timesheet.is_billable == False, Timesheet.hours_logged),
                        else_=0,
                    )
                ).label("non_billable_hours"),
                func.sum(Timesheet.billable_amount).label("total_revenue"),
                func.count(Timesheet.id).label("timesheet_count"),
            )
            .join(User, Timesheet.consultant_id == User.id)
            .where(Timesheet.status == "approved")
        )

        # Apply filters
        filters = []
        if start_date:
            filters.append(Timesheet.work_date >= start_date)
        if end_date:
            filters.append(Timesheet.work_date <= end_date)
        if consultant_id:
            filters.append(Timesheet.consultant_id == consultant_id)

        if filters:
            query = query.where(and_(*filters))

        query = query.group_by(Timesheet.consultant_id, User.full_name).order_by(
            func.sum(Timesheet.hours_logged).desc()
        )

        result = await db.execute(query)
        utilization_data = result.all()

        # Calculate aggregated totals
        total_hours = sum(
            row.total_hours for row in utilization_data if row.total_hours
        )
        total_billable = sum(
            row.billable_hours for row in utilization_data if row.billable_hours
        )
        total_revenue = sum(
            row.total_revenue for row in utilization_data if row.total_revenue
        )

        # Format response
        breakdown = []
        for row in utilization_data:
            total_h = float(row.total_hours) if row.total_hours else 0.0
            billable_h = float(row.billable_hours) if row.billable_hours else 0.0
            utilization_rate = (billable_h / total_h * 100) if total_h > 0 else 0.0

            breakdown.append(
                {
                    "consultant_id": row.consultant_id,
                    "consultant_name": row.consultant_name,
                    "total_hours": total_h,
                    "billable_hours": billable_h,
                    "non_billable_hours": (
                        float(row.non_billable_hours) if row.non_billable_hours else 0.0
                    ),
                    "utilization_rate": round(utilization_rate, 2),
                    "total_revenue": (
                        float(row.total_revenue) if row.total_revenue else 0.0
                    ),
                    "timesheet_count": row.timesheet_count,
                }
            )

        overall_utilization = (
            (total_billable / total_hours * 100) if total_hours > 0 else 0.0
        )

        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            "summary": {
                "total_hours": float(total_hours) if total_hours else 0.0,
                "total_billable_hours": (
                    float(total_billable) if total_billable else 0.0
                ),
                "overall_utilization_rate": round(overall_utilization, 2),
                "total_revenue": float(total_revenue) if total_revenue else 0.0,
                "consultant_count": len(breakdown),
            },
            "breakdown": breakdown,
        }

    @staticmethod
    async def get_overdue_invoices(
        db: AsyncSession, days_overdue: int = 0
    ) -> dict[str, Any]:
        """
        Get overdue invoices report.

        Identifies invoices past their due date that haven't been paid.

        Args:
            db: Database session
            days_overdue: Minimum days overdue (default 0 = all overdue)

        Returns:
            Dictionary with overdue invoice details and summary
        """
        today = date.today()
        cutoff_date = today - timedelta(days=days_overdue)

        # Query for overdue invoices
        query = (
            select(
                Invoice.id,
                Invoice.invoice_number,
                Invoice.invoice_date,
                Invoice.due_date,
                Invoice.total_amount,
                Invoice.status,
                Invoice.client_id,
                Client.name.label("client_name"),
                Client.email.label("client_email"),
                Project.name.label("project_name"),
            )
            .join(Client, Invoice.client_id == Client.id)
            .outerjoin(Project, Invoice.project_id == Project.id)
            .where(
                and_(
                    Invoice.status.in_(["sent", "overdue"]),
                    Invoice.due_date < today,
                    Invoice.due_date <= cutoff_date,
                )
            )
            .order_by(Invoice.due_date.asc())
        )

        result = await db.execute(query)
        overdue_invoices = result.all()

        # Calculate metrics
        total_overdue_amount = sum(
            inv.total_amount for inv in overdue_invoices if inv.total_amount
        )
        invoice_count = len(overdue_invoices)

        # Format breakdown
        breakdown = []
        for inv in overdue_invoices:
            days_past_due = (today - inv.due_date).days if inv.due_date else 0

            breakdown.append(
                {
                    "invoice_id": inv.id,
                    "invoice_number": inv.invoice_number,
                    "client_id": inv.client_id,
                    "client_name": inv.client_name,
                    "client_email": inv.client_email,
                    "project_name": inv.project_name,
                    "invoice_date": (
                        inv.invoice_date.isoformat() if inv.invoice_date else None
                    ),
                    "due_date": inv.due_date.isoformat() if inv.due_date else None,
                    "days_overdue": days_past_due,
                    "amount": float(inv.total_amount) if inv.total_amount else 0.0,
                    "status": inv.status,
                }
            )

        return {
            "as_of_date": today.isoformat(),
            "summary": {
                "total_overdue_amount": (
                    float(total_overdue_amount) if total_overdue_amount else 0.0
                ),
                "invoice_count": invoice_count,
                "average_days_overdue": (
                    round(
                        sum(inv["days_overdue"] for inv in breakdown) / invoice_count, 1
                    )
                    if invoice_count > 0
                    else 0.0
                ),
            },
            "invoices": breakdown,
        }
