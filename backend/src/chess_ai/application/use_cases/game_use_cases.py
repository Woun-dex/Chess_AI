"""Core use case class — the heart of CQRS command handling."""

from __future__ import annotations

from chess_ai.application.commands.game_commands import CreateGameCommand, MakeMoveCommand
from chess_ai.domain.models.game import Color, Game
from chess_ai.domain.ports.repository import UnitOfWork
from chess_ai.infrastructure.engine.opponent_strategy import OpponentStrategy


class GameUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        opponent_strategy: OpponentStrategy | None = None,
    ) -> None:
        self._uow = uow
        self._opponent_strategy = opponent_strategy

    async def create_game(self, cmd: CreateGameCommand) -> Game:
        async with self._uow as uow:
            game = Game(
                white_player_id=cmd.white_player_id,
                black_player_id=cmd.black_player_id,
            )
            await uow.games.save(game)
            await uow.commit()
            return game

    async def make_move(self, cmd: MakeMoveCommand) -> Game:
        async with self._uow as uow:
            game = await uow.games.get_by_id(cmd.game_id)
            if game is None:
                raise ValueError(f"Game {cmd.game_id} not found")

            # Apply player move (domain validates legality + concurrency)
            game.make_move(cmd.move_uci, expected_version=cmd.expected_version)

            # If opponent is a bot and game still in progress, play bot move
            if (
                self._opponent_strategy is not None
                and not game.is_game_over
                and game.black_player_id == "bot"
                and game.turn == Color.BLACK
            ):
                bot_move_uci = await self._opponent_strategy.choose_move(game.fen)
                game.make_move(bot_move_uci)

            await uow.games.save(game)
            await uow.commit()
            return game
