from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from core.database import get_db

from schemas.auth_schema import (
    LoginRequest
)

from services.auth_service import (
    login_user
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================================
# LOGIN
# ==========================================

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    return login_user(
        data,
        db
    )