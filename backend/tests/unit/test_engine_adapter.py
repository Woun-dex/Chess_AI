"""Unit tests for MockEngineAdapter."""

from __future__ import annotations

import pytest

from chess_ai.domain.ports.engine import MoveClassification, PositionEvaluation
from chess_ai.infrastructure.engine.mock_adapter import MockEngineAdapter

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


@pytest.fixture
def engine() -> MockEngineAdapter:
    return MockEngineAdapter()


async def test_evaluate_position_returns_position_evaluation(engine: MockEngineAdapter) -> None:
    result = await engine.evaluate_position(STARTING_FEN)
    assert isinstance(result, PositionEvaluation)
    assert result.fen == STARTING_FEN
    assert result.centipawns == 20
    assert result.mate_in is None
    assert result.depth > 0
    assert isinstance(result.best_move_uci, str)
    assert len(result.best_move_uci) >= 4  # e.g. "e2e4"


async def test_evaluate_position_has_valid_pv(engine: MockEngineAdapter) -> None:
    result = await engine.evaluate_position(STARTING_FEN, depth=10)
    assert isinstance(result.pv, list)
    assert len(result.pv) > 0
    assert result.pv[0] == result.best_move_uci


async def test_analyze_game_returns_move_analysis_list(engine: MockEngineAdapter) -> None:
    # Starting position, play e2e4
    fens = [STARTING_FEN]
    moves = ["e2e4"]
    results = await engine.analyze_game(fens, moves)
    assert len(results) == 1
    result = results[0]
    assert result.move_uci == "e2e4"
    assert result.move_san == "e4"
    assert result.centipawn_loss == 5
    assert isinstance(result.tactical_motifs, list)


async def test_analyze_game_move_classification_is_good(engine: MockEngineAdapter) -> None:
    fens = [STARTING_FEN]
    moves = ["e2e4"]
    results = await engine.analyze_game(fens, moves)
    assert results[0].classification == MoveClassification.GOOD


async def test_analyze_game_multiple_moves(engine: MockEngineAdapter) -> None:
    import chess

    fens = []
    moves_uci = []
    board = chess.Board()
    for uci in ["e2e4", "e7e5", "g1f3"]:
        fens.append(board.fen())
        moves_uci.append(uci)
        board.push_uci(uci)

    results = await engine.analyze_game(fens, moves_uci)
    assert len(results) == 3
    for r in results:
        assert r.classification == MoveClassification.GOOD


async def test_move_classification_values_exist() -> None:
    """Verify all expected MoveClassification members are present."""
    expected = {"brilliant", "great", "best", "excellent", "good", "inaccuracy", "mistake", "blunder"}
    actual = {c.value for c in MoveClassification}
    assert expected == actual
