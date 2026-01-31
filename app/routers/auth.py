"""Authentication router."""

from datetime import timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.models.user import LoginRequest, RefreshTokenRequest, Token
from app.services.auth_service import AuthService
from app.utils.security import create_access_token, create_refresh_token, decode_token

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
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
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
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
    user = await auth_service.authenticate_user(
        form_data.username, form_data.password
    )
    
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
        username: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")
        
        if username is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        # Create new access token
        access_token_expires = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token)
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
