from sqlalchemy.orm import Session
from screening.models.screening import (
    ScreeningSubmission, PhysicalAndSystemicExam, DevelopmentalMilestone, ImmunizationRecord
)
from screening.schemas.screening import ScreeningCreate


class ScreeningRepository:

    @staticmethod
    def create_screening_record(
        db: Session,
        schema_data: ScreeningCreate,
        provider_id: int,
        facility_id: int,
        bmi: float,
        bmi_computed_malnutrition_status: str,
        referral_flag: bool,
    ) -> ScreeningSubmission:
      
        db_submission = ScreeningSubmission(
            beneficiary_id=schema_data.beneficiary_id,
            provider_id=provider_id,
            facility_id=facility_id,
            date_of_screening=schema_data.date_of_screening,
            fiscal_year=schema_data.fiscal_year,
            weight_kg=schema_data.weight_kg,
            height_cm=schema_data.height_cm,
            bmi=bmi,
            head_circumference_cm=schema_data.head_circumference_cm,
            temperature_celsius=schema_data.temperature_celsius,
            pulse_bpm=schema_data.pulse_bpm,
            respiration_rate=schema_data.respiration_rate,
            blood_pressure_systolic=schema_data.blood_pressure_systolic,
            blood_pressure_diastolic=schema_data.blood_pressure_diastolic,
            vital_signs_comments=schema_data.vital_signs_comments,
            malnutrition_status=schema_data.malnutrition_status,             # examiner's judgment = source of truth
            bmi_computed_malnutrition_status=bmi_computed_malnutrition_status,  # system cross-check only
            vitamin_a_last_dose_date=schema_data.vitamin_a_last_dose_date,
            deworming_last_dose_date=schema_data.deworming_last_dose_date,
            past_medical_history=schema_data.past_medical_history,
            test_full_blood_count=schema_data.test_full_blood_count,
            test_sputum=schema_data.test_sputum,
            test_urinalysis=schema_data.test_urinalysis,
            test_hiv=schema_data.test_hiv,
            test_stool_analysis=schema_data.test_stool_analysis,
            test_x_ray=schema_data.test_x_ray,
            test_other_description=schema_data.test_other_description,
            laboratory_findings_notes=schema_data.laboratory_findings_notes,
            major_findings=schema_data.major_findings,
            diagnosis_text=schema_data.diagnosis_text,
            icd_number=schema_data.icd_number,
            therapy_and_recommendation=schema_data.therapy_and_recommendation,
            received_treatment_on_site=schema_data.received_treatment_on_site,
            examiner_name=schema_data.examiner_name,
            examiner_qualification=schema_data.examiner_qualification,
            conclusion_date=schema_data.conclusion_date,
            requires_referral_followup=referral_flag,
        )
        db.add(db_submission)
        db.flush() 

        db_exam = PhysicalAndSystemicExam(
            record_id=db_submission.record_id,
            **schema_data.physical_exam.dict()
        )
        db.add(db_exam)

        for entry in schema_data.immunizations:
            db.add(ImmunizationRecord(record_id=db_submission.record_id, **entry.dict()))

        if schema_data.developmental_milestones:
            db.add(DevelopmentalMilestone(
                record_id=db_submission.record_id,
                **schema_data.developmental_milestones.dict()
            ))

        db.commit()
        db.refresh(db_submission)
        return db_submission

    @staticmethod
    def get_by_id(db: Session, record_id: int) -> ScreeningSubmission:
        return db.query(ScreeningSubmission).filter(ScreeningSubmission.record_id == record_id).first()

    @staticmethod
    def get_history_by_beneficiary(db: Session, beneficiary_id: str):
        return db.query(ScreeningSubmission).filter(
            ScreeningSubmission.beneficiary_id == beneficiary_id
        ).order_by(ScreeningSubmission.date_of_screening.desc()).all()

    @staticmethod
    def update_record(db: Session, record_id: int, **fields) -> ScreeningSubmission:
        record = db.query(ScreeningSubmission).filter(ScreeningSubmission.record_id == record_id).first()
        if not record:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record
