from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import text
from core.database import SessionLocal

QUERIES = {
    # Materialized View
    "summary": """
        SELECT *
        FROM dashboard_summary_mat
    """,

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
    LEFT JOIN drivers d
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
    """,

    # Fleet Composition — by fuel type
    "fleet_by_fuel": """
        SELECT
            COALESCE(mft.fuel_type_name, 'Unspecified') AS label,
            COUNT(v.id) AS count
        FROM vehicles v
        LEFT JOIN master_fuel_type mft
            ON mft.id = v.fuel_type_id
        GROUP BY mft.fuel_type_name
        ORDER BY count DESC
    """,

    # Fleet Composition — by transmission type
    "fleet_by_transmission": """
        SELECT
            COALESCE(mtt.transmission_name, 'Unspecified') AS label,
            COUNT(v.id) AS count
        FROM vehicles v
        LEFT JOIN master_transmission_type mtt
            ON mtt.id = v.transmission_type_id
        GROUP BY mtt.transmission_name
        ORDER BY count DESC
    """,

    # Branch-wise Breakdown
    "branch_breakdown": """
        SELECT
            mb.branch_name AS label,
            COUNT(DISTINCT d.id) AS driver_count,
            COUNT(DISTINCT va.vehicle_id)
                FILTER (WHERE va.is_active = true) AS assigned_vehicle_count
        FROM master_branch mb
        LEFT JOIN drivers d
            ON d.branch_id = mb.id
        LEFT JOIN vehicle_assignments va
            ON va.branch_id = mb.id
        GROUP BY mb.branch_name
        ORDER BY mb.branch_name
    """,

    # Live Vehicle Map — latest known location per vehicle
    "live_vehicle_locations": """
        SELECT DISTINCT ON (pl.vehicle_id)
            pl.vehicle_id,
            v.vehicle_registration_number,
            v.vehicle_display_number,
            d.full_name AS driver_name,
            pl.latitude,
            pl.longitude,
            pl.location_name,
            pl.updated_at
        FROM parking_locations pl
        JOIN vehicles v
            ON v.id = pl.vehicle_id
        LEFT JOIN drivers d
            ON d.id = pl.driver_id
        ORDER BY pl.vehicle_id, pl.updated_at DESC
        LIMIT 50
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

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = dict(executor.map(_run_query, QUERIES.items()))

    summary = results.get("summary", [])

    return {
        "summary": summary[0] if summary else {},
        "recent_assignments": results.get("recent_assignments", []),
        "license_expiry": results.get("license_expiry", []),
        "outstanding_suppliers": results.get("outstanding_suppliers", []),
        "fleet_by_fuel": results.get("fleet_by_fuel", []),
        "fleet_by_transmission": results.get("fleet_by_transmission", []),
        "branch_breakdown": results.get("branch_breakdown", []),
        "live_vehicle_locations": results.get("live_vehicle_locations", [])
    }

































# from concurrent.futures import ThreadPoolExecutor
# from sqlalchemy import text
# from core.database import SessionLocal

# QUERIES = {
#     # Materialized View
#     "summary": """
#         SELECT *
#         FROM dashboard_summary_mat
#     """,

#     # Recent Assignments
#     "recent_assignments": """
#         SELECT
#             va.id,
#             v.vehicle_registration_number,
#             v.vehicle_display_number,
#             vmk.make_name AS vehicle_make,
#             vmd.model_name AS vehicle_model,
#             d.full_name,
#             d.mobile AS driver_mobile,
#             va.assignment_type,
#             va.assigned_date,
#             va.remarks,
#             va.is_active
#         FROM vehicle_assignments va
#         JOIN vehicles v
#             ON v.id = va.vehicle_id
#         LEFT JOIN master_vehicle_make vmk
#             ON vmk.id = v.vehicle_make_id
#         LEFT JOIN master_vehicle_model vmd
#             ON vmd.id = v.vehicle_model_id
#         JOIN drivers d
#             ON d.id = va.driver_id
#         ORDER BY va.assigned_date DESC
#         LIMIT 10
#     """,

#     # License Expiry
#     "license_expiry": """
#         SELECT
#             full_name,
#             license_expiry
#         FROM drivers
#         WHERE license_expiry
#         BETWEEN CURRENT_DATE
#             AND CURRENT_DATE + INTERVAL '30 days'
#         ORDER BY license_expiry
#     """,

#     # Outstanding Suppliers
#     "outstanding_suppliers": """
#         SELECT
#             supplier_name,
#             outstanding_amount
#         FROM suppliers
#         WHERE outstanding_amount > 0
#         ORDER BY outstanding_amount DESC
#         LIMIT 5
#     """,

#     # Fleet Composition — by fuel type
#     "fleet_by_fuel": """
#         SELECT
#             COALESCE(mft.fuel_type_name, 'Unspecified') AS label,
#             COUNT(v.id) AS count
#         FROM vehicles v
#         LEFT JOIN master_fuel_type mft
#             ON mft.id = v.fuel_type_id
#         GROUP BY mft.fuel_type_name
#         ORDER BY count DESC
#     """,

#     # Fleet Composition — by transmission type
#     "fleet_by_transmission": """
#         SELECT
#             COALESCE(mtt.transmission_name, 'Unspecified') AS label,
#             COUNT(v.id) AS count
#         FROM vehicles v
#         LEFT JOIN master_transmission_type mtt
#             ON mtt.id = v.transmission_type_id
#         GROUP BY mtt.transmission_name
#         ORDER BY count DESC
#     """,

#     # Branch-wise Breakdown
#     "branch_breakdown": """
#         SELECT
#             mb.branch_name AS label,
#             COUNT(DISTINCT d.id) AS driver_count,
#             COUNT(DISTINCT va.vehicle_id)
#                 FILTER (WHERE va.is_active = true) AS assigned_vehicle_count
#         FROM master_branch mb
#         LEFT JOIN drivers d
#             ON d.branch_id = mb.id
#         LEFT JOIN vehicle_assignments va
#             ON va.branch_id = mb.id
#         GROUP BY mb.branch_name
#         ORDER BY mb.branch_name
#     """,

#     # Live Vehicle Map — latest known location per vehicle
#     "live_vehicle_locations": """
#         SELECT DISTINCT ON (pl.vehicle_id)
#             pl.vehicle_id,
#             v.vehicle_registration_number,
#             v.vehicle_display_number,
#             d.full_name AS driver_name,
#             pl.latitude,
#             pl.longitude,
#             pl.location_name,
#             pl.updated_at
#         FROM parking_locations pl
#         JOIN vehicles v
#             ON v.id = pl.vehicle_id
#         LEFT JOIN drivers d
#             ON d.id = pl.driver_id
#         ORDER BY pl.vehicle_id, pl.updated_at DESC
#         LIMIT 50
#     """
# }


# def _run_query(item):
#     key, sql = item

#     db = SessionLocal()

#     try:
#         rows = db.execute(text(sql)).mappings().all()
#         return key, rows

#     finally:
#         db.close()


# async def get_dashboard_data_service(db=None):

#     with ThreadPoolExecutor(max_workers=8) as executor:
#         results = dict(executor.map(_run_query, QUERIES.items()))

#     summary = results.get("summary", [])

#     return {
#         "summary": summary[0] if summary else {},
#         "recent_assignments": results.get("recent_assignments", []),
#         "license_expiry": results.get("license_expiry", []),
#         "outstanding_suppliers": results.get("outstanding_suppliers", []),
#         "fleet_by_fuel": results.get("fleet_by_fuel", []),
#         "fleet_by_transmission": results.get("fleet_by_transmission", []),
#         "branch_breakdown": results.get("branch_breakdown", []),
#         "live_vehicle_locations": results.get("live_vehicle_locations", [])
#     }