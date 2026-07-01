# import asyncio
# from sqlalchemy import text
# from sqlalchemy.ext.asyncio import AsyncSession

# async def get_dashboard_data_service(db: AsyncSession):
#     summary_q = text("SELECT * FROM dashboard_summary_mat")
#     recent_q = text("""
#         SELECT
#             va.id,
#             v.vehicle_registration_number,
#             v.vehicle_type,
#             d.full_name,
#             d.mobile AS driver_mobile,
#             va.assigned_date,
#             va.status,
#             va.remarks
#         FROM vehicle_assignments va
#         JOIN vehicles v ON v.id = va.vehicle_id
#         JOIN drivers d ON d.id = va.driver_id
#         ORDER BY va.assigned_date DESC
#         LIMIT 10
#     """)
#     insurance_q = text("""
#         SELECT vehicle_registration_number, insurance_expiry_date
#         FROM vehicles
#         WHERE insurance_expiry_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
#         ORDER BY insurance_expiry_date
#     """)
#     license_q = text("""
#         SELECT full_name, license_expiry
#         FROM drivers
#         WHERE license_expiry BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
#         ORDER BY license_expiry
#     """)
#     suppliers_q = text("""
#         SELECT supplier_name, outstanding_amount
#         FROM suppliers
#         WHERE outstanding_amount > 0
#         ORDER BY outstanding_amount DESC
#         LIMIT 5
#     """)

#     # fire all five at once, each on its own connection from the pool
#     summary, recent, insurance, license_, suppliers = await asyncio.gather(
#         db.execute(summary_q),
#         db.execute(recent_q),
#         db.execute(insurance_q),
#         db.execute(license_q),
#         db.execute(suppliers_q),
#     )

#     return {
#         "summary": summary.mappings().first(),
#         "recent_assignments": recent.mappings().all(),
#         "insurance_expiry": insurance.mappings().all(),
#         "license_expiry": license_.mappings().all(),
#         "outstanding_suppliers": suppliers.mappings().all(),
#     }

from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import text
from core.database import SessionLocal

QUERIES = {
    # Materialized View
    "summary": """
        SELECT *
        FROM dashboard_summary_mat
    """,

    # Recent Assignments
    "recent_assignments": """
        SELECT
            va.id,
            v.vehicle_registration_number,
            v.vehicle_display_number,
            vmk.make_name AS vehicle_make,
            vmd.model_name AS vehicle_model,
            d.full_name,
            d.mobile AS driver_mobile,
            va.assignment_type,
            va.assigned_date,
            va.remarks,
            va.is_active
        FROM vehicle_assignments va
        JOIN vehicles v
            ON v.id = va.vehicle_id
        LEFT JOIN master_vehicle_make vmk
            ON vmk.id = v.vehicle_make_id
        LEFT JOIN master_vehicle_model vmd
            ON vmd.id = v.vehicle_model_id
        JOIN drivers d
            ON d.id = va.driver_id
        ORDER BY va.assigned_date DESC
        LIMIT 10
    """,

    # License Expiry
    "license_expiry": """
        SELECT
            full_name,
            license_expiry
        FROM drivers
        WHERE license_expiry
        BETWEEN CURRENT_DATE
            AND CURRENT_DATE + INTERVAL '30 days'
        ORDER BY license_expiry
    """,

    # Outstanding Suppliers
    "outstanding_suppliers": """
        SELECT
            supplier_name,
            outstanding_amount
        FROM suppliers
        WHERE outstanding_amount > 0
        ORDER BY outstanding_amount DESC
        LIMIT 5
    """
}


def _run_query(item):
    key, sql = item

    db = SessionLocal()

    try:
        rows = db.execute(text(sql)).mappings().all()
        return key, rows

    finally:
        db.close()


async def get_dashboard_data_service(db=None):

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = dict(executor.map(_run_query, QUERIES.items()))

    summary = results.get("summary", [])

    return {
        "summary": summary[0] if summary else {},
        "recent_assignments": results.get("recent_assignments", []),
        "license_expiry": results.get("license_expiry", []),
        "outstanding_suppliers": results.get("outstanding_suppliers", [])
    }