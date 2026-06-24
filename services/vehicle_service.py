from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.generated_models import Vehicles
from schemas.vehicle_schema import (
    VehicleCreate,
    VehicleUpdate
)

# services/master_service.py

from sqlalchemy.orm import Session
from models.generated_models import (
    MasterServiceLocation,
    MasterVehicleMake,
    MasterFuelType,
    MasterFuelIssue,
    MasterStatus,
    Suppliers
)


def create_vehicle(
    data: VehicleCreate,
    db: Session
):

    existing = (
        db.query(Vehicles)
        .filter(
            Vehicles.vehicle_registration_number
            ==
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
        vehicle_make_id=data.vehicle_make_id,

        fuel_type_id=data.fuel_type_id,

        vehicle_registration_number=data.vehicle_registration_number,

        vehicle_display_number=data.vehicle_display_number,

        average_mileage=data.average_mileage,

        year_of_make=data.year_of_make,

        engine_number=data.engine_number,

        chassis_number=data.chassis_number,

        gps_enabled=data.gps_enabled,

        fuel_issue_id=data.fuel_issue_id,

        insurance_company=data.insurance_company,

        insurance_policy_number=data.insurance_policy_number,

        insurance_expiry_date=data.insurance_expiry_date,

        status_id=data.status_id,

        created_by=data.created_by
    )

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle


def get_vehicles(db: Session):

    vehicles = db.query(Vehicles).all()

    result = []

    for v in vehicles:

        vehicle_data = {
            c.name: getattr(v, c.name)
            for c in v.__table__.columns
        }

        result.append(vehicle_data)

    return result

    
def get_vehicle(
    vehicle_id: int,
    db: Session
):
    vehicle = (
        db.query(Vehicles)
        .filter(
            Vehicles.id == vehicle_id
        )
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    return vehicle


def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session
):

    vehicle = (
        db.query(Vehicles)
        .filter(
            Vehicles.id == vehicle_id
        )
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    for key, value in (
        data.model_dump(
            exclude_unset=True
        ).items()
    ):
        setattr(
            vehicle,
            key,
            value
        )

    db.commit()
    db.refresh(vehicle)

    return vehicle


def delete_vehicle(
    vehicle_id: int,
    db: Session
):

    vehicle = (
        db.query(Vehicles)
        .filter(
            Vehicles.id == vehicle_id
        )
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    db.delete(vehicle)
    db.commit()

    return {
        "message":
        "Vehicle deleted successfully"
    }



def get_service_locations(db: Session):
    return [
        {
            "id": x.id,
            "name": x.location_name
        }
        for x in db.query(
            MasterServiceLocation
        ).all()
    ]


def get_vehicle_makes(db: Session):
    return [
        {
            "id": x.id,
            "name": x.make_name
        }
        for x in db.query(
            MasterVehicleMake
        ).all()
    ]


def get_fuel_types(db: Session):
    return [
        {
            "id": x.id,
            "name": x.fuel_type_name
        }
        for x in db.query(
            MasterFuelType
        ).all()
    ]


def get_fuel_issues(db: Session):
    return [
        {
            "id": x.id,
            "name": x.fuel_issue_name
        }
        for x in db.query(
            MasterFuelIssue
        ).all()
    ]


def get_statuses(db: Session):
    return [
        {
            "id": x.id,
            "name": x.status_name
        }
        for x in db.query(
            MasterStatus
        ).all()
    ]


def get_suppliers(db: Session):
    return [
        {
            "id": x.id,
            "name": x.supplier_name,
            "supplier_type_id": x.supplier_type_id,
            "supplier_type_name": (
                x.supplier_type.supplier_type_name
                if x.supplier_type
                else None
            )
        }
        for x in db.query(Suppliers).all()
    ]