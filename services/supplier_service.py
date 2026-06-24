from sqlalchemy.orm import Session

from models.generated_models import (
    Suppliers,
    MasterSupplierType,
    MasterServiceLocation,
    
)


# =========================
# SUPPLIER CRUD
# =========================

def create_supplier(
    db: Session,
    supplier
):
    new_supplier = Suppliers(
        **supplier.dict()
    )

    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)

    return new_supplier


def get_suppliers(
    db: Session
):
    return (
        db.query(Suppliers)
        .all()
    )


def get_supplier(
    db: Session,
    supplier_id: int
):
    return (
        db.query(Suppliers)
        .filter(
            Suppliers.id == supplier_id
        )
        .first()
    )


def update_supplier(
    db: Session,
    supplier_id: int,
    supplier_data
):
    supplier = get_supplier(
        db,
        supplier_id
    )

    if not supplier:
        return None

    update_data = supplier_data.dict(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            supplier,
            key,
            value
        )

    db.commit()
    db.refresh(supplier)

    return supplier


def delete_supplier(
    db: Session,
    supplier_id: int
):
    supplier = get_supplier(
        db,
        supplier_id
    )

    if not supplier:
        return None

    db.delete(supplier)
    db.commit()

    return True


# =========================
# MASTER SUPPLIER TYPE
# =========================

def get_supplier_types(
    db: Session
):
    return (
        db.query(
            MasterSupplierType
        )
        .all()
    )


# =========================
# MASTER SERVICE LOCATION
# =========================

def get_service_locations(
    db: Session
):
    return (
        db.query(
            MasterServiceLocation
        )
        .all()
    )