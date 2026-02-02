"""Authentication router."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import get_settings
from app.dependencies import get_current_active_user
from app.limiter import limiter
from app.models.user import (
    LoginRequest,
    RefreshTokenRequest,
    Token,
    TokenData,
    UserCreate,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.utils.security import create_access_token, create_refresh_token, decode_token

router = APIRouter()
settings = get_settings()


@router.post(
    "/token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login",
    description="Authenticate user and return JWT tokens",
)
@limiter.limit("5/minute")
async def login(
    request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """Authenticate user and return access token.

    Args:
        form_data: OAuth2 password form with username and password

    Returns:
        Token: JWT access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    auth_service = AuthService()
    user = await auth_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": user["username"]})

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login (JSON)",
    description="Authenticate user with JSON payload and return JWT tokens",
)
@limiter.limit("5/minute")
async def login_json(request: Request, credentials: LoginRequest) -> Token:
    """Authenticate user with JSON body and return access token.

    Args:
        credentials: Login credentials with username and password

    Returns:
        Token: JWT access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    auth_service = AuthService()
    user = await auth_service.authenticate_user(
        credentials.username, credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": user["username"]})

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Refresh Token",
    description="Get a new access token using refresh token",
)
@limiter.limit("10/minute")
async def refresh_token(request: Request, token_request: RefreshTokenRequest) -> Token:
    """Refresh access token using refresh token.

    Args:
        request: FastAPI request object (for rate limiting)
        token_request: Refresh token request with refresh token

    Returns:
        Token: New JWT access token

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        payload = decode_token(token_request.refresh_token)
        username: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")

        if username is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Create new access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )

        return Token(access_token=access_token)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register User",
    description="Create a new user account",
)
@limiter.limit("3/minute")
async def register(request: Request, user_data: UserCreate) -> UserResponse:
    """Register a new user.

    Args:
        request: FastAPI request object (for rate limiting)
        user_data: User registration data with email, username, password

    Returns:
        UserResponse: Created user data (excludes password)

    Raises:
        HTTPException: If user already exists (409) or validation fails (422)
    """
    auth_service = AuthService()

    # Check if user already exists by email or username
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user_data.email}' already registered",
        )

    existing_user = await auth_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user_data.username}' already taken",
        )

    # Create new user
    new_user = await auth_service.create_user(user_data)

    return new_user


@router.get(
    "/me",
    response_model=TokenData,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Get information about the currently authenticated user",
)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_active_user),
) -> TokenData:
    """Get current user information from JWT token.

    Args:
        current_user: Current authenticated user from dependency

    Returns:
        TokenData: Current user information

    Raises:
        HTTPException: If not authenticated (401)
    """
    return current_user


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Invalidate the current JWT token",
)
async def logout(
    current_user: TokenData = Depends(get_current_active_user),
) -> dict:
    """Logout current user by invalidating token.

    Note: This is a basic implementation. For production, consider:
    - Token blacklisting in Redis or database
    - Token revocation lists
    - Proper cleanup of user sessions

    Args:
        current_user: Current authenticated user

    Returns:
        dict: Success message
    """
    # In a production system, you would:
    # 1. Add token to blacklist in Redis/database
    # 2. Clean up user session data
    # 3. Revoke any related refresh tokens

    return {
        "message": "Successfully logged out",
        "username": current_user.username,
    }
