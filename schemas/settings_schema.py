from pydantic import BaseModel, EmailStr
from typing import Optional


class UpdateProfileRequest(BaseModel):
    full_name:  Optional[str] = None
    email:      Optional[str] = None
    mobile:     Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password:     str