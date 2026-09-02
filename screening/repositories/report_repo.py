from sqlalchemy.orm import Session
from sqlalchemy import func
from screening.models.beneficiary import Beneficiary
from screening.models.screening import ScreeningSubmission, PhysicalAndSystemicExam
from screening.models.referral import Referral


class ReportRepository:

    @staticmethod
    def count_registered_participants_by_cohort(db: Session, cohort_type: str) -> int:
        return db.query(func.count(Beneficiary.beneficiary_id)).filter(
            Beneficiary.cohort_type == cohort_type
        ).scalar() or 0

    @staticmethod
    def count_screened_participants(db: Session, cohort_type: str, fiscal_year: str) -> int:
        return db.query(func.count(ScreeningSubmission.record_id)).join(
            Beneficiary, ScreeningSubmission.beneficiary_id == Beneficiary.beneficiary_id
        ).filter(
            Beneficiary.cohort_type == cohort_type,
            ScreeningSubmission.fiscal_year == fiscal_year,
        ).scalar() or 0

    @staticmethod
    def count_not_yet_screened(db: Session, cohort_type: str, fiscal_year: str) -> int:
        already_screened_ids = db.query(ScreeningSubmission.beneficiary_id).filter(
            ScreeningSubmission.fiscal_year == fiscal_year
        ).subquery()
        return db.query(func.count(Beneficiary.beneficiary_id)).filter(
            Beneficiary.cohort_type == cohort_type,
            ~Beneficiary.beneficiary_id.in_(already_screened_ids),
        ).scalar() or 0

    @staticmethod
    def count_malnutrition_by_status(db: Session, cohort_type: str, fiscal_year: str, status: str) -> int:
        return db.query(func.count(ScreeningSubmission.record_id)).join(
            Beneficiary, ScreeningSubmission.beneficiary_id == Beneficiary.beneficiary_id
        ).filter(
            Beneficiary.cohort_type == cohort_type,
            ScreeningSubmission.fiscal_year == fiscal_year,
            ScreeningSubmission.malnutrition_status == status,
        ).scalar() or 0

    @staticmethod
    def count_disease_prevalence(db: Session, cohort_type: str, fiscal_year: str, body_system_field: str) -> int:
        exam_column = getattr(PhysicalAndSystemicExam, body_system_field, None)
        if exam_column is None:
            return 0
        return db.query(func.count(PhysicalAndSystemicExam.exam_id)).join(
            ScreeningSubmission, PhysicalAndSystemicExam.record_id == ScreeningSubmission.record_id
        ).join(
            Beneficiary, ScreeningSubmission.beneficiary_id == Beneficiary.beneficiary_id
        ).filter(
            Beneficiary.cohort_type == cohort_type,
            ScreeningSubmission.fiscal_year == fiscal_year,
            exam_column == True,
        ).scalar() or 0

    @staticmethod
    def count_summary_flag(db: Session, cohort_type: str, fiscal_year: str, submission_field: str) -> int:
        submission_column = getattr(ScreeningSubmission, submission_field, None)
        if submission_column is None:
            return 0
        return db.query(func.count(ScreeningSubmission.record_id)).join(
            Beneficiary, ScreeningSubmission.beneficiary_id == Beneficiary.beneficiary_id
        ).filter(
            Beneficiary.cohort_type == cohort_type,
            ScreeningSubmission.fiscal_year == fiscal_year,
            submission_column == True,
        ).scalar() or 0

    @staticmethod
    def count_prescriptions_given(db: Session, cohort_type: str, fiscal_year: str) -> int:
        return db.query(func.count(ScreeningSubmission.record_id)).join(
            Beneficiary, ScreeningSubmission.beneficiary_id == Beneficiary.beneficiary_id
        ).filter(
            Beneficiary.cohort_type == cohort_type,
            ScreeningSubmission.fiscal_year == fiscal_year,
            ScreeningSubmission.therapy_and_recommendation.isnot(None),
            ScreeningSubmission.therapy_and_recommendation != "",
        ).scalar() or 0

    @staticmethod
    def count_referred(db: Session, cohort_type: str, fiscal_year: str) -> int:
        return db.query(func.count(Referral.referral_id)).join(
            ScreeningSubmission, Referral.record_id == ScreeningSubmission.record_id
        ).join(
            Beneficiary, ScreeningSubmission.beneficiary_id == Beneficiary.beneficiary_id
        ).filter(
            Beneficiary.cohort_type == cohort_type,
            ScreeningSubmission.fiscal_year == fiscal_year,
        ).scalar() or 0
