"""CQRS command objects for game operations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CreateGameCommand:
    white_player_id: str
    black_player_id: str
    opponent_type: str = "stockfish"  # human | stockfish | random
    bot_skill_level: int = 10
    opponent_elo: int = 1400
    time_control_seconds: int | None = None


@dataclass(frozen=True)
class MakeMoveCommand:
    game_id: str
    move_uci: str  # Always UCI format from API
    player_id: str
    expected_version: int  # Optimistic concurrency
    idempotency_key: str  # Prevent duplicate move submissions


@dataclass(frozen=True)
class ResignGameCommand:
    game_id: str
    player_id: str


@dataclass(frozen=True)
class UndoMoveCommand:
    game_id: str
    player_id: str
    expected_version: int


@dataclass(frozen=True)
class RequestAnalysisCommand:
    game_id: str
    requested_by: str
    depth: int = 18
    idempotency_key: str = field(default="")
