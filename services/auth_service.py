import asyncio
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.sse_manager import sse_manager
from models.generated_models import Users, MasterRoles, StaffPermissions
from utils.security import verify_password
from utils.jwt_handler import create_access_token


PERMISSION_FIELDS = [
    "dashboard", "drivers", "vehicles", "suppliers",
    "assignments", "reports", "settings", "staff_management",
    "messages",
]

MAX_LOGIN_ATTEMPTS_BEFORE_FORCE = 3


def _full_permissions() -> dict:
    return {field: True for field in PERMISSION_FIELDS}


def _empty_permissions() -> dict:
    return {field: False for field in PERMISSION_FIELDS}


def _get_permissions_for_user(user: Users, role: MasterRoles, db: Session) -> dict:
    if role.role_name.strip().lower() == "admin":
        return _full_permissions()

    permissions_row = (
        db.query(StaffPermissions)
        .filter(StaffPermissions.user_id == user.id)
        .first()
    )
    if not permissions_row:
        return _empty_permissions()

    return {field: getattr(permissions_row, field, False) for field in PERMISSION_FIELDS}


async def _issue_session_and_login(
    user: Users, role: MasterRoles, db: Session, notify_old_session: bool = False
) -> dict:
    old_jti = user.active_session_token

    token, jti = create_access_token({
        "user_id": user.id,
        "role_id": user.role_id,
        "role_name": role.role_name,
    })

    user.active_session_token = jti
    user.login_attempt_count = 0
    user.last_login = datetime.utcnow()
    db.commit()

    if notify_old_session and old_jti:
        await sse_manager.notify_evicted(old_jti)

    permissions = _get_permissions_for_user(user, role, db)

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
        "mobile": user.mobile,
        "role_id": user.role_id,
        "role_name": role.role_name,
        "permissions": permissions,
    }


async def login_user(data, db: Session):

    user = db.query(Users).filter(Users.mobile == data.mobile).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid Mobile or Password")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid Mobile or Password")

    if user.is_blocked or user.status == "Block Listed":
        raise HTTPException(status_code=403, detail="Your account has been blocked. Contact admin.")

    if not user.is_active or user.status == "Deactive":
        raise HTTPException(status_code=403, detail="Your account is inactive. Contact admin.")

    role = db.query(MasterRoles).filter(MasterRoles.id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if user.active_session_token:
        user.login_attempt_count = (user.login_attempt_count or 0) + 1
        db.commit()

        if user.login_attempt_count < MAX_LOGIN_ATTEMPTS_BEFORE_FORCE:
            return {
                "success": False,
                "message": "You are already logged in on another device. Please log out from the other device first.",
                "session_exists": True,
                "attempt": user.login_attempt_count,
            }

        return await _issue_session_and_login(user, role, db, notify_old_session=True)

    return await _issue_session_and_login(user, role, db)


def logout_user(user_id: int, db: Session):
    user = db.query(Users).filter(Users.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.active_session_token = None
    user.login_attempt_count = 0
    db.commit()

    return {"success": True, "message": "Logged out successfully"}