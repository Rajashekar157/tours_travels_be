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

    # location / branch
    location_id: Optional[int] = None
    branch_id: Optional[int] = None

    # mandatory addresses
    permanent_address: str
    temporary_address: str

    # pancard
    pancard_number: Optional[str] = None
    pancard_file_url: Optional[str] = None

    # document uploads
    bank_passbook_photo_url: Optional[str] = None
    gas_bill_photo_url: Optional[str] = None
    electricity_bill_photo_url: Optional[str] = None

    # reference person (mandatory)
    reference_person_name: str
    reference_contact_number_1: str
    reference_contact_number_2: str

    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None

    blood_group: Optional[str] = None
    supplier_type_id: Optional[int] = None
    character_nature: Optional[str] = "Good"

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

    location_id: Optional[int] = None
    branch_id: Optional[int] = None

    permanent_address: Optional[str] = None
    temporary_address: Optional[str] = None

    pancard_number: Optional[str] = None
    pancard_file_url: Optional[str] = None

    bank_passbook_photo_url: Optional[str] = None
    gas_bill_photo_url: Optional[str] = None
    electricity_bill_photo_url: Optional[str] = None

    reference_person_name: Optional[str] = None
    reference_contact_number_1: Optional[str] = None
    reference_contact_number_2: Optional[str] = None

    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None

    blood_group: Optional[str] = None
    supplier_type_id: Optional[int] = None

    character_nature: Optional[str] = None

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

    location_id: Optional[int] = None
    branch_id: Optional[int] = None

    permanent_address: Optional[str] = None
    temporary_address: Optional[str] = None

    pancard_number: Optional[str] = None
    pancard_file_url: Optional[str] = None

    bank_passbook_photo_url: Optional[str] = None
    gas_bill_photo_url: Optional[str] = None
    electricity_bill_photo_url: Optional[str] = None

    reference_person_name: Optional[str] = None
    reference_contact_number_1: Optional[str] = None
    reference_contact_number_2: Optional[str] = None
    supplier_type_id: Optional[int] = None

    character_nature: Optional[str] = None

    status_id: Optional[int] = None

    class Config:
        from_attributes = True


class MasterServiceLocationCreate(BaseModel):
    location_name: str
    is_active: Optional[bool] = True


class MasterServiceLocationUpdate(BaseModel):
    location_name: Optional[str] = None
    is_active: Optional[bool] = None


class MasterServiceLocationResponse(BaseModel):
    id: int
    location_name: str
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class MasterBranchCreate(BaseModel):
    branch_name: str
    location_id: int
    is_active: Optional[bool] = True


class MasterBranchUpdate(BaseModel):
    branch_name: Optional[str] = None
    location_id: Optional[int] = None
    is_active: Optional[bool] = None


class MasterBranchResponse(BaseModel):
    id: int
    branch_name: str
    location_id: int
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True