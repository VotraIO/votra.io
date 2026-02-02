"""Tests for SOW endpoints."""

from datetime import date, timedelta

from fastapi import status
from fastapi.testclient import TestClient


def test_create_sow_success(client: TestClient, auth_headers: dict):
    """Test creating a new SOW."""
    # First create a client
    client_data = {"name": "Test Client", "email": "client@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    assert client_resp.status_code == status.HTTP_201_CREATED
    client_id = client_resp.json()["id"]

    # Create SOW
    sow_data = {
        "client_id": client_id,
        "title": "Website Development Project",
        "description": "Full website redesign and development",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=90)),
        "rate": "150.00",
        "total_budget": "45000.00",
    }
    response = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == sow_data["title"]
    assert data["client_id"] == client_id
    assert data["status"] == "draft"
    assert "id" in data
    assert "created_at" in data


def test_create_sow_invalid_client(client: TestClient, auth_headers: dict):
    """Test creating SOW with non-existent client."""
    sow_data = {
        "client_id": 99999,
        "title": "Test SOW",
        "description": "Test description",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "rate": "100.00",
        "total_budget": "3000.00",
    }
    response = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "not found" in response.json()["detail"].lower()


def test_create_sow_invalid_dates(client: TestClient, auth_headers: dict):
    """Test creating SOW with invalid date range."""
    # Create client first
    client_data = {"name": "Test Client", "email": "dates@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    client_id = client_resp.json()["id"]

    # Try to create SOW with end_date before start_date
    sow_data = {
        "client_id": client_id,
        "title": "Test SOW",
        "description": "Test description",
        "start_date": str(date.today()),
        "end_date": str(date.today() - timedelta(days=1)),  # Invalid!
        "rate": "100.00",
        "total_budget": "3000.00",
    }
    response = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_sows(client: TestClient, auth_headers: dict):
    """Test listing SOWs."""
    response = client.get("/api/v1/sows", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_list_sows_with_filters(client: TestClient, auth_headers: dict):
    """Test listing SOWs with status filter."""
    # Create client and SOW
    client_data = {"name": "Filter Client", "email": "filter@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    client_id = client_resp.json()["id"]

    sow_data = {
        "client_id": client_id,
        "title": "Filter Test SOW",
        "description": "Test",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "rate": "100.00",
        "total_budget": "3000.00",
    }
    client.post("/api/v1/sows", json=sow_data, headers=auth_headers)

    # Filter by status
    response = client.get("/api/v1/sows?status_filter=draft", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(item["status"] == "draft" for item in data["items"])


def test_get_sow(client: TestClient, auth_headers: dict):
    """Test getting a specific SOW."""
    # Create client and SOW
    client_data = {"name": "Get Client", "email": "get@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    client_id = client_resp.json()["id"]

    sow_data = {
        "client_id": client_id,
        "title": "Get Test SOW",
        "description": "Test",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "rate": "100.00",
        "total_budget": "3000.00",
    }
    create_resp = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)
    sow_id = create_resp.json()["id"]

    # Get SOW
    response = client.get(f"/api/v1/sows/{sow_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sow_id
    assert data["title"] == sow_data["title"]


def test_get_sow_not_found(client: TestClient, auth_headers: dict):
    """Test getting non-existent SOW."""
    response = client.get("/api/v1/sows/99999", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_sow_draft(client: TestClient, auth_headers: dict):
    """Test updating a SOW in draft status."""
    # Create client and SOW
    client_data = {"name": "Update Client", "email": "update@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    client_id = client_resp.json()["id"]

    sow_data = {
        "client_id": client_id,
        "title": "Original Title",
        "description": "Original description",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "rate": "100.00",
        "total_budget": "3000.00",
    }
    create_resp = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)
    sow_id = create_resp.json()["id"]

    # Update SOW
    update_data = {"title": "Updated Title", "description": "Updated description"}
    response = client.put(
        f"/api/v1/sows/{sow_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["status"] == "draft"


def test_update_sow_not_draft(client: TestClient, auth_headers: dict):
    """Test that updating non-draft SOW fails."""
    # Create client and SOW
    client_data = {"name": "Pending Client", "email": "pending@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    client_id = client_resp.json()["id"]

    sow_data = {
        "client_id": client_id,
        "title": "Pending SOW",
        "description": "Test",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "rate": "100.00",
        "total_budget": "3000.00",
    }
    create_resp = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)
    sow_id = create_resp.json()["id"]

    # Submit SOW (changes status to pending)
    client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)

    # Try to update (should fail)
    update_data = {"title": "Should Fail"}
    response = client.put(
        f"/api/v1/sows/{sow_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "draft" in response.json()["detail"].lower()


def test_submit_sow(client: TestClient, auth_headers: dict):
    """Test submitting SOW for approval."""
    # Create client and SOW
    client_data = {"name": "Submit Client", "email": "submit@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    client_id = client_resp.json()["id"]

    sow_data = {
        "client_id": client_id,
        "title": "Submit Test SOW",
        "description": "Test",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "rate": "100.00",
        "total_budget": "3000.00",
    }
    create_resp = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)
    sow_id = create_resp.json()["id"]

    # Submit SOW
    response = client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "pending"


def test_submit_sow_already_submitted(client: TestClient, auth_headers: dict):
    """Test that submitting already-submitted SOW fails."""
    # Create client and SOW
    client_data = {"name": "Double Submit", "email": "double@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    client_id = client_resp.json()["id"]

    sow_data = {
        "client_id": client_id,
        "title": "Double Submit SOW",
        "description": "Test",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "rate": "100.00",
        "total_budget": "3000.00",
    }
    create_resp = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)
    sow_id = create_resp.json()["id"]

    # Submit once
    client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)

    # Try to submit again (should fail)
    response = client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_approve_sow(client: TestClient, auth_headers: dict):
    """Test approving a SOW."""
    # Create client and SOW
    client_data = {"name": "Approve Client", "email": "approve@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    client_id = client_resp.json()["id"]

    sow_data = {
        "client_id": client_id,
        "title": "Approve Test SOW",
        "description": "Test",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "rate": "100.00",
        "total_budget": "3000.00",
    }
    create_resp = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)
    sow_id = create_resp.json()["id"]

    # Submit SOW
    client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)

    # Approve SOW
    approval_data = {"approved": True, "notes": "Looks good!"}
    response = client.post(
        f"/api/v1/sows/{sow_id}/approve", json=approval_data, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "approved"
    assert data["approved_by"] is not None
    assert data["approved_at"] is not None


def test_reject_sow(client: TestClient, auth_headers: dict):
    """Test rejecting a SOW."""
    # Create client and SOW
    client_data = {"name": "Reject Client", "email": "reject@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    client_id = client_resp.json()["id"]

    sow_data = {
        "client_id": client_id,
        "title": "Reject Test SOW",
        "description": "Test",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "rate": "100.00",
        "total_budget": "3000.00",
    }
    create_resp = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)
    sow_id = create_resp.json()["id"]

    # Submit SOW
    client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)

    # Reject SOW
    rejection_data = {"approved": False, "notes": "Needs revision"}
    response = client.post(
        f"/api/v1/sows/{sow_id}/approve", json=rejection_data, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "rejected"
    assert data["approved_by"] is not None
    assert data["approved_at"] is not None


def test_approve_sow_not_pending(client: TestClient, auth_headers: dict):
    """Test that approving non-pending SOW fails."""
    # Create client and SOW
    client_data = {"name": "Draft Approve", "email": "draftapprove@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    client_id = client_resp.json()["id"]

    sow_data = {
        "client_id": client_id,
        "title": "Draft SOW",
        "description": "Test",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "rate": "100.00",
        "total_budget": "3000.00",
    }
    create_resp = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)
    sow_id = create_resp.json()["id"]

    # Try to approve draft SOW (should fail)
    approval_data = {"approved": True}
    response = client.post(
        f"/api/v1/sows/{sow_id}/approve", json=approval_data, headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "pending" in response.json()["detail"].lower()


def test_sow_workflow(client: TestClient, auth_headers: dict):
    """Test complete SOW workflow: create → submit → approve."""
    # Create client
    client_data = {"name": "Workflow Client", "email": "workflow@example.com"}
    client_resp = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    client_id = client_resp.json()["id"]

    # 1. Create SOW (draft)
    sow_data = {
        "client_id": client_id,
        "title": "Workflow SOW",
        "description": "Full workflow test",
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=60)),
        "rate": "125.00",
        "total_budget": "15000.00",
    }
    create_resp = client.post("/api/v1/sows", json=sow_data, headers=auth_headers)
    assert create_resp.status_code == status.HTTP_201_CREATED
    sow_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "draft"

    # 2. Update SOW (still draft)
    update_data = {"title": "Updated Workflow SOW"}
    update_resp = client.put(
        f"/api/v1/sows/{sow_id}", json=update_data, headers=auth_headers
    )
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["title"] == "Updated Workflow SOW"

    # 3. Submit for approval (draft → pending)
    submit_resp = client.post(f"/api/v1/sows/{sow_id}/submit", headers=auth_headers)
    assert submit_resp.status_code == status.HTTP_200_OK
    assert submit_resp.json()["status"] == "pending"

    # 4. Approve SOW (pending → approved)
    approval_data = {"approved": True, "notes": "Approved!"}
    approve_resp = client.post(
        f"/api/v1/sows/{sow_id}/approve", json=approval_data, headers=auth_headers
    )
    assert approve_resp.status_code == status.HTTP_200_OK
    assert approve_resp.json()["status"] == "approved"

    # 5. Verify cannot update after approval
    update_after = {"title": "Should Fail"}
    update_after_resp = client.put(
        f"/api/v1/sows/{sow_id}", json=update_after, headers=auth_headers
    )
    assert update_after_resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
