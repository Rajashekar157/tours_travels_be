from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.generated_models import (
    Users,
    UserOtps,
    MasterRoles
)

from utils.security import (
    hash_password,
    verify_password
)

# =====================================================
# DEVELOPMENT OTP STORAGE
# =====================================================

OTP_CACHE = {}

VERIFIED_MOBILES = set()


# =====================================================
# CREATE STAFF
# =====================================================

def create_staff(data, db: Session):

    # OTP must be verified first
    if data.mobile not in VERIFIED_MOBILES:
        raise HTTPException(
            status_code=400,
            detail="Verify OTP First"
        )

    # Mobile already exists
    mobile_exists = (
        db.query(Users)
        .filter(
            Users.mobile == data.mobile
        )
        .first()
    )

    if mobile_exists:
        raise HTTPException(
            status_code=400,
            detail="Mobile already exists"
        )

    # Email already exists
    if data.email:

        email_exists = (
            db.query(Users)
            .filter(
                Users.email == data.email
            )
            .first()
        )

        if email_exists:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

    # Validate Role
    role = (
        db.query(MasterRoles)
        .filter(
            MasterRoles.id == data.role_id,
            MasterRoles.is_active == True
        )
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    # Create Staff
    user = Users(

        full_name=data.full_name,

        email=data.email,

        mobile=data.mobile,

        password_hash=hash_password(
            data.password
        ),

        role_id=data.role_id,

        is_active=True,

        mobile_verified=True,

        is_blocked=False,

        created_at=datetime.utcnow(),

        updated_at=datetime.utcnow()

    )

    db.add(user)

    db.commit()

    db.refresh(user)

    # Remove verified mobile after successful creation
    VERIFIED_MOBILES.discard(
        data.mobile
    )

    return {

        "message": "Staff Created Successfully",

        "staff_id": user.id

    }

# =====================================================
# GET ALL STAFF
# =====================================================

def get_staff(db: Session):

    staffs = (
        db.query(
            Users,
            MasterRoles
        )
        .join(
            MasterRoles,
            Users.role_id == MasterRoles.id
        )
        .order_by(Users.id.desc())
        .all()
    )

    response = []

    for user, role in staffs:

        response.append({

            "id": user.id,

            "full_name": user.full_name,

            "email": user.email,

            "mobile": user.mobile,

            "role_id": user.role_id,

            "role_name": role.role_name,

            "mobile_verified": user.mobile_verified,

            "is_active": user.is_active,

            "is_blocked": user.is_blocked,

            "created_at": user.created_at,

            "updated_at": user.updated_at

        })

    return response


# =====================================================
# GET STAFF BY ID
# =====================================================

def get_staff_by_id(id: int, db: Session):

    user = (
        db.query(Users)
        .filter(
            Users.id == id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Staff Not Found"
        )

    role = (
        db.query(MasterRoles)
        .filter(
            MasterRoles.id == user.role_id
        )
        .first()
    )

    return {

        "id": user.id,

        "full_name": user.full_name,

        "email": user.email,

        "mobile": user.mobile,

        "role_id": user.role_id,

        "role_name": role.role_name if role else "",

        "mobile_verified": user.mobile_verified,

        "is_active": user.is_active,

        "is_blocked": user.is_blocked,

        "created_at": user.created_at,

        "updated_at": user.updated_at

    }


# =====================================================
# GET ROLES
# =====================================================

def get_roles(db: Session):

    roles = (
        db.query(MasterRoles)
        .filter(
            MasterRoles.is_active == True
        )
        .order_by(MasterRoles.id)
        .all()
    )

    return [

        {

            "id": role.id,

            "role_name": role.role_name

        }

        for role in roles

    ]

# =====================================================
# UPDATE STAFF
# =====================================================

def update_staff(id: int, data, db: Session):

    user = (
        db.query(Users)
        .filter(
            Users.id == id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Staff Not Found"
        )

    # Check duplicate mobile
    mobile_exists = (
        db.query(Users)
        .filter(
            Users.mobile == data.mobile,
            Users.id != id
        )
        .first()
    )

    if mobile_exists:
        raise HTTPException(
            status_code=400,
            detail="Mobile already exists"
        )

    # Check duplicate email
    if data.email:

        email_exists = (
            db.query(Users)
            .filter(
                Users.email == data.email,
                Users.id != id
            )
            .first()
        )

        if email_exists:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

    # Validate Role
    role = (
        db.query(MasterRoles)
        .filter(
            MasterRoles.id == data.role_id,
            MasterRoles.is_active == True
        )
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Role not found"
        )

    user.full_name = data.full_name
    user.email = data.email
    user.mobile = data.mobile
    user.role_id = data.role_id
    user.is_active = data.is_active
    user.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    return {
        "message": "Staff Updated Successfully"
    }


# =====================================================
# DELETE STAFF (SOFT DELETE)
# =====================================================

def delete_staff(id: int, db: Session):

    user = (
        db.query(Users)
        .filter(
            Users.id == id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Staff Not Found"
        )

    # Soft delete
    user.is_active = False

    # Optional: mark as blocked also
    user.is_blocked = True

    user.updated_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Staff Deleted Successfully"
    }


# =====================================================
# CHANGE STAFF STATUS
# =====================================================

def change_staff_status(
    id: int,
    data,
    db: Session
):

    user = (
        db.query(Users)
        .filter(
            Users.id == id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Staff Not Found"
        )

    user.is_active = data.is_active
    user.updated_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Status Updated Successfully"
    }


# =====================================================
# RESET PASSWORD
# =====================================================

def reset_staff_password(
    id: int,
    data,
    db: Session
):

    user = (
        db.query(Users)
        .filter(
            Users.id == id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Staff Not Found"
        )

    user.password_hash = hash_password(
        data.password
    )

    user.updated_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Password Reset Successfully"
    }

# =====================================================
# SEND OTP
# =====================================================

def send_otp(data, db: Session):

    mobile = data.mobile.strip()

    if len(mobile) != 10 or not mobile.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Invalid Mobile Number"
        )

    # Static OTP for development
    otp = "123456"

    # Store OTP in memory
    OTP_CACHE[mobile] = {
        "otp": otp,
        "expires_at": datetime.utcnow() + timedelta(minutes=5)
    }

    # Uncomment when using SMS
    # send_sms_otp(mobile, otp)

    return {
        "message": "OTP Sent Successfully"
    }


# =====================================================
# VERIFY OTP
# =====================================================

def verify_otp(data, db: Session):

    mobile = data.mobile.strip()

    otp_data = OTP_CACHE.get(mobile)

    if not otp_data:
        raise HTTPException(
            status_code=400,
            detail="Please send OTP first"
        )

    # Check expiry
    if otp_data["expires_at"] < datetime.utcnow():

        OTP_CACHE.pop(mobile, None)

        raise HTTPException(
            status_code=400,
            detail="OTP Expired"
        )

    # Verify OTP
    if otp_data["otp"] != data.otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    # Remove OTP after verification
    OTP_CACHE.pop(mobile, None)

    # Mark this mobile as verified
    VERIFIED_MOBILES.add(mobile)

    return {
        "message": "OTP Verified Successfully",
        "mobile_verified": True
    }