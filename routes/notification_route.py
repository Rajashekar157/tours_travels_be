"""
Notifications API
------------------
Add to your FastAPI app with:

    from notifications_api import router as notifications_router
    app.include_router(notifications_router, prefix="/api")

Assumes you already have a `get_db()` dependency yielding a SQLAlchemy
Session (the standard FastAPI + SQLAlchemy pattern) and that `models.py`
contains the classes from your schema (Notifications, Users, ...).

One-time migration needed (your current `notifications` table only has
title/message — the frontend also wants a type + a click-through link):

    ALTER TABLE notifications ADD COLUMN notification_type VARCHAR(50);
    ALTER TABLE notifications ADD COLUMN link VARCHAR(255);

And add the matching columns to the Notifications model in models.py:

    notification_type: Mapped[Optional[str]] = mapped_column(String(50))
    link: Mapped[Optional[str]] = mapped_column(String(255))
"""

import asyncio
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from core.database import get_db
from models import generated_models as models

router = APIRouter()


def _serialize(n: models.Notifications) -> dict:
    return {
        "id": n.id,
        "type": n.notification_type,
        "message": n.message,
        "link": n.link,
        "read": n.is_read,
        "createdAt": n.created_at.isoformat() if n.created_at else None,
    }


class CreateNotificationBody(BaseModel):
    user_id: int
    title: str
    message: str
    notification_type: str = "test"
    link: str = "/"


@router.post("/notifications")
def create_notification(body: CreateNotificationBody, db: Session = Depends(get_db)):
    """Manual/test creation — lets you insert a notification from Swagger UI
    to verify the frontend picks it up, without waiting on real fleet data."""
    n = models.Notifications(
        user_id=body.user_id,
        title=body.title,
        message=body.message,
        notification_type=body.notification_type,
        link=body.link,
        is_read=False,
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return _serialize(n)


@router.get("/notifications")
def list_notifications(user_id: int = Query(...), db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(models.Notifications)
            .where(models.Notifications.user_id == user_id)
            .order_by(models.Notifications.created_at.desc())
            .limit(50)
        )
        .scalars()
        .all()
    )
    return [_serialize(n) for n in rows]


@router.patch("/notifications/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db)):
    db.execute(
        update(models.Notifications)
        .where(models.Notifications.id == notification_id)
        .values(is_read=True)
    )
    db.commit()
    return {"ok": True}


class MarkAllReadBody(BaseModel):
    user_id: int


@router.patch("/notifications/mark-all-read")
def mark_all_read(body: MarkAllReadBody, db: Session = Depends(get_db)):
    db.execute(
        update(models.Notifications)
        .where(models.Notifications.user_id == body.user_id)
        .where(models.Notifications.is_read.is_(False))
        .values(is_read=True)
    )
    db.commit()
    return {"ok": True}


@router.get("/notifications/stream")
async def stream_notifications(user_id: int = Query(...), db: Session = Depends(get_db)):
    """
    Server-Sent Events endpoint. Polls the DB every few seconds for rows
    newer than the last one seen and pushes them to the browser.

    This is "real-time" in the sense that matters for notifications
    (updates appear within a couple of seconds, no page refresh needed)
    without needing a WebSocket server. For instant (sub-second) push,
    swap the polling loop below for a Postgres LISTEN/NOTIFY listener.
    """

    async def event_generator():
        last_seen = datetime.utcnow() - timedelta(seconds=5)
        while True:
            rows = (
                db.execute(
                    select(models.Notifications)
                    .where(models.Notifications.user_id == user_id)
                    .where(models.Notifications.created_at > last_seen)
                    .order_by(models.Notifications.created_at.asc())
                )
                .scalars()
                .all()
            )

            for n in rows:
                last_seen = n.created_at
                yield f"data: {json.dumps(_serialize(n))}\n\n"

            # heartbeat keeps the connection from being closed by proxies
            yield ": heartbeat\n\n"
            await asyncio.sleep(3)

    return StreamingResponse(event_generator(), media_type="text/event-stream")