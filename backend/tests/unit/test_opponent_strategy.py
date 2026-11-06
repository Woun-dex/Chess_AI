"""Unit tests for AI Opponent Strategies."""

import chess
import pytest

from chess_ai.infrastructure.engine.opponent_strategy import (
    BotOpponentFactory,
    RandomOpponentStrategy,
)

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


@pytest.mark.asyncio
async def test_random_strategy_returns_legal_move() -> None:
    strategy = RandomOpponentStrategy()
    move_uci = await strategy.choose_move(STARTING_FEN)

    board = chess.Board(STARTING_FEN)
    move = chess.Move.from_uci(move_uci)
    assert move in board.legal_moves


@pytest.mark.asyncio
async def test_random_strategy_raises_on_checkmate() -> None:
    # Fool's mate position - White has no moves, is checkmated
    checkmate_fen = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
    strategy = RandomOpponentStrategy()

    with pytest.raises(ValueError, match="No legal moves"):
        await strategy.choose_move(checkmate_fen)


def test_bot_opponent_factory_creates_random_bot() -> None:
    bot = BotOpponentFactory.create("random")
    assert isinstance(bot, RandomOpponentStrategy)


def test_bot_opponent_factory_rejects_unknown_bot() -> None:
    with pytest.raises(ValueError, match="Unknown opponent type"):
        BotOpponentFactory.create("unsupported_bot")

