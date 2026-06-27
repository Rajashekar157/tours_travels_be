# services/vehicle_bulk_service.py
import io
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

REQUIRED_COLUMNS = [
    "vehicle_registration_number",
    "service_location",
    "vehicle_make",
    "fuel_type",
]

OPTIONAL_COLUMNS = [
    "vehicle_display_number",
    "average_mileage",
    "year_of_make",
    "engine_number",
    "chassis_number",
    "gps_enabled",
    "insurance_company",
    "insurance_policy_number",
    "insurance_expiry_date",
    "status",
]


# def _load_dataframe(file: UploadFile) -> pd.DataFrame:
#     filename = file.filename.lower()
#     content = file.file.read()

#     if filename.endswith(".csv"):
#         df = pd.read_csv(io.BytesIO(content))
#     elif filename.endswith((".xlsx", ".xls")):
#         df = pd.read_excel(io.BytesIO(content))
#     else:
#         raise HTTPException(
#             status_code=400,
#             detail="Unsupported file type. Upload .xlsx, .xls, or .csv",
#         )

#     df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
#     return df



def _load_dataframe(file: UploadFile) -> pd.DataFrame:
    filename = file.filename.lower()
    content = file.file.read()

    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(content))
    elif filename.endswith(".pdf"):
        import pdfplumber
        tables = []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    if table:
                        tables.append(pd.DataFrame(table[1:], columns=table[0]))
        if not tables:
            raise HTTPException(status_code=400, detail="No tables found in PDF")
        df = pd.concat(tables, ignore_index=True)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

def _build_lookup(db: Session, table: str) -> dict:
    """name (lowercased) -> id, for resolving master-table references."""
    rows = db.execute(text(f"SELECT id, name FROM {table}")).mappings().all()
    return {r["name"].strip().lower(): r["id"] for r in rows}


def bulk_upload_vehicles_service(file: UploadFile, db: Session) -> dict:
    df = _load_dataframe(file)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing_cols)}",
        )

    location_map = _build_lookup(db, "service_locations")
    make_map = _build_lookup(db, "vehicle_makes")
    fuel_map = _build_lookup(db, "fuel_types")
    status_map = _build_lookup(db, "statuses")

    inserted = 0
    errors = []  # list of {row, reason}

    for idx, row in df.iterrows():
        row_num = idx + 2  # +2 = account for header row + 0-index, matches Excel row number

        reg_no = str(row.get("vehicle_registration_number", "")).strip()
        if not reg_no or reg_no.lower() == "nan":
            errors.append({"row": row_num, "reason": "Missing registration number"})
            continue

        location_id = location_map.get(str(row.get("service_location", "")).strip().lower())
        make_id = make_map.get(str(row.get("vehicle_make", "")).strip().lower())
        fuel_id = fuel_map.get(str(row.get("fuel_type", "")).strip().lower())
        status_id = status_map.get(str(row.get("status", "")).strip().lower())

        if not location_id:
            errors.append({"row": row_num, "reason": f"Unknown service_location: '{row.get('service_location')}'"})
            continue
        if not make_id:
            errors.append({"row": row_num, "reason": f"Unknown vehicle_make: '{row.get('vehicle_make')}'"})
            continue
        if not fuel_id:
            errors.append({"row": row_num, "reason": f"Unknown fuel_type: '{row.get('fuel_type')}'"})
            continue

        gps_raw = str(row.get("gps_enabled", "")).strip().lower()
        gps_enabled = gps_raw in ("yes", "true", "1", "y")

        try:
            db.execute(
                text("""
                    INSERT INTO vehicles (
                        vehicle_registration_number, vehicle_display_number,
                        service_location_id, vehicle_make_id, fuel_type_id,
                        average_mileage, year_of_make, engine_number, chassis_number,
                        gps_enabled, insurance_company, insurance_policy_number,
                        insurance_expiry_date, status_id, created_by, updated_by
                    ) VALUES (
                        :reg_no, :display_no,
                        :location_id, :make_id, :fuel_id,
                        :mileage, :year, :engine_no, :chassis_no,
                        :gps_enabled, :ins_company, :ins_policy,
                        :ins_expiry, :status_id, 9, 9
                    )
                """),
                {
                    "reg_no": reg_no,
                    "display_no": str(row.get("vehicle_display_number", "")).strip() or None,
                    "location_id": location_id,
                    "make_id": make_id,
                    "fuel_id": fuel_id,
                    "mileage": row.get("average_mileage") or None,
                    "year": row.get("year_of_make") or None,
                    "engine_no": str(row.get("engine_number", "")).strip() or None,
                    "chassis_no": str(row.get("chassis_number", "")).strip() or None,
                    "gps_enabled": gps_enabled,
                    "ins_company": str(row.get("insurance_company", "")).strip() or None,
                    "ins_policy": str(row.get("insurance_policy_number", "")).strip() or None,
                    "ins_expiry": row.get("insurance_expiry_date") or None,
                    "status_id": status_id,
                },
            )
            inserted += 1
        except Exception as e:
            errors.append({"row": row_num, "reason": f"DB error: {str(e)}"})

    db.commit()

    return {
        "total_rows": len(df),
        "inserted": inserted,
        "failed": len(errors),
        "errors": errors,
    }