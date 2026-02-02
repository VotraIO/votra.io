"""Tests for health check endpoints."""

from fastapi import status
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint returns healthy status.

    Args:
        client: FastAPI test client
    """
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns API information.

    Args:
        client: FastAPI test client
    """
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "documentation" in data
    assert data["documentation"] == "/docs"


def test_health_check_response_structure(client: TestClient):
    """Test health check response has correct structure.

    Args:
        client: FastAPI test client
    """
    response = client.get("/health")
    data = response.json()

    # Verify all required fields are present
    required_fields = ["status", "version", "timestamp"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Verify field types
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["timestamp"], str)


def test_health_check_rate_limit(client: TestClient):
    """Test health check endpoint respects rate limiting.

    Args:
        client: FastAPI test client
    """
    # Make multiple requests (rate limit is 10/minute)
    responses = []
    for _ in range(5):
        response = client.get("/health")
        responses.append(response)

    # All should succeed within limit
    for response in responses:
        assert response.status_code == status.HTTP_200_OK
