from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from chess_ai.application.services.learning_service import calculate_mastery


def evidence(outcome: str, days_old: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        outcome=outcome,
        signal_strength=1.0,
        occurred_at=datetime.now(UTC) - timedelta(days=days_old),
    )


def test_mastery_is_bounded_and_confidence_grows_with_evidence() -> None:
    mastery, confidence, trend = calculate_mastery(
        [evidence("success") for _ in range(12)],
    )

    assert mastery <= 100
    assert confidence == 1
    assert trend == "stable"


def test_recent_success_after_historical_failures_is_improving() -> None:
    mastery, _, trend = calculate_mastery(
        [evidence("failure", days_old=90) for _ in range(4)]
        + [evidence("success") for _ in range(4)],
    )

    assert 0 < mastery < 100
    assert trend == "improving"


def test_unknown_outcomes_do_not_count_as_success() -> None:
    mastery, _, _ = calculate_mastery([evidence("failure"), evidence("partial")])

    assert mastery < 50
