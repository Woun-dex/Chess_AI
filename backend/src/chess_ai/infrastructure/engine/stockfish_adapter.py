"""Stockfish UCI engine adapter using python-chess asyncio protocol."""

from __future__ import annotations

from typing import Any

import chess
import chess.engine

from chess_ai.domain.ports.engine import (
    EnginePort,
    MoveAnalysisResult,
    MoveClassification,
    PositionEvaluation,
    PositionVariation,
)

THRESHOLDS: dict[str, int] = {
    # centipawn loss → classification boundary
    "best": 0,
    "excellent": 10,
    "good": 25,
    "inaccuracy": 50,
    "mistake": 100,
    # blunder: > 100
}


class StockfishAdapter(EnginePort):
    """
    Concrete Stockfish UCI adapter. Uses python-chess AsyncioProtocol.

    Senior tip: Never instantiate chess.engine directly in a request handler.
    Use an engine pool managed as a context manager.
    """

    def __init__(
        self,
        engine_path: str,
        threads: int = 2,
        hash_mb: int = 64,
    ) -> None:
        self._engine_path = engine_path
        self._threads = threads
        self._hash_mb = hash_mb
        self._engine: Any = None

    async def _get_engine(self) -> Any:
        """Lazily initialize; in production use an engine pool."""
        if self._engine is None:
            # Use asyncio protocol for non-blocking I/O
            _, self._engine = await chess.engine.popen_uci(self._engine_path)
            await self._engine.configure({"Threads": self._threads, "Hash": self._hash_mb})
        return self._engine

    async def evaluate_position(
        self,
        fen: str,
        depth: int = 18,
        time_limit_secs: float = 1.0,
        multipv: int = 1,
    ) -> PositionEvaluation:
        engine = await self._get_engine()
        board = chess.Board(fen)

        # Limit: use depth OR time, whichever is first
        limit = chess.engine.Limit(depth=depth, time=time_limit_secs)
        requested_multipv = max(1, min(multipv, 5))
        raw_infos = await engine.analyse(board, limit, multipv=requested_multipv)
        infos = raw_infos if isinstance(raw_infos, list) else [raw_infos]
        variations = [_to_variation(info, rank) for rank, info in enumerate(infos, start=1)]
        primary = variations[0] if variations else PositionVariation(1, None, None, "", [])

        return PositionEvaluation(
            fen=fen,
            centipawns=primary.centipawns,
            mate_in=primary.mate_in,
            best_move_uci=primary.best_move_uci,
            pv=primary.pv,
            depth=infos[0].get("depth", depth) if infos else depth,
            variations=variations,
        )

    async def analyze_game(
        self,
        fens: list[str],
        moves_uci: list[str],
        depth: int = 16,
        multipv: int = 1,
    ) -> list[MoveAnalysisResult]:
        results: list[MoveAnalysisResult] = []

        for fen_before, move_uci in zip(fens, moves_uci, strict=False):
            board = chess.Board(fen_before)

            # Evaluate BEFORE the move
            eval_before = await self.evaluate_position(fen_before, depth=depth, multipv=multipv)

            # Play the move
            chess_move = chess.Move.from_uci(move_uci)
            san = board.san(chess_move)
            board.push(chess_move)
            fen_after = board.fen()

            # Evaluate AFTER the move (from same side perspective)
            eval_after = await self.evaluate_position(fen_after, depth=depth, multipv=multipv)

            # Calculate centipawn loss from the moving side's perspective
            # board.turn is now the side to move AFTER the push
            cp_loss = _compute_centipawn_loss(eval_before, eval_after, board.turn)

            # Classify the move
            classification = _classify_move(cp_loss, move_uci, eval_before)

            # Detect tactical motifs
            motifs = _detect_tactical_motifs(board, chess_move, fen_before)

            results.append(
                MoveAnalysisResult(
                    move_uci=move_uci,
                    move_san=san,
                    classification=classification,
                    score_before=eval_before,
                    score_after=eval_after,
                    centipawn_loss=cp_loss,
                    tactical_motifs=motifs,
                )
            )

        return results

    async def close(self) -> None:
        if self._engine:
            await self._engine.quit()
            self._engine = None


def _compute_centipawn_loss(
    before: PositionEvaluation,
    after: PositionEvaluation,
    side_to_move_after: chess.Color,
) -> int:
    """Compute centipawn loss from the perspective of the side that JUST moved."""
    # If before is a forced mate, cp_loss is extreme
    if before.mate_in is not None:
        if after.mate_in is not None:
            return 0  # Both mate → no loss
        return 1000  # Missed forced mate → blunder

    if before.centipawns is None:
        return 0

    # Score is always from White's perspective from Stockfish
    # Side that just moved is the OPPOSITE of side_to_move_after
    score_before = before.centipawns
    score_after: int
    if after.centipawns is not None:
        score_after = after.centipawns
    elif after.mate_in is not None and after.mate_in > 0:
        score_after = 10000
    else:
        score_after = -10000

    if side_to_move_after == chess.BLACK:  # White just moved
        loss = score_before - score_after
    else:  # Black just moved
        loss = score_after - score_before

    return max(0, loss)  # cp_loss is always non-negative


def _to_variation(info: dict[str, Any], rank: int) -> PositionVariation:
    score = info["score"].white()
    pv = [move.uci() for move in info.get("pv", [])]
    return PositionVariation(
        rank=rank,
        centipawns=score.score(),
        mate_in=score.mate(),
        best_move_uci=pv[0] if pv else "",
        pv=pv,
    )


def _classify_move(
    cp_loss: int,
    move_uci: str,
    before: PositionEvaluation,
) -> MoveClassification:
    """Classify a move based on centipawn loss."""
    if move_uci == before.best_move_uci and cp_loss == 0:
        return MoveClassification.BEST
    if cp_loss <= 10:
        return MoveClassification.EXCELLENT
    if cp_loss <= 25:
        return MoveClassification.GOOD
    if cp_loss <= 50:
        return MoveClassification.INACCURACY
    if cp_loss <= 100:
        return MoveClassification.MISTAKE
    return MoveClassification.BLUNDER


def _detect_tactical_motifs(
    board_after: chess.Board,
    move: chess.Move,
    fen_before: str,
) -> list[str]:
    """Heuristic detection of tactical motifs. NOTE: LLM never does this."""
    motifs: list[str] = []

    # Check if move gives check
    if board_after.is_check():
        motifs.append("check")

    # Detect if a capture was made
    board_before = chess.Board(fen_before)
    if board_before.is_capture(move):
        motifs.append("capture")

    # Detect fork: moved piece attacks two or more valuable pieces
    moved_piece = board_after.piece_at(move.to_square)
    if moved_piece:
        attackers = list(board_after.attacks(move.to_square))
        valuable_targets = [
            sq
            for sq in attackers
            if board_after.piece_at(sq) is not None
            and board_after.piece_at(sq).color != moved_piece.color  # type: ignore[union-attr]
            and board_after.piece_at(sq).piece_type  # type: ignore[union-attr]
            in [chess.KING, chess.QUEEN, chess.ROOK]
        ]
        if len(valuable_targets) >= 2:
            motifs.append("fork")

    return motifs
