from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


# =====================================================
# CREATE
# =====================================================

class VehicleAssignmentCreate(BaseModel):

    # Core
    driver_id: int
    vehicle_id: int
    supplier_id: Optional[int] = None

    # New fields from form
    service_location_id: Optional[int] = None
    branch_id: Optional[int] = None
    vehicle_odometer_km: Optional[float] = None
    assignment_type: Optional[str] = None  # Dispatch / Handover / Recovery

    # Photos
    allotment_document_photo: Optional[str] = None
    vehicle_photo_front: Optional[str] = None
    vehicle_photo_back: Optional[str] = None
    vehicle_photo_left: Optional[str] = None
    vehicle_photo_right: Optional[str] = None

    remarks: Optional[str] = None
    created_by: Optional[int] = None


# =====================================================
# UPDATE
# =====================================================

class VehicleAssignmentUpdate(BaseModel):

    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    supplier_id: Optional[int] = None

    service_location_id: Optional[int] = None
    branch_id: Optional[int] = None
    vehicle_odometer_km: Optional[float] = None
    assignment_type: Optional[str] = None

    allotment_document_photo: Optional[str] = None
    vehicle_photo_front: Optional[str] = None
    vehicle_photo_back: Optional[str] = None
    vehicle_photo_left: Optional[str] = None
    vehicle_photo_right: Optional[str] = None

    relieved_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    remarks: Optional[str] = None
    updated_by: Optional[int] = None


# =====================================================
# RESPONSE
# =====================================================

class VehicleAssignmentResponse(BaseModel):

    id: int
    unique_number: Optional[str] = None

    driver_id: int
    vehicle_id: int
    supplier_id: Optional[int] = None

    service_location_id: Optional[int] = None
    branch_id: Optional[int] = None
    vehicle_odometer_km: Optional[float] = None
    assignment_type: Optional[str] = None

    assigned_date: datetime

    # Server-generated only — never accepted as client input
    transaction_id: Optional[str] = None
    transaction_date: Optional[datetime] = None

    allotment_document_photo: Optional[str] = None
    vehicle_photo_front: Optional[str] = None
    vehicle_photo_back: Optional[str] = None
    vehicle_photo_left: Optional[str] = None
    vehicle_photo_right: Optional[str] = None

    relieved_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    remarks: Optional[str] = None

    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    class Config:
        from_attributes = True