from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class ProviderOnboardRequest(BaseModel):
    name: str = Field(..., example="Jane Wanjiru")
    email: EmailStr
    telephone: Optional[str] = None
    designation: str = Field(..., description="e.g. Pediatrician, Clinical Officer, Nurse")
    facility_id: int = Field(..., description="Which clinic this provider belongs to")


class RevokeToggleRequest(BaseModel):
    target_status: str = Field(..., description="Must be 'Active' or 'Revoked'", example="Revoked")


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: str
    status: str
    designation: Optional[str] = None
    facility_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
