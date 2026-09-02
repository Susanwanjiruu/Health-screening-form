from sqlalchemy import Column, String, Date, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Beneficiary(Base):
  
   
    __tablename__ = "beneficiaries"

    beneficiary_id = Column(String(50), primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)

   
    birthdate = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)

    cohort_type = Column(String(30), default="Survival Mother", nullable=False)

    assigned_facility_id = Column(Integer, ForeignKey("facilities.facility_id"), nullable=True)
    consent_on_file = Column(Boolean, default=False, nullable=False)

    updated_by_admin_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    assigned_facility = relationship("Facility", back_populates="beneficiaries")
    screenings = relationship("ScreeningSubmission", backref="beneficiary", cascade="all, delete-orphan")
