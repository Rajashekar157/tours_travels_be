# import os
# import shutil
# import uuid

# from fastapi import HTTPException, Request
# from models.generated_models import Drivers, MasterBranch, MasterServiceLocation, MasterSupplierType
# from fastapi import UploadFile, File, HTTPException

# UPLOAD_ROOT = "uploads/drivers"  # relative to app's cwd, matches your StaticFiles mount

# ALLOWED_DOCUMENT_FIELDS = {
#     "adhaar_url", "license_file_url", "pancard_file_url",
#     "bank_passbook_photo_url", "gas_bill_photo_url",
#     "electricity_bill_photo_url", "driver_photo_url",
# }

# ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}

# # ── helpers ───────────────────────────────────────────────────────────────────

# def _build_file_url(request: Request, path: str | None) -> str | None:
#     """
#     Converts a stored relative path  →  full public URL.

#     Stored value examples:
#         uploads/drivers/aadhar/file.jpg
#         /uploads/drivers/photo/img.png
#         https://already-absolute.com/file.pdf   ← returned as-is
#     """
#     if not path:
#         return None
#     if path.startswith("http://") or path.startswith("https://"):
#         return path
#     # Normalise leading slash
#     clean = path.lstrip("/")
#     base  = str(request.base_url).rstrip("/")
#     return f"{base}/{clean}"


# # ── CRUD ──────────────────────────────────────────────────────────────────────

# def create_driver_service(db, payload, current_user):

#     existing_driver = (
#         db.query(Drivers)
#         .filter(Drivers.mobile == payload.mobile)
#         .first()
#     )
#     if existing_driver:
#         raise HTTPException(status_code=400, detail="Mobile already exists")

#     if payload.driver_code:
#         existing_code = db.query(Drivers).filter(Drivers.driver_code == payload.driver_code).first()
#         if existing_code:
#             raise HTTPException(status_code=400, detail="Driver code already exists")

#     if payload.aadhaar_number:
#         existing_aadhaar = db.query(Drivers).filter(Drivers.aadhaar_number == payload.aadhaar_number).first()
#         if existing_aadhaar:
#             raise HTTPException(status_code=400, detail="Aadhaar number already exists")

#     if payload.license_number:
#         existing_license = db.query(Drivers).filter(Drivers.license_number == payload.license_number).first()
#         if existing_license:
#             raise HTTPException(status_code=400, detail="License number already exists")

#     driver = Drivers(
#         driver_code=payload.driver_code,
#         full_name=payload.full_name,
#         mobile=payload.mobile,
#         email=payload.email,

#         aadhaar_number=payload.aadhaar_number,
#         adhaar_url=payload.adhaar_url,

#         license_number=payload.license_number,
#         license_file_url=payload.license_file_url,
#         license_expiry=payload.license_expiry,

#         driver_photo_url=payload.driver_photo_url,

#         date_of_birth=payload.date_of_birth,
#         joining_date=payload.joining_date,

#         address=payload.address,
#         city=payload.city,
#         state=payload.state,
#         pincode=payload.pincode,

#         location_id=payload.location_id,
#         branch_id=payload.branch_id,

#         permanent_address=payload.permanent_address,
#         temporary_address=payload.temporary_address,

#         pancard_number=payload.pancard_number,
#         pancard_file_url=payload.pancard_file_url,

#         bank_passbook_photo_url=payload.bank_passbook_photo_url,
#         gas_bill_photo_url=payload.gas_bill_photo_url,
#         electricity_bill_photo_url=payload.electricity_bill_photo_url,

#         reference_person_name=payload.reference_person_name,
#         reference_contact_number_1=payload.reference_contact_number_1,
#         reference_contact_number_2=payload.reference_contact_number_2,

#         emergency_contact_name=payload.emergency_contact_name,
#         emergency_contact_number=payload.emergency_contact_number,
#         supplier_type_id=payload.supplier_type_id,

#         blood_group=payload.blood_group,
#         character_nature=payload.character_nature,

#         user_id=current_user["user_id"],
#         created_by=current_user["user_id"],
#         updated_by=current_user["user_id"],

#         status_id=payload.status_id,
#         is_active=payload.is_active if payload.is_active is not None else True,
#     )

#     db.add(driver)
#     db.commit()
#     db.refresh(driver)
#     return driver


# def get_drivers_service(db, request: Request):
#     drivers = db.query(Drivers).order_by(Drivers.id.desc()).all()

#     result = []
#     for driver in drivers:
#         # Convert the ORM row to a plain dict of its own columns, then
#         # overwrite driver_photo_url with a fully-resolved absolute URL —
#         # the same treatment the /documents endpoint already gives it, so
#         # the frontend never has to guess how to build the path itself and
#         # can just render driver.driver_photo_url directly as an <img src>.
#         row = {c.name: getattr(driver, c.name) for c in driver.__table__.columns}
#         row["driver_photo_url"] = _build_file_url(request, driver.driver_photo_url)
#         result.append(row)

#     return result


# def get_driver_service(db, driver_id):
#     driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
#     if not driver:
#         raise HTTPException(status_code=404, detail="Driver not found")
#     return driver


# def update_driver_service(db, driver_id, payload):
#     driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
#     if not driver:
#         raise HTTPException(status_code=404, detail="Driver not found")

#     for key, value in payload.model_dump(exclude_unset=True).items():
#         setattr(driver, key, value)

#     db.commit()
#     db.refresh(driver)
#     return driver


# def delete_driver_service(db, driver_id):
#     driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
#     if not driver:
#         raise HTTPException(status_code=404, detail="Driver not found")

#     db.delete(driver)
#     db.commit()
#     return {"message": "Driver deleted successfully"}


# def search_driver_service(db, keyword):
#     return (
#         db.query(Drivers)
#         .filter(Drivers.full_name.ilike(f"%{keyword}%"))
#         .all()
#     )


# def get_locations_service(db):
#     return (
#         db.query(MasterServiceLocation)
#         .filter(MasterServiceLocation.is_active == True)
#         .order_by(MasterServiceLocation.location_name.asc())
#         .all()
#     )


# def get_branches_service(db, location_id=None):
#     query = db.query(MasterBranch).filter(MasterBranch.is_active == True)
#     if location_id:
#         query = query.filter(MasterBranch.location_id == location_id)
#     return query.order_by(MasterBranch.branch_name.asc()).all()


# def get_supplier_type_service(db):
#     supplier_type = db.query(MasterSupplierType).filter(MasterSupplierType.id == 1).first()
#     if not supplier_type:
#         raise HTTPException(status_code=404, detail="Supplier type not found")
#     return supplier_type



# def get_driver_documents_service(db, driver_id: int, request: Request):

#     driver = db.query(Drivers).filter(Drivers.id == driver_id).first()

#     if not driver:
#         raise HTTPException(status_code=404, detail="Driver not found")

#     documents = {
#         "adhaar_url": _build_file_url(request, driver.adhaar_url),
#         "license_file_url": _build_file_url(request, driver.license_file_url),
#         "pancard_file_url": _build_file_url(request, driver.pancard_file_url),
#         "bank_passbook_photo_url": _build_file_url(request, driver.bank_passbook_photo_url),
#         "gas_bill_photo_url": _build_file_url(request, driver.gas_bill_photo_url),
#         "electricity_bill_photo_url": _build_file_url(request, driver.electricity_bill_photo_url),
#         "driver_photo_url": _build_file_url(request, driver.driver_photo_url),
#     }

#     return {
#         "driver_id": driver.id,
#         "driver_code": driver.driver_code,
#         "full_name": driver.full_name,
#         "documents": documents,
#         "total_uploaded": sum(1 for v in documents.values() if v),
#         "total_fields": len(documents),
#     }


# def upload_driver_document_service(db, driver_id: int, field: str, file: UploadFile):
#     driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
#     if not driver:
#         raise HTTPException(status_code=404, detail="Driver not found")

#     if field not in ALLOWED_DOCUMENT_FIELDS:
#         raise HTTPException(status_code=400, detail="Invalid document field")

#     ext = os.path.splitext(file.filename or "")[1].lower()
#     if ext not in ALLOWED_EXTENSIONS:
#         raise HTTPException(
#             status_code=400,
#             detail="Only JPG, JPEG, PNG, WEBP and PDF files are allowed",
#         )

#     os.makedirs(UPLOAD_ROOT, exist_ok=True)

#     # UUID keeps filenames unique per upload (avoids stale browser/CDN caching
#     # on replace) while still being traceable back to the driver + field.
#     filename = f"{field}_{driver_id}_{uuid.uuid4().hex}{ext}"
#     disk_path = os.path.join(UPLOAD_ROOT, filename)

#     with open(disk_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Stored relative path — _build_file_url() turns this into a full URL later
#     stored_path = f"uploads/drivers/{filename}"
#     setattr(driver, field, stored_path)

#     db.commit()
#     db.refresh(driver)
#     return driver




import os
import shutil
import uuid

from fastapi import HTTPException, Request
from sqlalchemy import text
from models.generated_models import Drivers, MasterBranch, MasterServiceLocation, MasterSupplierType
from fastapi import UploadFile, File, HTTPException

UPLOAD_ROOT = "uploads/drivers"  # relative to app's cwd, matches your StaticFiles mount

ALLOWED_DOCUMENT_FIELDS = {
    "adhaar_url", "license_file_url", "pancard_file_url",
    "bank_passbook_photo_url", "gas_bill_photo_url",
    "electricity_bill_photo_url", "driver_photo_url",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}

# ── helpers ───────────────────────────────────────────────────────────────────

def _build_file_url(request: Request, path: str | None) -> str | None:
    """
    Converts a stored relative path  →  full public URL.

    Stored value examples:
        uploads/drivers/aadhar/file.jpg
        /uploads/drivers/photo/img.png
        https://already-absolute.com/file.pdf   ← returned as-is
    """
    if not path:
        return None
    if path.startswith("http://") or path.startswith("https://"):
        return path
    # Normalise leading slash
    clean = path.lstrip("/")
    base  = str(request.base_url).rstrip("/")
    return f"{base}/{clean}"


def generate_driver_code(db) -> str:
    """
    DRV-000001, DRV-000002, ... — generated via a raw SQL call to a
    Postgres sequence (driver_code_seq), NOT via ORM/model logic.

    nextval() is atomic at the database level, so two concurrent driver
    creations can never receive the same code — no read-then-increment
    race condition like a "SELECT MAX(id)+1" approach would have.
    """
    result = db.execute(text("SELECT nextval('driver_code_seq')")).scalar()
    return f"DRV-{str(result).zfill(6)}"


# ── CRUD ──────────────────────────────────────────────────────────────────────

def create_driver_service(db, payload, current_user):

    existing_driver = (
        db.query(Drivers)
        .filter(Drivers.mobile == payload.mobile)
        .first()
    )
    if existing_driver:
        raise HTTPException(status_code=400, detail="Mobile already exists")

    if payload.aadhaar_number:
        existing_aadhaar = db.query(Drivers).filter(Drivers.aadhaar_number == payload.aadhaar_number).first()
        if existing_aadhaar:
            raise HTTPException(status_code=400, detail="Aadhaar number already exists")

    if payload.license_number:
        existing_license = db.query(Drivers).filter(Drivers.license_number == payload.license_number).first()
        if existing_license:
            raise HTTPException(status_code=400, detail="License number already exists")

    # driver_code is no longer taken from the client — it's generated here,
    # guaranteed unique by the Postgres sequence, so the old
    # "check if driver_code already exists" block is no longer needed.
    driver = Drivers(
        driver_code=generate_driver_code(db),
        full_name=payload.full_name,
        mobile=payload.mobile,
        email=payload.email,

        aadhaar_number=payload.aadhaar_number,
        adhaar_url=payload.adhaar_url,

        license_number=payload.license_number,
        license_file_url=payload.license_file_url,
        license_expiry=payload.license_expiry,

        driver_photo_url=payload.driver_photo_url,

        date_of_birth=payload.date_of_birth,
        joining_date=payload.joining_date,

        address=payload.address,
        city=payload.city,
        state=payload.state,
        pincode=payload.pincode,

        location_id=payload.location_id,
        branch_id=payload.branch_id,

        permanent_address=payload.permanent_address,
        temporary_address=payload.temporary_address,

        pancard_number=payload.pancard_number,
        pancard_file_url=payload.pancard_file_url,

        bank_passbook_photo_url=payload.bank_passbook_photo_url,
        gas_bill_photo_url=payload.gas_bill_photo_url,
        electricity_bill_photo_url=payload.electricity_bill_photo_url,

        reference_person_name=payload.reference_person_name,
        reference_contact_number_1=payload.reference_contact_number_1,
        reference_contact_number_2=payload.reference_contact_number_2,

        emergency_contact_name=payload.emergency_contact_name,
        emergency_contact_number=payload.emergency_contact_number,
        supplier_type_id=payload.supplier_type_id,

        blood_group=payload.blood_group,
        character_nature=payload.character_nature,

        user_id=current_user["user_id"],
        created_by=current_user["user_id"],
        updated_by=current_user["user_id"],

        status_id=payload.status_id,
        is_active=payload.is_active if payload.is_active is not None else True,
    )

    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


def get_drivers_service(db, request: Request):
    drivers = db.query(Drivers).order_by(Drivers.id.desc()).all()

    result = []
    for driver in drivers:
        # Convert the ORM row to a plain dict of its own columns, then
        # overwrite driver_photo_url with a fully-resolved absolute URL —
        # the same treatment the /documents endpoint already gives it, so
        # the frontend never has to guess how to build the path itself and
        # can just render driver.driver_photo_url directly as an <img src>.
        row = {c.name: getattr(driver, c.name) for c in driver.__table__.columns}
        row["driver_photo_url"] = _build_file_url(request, driver.driver_photo_url)
        result.append(row)

    return result


def get_driver_service(db, driver_id):
    driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


def update_driver_service(db, driver_id, payload):
    driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # driver_code is intentionally excluded from DriverUpdate, so this
    # loop can never overwrite the generated code even if someone crafts
    # a raw request with a driver_code field — Pydantic will just ignore it.
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(driver, key, value)

    db.commit()
    db.refresh(driver)
    return driver


def delete_driver_service(db, driver_id):
    driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    db.delete(driver)
    db.commit()
    return {"message": "Driver deleted successfully"}


def search_driver_service(db, keyword):
    return (
        db.query(Drivers)
        .filter(Drivers.full_name.ilike(f"%{keyword}%"))
        .all()
    )


def get_locations_service(db):
    return (
        db.query(MasterServiceLocation)
        .filter(MasterServiceLocation.is_active == True)
        .order_by(MasterServiceLocation.location_name.asc())
        .all()
    )


def get_branches_service(db, location_id=None):
    query = db.query(MasterBranch).filter(MasterBranch.is_active == True)
    if location_id:
        query = query.filter(MasterBranch.location_id == location_id)
    return query.order_by(MasterBranch.branch_name.asc()).all()


def get_supplier_type_service(db):
    supplier_type = db.query(MasterSupplierType).filter(MasterSupplierType.id == 1).first()
    if not supplier_type:
        raise HTTPException(status_code=404, detail="Supplier type not found")
    return supplier_type



def get_driver_documents_service(db, driver_id: int, request: Request):

    driver = db.query(Drivers).filter(Drivers.id == driver_id).first()

    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    documents = {
        "adhaar_url": _build_file_url(request, driver.adhaar_url),
        "license_file_url": _build_file_url(request, driver.license_file_url),
        "pancard_file_url": _build_file_url(request, driver.pancard_file_url),
        "bank_passbook_photo_url": _build_file_url(request, driver.bank_passbook_photo_url),
        "gas_bill_photo_url": _build_file_url(request, driver.gas_bill_photo_url),
        "electricity_bill_photo_url": _build_file_url(request, driver.electricity_bill_photo_url),
        "driver_photo_url": _build_file_url(request, driver.driver_photo_url),
    }

    return {
        "driver_id": driver.id,
        "driver_code": driver.driver_code,
        "full_name": driver.full_name,
        "documents": documents,
        "total_uploaded": sum(1 for v in documents.values() if v),
        "total_fields": len(documents),
    }


def upload_driver_document_service(db, driver_id: int, field: str, file: UploadFile):
    driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    if field not in ALLOWED_DOCUMENT_FIELDS:
        raise HTTPException(status_code=400, detail="Invalid document field")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG, WEBP and PDF files are allowed",
        )

    os.makedirs(UPLOAD_ROOT, exist_ok=True)

    # UUID keeps filenames unique per upload (avoids stale browser/CDN caching
    # on replace) while still being traceable back to the driver + field.
    filename = f"{field}_{driver_id}_{uuid.uuid4().hex}{ext}"
    disk_path = os.path.join(UPLOAD_ROOT, filename)

    with open(disk_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Stored relative path — _build_file_url() turns this into a full URL later
    stored_path = f"uploads/drivers/{filename}"
    setattr(driver, field, stored_path)

    db.commit()
    db.refresh(driver)
    return driver