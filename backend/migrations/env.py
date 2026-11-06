"""Alembic environment for async SQLAlchemy engine."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

import chess_ai.infrastructure.db.models  # noqa: F401  # side-effect: registers all models

# ---------------------------------------------------------------------------
# Import Base and all models so their metadata is registered before autogenerate
# ---------------------------------------------------------------------------
from chess_ai.infrastructure.db.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """Return DB URL from alembic.ini (or override via env var DATABASE_URL)."""
    import os

    return os.environ.get("DATABASE_URL", config.get_main_option("sqlalchemy.url", ""))


# ---------------------------------------------------------------------------
# Offline mode — emit SQL to stdout without a live connection
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online mode — connect to the live database
# ---------------------------------------------------------------------------


async def run_async_migrations() -> None:
    """Create an async engine and run migrations inside a sync callable."""
    url = get_url()
    connectable = create_async_engine(url, echo=False)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection: object) -> None:
    context.configure(
        connection=connection,  # type: ignore[arg-type]
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Entry point for the online mode — bridges sync Alembic ↔ async engine."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
