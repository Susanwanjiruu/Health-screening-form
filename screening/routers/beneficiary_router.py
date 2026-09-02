

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from core.security import require_role, enforce_facility_scope
from core.audit import log_audit_event
from screening.models.facility import Facility
from screening.schemas.beneficiary import (
    BeneficiaryCreateRequest, BeneficiaryUpdateRequest, AssignFacilityRequest,
    LogBirthRequest, BeneficiaryResponse, ALLOWED_COHORTS
)
from screening.repositories.beneficiary_repo import BeneficiaryRepository

router = APIRouter(prefix="/beneficiary", tags=["Beneficiary Records"])


@router.post("", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
def create_beneficiary(
    payload: BeneficiaryCreateRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    if payload.cohort_type not in ALLOWED_COHORTS:
        raise HTTPException(status_code=400, detail=f"cohort_type must be one of: {ALLOWED_COHORTS}")

    if payload.cohort_type != "Survival Mother" and payload.birthdate is None:
        raise HTTPException(status_code=400, detail="birthdate is required unless cohort_type is 'Survival Mother'.")

    if BeneficiaryRepository.exists(db, payload.beneficiary_id):
        raise HTTPException(status_code=400, detail=f"Beneficiary ID '{payload.beneficiary_id}' already exists.")

    if payload.assigned_facility_id is not None:
        facility = db.query(Facility).filter(Facility.facility_id == payload.assigned_facility_id).first()
        if not facility or facility.status != "Active":
            raise HTTPException(status_code=400, detail="assigned_facility_id is invalid or inactive.")

    beneficiary = BeneficiaryRepository.create(
        db,
        beneficiary_id=payload.beneficiary_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        birthdate=payload.birthdate,
        gender=payload.gender,
        cohort_type=payload.cohort_type,
        assigned_facility_id=payload.assigned_facility_id,
        consent_on_file=payload.consent_on_file,
        updated_by_admin_id=token_data.get("user_id"),
    )
    log_audit_event(db, actor_user_id=token_data.get("user_id"), action="CREATE_BENEFICIARY",
                     target_beneficiary_id=beneficiary.beneficiary_id)
    return beneficiary


@router.get("", response_model=list[BeneficiaryResponse])
def list_beneficiaries(
    facility_id: int = None,
    cohort_type: str = None,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin", "Provider")),
):
    if token_data.get("role") == "Admin":
        effective_facility_id = facility_id
    else:
        effective_facility_id = token_data.get("facility_id")

    return BeneficiaryRepository.list_beneficiaries(db, facility_id=effective_facility_id, cohort_type=cohort_type)


@router.get("/due-for-screening/{fiscal_year}", response_model=list[BeneficiaryResponse])
def list_due_for_screening(
    fiscal_year: str,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    return BeneficiaryRepository.list_not_yet_screened(db, fiscal_year)


@router.get("/{beneficiary_id}", response_model=BeneficiaryResponse)
def get_beneficiary(
    beneficiary_id: str,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin", "Provider")),
):
    beneficiary = BeneficiaryRepository.get_by_id(db, beneficiary_id)
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary ID not found.")

    enforce_facility_scope(beneficiary.assigned_facility_id, token_data)
    log_audit_event(db, actor_user_id=token_data.get("user_id"), action="VIEW_BENEFICIARY",
                     target_beneficiary_id=beneficiary_id)
    return beneficiary


@router.put("/{beneficiary_id}", response_model=BeneficiaryResponse)
def update_beneficiary(
    beneficiary_id: str,
    payload: BeneficiaryUpdateRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    beneficiary = BeneficiaryRepository.update(
        db, beneficiary_id, admin_id=token_data.get("user_id"), **payload.dict()
    )
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary ID not found.")
    return beneficiary


@router.put("/{beneficiary_id}/log-birth", response_model=BeneficiaryResponse)
def log_birth(
    beneficiary_id: str,
    payload: LogBirthRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    beneficiary = BeneficiaryRepository.log_birth(
        db, beneficiary_id, payload.birthdate, payload.gender, token_data.get("user_id")
    )
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary ID not found.")

    log_audit_event(db, actor_user_id=token_data.get("user_id"), action="LOG_BIRTH",
                     target_beneficiary_id=beneficiary_id)
    return beneficiary


@router.put("/{beneficiary_id}/assign-facility", response_model=BeneficiaryResponse)
def assign_facility(
    beneficiary_id: str,
    payload: AssignFacilityRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    facility = db.query(Facility).filter(Facility.facility_id == payload.facility_id).first()
    if not facility or facility.status != "Active":
        raise HTTPException(status_code=400, detail="facility_id is invalid or inactive.")

    beneficiary = BeneficiaryRepository.assign_facility(
        db, beneficiary_id, payload.facility_id, token_data.get("user_id")
    )
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary ID not found.")
    return beneficiary
