"""Skill taxonomy and measurable learning-profile calculations."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime
from math import exp

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chess_ai.infrastructure.db.models.learning_profile import LearningProfileModel
from chess_ai.infrastructure.db.models.skill_evidence import SkillEvidenceModel

SKILLS: dict[str, dict[str, object]] = {
    "tactics.fork": {"name": "Forks", "parent": "tactics"},
    "tactics.pin": {"name": "Pins", "parent": "tactics"},
    "tactics.skewer": {"name": "Skewers", "parent": "tactics"},
    "tactics.calculation": {"name": "Calculation", "parent": "tactics"},
    "strategy.pawn_structure": {"name": "Pawn structure", "parent": "strategy"},
    "strategy.king_safety": {"name": "King safety", "parent": "strategy"},
    "endgame.king_activity": {"name": "King activity", "parent": "endgame"},
    "endgame.conversion": {"name": "Conversion", "parent": "endgame"},
}

MOTIF_TO_SKILL = {
    "fork": "tactics.fork",
    "pin": "tactics.pin",
    "skewer": "tactics.skewer",
    "back_rank": "strategy.king_safety",
    "king_safety": "strategy.king_safety",
    "pawn_structure": "strategy.pawn_structure",
    "king_activity": "endgame.king_activity",
}


def calculate_mastery(evidence: Iterable[SkillEvidenceModel], now: datetime | None = None) -> tuple[float, float, str]:
    """Return bounded mastery, confidence, and trend from append-only evidence."""
    reference = now or datetime.now(UTC)
    evidence_items = list(evidence)
    weighted_success = 2.0
    weighted_attempts = 4.0
    recent_score = []
    historical_score = []
    for item in evidence_items:
        age_days = max(0.0, (reference - item.occurred_at).total_seconds() / 86400)
        weight = item.signal_strength * exp(-age_days / 45)
        success = 1.0 if item.outcome == "success" else 0.5 if item.outcome == "partial" else 0.0
        weighted_success += weight * success
        weighted_attempts += weight
        (recent_score if age_days <= 45 else historical_score).append(success)
    mastery = round(max(0.0, min(100.0, weighted_success / weighted_attempts * 100)), 1)
    confidence = round(min(1.0, len(evidence_items) / 12), 2)
    recent = sum(recent_score) / len(recent_score) if recent_score else None
    historical = sum(historical_score) / len(historical_score) if historical_score else None
    trend = "stable" if recent is None or historical is None else (
        "improving" if recent > historical + 0.1 else "declining" if recent < historical - 0.1 else "stable"
    )
    return mastery, confidence, trend


async def get_learning_profile(session: AsyncSession, user_id: str) -> list[dict[str, object]]:
    profiles = list(await session.scalars(
        select(LearningProfileModel).where(LearningProfileModel.user_id == user_id)
    ))
    result = []
    for profile in profiles:
        evidence = list(await session.scalars(select(SkillEvidenceModel).where(
            SkillEvidenceModel.user_id == user_id,
            SkillEvidenceModel.skill_key == profile.concept_key,
        ).order_by(SkillEvidenceModel.occurred_at)))
        mastery, confidence, trend = calculate_mastery(evidence)
        result.append({
            "skill_key": profile.concept_key,
            "name": SKILLS.get(profile.concept_key, {}).get("name", profile.concept_key),
            "mastery_score": mastery,
            "confidence": confidence,
            "evidence_count": len(evidence),
            "trend": trend,
            "status": "weakness" if confidence >= 0.25 and mastery < 65 else "developing" if mastery < 80 else "strong",
        })
    return sorted(result, key=lambda item: float(item["mastery_score"]))


async def record_skill_evidence(
    session: AsyncSession,
    *,
    user_id: str,
    skill_key: str,
    source_type: str,
    source_id: str,
    outcome: str,
    signal_strength: float = 1.0,
    metadata: dict[str, object] | None = None,
) -> SkillEvidenceModel:
    if skill_key not in SKILLS:
        raise ValueError(f"Unknown skill: {skill_key}")
    if outcome not in {"success", "partial", "failure"}:
        raise ValueError(f"Unknown outcome: {outcome}")
    evidence = SkillEvidenceModel(
        user_id=user_id, skill_key=skill_key, source_type=source_type, source_id=source_id,
        outcome=outcome, signal_strength=max(0.1, min(signal_strength, 3.0)),
        metadata_json=metadata or {},
    )
    session.add(evidence)
    profile = await session.scalar(select(LearningProfileModel).where(
        LearningProfileModel.user_id == user_id,
        LearningProfileModel.concept_key == skill_key,
    ))
    if profile is None:
        profile = LearningProfileModel(user_id=user_id, concept_key=skill_key)
        session.add(profile)
    profile.total_attempts += 1
    profile.exposures += 1
    if outcome == "success":
        profile.correct_attempts += 1
    profile.last_practiced_at = evidence.occurred_at or datetime.now(UTC)
    await session.flush()
    return evidence
