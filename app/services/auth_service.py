"""Authentication service."""

from datetime import datetime, timezone

from app.models.user import UserCreate, UserResponse
from app.utils.security import get_password_hash, verify_password


class AuthService:
    """Authentication service for user authentication."""

    async def authenticate_user(self, username: str, password: str) -> dict | None:
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

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user account.

        Args:
            user_data: User creation data with email, username, password

        Returns:
            UserResponse: Created user data (excludes password)

        Raises:
            ValueError: If user validation fails
        """
        # TODO: Replace with actual database insertion
        # This is a mock implementation
        hashed_password = get_password_hash(user_data.password)
        now = datetime.now(timezone.utc)

        user = UserResponse(
            id=1,
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            created_at=now,
            updated_at=now,
        )

        return user

    async def get_user_by_email(self, email: str) -> dict | None:
        """Get user by email address.

        Args:
            email: Email address to search for

        Returns:
            Optional[dict]: User data if found, None otherwise
        """
        # TODO: Replace with actual database query
        # This is a mock implementation
        if email == "test@example.com":
            return {
                "username": "testuser",
                "email": "test@example.com",
                "is_active": True,
            }
        return None

    async def get_user_by_username(self, username: str) -> dict | None:
        """Get user by username.

        Args:
            username: Username to search for

        Returns:
            Optional[dict]: User data if found, None otherwise
        """
        # TODO: Replace with actual database query
        # This is a mock implementation
        if username == "testuser":
            return {
                "username": "testuser",
                "email": "test@example.com",
                "is_active": True,
            }
        return None

    async def verify_token(self, token: str) -> dict | None:
        """Verify a JWT token and return user data.

        Args:
            token: JWT token to verify

        Returns:
            Optional[dict]: User data if token is valid, None otherwise
        """
        # TODO: Implement token verification with database lookup
        pass
