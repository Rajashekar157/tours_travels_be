from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "ejhwufefyuhfbhucbsduycahcabscuicdachakdcbhjsdchsdbchwiccsdjhschyuewfcbdfcwebcweufcbwehcbweiuvbwe"
ALGORITHM = "HS256"


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