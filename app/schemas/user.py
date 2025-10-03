from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    role: Optional[str] = "usuario"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ConfirmAccount(BaseModel):
    token: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=256)

class TwoFactorVerify(BaseModel):
    email: EmailStr
    code: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    two_factor_enabled: bool
