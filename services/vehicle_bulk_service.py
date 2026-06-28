# services/vehicle_bulk_service.py

import io
import zipfile
import traceback

import pandas as pd
import pdfplumber

from fastapi import UploadFile, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

REQUIRED_COLUMNS = [
    "vehicle_registration_number",
    "service_location",
    "company",
    "vehicle_make",
    "vehicle_model",
    "fuel_type",
    "transmission_type",
    "tax_status",
]

OPTIONAL_COLUMNS = [
    "vehicle_display_number",
    "registration_date",
    "average_mileage",
    "year_of_make",
    "engine_number",
    "chassis_number",
    "seating_capacity",
    "gps_enabled",
    "insurance_company",
    "insurance_policy_number",
    "insurance_expiry_date",
    "vehicle_photo",
    "status",
]


# services/vehicle_bulk_service.py  — replace these two functions

async def _load_dataframe(file: UploadFile) -> pd.DataFrame:
    filename = file.filename.lower()
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        elif filename.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(content), engine="xlrd")
        elif filename.endswith(".pdf"):
            tables = []
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    for table in page.extract_tables():
                        if table:
                            tables.append(pd.DataFrame(table[1:], columns=table[0]))
            if not tables:
                raise HTTPException(status_code=400, detail="No table found in PDF.")
            df = pd.concat(tables, ignore_index=True)
        elif filename.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                target = next(
                    (n for n in archive.namelist()
                     if n.lower().endswith((".xlsx", ".xls", ".csv"))),
                    None
                )
                if not target:
                    raise HTTPException(status_code=400, detail="ZIP does not contain CSV or Excel.")
                data = archive.read(target)
                if target.endswith(".csv"):
                    df = pd.read_csv(io.BytesIO(data))
                elif target.endswith(".xlsx"):
                    df = pd.read_excel(io.BytesIO(data), engine="openpyxl")
                else:
                    df = pd.read_excel(io.BytesIO(data), engine="xlrd")
        else:
            raise HTTPException(status_code=400, detail="Supported: CSV, XLSX, XLS, PDF, ZIP.")

        # Normalize column names
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        # ✅ Normalize all string values — strip whitespace
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        return df

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


def _build_lookup(db: Session, table: str, column: str) -> dict:
    # Use LOWER + TRIM at DB level so casing in master data never matters
    rows = db.execute(
        text(f"SELECT id, LOWER(TRIM({column})) as val FROM {table}")
    ).mappings().all()
    return {r["val"]: r["id"] for r in rows}

async def bulk_upload_vehicles_service(file: UploadFile, db: Session, current_user):
    try:
        df = await _load_dataframe(file)

        # Validate required columns
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns: {', '.join(missing)}"
            )

        # Build all lookup maps
        location_map      = _build_lookup(db, "master_service_location", "location_name")
        company_map       = _build_lookup(db, "master_company", "company_name")
        make_map          = _build_lookup(db, "master_vehicle_make", "make_name")
        model_map         = _build_lookup(db, "master_vehicle_model", "model_name")
        fuel_map          = _build_lookup(db, "master_fuel_type", "fuel_type_name")
        transmission_map  = _build_lookup(db, "master_transmission_type", "transmission_name")
        tax_status_map    = _build_lookup(db, "master_tax_status", "tax_status_name")
        status_map        = _build_lookup(db, "master_status", "status_name")

        inserted, failed, errors = 0, 0, []

        for index, row in df.iterrows():
            excel_row = index + 2
            try:
                reg_number = str(row.get("vehicle_registration_number", "")).strip()
                if not reg_number:
                    failed += 1
                    errors.append({"row": excel_row, "reason": "Registration Number Missing"})
                    continue

                # Duplicate check
                if db.execute(
                    text("SELECT id FROM vehicles WHERE vehicle_registration_number=:reg"),
                    {"reg": reg_number}
                ).first():
                    failed += 1
                    errors.append({"row": excel_row, "reason": "Vehicle already exists"})
                    continue

                # Resolve all FK lookups
                def get_id(map_, col, label):
                    val = str(row.get(col, "")).strip().lower()
                    _id = map_.get(val)
                    if _id is None:
                        raise ValueError(f"Invalid {label}: '{val}'")
                    return _id

                location_id     = get_id(location_map,     "service_location",  "Service Location")
                company_id      = get_id(company_map,       "company",           "Company")
                make_id         = get_id(make_map,          "vehicle_make",      "Vehicle Make")
                model_id        = get_id(model_map,         "vehicle_model",     "Vehicle Model")
                fuel_id         = get_id(fuel_map,          "fuel_type",         "Fuel Type")
                transmission_id = get_id(transmission_map,  "transmission_type", "Transmission Type")
                tax_status_id   = get_id(tax_status_map,    "tax_status",        "Tax Status")
                status_id       = get_id(status_map,        "status",            "Status")

                gps_raw = str(row.get("gps_enabled", "")).strip().lower()
                gps_enabled = gps_raw in ["yes", "true", "1", "y"]

                def safe_str(col):
                    v = str(row.get(col, "")).strip()
                    return v or None

                def safe_num(col):
                    v = row.get(col)
                    return v if pd.notna(v) else None

                db.execute(
                    text("""
                        INSERT INTO vehicles (
                            service_location_id, company_id,
                            vehicle_make_id, vehicle_model_id,
                            fuel_type_id, transmission_type_id,
                            tax_status_id, status_id,
                            vehicle_registration_number, vehicle_display_number,
                            registration_date,
                            average_mileage, year_of_make,
                            engine_number, chassis_number,
                            seating_capacity, gps_enabled,
                            insurance_company, insurance_policy_number,
                            insurance_expiry_date, vehicle_photo,
                            created_by, updated_by
                        ) VALUES (
                            :service_location_id, :company_id,
                            :vehicle_make_id, :vehicle_model_id,
                            :fuel_type_id, :transmission_type_id,
                            :tax_status_id, :status_id,
                            :vehicle_registration_number, :vehicle_display_number,
                            :registration_date,
                            :average_mileage, :year_of_make,
                            :engine_number, :chassis_number,
                            :seating_capacity, :gps_enabled,
                            :insurance_company, :insurance_policy_number,
                            :insurance_expiry_date, :vehicle_photo,
                            :created_by, :updated_by
                        )
                    """),
                    {
                        "service_location_id":          location_id,
                        "company_id":                   company_id,
                        "vehicle_make_id":              make_id,
                        "vehicle_model_id":             model_id,
                        "fuel_type_id":                 fuel_id,
                        "transmission_type_id":         transmission_id,
                        "tax_status_id":                tax_status_id,
                        "status_id":                    status_id,
                        "vehicle_registration_number":  reg_number,
                        "vehicle_display_number":       safe_str("vehicle_display_number"),
                        "registration_date":            safe_num("registration_date"),
                        "average_mileage":              safe_num("average_mileage"),
                        "year_of_make":                 safe_num("year_of_make"),
                        "engine_number":                safe_str("engine_number"),
                        "chassis_number":               safe_str("chassis_number"),
                        "seating_capacity":             safe_num("seating_capacity"),
                        "gps_enabled":                  gps_enabled,
                        "insurance_company":            safe_str("insurance_company"),
                        "insurance_policy_number":      safe_str("insurance_policy_number"),
                        "insurance_expiry_date":        safe_num("insurance_expiry_date"),
                        "vehicle_photo":                safe_str("vehicle_photo"),
                        "created_by":                   current_user["user_id"],
                        "updated_by":                   current_user["user_id"],
                    }
                )
                inserted += 1

            except Exception as e:
                failed += 1
                errors.append({"row": excel_row, "reason": str(e)})

        db.commit()
        return {
            "success": True,
            "message": "Vehicle bulk upload completed.",
            "total_rows": len(df),
            "inserted": inserted,
            "failed": failed,
            "errors": errors
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))