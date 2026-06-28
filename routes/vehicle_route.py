# routes/vehicle_route.py

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from core.database import get_db
from services.vehicle_bulk_service import bulk_upload_vehicles_service
from schemas.vehicle_schema import VehicleCreate, VehicleUpdate
from services.vehicle_service import (
    create_vehicle as create_vehicle_service,
    get_vehicles,
    get_vehicle,
    update_vehicle as update_vehicle_service,
    delete_vehicle as delete_vehicle_service,
    get_service_locations,
    get_vehicle_makes,
    get_vehicle_models,
    get_fuel_types,
    get_fuel_issues,
    get_statuses,
    get_companies,
    get_transmission_types,
    get_tax_statuses,
    get_suppliers
)
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


# ----------- Master Dropdowns -----------
# MUST be defined BEFORE /{vehicle_id} routes

@router.get("/master/service-location")
def service_locations(db: Session = Depends(get_db)):
    return get_service_locations(db)


@router.get("/master/vehicle-make")
def vehicle_makes(db: Session = Depends(get_db)):
    return get_vehicle_makes(db)


@router.get("/master/vehicle-model")
def vehicle_models(
    make_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_vehicle_models(db, make_id)


@router.get("/master/fuel-type")
def fuel_types(db: Session = Depends(get_db)):
    return get_fuel_types(db)


@router.get("/master/fuel-issue")
def fuel_issues(db: Session = Depends(get_db)):
    return get_fuel_issues(db)


@router.get("/master/status")
def statuses(db: Session = Depends(get_db)):
    return get_statuses(db)


@router.get("/master/company")
def companies(db: Session = Depends(get_db)):
    return get_companies(db)


@router.get("/master/transmission-type")
def transmission_types(db: Session = Depends(get_db)):
    return get_transmission_types(db)


@router.get("/master/tax-status")
def tax_statuses(db: Session = Depends(get_db)):
    return get_tax_statuses(db)


@router.get("/master/supplier")
def suppliers(db: Session = Depends(get_db)):
    return get_suppliers(db)


# ----------- Bulk Upload -----------

@router.post("/bulk-upload")
async def bulk_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await bulk_upload_vehicles_service(file, db, current_user)


# ----------- CRUD -----------
# /{vehicle_id} routes LAST so they don't swallow /master/* paths

@router.post("/")
def create_vehicle(
    data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_vehicle_service(data, db, current_user)


@router.get("/")
def list_vehicles(db: Session = Depends(get_db)):
    return get_vehicles(db)


@router.get("/{vehicle_id}")
def fetch_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return get_vehicle(vehicle_id, db)


@router.put("/{vehicle_id}")
def update_vehicle_route(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return update_vehicle_service(vehicle_id, data, db, current_user)


@router.delete("/{vehicle_id}")
def delete_vehicle_route(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return delete_vehicle_service(vehicle_id, db)