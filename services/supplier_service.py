from fastapi import HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
import os
import shutil
import uuid
from sqlalchemy.exc import IntegrityError, DataError

from models.generated_models import (
    Suppliers,
    MasterSupplierType,
    MasterServiceLocation,
    MasterBranch,
)
from utils.code_generators import generate_supplier_code

UPLOAD_ROOT = "uploads/suppliers"  # relative to app's cwd, matches StaticFiles mount

DOC_URL_FIELDS = [
    "adhaar_url",
    "photo_url",
    "license_file_url",
    "pancard_file_url",
    "bank_passbook_photo_url",
    "gas_bill_photo_url",
    "electricity_bill_photo_url",
]


# ── helpers ───────────────────────────────────────────────────────────────────

def _build_file_url(request: Request, path: str | None) -> str | None:
    """
    Converts a stored relative path  →  full public URL.

    Stored value examples:
        uploads/suppliers/aadhar/file.jpg
        /uploads/suppliers/photo/img.png
        https://already-absolute.com/file.pdf   ← returned as-is
    """
    if not path:
        return None
    if path.startswith("http://") or path.startswith("https://"):
        return path
    clean = path.lstrip("/")
    base = str(request.base_url).rstrip("/")
    return f"{base}/{clean}"


def attach_file_urls(supplier: Suppliers, request: Request) -> Suppliers:
    """
    Mutates the in-memory supplier object so its *_url fields are absolute,
    right before it's serialized into SupplierResponse.
    """
    for field in DOC_URL_FIELDS:
        raw_value = getattr(supplier, field, None)
        setattr(supplier, field, _build_file_url(request, raw_value))
    return supplier


# =========================
# CREATE SUPPLIER
# =========================

def create_supplier(db: Session, supplier):
    existing_mobile = db.query(Suppliers).filter(Suppliers.mobile == supplier.mobile).first()
    if existing_mobile:
        raise HTTPException(status_code=400, detail="Mobile already exists")

    if supplier.aadhaar_number:
        existing_aadhaar = db.query(Suppliers).filter(Suppliers.aadhaar_number == supplier.aadhaar_number).first()
        if existing_aadhaar:
            raise HTTPException(status_code=400, detail="Aadhaar number already exists")

    supplier_data = supplier.dict()

    # ── auto-generate supplier_code if not supplied ──────────────────────
    provided_code = (supplier_data.get("supplier_code") or "").strip()

    if not provided_code:
        for _ in range(5):
            candidate = generate_supplier_code(db)
            clash = db.query(Suppliers).filter(Suppliers.supplier_code == candidate).first()
            if not clash:
                supplier_data["supplier_code"] = candidate
                break
        else:
            raise HTTPException(status_code=500, detail="Could not generate a unique supplier code")
    else:
        existing_code = db.query(Suppliers).filter(Suppliers.supplier_code == provided_code).first()
        if existing_code:
            raise HTTPException(status_code=400, detail="Supplier code already exists")
        supplier_data["supplier_code"] = provided_code

    try:
        new_supplier = Suppliers(**supplier_data)
        db.add(new_supplier)
        db.commit()
        db.refresh(new_supplier)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database constraint violated: {str(e.orig)}")
    except TypeError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Schema/model mismatch: {str(e)}")

    return new_supplier


def get_suppliers(db: Session, request: Request):
    suppliers = db.query(Suppliers).order_by(Suppliers.id.desc()).all()
    return [attach_file_urls(s, request) for s in suppliers]


def get_supplier(db: Session, supplier_id: int):
    return db.query(Suppliers).filter(Suppliers.id == supplier_id).first()


def update_supplier(db: Session, supplier_id: int, supplier_data):
    supplier = get_supplier(db, supplier_id)

    if not supplier:
        return None

    update_data = supplier_data.dict(exclude_unset=True)

    # if someone tries to blank out supplier_code on update, ignore it
    if "supplier_code" in update_data and not (update_data["supplier_code"] or "").strip():
        update_data.pop("supplier_code")

    for key, value in update_data.items():
        setattr(supplier, key, value)

    db.commit()
    db.refresh(supplier)

    return supplier


def delete_supplier(db: Session, supplier_id: int):
    supplier = get_supplier(db, supplier_id)

    if not supplier:
        return None

    db.delete(supplier)
    db.commit()

    return True


# =========================
# MASTER SUPPLIER TYPE
# =========================

def get_supplier_types(db: Session):
    return db.query(MasterSupplierType).all()


# =========================
# MASTER SERVICE LOCATION
# =========================

def get_service_locations(db: Session):
    return db.query(MasterServiceLocation).all()


# =========================
# MASTER BRANCH
# =========================

def get_branches(db: Session):
    return db.query(MasterBranch).all()


# =========================
# DOCUMENTS FETCH
# =========================

def get_supplier_documents_service(db, supplier_id: int, request: Request):

    supplier = db.query(Suppliers).filter(Suppliers.id == supplier_id).first()

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return {
       
        "supplier_code": supplier.supplier_code,
        "supplier_name": supplier.supplier_name,
        "documents": {
            "adhaar_url": _build_file_url(request, supplier.adhaar_url),
            "photo_url": _build_file_url(request, supplier.photo_url),
            "license_file_url": _build_file_url(request, supplier.license_file_url),
            "pancard_file_url": _build_file_url(request, supplier.pancard_file_url),
            "bank_passbook_photo_url": _build_file_url(request, supplier.bank_passbook_photo_url),
            "gas_bill_photo_url": _build_file_url(request, supplier.gas_bill_photo_url),
            "electricity_bill_photo_url": _build_file_url(request, supplier.electricity_bill_photo_url),
        }
    }


# =========================
# DOCUMENT UPLOAD
# =========================

def upload_supplier_document_service(field: str, file: UploadFile):

    allowed_fields = set(DOC_URL_FIELDS)
    if field not in allowed_fields:
        raise HTTPException(status_code=400, detail="Invalid document field")

    os.makedirs(UPLOAD_ROOT, exist_ok=True)

    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".pdf"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG, WEBP and PDF files are allowed"
        )

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_ROOT, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "url": f"/uploads/suppliers/{filename}"
    }