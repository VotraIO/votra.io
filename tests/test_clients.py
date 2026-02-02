"""Tests for client endpoints."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_create_client_success(client: TestClient, auth_headers: dict):
    """Test creating a client successfully.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    client_data = {
        "name": "Test Client",
        "email": "client@example.com",
        "phone": "555-1234",
        "company": "Test Company",
        "billing_address": "123 Main St",
        "payment_terms": 30,
    }

    response = client.post("/api/v1/clients", json=client_data, headers=auth_headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == client_data["name"]
    assert data["email"] == client_data["email"]
    assert "id" in data
    assert "created_at" in data


def test_create_client_duplicate_email(client: TestClient, auth_headers: dict):
    """Test creating a client with duplicate email returns 409.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    client_data = {
        "name": "Test Client",
        "email": "duplicate@example.com",
        "phone": "555-1234",
        "company": "Test Company",
    }

    # Create first client
    response1 = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    assert response1.status_code == status.HTTP_201_CREATED

    # Try to create duplicate
    response2 = client.post("/api/v1/clients", json=client_data, headers=auth_headers)
    assert response2.status_code == status.HTTP_409_CONFLICT
    data = response2.json()
    assert "already exists" in data["detail"]


def test_create_client_missing_required_fields(client: TestClient, auth_headers: dict):
    """Test creating a client without required fields returns 422.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    client_data = {
        "name": "Test Client",
        # Missing email (required field)
        "company": "Test Company",
    }

    response = client.post("/api/v1/clients", json=client_data, headers=auth_headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_client_invalid_email(client: TestClient, auth_headers: dict):
    """Test creating a client with invalid email returns 422.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    client_data = {
        "name": "Test Client",
        "email": "not-an-email",
        "company": "Test Company",
    }

    response = client.post("/api/v1/clients", json=client_data, headers=auth_headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_clients(client: TestClient, auth_headers: dict):
    """Test listing clients.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    # Create some clients first
    for i in range(3):
        client_data = {
            "name": f"Client {i}",
            "email": f"client{i}@example.com",
            "company": f"Company {i}",
        }
        client.post("/api/v1/clients", json=client_data, headers=auth_headers)

    # List clients
    response = client.get("/api/v1/clients", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "items" in data
    assert len(data["items"]) >= 3


def test_list_clients_pagination(client: TestClient, auth_headers: dict):
    """Test listing clients with pagination.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    # Create multiple clients
    for i in range(25):
        client_data = {
            "name": f"Client {i}",
            "email": f"pageclient{i}@example.com",
            "company": f"Company {i}",
        }
        client.post("/api/v1/clients", json=client_data, headers=auth_headers)

    # Get first page with limit=10
    response = client.get("/api/v1/clients?skip=0&limit=10", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["page"] == 1
    assert data["per_page"] == 10
    assert len(data["items"]) == 10


def test_list_clients_filter_active(client: TestClient, auth_headers: dict):
    """Test listing clients filtered by active status.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    # Create active client
    active_client = {
        "name": "Active Client",
        "email": "active@example.com",
        "is_active": True,
    }
    client.post("/api/v1/clients", json=active_client, headers=auth_headers)

    # List only active clients
    response = client.get("/api/v1/clients?is_active=true", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(item["is_active"] for item in data["items"])


def test_get_client(client: TestClient, auth_headers: dict):
    """Test getting a specific client.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    # Create a client
    client_data = {
        "name": "Get Test Client",
        "email": "gettest@example.com",
        "company": "Get Test Company",
    }
    create_response = client.post(
        "/api/v1/clients", json=client_data, headers=auth_headers
    )
    client_id = create_response.json()["id"]

    # Get the client
    response = client.get(f"/api/v1/clients/{client_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == client_id
    assert data["name"] == client_data["name"]
    assert data["email"] == client_data["email"]


def test_get_client_not_found(client: TestClient, auth_headers: dict):
    """Test getting a non-existent client returns 404.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    response = client.get("/api/v1/clients/99999", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "not found" in data["detail"]


def test_update_client(client: TestClient, auth_headers: dict):
    """Test updating a client.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    # Create a client
    client_data = {
        "name": "Original Name",
        "email": "update@example.com",
        "company": "Original Company",
    }
    create_response = client.post(
        "/api/v1/clients", json=client_data, headers=auth_headers
    )
    client_id = create_response.json()["id"]

    # Update the client
    update_data = {
        "name": "Updated Name",
        "company": "Updated Company",
    }
    response = client.put(
        f"/api/v1/clients/{client_id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["company"] == update_data["company"]
    # Email should remain unchanged
    assert data["email"] == client_data["email"]


def test_update_client_email_conflict(client: TestClient, auth_headers: dict):
    """Test updating a client's email to one that already exists returns 409.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    # Create two clients
    client1 = {
        "name": "Client 1",
        "email": "client1@example.com",
    }
    client2 = {
        "name": "Client 2",
        "email": "client2@example.com",
    }
    resp1 = client.post("/api/v1/clients", json=client1, headers=auth_headers)
    resp2 = client.post("/api/v1/clients", json=client2, headers=auth_headers)

    client1_id = resp1.json()["id"]
    client2_email = resp2.json()["email"]

    # Try to update client1's email to client2's email
    update_data = {"email": client2_email}
    response = client.put(
        f"/api/v1/clients/{client1_id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_update_client_not_found(client: TestClient, auth_headers: dict):
    """Test updating a non-existent client returns 404.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    update_data = {
        "name": "Updated Name",
    }
    response = client.put(
        "/api/v1/clients/99999",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_client(client: TestClient, auth_headers: dict):
    """Test deleting (deactivating) a client.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    # Create a client
    client_data = {
        "name": "Delete Test Client",
        "email": "deletetest@example.com",
    }
    create_response = client.post(
        "/api/v1/clients", json=client_data, headers=auth_headers
    )
    client_id = create_response.json()["id"]

    # Delete the client
    response = client.delete(f"/api/v1/clients/{client_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify client is deactivated (not fully deleted)
    get_response = client.get(f"/api/v1/clients/{client_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_200_OK
    data = get_response.json()
    assert data["is_active"] is False


def test_delete_client_not_found(client: TestClient, auth_headers: dict):
    """Test deleting a non-existent client returns 404.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    response = client.delete("/api/v1/clients/99999", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_client_response_structure(client: TestClient, auth_headers: dict):
    """Test client response has all required fields.

    Args:
        client: FastAPI test client
        auth_headers: Authentication headers
    """
    client_data = {
        "name": "Structure Test",
        "email": "structure@example.com",
        "phone": "555-1234",
        "company": "Structure Company",
        "billing_address": "123 Main St",
        "payment_terms": 30,
    }

    response = client.post("/api/v1/clients", json=client_data, headers=auth_headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    # Verify required fields
    required_fields = [
        "id",
        "name",
        "email",
        "phone",
        "company",
        "billing_address",
        "payment_terms",
        "is_active",
        "created_at",
        "updated_at",
    ]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
