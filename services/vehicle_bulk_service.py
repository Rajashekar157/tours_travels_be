# services/vehicle_bulk_service.py

import io
import zipfile
import traceback
import logging

import pandas as pd
import pdfplumber

from fastapi import UploadFile, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

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
                    None,
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
            raise HTTPException(status_code=400, detail="Supported formats: CSV, XLSX, XLS, PDF, ZIP.")

        # Normalize column names: lowercase, strip, spaces → underscores
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        # Strip whitespace from all string values
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Drop fully empty rows
        df = df.dropna(how="all").reset_index(drop=True)

        return df

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


def _build_lookup(db: Session, table: str, column: str) -> dict:
    """Build a lowercase-keyed id lookup from a master table."""
    rows = db.execute(
        text(f"SELECT id, LOWER(TRIM({column})) AS val FROM {table}")
    ).mappings().all()
    return {r["val"]: r["id"] for r in rows}


async def bulk_upload_vehicles_service(file: UploadFile, db: Session, current_user):
    try:
        df = await _load_dataframe(file)

        # ── Validate required columns ──────────────────────────────────────
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing)}",
            )

        # ── Build lookup maps ──────────────────────────────────────────────
        location_map     = _build_lookup(db, "master_service_location",  "location_name")
        company_map      = _build_lookup(db, "master_company",           "company_name")
        make_map         = _build_lookup(db, "master_vehicle_make",      "make_name")
        model_map        = _build_lookup(db, "master_vehicle_model",     "model_name")
        fuel_map         = _build_lookup(db, "master_fuel_type",         "fuel_type_name")
        transmission_map = _build_lookup(db, "master_transmission_type", "transmission_name")
        tax_status_map   = _build_lookup(db, "master_tax_status",        "tax_status_name")
        status_map       = _build_lookup(db, "master_status",            "status_name")

        logger.info(
            "Lookup maps loaded — locations: %s | companies: %s | makes: %s | "
            "models: %s | fuels: %s | transmissions: %s | tax_statuses: %s | statuses: %s",
            list(location_map.keys()),
            list(company_map.keys()),
            list(make_map.keys()),
            list(model_map.keys()),
            list(fuel_map.keys()),
            list(transmission_map.keys()),
            list(tax_status_map.keys()),
            list(status_map.keys()),
        )

        inserted, failed, errors = 0, 0, []

        for index, row in df.iterrows():
            excel_row = index + 2  # account for header row
            try:
                # ── Registration number ────────────────────────────────────
                reg_number = str(row.get("vehicle_registration_number", "")).strip()
                if not reg_number or reg_number.lower() == "nan":
                    failed += 1
                    errors.append({"row": excel_row, "reason": "Registration number is missing"})
                    continue

                # ── Duplicate check ────────────────────────────────────────
                if db.execute(
                    text("SELECT id FROM vehicles WHERE vehicle_registration_number = :reg"),
                    {"reg": reg_number},
                ).first():
                    failed += 1
                    errors.append({"row": excel_row, "reason": f"Vehicle '{reg_number}' already exists"})
                    continue

                # ── Required FK helpers ────────────────────────────────────
                def get_id(map_: dict, col: str, label: str) -> int:
                    val = str(row.get(col, "")).strip().lower()
                    if not val or val == "nan":
                        raise ValueError(f"{label} is required but missing")
                    _id = map_.get(val)
                    if _id is None:
                        raise ValueError(
                            f"Invalid {label}: '{val}'. "
                            f"Allowed values: {sorted(map_.keys())}"
                        )
                    return _id

                # ── Optional FK helper ─────────────────────────────────────
                def get_id_optional(map_: dict, col: str, label: str):
                    val = str(row.get(col, "")).strip().lower()
                    if not val or val == "nan":
                        return None
                    _id = map_.get(val)
                    if _id is None:
                        raise ValueError(
                            f"Invalid {label}: '{val}'. "
                            f"Allowed values: {sorted(map_.keys())}"
                        )
                    return _id

                # ── Resolve required lookups ───────────────────────────────
                location_id     = get_id(location_map,     "service_location",  "Service Location")
                company_id      = get_id(company_map,      "company",           "Company")
                make_id         = get_id(make_map,         "vehicle_make",      "Vehicle Make")
                model_id        = get_id(model_map,        "vehicle_model",     "Vehicle Model")
                fuel_id         = get_id(fuel_map,         "fuel_type",         "Fuel Type")
                transmission_id = get_id(transmission_map, "transmission_type", "Transmission Type")
                tax_status_id   = get_id(tax_status_map,   "tax_status",        "Tax Status")

                # ── Resolve optional lookup ────────────────────────────────
                status_id = get_id_optional(status_map, "status", "Status")

                # ── GPS flag ───────────────────────────────────────────────
                gps_raw = str(row.get("gps_enabled", "")).strip().lower()
                gps_enabled = gps_raw in ("yes", "true", "1", "y")

                # ── Safe helpers ───────────────────────────────────────────
                def safe_str(col: str):
                    v = str(row.get(col, "")).strip()
                    return v if v and v.lower() != "nan" else None

                def safe_num(col: str):
                    v = row.get(col)
                    return v if pd.notna(v) else None

                # ── Insert ─────────────────────────────────────────────────
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
                        "service_location_id":         location_id,
                        "company_id":                  company_id,
                        "vehicle_make_id":             make_id,
                        "vehicle_model_id":            model_id,
                        "fuel_type_id":                fuel_id,
                        "transmission_type_id":        transmission_id,
                        "tax_status_id":               tax_status_id,
                        "status_id":                   status_id,
                        "vehicle_registration_number": reg_number,
                        "vehicle_display_number":      safe_str("vehicle_display_number"),
                        "registration_date":           safe_num("registration_date"),
                        "average_mileage":             safe_num("average_mileage"),
                        "year_of_make":                safe_num("year_of_make"),
                        "engine_number":               safe_str("engine_number"),
                        "chassis_number":              safe_str("chassis_number"),
                        "seating_capacity":            safe_num("seating_capacity"),
                        "gps_enabled":                 gps_enabled,
                        "insurance_company":           safe_str("insurance_company"),
                        "insurance_policy_number":     safe_str("insurance_policy_number"),
                        "insurance_expiry_date":       safe_num("insurance_expiry_date"),
                        "vehicle_photo":               safe_str("vehicle_photo"),
                        "created_by":                  current_user["user_id"],
                        "updated_by":                  current_user["user_id"],
                    },
                )
                inserted += 1

            except Exception as e:
                failed += 1
                errors.append({"row": excel_row, "reason": str(e)})
                logger.warning("Row %d failed: %s", excel_row, e)

        db.commit()
        return {
            "success": True,
            "message": "Vehicle bulk upload completed.",
            "total_rows": len(df),
            "inserted": inserted,
            "failed": failed,
            "errors": errors,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))