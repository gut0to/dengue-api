from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "usuario"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    two_factor_enabled: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ConfirmAccount(BaseModel):
    token: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str

class TwoFactorVerify(BaseModel):
    email: EmailStr
    code: str

class UserUpdateRole(BaseModel):
    role: str

class UserToggle2FA(BaseModel):
    two_factor_enabled: bool