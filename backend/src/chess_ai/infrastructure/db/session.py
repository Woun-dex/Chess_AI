"""Async SQLAlchemy engine and session factory."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from chess_ai.config import get_settings


def build_engine(database_url: str) -> AsyncEngine:
    """Create an async SQLAlchemy engine from the given URL."""
    return create_async_engine(
        database_url,
        echo=False,  # Set True in dev to log SQL
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_pre_ping=True,  # Prevents "server closed connection" errors
    )


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Return a session factory bound to *engine*."""
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# ---------------------------------------------------------------------------
# Module-level singletons (lazy initialised on first import)
# ---------------------------------------------------------------------------


def _make_default_engine() -> AsyncEngine:
    return build_engine(get_settings().DATABASE_URL)


default_engine: AsyncEngine = _make_default_engine()
SessionFactory: async_sessionmaker[AsyncSession] = build_session_factory(default_engine)
