"""FastAPI router for game endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from chess_ai.application.commands.game_commands import (
    CreateGameCommand,
    MakeMoveCommand,
    ResignGameCommand,
)
from chess_ai.application.use_cases.game_use_cases import GameUseCase
from chess_ai.domain.models.game import Game
from chess_ai.domain.ports.engine import PositionEvaluation
from chess_ai.infrastructure.db.models.analysis_job import AnalysisJobModel, AnalysisJobStatus
from chess_ai.infrastructure.queue.tasks import run_analysis
from chess_ai.infrastructure.unit_of_work import InMemoryUnitOfWork
from chess_ai.presentation.api.dependencies import Session

router = APIRouter(prefix="/api/v1/games", tags=["Games"])

# ---------------------------------------------------------------------------
# Module-level singleton so all requests share the same in-memory store until
# a real DB is wired in Step 3.
# ---------------------------------------------------------------------------
_shared_uow = InMemoryUnitOfWork()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class CreateGameRequest(BaseModel):
    white_player_id: str = "player1"
    black_player_id: str = "bot"
    opponent_type: str = Field(default="stockfish", pattern="^(stockfish|random|human)$")
    bot_skill_level: int = Field(default=10, ge=0, le=20)
    time_control_seconds: int | None = None


class MakeMoveRequest(BaseModel):
    move: str = Field(..., description="Move in UCI format (e.g. e2e4) or SAN (e.g. e4)")
    player_id: str = "player1"
    expected_version: int = Field(
        ..., description="Current game version for optimistic concurrency"
    )


class ResignGameRequest(BaseModel):
    player_id: str = "player1"


class MoveResponse(BaseModel):
    move_id: str
    uci: str
    san: str
    fen_after: str
    color: str


class GameResponse(BaseModel):
    game_id: str
    status: str
    turn: str
    fen: str
    version: int
    white_player_id: str
    black_player_id: str
    opponent_type: str
    bot_skill_level: int
    time_control_seconds: int | None
    winner: str | None
    moves: list[MoveResponse]

    @classmethod
    def from_domain(cls, game: Game) -> GameResponse:
        return cls(
            game_id=game.game_id,
            status=game.status.value,
            turn=game.turn.value,
            fen=game.fen,
            version=game.version,
            white_player_id=game.white_player_id,
            black_player_id=game.black_player_id,
            opponent_type=game.opponent_type,
            bot_skill_level=game.bot_skill_level,
            time_control_seconds=game.time_control_seconds,
            winner=game.winner.value if game.winner else None,
            moves=[
                MoveResponse(
                    move_id=m.move_id,
                    uci=m.uci,
                    san=m.san,
                    fen_after=m.fen_after,
                    color=m.color.value,
                )
                for m in game.moves
            ],
        )


class VariationResponse(BaseModel):
    rank: int
    centipawns: int | None
    mate_in: int | None
    best_move_uci: str
    pv: list[str]


class EvaluationResponse(BaseModel):
    fen: str
    centipawns: int | None
    mate_in: int | None
    best_move_uci: str
    pv: list[str]
    depth: int
    variations: list[VariationResponse]

    @classmethod
    def from_domain(cls, evaluation: PositionEvaluation) -> EvaluationResponse:
        return cls(
            fen=evaluation.fen,
            centipawns=evaluation.centipawns,
            mate_in=evaluation.mate_in,
            best_move_uci=evaluation.best_move_uci,
            pv=evaluation.pv,
            depth=evaluation.depth,
            variations=[
                VariationResponse(
                    rank=variation.rank,
                    centipawns=variation.centipawns,
                    mate_in=variation.mate_in,
                    best_move_uci=variation.best_move_uci,
                    pv=variation.pv,
                )
                for variation in evaluation.variations
            ],
        )


class MoveAnalysisResponse(BaseModel):
    move_number: int
    color: str
    move_uci: str
    move_san: str
    classification: str
    centipawn_loss: int
    score_before: EvaluationResponse
    score_after: EvaluationResponse
    tactical_motifs: list[str]


class GameReviewResponse(BaseModel):
    depth: int
    multipv: int
    final_evaluation: EvaluationResponse
    moves: list[MoveAnalysisResponse]
    classification_counts: dict[str, int]
    accuracy: dict[str, float]
    critical_moments: list[int]
    summary: str


class AnalysisJobResponse(BaseModel):
    job_id: str
    game_id: str
    status: str
    attempts: int
    progress: float
    error_message: str | None = None
    result: GameReviewResponse | None = None


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------


def get_game_use_case() -> GameUseCase:
    """Return a GameUseCase backed by the shared in-memory store with dynamic strategy resolution."""
    return GameUseCase(uow=_shared_uow, opponent_strategy=None)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    request: CreateGameRequest,
    use_case: GameUseCase = Depends(get_game_use_case),
) -> GameResponse:
    cmd = CreateGameCommand(
        white_player_id=request.white_player_id,
        black_player_id=request.black_player_id,
        opponent_type=request.opponent_type,
        bot_skill_level=request.bot_skill_level,
        time_control_seconds=request.time_control_seconds,
    )
    game = await use_case.create_game(cmd)
    return GameResponse.from_domain(game)


def _snapshot_game(game: Game) -> dict[str, object]:
    return {
        "game_id": game.game_id,
        "white_player_id": game.white_player_id,
        "black_player_id": game.black_player_id,
        "opponent_type": game.opponent_type,
        "bot_skill_level": game.bot_skill_level,
        "time_control_seconds": game.time_control_seconds,
        "version": game.version,
        "moves": [
            {
                "move_id": move.move_id,
                "uci": move.uci,
                "san": move.san,
                "fen_before": move.fen_before,
                "fen_after": move.fen_after,
                "move_number": move.move_number,
                "color": move.color.value,
            }
            for move in game.moves
        ],
    }


def _job_response(job: AnalysisJobModel) -> AnalysisJobResponse:
    return AnalysisJobResponse(
        job_id=job.id,
        game_id=job.game_id,
        status=job.status,
        attempts=job.attempts,
        progress=job.progress,
        error_message=job.error_message,
        result=GameReviewResponse.model_validate(job.result) if job.result else None,
    )


@router.post("/{game_id}/analysis", response_model=AnalysisJobResponse, status_code=202)
async def analyze_game(
    game_id: str,
    session: Session,
    depth: int = 16,
    multipv: int = 3,
    use_case: GameUseCase = Depends(get_game_use_case),
) -> AnalysisJobResponse:
    async with use_case._uow as uow:
        game = await uow.games.get_by_id(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail=f"Game {game_id} not found")

    depth = max(1, min(depth, 30))
    multipv = max(1, min(multipv, 5))
    job = AnalysisJobModel(
        game_id=game.game_id,
        game_version=game.version,
        depth=depth,
        multipv=multipv,
        game_snapshot=_snapshot_game(game),
        status=AnalysisJobStatus.QUEUED,
    )
    session.add(job)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        job = await session.scalar(
            select(AnalysisJobModel).where(
                AnalysisJobModel.game_id == game.game_id,
                AnalysisJobModel.game_version == game.version,
                AnalysisJobModel.depth == depth,
                AnalysisJobModel.multipv == multipv,
            )
        )
        if job is None:
            raise HTTPException(status_code=503, detail="Unable to create analysis job")
        return _job_response(job)
    run_analysis.delay(job.id)
    return _job_response(job)


@router.get("/{game_id}/analysis", response_model=AnalysisJobResponse)
async def get_analysis_status(game_id: str, session: Session) -> AnalysisJobResponse:
    job = await session.scalar(
        select(AnalysisJobModel)
        .where(AnalysisJobModel.game_id == game_id)
        .order_by(AnalysisJobModel.queued_at.desc())
    )
    if job is None:
        raise HTTPException(status_code=404, detail=f"No analysis job found for game {game_id}")
    return _job_response(job)


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: str,
    use_case: GameUseCase = Depends(get_game_use_case),
) -> GameResponse:
    async with use_case._uow as uow:
        game = await uow.games.get_by_id(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
    return GameResponse.from_domain(game)


@router.post("/{game_id}/moves", response_model=GameResponse, status_code=status.HTTP_200_OK)
async def make_move(
    game_id: str,
    request: MakeMoveRequest,
    idempotency_key: str = Header(default=""),
    use_case: GameUseCase = Depends(get_game_use_case),
) -> GameResponse:
    cmd = MakeMoveCommand(
        game_id=game_id,
        move_uci=request.move,
        player_id=request.player_id,
        expected_version=request.expected_version,
        idempotency_key=idempotency_key or str(uuid.uuid4()),
    )
    game = await use_case.make_move(cmd)
    return GameResponse.from_domain(game)


@router.post("/{game_id}/resign", response_model=GameResponse, status_code=status.HTTP_200_OK)
async def resign_game(
    game_id: str,
    request: ResignGameRequest,
    use_case: GameUseCase = Depends(get_game_use_case),
) -> GameResponse:
    cmd = ResignGameCommand(game_id=game_id, player_id=request.player_id)
    game = await use_case.resign_game(cmd)
    return GameResponse.from_domain(game)
