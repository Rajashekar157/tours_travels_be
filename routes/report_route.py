from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from services import report_service 

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/")
def get_all_reports(
    search: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return report_service.get_all_reports(db, search=search, date=date)


@router.get("/summary")
def get_reports_summary(db: Session = Depends(get_db)):
    return report_service.get_reports_summary(db)


@router.get("/drivers")
def get_driver_report(db: Session = Depends(get_db)):
    return report_service.get_driver_report(db)


@router.get("/vehicles")
def get_vehicle_report(db: Session = Depends(get_db)):
    return report_service.get_vehicle_report(db)


@router.get("/suppliers")
def get_supplier_report(db: Session = Depends(get_db)):
    return report_service.get_supplier_report(db)


@router.get("/assignments")
def get_assignment_report(db: Session = Depends(get_db)):
    return report_service.get_assignment_report(db)


@router.get("/outstanding")
def get_outstanding_report(db: Session = Depends(get_db)):
    return report_service.get_outstanding_report(db)


@router.post("/download/log")
def log_download(
    payload: dict,
    db: Session = Depends(get_db),
):
    """Log every report download to reports_download_history"""
    return report_service.log_report_download(db, payload)