from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReferralStatusUpdateRequest(BaseModel):
    status: str  
    notes: Optional[str] = None
    referred_to: Optional[str] = None


class ReferralStatusLogEntry(BaseModel):
    status: str
    notes: Optional[str] = None
    updated_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralResponse(BaseModel):
    referral_id: int
    record_id: int
    beneficiary_id: str
    facility_id: int
    reason: str
    referred_to: Optional[str] = None
    urgency: str
    is_safeguarding_case: str
    status: str
    created_at: datetime
    updated_at: datetime
    status_history: List[ReferralStatusLogEntry] = []

    class Config:
        from_attributes = True
