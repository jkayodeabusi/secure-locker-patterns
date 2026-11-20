"""The parcel locker service: a small API that hosts all 17 patterns."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routes import pickup
from secure_patterns.boundary import AttemptLimiter, InMemoryCounterStore, TooManyAttempts
from secure_patterns.breakmode import BreakMode


def create_app(break_mode: BreakMode | None = None, limiter: AttemptLimiter | None = None) -> FastAPI:
    break_mode = break_mode or BreakMode.from_env()
    break_mode.validate()  # refuse to start with checks off outside demo mode

    app = FastAPI(title="Secure Locker Patterns", version="0.1.0")
    app.state.break_mode = break_mode
    app.state.limiter = limiter or AttemptLimiter(
        InMemoryCounterStore(),
        limit=5,
        window_seconds=60,
        enforce=not break_mode.is_broken("01"),
    )

    @app.exception_handler(TooManyAttempts)
    async def too_many(_: Request, exc: TooManyAttempts) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={"error": "too many attempts, try again later"},
            headers={"Retry-After": str(exc.retry_after)},
        )

    app.include_router(pickup.router)

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "broken_patterns": sorted(break_mode.broken) if break_mode.demo_mode else []}

    return app


app = create_app()
