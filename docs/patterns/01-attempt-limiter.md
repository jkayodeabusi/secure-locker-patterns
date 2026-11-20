# 01 · Attempt Limiter

> **Caps tries, so brute force and credential stuffing stall.**

| | |
| --- | --- |
| Stage | 1 · At the boundary (ingress) |
| Foundation | Proxy (Gang of Four) |
| Prevents | CWE-307 Improper Restriction of Excessive Authentication Attempts |
| Lives in | [`secure_patterns/boundary/attempt_limiter.py`](../../secure_patterns/boundary/attempt_limiter.py) |
| Used by | `POST /pickup/verify` in [`app/routes/pickup.py`](../../app/routes/pickup.py) |

## The check

```python
count = self.store.incr(key, ttl=self.window)
if count > self.limit and self.enforce:   # the check
    raise TooManyAttempts(retry_after=self.window)
```

Two keys are counted on every attempt: one per **locker** and one per **source IP**.
Counting per locker stops a distributed attack on one victim; counting per source
stops one attacker spraying many lockers.

## Run the demo

```bash
make demo-off PATTERN=01      # terminal 1: server with this check switched off
make attack PATTERN=01        # terminal 2: code found, locker opened

make demo                     # terminal 1: server with every check on
make attack PATTERN=01        # terminal 2: blocked after 5 attempts, HTTP 429
```

## Tests

[`tests/test_01_attempt_limiter.py`](../../tests/test_01_attempt_limiter.py) runs the same
attack twice: it must be **blocked** with the check on, and must **succeed** with the
check off. The second test proves the first one is meaningful.

## Red flag in code review

Login, OTP, password reset or pickup-code endpoints with no limiter, or a limiter
that counts only per IP (defeated by rotating sources) or stores counts in a
per-process dict while running several instances.

The Semgrep rule [`semgrep/01-attempt-limiter.yml`](../../semgrep/01-attempt-limiter.yml)
flags sensitive POST endpoints that never call `limiter.check(...)`.

## Production notes

- Use `RedisCounterStore` when you run more than one instance. Its `INCR` and
  `EXPIRE NX` run in one transaction, so parallel requests can't slip past the limit.
- Pair the limiter with MFA and breached-password checks on login. The limiter
  slows guessing; it doesn't replace strong authentication.
- Behind a proxy, take the client IP from a trusted `X-Forwarded-For` hop only.
