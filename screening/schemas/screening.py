from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List

MALNUTRITION_STATUSES = ["None", "Mild", "Moderate", "Severe"]


class PhysicalExamSchema(BaseModel):
    exam_head: Optional[str] = None
    exam_chest: Optional[str] = None
    exam_abdomen: Optional[str] = None
    exam_superior_extremities: Optional[str] = None
    exam_inferior_extremities: Optional[str] = None
    exam_genitourinary: Optional[str] = None
    exam_mental_health_status: Optional[str] = None
    exam_extremity_notes: Optional[str] = None

    appearance_edema_swelling: bool = False
    appearance_lethargic: bool = False
    appearance_skin_problem: bool = False
    appearance_jaundice: bool = False
    appearance_pallor_paleness: bool = False
    appearance_signs_of_abuse_neglect: bool = False
    appearance_other_notes: Optional[str] = None

    sys_auditory_ent: bool = False
    sys_circulatory: bool = False
    sys_digestive_git: bool = False
    sys_endocrine: bool = False
    sys_lymphatic: bool = False
    sys_musculoskeletal: bool = False
    sys_nervous: bool = False
    sys_reproductive: bool = False
    sys_respiratory: bool = False
    sys_skin: bool = False
    sys_genito_urinary: bool = False
    sys_vision_eye: bool = False
    sys_dental: bool = False
    sys_sti: bool = False
    sys_malaria: bool = False
    systemic_explanation_notes: Optional[str] = None

    class Config:
        from_attributes = True



class ImmunizationEntrySchema(BaseModel):
    vaccine_code: str = Field(..., example="BCG")
    vaccine_name: str = Field(..., example="Bacillus Calmette-Guerin")
    dose_number_or_booster: Optional[str] = Field(None, example="1")
    source: str = Field("given_today", description="given_today / childhood_completed / other")
    other_description: Optional[str] = None
    date_administered: Optional[date] = None

    class Config:
        from_attributes = True


class DevelopmentalMilestoneSchema(BaseModel):
    gross_motor_status: str = "Normal"
    fine_motor_status: str = "Normal"
    language_status: str = "Normal"
    personal_social_status: str = "Normal"

    class Config:
        from_attributes = True


class ScreeningCreate(BaseModel):
    beneficiary_id: str = Field(..., example="CH-8801")
    date_of_screening: date
    fiscal_year: str = Field(..., example="FY25")

  
    weight_kg: Optional[float] = Field(None, ge=0.5, le=200.0)
    height_cm: Optional[float] = Field(None, ge=30.0, le=250.0)
    head_circumference_cm: Optional[float] = None
    temperature_celsius: Optional[float] = Field(None, ge=34.0, le=43.0)
    pulse_bpm: Optional[int] = None
    respiration_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    vital_signs_comments: Optional[str] = None

    malnutrition_status: str = Field(..., description=f"One of: {MALNUTRITION_STATUSES}")

 
    vitamin_a_last_dose_date: Optional[date] = None
    deworming_last_dose_date: Optional[date] = None


    past_medical_history: Optional[str] = None

    immunizations: List[ImmunizationEntrySchema] = []

  
    test_full_blood_count: bool = False
    test_sputum: bool = False
    test_urinalysis: bool = False
    test_hiv: bool = False
    test_stool_analysis: bool = False
    test_x_ray: bool = False
    test_other_description: Optional[str] = None
    laboratory_findings_notes: Optional[str] = None

   
    major_findings: Optional[str] = None
    diagnosis_text: Optional[str] = None
    icd_number: Optional[str] = Field(None, example="E43")
    therapy_and_recommendation: Optional[str] = Field(None, description="Medical prescription")
    received_treatment_on_site: bool = False
    examiner_name: Optional[str] = None
    examiner_qualification: Optional[str] = None
    conclusion_date: Optional[date] = None

   
    physical_exam: PhysicalExamSchema
    developmental_milestones: Optional[DevelopmentalMilestoneSchema] = None


class ScreeningUpdate(BaseModel):
   
    major_findings: Optional[str] = None
    diagnosis_text: Optional[str] = None
    icd_number: Optional[str] = None
    therapy_and_recommendation: Optional[str] = None
    laboratory_findings_notes: Optional[str] = None
    vital_signs_comments: Optional[str] = None


class ScreeningResponse(BaseModel):
    record_id: int
    beneficiary_id: str
    provider_id: int
    facility_id: int
    date_of_screening: date
    fiscal_year: str
    bmi: Optional[float] = None
    malnutrition_status: str
    bmi_computed_malnutrition_status: Optional[str] = None
    requires_referral_followup: bool
    submitted_at: datetime

    class Config:
        from_attributes = True
