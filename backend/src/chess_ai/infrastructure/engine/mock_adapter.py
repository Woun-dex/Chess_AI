"""Mock engine adapter for testing — never calls Stockfish."""

from __future__ import annotations

import chess

from chess_ai.domain.ports.engine import (
    EnginePort,
    MoveAnalysisResult,
    MoveClassification,
    PositionEvaluation,
)


class MockEngineAdapter(EnginePort):
    """Mock engine for unit tests - returns deterministic synthetic evaluations."""

    async def evaluate_position(
        self,
        fen: str,
        depth: int = 18,
        time_limit_secs: float = 1.0,
    ) -> PositionEvaluation:
        board = chess.Board(fen)
        legal_moves = list(board.legal_moves)
        best = legal_moves[0].uci() if legal_moves else ""
        return PositionEvaluation(
            fen=fen,
            centipawns=20,  # slight white edge
            mate_in=None,
            best_move_uci=best,
            pv=[best] if best else [],
            depth=depth,
        )

    async def analyze_game(
        self,
        fens: list[str],
        moves_uci: list[str],
        depth: int = 16,
    ) -> list[MoveAnalysisResult]:
        results: list[MoveAnalysisResult] = []
        for fen, uci in zip(fens, moves_uci):
            board = chess.Board(fen)
            move = chess.Move.from_uci(uci)
            san = board.san(move)
            eval_before = await self.evaluate_position(fen, depth)
            board.push(move)
            eval_after = await self.evaluate_position(board.fen(), depth)
            results.append(
                MoveAnalysisResult(
                    move_uci=uci,
                    move_san=san,
                    classification=MoveClassification.GOOD,
                    score_before=eval_before,
                    score_after=eval_after,
                    centipawn_loss=5,
                    tactical_motifs=[],
                )
            )
        return results
