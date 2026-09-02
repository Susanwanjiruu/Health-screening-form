from sqlalchemy import Column, Integer, String, Boolean, Date, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class ScreeningSubmission(Base):
   
    __tablename__ = "screening_submissions"

    record_id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(String(50), ForeignKey("beneficiaries.beneficiary_id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facilities.facility_id"), nullable=False)  
    date_of_screening = Column(Date, nullable=False)
    fiscal_year = Column(String(10), nullable=False)

  
    weight_kg = Column(Numeric(5, 2), nullable=True)
    height_cm = Column(Numeric(5, 2), nullable=True)
    bmi = Column(Numeric(4, 2), nullable=True)                   
    head_circumference_cm = Column(Numeric(4, 2), nullable=True)
    temperature_celsius = Column(Numeric(4, 1), nullable=True)
    pulse_bpm = Column(Integer, nullable=True)
    respiration_rate = Column(Integer, nullable=True)
    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)
    vital_signs_comments = Column(Text, nullable=True)


    malnutrition_status = Column(String(15), default="None", nullable=False)
    bmi_computed_malnutrition_status = Column(String(15), nullable=True)

    
    vitamin_a_last_dose_date = Column(Date, nullable=True)
    deworming_last_dose_date = Column(Date, nullable=True)

    past_medical_history = Column(Text, nullable=True)

  
    test_full_blood_count = Column(Boolean, default=False)
    test_sputum = Column(Boolean, default=False)
    test_urinalysis = Column(Boolean, default=False)
    test_hiv = Column(Boolean, default=False)
    test_stool_analysis = Column(Boolean, default=False)
    test_x_ray = Column(Boolean, default=False)
    test_other_description = Column(String(100), nullable=True)
    laboratory_findings_notes = Column(Text, nullable=True)


    major_findings = Column(Text, nullable=True)
    diagnosis_text = Column(Text, nullable=True)
    icd_number = Column(String(20), nullable=True)
    therapy_and_recommendation = Column(Text, nullable=True)  
    received_treatment_on_site = Column(Boolean, default=False)

    examiner_name = Column(String(100), nullable=True)
    examiner_qualification = Column(String(100), nullable=True)
    examiner_signature_ref = Column(String(255), nullable=True)  
    conclusion_date = Column(Date, nullable=True)


    requires_referral_followup = Column(Boolean, default=False)  
                                                                   
    submitted_at = Column(DateTime, default=datetime.utcnow)

    physical_exam = relationship("PhysicalAndSystemicExam", uselist=False, back_populates="submission",
                                  cascade="all, delete-orphan")
    developmental_milestones = relationship("DevelopmentalMilestone", uselist=False, back_populates="submission",
                                             cascade="all, delete-orphan")
    immunizations = relationship("ImmunizationRecord", back_populates="submission", cascade="all, delete-orphan")
    referral = relationship("Referral", uselist=False, back_populates="submission")


class PhysicalAndSystemicExam(Base):
 
    __tablename__ = "physical_and_systemic_exams"

    exam_id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("screening_submissions.record_id", ondelete="CASCADE"), nullable=False)

    exam_head = Column(String(255), nullable=True)
    exam_chest = Column(String(255), nullable=True)
    exam_abdomen = Column(String(255), nullable=True)
    exam_superior_extremities = Column(String(255), nullable=True)
    exam_inferior_extremities = Column(String(255), nullable=True)
    exam_genitourinary = Column(String(255), nullable=True)
    exam_mental_health_status = Column(String(255), nullable=True)
    exam_extremity_notes = Column(String(255), nullable=True)

    appearance_edema_swelling = Column(Boolean, default=False)
    appearance_lethargic = Column(Boolean, default=False)
    appearance_skin_problem = Column(Boolean, default=False)
    appearance_jaundice = Column(Boolean, default=False)
    appearance_pallor_paleness = Column(Boolean, default=False)
    appearance_signs_of_abuse_neglect = Column(Boolean, default=False) 
    appearance_other_notes = Column(Text, nullable=True)

   
    sys_auditory_ent = Column(Boolean, default=False)
    sys_circulatory = Column(Boolean, default=False)
    sys_digestive_git = Column(Boolean, default=False)
    sys_endocrine = Column(Boolean, default=False)
    sys_lymphatic = Column(Boolean, default=False)
    sys_musculoskeletal = Column(Boolean, default=False)
    sys_nervous = Column(Boolean, default=False)
    sys_reproductive = Column(Boolean, default=False)
    sys_respiratory = Column(Boolean, default=False)
    sys_skin = Column(Boolean, default=False)
    sys_genito_urinary = Column(Boolean, default=False)
    sys_vision_eye = Column(Boolean, default=False)
    sys_dental = Column(Boolean, default=False)
    sys_sti = Column(Boolean, default=False)
    sys_malaria = Column(Boolean, default=False)
    systemic_explanation_notes = Column(Text, nullable=True)

    submission = relationship("ScreeningSubmission", back_populates="physical_exam")


class ImmunizationRecord(Base):
 
    __tablename__ = "immunization_records"

    immunization_id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("screening_submissions.record_id", ondelete="CASCADE"), nullable=False)

    vaccine_code = Column(String(10), nullable=False)     
    vaccine_name = Column(String(100), nullable=False)
    dose_number_or_booster = Column(String(5), nullable=True)  
    source = Column(String(20), nullable=False, default="given_today")  
    other_description = Column(String(150), nullable=True) 
    date_administered = Column(Date, nullable=True)

    submission = relationship("ScreeningSubmission", back_populates="immunizations")


class DevelopmentalMilestone(Base):
  
    __tablename__ = "developmental_milestones"

    development_id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("screening_submissions.record_id", ondelete="CASCADE"), nullable=False)

    gross_motor_status = Column(String(20), default="Normal")   
    fine_motor_status = Column(String(20), default="Normal")
    language_status = Column(String(20), default="Normal")
    personal_social_status = Column(String(20), default="Normal")

    submission = relationship("ScreeningSubmission", back_populates="developmental_milestones")
