from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, date
from models.generated_models import (
    Drivers,
    Vehicles,
    Suppliers,
    VehicleAssignments,
    ReportsDownloadHistory,
)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _safe_date(val):
    if val is None:
        return None
    if isinstance(val, (datetime, date)):
        return val.strftime("%d %b %Y")
    return str(val)


# ─────────────────────────────────────────────
# Summary cards  (matches frontend REPORT_DATA)
# ─────────────────────────────────────────────

def get_reports_summary(db: Session):
    driver_count     = db.query(func.count(Drivers.id)).scalar() or 0
    vehicle_count    = db.query(func.count(Vehicles.id)).scalar() or 0
    supplier_count   = db.query(func.count(Suppliers.id)).scalar() or 0
    assignment_count = db.query(func.count(VehicleAssignments.id)).scalar() or 0
    total            = driver_count + vehicle_count + supplier_count + assignment_count

    return {
        "driver_reports":      driver_count,
        "vehicle_reports":     vehicle_count,
        "supplier_reports":    supplier_count,
        "assignment_reports":  assignment_count,
        "total_reports":       total,
    }


# ─────────────────────────────────────────────
# Report list  (table rows on the Reports page)
# ─────────────────────────────────────────────

def get_all_reports(db: Session, search: str = None, date: str = None):
    driver_count     = db.query(func.count(Drivers.id)).scalar() or 0
    vehicle_count    = db.query(func.count(Vehicles.id)).scalar() or 0
    supplier_count   = db.query(func.count(Suppliers.id)).scalar() or 0
    assignment_count = db.query(func.count(VehicleAssignments.id)).scalar() or 0

    outstanding_count = (
        db.query(func.count(Suppliers.id))
        .filter(Suppliers.outstanding_amount > 0)
        .scalar()
        or 0
    )

    today = datetime.now().strftime("%d %b %Y")

    reports = [
        {"id": 1, "report": "Driver Report",      "generated": today, "records": driver_count,      "status": "Completed"},
        {"id": 2, "report": "Vehicle Report",     "generated": today, "records": vehicle_count,     "status": "Completed"},
        {"id": 3, "report": "Supplier Report",    "generated": today, "records": supplier_count,    "status": "Completed"},
        {"id": 4, "report": "Assignment Report",  "generated": today, "records": assignment_count,  "status": "Completed"},
        {"id": 5, "report": "Outstanding Report", "generated": today, "records": outstanding_count, "status": "Completed"},
    ]

    # Search filter
    if search:
        reports = [r for r in reports if search.lower() in r["report"].lower()]

    # Date filter  (date string like "2026-06-25")
    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d %b %Y")
            reports = [r for r in reports if r["generated"] == filter_date]
        except ValueError:
            pass

    return reports


# ─────────────────────────────────────────────
# Individual report data
# ─────────────────────────────────────────────

def get_driver_report(db: Session):
    drivers = db.query(Drivers).all()
    return [
        {
            "id":            d.id,
            "driver_code":   d.driver_code,
            "full_name":     d.full_name,
            "mobile":        d.mobile,
            "email":         d.email,
            "license_number": d.license_number,
            "license_expiry": _safe_date(d.license_expiry),
            "joining_date":  _safe_date(d.joining_date),
            "is_active":     d.is_active,
            "blood_group":   d.blood_group,
            "city":          d.city,
            "state":         d.state,
        }
        for d in drivers
    ]


def get_vehicle_report(db: Session):
    vehicles = db.query(Vehicles).all()
    return [
        {
            "id":                          v.id,
            "vehicle_registration_number": v.vehicle_registration_number,
            "vehicle_display_number":      v.vehicle_display_number,
            "year_of_make":                v.year_of_make,
            "engine_number":               v.engine_number,
            "chassis_number":              v.chassis_number,
            "gps_enabled":                 v.gps_enabled,
            "insurance_company":           v.insurance_company,
            "insurance_policy_number":     v.insurance_policy_number,
            "insurance_expiry_date":       _safe_date(v.insurance_expiry_date),
            "seating_capacity":            v.seating_capacity,
            "registration_date":           _safe_date(v.registration_date),
        }
        for v in vehicles
    ]


def get_supplier_report(db: Session):
    suppliers = db.query(Suppliers).all()
    return [
        {
            "id":               s.id,
            "supplier_id":      s.supplier_id,
            "supplier_name":    s.supplier_name,
            "mobile":           s.mobile,
            "email":            s.email,
            "city":             s.city,
            "state":            s.state,
            "outstanding_amount": float(s.outstanding_amount) if s.outstanding_amount else 0.0,
            "joining_date":     _safe_date(s.joining_date),
            "agreement_status": s.agreement_status,
            "character_nature": s.character_nature,
        }
        for s in suppliers
    ]


def get_assignment_report(db: Session):
    assignments = db.query(VehicleAssignments).all()
    return [
        {
            "id":              a.id,
            "driver_name":     a.driver.full_name if a.driver else None,
            "driver_code":     a.driver.driver_code if a.driver else None,
            "vehicle_no":      a.vehicle.vehicle_registration_number if a.vehicle else None,
            "display_no":      a.vehicle.vehicle_display_number if a.vehicle else None,
            "supplier_name":   a.supplier.supplier_name if a.supplier else None,
            "assignment_type": a.assignment_type,
            "assigned_date":   _safe_date(a.assigned_date),
            "is_active":       a.is_active,
            "emi_amount":      float(a.emi_amount) if a.emi_amount else 0.0,
            "emi_tenure_months": a.emi_tenure_months,
            "remarks":         a.remarks,
        }
        for a in assignments
    ]


def get_outstanding_report(db: Session):
    suppliers = (
        db.query(Suppliers)
        .filter(Suppliers.outstanding_amount > 0)
        .order_by(Suppliers.outstanding_amount.desc())
        .all()
    )
    return [
        {
            "id":               s.id,
            "supplier_id":      s.supplier_id,
            "supplier_name":    s.supplier_name,
            "mobile":           s.mobile,
            "outstanding_amount": float(s.outstanding_amount),
            "joining_date":     _safe_date(s.joining_date),
            "agreement_status": s.agreement_status,
        }
        for s in suppliers
    ]


# ─────────────────────────────────────────────
# Download log
# ─────────────────────────────────────────────

def log_report_download(db: Session, payload: dict):
    log = ReportsDownloadHistory(
        user_id=payload.get("user_id"),
        report_name=payload.get("report_name"),
        report_type=payload.get("report_type", "PDF"),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "Download logged", "id": log.id}