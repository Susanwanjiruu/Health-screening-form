from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Facility(Base):
  
    __tablename__ = "facilities"

    facility_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    contact_info = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="Active")  # Active / Suspended
    registered_by_admin_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    staff = relationship("User", back_populates="facility", foreign_keys="User.facility_id")
    beneficiaries = relationship("Beneficiary", back_populates="assigned_facility")
