from pydantic import BaseModel


class LoginRequest(BaseModel):
    mobile: str
    password: str


class PermissionsSchema(BaseModel):
    dashboard: bool
    drivers: bool
    vehicles: bool
    suppliers: bool
    assignments: bool
    reports: bool
    settings: bool
    staff_management: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    full_name: str
    mobile: str
    role_id: int
    role_name: str
    permissions: PermissionsSchema