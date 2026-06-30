from pydantic import BaseModel, EmailStr
from typing import Optional


class UpdateProfileRequest(BaseModel):
    full_name:   Optional[str] = None
    email:       Optional[str] = None
    mobile:      Optional[str] = None
    designation: Optional[str] = None
    address:     Optional[str] = None
    city:        Optional[str] = None
    pincode:     Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password:     str