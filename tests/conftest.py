"""Pytest configuration and fixtures."""

import asyncio
import os
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

# Set test environment before importing app
os.environ["SECRET_KEY"] = "test-secret-key-min-32-chars-long-for-testing-purposes-only"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["DEBUG"] = "True"
os.environ["ENVIRONMENT"] = "test"
os.environ["RATE_LIMIT_PER_MINUTE"] = "10000"  # High limit for testing

from app.config import get_settings
from app.main import app
from app.utils.security import create_access_token


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up test database after each test."""
    yield
    # Remove test database after test
    import os

    if os.path.exists("./test.db"):
        os.remove("./test.db")


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
    settings = get_settings()
    # Generate a valid JWT token for testing
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token(
        data={
            "sub": "testuser",
            "role": "admin",
            "email": "test@example.com",
            "user_id": 1,
        },
        expires_delta=access_token_expires,
    )
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
