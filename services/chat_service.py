# services/chat_service.py
from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session

from models.generated_models import Messages, Users
from core.chat_sse_manager import chat_sse_manager


async def send_message(sender_id: int, receiver_id: int, message: str, db: Session) -> Messages:
    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")

    receiver = db.query(Users).filter(Users.id == receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Recipient not found")

    msg = Messages(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    payload = {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id,
        "message": msg.message,
        "is_read": msg.is_read,
        "created_at": msg.created_at.isoformat(),
    }

    # Push to receiver's open tabs in real time
    await chat_sse_manager.push_to_user(receiver_id, payload)
    # Also echo to sender's other open tabs, so multi-tab stays in sync
    await chat_sse_manager.push_to_user(sender_id, payload)

    return msg


def get_conversation(user_id: int, other_user_id: int, db: Session) -> List[Messages]:
    messages = (
        db.query(Messages)
        .filter(
            or_(
                and_(Messages.sender_id == user_id, Messages.receiver_id == other_user_id),
                and_(Messages.sender_id == other_user_id, Messages.receiver_id == user_id),
            )
        )
        .order_by(Messages.created_at.asc())
        .all()
    )

    # Mark messages sent TO the current user as read
    db.query(Messages).filter(
        Messages.sender_id == other_user_id,
        Messages.receiver_id == user_id,
        Messages.is_read == False,
    ).update({"is_read": True})
    db.commit()

    return messages


def list_conversations(user_id: int, db: Session) -> list:
    """
    Returns one row per other user the current user has exchanged
    messages with, with the latest message and unread count.
    """
    subq = (
        db.query(
            func.greatest(Messages.sender_id, Messages.receiver_id).label("user_a"),
            func.least(Messages.sender_id, Messages.receiver_id).label("user_b"),
            Messages.id,
            Messages.sender_id,
            Messages.receiver_id,
            Messages.message,
            Messages.created_at,
            Messages.is_read,
        )
        .filter(or_(Messages.sender_id == user_id, Messages.receiver_id == user_id))
        .subquery()
    )

    all_msgs = (
        db.query(Messages)
        .filter(or_(Messages.sender_id == user_id, Messages.receiver_id == user_id))
        .order_by(Messages.created_at.desc())
        .all()
    )

    seen = {}
    unread_counts = {}

    for m in all_msgs:
        other_id = m.receiver_id if m.sender_id == user_id else m.sender_id
        if other_id not in seen:
            seen[other_id] = m
        if m.receiver_id == user_id and not m.is_read:
            unread_counts[other_id] = unread_counts.get(other_id, 0) + 1

    results = []
    for other_id, last_msg in seen.items():
        other_user = db.query(Users).filter(Users.id == other_id).first()
        if not other_user:
            continue
        results.append({
            "user_id": other_user.id,
            "full_name": other_user.full_name,
            "mobile": other_user.mobile,
            "last_message": last_msg.message,
            "last_message_at": last_msg.created_at,
            "unread_count": unread_counts.get(other_id, 0),
        })

    results.sort(key=lambda x: x["last_message_at"], reverse=True)
    return results


def list_all_users(current_user_id: int, db: Session) -> list:
    """For starting a new chat — everyone except yourself."""
    users = db.query(Users).filter(Users.id != current_user_id, Users.is_active == True).all()
    return [
        {"id": u.id, "full_name": u.full_name, "mobile": u.mobile}
        for u in users
    ]