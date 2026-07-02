# from fastapi import HTTPException, UploadFile, Request
# from sqlalchemy.orm import Session
# from sqlalchemy import func
# from datetime import datetime
# import os, uuid, shutil

# from models.generated_models import (
#     VehicleAssignments,
#     Drivers,
#     Vehicles,
#     Suppliers,
#     Users,
# )

# from schemas.VehicleAssignments_schema import (
#     VehicleAssignmentCreate,
#     VehicleAssignmentUpdate
# )

# UPLOAD_DIR = "uploads/vehicle_assignments"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# FILE_FIELDS = [
#     "allotment_document_photo",
#     "vehicle_photo_front",
#     "vehicle_photo_back",
#     "vehicle_photo_left",
#     "vehicle_photo_right",
# ]

# # Driver/supplier photo fields — pulled from related tables, not
# # stored directly on VehicleAssignments, so they need the same
# # url-prefixing pass as FILE_FIELDS (see attach_file_urls below).
# PHOTO_URL_FIELDS = [
#     "driver_photo_url",
#     "supplier_photo_url",
# ]


# # =====================================================
# # AUTO GENERATE UNIQUE NUMBER  →  VUP-01, VUP-02 ...
# # =====================================================

# def generate_unique_number(db: Session) -> str:
#     last = (
#         db.query(VehicleAssignments.unique_number)
#         .filter(
#             VehicleAssignments.unique_number.isnot(None),
#             VehicleAssignments.unique_number.like("VUP-%")
#         )
#         .order_by(VehicleAssignments.id.desc())
#         .first()
#     )
#     if not last or not last.unique_number:
#         return "VUP-01"
#     try:
#         num = int(last.unique_number.split("-")[1])
#         return f"VUP-{str(num + 1).zfill(2)}"
#     except (IndexError, ValueError):
#         count = db.query(func.count(VehicleAssignments.id)).scalar()
#         return f"VUP-{str(count + 1).zfill(2)}"


# # =====================================================
# # FILE UPLOAD HELPERS
# # =====================================================

# def upload_vehicle_assignment_document_service(field: str, file: UploadFile):
#     """
#     Saves into uploads/vehicle_assignments/<field>/<uuid>.<ext>
#     Returns the relative path to store on the assignment row.
#     """
#     if field not in FILE_FIELDS:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid field '{field}'. Must be one of {FILE_FIELDS}"
#         )
#     field_dir = os.path.join(UPLOAD_DIR, field)
#     os.makedirs(field_dir, exist_ok=True)
#     ext = os.path.splitext(file.filename)[1]
#     filename = f"{uuid.uuid4().hex}{ext}"
#     filepath = os.path.join(field_dir, filename)
#     with open(filepath, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#     return {"field": field, "path": f"{UPLOAD_DIR}/{field}/{filename}"}


# def attach_file_urls(assignment_dict: dict, request: Request) -> dict:
#     base_url = str(request.base_url).rstrip("/")
#     for field in FILE_FIELDS + PHOTO_URL_FIELDS:
#         value = assignment_dict.get(field)
#         if value and not str(value).startswith("http"):
#             assignment_dict[field] = f"{base_url}/{value.lstrip('/')}"
#     return assignment_dict


# def get_vehicle_assignment_documents_service(db: Session, assignment_id: int, request: Request):
#     x = db.query(VehicleAssignments).filter(VehicleAssignments.id == assignment_id).first()
#     if not x:
#         raise HTTPException(status_code=404, detail="Assignment not found")
#     docs = {
#         "id": x.id,
#         "unique_number": x.unique_number,
#         "driver_name": x.driver.full_name if x.driver else None,
#         "vehicle_no": x.vehicle.vehicle_registration_number if x.vehicle else None,
#         "allotment_document_photo": x.allotment_document_photo,
#         "vehicle_photo_front": x.vehicle_photo_front,
#         "vehicle_photo_back": x.vehicle_photo_back,
#         "vehicle_photo_left": x.vehicle_photo_left,
#         "vehicle_photo_right": x.vehicle_photo_right,
#     }
#     return attach_file_urls(docs, request)


# # =====================================================
# # AVAILABILITY HELPERS
# # A vehicle/driver/supplier is BUSY only when it has
# # an active Dispatch (is_active=True, type="Dispatch").
# # Recovery / Handover mark those rows inactive, freeing
# # everything for the next Dispatch.
# # =====================================================

# def _busy_vehicle_ids(db: Session):
#     rows = (
#         db.query(VehicleAssignments.vehicle_id)
#         .filter(
#             VehicleAssignments.is_active == True,
#             VehicleAssignments.assignment_type == "Dispatch"
#         )
#         .all()
#     )
#     return {r.vehicle_id for r in rows}


# def _busy_driver_ids(db: Session):
#     rows = (
#         db.query(VehicleAssignments.driver_id)
#         .filter(
#             VehicleAssignments.is_active == True,
#             VehicleAssignments.assignment_type == "Dispatch",
#             VehicleAssignments.driver_id.isnot(None)
#         )
#         .all()
#     )
#     return {r.driver_id for r in rows}


# def _busy_supplier_ids(db: Session):
#     rows = (
#         db.query(VehicleAssignments.supplier_id)
#         .filter(
#             VehicleAssignments.is_active == True,
#             VehicleAssignments.assignment_type == "Dispatch",
#             VehicleAssignments.supplier_id.isnot(None)
#         )
#         .all()
#     )
#     return {r.supplier_id for r in rows}


# def get_available_vehicles(db: Session):
#     """All vehicles NOT in an active Dispatch."""
#     busy = _busy_vehicle_ids(db)
#     vehicles = db.query(Vehicles).all()
#     return [
#         {
#             "id": v.id,
#             "vehicle_registration_number": v.vehicle_registration_number,
#             "vehicle_display_number": v.vehicle_display_number,
#         }
#         for v in vehicles
#         if v.id not in busy
#     ]


# def get_available_drivers(db: Session, request: Request):
#     """All active drivers NOT in an active Dispatch."""
#     busy = _busy_driver_ids(db)
#     base_url = str(request.base_url).rstrip("/")
#     drivers = db.query(Drivers).filter(Drivers.is_active == True).all()

#     result = []
#     for d in drivers:
#         if d.id in busy:
#             continue
#         photo = d.driver_photo_url
#         if photo and not str(photo).startswith("http"):
#             photo = f"{base_url}/{str(photo).lstrip('/')}"
#         result.append({
#             "id": d.id,
#             "driver_code": d.driver_code,
#             "full_name": d.full_name,
#             "mobile": d.mobile,
#             "supplier_type_id": d.supplier_type_id,
#             "driver_photo_url": photo,
#         })
#     return result


# def get_available_suppliers(db: Session, request: Request):
#     """All suppliers NOT in an active Dispatch."""
#     busy = _busy_supplier_ids(db)
#     base_url = str(request.base_url).rstrip("/")
#     suppliers = db.query(Suppliers).all()

#     result = []
#     for s in suppliers:
#         if s.id in busy:
#             continue
#         photo = s.photo_url  # Suppliers.photo_url — confirmed column name
#         if photo and not str(photo).startswith("http"):
#             photo = f"{base_url}/{str(photo).lstrip('/')}"
#         result.append({
#             "id": s.id,
#             "supplier_code": s.supplier_code,
#             "supplier_name": s.supplier_name,
#             "mobile": s.mobile,
#             "supplier_type_id": s.supplier_type_id,
#             "outstanding_amount": float(s.outstanding_amount) if s.outstanding_amount else None,
#             "supplier_photo_url": photo,
#         })
#     return result


# # =====================================================
# # CREATE
# # =====================================================

# def create_vehicle_assignment(data: VehicleAssignmentCreate, db: Session, current_user_id: int):

#     # ── Validate vehicle ──────────────────────────────
#     vehicle = db.query(Vehicles).filter(Vehicles.id == data.vehicle_id).first()
#     if not vehicle:
#         raise HTTPException(status_code=404, detail="Vehicle not found")

#     # ── Validate driver (optional) ────────────────────
#     driver = None
#     if data.driver_id:
#         driver = db.query(Drivers).filter(Drivers.id == data.driver_id).first()
#         if not driver:
#             raise HTTPException(status_code=404, detail="Driver not found")

#     # ── Validate supplier (optional) ──────────────────
#     if data.supplier_id:
#         supplier = db.query(Suppliers).filter(Suppliers.id == data.supplier_id).first()
#         if not supplier:
#             raise HTTPException(status_code=404, detail="Supplier not found")

#     is_dispatch = data.assignment_type == "Dispatch"

#     if is_dispatch:
#         # Block if vehicle already locked by active Dispatch
#         if data.vehicle_id in _busy_vehicle_ids(db):
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Vehicle {vehicle.vehicle_registration_number} is already on an active Dispatch"
#             )
#         # Block if driver already locked by active Dispatch
#         if data.driver_id and data.driver_id in _busy_driver_ids(db):
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Driver {driver.full_name} is already on an active Dispatch"
#             )
#         # Block if supplier already locked by active Dispatch
#         if data.supplier_id and data.supplier_id in _busy_supplier_ids(db):
#             raise HTTPException(
#                 status_code=400,
#                 detail="This supplier is already on an active Dispatch"
#             )
#     else:
#         # Recovery / Handover — close all active rows for this vehicle
#         # (and for this driver if specified) so they become free again.
#         now_close = datetime.utcnow()

#         active_rows = db.query(VehicleAssignments).filter(
#             VehicleAssignments.vehicle_id == data.vehicle_id,
#             VehicleAssignments.is_active == True
#         ).all()

#         if data.driver_id:
#             driver_rows = db.query(VehicleAssignments).filter(
#                 VehicleAssignments.driver_id == data.driver_id,
#                 VehicleAssignments.is_active == True
#             ).all()
#             seen_ids = {r.id for r in active_rows}
#             active_rows += [r for r in driver_rows if r.id not in seen_ids]

#         for row in active_rows:
#             row.is_active = False
#             row.relieved_date = now_close
#             row.updated_by = current_user_id
#             row.updated_at = now_close

#     # ── Create the new assignment record ──────────────
#     unique_number  = generate_unique_number(db)
#     transaction_id = f"TXN-{unique_number}"
#     now            = datetime.utcnow()

#     assignment = VehicleAssignments(
#         unique_number=unique_number,
#         driver_id=data.driver_id,
#         vehicle_id=data.vehicle_id,
#         supplier_id=data.supplier_id,
#         service_location_id=data.service_location_id,
#         branch_id=data.branch_id,
#         vehicle_odometer_km=data.vehicle_odometer_km,
#         assignment_type=data.assignment_type,
#         transaction_id=transaction_id,
#         transaction_date=now,
#         allotment_document_photo=data.allotment_document_photo,
#         vehicle_photo_front=data.vehicle_photo_front,
#         vehicle_photo_back=data.vehicle_photo_back,
#         vehicle_photo_left=data.vehicle_photo_left,
#         vehicle_photo_right=data.vehicle_photo_right,
#         remarks=data.remarks,
#         created_by=current_user_id,
#         updated_by=current_user_id,
#         # Only a Dispatch row marks the vehicle/driver as "busy"
#         is_active=is_dispatch,
#         assigned_date=now
#     )

#     db.add(assignment)
#     db.commit()
#     db.refresh(assignment)

#     return {
#         "message": "Assignment created successfully",
#         "unique_number": assignment.unique_number,
#         "transaction_id": assignment.transaction_id,
#         "id": assignment.id
#     }


# # =====================================================
# # GET ALL
# # =====================================================

# def get_vehicle_assignments(db: Session):
#     assignments = db.query(VehicleAssignments).all()
#     result = []
#     for x in assignments:
#         result.append({
#             "id": x.id,
#             "unique_number": x.unique_number,
#             "driver_id": x.driver_id,
#             "vehicle_id": x.vehicle_id,
#             "supplier_id": x.supplier_id,
#             # Guard every driver field — driver_id is now nullable
#             "driver_code": x.driver.driver_code if x.driver else None,
#             "full_name": x.driver.full_name if x.driver else None,
#             "mobile": x.driver.mobile if x.driver else None,
#             "email": x.driver.email if x.driver else None,
#             "driver_photo_url": x.driver.driver_photo_url if x.driver else None,
#             "vehicle_no": x.vehicle.vehicle_registration_number,
#             "display_no": x.vehicle.vehicle_display_number,
#             "supplier_name": x.supplier.supplier_name if x.supplier else None,
#             "supplier_code": x.supplier.supplier_code if x.supplier else None,
#             "supplier_mobile": x.supplier.mobile if x.supplier else None,
#             "supplier_type_id": x.supplier.supplier_type_id if x.supplier else None,
#             "supplier_photo_url": x.supplier.photo_url if x.supplier else None,
#             "outstanding_amount": float(x.supplier.outstanding_amount) if x.supplier and x.supplier.outstanding_amount else None,
#             "service_location_id": x.service_location_id,
#             "branch_id": x.branch_id,
#             "vehicle_odometer_km": float(x.vehicle_odometer_km) if x.vehicle_odometer_km else None,
#             "assignment_type": x.assignment_type,
#             "assigned_date": x.assigned_date,
#             "relieved_date": x.relieved_date,
#             "transaction_id": x.transaction_id,
#             "transaction_date": x.transaction_date,
#             "allotment_document_photo": x.allotment_document_photo,
#             "vehicle_photo_front": x.vehicle_photo_front,
#             "vehicle_photo_back": x.vehicle_photo_back,
#             "vehicle_photo_left": x.vehicle_photo_left,
#             "vehicle_photo_right": x.vehicle_photo_right,
#             "is_active": x.is_active,
#             "remarks": x.remarks,
#             "created_by": x.created_by,
#             "updated_by": x.updated_by,
#             "created_by_name": x.users.full_name if x.users else None,
#             "updated_by_name": x.users_.full_name if x.users_ else None,
#         })
#     return result


# # =====================================================
# # GET BY ID
# # =====================================================

# def get_vehicle_assignment(assignment_id: int, db: Session):
#     x = db.query(VehicleAssignments).filter(VehicleAssignments.id == assignment_id).first()
#     if not x:
#         raise HTTPException(status_code=404, detail="Assignment not found")

#     return {
#         "id": x.id,
#         "unique_number": x.unique_number,
#         "driver_id": x.driver_id,
#         "vehicle_id": x.vehicle_id,
#         "supplier_id": x.supplier_id,
#         "driver_code": x.driver.driver_code if x.driver else None,
#         "full_name": x.driver.full_name if x.driver else None,
#         "mobile": x.driver.mobile if x.driver else None,
#         "driver_photo_url": x.driver.driver_photo_url if x.driver else None,
#         "vehicle_no": x.vehicle.vehicle_registration_number,
#         "display_no": x.vehicle.vehicle_display_number,
#         "supplier_name": x.supplier.supplier_name if x.supplier else None,
#         "supplier_code": x.supplier.supplier_code if x.supplier else None,
#         "supplier_mobile": x.supplier.mobile if x.supplier else None,
#         "supplier_type_id": x.supplier.supplier_type_id if x.supplier else None,
#         "supplier_photo_url": x.supplier.photo_url if x.supplier else None,
#         "outstanding_amount": float(x.supplier.outstanding_amount) if x.supplier and x.supplier.outstanding_amount else None,
#         "service_location_id": x.service_location_id,
#         "branch_id": x.branch_id,
#         "vehicle_odometer_km": float(x.vehicle_odometer_km) if x.vehicle_odometer_km else None,
#         "assignment_type": x.assignment_type,
#         "assigned_date": x.assigned_date,
#         "relieved_date": x.relieved_date,
#         "transaction_id": x.transaction_id,
#         "transaction_date": x.transaction_date,
#         "allotment_document_photo": x.allotment_document_photo,
#         "vehicle_photo_front": x.vehicle_photo_front,
#         "vehicle_photo_back": x.vehicle_photo_back,
#         "vehicle_photo_left": x.vehicle_photo_left,
#         "vehicle_photo_right": x.vehicle_photo_right,
#         "is_active": x.is_active,
#         "remarks": x.remarks,
#         "created_by": x.created_by,
#         "updated_by": x.updated_by,
#         "created_by_name": x.users.full_name if x.users else None,
#         "updated_by_name": x.users_.full_name if x.users_ else None,
#     }


# # =====================================================
# # UPDATE
# # =====================================================

# def update_vehicle_assignment(assignment_id: int, data: VehicleAssignmentUpdate, db: Session, current_user_id: int):
#     assignment = db.query(VehicleAssignments).filter(VehicleAssignments.id == assignment_id).first()
#     if not assignment:
#         raise HTTPException(status_code=404, detail="Assignment not found")

#     if data.driver_id:
#         existing = db.query(VehicleAssignments).filter(
#             VehicleAssignments.driver_id == data.driver_id,
#             VehicleAssignments.id != assignment_id,
#             VehicleAssignments.is_active == True,
#             VehicleAssignments.assignment_type == "Dispatch"
#         ).first()
#         if existing:
#             driver = db.query(Drivers).filter(Drivers.id == data.driver_id).first()
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Driver {driver.full_name} is already on an active Dispatch"
#             )

#     if data.vehicle_id:
#         existing = db.query(VehicleAssignments).filter(
#             VehicleAssignments.vehicle_id == data.vehicle_id,
#             VehicleAssignments.id != assignment_id,
#             VehicleAssignments.is_active == True,
#             VehicleAssignments.assignment_type == "Dispatch"
#         ).first()
#         if existing:
#             vehicle = db.query(Vehicles).filter(Vehicles.id == data.vehicle_id).first()
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Vehicle {vehicle.vehicle_registration_number} is already on an active Dispatch"
#             )

#     if data.supplier_id:
#         supplier = db.query(Suppliers).filter(Suppliers.id == data.supplier_id).first()
#         if not supplier:
#             raise HTTPException(status_code=404, detail="Supplier not found")

#     for key, value in data.model_dump(exclude_unset=True).items():
#         setattr(assignment, key, value)

#     assignment.updated_by = current_user_id
#     assignment.updated_at = datetime.utcnow()
#     db.commit()
#     db.refresh(assignment)
#     return {"message": "Assignment updated successfully"}


# # =====================================================
# # DELETE (soft)
# # =====================================================

# def delete_vehicle_assignment(assignment_id: int, db: Session, current_user_id: int):
#     assignment = db.query(VehicleAssignments).filter(VehicleAssignments.id == assignment_id).first()
#     if not assignment:
#         raise HTTPException(status_code=404, detail="Assignment not found")
#     assignment.is_active = False
#     assignment.updated_by = current_user_id
#     assignment.updated_at = datetime.utcnow()
#     db.commit()
#     return {"message": "Vehicle Assignment deleted successfully"}











from fastapi import HTTPException, UploadFile, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
import os, uuid, shutil

from models.generated_models import (
    VehicleAssignments,
    Drivers,
    Vehicles,
    Suppliers,
    Users,
)

from schemas.VehicleAssignments_schema import (
    VehicleAssignmentCreate,
    VehicleAssignmentUpdate
)

UPLOAD_DIR = "uploads/vehicle_assignments"
os.makedirs(UPLOAD_DIR, exist_ok=True)

FILE_FIELDS = [
    "allotment_document_photo",
    "vehicle_photo_front",
    "vehicle_photo_back",
    "vehicle_photo_left",
    "vehicle_photo_right",
]

PHOTO_URL_FIELDS = [
    "driver_photo_url",
    "supplier_photo_url",
]

# ── Per-type sequence + prefix. Each type advances independently and
# atomically via Postgres nextval() — no two requests can ever compute
# the same number, unlike the old "read last row, +1 in Python" approach
# that caused the drivers_driver_code_key UniqueViolation.
SEQUENCE_BY_TYPE = {
    "Dispatch": ("dispatch_seq", "DCO"),
    "Handover": ("handover_seq", "HO"),
    "Recovery": ("recovery_seq", "RC"),
}

# ── Explicit state machine. Keys are the vehicle's CURRENT active stage
# (None = idle, no active row at all). Values are the assignment_types
# legally allowed to be recorded next. Centralizing this here means the
# rule lives in exactly one place instead of being inferred from
# is_dispatch / busy-id checks scattered through the function.
VALID_TRANSITIONS = {
    None:       {"Dispatch"},
    "Dispatch": {"Handover", "Recovery"},
    "Handover": {"Recovery", "Dispatch"},
    "Recovery": {"Dispatch"},
}


# =====================================================
# AUTO GENERATE TRANSACTION NUMBER  →  DCO-000123, HO-000045, RC-000032
# One independent sequence per assignment_type.
# =====================================================

def generate_transaction_number(db: Session, assignment_type: str) -> str:
    seq_info = SEQUENCE_BY_TYPE.get(assignment_type)
    if not seq_info:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown assignment_type '{assignment_type}'"
        )
    seq_name, prefix = seq_info
    next_val = db.execute(text(f"SELECT nextval('{seq_name}')")).scalar()
    return f"{prefix}-{str(next_val).zfill(6)}"


def generate_chain_id(db: Session) -> str:
    next_val = db.execute(text("SELECT nextval('chain_seq')")).scalar()
    return f"CHN-{str(next_val).zfill(6)}"


# =====================================================
# FILE UPLOAD HELPERS
# =====================================================

def upload_vehicle_assignment_document_service(field: str, file: UploadFile):
    if field not in FILE_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid field '{field}'. Must be one of {FILE_FIELDS}"
        )
    field_dir = os.path.join(UPLOAD_DIR, field)
    os.makedirs(field_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(field_dir, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"field": field, "path": f"{UPLOAD_DIR}/{field}/{filename}"}


def attach_file_urls(assignment_dict: dict, request: Request) -> dict:
    base_url = str(request.base_url).rstrip("/")
    for field in FILE_FIELDS + PHOTO_URL_FIELDS:
        value = assignment_dict.get(field)
        if value and not str(value).startswith("http"):
            assignment_dict[field] = f"{base_url}/{value.lstrip('/')}"
    return assignment_dict


def get_vehicle_assignment_documents_service(db: Session, assignment_id: int, request: Request):
    x = db.query(VehicleAssignments).filter(VehicleAssignments.id == assignment_id).first()
    if not x:
        raise HTTPException(status_code=404, detail="Assignment not found")
    docs = {
        "id": x.id,
        "unique_number": x.unique_number,
        "driver_name": x.driver.full_name if x.driver else None,
        "vehicle_no": x.vehicle.vehicle_registration_number if x.vehicle else None,
        "allotment_document_photo": x.allotment_document_photo,
        "vehicle_photo_front": x.vehicle_photo_front,
        "vehicle_photo_back": x.vehicle_photo_back,
        "vehicle_photo_left": x.vehicle_photo_left,
        "vehicle_photo_right": x.vehicle_photo_right,
    }
    return attach_file_urls(docs, request)


# =====================================================
# AVAILABILITY HELPERS
# A vehicle/driver/supplier is BUSY only when it has an active Dispatch
# (is_active=True, type="Dispatch"). Recovery / Handover mark those rows
# inactive, freeing everything for the next Dispatch.
# =====================================================

def _busy_vehicle_ids(db: Session):
    rows = (
        db.query(VehicleAssignments.vehicle_id)
        .filter(
            VehicleAssignments.is_active == True,
            VehicleAssignments.assignment_type == "Dispatch"
        )
        .all()
    )
    return {r.vehicle_id for r in rows}


def _busy_driver_ids(db: Session):
    rows = (
        db.query(VehicleAssignments.driver_id)
        .filter(
            VehicleAssignments.is_active == True,
            VehicleAssignments.assignment_type == "Dispatch",
            VehicleAssignments.driver_id.isnot(None)
        )
        .all()
    )
    return {r.driver_id for r in rows}


def _busy_supplier_ids(db: Session):
    rows = (
        db.query(VehicleAssignments.supplier_id)
        .filter(
            VehicleAssignments.is_active == True,
            VehicleAssignments.assignment_type == "Dispatch",
            VehicleAssignments.supplier_id.isnot(None)
        )
        .all()
    )
    return {r.supplier_id for r in rows}


def get_available_vehicles(db: Session):
    busy = _busy_vehicle_ids(db)
    vehicles = db.query(Vehicles).all()
    return [
        {
            "id": v.id,
            "vehicle_registration_number": v.vehicle_registration_number,
            "vehicle_display_number": v.vehicle_display_number,
        }
        for v in vehicles
        if v.id not in busy
    ]


def get_available_drivers(db: Session, request: Request):
    busy = _busy_driver_ids(db)
    base_url = str(request.base_url).rstrip("/")
    drivers = db.query(Drivers).filter(Drivers.is_active == True).all()

    result = []
    for d in drivers:
        if d.id in busy:
            continue
        photo = d.driver_photo_url
        if photo and not str(photo).startswith("http"):
            photo = f"{base_url}/{str(photo).lstrip('/')}"
        result.append({
            "id": d.id,
            "driver_code": d.driver_code,
            "full_name": d.full_name,
            "mobile": d.mobile,
            "supplier_type_id": d.supplier_type_id,
            "driver_photo_url": photo,
        })
    return result


def get_available_suppliers(db: Session, request: Request):
    busy = _busy_supplier_ids(db)
    base_url = str(request.base_url).rstrip("/")
    suppliers = db.query(Suppliers).all()

    result = []
    for s in suppliers:
        if s.id in busy:
            continue
        photo = s.photo_url
        if photo and not str(photo).startswith("http"):
            photo = f"{base_url}/{str(photo).lstrip('/')}"
        result.append({
            "id": s.id,
            "supplier_code": s.supplier_code,
            "supplier_name": s.supplier_name,
            "mobile": s.mobile,
            "supplier_type_id": s.supplier_type_id,
            "outstanding_amount": float(s.outstanding_amount) if s.outstanding_amount else None,
            "supplier_photo_url": photo,
        })
    return result


# =====================================================
# STATE MACHINE HELPER
# Locks the vehicle row for the duration of the transaction (SELECT ...
# FOR UPDATE) and returns its current active stage. Holding this lock
# until commit/rollback means a second concurrent request for the SAME
# vehicle simply waits — it can't read stale "still active" state and
# create a duplicate/conflicting transition, which is what let two
# Handover rows both go through in the screenshot.
# =====================================================

def _get_current_stage_locked(db: Session, vehicle_id: int):
    """
    Returns (current_stage: str|None, active_row: VehicleAssignments|None)
    for the given vehicle, having taken a row lock on its active
    assignment (if any) so concurrent requests serialize here.
    """
    active_row = (
        db.query(VehicleAssignments)
        .filter(
            VehicleAssignments.vehicle_id == vehicle_id,
            VehicleAssignments.is_active == True
        )
        .with_for_update()
        .first()
    )
    return (active_row.assignment_type if active_row else None), active_row


# =====================================================
# CREATE
# Dispatch -> vehicle/driver/supplier must be free (state = Idle).
# Handover / Recovery -> closes the currently active row(s) for this
# vehicle (and driver, if given), inherits/starts chain_id, and links
# back via parent_assignment_id.
# =====================================================

def create_vehicle_assignment(data: VehicleAssignmentCreate, db: Session, current_user_id: int):

    vehicle = (
        db.query(Vehicles)
        .filter(Vehicles.id == data.vehicle_id)
        .with_for_update()   # lock this vehicle for the whole transaction
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    driver = None
    if data.driver_id:
        driver = db.query(Drivers).filter(Drivers.id == data.driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

    if data.supplier_id:
        supplier = db.query(Suppliers).filter(Suppliers.id == data.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")

    if not data.assignment_type:
        raise HTTPException(status_code=400, detail="assignment_type is required")

    # ── Enforce the state machine ──
    # Now safe from races: the vehicle row is locked above, so a second
    # concurrent request for this SAME vehicle blocks until this
    # transaction commits or rolls back, then re-reads fresh state.
    current_stage, active_row = _get_current_stage_locked(db, data.vehicle_id)

    if data.assignment_type not in VALID_TRANSITIONS.get(current_stage, set()):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot record {data.assignment_type} — vehicle "
                f"{vehicle.vehicle_registration_number}'s current stage is "
                f"{current_stage or 'Idle'}"
            )
        )

    is_dispatch = data.assignment_type == "Dispatch"

    if is_dispatch:
        # current_stage already confirmed Idle above, but driver/supplier
        # busy-elsewhere checks are independent of this specific vehicle.
        if data.driver_id and data.driver_id in _busy_driver_ids(db):
            raise HTTPException(
                status_code=400,
                detail=f"Driver {driver.full_name} is already on an active Dispatch"
            )
        if data.supplier_id and data.supplier_id in _busy_supplier_ids(db):
            raise HTTPException(
                status_code=400,
                detail="This supplier is already on an active Dispatch"
            )

    parent_assignment_id = None
    chain_id = None

    if not is_dispatch:
        # Handover / Recovery — close the active row(s) for this vehicle
        # (and driver, if specified), remember the parent, and inherit
        # its chain_id so the whole lifecycle stays grouped.
        now_close = datetime.utcnow()

        active_rows = db.query(VehicleAssignments).filter(
            VehicleAssignments.vehicle_id == data.vehicle_id,
            VehicleAssignments.is_active == True
        ).all()

        if data.driver_id:
            driver_rows = db.query(VehicleAssignments).filter(
                VehicleAssignments.driver_id == data.driver_id,
                VehicleAssignments.is_active == True
            ).all()
            seen_ids = {r.id for r in active_rows}
            active_rows += [r for r in driver_rows if r.id not in seen_ids]

        if active_rows:
            dispatch_row = next(
                (r for r in active_rows if r.assignment_type == "Dispatch"), None
            )
            parent_row = dispatch_row or active_rows[0]
            parent_assignment_id = parent_row.id
            chain_id = parent_row.chain_id

        for row in active_rows:
            row.is_active = False
            row.relieved_date = now_close
            row.updated_by = current_user_id
            row.updated_at = now_close

    if chain_id is None:
        # New Dispatch, or an orphaned Handover/Recovery with no
        # traceable parent — start a fresh chain.
        chain_id = generate_chain_id(db)

    unique_number  = generate_transaction_number(db, data.assignment_type)
    transaction_id = f"TXN-{unique_number}"
    now            = datetime.utcnow()

    assignment = VehicleAssignments(
        unique_number=unique_number,
        chain_id=chain_id,
        driver_id=data.driver_id,
        vehicle_id=data.vehicle_id,
        supplier_id=data.supplier_id,
        service_location_id=data.service_location_id,
        branch_id=data.branch_id,
        vehicle_odometer_km=data.vehicle_odometer_km,
        assignment_type=data.assignment_type,
        transaction_id=transaction_id,
        transaction_date=now,
        parent_assignment_id=parent_assignment_id,
        allotment_document_photo=data.allotment_document_photo,
        vehicle_photo_front=data.vehicle_photo_front,
        vehicle_photo_back=data.vehicle_photo_back,
        vehicle_photo_left=data.vehicle_photo_left,
        vehicle_photo_right=data.vehicle_photo_right,
        remarks=data.remarks,
        created_by=current_user_id,
        updated_by=current_user_id,
        is_active=is_dispatch,
        assigned_date=now
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "message": f"{data.assignment_type} recorded successfully",
        "unique_number": assignment.unique_number,
        "chain_id": assignment.chain_id,
        "transaction_id": assignment.transaction_id,
        "id": assignment.id
    }


# =====================================================
# GET ALL
# =====================================================

def get_vehicle_assignments(db: Session):
    assignments = db.query(VehicleAssignments).all()
    result = []
    for x in assignments:
        result.append({
            "id": x.id,
            "unique_number": x.unique_number,
            "chain_id": x.chain_id,
            "driver_id": x.driver_id,
            "vehicle_id": x.vehicle_id,
            "supplier_id": x.supplier_id,
            "driver_code": x.driver.driver_code if x.driver else None,
            "full_name": x.driver.full_name if x.driver else None,
            "mobile": x.driver.mobile if x.driver else None,
            "email": x.driver.email if x.driver else None,
            "driver_photo_url": x.driver.driver_photo_url if x.driver else None,
            "vehicle_no": x.vehicle.vehicle_registration_number,
            "display_no": x.vehicle.vehicle_display_number,
            "supplier_name": x.supplier.supplier_name if x.supplier else None,
            "supplier_code": x.supplier.supplier_code if x.supplier else None,
            "supplier_mobile": x.supplier.mobile if x.supplier else None,
            "supplier_type_id": x.supplier.supplier_type_id if x.supplier else None,
            "supplier_photo_url": x.supplier.photo_url if x.supplier else None,
            "outstanding_amount": float(x.supplier.outstanding_amount) if x.supplier and x.supplier.outstanding_amount else None,
            "service_location_id": x.service_location_id,
            "branch_id": x.branch_id,
            "vehicle_odometer_km": float(x.vehicle_odometer_km) if x.vehicle_odometer_km else None,
            "assignment_type": x.assignment_type,
            "assigned_date": x.assigned_date,
            "relieved_date": x.relieved_date,
            "transaction_id": x.transaction_id,
            "transaction_date": x.transaction_date,
            "parent_assignment_id": x.parent_assignment_id,
            "parent_unique_number": x.parent_assignment.unique_number if x.parent_assignment else None,
            "allotment_document_photo": x.allotment_document_photo,
            "vehicle_photo_front": x.vehicle_photo_front,
            "vehicle_photo_back": x.vehicle_photo_back,
            "vehicle_photo_left": x.vehicle_photo_left,
            "vehicle_photo_right": x.vehicle_photo_right,
            "is_active": x.is_active,
            "remarks": x.remarks,
            "created_by": x.created_by,
            "updated_by": x.updated_by,
            "created_by_name": x.users.full_name if x.users else None,
            "updated_by_name": x.users_.full_name if x.users_ else None,
        })
    return result


# =====================================================
# GET BY ID
# =====================================================

def get_vehicle_assignment(assignment_id: int, db: Session):
    x = db.query(VehicleAssignments).filter(VehicleAssignments.id == assignment_id).first()
    if not x:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return {
        "id": x.id,
        "unique_number": x.unique_number,
        "chain_id": x.chain_id,
        "driver_id": x.driver_id,
        "vehicle_id": x.vehicle_id,
        "supplier_id": x.supplier_id,
        "driver_code": x.driver.driver_code if x.driver else None,
        "full_name": x.driver.full_name if x.driver else None,
        "mobile": x.driver.mobile if x.driver else None,
        "driver_photo_url": x.driver.driver_photo_url if x.driver else None,
        "vehicle_no": x.vehicle.vehicle_registration_number,
        "display_no": x.vehicle.vehicle_display_number,
        "supplier_name": x.supplier.supplier_name if x.supplier else None,
        "supplier_code": x.supplier.supplier_code if x.supplier else None,
        "supplier_mobile": x.supplier.mobile if x.supplier else None,
        "supplier_type_id": x.supplier.supplier_type_id if x.supplier else None,
        "supplier_photo_url": x.supplier.photo_url if x.supplier else None,
        "outstanding_amount": float(x.supplier.outstanding_amount) if x.supplier and x.supplier.outstanding_amount else None,
        "service_location_id": x.service_location_id,
        "branch_id": x.branch_id,
        "vehicle_odometer_km": float(x.vehicle_odometer_km) if x.vehicle_odometer_km else None,
        "assignment_type": x.assignment_type,
        "assigned_date": x.assigned_date,
        "relieved_date": x.relieved_date,
        "transaction_id": x.transaction_id,
        "transaction_date": x.transaction_date,
        "parent_assignment_id": x.parent_assignment_id,
        "parent_unique_number": x.parent_assignment.unique_number if x.parent_assignment else None,
        "allotment_document_photo": x.allotment_document_photo,
        "vehicle_photo_front": x.vehicle_photo_front,
        "vehicle_photo_back": x.vehicle_photo_back,
        "vehicle_photo_left": x.vehicle_photo_left,
        "vehicle_photo_right": x.vehicle_photo_right,
        "is_active": x.is_active,
        "remarks": x.remarks,
        "created_by": x.created_by,
        "updated_by": x.updated_by,
        "created_by_name": x.users.full_name if x.users else None,
        "updated_by_name": x.users_.full_name if x.users_ else None,
    }


# =====================================================
# GET CHAIN — every row belonging to one vehicle lifecycle
# =====================================================

def get_assignment_chain(chain_id: str, db: Session):
    rows = (
        db.query(VehicleAssignments)
        .filter(VehicleAssignments.chain_id == chain_id)
        .order_by(VehicleAssignments.assigned_date.asc())
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Chain not found")
    return [
        {
            "id": x.id,
            "unique_number": x.unique_number,
            "assignment_type": x.assignment_type,
            "assigned_date": x.assigned_date,
            "relieved_date": x.relieved_date,
            "is_active": x.is_active,
            "driver_name": x.driver.full_name if x.driver else None,
            "supplier_name": x.supplier.supplier_name if x.supplier else None,
        }
        for x in rows
    ]


# =====================================================
# UPDATE
# =====================================================

def update_vehicle_assignment(assignment_id: int, data: VehicleAssignmentUpdate, db: Session, current_user_id: int):
    assignment = db.query(VehicleAssignments).filter(VehicleAssignments.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if data.driver_id:
        existing = db.query(VehicleAssignments).filter(
            VehicleAssignments.driver_id == data.driver_id,
            VehicleAssignments.id != assignment_id,
            VehicleAssignments.is_active == True,
            VehicleAssignments.assignment_type == "Dispatch"
        ).first()
        if existing:
            driver = db.query(Drivers).filter(Drivers.id == data.driver_id).first()
            raise HTTPException(
                status_code=400,
                detail=f"Driver {driver.full_name} is already on an active Dispatch"
            )

    if data.vehicle_id:
        existing = db.query(VehicleAssignments).filter(
            VehicleAssignments.vehicle_id == data.vehicle_id,
            VehicleAssignments.id != assignment_id,
            VehicleAssignments.is_active == True,
            VehicleAssignments.assignment_type == "Dispatch"
        ).first()
        if existing:
            vehicle = db.query(Vehicles).filter(Vehicles.id == data.vehicle_id).first()
            raise HTTPException(
                status_code=400,
                detail=f"Vehicle {vehicle.vehicle_registration_number} is already on an active Dispatch"
            )

    if data.supplier_id:
        supplier = db.query(Suppliers).filter(Suppliers.id == data.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(assignment, key, value)

    assignment.updated_by = current_user_id
    assignment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assignment)
    return {"message": "Assignment updated successfully"}


# =====================================================
# DELETE (soft)
# =====================================================

def delete_vehicle_assignment(assignment_id: int, db: Session, current_user_id: int):
    assignment = db.query(VehicleAssignments).filter(VehicleAssignments.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment.is_active = False
    assignment.updated_by = current_user_id
    assignment.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Vehicle Assignment deleted successfully"}