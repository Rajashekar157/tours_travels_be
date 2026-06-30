# schemas/chat_schema.py
from pydantic import BaseModel
import datetime


class SendMessageRequest(BaseModel):
    receiver_id: int
    message: str


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    message: str
    is_read: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    user_id: int
    full_name: str
    mobile: str | None = None
    last_message: str
    last_message_at: datetime.datetime
    unread_count: int