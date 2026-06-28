from fastapi import APIRouter, Depends, HTTPException
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
)

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


# =========================
# MASTER SUPPLIER TYPE
# =========================

@router.get("/master-supplier-type")
def fetch_supplier_types(
    db: Session = Depends(get_db)
):
    return get_supplier_types(db)


# =========================
# MASTER SERVICE LOCATION
# =========================

@router.get("/master-service-locations")
def fetch_service_locations(
    db: Session = Depends(get_db)
):
    return get_service_locations(db)


# =========================
# MASTER BRANCH
# =========================

@router.get("/master-branch")
def fetch_branches(
    db: Session = Depends(get_db)
):
    return get_branches(db)


# =========================
# CREATE SUPPLIER
# =========================

@router.post(
    "/",
    response_model=SupplierResponse
)
def add_supplier(
    supplier: SupplierCreate,
    db: Session = Depends(get_db)
):
    return create_supplier(
        db,
        supplier
    )


# =========================
# GET ALL SUPPLIERS
# =========================

@router.get(
    "/",
    response_model=list[SupplierResponse]
)
def fetch_suppliers(
    db: Session = Depends(get_db)
):
    return get_suppliers(db)


# =========================
# GET SUPPLIER BY ID
# =========================

@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def fetch_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    supplier = get_supplier(
        db,
        supplier_id
    )

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return supplier


# =========================
# UPDATE SUPPLIER
# =========================

@router.put(
    "/{supplier_id}",
    response_model=SupplierResponse
)
def edit_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: Session = Depends(get_db)
):
    supplier = update_supplier(
        db,
        supplier_id,
        data
    )

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return supplier


# =========================
# DELETE SUPPLIER
# =========================

@router.delete(
    "/{supplier_id}"
)
def remove_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    result = delete_supplier(
        db,
        supplier_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    return {
        "message": "Supplier deleted successfully"
    }