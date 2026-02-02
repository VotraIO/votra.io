"""Tests for project management endpoints and service."""

import pytest
from fastapi.testclient import TestClient


class TestProjectCreation:
    """Test cases for project creation from SOWs."""

    def test_create_project_success(self, client: TestClient, auth_headers: dict):
        """Test successful project creation from approved SOW."""
        # First, create a client
        client_response = client.post(
            "/api/v1/clients",
            json={
                "name": "Test Client",
                "email": "test@example.com",
                "company": "Test Corp",
                "phone": "555-1234",
            },
            headers=auth_headers,
        )
        assert client_response.status_code == 201
        client_id = client_response.json()["id"]

        # Create a SOW
        sow_response = client.post(
            "/api/v1/sows",
            json={
                "client_id": client_id,
                "title": "Test SOW",
                "description": "Test Description",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "rate": 150,
                "total_budget": 100000,
            },
            headers=auth_headers,
        )
        assert sow_response.status_code == 201
        sow_id = sow_response.json()["id"]

        # Submit SOW
        submit_response = client.post(
            f"/api/v1/sows/{sow_id}/submit",
            headers=auth_headers,
        )
        assert submit_response.status_code == 200

        # Approve SOW
        approve_response = client.post(
            f"/api/v1/sows/{sow_id}/approve",
            json={"approved": True},
            headers=auth_headers,
        )
        assert approve_response.status_code == 200

        # Now create project from approved SOW
        project_response = client.post(
            "/api/v1/projects",
            json={"sow_id": sow_id},
            headers=auth_headers,
        )
        assert project_response.status_code == 201
        project = project_response.json()
        assert project["name"] == "Test SOW"
        assert project["status"] == "in_progress"
        assert project["sow_id"] == sow_id
        assert project["budget"] == "100000.00"

    def test_create_project_requires_approval(self, client: TestClient, auth_headers: dict):
        """Test that project creation fails if SOW is not approved."""
        # Create client
        client_response = client.post(
            "/api/v1/clients",
            json={
                "name": "Test Client",
                "email": "test2@example.com",
                "company": "Test Corp",
            },
            headers=auth_headers,
        )
        client_id = client_response.json()["id"]

        # Create SOW (will be in draft status)
        sow_response = client.post(
            "/api/v1/sows",
            json={
                "client_id": client_id,
                "title": "Unapproved SOW",
                "description": "Test",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "rate": 150,
                "total_budget": 50000,
            },
            headers=auth_headers,
        )
        sow_id = sow_response.json()["id"]

        # Try to create project without approving SOW
        project_response = client.post(
            "/api/v1/projects",
            json={"sow_id": sow_id},
            headers=auth_headers,
        )
        assert project_response.status_code == 422
        assert "approved" in project_response.json()["detail"].lower()

    def test_create_project_invalid_sow(self, client: TestClient, auth_headers: dict):
        """Test project creation fails with invalid SOW ID."""
        project_response = client.post(
            "/api/v1/projects",
            json={"sow_id": 99999},
            headers=auth_headers,
        )
        assert project_response.status_code == 422
        assert "not found" in project_response.json()["detail"].lower()

    def test_create_project_duplicate_not_allowed(self, client: TestClient, auth_headers: dict):
        """Test that cannot create multiple projects from same SOW."""
        # Create and approve SOW
        client_response = client.post(
            "/api/v1/clients",
            json={
                "name": "Test Client",
                "email": "test3@example.com",
                "company": "Test Corp",
            },
            headers=auth_headers,
        )
        client_id = client_response.json()["id"]

        sow_response = client.post(
            "/api/v1/sows",
            json={
                "client_id": client_id,
                "title": "SOW",
                "description": "Test",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "rate": 150,
                "total_budget": 75000,
            },
            headers=auth_headers,
        )
        sow_id = sow_response.json()["id"]

        # Submit and approve
        client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)
        client.post(
            f"/api/v1/sows/{sow_id}/approve",
            json={"approved": True},
            headers=auth_headers,
        )

        # Create first project
        project1 = client.post(
            "/api/v1/projects",
            json={"sow_id": sow_id},
            headers=auth_headers,
        )
        assert project1.status_code == 201

        # Try to create second project from same SOW
        project2 = client.post(
            "/api/v1/projects",
            json={"sow_id": sow_id},
            headers=auth_headers,
        )
        assert project2.status_code == 422
        assert "already exists" in project2.json()["detail"].lower()

    def test_create_project_requires_admin_or_pm(self, client: TestClient):
        """Test that only admin/PM can create projects."""
        # Get user token (default is non-PM user)
        from app.utils.security import create_access_token
        from datetime import timedelta

        token = create_access_token(
            data={
                "sub": "consultant",
                "role": "consultant",
                "email": "consultant@example.com",
                "user_id": 2,
            },
            expires_delta=timedelta(minutes=30),
        )
        consultant_headers = {"Authorization": f"Bearer {token}"}

        project_response = client.post(
            "/api/v1/projects",
            json={"sow_id": 1},
            headers=consultant_headers,
        )
        assert project_response.status_code == 403


class TestProjectListing:
    """Test cases for project listing."""

    def test_list_projects_empty(self, client: TestClient, auth_headers: dict):
        """Test listing projects when none exist."""
        response = client.get("/api/v1/projects", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_projects_with_pagination(self, client: TestClient, auth_headers: dict):
        """Test project list pagination."""
        response = client.get(
            "/api/v1/projects?skip=0&limit=10",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "skip" in data
        assert "limit" in data
        assert "total" in data
        assert "items" in data

    def test_list_projects_with_status_filter(self, client: TestClient, auth_headers: dict):
        """Test filtering projects by status."""
        response = client.get(
            "/api/v1/projects?status=in_progress",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        # All items should have in_progress status (or be empty)
        for item in data["items"]:
            assert item["status"] == "in_progress"


class TestProjectDetail:
    """Test cases for project detail retrieval."""

    def test_get_project_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent project."""
        response = client.get("/api/v1/projects/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_project_success(self, client: TestClient, auth_headers: dict):
        """Test getting existing project."""
        # First create a project
        client_response = client.post(
            "/api/v1/clients",
            json={
                "name": "Test Client",
                "email": "detail@example.com",
                "company": "Test",
            },
            headers=auth_headers,
        )
        client_id = client_response.json()["id"]

        sow_response = client.post(
            "/api/v1/sows",
            json={
                "client_id": client_id,
                "title": "Detail Test",
                "description": "Test",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "rate": 150,
                "total_budget": 100000,
            },
            headers=auth_headers,
        )
        sow_id = sow_response.json()["id"]

        client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)
        client.post(
            f"/api/v1/sows/{sow_id}/approve",
            json={"approved": True},
            headers=auth_headers,
        )

        project_response = client.post(
            "/api/v1/projects",
            json={"sow_id": sow_id},
            headers=auth_headers,
        )
        project_id = project_response.json()["id"]

        # Get the project
        get_response = client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200
        project = get_response.json()
        assert project["id"] == project_id
        assert project["name"] == "Detail Test"


class TestProjectUpdate:
    """Test cases for project updates."""

    def test_update_project_description(self, client: TestClient, auth_headers: dict):
        """Test updating project description."""
        # Create project first
        client_response = client.post(
            "/api/v1/clients",
            json={
                "name": "Test",
                "email": "update@example.com",
                "company": "Test",
            },
            headers=auth_headers,
        )
        client_id = client_response.json()["id"]

        sow_response = client.post(
            "/api/v1/sows",
            json={
                "client_id": client_id,
                "title": "Update Test",
                "description": "Original",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "rate": 150,
                "total_budget": 50000,
            },
            headers=auth_headers,
        )
        sow_id = sow_response.json()["id"]

        client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)
        client.post(
            f"/api/v1/sows/{sow_id}/approve",
            json={"approved": True},
            headers=auth_headers,
        )

        project_response = client.post(
            "/api/v1/projects",
            json={"sow_id": sow_id},
            headers=auth_headers,
        )
        project_id = project_response.json()["id"]

        # Update description
        update_response = client.put(
            f"/api/v1/projects/{project_id}",
            json={"description": "Updated description"},
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        assert update_response.json()["description"] == "Updated description"

    def test_update_closed_project_fails(self, client: TestClient, auth_headers: dict):
        """Test that updating closed project fails."""
        # Create and close project
        client_response = client.post(
            "/api/v1/clients",
            json={
                "name": "Test",
                "email": "closed@example.com",
                "company": "Test",
            },
            headers=auth_headers,
        )
        client_id = client_response.json()["id"]

        sow_response = client.post(
            "/api/v1/sows",
            json={
                "client_id": client_id,
                "title": "Closed Test",
                "description": "Test",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "rate": 150,
                "total_budget": 60000,
            },
            headers=auth_headers,
        )
        sow_id = sow_response.json()["id"]

        client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)
        client.post(
            f"/api/v1/sows/{sow_id}/approve",
            json={"approved": True},
            headers=auth_headers,
        )

        project_response = client.post(
            "/api/v1/projects",
            json={"sow_id": sow_id},
            headers=auth_headers,
        )
        project_id = project_response.json()["id"]

        # Close project
        client.post(
            f"/api/v1/projects/{project_id}/close",
            json={"notes": "Closing project"},
            headers=auth_headers,
        )

        # Try to update closed project
        update_response = client.put(
            f"/api/v1/projects/{project_id}",
            json={"description": "Cannot update"},
            headers=auth_headers,
        )
        assert update_response.status_code == 422


class TestProjectClosure:
    """Test cases for project closure."""

    def test_close_project_success(self, client: TestClient, auth_headers: dict):
        """Test successful project closure."""
        # Create project first
        client_response = client.post(
            "/api/v1/clients",
            json={
                "name": "Test",
                "email": "close@example.com",
                "company": "Test",
            },
            headers=auth_headers,
        )
        client_id = client_response.json()["id"]

        sow_response = client.post(
            "/api/v1/sows",
            json={
                "client_id": client_id,
                "title": "Close Test",
                "description": "Test",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "rate": 150,
                "total_budget": 70000,
            },
            headers=auth_headers,
        )
        sow_id = sow_response.json()["id"]

        client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)
        client.post(
            f"/api/v1/sows/{sow_id}/approve",
            json={"approved": True},
            headers=auth_headers,
        )

        project_response = client.post(
            "/api/v1/projects",
            json={"sow_id": sow_id},
            headers=auth_headers,
        )
        project_id = project_response.json()["id"]

        # Close project
        close_response = client.post(
            f"/api/v1/projects/{project_id}/close",
            json={"notes": "Project completed"},
            headers=auth_headers,
        )
        assert close_response.status_code == 200
        assert close_response.json()["status"] == "closed"

    def test_close_already_closed_project_fails(self, client: TestClient, auth_headers: dict):
        """Test that closing already closed project fails."""
        # Create and close project
        client_response = client.post(
            "/api/v1/clients",
            json={
                "name": "Test",
                "email": "already_closed@example.com",
                "company": "Test",
            },
            headers=auth_headers,
        )
        client_id = client_response.json()["id"]

        sow_response = client.post(
            "/api/v1/sows",
            json={
                "client_id": client_id,
                "title": "Already Closed",
                "description": "Test",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "rate": 150,
                "total_budget": 80000,
            },
            headers=auth_headers,
        )
        sow_id = sow_response.json()["id"]

        client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)
        client.post(
            f"/api/v1/sows/{sow_id}/approve",
            json={"approved": True},
            headers=auth_headers,
        )

        project_response = client.post(
            "/api/v1/projects",
            json={"sow_id": sow_id},
            headers=auth_headers,
        )
        project_id = project_response.json()["id"]

        # Close first time
        client.post(
            f"/api/v1/projects/{project_id}/close",
            json={"notes": "First close"},
            headers=auth_headers,
        )

        # Try to close again
        close_response = client.post(
            f"/api/v1/projects/{project_id}/close",
            json={"notes": "Second close"},
            headers=auth_headers,
        )
        assert close_response.status_code == 422
        assert "already closed" in close_response.json()["detail"].lower()

    def test_close_project_requires_admin(self, client: TestClient, auth_headers: dict):
        """Test that only admin can close projects."""
        from app.utils.security import create_access_token
        from datetime import timedelta

        # Create project as admin/PM
        client_response = client.post(
            "/api/v1/clients",
            json={
                "name": "Test",
                "email": "admin_close@example.com",
                "company": "Test",
            },
            headers=auth_headers,
        )
        client_id = client_response.json()["id"]

        sow_response = client.post(
            "/api/v1/sows",
            json={
                "client_id": client_id,
                "title": "Admin Close",
                "description": "Test",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "rate": 150,
                "total_budget": 90000,
            },
            headers=auth_headers,
        )
        sow_id = sow_response.json()["id"]

        client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)
        client.post(
            f"/api/v1/sows/{sow_id}/approve",
            json={"approved": True},
            headers=auth_headers,
        )

        project_response = client.post(
            "/api/v1/projects",
            json={"sow_id": sow_id},
            headers=auth_headers,
        )
        project_id = project_response.json()["id"]

        # Try to close as PM (should fail)
        pm_token = create_access_token(
            data={
                "sub": "pm",
                "role": "project_manager",
                "email": "pm@example.com",
                "user_id": 3,
            },
            expires_delta=timedelta(minutes=30),
        )
        pm_headers = {"Authorization": f"Bearer {pm_token}"}

        close_response = client.post(
            f"/api/v1/projects/{project_id}/close",
            json={"notes": "PM trying to close"},
            headers=pm_headers,
        )
        assert close_response.status_code == 403


class TestProjectSummary:
    """Test cases for project summary."""

    def test_get_project_summary(self, client: TestClient, auth_headers: dict):
        """Test getting project summary with billing info."""
        # Create project
        client_response = client.post(
            "/api/v1/clients",
            json={
                "name": "Test",
                "email": "summary@example.com",
                "company": "Test",
            },
            headers=auth_headers,
        )
        client_id = client_response.json()["id"]

        sow_response = client.post(
            "/api/v1/sows",
            json={
                "client_id": client_id,
                "title": "Summary Test",
                "description": "Test",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "rate": 150,
                "total_budget": 100000,
            },
            headers=auth_headers,
        )
        sow_id = sow_response.json()["id"]

        client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)
        client.post(
            f"/api/v1/sows/{sow_id}/approve",
            json={"approved": True},
            headers=auth_headers,
        )

        project_response = client.post(
            "/api/v1/projects",
            json={"sow_id": sow_id},
            headers=auth_headers,
        )
        project_id = project_response.json()["id"]

        # Get summary
        summary_response = client.get(
            f"/api/v1/projects/{project_id}/summary",
            headers=auth_headers,
        )
        assert summary_response.status_code == 200
        summary = summary_response.json()
        assert summary["id"] == project_id
        assert summary["budget"] == "100000.00"
        assert "total_hours" in summary
        assert "billable_amount" in summary
        assert "budget_percentage" in summary

    def test_get_project_summary_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting summary for non-existent project."""
        response = client.get(
            "/api/v1/projects/99999/summary",
            headers=auth_headers,
        )
        assert response.status_code == 404
