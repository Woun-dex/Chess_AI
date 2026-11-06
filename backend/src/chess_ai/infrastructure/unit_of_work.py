"""Unit-of-work implementations: SQLAlchemy async UoW and in-memory UoW for testing."""

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from chess_ai.infrastructure.repositories.game_repository import SqlAlchemyGameRepository
from chess_ai.infrastructure.repositories.user_repository import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork:
    """
    Async context manager that owns an ``AsyncSession`` and exposes typed
    repository properties.  Rolls back automatically on exception; callers
    must call ``await uow.commit()`` explicitly on success.

    Usage::

        async with SqlAlchemyUnitOfWork(session_factory) as uow:
            game = await uow.games.get_by_id(game_id)
            game.make_move("e4")
            await uow.games.save(game)
            await uow.commit()
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> Self:
        self._session: AsyncSession = self._session_factory()
        self.games = SqlAlchemyGameRepository(self._session)
        self.users = SqlAlchemyUserRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        """Flush and commit the current transaction."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Discard all pending changes."""
        await self._session.rollback()


class InMemoryUnitOfWork:
    """In-memory UoW for development/testing without a real database."""

    def __init__(self) -> None:
        from chess_ai.domain.ports.repository import GameRepositoryPort
        from chess_ai.infrastructure.repositories.in_memory_game_repository import (
            InMemoryGameRepository,
        )

        self.games: GameRepositoryPort = InMemoryGameRepository()

    async def __aenter__(self) -> "InMemoryUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        pass

    async def commit(self) -> None:
        pass  # In-memory: no-op

    async def rollback(self) -> None:
        pass  # In-memory: no-op
