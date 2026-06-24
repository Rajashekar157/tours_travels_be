from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from core.database import get_db

from schemas.vehicle_schema import (
    VehicleCreate,
    VehicleUpdate
)

from services.vehicle_service import (
    create_vehicle,
    get_vehicles,
    get_vehicle,
    update_vehicle,
    delete_vehicle,
    get_service_locations,
    get_vehicle_makes,
    get_fuel_types,
    get_fuel_issues,
    get_statuses,
    get_suppliers
)



router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"]
)


@router.post("/")
def add_vehicle(
    data: VehicleCreate,
    db: Session = Depends(get_db)
):
    return create_vehicle(
        data,
        db
    )


@router.get("/")
def list_vehicles(
    db: Session = Depends(get_db)
):
    return get_vehicles(db)


@router.get("/{vehicle_id}")
def fetch_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    return get_vehicle(
        vehicle_id,
        db
    )



@router.get("/master-service-location/")
def service_locations(
    db: Session = Depends(get_db)
):
    return get_service_locations(db)


@router.get("/master-vehicle-make/")
def vehicle_makes(
    db: Session = Depends(get_db)
):
    return get_vehicle_makes(db)


@router.get("/master-fuel-type/")
def fuel_types(
    db: Session = Depends(get_db)
):
    return get_fuel_types(db)


@router.get("/master-fuel-issue/")
def fuel_issues(
    db: Session = Depends(get_db)
):
    return get_fuel_issues(db)


@router.get("/master-status/")
def statuses(
    db: Session = Depends(get_db)
):
    return get_statuses(db)


@router.get("/supplier/")
def suppliers(
    db: Session = Depends(get_db)
):
    return get_suppliers(db)


@router.put("/{vehicle_id}")
def edit_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db)
):
    return update_vehicle(
        vehicle_id,
        data,
        db
    )


@router.delete("/{vehicle_id}")
def remove_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    return delete_vehicle(
        vehicle_id,
        db
    )