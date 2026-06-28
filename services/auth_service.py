from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.generated_models import (
    Users,
    MasterRoles,
    StaffPermissions
)

from utils.security import (
    verify_password
)

from utils.jwt_handler import (
    create_access_token
)


PERMISSION_FIELDS = [
    "dashboard",
    "drivers",
    "vehicles",
    "suppliers",
    "assignments",
    "reports",
    "settings",
    "staff_management",
]


def _full_permissions() -> dict:
    return {field: True for field in PERMISSION_FIELDS}


def _empty_permissions() -> dict:
    return {field: False for field in PERMISSION_FIELDS}


def _get_permissions_for_user(user: Users, role: MasterRoles, db: Session) -> dict:

    print(f"DEBUG role_name: '{role.role_name}'")

    if role.role_name.strip().lower() == "admin":
        print("DEBUG: Admin user — returning full permissions")
        return _full_permissions()

    print(f"DEBUG: Querying StaffPermissions for user_id={user.id}")

    permissions_row = (
        db.query(StaffPermissions)
        .filter(StaffPermissions.user_id == user.id)
        .first()
    )

    print(f"DEBUG permissions_row: {permissions_row}")

    if not permissions_row:
        print("DEBUG: No permissions row found — returning empty permissions")
        return _empty_permissions()

    result = {
        field: getattr(permissions_row, field, False)
        for field in PERMISSION_FIELDS
    }

    print(f"DEBUG permissions result: {result}")

    return result


def login_user(data, db: Session):

    user = (
        db.query(Users)
        .filter(
            Users.mobile == data.mobile
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Mobile or Password"
        )

    if user.is_blocked:
        raise HTTPException(
            status_code=403,
            detail="User is blocked"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User is inactive"
        )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Mobile or Password"
        )

    if not user.mobile_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify mobile first"
        )

    role = (
        db.query(MasterRoles)
        .filter(
            MasterRoles.id == user.role_id
        )
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    permissions = _get_permissions_for_user(user, role, db)

    print(f"DEBUG final permissions: {permissions}")

    token = create_access_token(
        {
            "user_id": user.id,
            "role_id": user.role_id,
            "role_name": role.role_name
        }
    )

    user.last_login = datetime.utcnow()

    db.commit()

    result = {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
        "mobile": user.mobile,
        "role_id": user.role_id,
        "role_name": role.role_name,
        "permissions": permissions
    }

    print(f"DEBUG full return result: {result}")

    return result