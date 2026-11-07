"""LangGraph state for one tutor turn."""

from typing import TypedDict

from chess_ai.application.tutor.schemas import TutorIntent, TutorResponse


class TutorState(TypedDict, total=False):
    user_id: str
    session_id: str
    student_message: str
    fen: str | None
    game_id: str | None
    hint_level: int
    intent: TutorIntent
    engine_analysis: dict[str, object] | None
    lesson_context: list[str]
    response: TutorResponse
