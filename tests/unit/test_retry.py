from __future__ import annotations

import pytest

from clockify.retry import NO_RETRY
from clockify.retry import CqsKind
from clockify.retry import RetryPolicy
from clockify.retry import compute_delay
from clockify.retry import should_retry


@pytest.mark.parametrize("kind", list(CqsKind))
def test_rate_limit_retries_for_every_kind(kind):
    # Arrange
    policy = RetryPolicy()
    # Act
    result = should_retry(policy, kind, 429, attempt=1)
    # Assert
    assert result is True


@pytest.mark.parametrize("status", [500, 502, 503, 504])
@pytest.mark.parametrize("kind", [CqsKind.QUERY, CqsKind.IDEMPOTENT_COMMAND])
def test_server_errors_retry_for_safe_kinds(status, kind):
    # Arrange
    policy = RetryPolicy()
    # Act
    result = should_retry(policy, kind, status, attempt=0)
    # Assert
    assert result is True


@pytest.mark.parametrize("status", [500, 502, 503, 504])
def test_server_errors_never_retry_non_idempotent_commands(status):
    # Arrange
    policy = RetryPolicy()
    # Act
    result = should_retry(policy, CqsKind.NON_IDEMPOTENT_COMMAND, status, attempt=0)
    # Assert
    assert result is False


@pytest.mark.parametrize("status", [200, 201, 400, 404, 409, 501])
def test_statuses_outside_policy_never_retry(status):
    # Arrange
    policy = RetryPolicy()
    # Act
    result = should_retry(policy, CqsKind.QUERY, status, attempt=0)
    # Assert
    assert result is False


def test_status_in_policy_but_not_in_known_tables_does_not_retry():
    # Arrange
    policy = RetryPolicy(retry_statuses=frozenset({418}))
    # Act
    result = should_retry(policy, CqsKind.QUERY, 418, attempt=0)
    # Assert
    assert result is False


@pytest.mark.parametrize("attempt", [3, 4, 10])
def test_exhausted_attempts_never_retry(attempt):
    # Arrange
    policy = RetryPolicy(max_attempts=3)
    # Act
    result = should_retry(policy, CqsKind.QUERY, 429, attempt=attempt)
    # Assert
    assert result is False


def test_compute_delay_honors_retry_after():
    # Arrange
    policy = RetryPolicy(random_source=lambda: 1.0)
    # Act
    delay = compute_delay(policy, attempt=0, retry_after=7.5)
    # Assert
    assert delay == pytest.approx(7.5)


def test_compute_delay_ignores_retry_after_when_policy_disables_it():
    # Arrange
    policy = RetryPolicy(respect_retry_after=False, random_source=lambda: 1.0)
    # Act
    delay = compute_delay(policy, attempt=0, retry_after=7.5)
    # Assert
    assert delay == pytest.approx(0.5)


@pytest.mark.parametrize(("attempt", "expected"), [(0, 0.5), (1, 1.0), (2, 2.0), (3, 4.0)])
def test_compute_delay_exponential_backoff(attempt, expected):
    # Arrange
    policy = RetryPolicy(random_source=lambda: 1.0)
    # Act
    delay = compute_delay(policy, attempt=attempt, retry_after=None)
    # Assert
    assert delay == pytest.approx(expected)


def test_compute_delay_is_bounded_by_max_backoff():
    # Arrange
    policy = RetryPolicy(max_backoff=3.0, random_source=lambda: 1.0)
    # Act
    delay = compute_delay(policy, attempt=20, retry_after=None)
    # Assert
    assert delay == pytest.approx(3.0)


def test_compute_delay_applies_full_jitter():
    # Arrange
    policy = RetryPolicy(random_source=lambda: 0.25)
    # Act
    delay = compute_delay(policy, attempt=2, retry_after=None)
    # Assert
    assert delay == pytest.approx(0.5)


def test_default_random_source_is_used_and_bounded():
    # Arrange
    policy = RetryPolicy(max_backoff=1.0)
    # Act
    delay = compute_delay(policy, attempt=10, retry_after=None)
    # Assert
    assert 0.0 <= delay <= 1.0


def test_no_retry_constant():
    # Arrange
    policy = NO_RETRY
    # Act
    result = should_retry(policy, CqsKind.QUERY, 429, attempt=1)
    # Assert
    assert policy.max_attempts == 1
    assert result is False


def test_policy_is_frozen():
    # Arrange
    policy = RetryPolicy()
    # Act
    with pytest.raises(AttributeError) as excinfo:
        policy.max_attempts = 9
    # Assert
    assert isinstance(excinfo.value, AttributeError)
