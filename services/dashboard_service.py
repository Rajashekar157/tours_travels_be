from sqlalchemy import text
from sqlalchemy.orm import Session


def get_dashboard_data_service(db: Session):

    summary = db.execute(
        text("""
            SELECT *
            FROM dashboard_summary
        """)
    ).mappings().first()

    recent_assignments = db.execute(
        text("""
            SELECT
                va.id,
                v.vehicle_registration_number,
                d.full_name,
                va.assigned_date
            FROM vehicle_assignments va
            JOIN vehicles v
                ON v.id = va.vehicle_id
            JOIN drivers d
                ON d.id = va.driver_id
            ORDER BY va.assigned_date DESC
            LIMIT 10
        """)
    ).mappings().all()

    insurance_expiry = db.execute(
        text("""
            SELECT
                vehicle_registration_number,
                insurance_expiry_date
            FROM vehicles
            WHERE insurance_expiry_date
            BETWEEN CURRENT_DATE
            AND CURRENT_DATE + INTERVAL '30 days'
            ORDER BY insurance_expiry_date
        """)
    ).mappings().all()

    license_expiry = db.execute(
        text("""
            SELECT
                full_name,
                license_expiry
            FROM drivers
            WHERE license_expiry
            BETWEEN CURRENT_DATE
            AND CURRENT_DATE + INTERVAL '30 days'
            ORDER BY license_expiry
        """)
    ).mappings().all()

    outstanding_suppliers = db.execute(
        text("""
            SELECT
                supplier_name,
                outstanding_amount
            FROM suppliers
            WHERE outstanding_amount > 0
            ORDER BY outstanding_amount DESC
            LIMIT 5
        """)
    ).mappings().all()

    return {
        "summary": summary,
        "recent_assignments": recent_assignments,
        "insurance_expiry": insurance_expiry,
        "license_expiry": license_expiry,
        "outstanding_suppliers": outstanding_suppliers
    }