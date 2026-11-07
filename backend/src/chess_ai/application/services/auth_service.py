"""Use cases for account authentication."""

from sqlalchemy.ext.asyncio import AsyncSession

from chess_ai.application.auth import create_access_token, hash_password, verify_password
from chess_ai.config import Settings
from chess_ai.infrastructure.db.models.user import UserModel
from chess_ai.infrastructure.repositories.user_repository import SqlAlchemyUserRepository


class InvalidCredentialsError(Exception):
    """Raised when authentication credentials are invalid."""


class AuthService:
    """Coordinates registration and login without HTTP concerns."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._repository = SqlAlchemyUserRepository(session)
        self._session = session
        self._settings = settings

    async def register(self, email: str, username: str, password: str) -> UserModel:
        if (
            await self._repository.get_by_email(email)
            or await self._repository.get_by_username(username)
        ):
            raise ValueError("Email or username already registered")
        user = await self._repository.create(
            email=email,
            username=username,
            hashed_password=hash_password(password),
        )
        await self._repository.create_profile(user.id)
        await self._session.commit()
        await self._session.refresh(user)
        await self._session.refresh(user, attribute_names=["player_profile"])
        return user

    async def login(self, email: str, password: str) -> tuple[str, int]:
        user = await self._repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError
        expires_in = self._settings.ACCESS_TOKEN_EXPIRE_SECONDS
        return (
            create_access_token(user.id, self._settings.AUTH_SECRET, expires_in),
            expires_in,
        )
