

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from core.security import require_role
from core.audit import log_audit_event
from screening.schemas.referral import ReferralStatusUpdateRequest, ReferralResponse
from screening.repositories.referral_repo import ReferralRepository
from screening.models.referral import ReferralStatus

router = APIRouter(prefix="/referrals", tags=["Referral Case Management (Admin only)"])


@router.get("", response_model=list[ReferralResponse])
def list_referrals(
    status_filter: str = None,
    facility_id: int = None,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    return ReferralRepository.list_open(db, facility_id=facility_id, status_filter=status_filter)


@router.get("/{referral_id}", response_model=ReferralResponse)
def get_referral(
    referral_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    referral = ReferralRepository.get_by_id(db, referral_id)
    if not referral:
        raise HTTPException(status_code=404, detail="Referral case not found.")
    return referral


@router.put("/{referral_id}/status", response_model=ReferralResponse)
def update_referral_status(
    referral_id: int,
    payload: ReferralStatusUpdateRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    valid_statuses = [s.value for s in ReferralStatus]
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"status must be one of: {valid_statuses}")

    referral = ReferralRepository.update_status(
        db, referral_id, payload.status, token_data.get("user_id"),
        notes=payload.notes, referred_to=payload.referred_to,
    )
    if not referral:
        raise HTTPException(status_code=404, detail="Referral case not found.")

    log_audit_event(db, actor_user_id=token_data.get("user_id"),
                     action=f"REFERRAL_STATUS_{payload.status.upper()}:{referral_id}",
                     target_beneficiary_id=referral.beneficiary_id)
    return referral
