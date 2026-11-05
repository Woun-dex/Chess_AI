from abc import ABC, abstractmethod
from typing import Protocol

from chess_ai.domain.models.game import Game


class GameRepositoryPort(ABC):
    """Port for game persistence."""

    @abstractmethod
    async def get_by_id(self, game_id: str) -> Game | None: ...

    @abstractmethod
    async def save(self, game: Game) -> None: ...


class UnitOfWork(Protocol):
    """Protocol defining transaction boundaries."""

    games: GameRepositoryPort

    async def __aenter__(self) -> "UnitOfWork": ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
