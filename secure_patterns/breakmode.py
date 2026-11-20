"""Break mode: switch off one pattern's check to demonstrate the attack it stops.

Break mode exists only for teaching. It is off unless BOTH are set:
  DEMO_MODE=1
  BREAK_PATTERNS=01,08   (pattern numbers, comma separated)

The application refuses to start if BREAK_PATTERNS is set without DEMO_MODE=1.
Never enable break mode on anything reachable from a network you don't control.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


class BreakModeNotAllowed(RuntimeError):
    """Raised when a check is switched off outside demo mode."""


def _parse(raw: str) -> frozenset[str]:
    return frozenset(p.strip().zfill(2) for p in raw.split(",") if p.strip())


@dataclass(frozen=True)
class BreakMode:
    demo_mode: bool = False
    broken: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def from_env(cls) -> "BreakMode":
        return cls(
            demo_mode=os.environ.get("DEMO_MODE") == "1",
            broken=_parse(os.environ.get("BREAK_PATTERNS", "")),
        )

    def validate(self) -> None:
        if self.broken and not self.demo_mode:
            raise BreakModeNotAllowed(
                "BREAK_PATTERNS is set but DEMO_MODE is not 1. "
                "Refusing to start with security checks switched off."
            )

    def is_broken(self, pattern: str) -> bool:
        """True only when this pattern's check is deliberately switched off in demo mode."""
        return self.demo_mode and pattern.zfill(2) in self.broken


SECURE = BreakMode()
