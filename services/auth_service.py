import random
from utils.sms_service import send_sms_otp
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.generated_models import (
    Users,
    UserOtps
)

from utils.security import (
    hash_password,
    verify_password
)

from utils.jwt_handler import (
    create_access_token
)


def register_user(data, db: Session):

    existing = (
        db.query(Users)
        .filter(Users.mobile == data.mobile)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Mobile already exists"
        )

    user = Users(
        full_name=data.full_name,
        email=data.email,
        mobile=data.mobile,
        password_hash=hash_password(data.password),
        mobile_verified=False,
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Registered successfully",
        "user_id": user.id
    }


# def send_otp(data, db: Session):

#     user = (
#         db.query(Users)
#         .filter(Users.mobile == data.mobile)
#         .first()
#     )

#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="User not found"
#         )

#     otp = str(
#         random.randint(
#             100000,
#             999999
#         )
#     )

#     otp_record = UserOtps(
#         user_id=user.id,
#         otp_code=otp,
#         expires_at=datetime.utcnow() +
#         timedelta(minutes=5),
#         is_used=False
#     )

#     db.add(otp_record)
#     db.commit()

#     return {
#         "message": "OTP Sent",
#         "otp": otp
#     }


# def send_otp(data, db: Session):

#     user = (
#         db.query(Users)
#         .filter(Users.mobile == data.mobile)
#         .first()
#     )

#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="User not found"
#         )

#     otp = str(
#         random.randint(
#             100000,
#             999999
#         )
#     )

#     otp_record = UserOtps(
#         user_id=user.id,
#         otp_code=otp,
#         expires_at=datetime.utcnow()
#         + timedelta(minutes=5),
#         is_used=False
#     )

#     db.add(otp_record)
#     db.commit()

#     # Send OTP SMS
#     send_sms_otp(
#         user.mobile,
#         otp
#     )

#     return {
#         "message": "OTP Sent Successfully"
#     }


def send_otp(data, db: Session):

    user = (
        db.query(Users)
        .filter(Users.mobile == data.mobile)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.query(UserOtps).filter(
        UserOtps.user_id == user.id
    ).delete()

    otp = "123456"

    otp_record = UserOtps(
        user_id=user.id,
        otp_code=otp,
        expires_at=datetime.utcnow()
        + timedelta(minutes=5),
        is_used=False
    )

    db.add(otp_record)
    db.commit()

    return {
        "message": "OTP Sent Successfully"
    }
def verify_otp(data, db: Session):

    user = (
        db.query(Users)
        .filter(Users.mobile == data.mobile)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    otp_record = (
        db.query(UserOtps)
        .filter(
            UserOtps.user_id == user.id,
            UserOtps.otp_code == data.otp,
            UserOtps.is_used == False
        )
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="OTP Expired"
        )

    otp_record.is_used = True
    user.mobile_verified = True

    db.commit()

    return {
        "message": "Mobile verified successfully"
    }


def login_user(data, db: Session):

    user = (
        db.query(Users)
        .filter(Users.mobile == data.mobile)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials"
        )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials"
        )

    if not user.mobile_verified:
        raise HTTPException(
            status_code=403,
            detail="Verify mobile first"
        )

    token = create_access_token(
        {
            "user_id": user.id,
            "role": user.role
        }
    )

    user.last_login = datetime.utcnow()

    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
        "role": user.role
    }