import pytest

from chess_ai.domain.models.game import (
    Color,
    ConcurrencyConflictError,
    Game,
    GameNotInProgressError,
    GameStatus,
    IllegalMoveError,
)


def test_game_initialization():
    game = Game()
    assert game.status == GameStatus.IN_PROGRESS
    assert game.version == 1
    assert game.turn == Color.WHITE
    assert len(game.moves) == 0
    assert not game.is_game_over
    assert game.fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_make_valid_moves():
    game = Game()
    # Move 1: e4
    m1 = game.make_move("e4", expected_version=1)
    assert m1.san == "e4"
    assert m1.uci == "e2e4"
    assert m1.color == Color.WHITE
    assert game.version == 2
    assert game.turn == Color.BLACK

    # Move 2: e5
    m2 = game.make_move("e5", expected_version=2)
    assert m2.san == "e5"
    assert m2.color == Color.BLACK
    assert game.version == 3
    assert game.turn == Color.WHITE


def test_illegal_move_rejection():
    game = Game()
    with pytest.raises(IllegalMoveError):
        game.make_move("e5")  # White cannot play e5 on first move


def test_optimistic_concurrency_conflict():
    game = Game()
    # Player submits move with stale version
    with pytest.raises(ConcurrencyConflictError):
        game.make_move("e4", expected_version=99)


def test_scholars_mate_detection():
    game = Game()
    # 1. e4 e5
    game.make_move("e4")
    game.make_move("e5")
    # 2. Bc4 Nc6
    game.make_move("Bc4")
    game.make_move("Nc6")
    # 3. Qh5 Nf6??
    game.make_move("Qh5")
    game.make_move("Nf6")
    # 4. Qxf7# Checkmate
    game.make_move("Qxf7#")

    assert game.status == GameStatus.CHECKMATE
    assert game.winner == Color.WHITE
    assert game.is_game_over

    # Subsequent moves must fail
    with pytest.raises(GameNotInProgressError):
        game.make_move("d5")


def test_resignation():
    game = Game()
    game.make_move("e4")
    game.resign(Color.BLACK)
    assert game.status == GameStatus.RESIGNED
    assert game.winner == Color.WHITE
    assert game.is_game_over
