from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session

from core.database import get_db

from schemas.supplier_schema import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse
)

from services.supplier_service import (
    create_supplier,
    get_suppliers,
    get_supplier,
    update_supplier,
    delete_supplier,
    get_supplier_types,
    get_service_locations,
    get_branches,
    get_supplier_documents_service,
    upload_supplier_document_service,
    attach_file_urls,
)

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


# =========================
# MASTER SUPPLIER TYPE
# =========================

@router.get("/master-supplier-type")
def fetch_supplier_types(db: Session = Depends(get_db)):
    return get_supplier_types(db)


@router.get("/list/suppliers")
def list_suppliers(request: Request, db: Session = Depends(get_db)):
    return get_suppliers(db, request)
# =========================
# MASTER SERVICE LOCATION
# =========================

@router.get("/master-service-locations")
def fetch_service_locations(db: Session = Depends(get_db)):
    return get_service_locations(db)


# =========================
# MASTER BRANCH
# =========================

@router.get("/master-branch")
def fetch_branches(db: Session = Depends(get_db)):
    return get_branches(db)


# =========================
# UPLOAD SUPPLIER DOCUMENT
# =========================

@router.post("/upload-document")
def upload_supplier_document(
    field: str,
    file: UploadFile = File(...),
):
    return upload_supplier_document_service(field, file)


# =========================
# CREATE SUPPLIER
# =========================

@router.post("/", response_model=SupplierResponse)
def add_supplier(
    supplier: SupplierCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    new_supplier = create_supplier(db, supplier)
    return attach_file_urls(new_supplier, request)


# =========================
# GET ALL SUPPLIERS
# =========================

@router.get("/", response_model=list[SupplierResponse])
def fetch_suppliers(
    request: Request,
    db: Session = Depends(get_db),
):
    suppliers = get_suppliers(db)
    return [attach_file_urls(s, request) for s in suppliers]


# ── Must come BEFORE /{supplier_id} so FastAPI doesn't match "documents" as an int ──
@router.get("/{supplier_id}/documents")
def get_supplier_documents(
    supplier_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    return get_supplier_documents_service(db, supplier_id, request)


# =========================
# GET SUPPLIER BY ID
# =========================

@router.get("/{supplier_id}", response_model=SupplierResponse)
def fetch_supplier(
    supplier_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    supplier = get_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return attach_file_urls(supplier, request)


# =========================
# UPDATE SUPPLIER
# =========================

@router.put("/{supplier_id}", response_model=SupplierResponse)
def edit_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    supplier = update_supplier(db, supplier_id, data)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return attach_file_urls(supplier, request)


# =========================
# DELETE SUPPLIER
# =========================

@router.delete("/{supplier_id}")
def remove_supplier(supplier_id: int, db: Session = Depends(get_db)):
    result = delete_supplier(db, supplier_id)
    if not result:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"message": "Supplier deleted successfully"}