from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass

from chess_ai.domain.ports.engine import MoveAnalysisResult


@dataclass(frozen=True)
class TutorContext:
    fen: str
    move_san: str
    move_analysis: MoveAnalysisResult
    player_rating: int = 1200
    student_question: str = ""


class LLMPort(ABC):
    """Port interface for pedagogical AI Tutor explanations."""

    @abstractmethod
    async def explain_move(self, context: TutorContext) -> str:
        """Generate a pedagogical, Socratic coaching explanation for a move."""
        ...

    @abstractmethod
    async def stream_explanation(self, context: TutorContext) -> AsyncIterator[str]:
        """Stream pedagogical coaching tokens in real-time."""
        ...
