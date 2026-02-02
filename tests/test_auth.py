"""Tests for authentication endpoints."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_login_with_valid_credentials(client: TestClient):
    """Test login with valid credentials returns tokens.
    
    Args:
        client: FastAPI test client
    """
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "secret"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_invalid_credentials(client: TestClient):
    """Test login with invalid credentials returns 401.
    
    Args:
        client: FastAPI test client
    """
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "wrongpassword"},
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data


def test_login_with_nonexistent_user(client: TestClient):
    """Test login with non-existent user returns 401.
    
    Args:
        client: FastAPI test client
    """
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "nonexistent", "password": "password"},
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_json_endpoint(client: TestClient):
    """Test login with JSON body.
    
    Args:
        client: FastAPI test client
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "secret"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_json_with_invalid_credentials(client: TestClient):
    """Test JSON login with invalid credentials.
    
    Args:
        client: FastAPI test client
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "wrong"},
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_endpoint(client: TestClient):
    """Test refresh token endpoint (mock test).
    
    Args:
        client: FastAPI test client
    """
    # This is a basic test - in a real scenario, you'd get a valid refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"},
    )
    
    # Should return 401 for invalid token
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_missing_credentials(client: TestClient):
    """Test login with missing credentials returns 422.

    Args:
        client: FastAPI test client
    """
    response = client.post("/api/v1/auth/token", data={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "secret"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify required fields
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    
    # Verify token is a string
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0
