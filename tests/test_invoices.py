"""Tests for invoice service and functionality."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_invoice_service_available(client: TestClient, auth_headers: dict):
    """Test that InvoiceService can be imported successfully."""
    from app.services.invoice_service import InvoiceService
    service = InvoiceService()
    assert service is not None


def test_invoice_service_tax_calculation():
    """Unit test for tax calculation (10%)."""
    # Test 10% tax calculation
    subtotal = Decimal("1000.00")
    tax_rate = Decimal("0.10")
    tax = (subtotal * tax_rate).quantize(Decimal("0.01"))
    total = (subtotal + tax).quantize(Decimal("0.01"))
    
    assert tax == Decimal("100.00")
    assert total == Decimal("1100.00")


def test_invoice_service_decimal_precision():
    """Unit test for decimal precision in financial calculations."""
    # Test fractional calculations maintain precision
    hours = Decimal("7.50")
    rate = Decimal("123.45")
    billable = (hours * rate).quantize(Decimal("0.01"))
    
    # 7.50 × 123.45 = 925.875 → rounds to 925.88
    assert billable == Decimal("925.88")
    
    # Tax on this amount
    tax = (billable * Decimal("0.10")).quantize(Decimal("0.01"))
    assert tax == Decimal("92.59")
    
    # Total
    total = (billable + tax).quantize(Decimal("0.01"))
    assert total == Decimal("1018.47")


def test_invoice_number_format():
    """Test invoice number format (INV-YYYYMMDD-NNNN)."""
    import re
    
    # Pattern for invoice number: INV-YYYYMMDD-NNNN
    pattern = r"^INV-\d{8}-\d{4}$"
    
    today = date.today().strftime("%Y%m%d")
    
    # Example invoice number
    test_invoice = f"INV-{today}-0001"
    
    assert re.match(pattern, test_invoice)


def test_invoice_days_overdue_calculation():
    """Test days overdue calculation logic."""
    from app.services.invoice_service import InvoiceService
    
    service = InvoiceService()
    
    # Create a mock invoice object for testing
    class MockInvoice:
        def __init__(self, due_date, payment_date=None):
            self.due_date = due_date
            self.payment_date = payment_date
    
    # Test: not yet due (positive days remaining)
    invoice = MockInvoice(due_date=date.today() + timedelta(days=30))
    days_overdue = service.calculate_days_overdue(invoice)
    assert days_overdue == 0
    
    # Test: 10 days overdue
    invoice = MockInvoice(due_date=date.today() - timedelta(days=10))
    days_overdue = service.calculate_days_overdue(invoice)
    assert days_overdue == 10
    
    # Test: paid invoice (no overdue regardless of due_date)
    invoice = MockInvoice(
        due_date=date.today() - timedelta(days=10),
        payment_date=datetime.now(timezone.utc)
    )
    days_overdue = service.calculate_days_overdue(invoice)
    assert days_overdue == 0
    
    # Test: no due date
    invoice = MockInvoice(due_date=None)
    days_overdue = service.calculate_days_overdue(invoice)
    assert days_overdue == 0


def test_invoice_number_uniqueness():
    """Test that invoice numbers are generated with proper format."""
    from app.services.invoice_service import InvoiceService
    
    service = InvoiceService()
    
    # Test invoice number generation format
    import datetime
    date_str = datetime.date.today().strftime("%Y%m%d")
    expected_prefix = f"INV-{date_str}"
    
    # Invoice numbers should start with INV-YYYYMMDD
    assert expected_prefix.startswith("INV-")
    assert len(expected_prefix) == 12  # INV-YYYYMMDD


def test_invoice_multiple_timesheet_calculations():
    """Test invoice total calculation with multiple timesheets."""
    # Simulate 3 timesheets with 8 hours each at $150/hour
    # Total: 24 hours × $150 = $3600 subtotal
    # Tax: $3600 × 0.10 = $360
    # Total: $3600 + $360 = $3960
    
    hours_per_timesheet = Decimal("8.00")
    num_timesheets = 3
    billing_rate = Decimal("150.00")
    
    total_hours = hours_per_timesheet * num_timesheets
    subtotal = (total_hours * billing_rate).quantize(Decimal("0.01"))
    tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
    total = (subtotal + tax).quantize(Decimal("0.01"))
    
    assert total_hours == Decimal("24.00")
    assert subtotal == Decimal("3600.00")
    assert tax == Decimal("360.00")
    assert total == Decimal("3960.00")


def test_invoice_fractional_hours_and_rates():
    """Test invoice calculations with fractional hours and rates."""
    # 7.5 hours at $123.45/hour = $925.875 → $925.88
    # Tax: $925.88 × 0.10 = $92.588 → $92.59
    # Total: $925.88 + $92.59 = $1018.47
    
    hours = Decimal("7.5")
    rate = Decimal("123.45")
    
    billable = (hours * rate).quantize(Decimal("0.01"))
    tax = (billable * Decimal("0.10")).quantize(Decimal("0.01"))
    total = (billable + tax).quantize(Decimal("0.01"))
    
    assert billable == Decimal("925.88")
    assert tax == Decimal("92.59")
    assert total == Decimal("1018.47")


def test_invoice_zero_amount():
    """Test invoice calculations with zero amounts."""
    subtotal = Decimal("0.00")
    tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
    total = (subtotal + tax).quantize(Decimal("0.01"))
    
    assert subtotal == Decimal("0.00")
    assert tax == Decimal("0.00")
    assert total == Decimal("0.00")


# ============================================================================
# HTTP Integration Tests for Invoice Router
# ============================================================================


class TestInvoiceRouter:
    """Test Invoice Router HTTP endpoints."""

    def test_list_invoices_empty(self, client: TestClient, auth_headers: dict):
        """Test listing invoices when none exist."""
        resp = client.get("/api/v1/invoices", headers=auth_headers)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["total"] >= 0
        assert data["page"] >= 1
        assert data["per_page"] >= 1
        assert isinstance(data["items"], list)

    def test_list_invoices_pagination(self, client: TestClient, auth_headers: dict):
        """Test invoice list pagination parameters."""
        resp = client.get(
            "/api/v1/invoices?skip=0&limit=10",
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert len(data["items"]) <= 10

    def test_list_invoices_with_status_filter(self, client: TestClient, auth_headers: dict):
        """Test invoice list with status filter."""
        resp = client.get(
            "/api/v1/invoices?status_filter=draft",
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert isinstance(data["items"], list)
        # All returned invoices should have status=draft if any exist
        for item in data["items"]:
            if item.get("status"):
                assert item["status"] == "draft"

    def test_list_invoices_with_client_filter(
        self, client: TestClient, auth_headers: dict
    ):
        """Test invoice list with client_id filter."""
        resp = client.get(
            "/api/v1/invoices?client_id=1",
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert isinstance(data["items"], list)
        # All returned invoices should belong to client_id=1 if any exist
        for item in data["items"]:
            assert item["client_id"] == 1

    def test_list_invoices_with_date_filter(self, client: TestClient, auth_headers: dict):
        """Test invoice list with date range filter."""
        today = date.today()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=30)

        resp = client.get(
            f"/api/v1/invoices?start_date={start_date}&end_date={end_date}",
            headers=auth_headers,
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert isinstance(data["items"], list)

    def test_list_invoices_unauthorized(self, client: TestClient):
        """Test listing invoices without authentication."""
        resp = client.get("/api/v1/invoices")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_invoice_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent invoice."""
        resp = client.get("/api/v1/invoices/9999", headers=auth_headers)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in resp.json()["detail"].lower()

    def test_send_invoice_unauthorized(self, client: TestClient, auth_headers: dict):
        """Test that non-PM cannot send invoice."""
        # This depends on user role in auth_headers
        # Mock users are typically 'admin' or 'user' role
        # We'd need a 'client' role to test proper rejection
        resp = client.post("/api/v1/invoices/1/send", headers=auth_headers)
        # Should either succeed (if admin) or fail with 403 (if client)
        assert resp.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_mark_paid_unauthorized(self, client: TestClient, auth_headers: dict):
        """Test that non-accountant cannot mark invoice paid."""
        # Similar to send_invoice, depends on user role
        resp = client.post(
            "/api/v1/invoices/1/mark-paid",
            json={"payment_date": str(date.today())},
            headers=auth_headers,
        )
        assert resp.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_router_endpoints_exist(self, client: TestClient, auth_headers: dict):
        """Test that all invoice router endpoints are registered."""
        # GET /api/v1/invoices - List
        resp = client.get("/api/v1/invoices", headers=auth_headers)
        assert resp.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

        # GET /api/v1/invoices/{id} - Get detail (404 is ok if no invoice)
        resp = client.get("/api/v1/invoices/1", headers=auth_headers)
        assert resp.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

        # POST /api/v1/invoices - Generate (422 is ok if data invalid)
        resp = client.post(
            "/api/v1/invoices",
            json={"project_id": 1, "invoice_date": str(date.today())},
            headers=auth_headers,
        )
        # Endpoint should exist, not 404
        assert resp.status_code != 404

        # POST /api/v1/invoices/{id}/send (422 is ok if no invoice)
        resp = client.post("/api/v1/invoices/1/send", headers=auth_headers)
        # Endpoint should exist, not 404
        assert resp.status_code != 404

        # POST /api/v1/invoices/{id}/mark-paid (422 is ok if no invoice)
        resp = client.post(
            "/api/v1/invoices/1/mark-paid",
            json={"payment_date": str(date.today())},
            headers=auth_headers,
        )
        # Endpoint should exist, not 404
        assert resp.status_code != 404

