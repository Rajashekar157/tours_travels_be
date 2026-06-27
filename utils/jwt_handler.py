from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "ejhwufefyuhfbhucbsduycahcabscuicdachakdcbhjsdchsdbchwiccsdjhschyuewfcbdfcwebcweufcbwehcbweiuvbwe"
ALGORITHM = "HS256"


security = HTTPBearer()


def create_access_token(data: dict):
    payload = data.copy()

    payload["exp"] = (
        datetime.utcnow() +
        timedelta(days=1)
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if "user_id" not in payload:
        raise HTTPException(
            status_code=401,
            detail="Token missing user_id"
        )

    return payload
















    