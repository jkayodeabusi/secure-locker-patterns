import pytest

from app.main import create_app
from secure_patterns.breakmode import BreakMode, BreakModeNotAllowed


def test_refuses_to_start_with_a_check_off_outside_demo_mode():
    with pytest.raises(BreakModeNotAllowed):
        create_app(BreakMode(demo_mode=False, broken=frozenset({"01"})))


def test_break_mode_only_applies_in_demo_mode():
    assert not BreakMode(demo_mode=False, broken=frozenset({"01"})).is_broken("01")
    assert BreakMode(demo_mode=True, broken=frozenset({"01"})).is_broken("1")


def test_secure_by_default():
    assert BreakMode().is_broken("01") is False
