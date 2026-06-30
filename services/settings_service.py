from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
import bcrypt

from models.generated_models import Users, Notifications
from schemas.settings_schema import UpdateProfileRequest, ChangePasswordRequest


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _fmt_dt(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.strftime("%d %b %Y, %I:%M %p")
    return str(val)


def _branch_name(branch):
    """MasterBranch's display-name column isn't known for certain here —
    try the common possibilities so this doesn't break if the column is
    named differently than expected."""
    if branch is None:
        return None
    for attr in ("branch_name", "name", "title"):
        val = getattr(branch, attr, None)
        if val:
            return val
    return None


# ─────────────────────────────────────────────
# Profile
# ─────────────────────────────────────────────

def get_profile(db: Session, user_id: int):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id":               user.id,
        "full_name":        user.full_name,
        "email":            user.email,
        "mobile":           user.mobile,
        "mobile_verified":  user.mobile_verified,
        "photo_url":        user.photo_url,
        "is_active":        user.is_active,
        "is_blocked":       user.is_blocked,
        "status":           user.status,
        "role":             user.role.role_name if user.role else None,
        "role_id":          user.role_id,
        "staff_code":       user.staff_code,
        "designation":      user.designation,
        "service_state":    user.service_state,
        "branch_id":        user.branch_id,
        "branch_name":      _branch_name(user.branch),
        "address":          user.address,
        "city":             user.city,
        "pincode":          user.pincode,
        "last_login":       _fmt_dt(user.last_login),
        "created_at":       _fmt_dt(user.created_at),
        "updated_at":       _fmt_dt(user.updated_at),
    }


def update_profile(db: Session, user_id: int, payload: UpdateProfileRequest):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.email is not None:
        # Check uniqueness
        existing = db.query(Users).filter(
            Users.email == payload.email, Users.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = payload.email
    if payload.mobile is not None:
        existing = db.query(Users).filter(
            Users.mobile == payload.mobile, Users.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Mobile already in use")
        user.mobile = payload.mobile
    if payload.designation is not None:
        user.designation = payload.designation
    if payload.address is not None:
        user.address = payload.address
    if payload.city is not None:
        user.city = payload.city
    if payload.pincode is not None:
        user.pincode = payload.pincode

    user.updated_at = datetime.now()
    db.commit()
    db.refresh(user)
    return {"message": "Profile updated successfully"}


# ─────────────────────────────────────────────
# Password
# ─────────────────────────────────────────────

def change_password(db: Session, user_id: int, payload: ChangePasswordRequest):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not _verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")

    user.password_hash = _hash_password(payload.new_password)
    user.updated_at    = datetime.now()
    db.commit()
    return {"message": "Password changed successfully"}


# ─────────────────────────────────────────────
# Notifications
# ─────────────────────────────────────────────

def get_notifications(db: Session, user_id: int):
    notifs = (
        db.query(Notifications)
        .filter(Notifications.user_id == user_id)
        .order_by(Notifications.created_at.desc())
        .all()
    )
    return [
        {
            "id":         n.id,
            "title":      n.title,
            "message":    n.message,
            "is_read":    n.is_read,
            "created_at": _fmt_dt(n.created_at),
        }
        for n in notifs
    ]


def mark_notification_read(db: Session, user_id: int, notif_id: int):
    notif = (
        db.query(Notifications)
        .filter(Notifications.id == notif_id, Notifications.user_id == user_id)
        .first()
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Marked as read"}


def mark_all_read(db: Session, user_id: int):
    db.query(Notifications).filter(
        Notifications.user_id == user_id,
        Notifications.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}


# ─────────────────────────────────────────────
# App info  (static — no DB needed)
# ─────────────────────────────────────────────

def get_app_info():
    return {
        "app_name":      "FleetPro Management System",
        "version":       "1.0.0",
        "support_phone": "+91 9876543210",
        "support_email": "support@fleetpro.com",
        "faq_url":       "/help/faq",
        "privacy_url":   "/legal/privacy",
        "terms_url":     "/legal/terms",
    }