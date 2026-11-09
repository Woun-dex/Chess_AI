"""Unit tests for GameUseCase."""

import pytest

from chess_ai.application.commands.game_commands import (
    CreateGameCommand,
    MakeMoveCommand,
    UndoMoveCommand,
)
from chess_ai.application.use_cases.game_use_cases import GameUseCase
from chess_ai.domain.models.game import Color, GameStatus
from chess_ai.infrastructure.engine.opponent_strategy import RandomOpponentStrategy
from chess_ai.infrastructure.unit_of_work import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_create_game_persists_new_game() -> None:
    uow = InMemoryUnitOfWork()
    use_case = GameUseCase(uow=uow)

    cmd = CreateGameCommand(
        white_player_id="player-1",
        black_player_id="bot",
    )
    game = await use_case.create_game(cmd)

    assert game.white_player_id == "player-1"
    assert game.black_player_id == "bot"
    assert game.status == GameStatus.IN_PROGRESS
    assert game.version == 1

    async with uow:
        retrieved = await uow.games.get_by_id(game.game_id)
        assert retrieved is not None
        assert retrieved.game_id == game.game_id


@pytest.mark.asyncio
async def test_make_move_triggers_bot_response() -> None:
    uow = InMemoryUnitOfWork()
    strategy = RandomOpponentStrategy()
    use_case = GameUseCase(uow=uow, opponent_strategy=strategy)

    # 1. Create game
    create_cmd = CreateGameCommand(white_player_id="human", black_player_id="bot")
    game = await use_case.create_game(create_cmd)

    # 2. Player plays e4
    move_cmd = MakeMoveCommand(
        game_id=game.game_id,
        move_uci="e2e4",
        player_id="human",
        expected_version=1,
        idempotency_key="idemp-1",
    )
    updated_game = await use_case.make_move(move_cmd)

    # Player played 1 move, then bot responded with 1 move -> total 2 moves!
    assert len(updated_game.moves) == 2
    assert updated_game.moves[0].uci == "e2e4"
    assert updated_game.moves[0].color == Color.WHITE
    assert updated_game.moves[1].color == Color.BLACK
    assert updated_game.turn == Color.WHITE
    assert updated_game.version == 3


@pytest.mark.asyncio
async def test_undo_removes_player_and_bot_turn() -> None:
    uow = InMemoryUnitOfWork()
    use_case = GameUseCase(uow=uow, opponent_strategy=RandomOpponentStrategy())
    game = await use_case.create_game(
        CreateGameCommand(white_player_id="human", black_player_id="bot")
    )
    updated = await use_case.make_move(
        MakeMoveCommand(game.game_id, "e2e4", "human", 1, "undo-test")
    )
    updated_version = updated.version

    undone = await use_case.undo_move(
        UndoMoveCommand(updated.game_id, "human", updated.version)
    )

    assert undone.moves == []
    assert undone.fen == game.fen
    assert undone.version == updated_version + 1
