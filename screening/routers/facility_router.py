

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from core.security import require_role
from core.audit import log_audit_event
from screening.schemas.facility import FacilityCreateRequest, FacilityStatusUpdateRequest, FacilityResponse
from screening.schemas.user import UserResponse
from screening.repositories.facility_repo import FacilityRepository
from screening.repositories.user_repo import UserRepository

router = APIRouter(prefix="/facility", tags=["Facility Management (Admin only)"])


@router.post("", response_model=FacilityResponse, status_code=status.HTTP_201_CREATED)
def register_facility(
    payload: FacilityCreateRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    facility = FacilityRepository.create(
        db, name=payload.name, contact_info=payload.contact_info,
        registered_by_admin_id=token_data.get("user_id"),
    )
    log_audit_event(db, actor_user_id=token_data.get("user_id"), action=f"FACILITY_REGISTERED:{facility.facility_id}")
    return facility


@router.get("", response_model=list[FacilityResponse])
def list_facilities(
    status_filter: str = None,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    return FacilityRepository.list_all(db, status=status_filter)


@router.get("/{facility_id}/staff", response_model=list[UserResponse])
def list_facility_staff(
    facility_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    return UserRepository.list_users(db, facility_id=facility_id)


@router.put("/{facility_id}/status", response_model=FacilityResponse)
def update_facility_status(
    facility_id: int,
    payload: FacilityStatusUpdateRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    if payload.status not in ["Active", "Suspended"]:
        raise HTTPException(status_code=400, detail="status must be 'Active' or 'Suspended'.")

    facility = FacilityRepository.update_status(db, facility_id, payload.status)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found.")

    log_audit_event(db, actor_user_id=token_data.get("user_id"),
                     action=f"FACILITY_STATUS_{payload.status.upper()}:{facility_id}")
    return facility
