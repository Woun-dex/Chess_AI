"""SQLAlchemy implementation of a user repository."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chess_ai.infrastructure.db.models.player_profile import PlayerProfileModel
from chess_ai.infrastructure.db.models.user import UserModel


class SqlAlchemyUserRepository:
    """Basic CRUD operations for the User aggregate."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: str) -> UserModel | None:
        result = await self._session.execute(
            select(UserModel)
            .options(selectinload(UserModel.player_profile))
            .where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> UserModel | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return result.scalar_one_or_none()

    async def save(self, user: UserModel) -> UserModel:
        """Persist (insert or update) a UserModel instance."""
        existing = await self.get_by_id(user.id)
        if existing is None:
            self._session.add(user)
        else:
            existing.email = user.email
            existing.hashed_password = user.hashed_password
            existing.username = user.username
            existing.is_active = user.is_active
        return user

    async def create(
        self,
        *,
        email: str,
        username: str,
        hashed_password: str,
    ) -> UserModel:
        """Factory helper: create and stage a new UserModel."""
        now = datetime.now(UTC)
        user = UserModel(
            id=str(uuid.uuid4()),
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self._session.add(user)
        return user

    async def get_profile(self, user_id: str) -> PlayerProfileModel | None:
        result = await self._session.execute(
            select(PlayerProfileModel).where(PlayerProfileModel.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_profile(self, user_id: str) -> PlayerProfileModel:
        profile = PlayerProfileModel(user_id=user_id)
        self._session.add(profile)
        return profile
