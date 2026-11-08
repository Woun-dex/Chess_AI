"""Learning profile and skill taxonomy endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from chess_ai.application.services.learning_service import SKILLS, get_learning_profile
from chess_ai.infrastructure.db.models.user import UserModel
from chess_ai.presentation.api.dependencies import Session, get_current_user

router = APIRouter(prefix="/api/v1/learning", tags=["Learning"])


class SkillResponse(BaseModel):
    skill_key: str
    name: str
    mastery_score: float
    confidence: float
    evidence_count: int
    trend: str
    status: str


class TaxonomySkillResponse(BaseModel):
    skill_key: str
    name: str
    parent: str


@router.get("/taxonomy", response_model=list[TaxonomySkillResponse])
async def taxonomy() -> list[TaxonomySkillResponse]:
    return [
        TaxonomySkillResponse(skill_key=key, name=str(value["name"]), parent=str(value["parent"]))
        for key, value in SKILLS.items()
    ]


@router.get("/profile", response_model=list[SkillResponse])
async def profile(
    session: Session,
    user: UserModel = Depends(get_current_user),
) -> list[SkillResponse]:
    return [SkillResponse.model_validate(item) for item in await get_learning_profile(session, user.id)]
