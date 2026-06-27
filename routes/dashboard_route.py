# routers/dashboard.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from services.dashboard_service import get_dashboard_data_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/")
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    return await get_dashboard_data_service(db)