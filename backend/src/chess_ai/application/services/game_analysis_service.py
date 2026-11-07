"""Application service for Stockfish-backed game reviews."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import exp

from chess_ai.domain.models.game import Color, Game
from chess_ai.domain.ports.engine import EnginePort, MoveAnalysisResult, PositionEvaluation


@dataclass(frozen=True)
class MoveReview:
    move_number: int
    color: str
    result: MoveAnalysisResult


@dataclass(frozen=True)
class GameReview:
    depth: int
    multipv: int
    final_evaluation: PositionEvaluation
    moves: list[MoveReview]
    classification_counts: dict[str, int]
    accuracy: dict[str, float]
    critical_moments: list[int]
    summary: str


class GameAnalysisService:
    """Build a complete, deterministic review from engine evaluations."""

    def __init__(self, engine: EnginePort) -> None:
        self._engine = engine

    async def review(
        self,
        game: Game,
        depth: int = 16,
        multipv: int = 3,
    ) -> GameReview:
        requested_depth = max(1, min(depth, 30))
        requested_multipv = max(1, min(multipv, 5))
        fens = [move.fen_before for move in game.moves]
        moves_uci = [move.uci for move in game.moves]
        results = await self._engine.analyze_game(
            fens,
            moves_uci,
            depth=requested_depth,
            multipv=requested_multipv,
        )
        final_evaluation = await self._engine.evaluate_position(
            game.fen,
            depth=requested_depth,
            multipv=requested_multipv,
        )
        reviewed_moves = [
            MoveReview(
                move_number=move.move_number,
                color=move.color.value,
                result=result,
            )
            for move, result in zip(game.moves, results, strict=False)
        ]
        counts = Counter(move.result.classification.value for move in reviewed_moves)
        losses = {
            color: [move.result.centipawn_loss for move in reviewed_moves if move.color == color]
            for color in (Color.WHITE.value, Color.BLACK.value)
        }
        accuracy = {
            color: _accuracy(losses[color])
            for color in (Color.WHITE.value, Color.BLACK.value)
        }
        critical = [
            move.move_number
            for move in reviewed_moves
            if move.result.centipawn_loss >= 50 or move.result.tactical_motifs
        ]
        summary = _summary(game, counts, accuracy, reviewed_moves)
        return GameReview(
            depth=requested_depth,
            multipv=requested_multipv,
            final_evaluation=final_evaluation,
            moves=reviewed_moves,
            classification_counts=dict(counts),
            accuracy=accuracy,
            critical_moments=critical,
            summary=summary,
        )


def _accuracy(losses: list[int]) -> float:
    if not losses:
        return 100.0
    return round(sum(exp(-loss / 100) for loss in losses) / len(losses) * 100, 1)


def _summary(
    game: Game,
    counts: Counter[str],
    accuracy: dict[str, float],
    moves: list[MoveReview],
) -> str:
    if not moves:
        return "No moves were played, so there is no game to review."
    worst = max(moves, key=lambda move: move.result.centipawn_loss)
    result = game.status.value.replace("_", " ")
    return (
        f"Game ended {result}. White accuracy was {accuracy['white']:.1f}% "
        f"and Black accuracy was {accuracy['black']:.1f}%. "
        f"The review found {counts.get('blunder', 0)} blunder(s), "
        f"{counts.get('mistake', 0)} mistake(s), and "
        f"{counts.get('inaccuracy', 0)} inaccuracy(ies). "
        f"The biggest swing was move {worst.move_number} ({worst.result.move_san}), "
        f"classified as {worst.result.classification.value}."
    )
