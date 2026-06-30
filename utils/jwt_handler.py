# from datetime import datetime, timedelta
# from jose import jwt, JWTError
# from fastapi import Depends, HTTPException
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# SECRET_KEY = "ejhwufefyuhfbhucbsduycahcabscuicdachakdcbhjsdchsdbchwiccsdjhschyuewfcbdfcwebcweufcbwehcbweiuvbwe"
# ALGORITHM = "HS256"


# security = HTTPBearer()


# def create_access_token(data: dict):
#     payload = data.copy()

#     payload["exp"] = (
#         datetime.utcnow() +
#         timedelta(days=1)
#     )

#     return jwt.encode(
#         payload,
#         SECRET_KEY,
#         algorithm=ALGORITHM
#     )

# def decode_access_token(token: str):
#     try:
#         payload = jwt.decode(
#             token,
#             SECRET_KEY,
#             algorithms=[ALGORITHM]
#         )
#         return payload
#     except JWTError:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid or expired token"
#         )


# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security)
# ):
#     token = credentials.credentials
#     payload = decode_access_token(token)

#     if "user_id" not in payload:
#         raise HTTPException(
#             status_code=401,
#             detail="Token missing user_id"
#         )

#     return payload


import uuid
from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.database import get_db
from models.generated_models import Users

SECRET_KEY = "ejhwufefyuhfbhucbsduycahcabscuicdachakdcbhjsdchsdbchwiccsdjhschyuewfcbdfcwebcweufcbwehcbweiuvbwe"
ALGORITHM = "HS256"

security = HTTPBearer()


def create_access_token(data: dict):
    payload = data.copy()
    jti = str(uuid.uuid4())
    payload["jti"] = jti
    payload["exp"] = datetime.utcnow() + timedelta(days=1)

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    jti = payload.get("jti")

    if user_id is None:
        raise HTTPException(status_code=401, detail="Token missing user_id")
    if jti is None:
        raise HTTPException(status_code=401, detail="Token missing session id")

    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    # The single-session check: this token's jti must match the
    # user's currently active session. If another device logged in
    # and overwrote active_session_token, this token is stale.
    if user.active_session_token != jti:
        raise HTTPException(
            status_code=401,
            detail="Your session has expired because your account was logged in elsewhere.",
        )

    return payload













    