

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from database import get_db
from core.security import require_role, enforce_facility_scope, limiter
from core.audit import log_audit_event
from screening.schemas.screening import ScreeningCreate, ScreeningUpdate, ScreeningResponse
from screening.repositories.screening_repo import ScreeningRepository
from screening.repositories.beneficiary_repo import BeneficiaryRepository
from screening.services.clinical_math import ClinicalMathService
from screening.services.referral_engine import ReferralEngineService
from screening.repositories.referral_repo import ReferralRepository

router = APIRouter(prefix="/screening", tags=["Clinical Screenings"])


@router.get("/status")
@limiter.limit("60/minute")
def health_check(request: Request):
    return {"status": "operational"}


@router.post("/submit", response_model=ScreeningResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def submit_screening(
    request: Request,
    payload: ScreeningCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Provider")),
):
    beneficiary = BeneficiaryRepository.get_by_id(db, payload.beneficiary_id)
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary ID not found.")

    # A provider can only screen beneficiaries assigned to their own facility.
    enforce_facility_scope(beneficiary.assigned_facility_id, token_data)

    provider_id = token_data.get("user_id")
    facility_id = token_data.get("facility_id")

    # --- Compute BMI + age-aware cross-check (does NOT overwrite examiner's own assessment) ---
    bmi_score = ClinicalMathService.calculate_bmi(payload.weight_kg, payload.height_cm)
    age_years = ClinicalMathService.calculate_age_years(beneficiary.birthdate, payload.date_of_screening)
    bmi_cross_check = ClinicalMathService.bmi_cross_check_malnutrition_status(bmi_score, age_years)

    # --- Referral rule engine ---
    exam_flags = payload.physical_exam.dict()
    lab_flags = {"test_hiv_positive": payload.test_hiv and "positive" in (payload.laboratory_findings_notes or "").lower()}
    requires_referral, reason, urgency, is_safeguarding = ReferralEngineService.evaluate(
        malnutrition_status=payload.malnutrition_status,
        temperature_celsius=payload.temperature_celsius,
        physical_exam_flags=exam_flags,
        lab_test_flags=lab_flags,
    )

    saved_record = ScreeningRepository.create_screening_record(
        db=db,
        schema_data=payload,
        provider_id=provider_id,
        facility_id=facility_id,
        bmi=bmi_score,
        bmi_computed_malnutrition_status=bmi_cross_check,
        referral_flag=requires_referral,
    )

    if requires_referral:
        ReferralRepository.create(
            db,
            record_id=saved_record.record_id,
            beneficiary_id=saved_record.beneficiary_id,
            facility_id=facility_id,
            reason=reason,
            urgency=urgency,
            is_safeguarding_case="Yes" if is_safeguarding else "No",
        )

    log_audit_event(db, actor_user_id=provider_id, action="SUBMIT_SCREENING",
                     target_beneficiary_id=saved_record.beneficiary_id)
    return saved_record


@router.get("/beneficiary/{beneficiary_id}", response_model=list[ScreeningResponse])
def get_screening_history(
    beneficiary_id: str,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin", "Provider")),
):
    beneficiary = BeneficiaryRepository.get_by_id(db, beneficiary_id)
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary ID not found.")

    enforce_facility_scope(beneficiary.assigned_facility_id, token_data)
    return ScreeningRepository.get_history_by_beneficiary(db, beneficiary_id)


@router.get("/{record_id}", response_model=ScreeningResponse)
def get_screening_record(
    record_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin", "Provider")),
):
    record = ScreeningRepository.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Screening record not found.")

    enforce_facility_scope(record.facility_id, token_data)
    log_audit_event(db, actor_user_id=token_data.get("user_id"), action="VIEW_SCREENING",
                     target_beneficiary_id=record.beneficiary_id)
    return record


@router.put("/{record_id}", response_model=ScreeningResponse)
def amend_screening_record(
    record_id: int,
    payload: ScreeningUpdate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin", "Provider")),
):
    record = ScreeningRepository.get_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Screening record not found.")

    enforce_facility_scope(record.facility_id, token_data)

    updated = ScreeningRepository.update_record(db, record_id, **payload.dict())
    log_audit_event(db, actor_user_id=token_data.get("user_id"), action="AMEND_SCREENING",
                     target_beneficiary_id=record.beneficiary_id)
    return updated
