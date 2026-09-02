from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CenterUpdateRequest(BaseModel):
    name: Optional[str] = None
    region: Optional[str] = None
    contact_info: Optional[str] = None


class CenterResponse(BaseModel):
    center_id: int
    name: str
    region: str
    contact_info: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True
