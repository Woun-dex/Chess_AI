"""FastAPI router for game endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from chess_ai.application.commands.game_commands import (
    CreateGameCommand,
    MakeMoveCommand,
    ResignGameCommand,
)
from chess_ai.application.use_cases.game_use_cases import GameUseCase
from chess_ai.domain.models.game import Game
from chess_ai.infrastructure.unit_of_work import InMemoryUnitOfWork

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
    expected_version: int = Field(..., description="Current game version for optimistic concurrency")


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
