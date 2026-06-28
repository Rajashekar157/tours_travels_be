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
    role_id: int
    permissions: StaffPermissionsSchema = StaffPermissionsSchema()


# ==============================
# UPDATE STAFF
# ==============================

class StaffUpdate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    mobile: str
    role_id: int
    is_active: bool
    permissions: StaffPermissionsSchema = StaffPermissionsSchema()


# ==============================
# SEND OTP
# ==============================

class SendOTPRequest(BaseModel):
    mobile: str


# ==============================
# VERIFY OTP
# ==============================

class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: str


# ==============================
# STATUS
# ==============================

class StaffStatusUpdate(BaseModel):
    is_active: bool


# ==============================
# RESET PASSWORD
# ==============================

class StaffPasswordReset(BaseModel):
    password: str = Field(..., min_length=6)


# ==============================
# STAFF RESPONSE
# ==============================

class StaffResponse(BaseModel):
    id: int
    full_name: str
    email: Optional[str]
    mobile: Optional[str]
    role_id: int
    role_name: str
    is_active: bool
    permissions: Optional[StaffPermissionsSchema] = None

    class Config:
        from_attributes = True