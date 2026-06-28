from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from models.generated_models import (
    VehicleAssignments,
    Drivers,
    Vehicles,
    Suppliers,
)

from schemas.VehicleAssignments_schema import (
    VehicleAssignmentCreate,
    VehicleAssignmentUpdate
)


# =====================================================
# AUTO GENERATE UNIQUE NUMBER  →  VUP-01, VUP-02 ...
# =====================================================

def generate_unique_number(db: Session) -> str:

    last = (
        db.query(VehicleAssignments.unique_number)
        .filter(
            VehicleAssignments.unique_number.isnot(None),
            VehicleAssignments.unique_number.like("VUP-%")
        )
        .order_by(VehicleAssignments.id.desc())
        .first()
    )

    if not last or not last.unique_number:
        return "VUP-01"

    try:
        num = int(last.unique_number.split("-")[1])
        return f"VUP-{str(num + 1).zfill(2)}"
    except (IndexError, ValueError):
        count = db.query(func.count(VehicleAssignments.id)).scalar()
        return f"VUP-{str(count + 1).zfill(2)}"


# =====================================================
# CREATE
# =====================================================

def create_vehicle_assignment(
    data: VehicleAssignmentCreate,
    db: Session,
    current_user_id: int           # ← from JWT
):

    driver = db.query(Drivers).filter(
        Drivers.id == data.driver_id
    ).first()

    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    vehicle = db.query(Vehicles).filter(
        Vehicles.id == data.vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if data.supplier_id:
        supplier = db.query(Suppliers).filter(
            Suppliers.id == data.supplier_id
        ).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")

    existing_driver = db.query(VehicleAssignments).filter(
        VehicleAssignments.driver_id == data.driver_id,
        VehicleAssignments.is_active == True
    ).first()

    if existing_driver:
        raise HTTPException(
            status_code=400,
            detail=f"Driver {driver.full_name} is already assigned to another vehicle"
        )

    existing_vehicle = db.query(VehicleAssignments).filter(
        VehicleAssignments.vehicle_id == data.vehicle_id,
        VehicleAssignments.is_active == True
    ).first()

    if existing_vehicle:
        raise HTTPException(
            status_code=400,
            detail=f"Vehicle {vehicle.vehicle_registration_number} is already assigned to another driver"
        )

    unique_number = generate_unique_number(db)

    assignment = VehicleAssignments(

        unique_number=unique_number,

        driver_id=data.driver_id,
        vehicle_id=data.vehicle_id,
        supplier_id=data.supplier_id,

        service_location_id=data.service_location_id,
        branch_id=data.branch_id,
        vehicle_odometer_km=data.vehicle_odometer_km,
        assignment_type=data.assignment_type,

        emi_amount=data.emi_amount,
        emi_tenure_months=data.emi_tenure_months,
        emi_start_date=data.emi_start_date,
        emi_end_date=data.emi_end_date,
        transaction_id=data.transaction_id,

        allotment_document_photo=data.allotment_document_photo,
        vehicle_photo_front=data.vehicle_photo_front,
        vehicle_photo_back=data.vehicle_photo_back,
        vehicle_photo_left=data.vehicle_photo_left,
        vehicle_photo_right=data.vehicle_photo_right,

        remarks=data.remarks,

        created_by=current_user_id,   # ← JWT user
        updated_by=current_user_id,   # ← JWT user

        is_active=True,
        assigned_date=datetime.utcnow()
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "message": "Assignment created successfully",
        "unique_number": assignment.unique_number,
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

            "driver_id": x.driver_id,
            "vehicle_id": x.vehicle_id,
            "supplier_id": x.supplier_id,

            "driver_code": x.driver.driver_code,
            "full_name": x.driver.full_name,
            "mobile": x.driver.mobile,
            "email": x.driver.email,

            "vehicle_no": x.vehicle.vehicle_registration_number,
            "display_no": x.vehicle.vehicle_display_number,

            "supplier_name": x.supplier.supplier_name if x.supplier else None,
            "supplier_code": x.supplier.supplier_code if x.supplier else None,
            "supplier_mobile": x.supplier.mobile if x.supplier else None,
            "supplier_type_id": x.supplier.supplier_type_id if x.supplier else None,
            "outstanding_amount": float(x.supplier.outstanding_amount) if x.supplier and x.supplier.outstanding_amount else None,

            "service_location_id": x.service_location_id,
            "branch_id": x.branch_id,
            "vehicle_odometer_km": float(x.vehicle_odometer_km) if x.vehicle_odometer_km else None,
            "assignment_type": x.assignment_type,

            "assigned_date": x.assigned_date,
            "relieved_date": x.relieved_date,

            "emi_amount": float(x.emi_amount) if x.emi_amount else None,
            "emi_tenure_months": x.emi_tenure_months,
            "emi_start_date": x.emi_start_date,
            "emi_end_date": x.emi_end_date,
            "transaction_id": x.transaction_id,

            "allotment_document_photo": x.allotment_document_photo,
            "vehicle_photo_front": x.vehicle_photo_front,
            "vehicle_photo_back": x.vehicle_photo_back,
            "vehicle_photo_left": x.vehicle_photo_left,
            "vehicle_photo_right": x.vehicle_photo_right,

            "is_active": x.is_active,
            "remarks": x.remarks,

            "created_by": x.created_by,
            "updated_by": x.updated_by,
        })

    return result


# =====================================================
# GET BY ID
# =====================================================

def get_vehicle_assignment(assignment_id: int, db: Session):

    x = db.query(VehicleAssignments).filter(
        VehicleAssignments.id == assignment_id
    ).first()

    if not x:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return {
        "id": x.id,
        "unique_number": x.unique_number,

        "driver_id": x.driver_id,
        "vehicle_id": x.vehicle_id,
        "supplier_id": x.supplier_id,

        "driver_code": x.driver.driver_code,
        "full_name": x.driver.full_name,
        "mobile": x.driver.mobile,

        "vehicle_no": x.vehicle.vehicle_registration_number,
        "display_no": x.vehicle.vehicle_display_number,

        "supplier_name": x.supplier.supplier_name if x.supplier else None,
        "supplier_code": x.supplier.supplier_code if x.supplier else None,
        "supplier_mobile": x.supplier.mobile if x.supplier else None,
        "supplier_type_id": x.supplier.supplier_type_id if x.supplier else None,
        "outstanding_amount": float(x.supplier.outstanding_amount) if x.supplier and x.supplier.outstanding_amount else None,

        "service_location_id": x.service_location_id,
        "branch_id": x.branch_id,
        "vehicle_odometer_km": float(x.vehicle_odometer_km) if x.vehicle_odometer_km else None,
        "assignment_type": x.assignment_type,

        "assigned_date": x.assigned_date,
        "relieved_date": x.relieved_date,

        "emi_amount": float(x.emi_amount) if x.emi_amount else None,
        "emi_tenure_months": x.emi_tenure_months,
        "emi_start_date": x.emi_start_date,
        "emi_end_date": x.emi_end_date,
        "transaction_id": x.transaction_id,

        "allotment_document_photo": x.allotment_document_photo,
        "vehicle_photo_front": x.vehicle_photo_front,
        "vehicle_photo_back": x.vehicle_photo_back,
        "vehicle_photo_left": x.vehicle_photo_left,
        "vehicle_photo_right": x.vehicle_photo_right,

        "is_active": x.is_active,
        "remarks": x.remarks,

        "created_by": x.created_by,
        "updated_by": x.updated_by,
    }


# =====================================================
# UPDATE
# =====================================================

def update_vehicle_assignment(
    assignment_id: int,
    data: VehicleAssignmentUpdate,
    db: Session,
    current_user_id: int           # ← from JWT
):

    assignment = db.query(VehicleAssignments).filter(
        VehicleAssignments.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if data.driver_id:
        existing = db.query(VehicleAssignments).filter(
            VehicleAssignments.driver_id == data.driver_id,
            VehicleAssignments.id != assignment_id,
            VehicleAssignments.is_active == True
        ).first()
        if existing:
            driver = db.query(Drivers).filter(Drivers.id == data.driver_id).first()
            raise HTTPException(
                status_code=400,
                detail=f"Driver {driver.full_name} is already assigned to another vehicle"
            )

    if data.vehicle_id:
        existing = db.query(VehicleAssignments).filter(
            VehicleAssignments.vehicle_id == data.vehicle_id,
            VehicleAssignments.id != assignment_id,
            VehicleAssignments.is_active == True
        ).first()
        if existing:
            vehicle = db.query(Vehicles).filter(Vehicles.id == data.vehicle_id).first()
            raise HTTPException(
                status_code=400,
                detail=f"Vehicle {vehicle.vehicle_registration_number} is already assigned"
            )

    if data.supplier_id:
        supplier = db.query(Suppliers).filter(Suppliers.id == data.supplier_id).first()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(assignment, key, value)

    assignment.updated_by = current_user_id   # ← JWT user
    assignment.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(assignment)

    return {"message": "Assignment updated successfully"}


# =====================================================
# DELETE
# =====================================================

def delete_vehicle_assignment(
    assignment_id: int,
    db: Session,
    current_user_id: int           # ← from JWT
):

    assignment = db.query(VehicleAssignments).filter(
        VehicleAssignments.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Soft delete — mark inactive, track who deleted
    assignment.is_active = False
    assignment.updated_by = current_user_id   # ← JWT user
    assignment.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Vehicle Assignment deleted successfully"}