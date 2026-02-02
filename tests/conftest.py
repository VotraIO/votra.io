"""Pytest configuration and fixtures."""

import os

import pytest
from fastapi.testclient import TestClient

# Set test environment before importing app
os.environ["SECRET_KEY"] = "test-secret-key-min-32-chars-long-for-testing-purposes-only"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["DEBUG"] = "True"
os.environ["ENVIRONMENT"] = "test"
os.environ["RATE_LIMIT_PER_MINUTE"] = "10000"  # High limit for testing

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application.

    Yields:
        TestClient: FastAPI test client
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing protected endpoints.

    Returns:
        dict: Headers with Bearer token
    """
    # TODO: Generate real token for testing
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6OTk5OTk5OTk5OX0.fake"
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_user():
    """Create a mock user for testing.

    Returns:
        dict: Mock user data
    """
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
    }
