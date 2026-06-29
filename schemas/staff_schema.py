from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ==============================
# PERMISSIONS
# ==============================

class StaffPermissionsSchema(BaseModel):
    dashboard: bool = False
    drivers: bool = False
    vehicles: bool = False
    suppliers: bool = False
    assignments: bool = False
    reports: bool = False
    settings: bool = False
    staff_management: bool = False


# ==============================
# CREATE STAFF
# ==============================

class StaffCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    mobile: str
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    role_id: int
    staff_code: Optional[str] = None
    designation: Optional[str] = None
    service_state: Optional[str] = None
    branch_id: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    status: Optional[str] = "Active"  # Active | Deactive | Block Listed
    permissions: StaffPermissionsSchema = StaffPermissionsSchema()


# ==============================
# UPDATE STAFF
# ==============================

class StaffUpdate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    mobile: str
    role_id: int
    staff_code: Optional[str] = None
    designation: Optional[str] = None
    service_state: Optional[str] = None
    branch_id: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    status: Optional[str] = "Active"  # Active | Deactive | Block Listed
    is_active: bool = True
    permissions: StaffPermissionsSchema = StaffPermissionsSchema()


# ==============================
# STATUS UPDATE
# ==============================

class StaffStatusUpdate(BaseModel):
    status: str  # Active | Deactive | Block Listed


# ==============================
# RESET PASSWORD
# ==============================

class StaffPasswordReset(BaseModel):
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)


# ==============================
# STAFF RESPONSE
# ==============================

class StaffResponse(BaseModel):
    id: int
    full_name: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    role_id: int
    role_name: str
    staff_code: Optional[str] = None
    designation: Optional[str] = None
    service_state: Optional[str] = None
    branch_id: Optional[int] = None
    branch_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    status: Optional[str] = None
    is_active: bool
    is_blocked: bool
    permissions: Optional[StaffPermissionsSchema] = None

    class Config:
        from_attributes = True