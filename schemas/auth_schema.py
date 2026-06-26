from pydantic import BaseModel


class LoginRequest(BaseModel):
    mobile: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    full_name: str
    mobile: str
    role_id: int
    role_name: str