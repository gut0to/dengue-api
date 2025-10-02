from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    emaiil: EmailStr
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
    two_factor_enable: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    acess_token: str
    token_type: str

class ConfirmAccount(BaseModel):
    Token: str

class ResetPasswordRequest(BaseModel):
    email: str

class ResetPasswordConfirm(BaseModel):
    email: str

class TwoFactorVerify(BaseModel):
    email: EmailStr
    new_password: str

class UserUpdateRole(BaseModel):
    role: str

class UserToggle2FA(BaseModel):
    two_factor_enable: bool
    