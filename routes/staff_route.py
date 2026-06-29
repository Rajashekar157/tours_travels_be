from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db

from schemas.staff_schema import (
    StaffCreate,
    StaffUpdate,
    StaffStatusUpdate,
    StaffPasswordReset,
)

from services.staff_service import (
    create_staff,
    get_staff,
    get_staff_by_id,
    update_staff,
    delete_staff,
    change_staff_status,
    reset_staff_password,
    get_roles,
)

router = APIRouter(
    prefix="/staff",
    tags=["Staff Management"]
)


# ======================================================
# CREATE STAFF
# ======================================================

@router.post("/")
def add_staff(
    data: StaffCreate,
    db: Session = Depends(get_db)
):
    return create_staff(data, db)


# ======================================================
# GET ALL STAFF
# ======================================================

@router.get("/")
def fetch_staff(
    db: Session = Depends(get_db)
):
    return get_staff(db)


# ======================================================
# GET ROLES  — must come before /{id} to avoid conflict
# ======================================================

@router.get("/roles/all")
def fetch_roles(
    db: Session = Depends(get_db)
):
    return get_roles(db)


# ======================================================
# GET STAFF BY ID
# ======================================================

@router.get("/{id}")
def fetch_staff_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    return get_staff_by_id(id, db)


# ======================================================
# UPDATE STAFF
# ======================================================

@router.put("/{id}")
def edit_staff(
    id: int,
    data: StaffUpdate,
    db: Session = Depends(get_db)
):
    return update_staff(id, data, db)


# ======================================================
# SOFT DELETE STAFF
# ======================================================

@router.delete("/{id}")
def remove_staff(
    id: int,
    db: Session = Depends(get_db)
):
    return delete_staff(id, db)


# ======================================================
# CHANGE STAFF STATUS
# ======================================================

@router.put("/{id}/status")
def update_status(
    id: int,
    data: StaffStatusUpdate,
    db: Session = Depends(get_db)
):
    return change_staff_status(id, data, db)


# ======================================================
# RESET PASSWORD
# ======================================================

@router.put("/{id}/reset-password")
def reset_password(
    id: int,
    data: StaffPasswordReset,
    db: Session = Depends(get_db)
):
    return reset_staff_password(id, data, db)