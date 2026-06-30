import os
import uuid
from datetime import datetime
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from models.generated_models import (
    Users,
    MasterRoles,
    MasterBranch,
    StaffPermissions
)

from utils.security import hash_password


# =====================================================
# PERMISSION FIELDS
# =====================================================

PERMISSION_FIELDS = [
    "dashboard",
    "drivers",
    "vehicles",
    "suppliers",
    "assignments",
    "reports",
    "settings",
    "staff_management",
    "messages",
]

VALID_STATUSES = ["Active", "Deactive", "Block Listed"]

# Where staff photos get written on disk. Adjust to match how your
# other upload endpoints (vehicle/driver photos) are configured —
# this should point at a directory that's actually served as static
# files by your FastAPI app (e.g. app.mount("/uploads", StaticFiles(...))).
UPLOAD_DIR = "uploads/staff"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _permissions_to_dict(permissions: StaffPermissions | None) -> dict:
    if not permissions:
        return {field: False for field in PERMISSION_FIELDS}
    return {
        field: getattr(permissions, field, False)
        for field in PERMISSION_FIELDS
    }


def _format_user(user: Users, role: MasterRoles, permissions: StaffPermissions | None, branch: MasterBranch | None = None) -> dict:
    return {
        "id":             user.id,
        "full_name":      user.full_name,
        "email":          user.email,
        "mobile":         user.mobile,
        "role_id":        user.role_id,
        "role_name":      role.role_name if role else "",
        "staff_code":     user.staff_code,
        "designation":    user.designation,
        "service_state":  user.service_state,
        "branch_id":      user.branch_id,
        "branch_name":    branch.branch_name if branch else None,
        "address":        user.address,
        "city":           user.city,
        "pincode":        user.pincode,
        "status":         user.status,
        "is_active":      user.is_active,
        "is_blocked":     user.is_blocked,
        "mobile_verified": user.mobile_verified,
        "photo_url":      user.photo_url,
        "created_at":     user.created_at,
        "updated_at":     user.updated_at,
        "permissions":    _permissions_to_dict(permissions),
    }


# =====================================================
# CREATE STAFF
# =====================================================

def create_staff(data, db: Session):

    # Password match
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Validate status
    if data.status and data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {VALID_STATUSES}")

    # Duplicate mobile
    if db.query(Users).filter(Users.mobile == data.mobile).first():
        raise HTTPException(status_code=400, detail="Mobile already exists")

    # Duplicate email
    if data.email and db.query(Users).filter(Users.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # Duplicate staff_code
    if data.staff_code and db.query(Users).filter(Users.staff_code == data.staff_code).first():
        raise HTTPException(status_code=400, detail="Staff code already exists")

    # Validate role
    role = db.query(MasterRoles).filter(
        MasterRoles.id == data.role_id,
        MasterRoles.is_active == True
    ).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Validate branch if provided
    if data.branch_id:
        branch = db.query(MasterBranch).filter(MasterBranch.id == data.branch_id).first()
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

    # Create user
    user = Users(
        full_name=data.full_name,
        email=data.email,
        mobile=data.mobile,
        password_hash=hash_password(data.password),
        role_id=data.role_id,
        staff_code=data.staff_code,
        designation=data.designation,
        service_state=data.service_state,
        branch_id=data.branch_id,
        address=data.address,
        city=data.city,
        pincode=data.pincode,
        status=data.status or "Active",
        photo_url=data.photo_url or "",
        is_active=True,
        is_blocked=False,
        mobile_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create permissions row
    permissions_data = data.permissions.dict() if data.permissions else {}
    staff_permissions = StaffPermissions(
        user_id=user.id,
        **{field: permissions_data.get(field, False) for field in PERMISSION_FIELDS}
    )
    db.add(staff_permissions)
    db.commit()

    return {"message": "Staff Created Successfully", "staff_id": user.id}


# =====================================================
# GET ALL STAFF
# =====================================================

def get_staff(db: Session):

    rows = (
        db.query(Users, MasterRoles)
        .join(MasterRoles, Users.role_id == MasterRoles.id)
        .order_by(Users.id.desc())
        .all()
    )

    response = []
    for user, role in rows:
        permissions = db.query(StaffPermissions).filter(StaffPermissions.user_id == user.id).first()
        branch = db.query(MasterBranch).filter(MasterBranch.id == user.branch_id).first() if user.branch_id else None
        response.append(_format_user(user, role, permissions, branch))

    return response


# =====================================================
# GET STAFF BY ID
# =====================================================

def get_staff_by_id(id: int, db: Session):

    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Staff Not Found")

    role = db.query(MasterRoles).filter(MasterRoles.id == user.role_id).first()
    permissions = db.query(StaffPermissions).filter(StaffPermissions.user_id == user.id).first()
    branch = db.query(MasterBranch).filter(MasterBranch.id == user.branch_id).first() if user.branch_id else None

    return _format_user(user, role, permissions, branch)


# =====================================================
# GET ROLES
# =====================================================

def get_roles(db: Session):
    roles = db.query(MasterRoles).filter(MasterRoles.is_active == True).order_by(MasterRoles.id).all()
    return [{"id": r.id, "role_name": r.role_name} for r in roles]


# =====================================================
# UPDATE STAFF
# =====================================================

def update_staff(id: int, data, db: Session):

    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Staff Not Found")

    # Validate status
    if data.status and data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {VALID_STATUSES}")

    # Duplicate mobile check
    if db.query(Users).filter(Users.mobile == data.mobile, Users.id != id).first():
        raise HTTPException(status_code=400, detail="Mobile already exists")

    # Duplicate email check
    if data.email and db.query(Users).filter(Users.email == data.email, Users.id != id).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # Duplicate staff_code check
    if data.staff_code and db.query(Users).filter(Users.staff_code == data.staff_code, Users.id != id).first():
        raise HTTPException(status_code=400, detail="Staff code already exists")

    # Validate role
    role = db.query(MasterRoles).filter(MasterRoles.id == data.role_id, MasterRoles.is_active == True).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Validate branch
    if data.branch_id:
        branch = db.query(MasterBranch).filter(MasterBranch.id == data.branch_id).first()
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

    # Update fields
    user.full_name     = data.full_name
    user.email         = data.email
    user.mobile        = data.mobile
    user.role_id       = data.role_id
    user.staff_code    = data.staff_code
    user.designation   = data.designation
    user.service_state = data.service_state
    user.branch_id     = data.branch_id
    user.address       = data.address
    user.city          = data.city
    user.pincode       = data.pincode
    user.status        = data.status or "Active"
    user.is_active     = data.is_active
    user.is_blocked    = (data.status == "Block Listed")
    # Only overwrite photo_url if the caller actually sent one; keeps the
    # existing photo intact when the edit form doesn't touch the photo field.
    if data.photo_url is not None:
        user.photo_url = data.photo_url
    user.updated_at    = datetime.utcnow()

    db.commit()
    db.refresh(user)

    # Update permissions
    permissions_row = db.query(StaffPermissions).filter(StaffPermissions.user_id == id).first()
    permissions_data = data.permissions.dict() if data.permissions else {}
    if not permissions_row:
        permissions_row = StaffPermissions(user_id=id)
        db.add(permissions_row)
    for field in PERMISSION_FIELDS:
        setattr(permissions_row, field, permissions_data.get(field, False))

    db.commit()

    return {"message": "Staff Updated Successfully"}


# =====================================================
# DELETE STAFF (SOFT DELETE)
# =====================================================

def delete_staff(id: int, db: Session):

    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Staff Not Found")

    user.is_active  = False
    user.is_blocked = True
    user.status     = "Deactive"
    user.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Staff Deleted Successfully"}


# =====================================================
# CHANGE STAFF STATUS
# =====================================================

def change_staff_status(id: int, data, db: Session):

    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Staff Not Found")

    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {VALID_STATUSES}")

    user.status     = data.status
    user.is_active  = (data.status == "Active")
    user.is_blocked = (data.status == "Block Listed")
    user.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Status Updated Successfully"}


# =====================================================
# RESET PASSWORD
# =====================================================

def reset_staff_password(id: int, data, db: Session):

    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Staff Not Found")

    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user.password_hash = hash_password(data.password)
    user.updated_at    = datetime.utcnow()

    db.commit()

    return {"message": "Password Reset Successfully"}


# =====================================================
# UPLOAD STAFF PHOTO
# =====================================================

def upload_staff_photo(file: UploadFile) -> dict:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    # Adjust this path to match how your app serves static uploads
    # (e.g. if app.mount("/uploads", StaticFiles(directory="uploads")),
    # then the URL the frontend should hit is "/uploads/staff/<filename>").
    return {"url": f"/uploads/staff/{filename}"}