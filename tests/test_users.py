"""Tests for user endpoints."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    """Test user registration with valid data.
    
    Args:
        client: FastAPI test client
    """
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "SecurePass123",
        "full_name": "New User",
    }
    
    response = client.post("/api/v1/users/register", json=user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be in response


def test_register_user_with_weak_password(client: TestClient):
    """Test registration with weak password fails validation.
    
    Args:
        client: FastAPI test client
    """
    user_data = {
        "username": "newuser2",
        "email": "newuser2@example.com",
        "password": "weak",  # Too short and no uppercase/numbers
        "full_name": "New User",
    }
    
    response = client.post("/api/v1/users/register", json=user_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


def test_get_current_user_unauthorized(client: TestClient):
    """Test getting current user without authentication.
    
    Args:
        client: FastAPI test client
    """
    response = client.get("/api/v1/users/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_users_unauthorized(client: TestClient):
    """Test listing users without authentication.
    
    Args:
        client: FastAPI test client
    """
    response = client.get("/api/v1/users/")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_by_username_unauthorized(client: TestClient):
    """Test getting user by username without authentication.
    
    Args:
        client: FastAPI test client
    """
    response = client.get("/api/v1/users/testuser")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_user_response_structure(client: TestClient):
    """Test user registration response structure.
    
    Args:
        client: FastAPI test client
    """
    user_data = {
        "username": "structuretest",
        "email": "structure@example.com",
        "password": "SecurePass123",
        "full_name": "Structure Test",
    }
    
    response = client.post("/api/v1/users/register", json=user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    # Verify required fields
    required_fields = ["id", "username", "email", "is_active", "created_at", "updated_at"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Verify password is not exposed
    assert "password" not in data
    assert "hashed_password" not in data


def test_password_validation_no_uppercase(client: TestClient):
    """Test password validation requires uppercase letter.

    Args:
        client: FastAPI test client
    """
    user_data = {
        "username": "nouppercaseuser",
        "email": "nouppercase@example.com",
        "password": "lowercase123",  # No uppercase
    }

    response = client.post("/api/v1/users/register", json=user_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert any("uppercase" in str(error).lower() for error in data.get("detail", []))


def test_password_validation_no_number(client: TestClient):
    """Test password validation requires number.

    Args:
        client: FastAPI test client
    """
    user_data = {
        "username": "nonumberuser",
        "email": "nonumber@example.com",
        "password": "NoNumberPass",  # No number
    }

    response = client.post("/api/v1/users/register", json=user_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert any("number" in str(error).lower() for error in data.get("detail", []))
