"""Stable request and response contracts for tutor conversations."""

from enum import StrEnum

from pydantic import BaseModel, Field


class TutorIntent(StrEnum):
    EXPLAIN_POSITION = "explain_position"
    HINT = "hint"
    LESSON = "lesson"
    GAME_SUMMARY = "game_summary"


class TutorMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    fen: str | None = None
    game_id: str | None = None
    hint_level: int = Field(default=1, ge=1, le=4)


class TutorResponse(BaseModel):
    answer: str
    teaching_point: str
    hint: str | None = None
    next_question: str | None = None
    cited_moves: list[str] = Field(default_factory=list)
    cited_concepts: list[str] = Field(default_factory=list)


class TutorMessageResponse(BaseModel):
    session_id: str
    intent: TutorIntent
    response: TutorResponse
    checkpoint_id: str
