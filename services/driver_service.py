from fastapi import HTTPException, Request
from models.generated_models import Drivers, MasterBranch, MasterServiceLocation, MasterSupplierType
from fastapi import UploadFile, File, HTTPException
UPLOAD_ROOT = "uploads/drivers"  # relative to app's cwd, matches your StaticFiles mount

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


# ── CRUD ──────────────────────────────────────────────────────────────────────

def create_driver_service(db, payload, current_user):

    existing_driver = (
        db.query(Drivers)
        .filter(Drivers.mobile == payload.mobile)
        .first()
    )
    if existing_driver:
        raise HTTPException(status_code=400, detail="Mobile already exists")

    if payload.driver_code:
        existing_code = db.query(Drivers).filter(Drivers.driver_code == payload.driver_code).first()
        if existing_code:
            raise HTTPException(status_code=400, detail="Driver code already exists")

    if payload.aadhaar_number:
        existing_aadhaar = db.query(Drivers).filter(Drivers.aadhaar_number == payload.aadhaar_number).first()
        if existing_aadhaar:
            raise HTTPException(status_code=400, detail="Aadhaar number already exists")

    if payload.license_number:
        existing_license = db.query(Drivers).filter(Drivers.license_number == payload.license_number).first()
        if existing_license:
            raise HTTPException(status_code=400, detail="License number already exists")

    driver = Drivers(
        driver_code=payload.driver_code,
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


def get_drivers_service(db):
    return db.query(Drivers).order_by(Drivers.id.desc()).all()


def get_driver_service(db, driver_id):
    driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


def update_driver_service(db, driver_id, payload):
    driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

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


# ── KEY FUNCTION: now accepts `request` to build absolute URLs ────────────────

def get_driver_documents_service(db, driver_id: int, request: Request):
    driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # Map of field_key → stored path
    raw_documents = {
        "adhaar_url":                 driver.adhaar_url,
        "license_file_url":           driver.license_file_url,
        "pancard_file_url":           driver.pancard_file_url,
        "bank_passbook_photo_url":    driver.bank_passbook_photo_url,
        "gas_bill_photo_url":         driver.gas_bill_photo_url,
        "electricity_bill_photo_url": driver.electricity_bill_photo_url,
        "driver_photo_url":           driver.driver_photo_url,
    }

    # Build full public URLs
    documents_with_urls = {
        key: _build_file_url(request, path)
        for key, path in raw_documents.items()
    }

    uploaded_documents = {k: v for k, v in documents_with_urls.items() if v}

    return {
        "driver_id":       driver.id,
        "driver_code":     driver.driver_code,
        "full_name":       driver.full_name,
        "documents":       documents_with_urls,   # all fields (nulls included)
        "uploaded":        uploaded_documents,     # only uploaded ones
        "total_uploaded":  len(uploaded_documents),
        "total_fields":    len(documents_with_urls),
    }



def upload_driver_document_service(db, driver_id: int, field: str, file: UploadFile):
    driver = db.query(Drivers).filter(Drivers.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    allowed_fields = {
        "adhaar_url", "license_file_url", "pancard_file_url",
        "bank_passbook_photo_url", "gas_bill_photo_url",
        "electricity_bill_photo_url", "driver_photo_url",
    }
    if field not in allowed_fields:
        raise HTTPException(status_code=400, detail="Invalid document field")

    os.makedirs(UPLOAD_ROOT, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    filename = f"{field}_{driver_id}{ext}"
    disk_path = os.path.join(UPLOAD_ROOT, filename)

    with open(disk_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Stored relative path — _build_file_url() turns this into a full URL later
    stored_path = f"uploads/drivers/{filename}"
    setattr(driver, field, stored_path)

    db.commit()
    db.refresh(driver)
    return driver