from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal


class SupplierCreate(BaseModel):
    supplier_id: str
    supplier_name: str
    

    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    email: Optional[EmailStr] = None

    aadhaar_number: Optional[str] = None
    photo_url: Optional[str] = None

    current_address: Optional[str] = None
    permanent_address: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    status_id: Optional[int] = None
    supplier_type_id: Optional[int] = None
    service_location_id: Optional[int] = None

    outstanding_amount: Optional[Decimal] = None
    remarks: Optional[str] = None


class SupplierUpdate(BaseModel):
    supplier_name: Optional[str] = None

    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    email: Optional[EmailStr] = None

    aadhaar_number: Optional[str] = None
    photo_url: Optional[str] = None

    current_address: Optional[str] = None
    permanent_address: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

    status_id: Optional[int] = None
    supplier_type_id: Optional[int] = None
    service_location_id: Optional[int] = None

    outstanding_amount: Optional[Decimal] = None
    remarks: Optional[str] = None


class SupplierResponse(BaseModel):
    id: int
    supplier_id: str
    supplier_name: str
    supplier_type_name: Optional[str] = None
    mobile: Optional[str]
    alternate_mobile: Optional[str]
    email: Optional[str]

    aadhaar_number: Optional[str]
    photo_url: Optional[str]

    current_address: Optional[str]
    permanent_address: Optional[str]

    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]

    status_id: Optional[int]
    supplier_type_id: Optional[int]
    service_location_id: Optional[int]

    outstanding_amount: Optional[Decimal]
    remarks: Optional[str]

    class Config:
        from_attributes = True