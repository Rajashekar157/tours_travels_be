# schemas/vehicle_schema.py

from pydantic import BaseModel, field_validator
from typing import Optional
import datetime
import re


class VehicleCreate(BaseModel):
    # Location & Company
    service_location_id: int
    company_id: int

    # Registration
    vehicle_registration_number: str
    vehicle_display_number: Optional[str] = None
    registration_date: Optional[datetime.date] = None

    # Make & Model
    vehicle_make_id: int
    vehicle_model_id: int

    # Engine & Chassis
    engine_number: Optional[str] = None
    chassis_number: Optional[str] = None

    # Fuel & Mileage
    fuel_type_id: int
    average_mileage: Optional[float] = None

    # Year
    year_of_make: Optional[int] = None

    # Transmission
    transmission_type_id: int

    # Seating
    seating_capacity: Optional[int] = None

    # GPS
    gps_enabled: Optional[bool] = False

    # Tax
    tax_status_id: int

    # Photo (stores the relative URL returned by /vehicles/upload-photo,
    # e.g. "/uploads/vehicles/<uuid>.jpg")
    vehicle_photo: Optional[str] = None

    # Status
    status_id: int

    # Fuel Issue
    fuel_issue_id: Optional[int] = None

    @field_validator("engine_number", "chassis_number", "vehicle_registration_number")
    @classmethod
    def must_be_uppercase_alphanumeric(cls, v):
        if v and not re.match(r'^[A-Z0-9]+$', v):
            raise ValueError("Must be all capital letters and numbers only")
        return v

    @field_validator("year_of_make")
    @classmethod
    def year_must_be_4_digits(cls, v):
        if v and (v < 1000 or v > 9999):
            raise ValueError("Year must be a 4-digit number")
        return v

    @field_validator("seating_capacity")
    @classmethod
    def seating_must_be_above_50(cls, v):
        if v is not None and v > 50:
            raise ValueError("Seating capacity must not exceed 50")
        return v


class VehicleUpdate(BaseModel):
    # Location & Company
    service_location_id: Optional[int] = None
    company_id: Optional[int] = None

    # Registration
    vehicle_registration_number: Optional[str] = None
    vehicle_display_number: Optional[str] = None
    registration_date: Optional[datetime.date] = None

    # Make & Model
    vehicle_make_id: Optional[int] = None
    vehicle_model_id: Optional[int] = None

    # Engine & Chassis
    engine_number: Optional[str] = None
    chassis_number: Optional[str] = None

    # Fuel & Mileage
    fuel_type_id: Optional[int] = None
    average_mileage: Optional[float] = None

    # Year
    year_of_make: Optional[int] = None

    # Transmission
    transmission_type_id: Optional[int] = None

    # Seating
    seating_capacity: Optional[int] = None

    # GPS
    gps_enabled: Optional[bool] = None

    # Tax
    tax_status_id: Optional[int] = None

    # Photo
    vehicle_photo: Optional[str] = None

    # Status
    status_id: Optional[int] = None

    # Fuel Issue
    fuel_issue_id: Optional[int] = None

    @field_validator("engine_number", "chassis_number", "vehicle_registration_number")
    @classmethod
    def must_be_uppercase_alphanumeric(cls, v):
        if v and not re.match(r'^[A-Z0-9]+$', v):
            raise ValueError("Must be all capital letters and numbers only")
        return v

    @field_validator("year_of_make")
    @classmethod
    def year_must_be_4_digits(cls, v):
        if v and (v < 1000 or v > 9999):
            raise ValueError("Year must be a 4-digit number")
        return v

    @field_validator("seating_capacity")
    @classmethod
    def seating_must_be_above_50(cls, v):
        if v is not None and v > 50:
            raise ValueError("Seating capacity must not exceed 50")
        return v