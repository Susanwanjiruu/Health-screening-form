from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FacilityCreateRequest(BaseModel):
    name: str
    contact_info: Optional[str] = None


class FacilityStatusUpdateRequest(BaseModel):
    status: str  


class FacilityResponse(BaseModel):
    facility_id: int
    name: str
    contact_info: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
