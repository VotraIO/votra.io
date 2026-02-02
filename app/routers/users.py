"""Users router."""


from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.dependencies import get_current_active_user
from app.limiter import limiter
from app.models.user import TokenData, UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register User",
    description="Create a new user account",
)
@limiter.limit("3/hour")
async def register_user(request: Request, user: UserCreate) -> UserResponse:
    """Register a new user.

    Args:
        user: User creation data

    Returns:
        UserResponse: Created user information

    Raises:
        HTTPException: If user already exists or validation fails
    """
    user_service = UserService()

    # Check if user already exists
    existing_user = await user_service.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    existing_email = await user_service.get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    created_user = await user_service.create_user(user)
    return created_user


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Get the currently authenticated user's information",
)
@limiter.limit("30/minute")
async def get_current_user_info(
    request: Request,
    current_user: TokenData = Depends(get_current_active_user),
) -> UserResponse:
    """Get current user information.

    Args:
        current_user: Current authenticated user from token

    Returns:
        UserResponse: Current user information

    Raises:
        HTTPException: If user not found
    """
    user_service = UserService()
    user = await user_service.get_user_by_username(str(current_user.username))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List Users",
    description="Get a list of all users (requires authentication)",
)
@limiter.limit("20/minute")
async def list_users(
    request: Request,
    current_user: TokenData = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> list[UserResponse]:
    """Get list of all users.

    Args:
        current_user: Current authenticated user
        skip: Number of users to skip (pagination)
        limit: Maximum number of users to return

    Returns:
        List[UserResponse]: List of users
    """
    user_service = UserService()
    users = await user_service.get_users(skip=skip, limit=limit)
    return users


@router.get(
    "/{username}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User by Username",
    description="Get user information by username",
)
@limiter.limit("30/minute")
async def get_user(
    request: Request,
    username: str,
    current_user: TokenData = Depends(get_current_active_user),
) -> UserResponse:
    """Get user by username.

    Args:
        username: Username to look up
        current_user: Current authenticated user

    Returns:
        UserResponse: User information

    Raises:
        HTTPException: If user not found
    """
    user_service = UserService()
    user = await user_service.get_user_by_username(username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
