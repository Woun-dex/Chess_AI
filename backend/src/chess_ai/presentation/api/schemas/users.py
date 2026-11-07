"""User and profile HTTP schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from chess_ai.infrastructure.db.models.player_profile import PlayerProfileModel, PreferredColor


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    preferred_color: str
    classical_rating: int
    blitz_rating: int
    rapid_rating: int
    games_played: int
    wins: int
    losses: int
    draws: int
    favorite_opening_as_white: str | None
    favorite_opening_as_black: str | None

    @classmethod
    def from_model(cls, profile: PlayerProfileModel) -> ProfileResponse:
        return cls.model_validate(profile, from_attributes=True)


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    profile: ProfileResponse


class ProfileUpdateRequest(BaseModel):
    preferred_color: PreferredColor | None = None
    favorite_opening_as_white: str | None = Field(default=None, max_length=100)
    favorite_opening_as_black: str | None = Field(default=None, max_length=100)
