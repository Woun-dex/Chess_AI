"""LangGraph tutor workflow."""

from __future__ import annotations

from typing import cast

import chess
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from chess_ai.application.tutor.schemas import TutorIntent
from chess_ai.application.tutor.state import TutorState
from chess_ai.config import get_settings
from chess_ai.infrastructure.engine.stockfish_adapter import StockfishAdapter
from chess_ai.infrastructure.tutor.mock_llm import MockTutorAdapter
from chess_ai.infrastructure.tutor.ollama_llm import OllamaTutorAdapter


def _route_intent(state: TutorState) -> dict[str, TutorIntent]:
    message = state["student_message"].lower()
    if any(word in message for word in ("hint", "clue", "help me find")):
        intent = TutorIntent.HINT
    elif any(word in message for word in ("lesson", "teach", "what is", "concept")):
        intent = TutorIntent.LESSON
    elif any(word in message for word in ("summary", "review", "game")):
        intent = TutorIntent.GAME_SUMMARY
    else:
        intent = TutorIntent.EXPLAIN_POSITION
    return {"intent": intent}


async def _analyze_position(state: TutorState) -> dict[str, object | None]:
    fen = state.get("fen")
    if not fen:
        return {"engine_analysis": None}
    chess.Board(fen)
    engine = StockfishAdapter(
        get_settings().STOCKFISH_PATH,
        threads=get_settings().STOCKFISH_ANALYSIS_THREADS,
    )
    try:
        evaluation = await engine.evaluate_position(fen, depth=12, multipv=3)
        return {
            "engine_analysis": {
                "fen": evaluation.fen,
                "centipawns": evaluation.centipawns,
                "mate_in": evaluation.mate_in,
                "best_move_uci": evaluation.best_move_uci,
                "pv": evaluation.pv,
            }
        }
    finally:
        await engine.close()


def _retrieve_lessons(state: TutorState) -> dict[str, list[str]]:
    if state.get("lesson_context"):
        return {"lesson_context": state["lesson_context"]}
    message = state["student_message"].lower()
    concepts = ["checks, captures, and threats"]
    if "fork" in message:
        concepts = ["knight forks", "double attacks"]
    elif "pin" in message:
        concepts = ["pins", "piece mobility"]
    elif "pawn" in message:
        concepts = ["pawn structure", "pawn breaks"]
    return {"lesson_context": concepts}


async def _generate_response(state: TutorState) -> dict[str, object]:
    settings = get_settings()
    adapter = (
        OllamaTutorAdapter(settings.LLM_BASE_URL, settings.LLM_MODEL_NAME)
        if settings.LLM_PROVIDER == "ollama"
        else MockTutorAdapter()
    )
    response = await adapter.respond(
        intent=state["intent"],
        message=state["student_message"],
        analysis=state.get("engine_analysis"),
        hint_level=state.get("hint_level", 1),
        lesson_context=state.get("lesson_context", []),
    )
    return {"response": response}


def build_tutor_graph() -> CompiledStateGraph[TutorState, None, TutorState, TutorState]:
    graph = StateGraph(TutorState)
    graph.add_node("route_intent", _route_intent)
    graph.add_node("analyze_position", _analyze_position)
    graph.add_node("retrieve_lessons", _retrieve_lessons)
    graph.add_node("generate_response", _generate_response)
    graph.add_edge(START, "route_intent")
    graph.add_edge("route_intent", "analyze_position")
    graph.add_edge("analyze_position", "retrieve_lessons")
    graph.add_edge("retrieve_lessons", "generate_response")
    graph.add_edge("generate_response", END)
    return graph.compile()


tutor_graph = build_tutor_graph()


async def run_tutor_turn(state: TutorState) -> TutorState:
    result = await tutor_graph.ainvoke(state)
    return cast(TutorState, result)
