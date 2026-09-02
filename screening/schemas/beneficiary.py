from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

ALLOWED_COHORTS = ["Survival Mother", "Survival Baby", "Sponsorship Participant"]


class BeneficiaryCreateRequest(BaseModel):
    beneficiary_id: str = Field(..., example="CH-8801")
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    birthdate: Optional[date] = None  
    gender: Optional[str] = None
    cohort_type: str = Field(..., description=f"One of: {ALLOWED_COHORTS}")
    assigned_facility_id: Optional[int] = None
    consent_on_file: bool = False


class BeneficiaryUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate: Optional[date] = None
    gender: Optional[str] = None
    consent_on_file: Optional[bool] = None


class AssignFacilityRequest(BaseModel):
    facility_id: int


class LogBirthRequest(BaseModel):
    birthdate: date
    gender: Optional[str] = None


class BeneficiaryResponse(BaseModel):
    beneficiary_id: str
    first_name: str
    last_name: str
    birthdate: Optional[date] = None
    gender: Optional[str] = None
    cohort_type: str
    assigned_facility_id: Optional[int] = None
    consent_on_file: bool
    last_updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
