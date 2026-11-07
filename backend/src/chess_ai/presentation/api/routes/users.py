"""Authentication and user profile routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from chess_ai.application.services.auth_service import AuthService, InvalidCredentialsError
from chess_ai.application.services.user_service import UserService
from chess_ai.config import get_settings
from chess_ai.infrastructure.db.models.user import UserModel
from chess_ai.presentation.api.dependencies import Session, get_current_user
from chess_ai.presentation.api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from chess_ai.presentation.api.schemas.users import (
    ProfileResponse,
    ProfileUpdateRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/v1", tags=["Authentication", "Users"])


def _to_user_response(user: UserModel) -> UserResponse:
    if user.player_profile is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User profile missing"
        )
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        profile=ProfileResponse.from_model(user.player_profile),
    )


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, session: Session) -> UserResponse:
    try:
        user = await AuthService(session, get_settings()).register(
            request.email, request.username, request.password
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered",
        ) from exc
    return _to_user_response(user)


@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, session: Session) -> TokenResponse:
    try:
        token, expires_in = await AuthService(session, get_settings()).login(
            request.email.lower(), request.password
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        ) from exc
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.get("/users/me", response_model=UserResponse)
async def get_me(
    user: Annotated[UserModel, Depends(get_current_user)],
) -> UserResponse:
    return _to_user_response(user)


@router.patch("/users/me/profile", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    session: Session,
) -> ProfileResponse:
    profile = await UserService(session).update_profile(
        user.id, request.model_dump(exclude_unset=True)
    )
    return ProfileResponse.from_model(profile)
