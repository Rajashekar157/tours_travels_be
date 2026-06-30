import asyncio
import json

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.sse_manager import sse_manager
from schemas.auth_schema import LoginRequest
from services.auth_service import login_user, logout_user
from utils.jwt_handler import get_current_user, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    return await login_user(data, db)


@router.post("/logout")
def logout(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return logout_user(current_user["user_id"], db)


@router.get("/session-events")
async def session_events(token: str = Query(...)):
    payload = decode_access_token(token)
    jti = payload.get("jti")

    queue = sse_manager.register(jti)

    async def event_stream():
        try:
            yield ": connected\n\n"
            while True:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"event: session\ndata: {json.dumps({'status': message})}\n\n"
                    if message == "evicted":
                        break
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            sse_manager.unregister(jti)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )