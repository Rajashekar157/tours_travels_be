from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.orm import Session

from core.database import get_db
from utils.jwt_handler import get_current_user

from schemas.VehicleAssignments_schema import (
    VehicleAssignmentCreate,
    VehicleAssignmentUpdate,
)

from services.VehicleAssignments_service import (
    create_vehicle_assignment,
    get_vehicle_assignments,
    get_vehicle_assignment,
    get_assignment_chain,
    update_vehicle_assignment,
    delete_vehicle_assignment,
    upload_vehicle_assignment_document_service,
    get_vehicle_assignment_documents_service,
    attach_file_urls,
    get_available_vehicles,
    get_available_drivers,
    get_available_suppliers,
)

router = APIRouter(
    prefix="/vehicle-assignments",
    tags=["Vehicle Assignments"]
)


# =====================================================
# UPLOAD ASSIGNMENT DOCUMENT/PHOTO
# =====================================================

@router.post("/upload-document")
def upload_assignment_document(
    field: str,
    file: UploadFile = File(...),
):
    return upload_vehicle_assignment_document_service(field, file)


# =====================================================
# AVAILABILITY ENDPOINTS
# Must come BEFORE /{assignment_id} routes so FastAPI
# doesn't try to parse "available" as an integer.
# =====================================================

@router.get("/available/vehicles")
def available_vehicles(db: Session = Depends(get_db)):
    """Returns all vehicles not currently on an active Dispatch."""
    return get_available_vehicles(db)


@router.get("/available/drivers")
def available_drivers(request: Request, db: Session = Depends(get_db)):
    return get_available_drivers(db, request)


@router.get("/available/suppliers")
def available_suppliers(request: Request, db: Session = Depends(get_db)):
    return get_available_suppliers(db, request)


# =====================================================
# CREATE  — created_by from JWT
# =====================================================

@router.post("/")
def create_assignment(
    data: VehicleAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return create_vehicle_assignment(
        data,
        db,
        current_user["user_id"]
    )


# =====================================================
# GET ALL
# =====================================================

@router.get("/")
def get_assignments(
    request: Request,
    db: Session = Depends(get_db)
):
    assignments = get_vehicle_assignments(db)
    return [attach_file_urls(a, request) for a in assignments]


# ── Must come BEFORE /{assignment_id} so FastAPI doesn't match
# "documents" or "chain" as an int ──

@router.get("/{assignment_id}/documents")
def get_assignment_documents(
    assignment_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    return get_vehicle_assignment_documents_service(db, assignment_id, request)


@router.get("/chain/{chain_id}")
def get_chain(
    chain_id: str,
    db: Session = Depends(get_db),
):
    """
    Returns every row (Dispatch, Handover, Recovery, ...) that belongs to
    one vehicle's lifecycle, ordered chronologically — the full audit
    trail for a chain_id like 'CHN-000058'.
    """
    return get_assignment_chain(chain_id, db)


# =====================================================
# GET BY ID
# =====================================================

@router.get("/{assignment_id}")
def get_assignment(
    assignment_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    assignment = get_vehicle_assignment(assignment_id, db)
    return attach_file_urls(assignment, request)


# =====================================================
# UPDATE  — updated_by from JWT
# =====================================================

@router.put("/{assignment_id}")
def update_assignment(
    assignment_id: int,
    data: VehicleAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return update_vehicle_assignment(
        assignment_id,
        data,
        db,
        current_user["user_id"]
    )


# =====================================================
# DELETE  — updated_by tracked from JWT
# =====================================================

@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return delete_vehicle_assignment(
        assignment_id,
        db,
        current_user["user_id"]
    )