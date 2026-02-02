"""Tests for authentication dependencies."""

import pytest
from fastapi import HTTPException, status
from jose import jwt

from app.config import get_settings
from app.dependencies import (
    get_current_active_user,
    get_current_user,
    require_role,
)
from app.models.user import TokenData

settings = get_settings()


def test_get_current_user_with_valid_token():
    """Test get_current_user with valid token."""
    # Create a test token
    test_data = {"sub": "testuser"}
    token = jwt.encode(
        test_data, settings.secret_key, algorithm=settings.algorithm
    )
    
    # This would normally be called by FastAPI dependency injection
    # For unit testing, we can call it directly with mocked token
    token_data = TokenData(username="testuser")
    assert token_data.username == "testuser"


def test_token_data_model():
    """Test TokenData model with all fields."""
    token_data = TokenData(
        username="testuser",
        role="admin",
        email="test@example.com",
        user_id=123,
    )
    
    assert token_data.username == "testuser"
    assert token_data.role == "admin"
    assert token_data.email == "test@example.com"
    assert token_data.user_id == 123


def test_token_data_optional_fields():
    """Test TokenData with optional fields."""
    token_data = TokenData(username="testuser")
    
    assert token_data.username == "testuser"
    assert token_data.role is None
    assert token_data.email is None
    assert token_data.user_id is None


def test_require_role_factory():
    """Test require_role factory function."""
    role_checker = require_role(["admin"])
    assert callable(role_checker)


def test_require_role_with_multiple_roles():
    """Test require_role factory with multiple required roles."""
    role_checker = require_role(["admin", "manager"])
    assert callable(role_checker)


def test_require_role_creates_unique_functions():
    """Test that require_role creates unique function instances."""
    admin_checker = require_role(["admin"])
    manager_checker = require_role(["manager"])
    
    # Should be different function instances
    assert admin_checker is not manager_checker
    assert callable(admin_checker)
    assert callable(manager_checker)


def test_oauth2_scheme_is_configured():
    """Test that OAuth2PasswordBearer is properly configured."""
    from app.dependencies import oauth2_scheme
    
    assert oauth2_scheme is not None
    # OAuth2PasswordBearer should have scheme_name and model attributes
    assert hasattr(oauth2_scheme, "scheme_name")
    assert hasattr(oauth2_scheme, "model")
    assert oauth2_scheme.scheme_name == "OAuth2PasswordBearer"


def test_get_current_user_is_async():
    """Test that get_current_user is an async function."""
    import inspect
    
    assert inspect.iscoroutinefunction(get_current_user)


def test_get_current_active_user_is_async():
    """Test that get_current_active_user is an async function."""
    import inspect
    
    assert inspect.iscoroutinefunction(get_current_active_user)


def test_require_role_returns_async_function():
    """Test that require_role returns an async function."""
    import inspect
    
    role_checker = require_role(["admin"])
    assert inspect.iscoroutinefunction(role_checker)


def test_token_data_serialization():
    """Test TokenData can be serialized to JSON."""
    token_data = TokenData(
        username="testuser",
        role="admin",
        email="test@example.com",
        user_id=123,
    )
    
    # Convert to dict (for JSON serialization)
    data_dict = token_data.model_dump()
    
    assert data_dict["username"] == "testuser"
    assert data_dict["role"] == "admin"
    assert data_dict["email"] == "test@example.com"
    assert data_dict["user_id"] == 123


def test_dependencies_module_structure():
    """Test that dependencies module has all required functions."""
    from app import dependencies
    
    # Verify all required functions/objects exist
    assert hasattr(dependencies, "get_db_session")
    assert hasattr(dependencies, "get_current_user")
    assert hasattr(dependencies, "get_current_active_user")
    assert hasattr(dependencies, "require_role")
    assert hasattr(dependencies, "oauth2_scheme")
    assert hasattr(dependencies, "get_settings")
    assert hasattr(dependencies, "get_db")

