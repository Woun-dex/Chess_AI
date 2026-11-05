import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

import chess


class Color(StrEnum):
    WHITE = "white"
    BLACK = "black"


class GameStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    INSUFFICIENT_MATERIAL = "insufficient_material"
    SEVENTYFIVE_MOVES = "seventyfive_moves"
    FIVEFOLD_REPETITION = "fivefold_repetition"
    RESIGNED = "resigned"
    DRAW_AGREED = "draw_agreed"


class DomainException(Exception):
    """Base domain exception."""


class IllegalMoveError(DomainException):
    """Raised when an attempted move is not legal in the current position."""


class GameNotInProgressError(DomainException):
    """Raised when attempting to play in a game that has finished."""


class ConcurrencyConflictError(DomainException):
    """Raised when move submission expected version does not match current version."""


@dataclass(frozen=True)
class MoveRecord:
    move_id: str
    uci: str
    san: str
    fen_before: str
    fen_after: str
    move_number: int
    color: Color
    played_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Game:
    game_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    white_player_id: str = "human"
    black_player_id: str = "bot"
    status: GameStatus = GameStatus.IN_PROGRESS
    winner: Color | None = None
    moves: list[MoveRecord] = field(default_factory=list)
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _board: chess.Board = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._board = chess.Board()
        # Reconstruct board state from moves if loaded from storage
        for move_rec in self.moves:
            self._board.push_uci(move_rec.uci)
        self._update_status_from_board()

    @property
    def fen(self) -> str:
        return self._board.fen()

    @property
    def turn(self) -> Color:
        return Color.WHITE if self._board.turn == chess.WHITE else Color.BLACK

    @property
    def is_game_over(self) -> bool:
        return self.status != GameStatus.IN_PROGRESS

    def make_move(self, move_str: str, expected_version: int | None = None) -> MoveRecord:
        """Execute a move (SAN or UCI format) with legality check and optimistic concurrency control."""
        if self.is_game_over:
            raise GameNotInProgressError(
                f"Cannot play move: Game {self.game_id} is already {self.status.value}"
            )

        if expected_version is not None and expected_version != self.version:
            raise ConcurrencyConflictError(
                f"Concurrency conflict: expected version {expected_version}, current is {self.version}"
            )

        # Parse move
        try:
            # Try UCI first, fallback to SAN
            try:
                chess_move = chess.Move.from_uci(move_str)
                if chess_move not in self._board.legal_moves:
                    chess_move = self._board.parse_san(move_str)
            except ValueError:
                chess_move = self._board.parse_san(move_str)
        except ValueError as err:
            raise IllegalMoveError(f"Invalid move notation '{move_str}': {err}") from err

        if chess_move not in self._board.legal_moves:
            raise IllegalMoveError(f"Move '{move_str}' is illegal in current position.")

        fen_before = self._board.fen()
        color = self.turn
        san = self._board.san(chess_move)
        uci = chess_move.uci()

        # Push to internal board
        self._board.push(chess_move)
        fen_after = self._board.fen()

        move_record = MoveRecord(
            move_id=str(uuid.uuid4()),
            uci=uci,
            san=san,
            fen_before=fen_before,
            fen_after=fen_after,
            move_number=len(self.moves) + 1,
            color=color,
            played_at=datetime.now(UTC),
        )

        self.moves.append(move_record)
        self.version += 1
        self.updated_at = datetime.now(UTC)
        self._update_status_from_board()

        return move_record

    def resign(self, player_color: Color) -> None:
        if self.is_game_over:
            raise GameNotInProgressError(f"Cannot resign: game is already {self.status.value}")
        self.status = GameStatus.RESIGNED
        self.winner = Color.BLACK if player_color == Color.WHITE else Color.WHITE
        self.version += 1
        self.updated_at = datetime.now(UTC)

    def _update_status_from_board(self) -> None:
        if self._board.is_checkmate():
            self.status = GameStatus.CHECKMATE
            # Previous turn delivered mate
            self.winner = Color.BLACK if self._board.turn == chess.WHITE else Color.WHITE
        elif self._board.is_stalemate():
            self.status = GameStatus.STALEMATE
        elif self._board.is_insufficient_material():
            self.status = GameStatus.INSUFFICIENT_MATERIAL
        elif self._board.is_seventyfive_moves():
            self.status = GameStatus.SEVENTYFIVE_MOVES
        elif self._board.is_fivefold_repetition():
            self.status = GameStatus.FIVEFOLD_REPETITION
