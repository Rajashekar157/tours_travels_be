from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class DriverCreate(BaseModel):
    driver_code: str

    full_name: str
    mobile: str

    user_id: Optional[int] = None
  
    email: Optional[EmailStr] = None

    aadhaar_number: Optional[str] = None
    adhaar_url: Optional[str] = None

    license_number: Optional[str] = None
    license_file_url: Optional[str] = None
    license_expiry: Optional[date] = None

    driver_photo_url: Optional[str] = None

    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None

    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None

    blood_group: Optional[str] = None

    status_id: int


class DriverUpdate(BaseModel):

    full_name: Optional[str] = None
    mobile: Optional[str] = None

    email: Optional[EmailStr] = None

    aadhaar_number: Optional[str] = None
    adhaar_url: Optional[str] = None

    license_number: Optional[str] = None
    license_file_url: Optional[str] = None
    license_expiry: Optional[date] = None

    driver_photo_url: Optional[str] = None

    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None

    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None

    blood_group: Optional[str] = None

    status_id: Optional[int] = None

  

class DriverResponse(BaseModel):
    id: int
    driver_code: str
    full_name: str
    mobile: str

    email: Optional[str] = None

    aadhaar_number: Optional[str] = None
    adhaar_url: Optional[str] = None

    license_number: Optional[str] = None
    license_file_url: Optional[str] = None

    driver_photo_url: Optional[str] = None

    status_id: Optional[int] = None

    class Config:
        from_attributes = True