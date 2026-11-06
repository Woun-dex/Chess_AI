"""SQLAlchemy implementation of GameRepositoryPort."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chess_ai.domain.models.game import Color, Game, GameStatus, MoveRecord
from chess_ai.domain.ports.repository import GameRepositoryPort
from chess_ai.infrastructure.db.models.game import GameModel
from chess_ai.infrastructure.db.models.game_move import GameMoveModel


class SqlAlchemyGameRepository(GameRepositoryPort):
    """Concrete persistence adapter for the Game aggregate using SQLAlchemy 2.0 async."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get_by_id(self, game_id: str) -> Game | None:
        """Load a game aggregate (with moves) by its primary key."""
        result = await self._session.execute(
            select(GameModel)
            .where(GameModel.id == game_id)
            .options(selectinload(GameModel.moves))
        )
        db_game = result.scalar_one_or_none()
        if db_game is None:
            return None
        return self._to_domain(db_game)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def save(self, game: Game) -> None:
        """Persist (insert or update) a game aggregate and its moves."""
        # Try to load the existing ORM instance so SQLAlchemy tracks changes.
        result = await self._session.execute(
            select(GameModel)
            .where(GameModel.id == game.game_id)
            .options(selectinload(GameModel.moves))
        )
        db_game = result.scalar_one_or_none()

        if db_game is None:
            db_game = GameModel(id=game.game_id)
            self._session.add(db_game)

        # Sync scalar fields
        db_game.white_player_id = game.white_player_id
        db_game.black_player_id = game.black_player_id if game.black_player_id != "bot" else None
        db_game.opponent_type = game.opponent_type
        db_game.bot_skill_level = game.bot_skill_level
        db_game.time_control_seconds = game.time_control_seconds
        db_game.status = game.status.value
        db_game.winner_color = game.winner.value if game.winner else None
        db_game.version = game.version
        db_game.updated_at = game.updated_at

        # Sync moves — append any moves that are not already persisted.
        existing_move_ids = {m.id for m in db_game.moves}
        for move_rec in game.moves:
            if move_rec.move_id not in existing_move_ids:
                db_game.moves.append(
                    GameMoveModel(
                        id=move_rec.move_id,
                        game_id=game.game_id,
                        move_number=move_rec.move_number,
                        color=move_rec.color.value,
                        uci=move_rec.uci,
                        san=move_rec.san,
                        fen_before=move_rec.fen_before,
                        fen_after=move_rec.fen_after,
                        is_in_check=False,
                        played_at=move_rec.played_at,
                    )
                )

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------

    def _to_domain(self, db_game: GameModel) -> Game:
        """Reconstitute the Game aggregate from an ORM row (without replaying moves through the board)."""
        moves = [
            MoveRecord(
                move_id=m.id,
                uci=m.uci,
                san=m.san,
                fen_before=m.fen_before,
                fen_after=m.fen_after,
                move_number=m.move_number,
                color=Color(m.color),
                played_at=m.played_at,
            )
            for m in sorted(db_game.moves, key=lambda x: x.move_number)
        ]

        game = Game(
            game_id=db_game.id,
            white_player_id=db_game.white_player_id,
            black_player_id=db_game.black_player_id or "bot",
            opponent_type=db_game.opponent_type,
            bot_skill_level=db_game.bot_skill_level if db_game.bot_skill_level is not None else 10,
            time_control_seconds=db_game.time_control_seconds,
            status=GameStatus(db_game.status),
            winner=Color(db_game.winner_color) if db_game.winner_color and db_game.winner_color != "draw" else None,
            moves=moves,
            version=db_game.version,
            created_at=db_game.created_at,
            updated_at=db_game.updated_at,
        )
        return game
