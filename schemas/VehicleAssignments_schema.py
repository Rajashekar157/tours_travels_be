from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# =====================================================
# CREATE
# =====================================================

class VehicleAssignmentCreate(BaseModel):

    # Core — driver_id is optional: either driver OR supplier
    driver_id: Optional[int] = None
    vehicle_id: int
    supplier_id: Optional[int] = None

    service_location_id: Optional[int] = None
    branch_id: Optional[int] = None
    vehicle_odometer_km: Optional[float] = None
    assignment_type: Optional[str] = None  # Dispatch / Handover / Recovery

    # Photos — paths returned by /upload-document
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

    # driver_id is now nullable — either driver or supplier is present
    driver_id: Optional[int] = None
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

    # Chain — every row in one vehicle's Dispatch -> Handover -> Recovery
    # lifecycle shares this value, independent of each row's own
    # unique_number. Set once at the Dispatch and inherited down the chain.
    chain_id: Optional[str] = None

    # Direct parent link — set only on Handover/Recovery rows; points back
    # to the specific row (Dispatch or prior stage) this one closed out.
    parent_assignment_id: Optional[int] = None
    parent_unique_number: Optional[str] = None

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