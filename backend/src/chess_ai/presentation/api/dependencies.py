"""FastAPI dependencies shared by API routes."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from chess_ai.application.auth import get_user_id_from_token
from chess_ai.application.services.user_service import UserService
from chess_ai.config import get_settings
from chess_ai.infrastructure.db.models.user import UserModel
from chess_ai.infrastructure.unit_of_work import get_session

Session = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_session),
) -> UserModel:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = get_user_id_from_token(authorization[7:].strip(), get_settings().AUTH_SECRET)
    user = await UserService(session).get_current(user_id) if user_id else None
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    return user
