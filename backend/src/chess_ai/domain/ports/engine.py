from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


class MoveClassification(StrEnum):
    BRILLIANT = "brilliant"
    GREAT = "great"
    BEST = "best"
    EXCELLENT = "excellent"
    GOOD = "good"
    INACCURACY = "inaccuracy"
    MISTAKE = "mistake"
    BLUNDER = "blunder"


@dataclass(frozen=True)
class PositionEvaluation:
    fen: str
    centipawns: int | None
    mate_in: int | None
    best_move_uci: str
    pv: list[str]  # Principal variation / line
    depth: int


@dataclass(frozen=True)
class MoveAnalysisResult:
    move_uci: str
    move_san: str
    classification: MoveClassification
    score_before: PositionEvaluation
    score_after: PositionEvaluation
    centipawn_loss: int
    tactical_motifs: list[str]


class EnginePort(ABC):
    """Port interface for chess calculation engine (Stockfish)."""

    @abstractmethod
    async def evaluate_position(
        self,
        fen: str,
        depth: int = 18,
        time_limit_secs: float = 1.0,
    ) -> PositionEvaluation:
        """Evaluate a single board position."""
        ...

    @abstractmethod
    async def analyze_game(
        self,
        fens: list[str],
        moves_uci: list[str],
        depth: int = 16,
    ) -> list[MoveAnalysisResult]:
        """Analyze an entire sequence of moves asynchronously."""
        ...
