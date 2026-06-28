# services/vehicle_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from models.generated_models import (
    Vehicles,
    MasterServiceLocation,
    MasterVehicleMake,
    MasterVehicleModel,
    MasterFuelType,
    MasterFuelIssue,
    MasterStatus,
    MasterCompany,
    MasterTransmissionType,
    MasterTaxStatus,
    Suppliers
)
from schemas.vehicle_schema import VehicleCreate, VehicleUpdate


def create_vehicle(data: VehicleCreate, db: Session, current_user):
    try:
        existing = (
            db.query(Vehicles)
            .filter(
                Vehicles.vehicle_registration_number ==
                data.vehicle_registration_number
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Vehicle already exists"
            )

        vehicle = Vehicles(
            service_location_id=data.service_location_id,
            company_id=data.company_id,
            vehicle_make_id=data.vehicle_make_id,
            vehicle_model_id=data.vehicle_model_id,
            fuel_type_id=data.fuel_type_id,
            vehicle_registration_number=data.vehicle_registration_number,
            vehicle_display_number=data.vehicle_display_number,
            registration_date=data.registration_date,
            average_mileage=data.average_mileage,
            year_of_make=data.year_of_make,
            engine_number=data.engine_number,
            chassis_number=data.chassis_number,
            transmission_type_id=data.transmission_type_id,
            seating_capacity=data.seating_capacity,
            gps_enabled=data.gps_enabled,
            tax_status_id=data.tax_status_id,
            fuel_issue_id=data.fuel_issue_id,
            insurance_company=data.insurance_company,
            insurance_policy_number=data.insurance_policy_number,
            insurance_expiry_date=data.insurance_expiry_date,
            vehicle_photo=data.vehicle_photo,
            status_id=data.status_id,
            created_by=current_user["user_id"],
            updated_by=current_user["user_id"]
        )

        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)
        return vehicle

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def get_vehicles(db: Session):
    vehicles = db.query(Vehicles).all()
    return [
        {c.name: getattr(v, c.name) for c in v.__table__.columns}
        for v in vehicles
    ]


def get_vehicle(vehicle_id: int, db: Session):
    vehicle = db.query(Vehicles).filter(Vehicles.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


def update_vehicle(vehicle_id: int, data: VehicleUpdate, db: Session, current_user):
    vehicle = db.query(Vehicles).filter(Vehicles.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, key, value)

    vehicle.updated_by = current_user["user_id"]
    db.commit()
    db.refresh(vehicle)
    return vehicle


def delete_vehicle(vehicle_id: int, db: Session):
    vehicle = db.query(Vehicles).filter(Vehicles.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted successfully"}


# ----------- Master Dropdowns -----------

def get_service_locations(db: Session):
    return [
        {"id": x.id, "name": x.location_name}
        for x in db.query(MasterServiceLocation).filter_by(is_active=True).all()
    ]


def get_vehicle_makes(db: Session):
    return [
        {"id": x.id, "name": x.make_name}
        for x in db.query(MasterVehicleMake).filter_by(is_active=True).all()
    ]


def get_vehicle_models(db: Session, make_id: Optional[int] = None):
    query = db.query(MasterVehicleModel).filter_by(is_active=True)
    if make_id:
        query = query.filter(MasterVehicleModel.vehicle_make_id == make_id)
    return [
        {"id": x.id, "name": x.model_name, "make_id": x.vehicle_make_id}
        for x in query.all()
    ]


def get_fuel_types(db: Session):
    return [
        {"id": x.id, "name": x.fuel_type_name}
        for x in db.query(MasterFuelType).filter_by(is_active=True).all()
    ]


def get_fuel_issues(db: Session):
    return [
        {"id": x.id, "name": x.fuel_issue_name}
        for x in db.query(MasterFuelIssue).all()
    ]


def get_statuses(db: Session):
    return [
        {"id": x.id, "name": x.status_name}
        for x in db.query(MasterStatus).filter_by(is_active=True).all()
    ]


def get_companies(db: Session):
    return [
        {"id": x.id, "name": x.company_name}
        for x in db.query(MasterCompany).filter_by(is_active=True).all()
    ]


def get_transmission_types(db: Session):
    return [
        {"id": x.id, "name": x.transmission_name}
        for x in db.query(MasterTransmissionType).filter_by(is_active=True).all()
    ]


def get_tax_statuses(db: Session):
    return [
        {"id": x.id, "name": x.tax_status_name}
        for x in db.query(MasterTaxStatus).filter_by(is_active=True).all()
    ]


def get_suppliers(db: Session):
    return [
        {
            "id": x.id,
            "name": x.supplier_name,
            "supplier_type_id": x.supplier_type_id,
            "supplier_type_name": (
                x.supplier_type.supplier_type_name if x.supplier_type else None
            )
        }
        for x in db.query(Suppliers).all()
    ]