from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from services import settings_service
from schemas.settings_schema import UpdateProfileRequest, ChangePasswordRequest

router = APIRouter(prefix="/settings", tags=["Settings"])


# ── Profile ──────────────────────────────────

@router.get("/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    return settings_service.get_profile(db, user_id)


@router.put("/profile/{user_id}")
def update_profile(
    user_id: int,
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
):
    return settings_service.update_profile(db, user_id, payload)


# ── Password ─────────────────────────────────

@router.put("/change-password/{user_id}")
def change_password(
    user_id: int,
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
):
    return settings_service.change_password(db, user_id, payload)


# ── Notifications toggle ──────────────────────

@router.get("/notifications/{user_id}")
def get_notifications(user_id: int, db: Session = Depends(get_db)):
    return settings_service.get_notifications(db, user_id)


@router.put("/notifications/{user_id}/read/{notif_id}")
def mark_notification_read(
    user_id: int,
    notif_id: int,
    db: Session = Depends(get_db),
):
    return settings_service.mark_notification_read(db, user_id, notif_id)


@router.put("/notifications/{user_id}/read-all")
def mark_all_notifications_read(user_id: int, db: Session = Depends(get_db)):
    return settings_service.mark_all_read(db, user_id)


# ── App info ─────────────────────────────────

@router.get("/app-info")
def get_app_info():
    return settings_service.get_app_info()