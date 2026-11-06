
"""
Unit-of-work implementations:
- SQLAlchemy async UoW for production.
- In-memory UoW for development and testing.

Both implementations use @asynccontextmanager to manage their lifecycle.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from chess_ai.infrastructure.repositories.game_repository import (
    SqlAlchemyGameRepository,
)
from chess_ai.infrastructure.repositories.user_repository import (
    SqlAlchemyUserRepository,
)


# ============================================================
# SQLAlchemy Unit of Work
# ============================================================

class SqlAlchemyUnitOfWork:
    """
    Coordinates repositories sharing one AsyncSession.

    The session lifecycle is managed by sqlalchemy_unit_of_work().

    Callers must explicitly call await uow.commit() on success.

    Usage:

        async with sqlalchemy_unit_of_work(session_factory) as uow:
            game = await uow.games.get_by_id(game_id)

            game.make_move("e4")

            await uow.games.save(game)

            await uow.commit()
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

        # All repositories share the same session.
        self.games = SqlAlchemyGameRepository(session)
        self.users = SqlAlchemyUserRepository(session)

    async def commit(self) -> None:
        """Flush and commit the current transaction."""

        try:
            await self._session.commit()

        except Exception:
            await self._session.rollback()
            raise

    async def rollback(self) -> None:
        """Discard all pending changes."""

        await self._session.rollback()


@asynccontextmanager
async def sqlalchemy_unit_of_work(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[SqlAlchemyUnitOfWork]:
    """
    Creates and manages a SQLAlchemy Unit of Work.

    Lifecycle:
        1. Create an AsyncSession.
        2. Construct the Unit of Work.
        3. Yield control to the application.
        4. Roll back if an exception occurs.
        5. Close the session.
    """

    async with session_factory() as session:

        uow = SqlAlchemyUnitOfWork(session)

        try:
            yield uow

        except BaseException:
            await uow.rollback()
            raise

        # The session context manager closes the session.
        # Any uncommitted transaction is rolled back on close.


# ============================================================
# In-Memory Unit of Work
# ============================================================

class InMemoryUnitOfWork:
    """
    In-memory UoW for development and testing.

    This implementation does not use a database.
    Its commit and rollback methods are no-ops.
    """

    def __init__(self) -> None:
        from chess_ai.domain.ports.repository import (
            GameRepositoryPort,
        )

        from chess_ai.infrastructure.repositories.in_memory_game_repository import (
            InMemoryGameRepository,
        )

        self.games: GameRepositoryPort = InMemoryGameRepository()

    async def commit(self) -> None:
        """No-op for in-memory persistence."""

        pass

    async def rollback(self) -> None:
        """No-op: transactional rollback is not implemented."""

        pass


@asynccontextmanager
async def in_memory_unit_of_work() -> AsyncIterator[InMemoryUnitOfWork]:
    """
    Creates and manages an in-memory Unit of Work.

    Lifecycle:
        1. Create the in-memory UoW.
        2. Yield control to the application.
        3. Call rollback if an exception occurs.
    """

    uow = InMemoryUnitOfWork()

    try:
        yield uow

    except BaseException:
        await uow.rollback()
        raise
