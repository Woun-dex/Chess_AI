"""Core use case class — the heart of CQRS command handling."""

from __future__ import annotations

from chess_ai.application.commands.game_commands import (
    CreateGameCommand,
    MakeMoveCommand,
    ResignGameCommand,
)
from chess_ai.domain.models.game import Color, Game
from chess_ai.domain.ports.repository import UnitOfWork
from chess_ai.infrastructure.engine.opponent_strategy import (
    BotOpponentFactory,
    OpponentStrategy,
)


class GameUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        opponent_strategy: OpponentStrategy | None = None,
    ) -> None:
        self._uow = uow
        self._opponent_strategy = opponent_strategy

    async def _resolve_strategy(self, game: Game) -> OpponentStrategy | None:
        """Resolve the opponent strategy from configured injection or game settings."""
        if self._opponent_strategy is not None:
            return self._opponent_strategy
        if game.opponent_type == "human":
            return None

        from chess_ai.config import get_settings

        settings = get_settings()
        return BotOpponentFactory.create(
            opponent_type=game.opponent_type,
            engine_path=settings.STOCKFISH_PATH,
            skill_level=game.bot_skill_level,
        )

    async def create_game(self, cmd: CreateGameCommand) -> Game:
        async with self._uow as uow:
            game = Game(
                white_player_id=cmd.white_player_id,
                black_player_id=cmd.black_player_id,
                opponent_type=cmd.opponent_type,
                bot_skill_level=cmd.bot_skill_level,
                time_control_seconds=cmd.time_control_seconds,
            )

            # If White is the bot (e.g. human chose to play as Black), bot makes opening move!
            if game.white_player_id == "bot" and game.turn == Color.WHITE:
                strategy = await self._resolve_strategy(game)
                if strategy is not None:
                    bot_move_uci = await strategy.choose_move(game.fen)
                    game.make_move(bot_move_uci)

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
            strategy = await self._resolve_strategy(game)
            bot_color = (
                Color.BLACK
                if game.black_player_id == "bot"
                else (Color.WHITE if game.white_player_id == "bot" else None)
            )

            if (
                strategy is not None
                and not game.is_game_over
                and bot_color is not None
                and game.turn == bot_color
            ):
                bot_move_uci = await strategy.choose_move(game.fen)
                game.make_move(bot_move_uci)

            await uow.games.save(game)
            await uow.commit()
            return game

    async def resign_game(self, cmd: ResignGameCommand) -> Game:
        async with self._uow as uow:
            game = await uow.games.get_by_id(cmd.game_id)
            if game is None:
                raise ValueError(f"Game {cmd.game_id} not found")

            # Determine player color
            player_color = Color.WHITE if cmd.player_id == game.white_player_id else Color.BLACK
            game.resign(player_color)

            await uow.games.save(game)
            await uow.commit()
            return game
