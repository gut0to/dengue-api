from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "usuario"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

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

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    two_factor_enabled: bool
    model_config = ConfigDict(from_attributes=True)

class UserUpdateRole(BaseModel):
    role: str

class UserToggle2FA(BaseModel):
    two_factor_enabled: bool
