# Secure Locker Patterns

**17 code-level security design patterns, each with an attack you can switch on and off.**

A small parcel locker API that implements every pattern from the *Security Design Patterns:
Code-Level Catalog*. Each pattern lives once in a shared library, `secure_patterns/`, guards a
real feature of the app, and ships with an attack script and tests that prove its check fires.

The hook is **break mode**: switch one pattern's check off and watch the same attack succeed.

```bash
make demo-off PATTERN=01 && make attack PATTERN=01   # OPENED L-1042 after 138 guesses
make demo               && make attack PATTERN=01   # BLOCKED after 5 wrong guesses: HTTP 429
```

## Quick start

```bash
git clone https://github.com/jkayodeabusi/secure-locker-patterns.git
cd secure-locker-patterns
python3 -m venv .venv && source .venv/bin/activate   # Python 3.12, 3.13 or 3.14
make install
make test            # every pattern: attack blocked with the check on, succeeds with it off
make demo            # terminal 1: the API on 127.0.0.1:8000, every check on
make attack PATTERN=01   # terminal 2
```

## The four stages

A request meets the patterns in this order:

1. **At the boundary (ingress):** should this request be processed? Patterns 01 to 07.
2. **Inside business logic:** reach data and secrets safely. Patterns 08 to 13.
3. **On the way out (egress):** control what leaves the component. Patterns 14 to 16.
4. **At construction:** before any request arrives. Pattern 17.

## The 17 patterns

| # | Pattern | Stage | Feature | Attack it stops | Status |
|---|---|---|---|---|---|
| 01 | [Attempt Limiter](docs/patterns/01-attempt-limiter.md) | 1 | Pickup code check | Guess all codes until the locker opens | ✅ Built |
| 02 | Signed Request Verifier | 1 | Courier status webhook | Forged and replayed "delivered" events | Planned |
| 03 | Authentication Enforcer | 1 | Middleware on every API route | Unsigned or wrong-audience token accepted | Planned |
| 04 | Secure Session Manager | 1 | Customer portal login | Session fixation; a session that never expires | Planned |
| 05 | Intercepting Validator | 1 | Reschedule delivery request | Extra fields and negative values accepted | Planned |
| 06 | Safe Deserializer | 1 | Courier event queue consumer | Unknown event type processed | Planned |
| 07 | Authorization Enforcer | 1 | Admin: delete a locker | Customer deletes a locker; route with no rule ships | Planned |
| 08 | Scoped Repository | 2 | Get parcel by ID | Changing the ID returns someone else's parcel | Planned |
| 09 | Parameterized Command | 2 | Locker search; label printing | SQL injection via sort; shell injection via file name | Planned |
| 10 | Capability Token | 2 | Proof-of-delivery download link | Edited or expired link still works | Planned |
| 11 | Upgradable Password Hasher | 2 | User store moving to Argon2id | Any password accepted; old hashes never upgraded | Planned |
| 12 | Crypto Facade | 2 | Customer address encrypted at rest | Reused nonce; tampered ciphertext accepted | Planned |
| 13 | Secret Value Type | 2 | Database and webhook secrets | Secret printed in logs | Planned |
| 14 | Context-Aware Output Encoder | 3 | Delivery note in portal; CSV export | Stored XSS; spreadsheet formula injection | Planned |
| 15 | Fail-Secure Error Handler | 3 | Global error boundary | Stack trace leaked; forbidden vs missing distinguishable | Planned |
| 16 | Secure Logger | 3 | Audit events | Token logged; forged log line via newline | Planned |
| 17 | Secure Defaults Builder | 4 | Courier API client; cookies | TLS verification off; request with no timeout | Planned |

## Every pattern ships with

- A module in `secure_patterns/`, wired into a real feature of the app
- A break-mode switch that turns off only that pattern's check
- An attack script in `attacks/`, runnable with one command
- Two tests: the attack is **blocked** with the check on, and **succeeds** with it off
- A Semgrep rule, where the red flag can be found by matching code
- A doc page in `docs/patterns/`: one-liner, stage, CWE, foundation, red flag

## Break mode is demo-only

Break mode needs **both** `DEMO_MODE=1` and `BREAK_PATTERNS=<numbers>`. The app refuses to
start if a check is switched off without `DEMO_MODE=1`, the Makefile binds it to `127.0.0.1`,
and attack scripts refuse any target that isn't local. All data and secrets are fake.
See [SECURITY.md](SECURITY.md).

## CI

Every push and pull request runs the tests, the Semgrep house rules, dependency review and
CodeQL. Every GitHub Action is pinned to a full commit SHA, and Dependabot keeps those pins
current.

## Learn more

- *Security Design Patterns: Code-Level Catalog*, the study guide behind this repo
- *The Secure Request Line*, an interactive companion that animates a request through all 17 patterns
- YouTube: [@SecureTechWithJKA](https://www.youtube.com/@SecureTechWithJKA)

## Author

**John Kayode-Abusi** · Cybersecurity Engineering Practitioner | Security across AI, Cloud,
Product, Platform, Infrastructure and ERP
[LinkedIn](https://www.linkedin.com/in/johnkayode-abusi) · [YouTube](https://www.youtube.com/@SecureTechWithJKA)

Licensed under MIT.
