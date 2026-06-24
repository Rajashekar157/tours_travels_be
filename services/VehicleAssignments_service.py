
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from models.generated_models import (
    VehicleAssignments,
    Drivers,
    Vehicles,
    Suppliers
)

from schemas.VehicleAssignments_schema import (
    VehicleAssignmentCreate,
    VehicleAssignmentUpdate
)


def create_vehicle_assignment(
    data: VehicleAssignmentCreate,
    db: Session
):

    driver = db.query(
        Drivers
    ).filter(
        Drivers.id == data.driver_id
    ).first()

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    vehicle = db.query(
        Vehicles
    ).filter(
        Vehicles.id == data.vehicle_id
    ).first()

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    supplier = db.query(
        Suppliers
    ).filter(
        Suppliers.id == data.supplier_id
    ).first()

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )

    existing_driver_assignment = db.query(
        VehicleAssignments
    ).filter(
        VehicleAssignments.driver_id == data.driver_id,
        VehicleAssignments.is_active == True
    ).first()

    if existing_driver_assignment:
        raise HTTPException(
            status_code=400,
            detail=f"Driver {driver.full_name} is already assigned to another vehicle"
        )

    existing_vehicle_assignment = db.query(
        VehicleAssignments
    ).filter(
        VehicleAssignments.vehicle_id == data.vehicle_id,
        VehicleAssignments.is_active == True
    ).first()

    if existing_vehicle_assignment:
        raise HTTPException(
            status_code=400,
            detail=f"Vehicle {vehicle.vehicle_registration_number} is already assigned to another driver"
        )

    today = datetime.now().strftime("%d-%m-%Y")

    count = db.query(
        func.count(VehicleAssignments.id)
    ).scalar()

    unique_number = (
        f"{today}/{str(count + 1).zfill(2)}"
    )

    assignment = VehicleAssignments(
        unique_number=unique_number,

        driver_id=data.driver_id,
        vehicle_id=data.vehicle_id,
        supplier_id=data.supplier_id,

        assignment_type=data.assignment_type,

        emi_amount=data.emi_amount,
        emi_tenure_months=data.emi_tenure_months,

        emi_start_date=data.emi_start_date,
        emi_end_date=data.emi_end_date,

        transaction_id=data.transaction_id,

        remarks=data.remarks,

        created_by=data.created_by,

        is_active=True
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment


def get_vehicle_assignments(
    db: Session
):

    assignments = db.query(
        VehicleAssignments
    ).all()

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

            "supplier_name":
                x.supplier.supplier_name
                if x.supplier else None,

            "assigned_date": x.assigned_date,
            "relieved_date": x.relieved_date,

            "assignment_type": x.assignment_type,

            "emi_amount": x.emi_amount,
            "emi_tenure_months": x.emi_tenure_months,

            "emi_start_date": x.emi_start_date,
            "emi_end_date": x.emi_end_date,

            "transaction_id": x.transaction_id,

            "is_active": x.is_active,
            "remarks": x.remarks
        })

    return result


def get_vehicle_assignment(
    assignment_id: int,
    db: Session
):

    assignment = db.query(
        VehicleAssignments
    ).filter(
        VehicleAssignments.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    return assignment


def update_vehicle_assignment(
    assignment_id: int,
    data: VehicleAssignmentUpdate,
    db: Session
):

    assignment = db.query(
        VehicleAssignments
    ).filter(
        VehicleAssignments.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    if data.driver_id:

        existing_driver = db.query(
            VehicleAssignments
        ).filter(
            VehicleAssignments.driver_id == data.driver_id,
            VehicleAssignments.id != assignment_id,
            VehicleAssignments.is_active == True
        ).first()

        if existing_driver:

            driver = db.query(
                Drivers
            ).filter(
                Drivers.id == data.driver_id
            ).first()

            raise HTTPException(
                status_code=400,
                detail=f"Driver {driver.full_name} is already assigned to another vehicle"
            )

    if data.vehicle_id:

        existing_vehicle = db.query(
            VehicleAssignments
        ).filter(
            VehicleAssignments.vehicle_id == data.vehicle_id,
            VehicleAssignments.id != assignment_id,
            VehicleAssignments.is_active == True
        ).first()

        if existing_vehicle:

            vehicle = db.query(
                Vehicles
            ).filter(
                Vehicles.id == data.vehicle_id
            ).first()

            raise HTTPException(
                status_code=400,
                detail=f"Vehicle {vehicle.vehicle_registration_number} is already assigned to another driver"
            )

    if data.supplier_id:

        supplier = db.query(
            Suppliers
        ).filter(
            Suppliers.id == data.supplier_id
        ).first()

        if not supplier:
            raise HTTPException(
                status_code=404,
                detail="Supplier not found"
            )

    for key, value in data.model_dump(
        exclude_unset=True
    ).items():

        setattr(
            assignment,
            key,
            value
        )

    db.commit()
    db.refresh(assignment)

    return assignment


def delete_vehicle_assignment(
    assignment_id: int,
    db: Session
):

    assignment = db.query(
        VehicleAssignments
    ).filter(
        VehicleAssignments.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    db.delete(assignment)
    db.commit()

    return {
        "message": "Vehicle Assignment deleted successfully"
    }

