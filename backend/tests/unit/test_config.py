import pytest
from pydantic import ValidationError

from chess_ai.config import Settings


def test_development_allows_local_auth_secret() -> None:
    settings = Settings(APP_ENV="development")

    assert settings.AUTH_SECRET == "change-this-development-secret"


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_deployed_environments_reject_default_auth_secret(environment: str) -> None:
    with pytest.raises(ValidationError, match="AUTH_SECRET must be explicitly configured"):
        Settings(APP_ENV=environment)


@pytest.mark.parametrize("environment", ["staging", "production"])
def test_deployed_environments_require_long_auth_secret(environment: str) -> None:
    with pytest.raises(ValidationError, match="at least 32 characters"):
        Settings(APP_ENV=environment, AUTH_SECRET="too-short-secret")


def test_deployed_environment_accepts_configured_auth_secret() -> None:
    settings = Settings(APP_ENV="production", AUTH_SECRET="a" * 32)

    assert settings.AUTH_SECRET == "a" * 32
