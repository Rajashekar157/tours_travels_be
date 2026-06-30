# routes/chat_routes.py
import asyncio
import json
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.chat_sse_manager import chat_sse_manager
from schemas.chat_schema import SendMessageRequest, MessageResponse, ConversationSummary
from services.chat_service import (
    send_message, get_conversation, list_conversations, list_all_users
)
from utils.jwt_handler import get_current_user, decode_access_token

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/users")
def get_users(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_all_users(current_user["user_id"], db)


@router.get("/conversations", response_model=List[ConversationSummary])
def get_conversations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_conversations(current_user["user_id"], db)


@router.get("/conversations/{other_user_id}", response_model=List[MessageResponse])
def get_messages(
    other_user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_conversation(current_user["user_id"], other_user_id, db)


@router.post("/send", response_model=MessageResponse)
async def post_message(
    data: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await send_message(current_user["user_id"], data.receiver_id, data.message, db)


@router.get("/stream")
async def chat_stream(token: str = Query(...)):
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    queue = chat_sse_manager.register(user_id)

    async def event_stream():
        try:
            yield ": connected\n\n"
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"event: message\ndata: {json.dumps(data, default=str)}\n\n"
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            chat_sse_manager.unregister(user_id, queue)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )