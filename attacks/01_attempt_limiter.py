"""Attack 01: guess a locker's six-digit pickup code.

Run against a local server:
  make attack PATTERN=01 MODE=on    # expect: blocked after 5 attempts (HTTP 429)
  make attack PATTERN=01 MODE=off   # expect: code found, locker opened

Demo only. Point it at your own local server, never at a system you don't own.
"""
from __future__ import annotations

import os
import sys

import httpx

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")
LOCKER = "L-1042"
MAX_GUESSES = 1000


def main() -> int:
    if not BASE_URL.startswith(("http://127.0.0.1", "http://localhost")):
        print("Refusing: this demo attack only targets a local server.")
        return 2
    with httpx.Client(base_url=BASE_URL, timeout=5) as client:
        for n in range(MAX_GUESSES):
            code = f"{n:06d}"
            r = client.post("/pickup/verify", json={"locker_id": LOCKER, "code": code})
            if r.status_code == 429:
                print(f"BLOCKED after {n} wrong guesses: HTTP 429, Retry-After {r.headers.get('Retry-After')}s")
                print("Attempt Limiter is ON. Brute force stalled.")
                return 0
            if r.status_code == 200:
                print(f"OPENED {LOCKER} with code {code} after {n + 1} guesses.")
                print("Attempt Limiter is OFF. Nothing stopped the guessing.")
                return 1
    print(f"No result after {MAX_GUESSES} guesses.")
    return 3


if __name__ == "__main__":
    sys.exit(main())
