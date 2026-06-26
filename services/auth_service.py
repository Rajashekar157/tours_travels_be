from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.generated_models import (
    Users,
    MasterRoles
)

from utils.security import (
    verify_password
)

from utils.jwt_handler import (
    create_access_token
)


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

    token = create_access_token(
        {
            "user_id": user.id,
            "role_id": user.role_id,
            "role_name": role.role_name
        }
    )

    user.last_login = datetime.utcnow()

    db.commit()

    return {

        "access_token": token,

        "token_type": "bearer",

        "user_id": user.id,

        "full_name": user.full_name,

        "mobile": user.mobile,

        "role_id": user.role_id,

        "role_name": role.role_name

    }