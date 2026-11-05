"""In-memory game repository for development/testing without a real database."""

from __future__ import annotations

from chess_ai.domain.models.game import Game
from chess_ai.domain.ports.repository import GameRepositoryPort


class InMemoryGameRepository(GameRepositoryPort):
    """Thread-safe in-memory store. Used in development before DB is wired."""

    def __init__(self) -> None:
        self._store: dict[str, Game] = {}

    async def get_by_id(self, game_id: str) -> Game | None:
        return self._store.get(game_id)

    async def save(self, game: Game) -> None:
        self._store[game.game_id] = game
