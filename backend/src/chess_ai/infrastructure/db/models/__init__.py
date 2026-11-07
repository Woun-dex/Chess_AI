"""ORM models package — import all models here so Alembic can discover them."""

from chess_ai.infrastructure.db.models.game import GameModel
from chess_ai.infrastructure.db.models.game_analysis import GameAnalysisModel
from chess_ai.infrastructure.db.models.game_move import GameMoveModel
from chess_ai.infrastructure.db.models.learning_profile import (
    LearningProfileModel,
    TrainingPlanItemModel,
    TrainingPlanModel,
)
from chess_ai.infrastructure.db.models.lesson import (
    ExerciseAttemptModel,
    ExerciseModel,
    LessonModel,
)
from chess_ai.infrastructure.db.models.move_analysis import MoveAnalysisModel
from chess_ai.infrastructure.db.models.outbox import OutboxEventModel
from chess_ai.infrastructure.db.models.player_profile import PlayerProfileModel
from chess_ai.infrastructure.db.models.tutor_checkpoint import TutorCheckpointModel
from chess_ai.infrastructure.db.models.tutor_session import TutorMessageModel, TutorSessionModel
from chess_ai.infrastructure.db.models.user import UserModel

__all__ = [
    "ExerciseAttemptModel",
    "ExerciseModel",
    "GameAnalysisModel",
    "GameModel",
    "GameMoveModel",
    "LearningProfileModel",
    "LessonModel",
    "MoveAnalysisModel",
    "OutboxEventModel",
    "PlayerProfileModel",
    "TrainingPlanItemModel",
    "TrainingPlanModel",
    "TutorCheckpointModel",
    "TutorMessageModel",
    "TutorSessionModel",
    "UserModel",
]
