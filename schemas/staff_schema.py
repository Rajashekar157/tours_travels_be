from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ==============================
# CREATE STAFF
# ==============================

class StaffCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    mobile: str
    password: str = Field(..., min_length=6)
    role_id: int


# ==============================
# UPDATE STAFF
# ==============================

class StaffUpdate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    mobile: str
    role_id: int
    is_active: bool


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

    class Config:
        from_attributes = True