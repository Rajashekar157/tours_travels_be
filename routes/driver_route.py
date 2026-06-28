from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db

from schemas.driver_schema import (
    DriverCreate,
    DriverUpdate,
    MasterServiceLocationCreate,
    MasterServiceLocationUpdate,
    MasterBranchCreate,
    MasterBranchUpdate


)

from services.driver_service import (
    create_driver_service,
    get_drivers_service,
    get_driver_service,
    update_driver_service,
    delete_driver_service,
    search_driver_service,
    get_locations_service,
    get_branches_service

)

router = APIRouter(
    prefix="/drivers",
    tags=["Drivers"]
)


from utils.jwt_handler import get_current_user

@router.post("/")
def create_driver(
    payload: DriverCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_driver_service(
        db,
        payload,
        current_user
    )


@router.get("/")
def get_drivers(
    db: Session = Depends(get_db)
):
    return get_drivers_service(db)


@router.get("/search")
def search_driver(
    keyword: str,
    db: Session = Depends(get_db)
):
    return search_driver_service(
        db,
        keyword
    )


@router.get("/master-service-locations")
def get_locations(
    db: Session = Depends(get_db)
):
    return get_locations_service(db)

@router.get("/master-branch")
def get_branches(
    location_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_branches_service(db, location_id)



@router.get("/{driver_id}")
def get_driver(
    driver_id: int,
    db: Session = Depends(get_db)
):
    return get_driver_service(
        db,
        driver_id
    )


@router.put("/{driver_id}")
def update_driver(
    driver_id: int,
    payload: DriverUpdate,
    db: Session = Depends(get_db)
):
    return update_driver_service(
        db,
        driver_id,
        payload
    )


@router.delete("/{driver_id}")
def delete_driver(
    driver_id: int,
    db: Session = Depends(get_db)
):
    return delete_driver_service(
        db,
        driver_id
    )