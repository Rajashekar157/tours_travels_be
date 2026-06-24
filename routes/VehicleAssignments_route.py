from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db

from schemas.VehicleAssignments_schema import (
    VehicleAssignmentCreate,
    VehicleAssignmentUpdate,
    VehicleAssignmentResponse
)

from services.VehicleAssignments_service import (
    create_vehicle_assignment,
    get_vehicle_assignments,
    get_vehicle_assignment,
    update_vehicle_assignment,
    delete_vehicle_assignment
)

router = APIRouter(
    prefix="/vehicle-assignments",
    tags=["Vehicle Assignments"]
)


@router.post(
    "/",
    response_model=VehicleAssignmentResponse
)
def create_assignment(
    data: VehicleAssignmentCreate,
    db: Session = Depends(get_db)
):
    return create_vehicle_assignment(
        data,
        db
    )


@router.get("/")
def get_assignments(
    db: Session = Depends(get_db)
):
    return get_vehicle_assignments(
        db
    )


@router.get("/{assignment_id}")
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    return get_vehicle_assignment(
        assignment_id,
        db
    )


@router.put("/{assignment_id}")
def update_assignment(
    assignment_id: int,
    data: VehicleAssignmentUpdate,
    db: Session = Depends(get_db)
):
    return update_vehicle_assignment(
        assignment_id,
        data,
        db
    )


@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    return delete_vehicle_assignment(
        assignment_id,
        db
    )