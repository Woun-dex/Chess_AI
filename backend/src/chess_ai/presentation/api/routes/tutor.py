"""Authenticated tutor session endpoints."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from chess_ai.application.services.lesson_service import retrieve_lessons
from chess_ai.application.tutor.schemas import (
    TutorMessageRequest,
    TutorMessageResponse,
    TutorResponse,
)
from chess_ai.application.tutor.state import TutorState
from chess_ai.infrastructure.db.models.tutor_checkpoint import TutorCheckpointModel
from chess_ai.infrastructure.db.models.tutor_session import (
    MessageRole,
    TutorMessageModel,
    TutorSessionModel,
)
from chess_ai.infrastructure.db.models.user import UserModel
from chess_ai.infrastructure.tutor.graph import run_tutor_turn
from chess_ai.presentation.api.dependencies import Session, get_current_user

router = APIRouter(prefix="/api/v1/tutor", tags=["Tutor"])
CurrentUser = Annotated[UserModel, Depends(get_current_user)]


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(
    session: Session,
    user: CurrentUser,
) -> dict[str, str]:
    tutor_session = TutorSessionModel(user_id=user.id)
    session.add(tutor_session)
    await session.commit()
    await session.refresh(tutor_session)
    return {"session_id": tutor_session.id}


@router.post(
    "/sessions/{session_id}/messages",
    response_model=TutorMessageResponse,
)
async def send_message(
    session_id: str,
    request: TutorMessageRequest,
    session: Session,
    user: CurrentUser,
) -> TutorMessageResponse:
    tutor_session = await session.scalar(
        select(TutorSessionModel).where(
            TutorSessionModel.id == session_id,
            TutorSessionModel.user_id == user.id,
            TutorSessionModel.is_active.is_(True),
        )
    )
    if tutor_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutor session not found")

    student_message = TutorMessageModel(
        session_id=session_id,
        role=MessageRole.STUDENT,
        content=request.message,
        fen_context=request.fen,
    )
    session.add(student_message)
    await session.flush()

    state: TutorState = {
        "user_id": user.id,
        "session_id": session_id,
        "student_message": request.message,
        "fen": request.fen,
        "game_id": request.game_id,
        "hint_level": request.hint_level,
        "lesson_context": await retrieve_lessons(session, request.message),
    }
    try:
        result = await run_tutor_turn(state)
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except OSError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chess analysis is currently unavailable",
        ) from exc

    response = result["response"]
    tutor_message = TutorMessageModel(
        session_id=session_id,
        role=MessageRole.TUTOR,
        content=response.answer,
        fen_context=request.fen,
    )
    session.add(tutor_message)
    await session.flush()
    checkpoint = TutorCheckpointModel(
        session_id=session_id,
        state={
            "user_id": user.id,
            "session_id": session_id,
            "student_message": request.message,
            "fen": request.fen,
            "game_id": request.game_id,
            "hint_level": request.hint_level,
            "intent": result["intent"].value,
            "lesson_context": result.get("lesson_context", []),
            "response": response.model_dump(),
        },
    )
    session.add(checkpoint)
    await session.flush()
    await session.commit()

    return TutorMessageResponse(
        session_id=session_id,
        intent=result["intent"],
        response=TutorResponse.model_validate(response),
        checkpoint_id=checkpoint.id,
    )


@router.post("/sessions/{session_id}/messages/stream")
async def stream_message(
    session_id: str,
    request: TutorMessageRequest,
    session: Session,
    user: CurrentUser,
) -> StreamingResponse:
    response = await send_message(session_id, request, session, user)

    async def events() -> AsyncIterator[str]:
        yield f"event: started\ndata: {json.dumps({'session_id': session_id})}\n\n"
        words = response.response.answer.split(" ")
        for index, word in enumerate(words):
            yield f"event: token\ndata: {json.dumps({'text': word + (' ' if index < len(words) - 1 else '')})}\n\n"
            await asyncio.sleep(0)
        yield (f"event: complete\ndata: {response.model_dump_json()}\n\n")

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
