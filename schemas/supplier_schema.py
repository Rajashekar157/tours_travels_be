from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal
from datetime import date


class SupplierCreate(BaseModel):
    supplier_id: str
    supplier_code: Optional[str] = None
    supplier_name: str

    mobile: str
    alternate_mobile: Optional[str] = None
    email: Optional[EmailStr] = None

    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None

    aadhaar_number: Optional[str] = None
    adhaar_url: Optional[str] = None
    photo_url: Optional[str] = None

    current_address: Optional[str] = None
    permanent_address: str
    temporary_address: str

    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    license_number: Optional[str] = None
    license_expiry: Optional[date] = None
    license_file_url: Optional[str] = None

    pancard_number: Optional[str] = None
    pancard_file_url: Optional[str] = None

    bank_passbook_photo_url: Optional[str] = None
    gas_bill_photo_url: Optional[str] = None
    electricity_bill_photo_url: Optional[str] = None

    reference_person_name: str
    reference_contact_number_1: str
    reference_contact_number_2: str

    emergency_contact_name: str
    emergency_contact_number: str

    joining_date: Optional[date] = None
    agreement_start_date: Optional[date] = None
    agreement_end_date: Optional[date] = None
    agreement_status: Optional[str] = None
    agreement_tenure_months: Optional[int] = None
    emi_completed_months: Optional[int] = None

    character_nature: Optional[str] = "Good"

    status_id: Optional[int] = None
    supplier_type_id: Optional[int] = None
    service_location_id: Optional[int] = None
    branch_id: Optional[int] = None

    outstanding_amount: Optional[Decimal] = None
    remarks: Optional[str] = None


class SupplierUpdate(BaseModel):
    supplier_code: Optional[str] = None
    supplier_name: Optional[str] = None

    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    email: Optional[EmailStr] = None

    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None

    aadhaar_number: Optional[str] = None
    adhaar_url: Optional[str] = None
    photo_url: Optional[str] = None

    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    temporary_address: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    license_number: Optional[str] = None
    license_expiry: Optional[date] = None
    license_file_url: Optional[str] = None

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

    joining_date: Optional[date] = None
    agreement_start_date: Optional[date] = None
    agreement_end_date: Optional[date] = None
    agreement_status: Optional[str] = None
    agreement_tenure_months: Optional[int] = None
    emi_completed_months: Optional[int] = None

    character_nature: Optional[str] = None

    status_id: Optional[int] = None
    supplier_type_id: Optional[int] = None
    service_location_id: Optional[int] = None
    branch_id: Optional[int] = None

    outstanding_amount: Optional[Decimal] = None
    remarks: Optional[str] = None


class SupplierResponse(BaseModel):
    id: int
    supplier_id: str
    supplier_code: Optional[str] = None
    supplier_name: str

    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    email: Optional[str] = None

    blood_group: Optional[str] = None
    date_of_birth: Optional[date] = None

    aadhaar_number: Optional[str] = None
    adhaar_url: Optional[str] = None
    photo_url: Optional[str] = None

    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    temporary_address: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    license_number: Optional[str] = None
    license_expiry: Optional[date] = None
    license_file_url: Optional[str] = None

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

    joining_date: Optional[date] = None
    agreement_start_date: Optional[date] = None
    agreement_end_date: Optional[date] = None
    agreement_status: Optional[str] = None
    agreement_tenure_months: Optional[int] = None
    emi_completed_months: Optional[int] = None

    character_nature: Optional[str] = None

    status_id: Optional[int] = None
    supplier_type_id: Optional[int] = None
    service_location_id: Optional[int] = None
    branch_id: Optional[int] = None

    outstanding_amount: Optional[Decimal] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True