from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ActivateAccountRequest(BaseModel):
    email: EmailStr
    access_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyLoginOtpRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    token_type: str = "Bearer"
    session_token: str
    refresh_token: Optional[str] = None
