

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from core.security import require_role
from screening.schemas.center import CenterUpdateRequest, CenterResponse
from screening.repositories.center_repo import CenterRepository

router = APIRouter(prefix="/center", tags=["Center Profile"])


@router.get("", response_model=CenterResponse)
def get_center_profile(
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin", "Provider")),
):
    profile = CenterRepository.get_profile(db)
    if not profile:
        raise HTTPException(status_code=404, detail="Center profile has not been set up yet.")
    return profile


@router.put("/{center_id}", response_model=CenterResponse)
def update_center_profile(
    center_id: int,
    payload: CenterUpdateRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    profile = CenterRepository.update_profile(
        db, name=payload.name, region=payload.region, contact_info=payload.contact_info
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Center profile not found.")
    return profile
