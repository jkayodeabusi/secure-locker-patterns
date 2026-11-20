# Semgrep rule fixture: this endpoint is missing the Attempt Limiter.
from fastapi import APIRouter

router = APIRouter()


# ruleid: sensitive-endpoint-without-attempt-limiter
@router.post("/login")
def login(body: dict):
    return {"ok": True}


# ok: sensitive-endpoint-without-attempt-limiter
@router.post("/otp/verify")
def verify(body: dict, request=None):
    request.app.state.limiter.check("k")
    return {"ok": True}
