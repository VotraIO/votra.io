"""Authentication service."""

from typing import Optional

from app.utils.security import verify_password


class AuthService:
    """Authentication service for user authentication."""

    async def authenticate_user(
        self, username: str, password: str
    ) -> Optional[dict]:
        """Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            Optional[dict]: User data if authentication successful, None otherwise
        """
        # TODO: Replace with actual database query
        # This is a mock implementation
        fake_users_db = {
            "testuser": {
                "username": "testuser",
                "email": "test@example.com",
                # bcrypt hash of "secret"
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "is_active": True,
            }
        }
        
        user = fake_users_db.get(username)
        if not user:
            return None
        
        if not verify_password(password, user["hashed_password"]):
            return None
        
        return user

    async def verify_token(self, token: str) -> Optional[dict]:
        """Verify a JWT token and return user data.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Optional[dict]: User data if token is valid, None otherwise
        """
        # TODO: Implement token verification with database lookup
        pass
