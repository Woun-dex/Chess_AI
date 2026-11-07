"""Database-backed lesson retrieval for tutor turns."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from chess_ai.infrastructure.db.models.lesson import LessonModel

CONCEPT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "fork": ("fork", "double attack"),
    "pin": ("pin",),
    "skewer": ("skewer",),
    "pawn": ("pawn structure", "pawn break"),
    "king": ("king safety", "back rank"),
    "endgame": ("endgame",),
}


async def retrieve_lessons(
    session: AsyncSession,
    message: str,
    limit: int = 3,
) -> list[str]:
    lowered = message.lower()
    concepts = [
        concept
        for keyword, matches in CONCEPT_KEYWORDS.items()
        if any(match in lowered for match in matches)
        for concept in (keyword,)
    ]
    if not concepts:
        concepts = ["opening_principles"]
    result = await session.scalars(
        select(LessonModel)
        .where(
            LessonModel.is_published.is_(True),
            or_(*(LessonModel.concept_key == concept for concept in concepts)),
        )
        .order_by(LessonModel.difficulty_level)
        .limit(limit)
    )
    lessons = list(result)
    return [
        f"{lesson.title}: {lesson.description or lesson.content_markdown[:240]}"
        for lesson in lessons
    ] or concepts
