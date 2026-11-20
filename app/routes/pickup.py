"""Pickup: a customer enters the six-digit code to open their locker."""
from __future__ import annotations

import hmac

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from app.data import PICKUP_CODES

router = APIRouter(prefix="/pickup", tags=["pickup"])


class VerifyCode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    locker_id: str = Field(pattern=r"^L-\d{4}$")
    code: str = Field(pattern=r"^\d{6}$")


@router.post("/verify")
def verify_code(body: VerifyCode, request: Request) -> dict[str, str]:
    client_ip = request.client.host if request.client else "unknown"
    # Pattern 01: count per locker AND per source, before checking the code.
    request.app.state.limiter.check(f"pickup:locker:{body.locker_id}", f"pickup:ip:{client_ip}")

    expected = PICKUP_CODES.get(body.locker_id)
    if expected is None or not hmac.compare_digest(expected, body.code):
        raise HTTPException(status_code=401, detail="invalid code")
    return {"result": "opened", "locker_id": body.locker_id}
