"""Deterministic tutor adapter used until a real LLM provider is configured."""

from collections.abc import AsyncIterator

from chess_ai.application.tutor.schemas import TutorIntent, TutorResponse
from chess_ai.domain.ports.llm import LLMPort, TutorContext


class MockTutorAdapter(LLMPort):
    """Produces predictable, engine-grounded teaching responses."""

    async def explain_move(self, context: TutorContext) -> str:
        return (
            f"Stockfish evaluated {context.move_san} as "
            f"{context.move_analysis.classification.value}. "
            "Look first at the checks, captures, and threats in the position."
        )

    def stream_explanation(self, context: TutorContext) -> AsyncIterator[str]:
        async def stream() -> AsyncIterator[str]:
            yield await self.explain_move(context)

        return stream()

    async def respond(
        self,
        intent: TutorIntent,
        message: str,
        analysis: dict[str, object] | None,
        hint_level: int,
        lesson_context: list[str],
    ) -> TutorResponse:
        """Return a structured response without network calls or randomness."""
        best_move = str(analysis.get("best_move_uci", "")) if analysis else ""
        concepts = lesson_context or ["checks, captures, and threats"]
        if intent == TutorIntent.HINT:
            hints = {
                1: "What forcing moves can you find for either side?",
                2: f"Start by examining the move {best_move or 'that changes the tension'} carefully.",
                3: "Compare your candidate with the engine's principal variation.",
                4: f"The engine's leading move is {best_move or 'not available'}; now explain why.",
            }
            return TutorResponse(
                answer=hints[hint_level],
                teaching_point="Strong players examine forcing moves before quiet plans.",
                hint=hints[min(hint_level + 1, 4)] if hint_level < 4 else None,
                next_question="Which checks, captures, or threats did you consider?",
                cited_moves=[best_move] if best_move else [],
                cited_concepts=concepts,
            )
        if intent == TutorIntent.LESSON:
            return TutorResponse(
                answer=f"Let's connect this position to {concepts[0]}. "
                "Identify the pieces that create the immediate threat before calculating variations.",
                teaching_point="Name the chess concept before memorizing a move.",
                next_question="What is the opponent threatening?",
                cited_concepts=concepts,
            )
        return TutorResponse(
            answer=(
                f"I checked the position while considering your question: {message} "
                f"The engine's leading continuation is {best_move or 'not available'}."
            ),
            teaching_point="Use the engine line as evidence, then explain the idea in your own words.",
            next_question="What changed in the position after the candidate move?",
            cited_moves=[best_move] if best_move else [],
            cited_concepts=concepts,
        )
