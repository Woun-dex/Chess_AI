"""Use cases for user profile management."""

from sqlalchemy.ext.asyncio import AsyncSession

from chess_ai.infrastructure.db.models.player_profile import PlayerProfileModel
from chess_ai.infrastructure.db.models.user import UserModel
from chess_ai.infrastructure.repositories.user_repository import SqlAlchemyUserRepository


class UserService:
    """Coordinates authenticated user and profile operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._repository = SqlAlchemyUserRepository(session)
        self._session = session

    async def get_current(self, user_id: str) -> UserModel | None:
        return await self._repository.get_by_id(user_id)

    async def update_profile(self, user_id: str, changes: dict[str, object]) -> PlayerProfileModel:
        profile = await self._repository.get_profile(user_id)
        if profile is None:
            profile = await self._repository.create_profile(user_id)
        for field, value in changes.items():
            setattr(profile, field, value)
        await self._session.commit()
        await self._session.refresh(profile)
        return profile
