from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class VehicleCreate(BaseModel):
    service_location_id: int
    vehicle_make_id: int
    fuel_type_id: int

    vehicle_registration_number: str = Field(
        ...,
        min_length=5,
        max_length=20
    )

    vehicle_display_number: Optional[str] = None

    average_mileage: Optional[float] = None

    year_of_make: Optional[int] = None

    engine_number: Optional[str] = None

    chassis_number: Optional[str] = None

    gps_enabled: bool = False

    fuel_issue_id: Optional[int] = None

    insurance_company: Optional[str] = None

    insurance_policy_number: Optional[str] = None

    insurance_expiry_date: Optional[date] = None

    status_id: int

    created_by: int


class VehicleUpdate(BaseModel):
    service_location_id: Optional[int] = None
    vehicle_make_id: Optional[int] = None
    fuel_type_id: Optional[int] = None

    vehicle_display_number: Optional[str] = None

    average_mileage: Optional[float] = None

    year_of_make: Optional[int] = None

    engine_number: Optional[str] = None

    chassis_number: Optional[str] = None

    gps_enabled: Optional[bool] = None

    fuel_issue_id: Optional[int] = None

    insurance_company: Optional[str] = None

    insurance_policy_number: Optional[str] = None

    insurance_expiry_date: Optional[date] = None

    status_id: Optional[int] = None

    updated_by: int