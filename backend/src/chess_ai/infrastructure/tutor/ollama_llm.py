"""Ollama adapter for local structured tutor responses."""

import json

import httpx

from chess_ai.application.tutor.schemas import TutorIntent, TutorResponse


class OllamaTutorAdapter:
    def __init__(self, base_url: str, model: str) -> None:
        self._url = f"{base_url.rstrip('/')}/api/chat"
        self._model = model

    async def respond(
        self,
        intent: TutorIntent,
        message: str,
        analysis: dict[str, object] | None,
        hint_level: int,
        lesson_context: list[str],
    ) -> TutorResponse:
        prompt = {
            "intent": intent.value,
            "student_message": message,
            "hint_level": hint_level,
            "engine_analysis": analysis,
            "lesson_context": lesson_context,
        }
        system = (
            "You are a patient chess tutor. Stockfish data is authoritative; never invent "
            "evaluations or legal moves. Return only valid JSON with keys: answer, "
            "teaching_point, hint, next_question, cited_moves, cited_concepts."
        )
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                self._url,
                json={
                    "model": self._model,
                    "stream": False,
                    "format": "json",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": json.dumps(prompt)},
                    ],
                },
            )
            response.raise_for_status()
        content = response.json()["message"]["content"]
        return TutorResponse.model_validate_json(content)
