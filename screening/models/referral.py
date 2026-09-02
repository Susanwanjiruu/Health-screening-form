from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class ReferralStatus(str, enum.Enum):
    IDENTIFIED = "Identified"
    REFERRED = "Referred"
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    LOST_TO_FOLLOWUP = "LostToFollowUp"


class Referral(Base):
 
    __tablename__ = "referrals"

    referral_id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("screening_submissions.record_id"), nullable=False)
    beneficiary_id = Column(String(50), ForeignKey("beneficiaries.beneficiary_id"), nullable=False)
    facility_id = Column(Integer, ForeignKey("facilities.facility_id"), nullable=False) 

    reason = Column(Text, nullable=False)
    referred_to = Column(String(150), nullable=True)  
    urgency = Column(String(20), default="Routine")    
    is_safeguarding_case = Column(String(5), default="No")  

    status = Column(String(20), default=ReferralStatus.IDENTIFIED.value)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submission = relationship("ScreeningSubmission", back_populates="referral")
    beneficiary = relationship("Beneficiary")
    status_history = relationship(
        "ReferralStatusLog", back_populates="referral",
        cascade="all, delete-orphan", order_by="ReferralStatusLog.created_at"
    )


class ReferralStatusLog(Base):
   
    __tablename__ = "referral_status_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    referral_id = Column(Integer, ForeignKey("referrals.referral_id", ondelete="CASCADE"), nullable=False)
    updated_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    referral = relationship("Referral", back_populates="status_history")
