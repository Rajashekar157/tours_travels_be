from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class VehicleAssignmentCreate(BaseModel):
    driver_id: int
    vehicle_id: int
    supplier_id: int

    assignment_type: Optional[str] = None

    emi_amount: Optional[float] = None
    emi_tenure_months: Optional[int] = None

    emi_start_date: Optional[date] = None
    emi_end_date: Optional[date] = None

    transaction_id: Optional[str] = None

    remarks: Optional[str] = None

    created_by: Optional[int] = None


class VehicleAssignmentUpdate(BaseModel):
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    supplier_id: Optional[int] = None

    assignment_type: Optional[str] = None

    emi_amount: Optional[float] = None
    emi_tenure_months: Optional[int] = None

    emi_start_date: Optional[date] = None
    emi_end_date: Optional[date] = None

    transaction_id: Optional[str] = None

    relieved_date: Optional[datetime] = None

    is_active: Optional[bool] = None
    remarks: Optional[str] = None

    updated_by: Optional[int] = None


class VehicleAssignmentResponse(BaseModel):

    id: int
    unique_number: Optional[str]

    driver_id: int
    vehicle_id: int
    supplier_id: Optional[int]

    assigned_date: datetime

    assignment_type: Optional[str]

    emi_amount: Optional[float]
    emi_tenure_months: Optional[int]

    emi_start_date: Optional[date]
    emi_end_date: Optional[date]

    transaction_id: Optional[str]

    relieved_date: Optional[datetime]

    is_active: Optional[bool]

    remarks: Optional[str]

    created_by: Optional[int]
    updated_by: Optional[int]

    class Config:
        from_attributes = True