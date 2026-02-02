"""
Tests for reports router.

Comprehensive HTTP integration tests for revenue, utilization, and overdue invoice reports.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import SOW, Client, Invoice, Project, Timesheet, User


class TestReportsRouter:
    """Test suite for reports API endpoints."""

    def test_revenue_report_empty(self, client: TestClient, auth_headers: dict):
        """Test revenue report with no paid invoices."""
        response = client.get("/api/v1/reports/revenue", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "breakdown" in data
        assert data["summary"]["total_revenue"] == 0.0
        assert data["summary"]["total_invoices"] == 0
        assert len(data["breakdown"]) == 0

    def test_revenue_report_unauthorized(self, client: TestClient):
        """Test revenue report requires authentication."""
        response = client.get("/api/v1/reports/revenue")
        assert response.status_code == 401

    def test_revenue_report_date_validation(
        self, client: TestClient, auth_headers: dict
    ):
        """Test revenue report validates date range."""
        response = client.get(
            "/api/v1/reports/revenue",
            params={
                "start_date": "2024-12-31",
                "end_date": "2024-01-01",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422
        assert "start_date must be before" in response.json()["detail"]

    def test_utilization_report_empty(self, client: TestClient, auth_headers: dict):
        """Test utilization report with no approved timesheets."""
        response = client.get("/api/v1/reports/utilization", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "breakdown" in data
        assert data["summary"]["total_hours"] == 0.0
        assert data["summary"]["overall_utilization_rate"] == 0.0
        assert len(data["breakdown"]) == 0

    def test_utilization_report_unauthorized(self, client: TestClient):
        """Test utilization report requires authentication."""
        response = client.get("/api/v1/reports/utilization")
        assert response.status_code == 401

    def test_utilization_report_date_validation(
        self, client: TestClient, auth_headers: dict
    ):
        """Test utilization report validates date range."""
        response = client.get(
            "/api/v1/reports/utilization",
            params={
                "start_date": "2024-12-31",
                "end_date": "2024-01-01",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422
        assert "start_date must be before" in response.json()["detail"]

    def test_overdue_invoices_empty(self, client: TestClient, auth_headers: dict):
        """Test overdue invoices report with no overdue invoices."""
        response = client.get("/api/v1/reports/overdue-invoices", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "invoices" in data
        assert data["summary"]["total_overdue_amount"] == 0.0
        assert data["summary"]["invoice_count"] == 0
        assert len(data["invoices"]) == 0

    def test_overdue_invoices_unauthorized(self, client: TestClient):
        """Test overdue invoices report requires authentication."""
        response = client.get("/api/v1/reports/overdue-invoices")
        assert response.status_code == 401

    def test_overdue_invoices_days_filter(self, client: TestClient, auth_headers: dict):
        """Test overdue invoices with days filter."""
        response = client.get(
            "/api/v1/reports/overdue-invoices",
            params={"days_overdue": 30},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "invoices" in data

    def test_all_report_endpoints_exist(self, client: TestClient, auth_headers: dict):
        """Test that all report endpoints are registered and accessible."""
        endpoints = [
            "/api/v1/reports/revenue",
            "/api/v1/reports/utilization",
            "/api/v1/reports/overdue-invoices",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint, headers=auth_headers)
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404, f"Endpoint {endpoint} not found"
            # Should be 200 (success) for empty reports
            assert response.status_code == 200, f"Endpoint {endpoint} failed"

    def test_revenue_report_with_filters(self, client: TestClient, auth_headers: dict):
        """Test revenue report with date and client filters."""
        today = date.today()
        start = today - timedelta(days=30)
        end = today

        response = client.get(
            "/api/v1/reports/revenue",
            params={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "client_id": 1,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period"]["start_date"] == start.isoformat()
        assert data["period"]["end_date"] == end.isoformat()

    def test_utilization_report_with_filters(
        self, client: TestClient, auth_headers: dict
    ):
        """Test utilization report with date and consultant filters."""
        today = date.today()
        start = today - timedelta(days=30)
        end = today

        response = client.get(
            "/api/v1/reports/utilization",
            params={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "consultant_id": 1,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period"]["start_date"] == start.isoformat()
        assert data["period"]["end_date"] == end.isoformat()

    def test_report_response_structure(self, client: TestClient, auth_headers: dict):
        """Test that all reports return proper structure."""
        # Revenue report structure
        response = client.get("/api/v1/reports/revenue", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "summary" in data
        assert "breakdown" in data
        assert "total_revenue" in data["summary"]
        assert "total_invoices" in data["summary"]

        # Utilization report structure
        response = client.get("/api/v1/reports/utilization", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "summary" in data
        assert "breakdown" in data
        assert "total_hours" in data["summary"]
        assert "overall_utilization_rate" in data["summary"]

        # Overdue invoices structure
        response = client.get("/api/v1/reports/overdue-invoices", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "as_of_date" in data
        assert "summary" in data
        assert "invoices" in data
        assert "total_overdue_amount" in data["summary"]
        assert "invoice_count" in data["summary"]
