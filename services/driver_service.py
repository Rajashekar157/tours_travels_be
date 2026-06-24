from fastapi import HTTPException
from models.generated_models import Drivers


def create_driver_service(db, payload):

    existing_driver = (
        db.query(Drivers)
        .filter(
            Drivers.mobile == payload.mobile
        )
        .first()
    )

    if existing_driver:
        raise HTTPException(
            status_code=400,
            detail="Mobile already exists"
        )

    if payload.driver_code:
        existing_code = (
            db.query(Drivers)
            .filter(
                Drivers.driver_code == payload.driver_code
            )
            .first()
        )

        if existing_code:
            raise HTTPException(
                status_code=400,
                detail="Driver code already exists"
            )

    if payload.aadhaar_number:
        existing_aadhaar = (
            db.query(Drivers)
            .filter(
                Drivers.aadhaar_number == payload.aadhaar_number
            )
            .first()
        )

        if existing_aadhaar:
            raise HTTPException(
                status_code=400,
                detail="Aadhaar number already exists"
            )

    if payload.license_number:
        existing_license = (
            db.query(Drivers)
            .filter(
                Drivers.license_number == payload.license_number
            )
            .first()
        )

        if existing_license:
            raise HTTPException(
                status_code=400,
                detail="License number already exists"
            )

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

    emergency_contact_name=payload.emergency_contact_name,
    emergency_contact_number=payload.emergency_contact_number,

    blood_group=payload.blood_group,

    user_id=payload.user_id,
    created_by=payload.created_by,

    status_id=payload.status_id
)


    db.add(driver)
    db.commit()
    db.refresh(driver)

    return driver


def get_drivers_service(db):

    return (
        db.query(Drivers)
        .filter(Drivers.is_active == True)
        .order_by(Drivers.id.desc())
        .all()
    )


def get_driver_service(db, driver_id):

    driver = (
        db.query(Drivers)
        .filter(
            Drivers.id == driver_id
        )
        .first()
    )

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    return driver


def update_driver_service(
    db,
    driver_id,
    payload
):

    driver = (
        db.query(Drivers)
        .filter(
            Drivers.id == driver_id
        )
        .first()
    )

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    for key, value in payload.model_dump(
        exclude_unset=True
    ).items():

        setattr(
            driver,
            key,
            value
        )

    db.commit()
    db.refresh(driver)

    return driver


def delete_driver_service(
    db,
    driver_id
):

    driver = (
        db.query(Drivers)
        .filter(
            Drivers.id == driver_id
        )
        .first()
    )

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Driver not found"
        )

    driver.is_active = False

    db.commit()

    return {
        "message": "Driver deactivated successfully"
    }


def search_driver_service(
    db,
    keyword
):

    return (
        db.query(Drivers)
        .filter(
            Drivers.full_name.ilike(
                f"%{keyword}%"
            )
        )
        .all()
    )