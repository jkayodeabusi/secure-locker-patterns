"""Pattern 01 · Attempt Limiter: prove the check fires, and prove the attack test works."""
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from secure_patterns.boundary import AttemptLimiter, InMemoryCounterStore, TooManyAttempts
from secure_patterns.breakmode import BreakMode


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


# --- unit tests -------------------------------------------------------------

def test_allows_up_to_the_limit_then_refuses():
    limiter = AttemptLimiter(InMemoryCounterStore(), limit=5, window_seconds=60)
    for _ in range(5):
        limiter.check("k")
    with pytest.raises(TooManyAttempts) as exc:
        limiter.check("k")
    assert exc.value.retry_after == 60


def test_window_resets_after_expiry():
    clock = FakeClock()
    limiter = AttemptLimiter(InMemoryCounterStore(clock=clock), limit=2, window_seconds=60)
    limiter.check("k"); limiter.check("k")
    clock.t = 61
    limiter.check("k")  # new window, allowed


def test_any_key_over_the_limit_refuses():
    limiter = AttemptLimiter(InMemoryCounterStore(), limit=1, window_seconds=60)
    limiter.check("account", "ip-a")
    with pytest.raises(TooManyAttempts):
        limiter.check("account", "ip-b")  # new source, same account: still refused


# --- attack tests: same attack, check on vs off ------------------------------

def guess_codes(client, max_guesses=200):
    for n in range(max_guesses):
        r = client.post("/pickup/verify", json={"locker_id": "L-1042", "code": f"{n:06d}"})
        if r.status_code in (200, 429):
            return r.status_code, n
    return None, max_guesses


def test_attack_is_blocked_when_check_is_on():
    client = TestClient(create_app(BreakMode()))
    status, wrong_guesses = guess_codes(client)
    assert status == 429
    assert wrong_guesses == 5


def test_attack_succeeds_when_check_is_off():
    """Proves the attack test is real: with the check switched off, the locker opens."""
    client = TestClient(create_app(BreakMode(demo_mode=True, broken=frozenset({"01"}))))
    status, _ = guess_codes(client)
    assert status == 200


def test_correct_code_still_works_for_the_real_customer():
    client = TestClient(create_app(BreakMode()))
    r = client.post("/pickup/verify", json={"locker_id": "L-1042", "code": "000137"})
    assert r.status_code == 200
