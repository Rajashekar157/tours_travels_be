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


# ---------------------------------------------------
# LOAD FILE
# ---------------------------------------------------

async def _load_dataframe(file: UploadFile) -> pd.DataFrame:

    filename = file.filename.lower()

    print("Uploaded File :", filename)

    # IMPORTANT: use the async read provided by FastAPI/Starlette's
    # UploadFile, not file.file.read(). Reading the raw SpooledTemporaryFile
    # directly can return truncated/partial bytes depending on how the
    # upload was buffered, which is what causes
    # "zipfile.BadZipFile: File is not a zip file" for xlsx/zip uploads.
    content = await file.read()

    print("File Size :", len(content))

    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:

        # ---------------- CSV ----------------

        if filename.endswith(".csv"):

            df = pd.read_csv(
                io.BytesIO(content)
            )

        # ---------------- XLSX ----------------

        elif filename.endswith(".xlsx"):

            df = pd.read_excel(
                io.BytesIO(content),
                engine="openpyxl"
            )

        # ---------------- XLS ----------------

        elif filename.endswith(".xls"):

            df = pd.read_excel(
                io.BytesIO(content),
                engine="xlrd"
            )

        # ---------------- PDF ----------------

        elif filename.endswith(".pdf"):

            tables = []

            with pdfplumber.open(
                io.BytesIO(content)
            ) as pdf:

                for page in pdf.pages:

                    extracted = page.extract_tables()

                    for table in extracted:

                        if table:

                            tables.append(
                                pd.DataFrame(
                                    table[1:],
                                    columns=table[0]
                                )
                            )

            if not tables:

                raise HTTPException(
                    status_code=400,
                    detail="No table found in PDF."
                )

            df = pd.concat(
                tables,
                ignore_index=True
            )

        # ---------------- ZIP ----------------

        elif filename.endswith(".zip"):

            with zipfile.ZipFile(
                io.BytesIO(content)
            ) as archive:

                target = None

                for name in archive.namelist():

                    if name.lower().endswith(
                        (
                            ".xlsx",
                            ".xls",
                            ".csv"
                        )
                    ):
                        target = name
                        break

                if target is None:

                    raise HTTPException(
                        status_code=400,
                        detail="ZIP does not contain CSV or Excel."
                    )

                with archive.open(target) as f:

                    data = f.read()

                    if target.endswith(".csv"):

                        df = pd.read_csv(
                            io.BytesIO(data)
                        )

                    elif target.endswith(".xlsx"):

                        df = pd.read_excel(
                            io.BytesIO(data),
                            engine="openpyxl"
                        )

                    else:

                        df = pd.read_excel(
                            io.BytesIO(data),
                            engine="xlrd"
                        )

        else:

            raise HTTPException(
                status_code=400,
                detail="Supported files are CSV, XLSX, XLS, PDF and ZIP."
            )

        df.columns = [

            str(col)
            .strip()
            .lower()
            .replace(" ", "_")

            for col in df.columns

        ]

        return df

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ---------------------------------------------------
# LOOKUP
# ---------------------------------------------------

def _build_lookup(
    db: Session,
    table: str,
    column: str
):

    rows = db.execute(

        text(
            f"""
            SELECT
                id,
                {column}
            FROM
                {table}
            """
        )

    ).mappings().all()

    return {

        str(r[column]).strip().lower(): r["id"]

        for r in rows

    }


# ---------------------------------------------------
# BULK UPLOAD VEHICLES
# ---------------------------------------------------

async def bulk_upload_vehicles_service(
    file: UploadFile,
    db: Session,
    current_user
):

    try:

        df = await _load_dataframe(file)

        # -----------------------------
        # Validate Required Columns
        # -----------------------------

        missing_columns = [

            col

            for col in REQUIRED_COLUMNS

            if col not in df.columns

        ]

        if missing_columns:

            raise HTTPException(

                status_code=400,

                detail=f"Missing columns : {', '.join(missing_columns)}"

            )

        # -----------------------------
        # Master Table Lookup
        # -----------------------------

        location_map = _build_lookup(

            db,

            "master_service_location",

            "location_name"

        )

        make_map = _build_lookup(

            db,

            "master_vehicle_make",

            "make_name"

        )

        fuel_map = _build_lookup(

            db,

            "master_fuel_type",

            "fuel_type_name"

        )

        status_map = _build_lookup(

            db,

            "master_status",

            "status_name"

        )

        inserted = 0

        failed = 0

        errors = []

        # -----------------------------
        # Iterate Excel Rows
        # -----------------------------

        for index, row in df.iterrows():

            excel_row = index + 2

            try:

                registration_number = str(

                    row.get(

                        "vehicle_registration_number",

                        ""

                    )

                ).strip()

                if registration_number == "":

                    failed += 1

                    errors.append({

                        "row": excel_row,

                        "reason": "Registration Number Missing"

                    })

                    continue

                # -----------------------------
                # Duplicate Check
                # -----------------------------

                duplicate = db.execute(

                    text("""

                    SELECT id

                    FROM vehicles

                    WHERE vehicle_registration_number=:reg

                    """),

                    {

                        "reg": registration_number

                    }

                ).first()

                if duplicate:

                    failed += 1

                    errors.append({

                        "row": excel_row,

                        "reason": "Vehicle already exists"

                    })

                    continue

                # -----------------------------
                # Lookup IDs
                # -----------------------------

                location_id = location_map.get(

                    str(

                        row.get(

                            "service_location",

                            ""

                        )

                    ).strip().lower()

                )

                make_id = make_map.get(

                    str(

                        row.get(

                            "vehicle_make",

                            ""

                        )

                    ).strip().lower()

                )

                fuel_id = fuel_map.get(

                    str(

                        row.get(

                            "fuel_type",

                            ""

                        )

                    ).strip().lower()

                )

                status_name = str(

                    row.get(

                        "status",

                        "Active"

                    )

                ).strip().lower()

                status_id = status_map.get(status_name)

                if location_id is None:

                    failed += 1

                    errors.append({

                        "row": excel_row,

                        "reason": "Invalid Service Location"

                    })

                    continue

                if make_id is None:

                    failed += 1

                    errors.append({

                        "row": excel_row,

                        "reason": "Invalid Vehicle Make"

                    })

                    continue

                if fuel_id is None:

                    failed += 1

                    errors.append({

                        "row": excel_row,

                        "reason": "Invalid Fuel Type"

                    })

                    continue

                if status_id is None:

                    failed += 1

                    errors.append({

                        "row": excel_row,

                        "reason": "Invalid Status"

                    })

                    continue

                gps = str(

                    row.get(

                        "gps_enabled",

                        ""

                    )

                ).strip().lower()

                gps_enabled = gps in [

                    "yes",

                    "true",

                    "1",

                    "y"

                ]

                db.execute(

                    text("""

                    INSERT INTO vehicles (

                        service_location_id,

                        vehicle_make_id,

                        fuel_type_id,

                        vehicle_registration_number,

                        vehicle_display_number,

                        average_mileage,

                        year_of_make,

                        engine_number,

                        chassis_number,

                        gps_enabled,

                        insurance_company,

                        insurance_policy_number,

                        insurance_expiry_date,

                        status_id,

                        created_by,

                        updated_by

                    )

                    VALUES (

                        :service_location_id,

                        :vehicle_make_id,

                        :fuel_type_id,

                        :vehicle_registration_number,

                        :vehicle_display_number,

                        :average_mileage,

                        :year_of_make,

                        :engine_number,

                        :chassis_number,

                        :gps_enabled,

                        :insurance_company,

                        :insurance_policy_number,

                        :insurance_expiry_date,

                        :status_id,

                        :created_by,

                        :updated_by

                    )

                    """),

                    {

                        "service_location_id": location_id,

                        "vehicle_make_id": make_id,

                        "fuel_type_id": fuel_id,

                        "vehicle_registration_number": registration_number,

                        "vehicle_display_number":

                            str(

                                row.get(

                                    "vehicle_display_number",

                                    ""

                                )

                            ).strip() or None,

                        "average_mileage":

                            row.get(

                                "average_mileage"

                            )

                            if pd.notna(

                                row.get(

                                    "average_mileage"

                                )

                            )

                            else None,

                        "year_of_make":

                            row.get(

                                "year_of_make"

                            )

                            if pd.notna(

                                row.get(

                                    "year_of_make"

                                )

                            )

                            else None,

                        "engine_number":

                            str(

                                row.get(

                                    "engine_number",

                                    ""

                                )

                            ).strip() or None,

                        "chassis_number":

                            str(

                                row.get(

                                    "chassis_number",

                                    ""

                                )

                            ).strip() or None,

                        "gps_enabled": gps_enabled,

                        "insurance_company":

                            str(

                                row.get(

                                    "insurance_company",

                                    ""

                                )

                            ).strip() or None,

                        "insurance_policy_number":

                            str(

                                row.get(

                                    "insurance_policy_number",

                                    ""

                                )

                            ).strip() or None,

                        "insurance_expiry_date":

                            row.get(

                                "insurance_expiry_date"

                            )

                            if pd.notna(

                                row.get(

                                    "insurance_expiry_date"

                                )

                            )

                            else None,

                        "status_id": status_id,

                        "created_by": current_user["user_id"],

                        "updated_by": current_user["user_id"]

                    }

                )

                inserted += 1

            except Exception as e:

                failed += 1

                errors.append(

                    {

                        "row": excel_row,

                        "reason": str(e)

                    }

                )

        db.commit()

        return {

            "success": True,

            "message": "Vehicle bulk upload completed successfully.",

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

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )