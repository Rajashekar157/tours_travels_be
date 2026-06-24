from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from services.dashboard_service import get_dashboard_data_service

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db)
):
    return get_dashboard_data_service(db)