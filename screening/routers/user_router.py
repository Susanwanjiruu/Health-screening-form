

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from core.config import settings
from core.security import require_role, TokenSecurityService
from core.email_service import EmailService
from core.audit import log_audit_event
from screening.models.user import User
from screening.models.facility import Facility
from screening.schemas.user import ProviderOnboardRequest, RevokeToggleRequest, UserResponse
from screening.repositories.user_repo import UserRepository

router = APIRouter(prefix="/user", tags=["Provider & User Management (Admin only)"])


@router.post("/onboard", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def onboard_provider(
    payload: ProviderOnboardRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    facility = db.query(Facility).filter(Facility.facility_id == payload.facility_id).first()
    if not facility or facility.status != "Active":
        raise HTTPException(status_code=400, detail="Facility not found or not active.")

    if UserRepository.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="An account matching that email address already exists.")

    access_code = TokenSecurityService.generate_six_digit_code()

    new_provider = User(
        name=payload.name,
        email=payload.email,
        password_hash=None,
        telephone=payload.telephone,
        designation=payload.designation,
        role="Provider",
        status="Pending",
        facility_id=payload.facility_id,
        email_verification_code=access_code,
        email_verification_code_expires_at=datetime.utcnow() + timedelta(days=settings.ACCESS_CODE_VALID_DAYS),
        is_email_verified=False,
    )
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)

    EmailService.send_provider_access_code(new_provider.email, new_provider.name, access_code, facility.name)
    log_audit_event(db, actor_user_id=token_data.get("user_id"), action=f"PROVIDER_ONBOARDED:{new_provider.user_id}")
    return new_provider


@router.post("/{user_id}/resend-access-code", response_model=UserResponse)
def resend_access_code(
    user_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    user = UserRepository.get_user_by_id(db, user_id)
    if not user or user.status != "Pending":
        raise HTTPException(status_code=404, detail="No pending provider account found for that ID.")

    new_code = TokenSecurityService.generate_six_digit_code()
    user.email_verification_code = new_code
    user.email_verification_code_expires_at = datetime.utcnow() + timedelta(days=settings.ACCESS_CODE_VALID_DAYS)
    db.commit()
    db.refresh(user)

    facility = db.query(Facility).filter(Facility.facility_id == user.facility_id).first()
    EmailService.send_provider_access_code(user.email, user.name, new_code, facility.name if facility else "")
    return user


@router.put("/{user_id}/toggle-status", response_model=UserResponse)
def toggle_provider_status(
    user_id: int,
    payload: RevokeToggleRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    if payload.target_status not in ["Active", "Revoked"]:
        raise HTTPException(status_code=400, detail="target_status must be 'Active' or 'Revoked'.")

    updated_user = UserRepository.toggle_status(db, user_id, payload.target_status)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Target user profile not found.")

    log_audit_event(db, actor_user_id=token_data.get("user_id"),
                     action=f"PROVIDER_STATUS_{payload.target_status.upper()}:{user_id}")
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
def get_provider(
    user_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    user = UserRepository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.get("", response_model=list[UserResponse])
def list_providers(
    facility_id: int = None,
    role: str = None,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    return UserRepository.list_users(db, facility_id=facility_id, role=role)
