from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from core.database import get_db

from schemas.auth_schema import (
    RegisterRequest,
    SendOTPRequest,
    VerifyOTPRequest,
    LoginRequest
)

from services.auth_service import (
    register_user,
    send_otp,
    verify_otp,
    login_user
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    return register_user(data, db)


@router.post("/send-otp")
def sendotp(
    data: SendOTPRequest,
    db: Session = Depends(get_db)
):
    return send_otp(data, db)


@router.post("/verify-otp")
def verifyotp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    return verify_otp(data, db)


@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    return login_user(data, db)