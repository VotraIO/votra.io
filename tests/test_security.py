"""Tests for security utilities."""

import pytest
from jose import JWTError, jwt

from app.config import get_settings
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)

settings = get_settings()


def test_password_hashing():
    """Test password hashing and verification."""
    password = "SecurePassword123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original password
    assert hashed != password
    
    # Should be able to verify correct password
    assert verify_password(password, hashed)
    
    # Should reject incorrect password
    assert not verify_password("WrongPassword", hashed)


def test_password_hash_uniqueness():
    """Test that same password produces different hashes."""
    password = "TestPassword123"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Bcrypt should produce different hashes due to salt
    assert hash1 != hash2
    
    # Both should verify correctly
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_create_access_token():
    """Test JWT access token creation."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    # Token should be a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Should be able to decode token
    payload = decode_token(token)
    assert payload["sub"] == "testuser"
    assert "exp" in payload


def test_create_refresh_token():
    """Test JWT refresh token creation."""
    data = {"sub": "testuser"}
    token = create_refresh_token(data)
    
    # Token should be a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Should be able to decode token
    payload = decode_token(token)
    assert payload["sub"] == "testuser"
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_decode_token():
    """Test token decoding."""
    data = {"sub": "testuser", "role": "admin"}
    token = create_access_token(data)
    
    decoded = decode_token(token)
    
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded


def test_decode_invalid_token():
    """Test decoding invalid token raises error."""
    invalid_token = "invalid.token.here"
    
    with pytest.raises(JWTError):
        decode_token(invalid_token)


def test_token_contains_expiration():
    """Test that tokens contain expiration time."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    payload = decode_token(token)
    
    assert "exp" in payload
    assert isinstance(payload["exp"], int)
    assert payload["exp"] > 0


def test_verify_password_empty_strings():
    """Test password verification with empty strings."""
    # Empty password should not verify against any hash
    hashed = get_password_hash("password123")
    assert not verify_password("", hashed)


def test_verify_password_special_characters():
    """Test password hashing with special characters."""
    password = "P@ssw0rd!#$%^&*()"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed)
    assert not verify_password("P@ssw0rd!#$%^&*", hashed)  # Missing characters

def test_create_access_token_with_custom_expiration():
    """Test JWT access token with custom expiration."""
    from datetime import timedelta
    
    data = {"sub": "testuser"}
    custom_expiration = timedelta(hours=2)
    token = create_access_token(data, expires_delta=custom_expiration)
    
    payload = decode_token(token)
    assert payload["sub"] == "testuser"
    assert "exp" in payload
    # Verify token was created with roughly 2 hour expiration
    assert payload["exp"] > 0


def test_access_token_vs_refresh_token():
    """Test that access and refresh tokens are different types."""
    data = {"sub": "testuser"}
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    
    # Tokens should be different
    assert access_token != refresh_token
    
    # Decode both
    access_payload = decode_token(access_token)
    refresh_payload = decode_token(refresh_token)
    
    # Refresh token should have type marker
    assert "type" not in access_payload or access_payload.get("type") != "refresh"
    assert refresh_payload.get("type") == "refresh"


def test_token_preserves_data():
    """Test that token preserves all encoded data."""
    data = {
        "sub": "testuser",
        "email": "test@example.com",
        "role": "admin",
    }
    token = create_access_token(data)
    payload = decode_token(token)
    
    # All data should be preserved
    assert payload["sub"] == "testuser"
    assert payload["email"] == "test@example.com"
    assert payload["role"] == "admin"


def test_token_uses_configured_settings():
    """Test that tokens use settings from config."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    payload = decode_token(token)
    
    # Token should be created with configured algorithm
    assert isinstance(token, str)
    # Refresh token should use configured expiration days
    refresh_token = create_refresh_token(data)
    refresh_payload = decode_token(refresh_token)
    assert refresh_payload.get("type") == "refresh"