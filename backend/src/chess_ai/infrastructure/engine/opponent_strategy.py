"""Strategy pattern for AI opponents."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass

import chess
import chess.engine


class OpponentStrategy(ABC):
    """Strategy pattern: different opponent behavior without changing game logic."""

    @abstractmethod
    async def choose_move(self, fen: str) -> str:
        """Return UCI string of the chosen move."""
        ...


class RandomOpponentStrategy(OpponentStrategy):
    """Completely random legal move selector — good for absolute beginners."""

    async def choose_move(self, fen: str) -> str:
        board = chess.Board(fen)
        legal = list(board.legal_moves)
        if not legal:
            raise ValueError("No legal moves in position")
        return random.choice(legal).uci()


class StockfishBotStrategy(OpponentStrategy):
    """
    Configurable Stockfish bot opponent.

    Skill Level 0-20 controls Elo:
      0  = ~800 Elo (beginner)
      5  = ~1100 Elo
      10 = ~1400 Elo
      15 = ~1800 Elo
      20 = ~3000 Elo (superhuman)
    """

    def __init__(self, engine_path: str, skill_level: int = 10) -> None:
        self._engine_path = engine_path
        self._skill_level = max(0, min(20, skill_level))  # Clamp 0-20
        self._engine: chess.engine.SimpleEngine | None = None

    async def choose_move(self, fen: str) -> str:
        if self._engine is None:
            try:
                _, self._engine = await chess.engine.popen_uci(self._engine_path)
                await self._engine.configure(
                    {
                        "Skill Level": self._skill_level,
                        "UCI_LimitStrength": True,
                    }
                )
            except FileNotFoundError:
                # Stockfish not installed — fall back to random move
                board = chess.Board(fen)
                legal = list(board.legal_moves)
                if not legal:
                    raise ValueError("No legal moves in position")
                return random.choice(legal).uci()

        board = chess.Board(fen)
        result = await self._engine.play(board, chess.engine.Limit(time=0.1))
        if result.move is None:
            raise ValueError("Stockfish returned no move")
        return result.move.uci()

    async def close(self) -> None:
        if self._engine:
            await self._engine.quit()
            self._engine = None


@dataclass
class BotOpponentFactory:
    """
    Factory pattern for creating configured opponents.

    Usage:
        strategy = BotOpponentFactory.create(opponent_type="stockfish", skill_level=5)
    """

    @staticmethod
    def create(
        opponent_type: str,
        engine_path: str = "stockfish",
        skill_level: int = 10,
    ) -> OpponentStrategy:
        match opponent_type:
            case "random":
                return RandomOpponentStrategy()
            case "stockfish":
                return StockfishBotStrategy(engine_path, skill_level)
            case _:
                raise ValueError(f"Unknown opponent type: {opponent_type}")
