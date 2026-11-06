"""Unit-of-work implementations: SQLAlchemy async UoW and in-memory UoW for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from chess_ai.domain.ports.repository import GameRepositoryPort
from chess_ai.infrastructure.repositories.game_repository import SqlAlchemyGameRepository
from chess_ai.infrastructure.repositories.in_memory_game_repository import (
    InMemoryGameRepository,
)
from chess_ai.infrastructure.repositories.user_repository import SqlAlchemyUserRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class SqlAlchemyUnitOfWork:
    """Async context manager that owns an AsyncSession and exposes typed repository properties."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self.games = SqlAlchemyGameRepository(self._session)
        self.users = SqlAlchemyUserRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        if self._session is not None:
            await self._session.close()

    async def commit(self) -> None:
        """Flush and commit the current transaction."""
        if self._session is not None:
            await self._session.commit()

    async def rollback(self) -> None:
        """Discard all pending changes."""
        if self._session is not None:
            await self._session.rollback()


class InMemoryUnitOfWork:
    """In-memory UoW for development/testing without a real database."""

    def __init__(self, repository: GameRepositoryPort | None = None) -> None:
        self.games: GameRepositoryPort = (
            repository if repository is not None else InMemoryGameRepository()
        )

    async def __aenter__(self) -> InMemoryUnitOfWork:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass
