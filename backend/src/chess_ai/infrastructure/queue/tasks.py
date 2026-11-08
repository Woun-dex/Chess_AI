"""Celery tasks for background Stockfish analysis."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

import chess.engine

from chess_ai.application.services.game_analysis_service import GameAnalysisService
from chess_ai.config import get_settings
from chess_ai.domain.models.game import Color, Game, MoveRecord
from chess_ai.infrastructure.db.models.analysis_job import AnalysisJobModel, AnalysisJobStatus
from chess_ai.infrastructure.db.session import SessionFactory
from chess_ai.infrastructure.engine.stockfish_adapter import StockfishAdapter
from chess_ai.infrastructure.queue.celery_app import celery_app


def _game_from_snapshot(snapshot: dict[str, Any]) -> Game:
    moves = [
        MoveRecord(
            move_id=str(item["move_id"]),
            uci=str(item["uci"]),
            san=str(item["san"]),
            fen_before=str(item["fen_before"]),
            fen_after=str(item["fen_after"]),
            move_number=int(item["move_number"]),
            color=Color(str(item["color"])),
        )
        for item in snapshot["moves"]
    ]
    return Game(
        game_id=str(snapshot["game_id"]),
        white_player_id=str(snapshot["white_player_id"]),
        black_player_id=str(snapshot["black_player_id"]),
        opponent_type=str(snapshot["opponent_type"]),
        bot_skill_level=int(snapshot["bot_skill_level"]),
        time_control_seconds=snapshot.get("time_control_seconds"),
        moves=moves,
        version=int(snapshot["version"]),
    )


def _review_to_json(review: Any) -> dict[str, object]:
    return {
        "depth": review.depth,
        "multipv": review.multipv,
        "final_evaluation": _evaluation_to_json(review.final_evaluation),
        "moves": [
            {
                "move_number": move.move_number,
                "color": move.color,
                "move_uci": move.result.move_uci,
                "move_san": move.result.move_san,
                "classification": move.result.classification.value,
                "centipawn_loss": move.result.centipawn_loss,
                "score_before": _evaluation_to_json(move.result.score_before),
                "score_after": _evaluation_to_json(move.result.score_after),
                "tactical_motifs": move.result.tactical_motifs,
            }
            for move in review.moves
        ],
        "classification_counts": review.classification_counts,
        "accuracy": review.accuracy,
        "critical_moments": review.critical_moments,
        "summary": review.summary,
    }


def _evaluation_to_json(evaluation: Any) -> dict[str, object]:
    return {
        "fen": evaluation.fen,
        "centipawns": evaluation.centipawns,
        "mate_in": evaluation.mate_in,
        "best_move_uci": evaluation.best_move_uci,
        "pv": evaluation.pv,
        "depth": evaluation.depth,
        "variations": [
            {
                "rank": variation.rank,
                "centipawns": variation.centipawns,
                "mate_in": variation.mate_in,
                "best_move_uci": variation.best_move_uci,
                "pv": variation.pv,
            }
            for variation in evaluation.variations
        ],
    }


async def _run_analysis(job_id: str) -> None:
    async with SessionFactory() as session:
        job = await session.get(AnalysisJobModel, job_id)
        if job is None or job.status == AnalysisJobStatus.COMPLETED:
            return
        job.status = AnalysisJobStatus.RUNNING
        job.attempts += 1
        job.started_at = datetime.now(UTC)
        job.progress = 0.05
        await session.commit()

        engine = StockfishAdapter(
            engine_path=get_settings().STOCKFISH_PATH,
            threads=get_settings().STOCKFISH_ANALYSIS_THREADS,
        )
        try:
            game = _game_from_snapshot(job.game_snapshot)
            review = await GameAnalysisService(engine).review(
                game, depth=job.depth, multipv=job.multipv
            )
            job.result = _review_to_json(review)
            job.status = AnalysisJobStatus.COMPLETED
            job.progress = 1.0
            job.completed_at = datetime.now(UTC)
            job.error_message = None
        except (FileNotFoundError, OSError, chess.engine.EngineError) as exc:
            job.error_message = str(exc)[:2000]
            if job.attempts >= job.max_attempts:
                job.status = AnalysisJobStatus.DEAD
            else:
                job.status = AnalysisJobStatus.RETRYING
                job.next_retry_at = datetime.now(UTC) + timedelta(seconds=2**job.attempts)
            await session.commit()
            raise
        finally:
            await engine.close()
        await session.commit()


@celery_app.task(
    name="chess_ai.analysis.run",
    autoretry_for=(FileNotFoundError, OSError, chess.engine.EngineError),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_kwargs={"max_retries": 2},
)
def run_analysis(job_id: str) -> None:
    """Run one analysis job; Celery retries transient engine failures."""
    asyncio.run(_run_analysis(job_id))
