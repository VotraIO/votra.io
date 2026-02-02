"""Dependency injection for FastAPI endpoints."""

from collections.abc import AsyncGenerator, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.base import get_db
from app.models.user import TokenData

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session dependency.

    Yields:
        AsyncSession: Database session
    """
    async for session in get_db():
        yield session


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Get current user from JWT token.

    Args:
        token: JWT access token from Authorization header

    Returns:
        TokenData: Decoded token data with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        TokenData: Validated active user data

    Raises:
        HTTPException: If user is inactive
    """
    # Here you would check if user is active in database
    # For now, we just return the user
    return current_user


def require_role(required_roles: list[str]) -> Callable:
    """Create a role-based access control (RBAC) dependency factory.

    Args:
        required_roles: List of roles required to access the endpoint

    Returns:
        Callable: A dependency function that validates user roles

    Raises:
        HTTPException: If user doesn't have required role

    Example:
        @app.get("/admin")
        async def admin_endpoint(user: TokenData = Depends(require_role(["admin"]))):
            return {"message": f"Hello {user.username}"}
    """

    async def check_role(
        current_user: TokenData = Depends(get_current_active_user),
    ) -> TokenData:
        """Check if user has required role.

        Args:
            current_user: Current user from token

        Returns:
            TokenData: User data if role matches

        Raises:
            HTTPException: If user role not in required roles
        """
        user_role = current_user.role if hasattr(current_user, "role") else None
        if not user_role or user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{user_role}' not in required roles: {required_roles}",
            )
        return current_user

    return check_role
